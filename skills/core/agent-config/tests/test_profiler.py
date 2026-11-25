"""Behavioral tests for agent-config deterministic profiling and normalized decide score intake."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def test_scripts_import_only_stdlib_and_local_modules() -> None:
    expected_files = {
        "__init__.py",
        "abstract_profiler.py",
        "agent_config.py",
        "agent_config_models.py",
        "candidate_selector.py",
        "harness_adapter.py",
    }
    actual_files = {p.name for p in SCRIPTS_DIR.glob("*.py")}
    assert actual_files == expected_files

    local_modules = {name[:-3] for name in expected_files if name != "__init__.py"}
    allowed_roots = set(sys.stdlib_module_names) | local_modules | {"__future__"}

    for py_file in sorted(SCRIPTS_DIR.glob("*.py")):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root in allowed_roots, f"{py_file.name} imports external module {root!r}"
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    if node.module:
                        root = node.module.split(".")[0]
                        assert root in local_modules, f"{py_file.name} relative-imports unexpected {root!r}"
                elif node.module:
                    root = node.module.split(".")[0]
                    assert root in allowed_roots, f"{py_file.name} imports external module {root!r}"


def test_deterministic_profile_maps_difficulty_and_preserves_cost_invariant() -> None:
    from abstract_profiler import build_deterministic_profile
    from agent_config_models import TaskCharacteristics

    routine_task = TaskCharacteristics(difficulty="routine", cost_sensitive=True, latency_sensitive=True)
    routine_prof = build_deterministic_profile(routine_task)
    assert routine_prof.recommended_tier == "routine"
    assert routine_prof.reasoning_need == "low"
    assert routine_prof.cost_sensitivity == "high"
    assert routine_prof.latency_sensitivity == "high"
    assert routine_prof.dimension_provenance["complexity"].fallback_used is True

    standard_cost_task = TaskCharacteristics(difficulty="standard", cost_sensitive=True)
    standard_prof = build_deterministic_profile(standard_cost_task)
    assert standard_prof.recommended_tier == "standard"
    assert standard_prof.reasoning_need == "medium"

    critical_task = TaskCharacteristics(
        difficulty="critical",
        difficulty_source="verified-ticket",
        reasoning_policy="highest-supported",
        cost_sensitive=True,
    )
    critical_prof = build_deterministic_profile(critical_task)
    assert critical_prof.recommended_tier == "high"
    assert critical_prof.reasoning_need == "high"
    assert critical_prof.dimension_provenance["complexity"].source == "verified-ticket"
    assert critical_prof.dimension_provenance["complexity"].fallback_used is False
    assert critical_prof.dimension_provenance["reasoning"].source == "explicit-policy"
    assert critical_prof.dimension_provenance["reasoning"].fallback_used is False


def _make_mcp_score(
    levels: list[str],
    probs_by_idx: list[float],
    *,
    backend: str = "local-opendecider",
    model: str = "opendecider-small",
    data_destination: str = "on-device",
    provider_confidence: float | None = 0.91,
    index_keyed: bool = False,
    score_override: float | None = None,
    expected_override: float | None = None,
) -> dict:
    expected = round(sum(i * p for i, p in enumerate(probs_by_idx)), 6)
    top_idx = max(range(len(probs_by_idx)), key=lambda i: probs_by_idx[i])
    probabilities = (
        {i: p for i, p in enumerate(probs_by_idx)}
        if index_keyed
        else {levels[i]: p for i, p in enumerate(probs_by_idx)}
    )
    return {
        "backend": backend,
        "model": model,
        "data_destination": data_destination,
        "fallback_used": False,
        "level": top_idx,
        "label": levels[top_idx],
        "expected_level": expected if expected_override is None else expected_override,
        "score": expected if score_override is None else score_override,
        "probabilities": probabilities,
        "confidence": round(probs_by_idx[top_idx], 4),
        "provider_confidence": provider_confidence,
    }


CALIBRATED_POLICY = {
    "version": 1,
    "backends": {
        "local-opendecider": {
            "names": ["local-opendecider", "magpie-local"],
            "data": "on-device",
            "questions": {
                "agent-config/task-complexity": {
                    "min_confidence": 0.55,
                    "calibration": "labeled benchmark v1",
                },
                "agent-config/reasoning-need": {
                    "min_confidence": 0.55,
                    "calibration": "labeled benchmark v1",
                },
            },
        }
    },
}


def test_decide_intake_accepts_upgrade_and_same_tier_with_label_or_index_probabilities() -> None:
    from abstract_profiler import (
        COMPLEXITY_LEVELS,
        REASONING_LEVELS,
        extract_abstract_task_profile,
    )
    from agent_config_models import TaskCharacteristics

    # Upgrade from routine baseline -> high tier using multi-question decide envelope (answers map)
    task = TaskCharacteristics(
        title="Distributed lock coordinator",
        description="Coordinate lease renewal and fencing tokens",
        difficulty="routine",
        difficulty_source="unknown",
    )
    decide_envelope = {
        "backend": "local-opendecider",
        "model": "opendecider-small",
        "data_destination": "on-device",
        "fallback_used": False,
        "answers": {
            "agent-config/task-complexity": _make_mcp_score(
                COMPLEXITY_LEVELS, [0.02, 0.08, 0.80, 0.10]
            ),
            "agent-config/reasoning-need": _make_mcp_score(
                REASONING_LEVELS, [0.05, 0.15, 0.80], index_keyed=True
            ),
        },
    }
    prof, conf, fallback_used, fallback_reason = extract_abstract_task_profile(
        task,
        decide_scores=decide_envelope,
        policy=CALIBRATED_POLICY,
    )
    assert fallback_used is False
    assert fallback_reason is None
    assert prof.recommended_tier == "high"
    assert prof.complexity_level == "high"
    assert prof.reasoning_need == "high"
    assert conf == pytest.approx(0.80)
    assert prof.dimension_provenance["complexity"].source == "typed-decision"
    assert prof.dimension_provenance["reasoning"].source == "typed-decision"

    # Same-tier hold with direct calibration_thresholds argument
    same_tier_task = TaskCharacteristics(difficulty="standard", difficulty_source="unknown")
    same_scores = {
        "agent-config/task-complexity": _make_mcp_score(
            COMPLEXITY_LEVELS, [0.10, 0.75, 0.15, 0.00]
        ),
        "agent-config/reasoning-need": _make_mcp_score(
            REASONING_LEVELS, [0.10, 0.70, 0.20]
        ),
    }
    prof_hold, conf_hold, fb_hold, _ = extract_abstract_task_profile(
        same_tier_task,
        decide_scores=same_scores,
        calibration_thresholds={
            "agent-config/task-complexity": 0.60,
            "agent-config/reasoning-need": 0.60,
        },
    )
    assert fb_hold is False
    assert prof_hold.recommended_tier == "standard"
    assert prof_hold.reasoning_need == "medium"
    assert conf_hold == pytest.approx(0.70)


def test_downgrade_margin_rejects_borderline_shift_and_accepts_clear_shift() -> None:
    from abstract_profiler import (
        COMPLEXITY_LEVELS,
         DOWNGRADE_MARGIN,
        REASONING_LEVELS,
        extract_abstract_task_profile,
    )
    from agent_config_models import TaskCharacteristics

    assert DOWNGRADE_MARGIN == 0.15
    task = TaskCharacteristics(
        title="Pagination tweak",
        description="Adjust page offset",
        difficulty="standard",
        difficulty_source="unknown",
    )

    # Expected score = 0*0.60 + 1*0.38 + 2*0.02 = 0.42 -> bin 0 (routine),
    # upper bin edge = 0.50 -> margin = 0.08 < 0.15 -> REJECTED despite confidence 0.60 >= 0.55!
    marginal_downgrade = {
        "agent-config/task-complexity": _make_mcp_score(
            COMPLEXITY_LEVELS, [0.60, 0.38, 0.02, 0.00]
        ),
        "agent-config/reasoning-need": _make_mcp_score(
            REASONING_LEVELS, [0.10, 0.80, 0.10]
        ),
    }
    prof_rej, _, fb_rej, _ = extract_abstract_task_profile(
        task, decide_scores=marginal_downgrade, policy=CALIBRATED_POLICY
    )
    assert fb_rej is True
    assert prof_rej.recommended_tier == "standard"
    assert prof_rej.complexity_level == "standard"
    assert prof_rej.dimension_provenance["complexity"].fallback_used is True
    comp_rec = next(d for d in prof_rej.decisions if d["question_id"] == "agent-config/task-complexity")
    assert comp_rec["applied"] is False
    assert comp_rec["final"] == "standard"

    # Expected score = 0*0.85 + 1*0.15 = 0.15 -> bin 0 (routine),
    # upper bin edge = 0.50 -> margin = 0.35 >= 0.15 -> ACCEPTED!
    clear_downgrade = {
        "agent-config/task-complexity": _make_mcp_score(
            COMPLEXITY_LEVELS, [0.85, 0.15, 0.00, 0.00]
        ),
        "agent-config/reasoning-need": _make_mcp_score(
            REASONING_LEVELS, [0.85, 0.15, 0.00]
        ),
    }
    prof_acc, _, fb_acc, _ = extract_abstract_task_profile(
        task, decide_scores=clear_downgrade, policy=CALIBRATED_POLICY
    )
    assert fb_acc is False
    assert prof_acc.recommended_tier == "routine"
    assert prof_acc.complexity_level == "routine"
    assert prof_acc.reasoning_need == "low"


@pytest.mark.parametrize(
    "bad_complexity",
    [
        # Probabilities do not sum to 1.0
        {"probabilities": {"routine": 0.5, "standard": 0.5, "high": 0.5, "critical": 0.0}, "score": 0.5},
        # NaN score
        {"probabilities": {"routine": 1.0, "standard": 0.0, "high": 0.0, "critical": 0.0}, "score": float("nan")},
        # Infinite probability
        {"probabilities": {"routine": float("inf"), "standard": 0.0, "high": 0.0, "critical": 0.0}, "score": 0.0},
        # Boolean disguised as number
        {"probabilities": {"routine": True, "standard": 0.0, "high": 0.0, "critical": 0.0}, "score": 0.0},
        # Expected-score mismatch (expected is 0*0.6 + 3*0.4 = 1.2, reported score is 0.1)
        {"probabilities": {"routine": 0.6, "standard": 0.0, "high": 0.0, "critical": 0.4}, "score": 0.1},
        # Out-of-range score
        {"probabilities": {"routine": 1.0, "standard": 0.0, "high": 0.0, "critical": 0.0}, "score": -1.0},
        # Missing level key
        {"probabilities": {"routine": 0.5, "standard": 0.5}, "score": 0.5},
        # Disagreement between score and expected_level
        {
            "probabilities": {"routine": 0.0, "standard": 1.0, "high": 0.0, "critical": 0.0},
            "score": 1.0,
            "expected_level": 2.0,
        },
    ],
)
def test_malformed_distributions_and_inconsistent_scores_fall_back(bad_complexity: dict) -> None:
    from abstract_profiler import REASONING_LEVELS, extract_abstract_task_profile
    from agent_config_models import TaskCharacteristics

    task = TaskCharacteristics(difficulty="high", difficulty_source="heuristic")
    scores = {
        "agent-config/task-complexity": {
            "backend": "local-opendecider",
            "data_destination": "on-device",
            **bad_complexity,
        },
        "agent-config/reasoning-need": _make_mcp_score(REASONING_LEVELS, [0.05, 0.15, 0.80]),
    }
    prof, _, fb, _ = extract_abstract_task_profile(
        task, decide_scores=scores, policy=CALIBRATED_POLICY
    )
    assert fb is True
    assert prof.recommended_tier == "high"
    comp_rec = next(d for d in prof.decisions if d["question_id"] == "agent-config/task-complexity")
    assert comp_rec["fallback_reason"] == "malformed"
    # Reasoning was valid and calibrated, so per-dimension independence keeps it!
    assert prof.dimension_provenance["reasoning"].source == "typed-decision"
    assert prof.reasoning_need == "high"


def test_absent_uncalibrated_low_confidence_and_data_boundary_fall_back(tmp_path: Path) -> None:
    from abstract_profiler import (
        COMPLEXITY_LEVELS,
        REASONING_LEVELS,
        extract_abstract_task_profile,
    )
    from agent_config_models import TaskCharacteristics

    task = TaskCharacteristics(difficulty="routine", difficulty_source="unknown")
    high_scores = {
        "agent-config/task-complexity": _make_mcp_score(COMPLEXITY_LEVELS, [0.0, 0.1, 0.9, 0.0]),
        "agent-config/reasoning-need": _make_mcp_score(REASONING_LEVELS, [0.0, 0.1, 0.9]),
    }

    # 1. Absent decide_scores -> deterministic fallback
    prof_abs, _, fb_abs, _ = extract_abstract_task_profile(task, decide_scores=None, policy=CALIBRATED_POLICY)
    assert fb_abs is True
    assert prof_abs.recommended_tier == "routine"

    # 2. Uncalibrated policy -> uncalibrated fallback
    prof_uncal, _, fb_uncal, _ = extract_abstract_task_profile(task, decide_scores=high_scores, policy={})
    assert fb_uncal is True
    assert prof_uncal.recommended_tier == "routine"
    assert all(d["fallback_reason"] == "uncalibrated" for d in prof_uncal.decisions)

    # 3. Low confidence (< threshold 0.85) -> low-confidence fallback
    strict_thresholds = {
        "agent-config/task-complexity": 0.95,
        "agent-config/reasoning-need": 0.95,
    }
    prof_low, _, fb_low, _ = extract_abstract_task_profile(
        task, decide_scores=high_scores, calibration_thresholds=strict_thresholds
    )
    assert fb_low is True
    assert prof_low.recommended_tier == "routine"
    assert all(d["fallback_reason"] == "low-confidence" for d in prof_low.decisions)

    # 4. Project Decision data: off -> rejects typed scores with reason 'off'
    (tmp_path / "docs" / "agents").mkdir(parents=True)
    (tmp_path / "docs" / "agents" / "light-project.md").write_text("Decision data: off\n", encoding="utf-8")
    prof_off, _, fb_off, reason_off = extract_abstract_task_profile(
        task, decide_scores=high_scores, policy=CALIBRATED_POLICY, project_root=tmp_path
    )
    assert fb_off is True
    assert "off" in (reason_off or "")
    assert prof_off.recommended_tier == "routine"
    assert all(d["fallback_reason"] == "off" for d in prof_off.decisions)

    # 5. Project Decision data: on-device blocks third-party score envelope
    (tmp_path / "docs" / "agents" / "light-project.md").write_text("Decision data: on-device\n", encoding="utf-8")
    cloud_scores = {
        "agent-config/task-complexity": _make_mcp_score(
            COMPLEXITY_LEVELS, [0.0, 0.1, 0.9, 0.0], backend="magpie", data_destination="third-party"
        ),
        "agent-config/reasoning-need": _make_mcp_score(
            REASONING_LEVELS, [0.0, 0.1, 0.9], backend="magpie", data_destination="third-party"
        ),
    }
    prof_cloud, _, fb_cloud, _ = extract_abstract_task_profile(
        task,
        decide_scores=cloud_scores,
        calibration_thresholds={"agent-config/task-complexity": 0.5, "agent-config/reasoning-need": 0.5},
        project_root=tmp_path,
    )
    assert fb_cloud is True
    assert prof_cloud.recommended_tier == "routine"
    assert all(d["fallback_reason"] == "unavailable" for d in prof_cloud.decisions)


def test_authoritative_difficulty_and_policy_are_not_overridden_by_decide_scores() -> None:
    from abstract_profiler import (
        COMPLEXITY_LEVELS,
        REASONING_LEVELS,
        extract_abstract_task_profile,
    )
    from agent_config_models import TaskCharacteristics

    scores_attempting_downgrade = {
        "agent-config/task-complexity": _make_mcp_score(COMPLEXITY_LEVELS, [1.0, 0.0, 0.0, 0.0]),
        "agent-config/reasoning-need": _make_mcp_score(REASONING_LEVELS, [1.0, 0.0, 0.0]),
    }
    task = TaskCharacteristics(
        difficulty="critical",
        difficulty_source="explicit-user",
        reasoning_policy="highest-supported",
    )
    prof, conf, fb, reason = extract_abstract_task_profile(
        task,
        decide_scores=scores_attempting_downgrade,
        policy=CALIBRATED_POLICY,
    )
    assert fb is False
    assert conf is None
    assert reason is None
    assert prof.recommended_tier == "high"
    assert prof.complexity_level == "critical"
    assert prof.reasoning_need == "high"
    assert prof.decisions == []


def test_exact_downgrade_margin_boundary_on_high_to_standard_shift() -> None:
    from abstract_profiler import (
        COMPLEXITY_LEVELS,
        REASONING_LEVELS,
        extract_abstract_task_profile,
    )
    from agent_config_models import TaskCharacteristics

    task = TaskCharacteristics(difficulty="high", difficulty_source="heuristic")

    # Expected score = 1*0.64 + 2*0.36 = 1.36 -> margin below 1.50 is 0.14 (< 0.15) -> REJECTED
    just_inside_margin = {
        "agent-config/task-complexity": _make_mcp_score(COMPLEXITY_LEVELS, [0.0, 0.64, 0.36, 0.0]),
        "agent-config/reasoning-need": _make_mcp_score(REASONING_LEVELS, [0.0, 0.20, 0.80]),
    }
    prof_rej, _, fb_rej, _ = extract_abstract_task_profile(
        task, decide_scores=just_inside_margin, policy=CALIBRATED_POLICY
    )
    assert fb_rej is True
    assert prof_rej.recommended_tier == "high"

    # Expected score = 1*0.65 + 2*0.35 = 1.35 -> margin below 1.50 is 0.15 (== 0.15) -> ACCEPTED
    at_exact_margin = {
        "agent-config/task-complexity": _make_mcp_score(COMPLEXITY_LEVELS, [0.0, 0.65, 0.35, 0.0]),
        "agent-config/reasoning-need": _make_mcp_score(REASONING_LEVELS, [0.0, 0.20, 0.80]),
    }
    prof_acc, _, fb_acc, _ = extract_abstract_task_profile(
        task, decide_scores=at_exact_margin, policy=CALIBRATED_POLICY
    )
    assert fb_acc is False
    assert prof_acc.recommended_tier == "standard"



def test_model_calibration_matching_behind_gateway_and_self_judgment_fallback() -> None:
    from abstract_profiler import (
        COMPLEXITY_LEVELS,
        REASONING_LEVELS,
        extract_abstract_task_profile,
    )
    from agent_config_models import TaskCharacteristics

    gateway_policy = {
        "version": 1,
        "backends": {
            "gemini-decision": {
                "names": ["google/gemini-decision-1", "gemini-decision-1"],
                "data": "third-party",
                "questions": {
                    "agent-config/task-complexity": {
                        "min_confidence": 0.60,
                        "calibration": "gateway model calibration v1",
                    },
                    "agent-config/reasoning-need": {
                        "min_confidence": 0.60,
                        "calibration": "gateway model calibration v1",
                    },
                },
            }
        },
    }
    task = TaskCharacteristics(difficulty="routine", difficulty_source="unknown")
    gateway_scores = {
        "backend": "magpie",
        "model": "google/gemini-decision-1",
        "data_destination": "third-party",
        "answers": {
            "agent-config/task-complexity": _make_mcp_score(
                COMPLEXITY_LEVELS,
                [0.05, 0.15, 0.80, 0.00],
                backend="magpie",
                model="google/gemini-decision-1",
                data_destination="third-party",
            ),
            "agent-config/reasoning-need": _make_mcp_score(
                REASONING_LEVELS,
                [0.05, 0.15, 0.80],
                backend="magpie",
                model="google/gemini-decision-1",
                data_destination="third-party",
            ),
        },
    }
    prof, conf, fb, _ = extract_abstract_task_profile(
        task,
        decide_scores=gateway_scores,
        policy=gateway_policy,
        max_data_destination="third-party",
    )
    assert fb is False
    assert conf == pytest.approx(0.80)
    assert prof.recommended_tier == "high"
    assert all(d["data_destination"] == "third-party" for d in prof.decisions)

    # Self-judgment caller envelope falls back cleanly without 'malformed' misclassification
    self_judgment_scores = {
        "agent-config/task-complexity": {
            "question_id": "agent-config/task-complexity",
            "kind": "score",
            "method": "self-judgment",
            "probabilities": {},
            "score": None,
            "applied": True,
            "fallback_reason": "none",
            "final": "high",
        },
        "agent-config/reasoning-need": {
            "question_id": "agent-config/reasoning-need",
            "kind": "score",
            "method": "self-judgment",
            "probabilities": {},
            "score": None,
            "applied": True,
            "fallback_reason": "unavailable",
            "final": "high",
        },
    }
    prof_self, _, fb_self, _ = extract_abstract_task_profile(
        task, decide_scores=self_judgment_scores, policy=gateway_policy
    )
    assert fb_self is True
    assert prof_self.recommended_tier == "routine"
    reasons = {d["question_id"]: d["fallback_reason"] for d in prof_self.decisions}
    assert reasons["agent-config/task-complexity"] == "self-judgment"
    assert reasons["agent-config/reasoning-need"] == "unavailable"
    assert all(d["data_destination"] == "in-session" for d in prof_self.decisions)
