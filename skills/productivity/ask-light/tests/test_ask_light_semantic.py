"""Unit and contract tests for ask-light bounded typed-decision routing and fail-closed invariants."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
import sys
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ask_light_models import (
    AskLightRecommendation,
    CompactProjectState,
    LegalActionsResult,
    SemanticJudgments,
)
from compact_state_builder import build_compact_decision_state
from state_extractor import (
    CANDIDATE_DESCRIPTIONS,
    compute_legal_actions,
    extract_compact_state_from_dict,
)
from semantic_router import route_with_decisions
from decision_source import read_decision_limit, resolve_source, within_limit

LOCAL_ENV = {"TYPESAFE_BASE_URL": "http://127.0.0.1:8001"}
NORMALIZED_KEYS = {
    "question_id", "question", "kind", "options", "answer", "score", "probabilities", "confidence",
    "provider_confidence", "method", "data", "backend", "calibrated", "applied", "fallback_reason", "final",
}
CALIBRATED = {
    "version": 1,
    "backends": {
        "local-decider": {
            "names": ["127.0.0.1:8001"],
            "data": "on-device",
            "questions": {
                qid: {"min_confidence": 0.6, "calibration": "test fixture"}
                for qid in ("ask-light/next-action", "ask-light/material-ambiguity", "ask-light/reasoning-escalation")
            },
        }
    },
}


def route_calibrated(*args, **kwargs):
    kwargs.setdefault("policy", CALIBRATED)
    return route_with_decisions(*args, **kwargs)


def two_actions():
    return LegalActionsResult(
        status="RECOMMEND",
        allowed_actions=["light-implement", "agent-config"],
        fallback_action="light-implement",
        candidate_descriptions={"light-implement": "Implement ticket", "agent-config": "Configure agent"},
    )


def choice_client(choice, p):
    ans = MagicMock(choice=choice, confidence=p, probabilities={choice: p, "light-implement": round(1 - p, 4)} if choice != "light-implement" else {choice: p})
    client = MagicMock()
    client.system_one.return_value = MagicMock(choices={"next_action": ans}, nouls={}, scores={})
    return client
from advisor import ask_light_semantic_recommend


class AskLightSemanticTest(unittest.TestCase):
    def test_compact_state_builder_privacy_and_compactness(self) -> None:
        """Verify compact state builder never leaks raw files, code, or secrets, and stays <350 bytes."""
        state = CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=[".scratch/feat/issues/01.md"],
            resolved_tickets=[".scratch/feat/issues/00.md"],
        )
        legal = compute_legal_actions(state, "What next?")
        compact = build_compact_decision_state(legal, "What next?")

        self.assertEqual(
            set(compact.keys()),
            {"user_request", "project", "known_blockers", "allowed_candidate_actions"},
        )
        self.assertEqual(compact["user_request"], "What next?")
        self.assertTrue(compact["project"]["initialized"])
        self.assertEqual(compact["project"]["implementation_status"], "partial")
        self.assertEqual(compact["allowed_candidate_actions"], ["light-implement"])

        dumped = json.dumps(compact)
        self.assertNotIn("issues/01.md", dumped)
        self.assertLess(len(dumped), 350)

    def test_deterministic_pre_checks_happy_paths(self) -> None:
        """Verify canonical progression across standard project lifecycle states."""
        # 1. Uninitialized
        res = compute_legal_actions(CompactProjectState(initialized=False))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-init"])

        # 2. Initialized, no spec
        res = compute_legal_actions(CompactProjectState(initialized=True, spec_exists=False))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-clarify"])

        # 3. Clarification ready
        res = compute_legal_actions(CompactProjectState(initialized=True, spec_exists=False, clarification_ready=True))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-spec"])

        # 4. Active spec, no tickets
        res = compute_legal_actions(CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=False))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-tickets"])

        # 5. Tickets ready
        res = compute_legal_actions(CompactProjectState(
            initialized=True, spec_exists=True, spec_active=True, tickets_exist=True,
            ready_tickets=["issue-01.md"]
        ))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["light-implement"])
        self.assertEqual(res.target_item, "issue-01.md")

        # 6. All tickets resolved
        res = compute_legal_actions(CompactProjectState(
            initialized=True, spec_exists=True, spec_active=True, tickets_exist=True,
            all_tickets_resolved=True
        ))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-review"])

        # 7. Review fresh pass
        res = compute_legal_actions(CompactProjectState(
            initialized=True, review_exists=True, review_verdict="PASS", review_freshness="fresh"
        ))
        self.assertEqual(res.status, "TERMINAL")
        self.assertEqual(res.allowed_actions, ["release-workflow"])

    def test_fail_closed_invariants(self) -> None:
        """Verify hard boundaries: unknown tickets, multiple efforts, stale review, dirty tree."""
        # Unknown ticket
        res = compute_legal_actions(
            CompactProjectState(initialized=True),
            user_request="implement ticket 99",
            explicit_target="99",
        )
        self.assertEqual(res.status, "BLOCKED")
        self.assertTrue(res.fail_closed)

        state = CompactProjectState(
            initialized=True, spec_exists=True, spec_active=True, tickets_exist=True,
            ready_tickets=["issue-01.md", "issue-02.md"], claimed_tickets=["issue-03.md"],
        )
        unknown = compute_legal_actions(state, "开始执行", explicit_target="42")
        self.assertEqual(unknown.status, "BLOCKED")
        self.assertTrue(unknown.fail_closed)
        claimed = compute_legal_actions(state, "开始执行", explicit_target="03")
        self.assertEqual(claimed.status, "BLOCKED")
        selected = compute_legal_actions(state, "开始执行", explicit_target="02")
        self.assertEqual(selected.status, "TRANSITION")
        self.assertEqual(selected.target_item, "issue-02.md")

        # Multiple active efforts
        res = compute_legal_actions(
            CompactProjectState(initialized=True, active_efforts=["feat-a", "feat-b"], current_effort=None)
        )
        self.assertEqual(res.status, "NEED_INPUT")
        self.assertTrue(res.fail_closed)

        # Stale review
        res = compute_legal_actions(
            CompactProjectState(initialized=True, review_exists=True, review_verdict="PASS", review_freshness="stale")
        )
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-review"])
        self.assertTrue(res.fail_closed)

        # Dirty working tree after review
        res = compute_legal_actions(
            CompactProjectState(initialized=True, review_exists=True, review_verdict="PASS", working_tree_dirty=True)
        )
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-review"])
        self.assertTrue(res.fail_closed)

    def test_request_intent_detection(self) -> None:
        """Verify question explanation, progress reporting, and explicit execution intent."""
        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])

        # Explanation inquiry
        res_explain = compute_legal_actions(state, user_request="explain the difference between tdd and prototype")
        self.assertEqual(res_explain.status, "EXPLAIN")
        self.assertEqual(res_explain.allowed_actions, [])

        # Progress inquiry
        res_report = compute_legal_actions(state, user_request="汇报当前项目进度")
        self.assertEqual(res_report.status, "EXPLAIN")

        # Explicit execution
        res_exec = compute_legal_actions(state, user_request="立刻开始执行工单")
        self.assertEqual(res_exec.status, "TRANSITION")
        self.assertEqual(res_exec.allowed_actions, ["light-implement"])

    def test_hosted_endpoint_is_beyond_the_default_limit(self) -> None:
        """No Decision data line means on-device: the hosted service is never asked."""
        client = choice_client("agent-config", 0.95)
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(two_actions(), "What next?", client=client)
        client.system_one.assert_not_called()
        self.assertTrue(rec.fallback_used)
        self.assertEqual(rec.primary_skill, "light-implement")
        self.assertEqual(rec.decisions[0]["method"], "self-judgment")
        self.assertEqual(rec.decisions[0]["fallback_reason"], "unavailable")

    def test_calibrated_escalation_recommends_agent_config(self) -> None:
        """Verify calibrated yes/no judgments: Ambiguity & Escalation with active consumers."""
        mock_choice = MagicMock()
        mock_choice.choice = "light-implement"
        mock_choice.confidence = 0.95
        mock_choice.probabilities = {"light-implement": 0.95}

        mock_noul_ambig = MagicMock()
        mock_noul_ambig.noul = 0.10

        mock_noul_escala = MagicMock()
        mock_noul_escala.noul = 0.75

        mock_resp = MagicMock()
        mock_resp.choices = {"next_action": mock_choice}
        mock_resp.nouls = {
            "has_material_ambiguity": mock_noul_ambig,
            "needs_deep_reasoning_escalation": mock_noul_escala,
        }
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                # Request contains complexity keywords -> triggers escalation check with consumer
                rec = route_calibrated(legal, "Should we refactor the consensus engine now?", client=mock_client)
                self.assertEqual(rec.primary_skill, "light-implement")
                self.assertFalse(rec.fallback_used)
                # Hard invariant: a typed answer cannot grant TRANSITION authority
                self.assertEqual(rec.status, "RECOMMEND")
                self.assertTrue(rec.escalated)  # Escalation detected
                self.assertEqual(rec.alternative_skill, "agent-config")
                self.assertIsNotNone(rec.semantic_judgments)
                self.assertNotIn("next_action", rec.semantic_judgments.questions_sent)  # singleton candidate skips Choice

    def test_defense_in_depth_unauthorized_action_rejected(self) -> None:
        """Verify that if the source selects an unauthorized action among multiple choices, it is blocked and falls back."""
        mock_choice = MagicMock()
        mock_choice.choice = "unauthorized-external-skill"
        mock_choice.confidence = 0.99
        mock_choice.probabilities = {"unauthorized-external-skill": 0.99}

        mock_resp = MagicMock()
        mock_resp.choices = {"next_action": mock_choice}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        # Set up a legal result with multiple actions to trigger Choice
        legal = LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["light-implement", "agent-config"],
            fallback_action="light-implement",
            candidate_descriptions={"light-implement": "Implement ticket", "agent-config": "Configure agent"},
        )

        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(legal, "What next?", client=mock_client)
                self.assertTrue(rec.fallback_used)
                self.assertEqual(rec.primary_skill, "light-implement")  # Baseline fallback preserved
                self.assertIn("malformed", rec.fallback_reason)
                self.assertEqual(rec.decisions[0]["fallback_reason"], "malformed")

    def test_typed_answer_cannot_grant_transition_authority(self) -> None:
        """Hard Invariant (Section 12): a typed answer cannot change status to TRANSITION without deterministic authorization."""
        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state, user_request="Advice only, do not run.")
        self.assertEqual(legal.status, "RECOMMEND")

        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(legal, "Advice only, do not run.", client=mock_client)
                self.assertEqual(rec.status, "RECOMMEND")

    def test_single_legal_action_causes_zero_choice_request(self) -> None:
        """Section 13: len(allowed_actions) == 1 must skip Choice."""
        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        legal = LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["light-implement"],
            fallback_action="light-implement",
        )

        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(legal, "What next?", client=mock_client)
                self.assertNotIn("next_action", rec.semantic_judgments.questions_sent)
                self.assertEqual(rec.primary_skill, "light-implement")

    def test_zero_legal_actions_causes_zero_choice_request(self) -> None:
        """Section 13: len(allowed_actions) == 0 returns immediately without asking any source."""
        mock_client = MagicMock()

        legal = LegalActionsResult(
            status="BLOCKED",
            allowed_actions=[],
            blocked_reason="All tickets blocked",
        )

        rec = route_calibrated(legal, "What next?", client=mock_client)
        self.assertEqual(rec.status, "BLOCKED")
        mock_client.system_one.assert_not_called()

    def test_fallback_action_is_explicit_not_list_order_dependent(self) -> None:
        """Section 15: Fallback action is explicit, not list-order dependent."""
        legal = LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["secondary-action", "preferred-fallback"],
            fallback_action="preferred-fallback",
            candidate_descriptions={"secondary-action": "Second", "preferred-fallback": "First"},
        )

        with patch.dict(os.environ, {}, clear=True):
            rec = route_calibrated(legal, "What next?")
            self.assertEqual(rec.primary_skill, "preferred-fallback")
            self.assertTrue(rec.fallback_used)

    def test_unconsumed_semantic_questions_are_not_sent(self) -> None:
        """Section 16: Unconsumed readiness_score is never sent."""
        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(legal, "What next?", client=mock_client)
                self.assertNotIn("readiness_score", rec.semantic_judgments.questions_sent)

    def test_uncalibrated_answer_is_recorded_not_applied(self) -> None:
        """Without calibration the typed answer is kept on record and the baseline stands."""
        client = choice_client("agent-config", 0.95)
        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_decisions(two_actions(), "What next?", client=client, policy={})
        self.assertEqual(rec.primary_skill, "light-implement")
        self.assertEqual(rec.semantic_judgments.action_choice, "agent-config")
        result = rec.decisions[0]
        self.assertEqual(set(result), NORMALIZED_KEYS)
        self.assertEqual((result["applied"], result["fallback_reason"], result["final"]), (False, "uncalibrated", "light-implement"))
        self.assertEqual((result["data"], result["backend"]), ("on-device", "127.0.0.1:8001"))

    def test_calibrated_answer_is_applied_only_at_threshold(self) -> None:
        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                applied = route_calibrated(two_actions(), "What next?", client=choice_client("agent-config", 0.9))
                low = route_calibrated(two_actions(), "What next?", client=choice_client("agent-config", 0.55))
        self.assertEqual(applied.primary_skill, "agent-config")
        self.assertEqual(applied.decisions[0]["backend"], "local-decider")
        self.assertFalse(applied.fallback_used)
        self.assertEqual(low.primary_skill, "light-implement")
        self.assertEqual(low.decisions[0]["fallback_reason"], "low-confidence")

    def test_decision_data_off_and_unrecognized_skip_the_source(self) -> None:
        import tempfile
        for line, reason in (("Decision data: off", "off"), ("Decision data: cloud-please", "off")):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "docs/agents").mkdir(parents=True)
                (root / "docs/agents/light-project.md").write_text(f"# Project\n\n{line}\n", encoding="utf-8")
                client = choice_client("agent-config", 0.95)
                with patch.dict(os.environ, LOCAL_ENV, clear=True):
                    with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                        rec = route_calibrated(two_actions(), "What next?", client=client, project_root=root)
                client.system_one.assert_not_called()
                self.assertEqual(rec.decisions[0]["fallback_reason"], reason)

    def test_third_party_limit_allows_the_hosted_service(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs/agents").mkdir(parents=True)
            (root / "docs/agents/light-project.md").write_text("Decision data: third-party\n", encoding="utf-8")
            client = choice_client("agent-config", 0.95)
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}, clear=True):
                with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                    rec = route_calibrated(two_actions(), "What next?", client=client, project_root=root)
            client.system_one.assert_called_once()
            self.assertEqual(rec.decisions[0]["data"], "third-party")

    def test_source_error_falls_back_without_retry(self) -> None:
        client = MagicMock()
        client.system_one.side_effect = TimeoutError("slow")
        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(two_actions(), "What next?", client=client)
        client.system_one.assert_called_once()
        self.assertEqual(rec.primary_skill, "light-implement")
        self.assertEqual(rec.decisions[0]["fallback_reason"], "timeout")

    def _project(self, tmp, text):
        root = Path(tmp)
        (root / "docs/agents").mkdir(parents=True)
        (root / "docs/agents/light-project.md").write_text(text, encoding="utf-8")
        return root

    def test_decision_data_variants_never_lift_off(self) -> None:
        import tempfile
        cases = {
            "Decision data: off.\n": ("off", False),
            "Decision data: `off` (no model)\n": ("off", False),
            "- **Decision data:** off\n": ("off", True),
            "decision data: OFF\n": ("off", True),
            "| Decision data | off |\n": ("off", True),
            "Decision data: third party\n": ("off", False),
            "- Decision data: private-network\n": ("private-network", True),
            "```\nDecision data: third-party\n```\n": ("on-device", True),
            "- Constraints: keep decision data local\n- Decision data: third-party\n": ("third-party", True),
            "## Decision data\n\nSee below.\n": ("on-device", True),
            "- Decision data: on-device (default)\n": ("off", False),
        }
        for text, expected in cases.items():
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(read_decision_limit(self._project(tmp, text)), expected)

    def test_limit_is_found_from_a_subdirectory_or_cwd(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, "Decision data: off\n")
            (root / ".git").mkdir()
            sub = root / "src" / "pkg"
            sub.mkdir(parents=True)
            self.assertEqual(read_decision_limit(sub), ("off", True))
            cwd = os.getcwd()
            try:
                os.chdir(sub)
                self.assertEqual(read_decision_limit(None), ("off", True))
            finally:
                os.chdir(cwd)

    def test_backend_name_drops_credentials_and_bad_policy_is_uncalibrated(self) -> None:
        with patch.dict(os.environ, {"TYPESAFE_BASE_URL": "http://user:token@127.0.0.1:8001/v1"}, clear=True):
            self.assertEqual(resolve_source(None, True, {}).backend, "127.0.0.1:8001")
        bad_policies = (
            {"backends": [{"names": ["127.0.0.1:8001"]}]},
            {"backends": {"x": {"names": "127.0.0.1:8001x", "questions": {"ask-light/next-action": {"min_confidence": 0.1, "calibration": "c"}}}}},
            {"backends": {"x": {"names": ["127.0.0.1:8001"], "questions": ["ask-light/next-action"]}}},
            {"backends": {"x": {"names": ["127.0.0.1:8001"], "questions": {"ask-light/next-action": {"min_confidence": True, "calibration": "c"}}}}},
        )
        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            for policy in bad_policies:
                with self.subTest(policy=policy):
                    self.assertIsNone(resolve_source(None, True, policy).min_confidence("ask-light/next-action"))

    def test_malformed_answers_mark_fallback_and_unapplied_choice_keeps_baseline_numbers(self) -> None:
        legal = LegalActionsResult(
            status="RECOMMEND", allowed_actions=["light-implement", "project-clarify"], fallback_action="light-implement",
            candidate_descriptions={"light-implement": "Implement", "project-clarify": "Clarify"},
        )
        empty = MagicMock()
        empty.system_one.return_value = MagicMock(choices={}, nouls={}, scores={})
        with patch.dict(os.environ, LOCAL_ENV, clear=True), patch("semantic_router.TYPESAFE_AVAILABLE", True):
            rec = route_calibrated(legal, "What next?", client=empty)
            self.assertTrue(rec.fallback_used)
            self.assertIn("malformed", rec.fallback_reason)
            rec = route_with_decisions(legal, "What next?", client=choice_client("project-clarify", 0.9), policy={})
        self.assertEqual(rec.primary_skill, "light-implement")
        self.assertIsNone(rec.confidence)
        self.assertEqual(rec.probabilities, {"light-implement": 1.0})
        self.assertEqual(rec.semantic_judgments.action_probabilities["project-clarify"], 0.9)

    def test_destination_and_limit_rules(self) -> None:
        self.assertEqual(read_decision_limit(None), ("on-device", True))
        self.assertTrue(within_limit("on-device", "private-network"))
        self.assertFalse(within_limit("private-network", "on-device"))
        self.assertFalse(within_limit("on-device", "off"))
        # A private address is the user's own network only when the policy names it so.
        for url, dest in (("http://localhost:8001", "on-device"), ("http://192.168.1.20:8001", "third-party"),
                          ("https://decider.example.com", "third-party")):
            with patch.dict(os.environ, {"TYPESAFE_BASE_URL": url}, clear=True):
                self.assertEqual(resolve_source(None, True, {}).data, dest)
        lan = {"backends": {"lan": {"names": ["192.168.1.20:8001"], "data": "private-network"}}}
        with patch.dict(os.environ, {"TYPESAFE_BASE_URL": "http://192.168.1.20:8001"}, clear=True):
            self.assertEqual(resolve_source(None, True, lan).data, "private-network")
        # A policy entry that declares a farther destination wins over the address.
        policy = {"backends": {"tunnel": {"names": ["localhost:9000"], "data": "third-party"}}}
        with patch.dict(os.environ, {"TYPESAFE_BASE_URL": "http://localhost:9000"}, clear=True):
            source = resolve_source(None, True, policy)
        self.assertEqual((source.data, source.usable, source.reason), ("third-party", False, "unavailable"))

    def test_advisor_end_to_end_from_dict(self) -> None:
        """Verify ask_light_semantic_recommend accepting standard evidence dict."""
        evidence = {
            "initialized": True,
            "spec": {"exists": True, "active": True, "paths": ["docs/spec.md"]},
            "tickets": {"exists": True, "ready": [{"path": "01.md"}], "blocked": [], "resolved": []},
            "review": {"exists": False},
        }
        rec = ask_light_semantic_recommend(evidence, user_request="下一步做什么？", use_typed_decisions=False)
        self.assertEqual(rec.status, "RECOMMEND")
        self.assertEqual(rec.primary_skill, "light-implement")
        self.assertEqual(rec.target_item, "01.md")

    def test_query_planner_zero_questions_on_plain_query_and_single_action(self) -> None:
        """P1 (Section 13-15): Standard query with single legal action skips the decision source completely."""
        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        mock_client = MagicMock()
        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(legal, "What should I do next?", client=mock_client)
                self.assertEqual(rec.primary_skill, "light-implement")
                self.assertEqual(rec.confidence, 1.0)
                # Query planner emitted 0 questions -> system_one was never called!
                mock_client.system_one.assert_not_called()
                self.assertEqual(rec.semantic_judgments.questions_sent, [])

    def test_query_planner_sends_ambiguity_when_ambiguous_phrasing_present(self) -> None:
        """P1 (Section 14 & 18): Ambiguous user phrasing on implementable state triggers ambiguity question with consumer."""
        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {"has_material_ambiguity": MagicMock(noul=0.92)}
        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_calibrated(legal, "Maybe we should redesign auth or database first?", client=mock_client)
                self.assertIn("has_material_ambiguity", rec.semantic_judgments.questions_sent)
                self.assertEqual(rec.alternative_skill, "project-clarify")

        # Invariant (Section 17): Unambiguous query on project-clarify sends 0 questions
        state_no_spec = CompactProjectState(initialized=True, spec_exists=False)
        legal_clarify = compute_legal_actions(state_no_spec)
        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec2 = route_calibrated(legal_clarify, "What is the next step?", client=mock_client)
                self.assertEqual(rec2.primary_skill, "project-clarify")
                self.assertEqual(rec2.semantic_judgments.questions_sent, [])

    def test_adversarial_linguistic_cases_distinguish_intent_from_authorization(self) -> None:
        """P1 (Sections 35-37): Natural language adversarial cases separate semantic intent from deterministic authority."""
        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])

        mock_client = MagicMock()
        mock_client.system_one.return_value = MagicMock(
            choices={},
            nouls={"wants_immediate_execution": MagicMock(noul=0.15)}
        )

        with patch.dict(os.environ, LOCAL_ENV, clear=True):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                # 1. "Don't implement anything; just tell me what comes next."
                legal_neg = compute_legal_actions(state, user_request="Don't implement anything; just tell me what comes next.")
                rec_neg = route_calibrated(legal_neg, "Don't implement anything; just tell me what comes next.", client=mock_client)
                self.assertEqual(rec_neg.status, "RECOMMEND")
                self.assertEqual(rec_neg.primary_skill, "light-implement")

                # 2. "Should I implement now?"
                legal_hes = compute_legal_actions(state, user_request="Should I implement now?")
                rec_hes = route_calibrated(legal_hes, "Should I implement now?", client=mock_client)
                self.assertEqual(rec_hes.status, "RECOMMEND")  # Hesitant inquiry cannot grant transition

                # 3. "Implement now."
                legal_cmd = compute_legal_actions(state, user_request="Implement now.")
                self.assertEqual(legal_cmd.status, "TRANSITION")  # Deterministic authorization holds!


if __name__ == "__main__":
    unittest.main()
