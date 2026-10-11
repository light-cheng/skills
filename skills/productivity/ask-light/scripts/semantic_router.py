"""Bounded semantic router for ask-light, on the light-decide script path.

Asks a typed decision client only within the project's `Decision data:` limit:
  1. Choice: constrained to code-computed legal candidates when >1 candidate exists.
  2. Yes/no: ambiguity and reasoning-escalation questions, only where a consumer exists.
  3. Policy: a typed answer is applied only when the user's policy file calibrates
     its question id and the answer meets that threshold; otherwise the
     deterministic baseline stands and the typed answer is kept on record.
  4. Every judgment is returned in the light-decide normalized format.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
    TYPESAFE_AVAILABLE = True
except ImportError:
    TYPESAFE_AVAILABLE = False
    class Choice:  # type: ignore[no-redef]
        def __init__(self, instructions: str = "", criteria: Any = None):
            self.instructions = instructions
            self.criteria = criteria
    class Noul:  # type: ignore[no-redef]
        def __init__(self, instructions: str = ""):
            self.instructions = instructions
    class Score:  # type: ignore[no-redef]
        def __init__(self, instructions: str = "", criteria: Any = None):
            self.instructions = instructions
            self.criteria = criteria
    class TypeSafeClient:  # type: ignore[no-redef]
        def __init__(self, api_key: Optional[str] = None):
            self.api_key = api_key
        def system_one(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("TypeSafe SDK is not installed.")

try:
    from .compact_state_builder import build_compact_decision_state
    from .ask_light_models import AskLightRecommendation, LegalActionsResult, SemanticJudgments
    from .decision_source import make_client, own_result, resolve_source, typed_result, yes_no_probabilities
except ImportError:
    from compact_state_builder import build_compact_decision_state
    from ask_light_models import AskLightRecommendation, LegalActionsResult, SemanticJudgments
    from decision_source import make_client, own_result, resolve_source, typed_result, yes_no_probabilities

QUESTION_IDS = {
    "next_action": "ask-light/next-action",
    "has_material_ambiguity": "ask-light/material-ambiguity",
    "needs_deep_reasoning_escalation": "ask-light/reasoning-escalation",
}


def plan_semantic_queries(
    legal_result: LegalActionsResult,
    user_request: str,
    enable_expanded_judgments: bool = True,
) -> tuple[Dict[str, Any], List[str], Dict[str, str], Dict[str, str]]:
    """Plan the minimal necessary decision questions based on deterministic facts, active consumers, and request phrasing.

    Invariants:
      1. Non-executable queries (BLOCKED, NEED_INPUT, EXPLAIN) send 0 questions.
      2. Choice is sent ONLY when len(allowed_actions) > 1.
      3. Ambiguity Noul is sent ONLY when an active consumer exists:
         - If len(allowed_actions) > 1 and "project-clarify" is a candidate (selects clarify over others).
         - If allowed_actions == ["light-implement"] and user phrasing contains explicit ambiguity keywords (recommends clarify alternative).
         - If allowed_actions == ["project-clarify"] alone, NO question is sent (clarify is already the only action; zero-value inference).
      4. Escalation Noul is sent ONLY when "light-implement" is in allowed_actions and task complexity warrants agent-config alternative.
      5. Execution intent Noul is REMOVED: authorization is 100% deterministic code; a typed answer cannot grant transition authority.
    """
    questions: Dict[str, Any] = {}
    questions_sent: List[str] = []
    reasons_needed: Dict[str, str] = {}
    consumers: Dict[str, str] = {}

    req_lower = user_request.lower()

    # 1. Non-executable queries send 0 questions
    if legal_result.status in ("BLOCKED", "NEED_INPUT", "EXPLAIN"):
        return questions, questions_sent, reasons_needed, consumers

    # 2. Choice: Multiple legal alternatives
    if len(legal_result.allowed_actions) > 1:
        criteria = {
            action: legal_result.candidate_descriptions.get(action, f"Execute {action} workflow step")
            for action in legal_result.allowed_actions
        }
        questions["next_action"] = Choice(
            instructions="Which legal workflow action best matches the user intent and project evidence?",
            criteria=criteria,
        )
        questions_sent.append("next_action")
        reasons_needed["next_action"] = "Multiple legal candidate actions available; semantic preference needed."
        consumers["next_action"] = "Selects primary recommended action among legal candidates."

    if not enable_expanded_judgments:
        return questions, questions_sent, reasons_needed, consumers

    # 3. Material Ambiguity
    # Consumer check: does answering this materially change behavior?
    ambiguity_keywords = ["maybe", "perhaps", " or ", "not sure", "whether", "tradeoff", "redesign", "unclear", "ambiguous", "confused"]
    has_ambiguity_phrasing = any(kw in req_lower for kw in ambiguity_keywords)

    if len(legal_result.allowed_actions) > 1 and "project-clarify" in legal_result.allowed_actions:
        # Consumer: pick project-clarify over other legal paths
        questions["has_material_ambiguity"] = Noul(
            instructions="Does the request or project state have material ambiguity or unsettled decisions requiring clarification?",
        )
        questions_sent.append("has_material_ambiguity")
        reasons_needed["has_material_ambiguity"] = "Disambiguate between clarification and other legal actions."
        consumers["has_material_ambiguity"] = "Selects project-clarify over other candidates when ambiguity is material."
    elif legal_result.allowed_actions == ["light-implement"] and has_ambiguity_phrasing:
        # Consumer: recommend project-clarify as alternative skill
        questions["has_material_ambiguity"] = Noul(
            instructions="Does the user request express material ambiguity or conflicting requirements requiring clarification before implementation?",
        )
        questions_sent.append("has_material_ambiguity")
        reasons_needed["has_material_ambiguity"] = "Ambiguity phrasing detected on implementable state."
        consumers["has_material_ambiguity"] = "Recommends project-clarify as alternative skill to resolve requirement ambiguity."

    # 4. Deep Reasoning Escalation
    complexity_keywords = [
        "architecture", "overhaul", "distributed", "consensus", "raft", "concurrency",
        "lock-free", "refactor", "security", "cryptographic", "performance",
    ]
    has_complexity_phrasing = any(kw in req_lower for kw in complexity_keywords)
    if "light-implement" in legal_result.allowed_actions and has_complexity_phrasing:
        questions["needs_deep_reasoning_escalation"] = Noul(
            instructions="Does this request involve high architectural complexity or conflicting requirements requiring deep reasoning escalation rather than fast routing?",
        )
        questions_sent.append("needs_deep_reasoning_escalation")
        reasons_needed["needs_deep_reasoning_escalation"] = "Assess whether implementation task warrants reasoning escalation to agent-config."
        consumers["needs_deep_reasoning_escalation"] = "Recommends agent-config as alternative skill for deep reasoning escalation."

    return questions, questions_sent, reasons_needed, consumers


def _question_text(questions: Dict[str, Any], key: str) -> str:
    return getattr(questions[key], "instructions", key)


def _own_results(
    questions: Dict[str, Any],
    legal_result: LegalActionsResult,
    baseline_skill: str,
    reason: str,
) -> List[Dict[str, Any]]:
    results = []
    for key in questions:
        if key == "next_action":
            results.append(own_result(QUESTION_IDS[key], _question_text(questions, key), "choice",
                                      legal_result.allowed_actions, baseline_skill, reason))
        else:
            results.append(own_result(QUESTION_IDS[key], _question_text(questions, key), "yes_no",
                                      ["yes", "no"], "no", reason))
    return results


def route_with_decisions(
    legal_result: LegalActionsResult,
    user_request: str,
    client: Optional[Any] = None,
    policy: Optional[Dict[str, Any]] = None,
    enable_expanded_judgments: bool = True,
    project_root: Optional[Path] = None,
) -> AskLightRecommendation:
    """Judge legal candidate actions through a typed decision source within the data limit.

    Invariants:
      1. Never asks for BLOCKED, NEED_INPUT, EXPLAIN or TERMINAL states.
      2. Choice is asked ONLY when len(allowed_actions) > 1.
      3. A typed answer CANNOT grant transition authority (status stays legal_result.status).
      4. An answer outside the legal options, an uncalibrated question, a low
         confidence, an error or a disallowed destination keeps the baseline.
    """
    if legal_result.status in ["BLOCKED", "NEED_INPUT", "EXPLAIN"]:
        return AskLightRecommendation(
            status=legal_result.status,
            target_item=legal_result.target_item,
            fail_closed=legal_result.fail_closed,
            justification=legal_result.blocked_reason or "Non-execution query resolved deterministically.",
        )

    if legal_result.status == "TERMINAL":
        return AskLightRecommendation(
            status="TERMINAL",
            alternative_skill="release-workflow",
            confidence=1.0,
            justification="Current effort accepted and complete; no mandatory next workflow step.",
        )

    if not legal_result.allowed_actions:
        return AskLightRecommendation(
            status="BLOCKED",
            fail_closed=True,
            justification="No legal workflow actions available for current project state.",
        )

    baseline_skill = legal_result.fallback_action or legal_result.allowed_actions[0]
    questions, questions_sent, reasons_needed, _ = plan_semantic_queries(
        legal_result, user_request, enable_expanded_judgments=enable_expanded_judgments,
    )

    if not questions:
        return AskLightRecommendation(
            status=legal_result.status,
            primary_skill=baseline_skill,
            target_item=legal_result.target_item,
            confidence=1.0,
            probabilities={baseline_skill: 1.0},
            semantic_judgments=SemanticJudgments(),
            fail_closed=legal_result.fail_closed,
            justification=f"Deterministic action {baseline_skill} selected; query planner determined zero semantic queries needed.",
        )

    source = resolve_source(project_root, TYPESAFE_AVAILABLE or client is not None, policy)

    def baseline(reason: str, note: str) -> AskLightRecommendation:
        return AskLightRecommendation(
            status=legal_result.status,
            primary_skill=baseline_skill,
            target_item=legal_result.target_item,
            probabilities={baseline_skill: 1.0},
            fallback_used=True,
            fallback_reason=note,
            fail_closed=legal_result.fail_closed,
            justification=f"Deterministic baseline selected {baseline_skill} from legal candidates.",
            decisions=_own_results(questions, legal_result, baseline_skill, reason),
        )

    if not source.usable:
        if source.reason == "off":
            note = "Decision data is off" + ("" if source.limit_recognized else " (unrecognized Decision data line)") + "; used deterministic baseline."
        else:
            note = f"No typed decision source available within Decision data '{source.limit}'; used deterministic baseline."
            if source.limit == "private-network" and source.data == "third-party":
                note += " A machine on your own network counts only when its policy entry declares data: private-network."
        return baseline(source.reason, note)

    try:
        ts_client = client or make_client(TypeSafeClient, source)
        response = ts_client.system_one(
            state=build_compact_decision_state(legal_result, user_request), questions=questions,
        )
    except Exception as exc:
        reason = "timeout" if isinstance(exc, TimeoutError) else "unavailable"
        return baseline(reason, f"Decision source call failed ({type(exc).__name__}); used deterministic baseline.")

    decisions: List[Dict[str, Any]] = []
    selected_skill = baseline_skill
    choice_confidence: Optional[float] = None
    probabilities: Dict[str, float] = {baseline_skill: 1.0}
    finals: Dict[str, str] = {}
    yes_probs: Dict[str, float] = {}

    if "next_action" in questions:
        choice_ans = (getattr(response, "choices", None) or {}).get("next_action")
        if choice_ans is None:
            decisions.append(own_result(QUESTION_IDS["next_action"], _question_text(questions, "next_action"),
                                        "choice", legal_result.allowed_actions, baseline_skill, "malformed"))
        else:
            probabilities = {str(k): float(v) for k, v in dict(choice_ans.probabilities).items()}
            result = typed_result(
                source, QUESTION_IDS["next_action"], _question_text(questions, "next_action"), "choice",
                legal_result.allowed_actions, str(choice_ans.choice), probabilities, baseline_skill,
                provider_confidence=getattr(choice_ans, "confidence", None),
            )
            decisions.append(result)
            selected_skill = result["final"]
            if result["applied"]:
                choice_confidence = result["confidence"]
            else:
                probabilities = {baseline_skill: 1.0}

    nouls = getattr(response, "nouls", None) or {}
    for key in ("has_material_ambiguity", "needs_deep_reasoning_escalation"):
        if key not in questions:
            continue
        value = getattr(nouls.get(key), "noul", None)
        if not isinstance(value, (int, float)):
            decisions.append(own_result(QUESTION_IDS[key], _question_text(questions, key), "yes_no",
                                        ["yes", "no"], "no", "malformed"))
            finals[key] = "no"
            continue
        yes_probs[key] = float(value)
        probs = yes_no_probabilities(value)
        answer = "yes" if probs["yes"] >= 0.5 else "no"
        result = typed_result(source, QUESTION_IDS[key], _question_text(questions, key), "yes_no",
                              ["yes", "no"], answer, probs, "no")
        decisions.append(result)
        finals[key] = result["final"]

    alternative_skill = None
    escalated = finals.get("needs_deep_reasoning_escalation") == "yes"
    escalation_reason = "Calibrated decision source judged that this request needs deeper reasoning." if escalated else None
    if escalated and selected_skill == "light-implement":
        alternative_skill = "agent-config"
    if finals.get("has_material_ambiguity") == "yes":
        if "project-clarify" in legal_result.allowed_actions:
            selected_skill = "project-clarify"
        elif "light-implement" in legal_result.allowed_actions:
            alternative_skill = "project-clarify"

    fallen_back = [d for d in decisions if d["fallback_reason"] != "none"]
    fallback_used = bool(fallen_back)
    fallback_reason = None
    if fallback_used:
        reasons = sorted({d["fallback_reason"] for d in fallen_back})
        fallback_reason = "Typed answers not used (" + ", ".join(reasons) + "); baseline kept where they were not applied."

    return AskLightRecommendation(
        status=legal_result.status,
        primary_skill=selected_skill,
        alternative_skill=alternative_skill,
        target_item=legal_result.target_item,
        confidence=choice_confidence,
        probabilities=probabilities,
        semantic_judgments=SemanticJudgments(
            action_choice=next((d["answer"] for d in decisions if d["question_id"] == QUESTION_IDS["next_action"]), None),
            action_confidence=choice_confidence,
            action_probabilities=next((d["probabilities"] for d in decisions if d["question_id"] == QUESTION_IDS["next_action"]), {}),
            ambiguity_probability=yes_probs.get("has_material_ambiguity"),
            escalation_probability=yes_probs.get("needs_deep_reasoning_escalation"),
            questions_sent=questions_sent,
            reason_each_question_needed=reasons_needed,
        ),
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        escalated=escalated,
        escalation_reason=escalation_reason,
        fail_closed=legal_result.fail_closed,
        justification=f"Selected {selected_skill} from legal candidates; see decisions for each judgment.",
        decisions=decisions,
    )
