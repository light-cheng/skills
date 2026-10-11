"""Abstract task profiler extracting configuration intent without hardcoding model names.

Profiles work items into abstract tiers (routine, standard, high) and reasoning needs (low, medium, high).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
    from .agent_config_models import AbstractTaskProfile, DimensionProvenance, TaskCharacteristics
    from .decision_source import make_client, own_result, resolve_source, typed_result
except ImportError:
    from agent_config_models import AbstractTaskProfile, DimensionProvenance, TaskCharacteristics
    from decision_source import make_client, own_result, resolve_source, typed_result

# Capability tier ranks for direction evaluation
TIER_RANKS: Dict[str, int] = {"routine": 1, "standard": 2, "high": 3}
REASONING_RANKS: Dict[str, int] = {"low": 1, "medium": 2, "high": 3}

# Question ids for the user's decision policy file (light-decide). Thresholds live there.
COMPLEXITY_QUESTION = "agent-config/task-complexity"
REASONING_QUESTION = "agent-config/reasoning-need"
COMPLEXITY_LEVELS = ["routine", "standard", "high", "critical"]
REASONING_LEVELS = ["low", "medium", "high"]
COMPLEXITY_TEXT = "How complex is the implementation work described in this task?"
REASONING_TEXT = "What level of reasoning effort is required for this task?"
# Structural rule, not a confidence threshold: a downgrade (the unsafe direction)
# also needs its score at least this far below the edge of the higher bin.
DOWNGRADE_MARGIN: float = 0.15


def _bin_confidence(answer: Any, level: int, levels: int) -> Optional[float]:
    """Probability of the bin's level (light-decide Score rule).

    The client returns `probabilities` keyed by level index (0 = first criterion).
    """
    probs = getattr(answer, "probabilities", None)
    if not isinstance(probs, dict) or set(probs) != set(range(levels)):
        return None
    value = probs[level]
    return float(value) if isinstance(value, (int, float)) else None


def _bin_level(score: float, levels: int) -> int:
    """Index of the level whose bin [i-0.5, i+0.5) holds the expected score; the top bin is closed."""
    return max(0, min(levels - 1, int(score + 0.5)))


def _accept(direction: str, conf: float, threshold: Optional[float], margin: float) -> tuple[bool, str]:
    if threshold is None:
        return False, "uncalibrated"
    if conf < threshold:
        return False, "low-confidence"
    if direction == "downgrade" and margin < DOWNGRADE_MARGIN:
        return False, "low-confidence (score within the downgrade margin)"
    return True, "none"


def _score_record(source: Any, question_id: str, question: str, levels: List[str], answer: Any,
                  score: float, conf: float, baseline: str, accepted: bool) -> Dict[str, Any]:
    """A light-decide Score result; `accepted` also carries the downgrade margin rule."""
    probabilities = {levels[int(k)]: float(v) for k, v in answer.probabilities.items()}
    record = typed_result(
        source, question_id, question, "score", levels, levels[_bin_level(score, len(levels))],
        probabilities, baseline, provider_confidence=getattr(answer, "confidence", None),
        score=round(score, 4), confidence=conf,
    )
    if record["applied"] and not accepted:
        record.update(applied=False, fallback_reason="low-confidence", final=baseline)
    return record


def _own_records(task: TaskCharacteristics, reason: str, ask_complexity: bool, ask_reasoning: bool) -> List[Dict[str, Any]]:
    baseline = build_deterministic_profile(task)
    records = []
    if ask_complexity:
        records.append(own_result(COMPLEXITY_QUESTION, COMPLEXITY_TEXT, "score", COMPLEXITY_LEVELS, baseline.complexity_level, reason))
    if ask_reasoning:
        records.append(own_result(REASONING_QUESTION, REASONING_TEXT, "score", REASONING_LEVELS, baseline.reasoning_need, reason))
    return records


def build_deterministic_profile(task: TaskCharacteristics) -> AbstractTaskProfile:
    """Deterministic fallback mapping of task characteristics to abstract profile.

    Separates capability requirement from cost preference:
    Difficulty maps directly to capability tier and reasoning need;
    cost sensitivity does NOT downgrade capability tier or reasoning need.
    Preserves authoritative provenance for explicit user, verified ticket, or policy inputs.
    """
    if task.difficulty in ["high", "critical"]:
        rec_tier = "high"
        reasoning = "high"
    elif task.difficulty == "routine":
        rec_tier = "routine"
        reasoning = "low"
    else:
        rec_tier = "standard"
        reasoning = "medium"

    lat_sens = "high" if task.latency_sensitive else "medium"
    cost_sens = "high" if task.cost_sensitive else "medium"

    is_comp_auth = task.difficulty_source not in ("unknown", "heuristic") and bool(task.difficulty)
    comp_src = task.difficulty_source if is_comp_auth else "deterministic-fallback"
    comp_fallback = not is_comp_auth

    is_reas_auth = bool(task.reasoning_policy)
    if is_reas_auth:
        if task.reasoning_policy in ("highest-supported", "high"):
            reasoning = "high"
        elif task.reasoning_policy in ("minimal", "low"):
            reasoning = "low"
        else:
            reasoning = "medium"
        reas_src = "explicit-policy"
        reas_fallback = False
    else:
        reas_src = "deterministic-fallback"
        reas_fallback = True

    prov = {
        "complexity": DimensionProvenance(
            dimension="complexity",
            value=task.difficulty,
            source=comp_src,
            fallback_used=comp_fallback,
            fallback_reason=None if is_comp_auth else "Deterministic fallback baseline",
        ),
        "reasoning": DimensionProvenance(
            dimension="reasoning",
            value=reasoning,
            source=reas_src,
            fallback_used=reas_fallback,
            fallback_reason=None if is_reas_auth else "Deterministic fallback baseline",
        ),
        "tier": DimensionProvenance(
            dimension="tier",
            value=rec_tier,
            source=comp_src,
            fallback_used=comp_fallback,
            fallback_reason=None if is_comp_auth else "Deterministic fallback baseline",
        ),
    }

    return AbstractTaskProfile(
        complexity_level=task.difficulty,
        reasoning_need=reasoning,
        latency_sensitivity=lat_sens,
        cost_sensitivity=cost_sens,
        recommended_tier=rec_tier,
        dimension_provenance=prov,
    )


def extract_abstract_task_profile(
    task: TaskCharacteristics,
    client: Optional[Any] = None,
    use_typed_decisions: bool = True,
    project_root: Optional[Path] = None,
    policy: Optional[Dict[str, Any]] = None,
) -> Tuple[AbstractTaskProfile, Optional[float], bool, Optional[str]]:
    """Extract abstract configuration intent using typed Score judgments with per-dimension fallback.

    A typed answer is applied only within the project's `Decision data:` limit,
    and only when the user's policy file calibrates its question id and the
    bin confidence meets that threshold.

    Uses Score primitive for ordered dimensions (complexity and reasoning_need).
    Enforces independent per-dimension confidence evaluation and preserves provenance.

    Core responsibility boundary:
      - If task.difficulty is authoritative (source != 'unknown'), complexity is owned by code.
        Do NOT ask the source for task_complexity; its state never contains declared_difficulty.
      - If task.reasoning_policy is explicit, reasoning is owned by code/policy.
        Do NOT ask the source for reasoning_need.
      - If both are authoritative, return immediately without asking a source.

    Returns:
      (profile, overall_confidence, fallback_used, fallback_reason)
    """
    is_complexity_authoritative = (
        task.difficulty_source not in ("unknown", "heuristic")
        and bool(task.difficulty)
    )
    is_reasoning_authoritative = bool(task.reasoning_policy)

    # 1. If both dimensions are authoritative, deterministic code handles everything with no source call
    if is_complexity_authoritative and is_reasoning_authoritative:
        det_prof = build_deterministic_profile(task)
        return det_prof, None, False, None

    # 2. Check the decision source: data limit, availability
    if not use_typed_decisions:
        return build_deterministic_profile(task), None, True, "Typed decisions disabled"
    source = resolve_source(project_root, TYPESAFE_AVAILABLE or client is not None, policy)
    if not source.usable:
        det_prof = build_deterministic_profile(task)
        det_prof.decisions = _own_records(task, source.reason, not is_complexity_authoritative, not is_reasoning_authoritative)
        return det_prof, None, True, (
            f"No typed decision source used ({source.reason}; Decision data '{source.limit}')"
        )

    # 3. Construct label-clean decision state (NO declared_difficulty, NO ground truth labels!)
    state = {
        "task_title": task.title,
        "task_description": task.description,
        "cost_sensitive": task.cost_sensitive,
        "latency_sensitive": task.latency_sensitive,
    }

    # 4. Construct questions only for dimensions needing semantic evaluation
    questions: Dict[str, Score] = {}
    if not is_complexity_authoritative:
        questions["task_complexity"] = Score(
            instructions=COMPLEXITY_TEXT,
            criteria=[
                "Routine: Simple typos, formatting, minor documentation, or repetitive low-risk edits",
                "Standard: Standard feature implementation, UI Polish, or typical application logic",
                "Complex: Multi-module coordination, complex state management, or algorithmic work",
                "Critical: System-wide architectural overhaul, security-critical paths, or high-concurrency invariants",
            ],
        )
    if not is_reasoning_authoritative:
        questions["reasoning_need"] = Score(
            instructions=REASONING_TEXT,
            criteria=[
                "Low: Minimal reasoning, straightforward coding, or template filling",
                "Medium: Standard programming reasoning, trade-off evaluation, and component composition",
                "High: Deep architectural analysis, multi-system coordination, or subtle edge case handling",
            ],
        )

    try:
        ts_client = client or make_client(TypeSafeClient, source)
        response = ts_client.system_one(state=state, questions=questions)
    except Exception as exc:
        failure = f"Decision source call failed ({type(exc).__name__})"
        det_prof = build_deterministic_profile(task)
        prov = det_prof.dimension_provenance
        if not is_complexity_authoritative:
            prov["complexity"].fallback_reason = failure
            prov["tier"].fallback_reason = failure
        if not is_reasoning_authoritative:
            prov["reasoning"].fallback_reason = failure
        det_prof.decisions = _own_records(task, "timeout" if isinstance(exc, TimeoutError) else "unavailable",
                                          not is_complexity_authoritative, not is_reasoning_authoritative)
        return det_prof, None, True, failure

    comp_score_val: Optional[float] = None
    comp_conf: Optional[float] = None
    reas_score_val: Optional[float] = None
    reas_conf: Optional[float] = None

    # Check for Score answers
    scores_dict = getattr(response, "scores", None)
    score_comp = score_reas = None
    decisions: List[Dict[str, Any]] = []

    if isinstance(scores_dict, dict) and scores_dict:
        score_comp = scores_dict.get("task_complexity")
        score_reas = scores_dict.get("reasoning_need")

        if score_comp is not None and isinstance(getattr(score_comp, "score", None), (int, float)):
            comp_score_val = float(score_comp.score)
            comp_conf = _bin_confidence(score_comp, _bin_level(comp_score_val, 4), 4)

        if score_reas is not None and isinstance(getattr(score_reas, "score", None), (int, float)):
            reas_score_val = float(score_reas.score)
            reas_conf = _bin_confidence(score_reas, _bin_level(reas_score_val, 3), 3)


    prov: Dict[str, DimensionProvenance] = {}
    fallback_dims: List[str] = []
    reported_confs: List[float] = []

    # Process Complexity dimension:
    # Discretization Mapping:
    #   [0.0, 0.5) -> routine (rec_tier: routine)
    #   [0.5, 1.5) -> standard (rec_tier: standard)
    #   [1.5, 2.5) -> high (rec_tier: high)
    #   [2.5, 3.0] -> critical (rec_tier: high)
    comp_fallback = False
    if is_complexity_authoritative:
        comp_level = task.difficulty
        rec_tier = "high" if comp_level in ("high", "critical") else ("routine" if comp_level == "routine" else "standard")
        prov["complexity"] = DimensionProvenance(
            dimension="complexity",
            value=comp_level,
            confidence=None,
            source=task.difficulty_source,
            fallback_used=False,
        )
        prov["tier"] = DimensionProvenance(
            dimension="tier",
            value=rec_tier,
            confidence=None,
            source=task.difficulty_source,
            fallback_used=False,
        )
    else:
        det_base = build_deterministic_profile(task)
        baseline_tier = det_base.recommended_tier
        baseline_level = det_base.complexity_level

        if comp_score_val is not None and comp_conf is not None:
            # 1. Discretization mapping
            if comp_score_val < 0.5:
                cand_level = "routine"
                cand_tier = "routine"
            elif comp_score_val < 1.5:
                cand_level = "standard"
                cand_tier = "standard"
            elif comp_score_val < 2.5:
                cand_level = "high"
                cand_tier = "high"
            else:
                cand_level = "critical"
                cand_tier = "high"

            # 2. Evaluate direction relative to baseline: UPGRADE, HOLD, or DOWNGRADE
            cand_rank = TIER_RANKS[cand_tier]
            base_rank = TIER_RANKS[baseline_tier]

            direction = "upgrade" if cand_rank > base_rank else ("hold" if cand_rank == base_rank else "downgrade")
            margin = (_bin_level(comp_score_val, 4) + 0.5) - comp_score_val
            accepted, why = _accept(direction, comp_conf, source.min_confidence(COMPLEXITY_QUESTION), margin)
            decisions.append(_score_record(source, COMPLEXITY_QUESTION, COMPLEXITY_TEXT, COMPLEXITY_LEVELS,
                                           score_comp, comp_score_val, comp_conf, baseline_level, accepted))
            rejection_reason = f"{direction.capitalize()} from {baseline_tier} to {cand_tier} not applied: {why} (confidence {comp_conf:.2f})"

            if accepted:
                reported_confs.append(comp_conf)
                comp_level = cand_level
                rec_tier = cand_tier
                prov["complexity"] = DimensionProvenance(
                    dimension="complexity",
                    value=comp_level,
                    confidence=comp_conf,
                    source="typed-decision",
                    fallback_used=False,
                )
                prov["tier"] = DimensionProvenance(
                    dimension="tier",
                    value=rec_tier,
                    confidence=comp_conf,
                    source="typed-decision",
                    fallback_used=False,
                )
            else:
                comp_fallback = True
                fallback_dims.append("complexity")
                comp_level = baseline_level
                rec_tier = baseline_tier
                prov["complexity"] = DimensionProvenance(
                    dimension="complexity",
                    value=comp_level,
                    confidence=comp_conf,
                    source="deterministic-fallback",
                    fallback_used=True,
                    fallback_reason=rejection_reason,
                )
                prov["tier"] = DimensionProvenance(
                    dimension="tier",
                    value=rec_tier,
                    confidence=comp_conf,
                    source="deterministic-fallback",
                    fallback_used=True,
                    fallback_reason=rejection_reason,
                )
        else:
            comp_fallback = True
            fallback_dims.append("complexity")
            comp_level = baseline_level
            rec_tier = baseline_tier
            reason_msg = "malformed: typed score or per-level probabilities missing"
            decisions.append(own_result(COMPLEXITY_QUESTION, COMPLEXITY_TEXT, "score", COMPLEXITY_LEVELS, comp_level, "malformed"))
            prov["complexity"] = DimensionProvenance(
                dimension="complexity",
                value=comp_level,
                confidence=comp_conf,
                source="deterministic-fallback",
                fallback_used=True,
                fallback_reason=reason_msg,
            )
            prov["tier"] = DimensionProvenance(
                dimension="tier",
                value=rec_tier,
                confidence=comp_conf,
                source="deterministic-fallback",
                fallback_used=True,
                fallback_reason=reason_msg,
            )

    # Process Reasoning dimension:
    # Discretization Mapping:
    #   [0.0, 0.5) -> low
    #   [0.5, 1.5) -> medium
    #   [1.5, 2.0] -> high
    reas_fallback = False
    if is_reasoning_authoritative:
        if task.reasoning_policy in ("highest-supported", "high"):
            reasoning_need = "high"
        elif task.reasoning_policy in ("minimal", "low"):
            reasoning_need = "low"
        else:
            reasoning_need = "medium"
        prov["reasoning"] = DimensionProvenance(
            dimension="reasoning",
            value=reasoning_need,
            confidence=None,
            source="explicit-policy",
            fallback_used=False,
        )
    else:
        det_base_reas = build_deterministic_profile(task)
        baseline_reas = det_base_reas.reasoning_need

        if reas_conf is not None and reas_score_val is not None:
            if reas_score_val < 0.5:
                cand_reas = "low"
            elif reas_score_val < 1.5:
                cand_reas = "medium"
            else:
                cand_reas = "high"

            cand_rank_reas = REASONING_RANKS[cand_reas]
            base_rank_reas = REASONING_RANKS[baseline_reas]

            direction_reas = "upgrade" if cand_rank_reas > base_rank_reas else ("hold" if cand_rank_reas == base_rank_reas else "downgrade")
            margin_reas = (_bin_level(reas_score_val, 3) + 0.5) - reas_score_val
            accepted_reas, why_reas = _accept(direction_reas, reas_conf, source.min_confidence(REASONING_QUESTION), margin_reas)
            decisions.append(_score_record(source, REASONING_QUESTION, REASONING_TEXT, REASONING_LEVELS,
                                           score_reas, reas_score_val, reas_conf, baseline_reas, accepted_reas))
            rejection_reason_reas = f"{direction_reas.capitalize()} reasoning from {baseline_reas} to {cand_reas} not applied: {why_reas} (confidence {reas_conf:.2f})"

            if accepted_reas:
                reported_confs.append(reas_conf)
                reasoning_need = cand_reas
                prov["reasoning"] = DimensionProvenance(
                    dimension="reasoning",
                    value=reasoning_need,
                    confidence=reas_conf,
                    source="typed-decision",
                    fallback_used=False,
                )
            else:
                reas_fallback = True
                fallback_dims.append("reasoning")
                reasoning_need = baseline_reas
                prov["reasoning"] = DimensionProvenance(
                    dimension="reasoning",
                    value=reasoning_need,
                    confidence=reas_conf,
                    source="deterministic-fallback",
                    fallback_used=True,
                    fallback_reason=rejection_reason_reas,
                )
        else:
            reas_fallback = True
            fallback_dims.append("reasoning")
            det_base = build_deterministic_profile(task)
            reasoning_need = det_base.reasoning_need
            reason_msg = "malformed: typed score or per-level probabilities missing"
            decisions.append(own_result(REASONING_QUESTION, REASONING_TEXT, "score", REASONING_LEVELS, reasoning_need, "malformed"))
            prov["reasoning"] = DimensionProvenance(
                dimension="reasoning",
                value=reasoning_need,
                confidence=reas_conf,
                source="deterministic-fallback",
                fallback_used=True,
                fallback_reason=reason_msg,
            )

    any_fallback = comp_fallback or reas_fallback
    fallback_reason = f"Per-dimension fallback on: {', '.join(fallback_dims)}" if any_fallback else None
    overall_conf = min(reported_confs) if reported_confs else None

    profile = AbstractTaskProfile(
        complexity_level=comp_level,
        complexity_score=comp_score_val,
        complexity_confidence=comp_conf,
        reasoning_need=reasoning_need,
        reasoning_score=reas_score_val,
        reasoning_confidence=reas_conf,
        latency_sensitivity="high" if task.latency_sensitive else "medium",
        cost_sensitivity="high" if task.cost_sensitive else "medium",
        recommended_tier=rec_tier,
        dimension_provenance=prov,
        decisions=decisions,
    )
    return profile, overall_conf, any_fallback, fallback_reason

