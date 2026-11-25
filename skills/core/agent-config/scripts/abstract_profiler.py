"""Abstract task profiler extracting configuration intent without hardcoding model names.

Profiles work items into abstract tiers (routine, standard, high) and reasoning needs
(low, medium, high) using deterministic baselines and optional normalized score payloads
from decide (light-decision-mcp).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    from .agent_config_models import AbstractTaskProfile, DimensionProvenance, TaskCharacteristics
except ImportError:
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    from agent_config_models import AbstractTaskProfile, DimensionProvenance, TaskCharacteristics

TIER_RANKS: Dict[str, int] = {"routine": 1, "standard": 2, "high": 3}
REASONING_RANKS: Dict[str, int] = {"low": 1, "medium": 2, "high": 3}

COMPLEXITY_QUESTION = "agent-config/task-complexity"
REASONING_QUESTION = "agent-config/reasoning-need"
COMPLEXITY_LEVELS: List[str] = ["routine", "standard", "high", "critical"]
REASONING_LEVELS: List[str] = ["low", "medium", "high"]
COMPLEXITY_TEXT = "How complex is the implementation work described in this task?"
REASONING_TEXT = "What level of reasoning effort is required for this task?"

# Structural conservatism: a downward tier or reasoning shift must also sit at least
# DOWNGRADE_MARGIN below the upper edge of the lower bin.
DOWNGRADE_MARGIN: float = 0.15

DESTINATIONS = ("on-device", "private-network", "third-party")
LIMITS = DESTINATIONS + ("off",)
DEFAULT_LIMIT = "on-device"
DEFAULT_POLICY_PATH = Path("~/.config/light/decision-policy.json")
PROJECT_CONFIG_REL = Path("docs/agents/light-project.md")

_DECISION_LABEL = re.compile(
    r"^\s*(?:>\s*)*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)?\|?\s*[*_`]*decision data[*_`]*\s*(?::|\||=|-\s)",
    re.IGNORECASE,
)
_DECISION_HEADING = re.compile(
    r"^\s*#{1,6}\s+[*_`]*decision data[*_`]*\s*:?\s*$",
    re.IGNORECASE,
)
_TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}")
_FENCE = re.compile(r"^\s*(```|~~~)")


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _is_valid_probability(value: Any) -> bool:
    return _is_finite_number(value) and 0.0 <= float(value) <= 1.0


def _bin_level(score: float, count: int) -> int:
    """Index of the level whose bin [i - 0.5, i + 0.5) holds expected score (top bin closed)."""
    return max(0, min(count - 1, int(score + 0.5)))


def _complexity_to_tier(level: str) -> str:
    if level in ("high", "critical"):
        return "high"
    if level == "routine":
        return "routine"
    return "standard"


def _find_project_config(start: Path, explicit_root: bool) -> Optional[Path]:
    here = start.resolve()
    direct = here / PROJECT_CONFIG_REL
    if direct.is_file():
        return direct
    if explicit_root:
        return None
    for folder in (here, *here.parents):
        candidate = folder / PROJECT_CONFIG_REL
        if candidate.is_file():
            return candidate
        if (folder / ".git").exists():
            return None
    return None


def read_decision_data_limit(project_root: Optional[Path]) -> Optional[str]:
    """Read Decision data limit from docs/agents/light-project.md."""
    explicit_root = project_root is not None
    path = _find_project_config(project_root or Path.cwd(), explicit_root=explicit_root)
    if path is None:
        return DEFAULT_LIMIT if explicit_root else None

    in_fence = False
    values: List[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        following = next((ln for ln in lines[index + 1 :] if ln.strip()), "")
        if _DECISION_HEADING.match(line):
            if _DECISION_LABEL.match(following) or following.lstrip().startswith("#"):
                continue
            raw = following
        else:
            match = _DECISION_LABEL.match(line)
            if not match or (line.lstrip().startswith("|") and _TABLE_RULE.match(following)):
                continue
            raw = line[match.end() :]
        cleaned = re.sub(r"[*_`|:=]", " ", raw).strip().lower()
        if cleaned not in LIMITS:
            return "off"
        values.append(cleaned)

    if not values:
        return DEFAULT_LIMIT
    return min(values, key=lambda v: -1 if v == "off" else DESTINATIONS.index(v))


def _stricter_limit(first: Optional[str], second: Optional[str]) -> Optional[str]:
    candidates: List[str] = []
    for item in (first, second):
        if item is None:
            continue
        norm = str(item).strip().lower()
        if norm not in LIMITS:
            return "off"
        candidates.append(norm)
    if not candidates:
        return None
    return min(candidates, key=lambda v: -1 if v == "off" else DESTINATIONS.index(v))


def _within_data_limit(destination: str, limit: Optional[str]) -> bool:
    if destination not in DESTINATIONS:
        return False
    if limit is None:
        return True
    if limit == "off" or limit not in DESTINATIONS:
        return False
    return DESTINATIONS.index(destination) <= DESTINATIONS.index(limit)


def _farther_destination(a: str, b: str) -> str:
    return a if DESTINATIONS.index(a) >= DESTINATIONS.index(b) else b


def load_decision_policy(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load calibration policy JSON. Missing or unreadable files return an empty dict."""
    env_override = os.environ.get("LIGHT_DECISION_POLICY_PATH", "").strip()
    target = (path or (Path(env_override) if env_override else DEFAULT_POLICY_PATH)).expanduser()
    try:
        parsed = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _resolve_question_calibration(
    question_id: str,
    backend: Optional[str],
    model: Optional[str],
    policy: Optional[Dict[str, Any]],
    calibration_thresholds: Optional[Dict[str, float]],
) -> Tuple[Optional[float], Optional[str]]:
    """Return (min_confidence_threshold, declared_backend_data_destination).

    Matches answering backend/model against policy.backends keys and names lists,
    checking compound 'backend/model' and 'model' before 'backend' so per-model
    calibrations behind gateways (such as Magpie) resolve accurately.
    """
    short_key = question_id.split("/")[-1]

    if isinstance(calibration_thresholds, dict):
        raw_thresh = calibration_thresholds.get(question_id)
        if raw_thresh is None:
            raw_thresh = calibration_thresholds.get(short_key)
        if _is_valid_probability(raw_thresh):
            return float(raw_thresh), None

    if not isinstance(policy, dict) or not policy:
        return None, None

    backends = policy.get("backends")
    if isinstance(backends, dict):
        tokens: List[str] = []
        if backend and model:
            tokens.append(f"{backend}/{model}")
        if model and model not in tokens:
            tokens.append(model)
        if backend and backend not in tokens:
            tokens.append(backend)

        matched_entry: Optional[Dict[str, Any]] = None
        for token in tokens:
            for key, entry in backends.items():
                if not isinstance(entry, dict):
                    continue
                names = entry.get("names")
                if token == key or (isinstance(names, list) and token in names):
                    matched_entry = entry
                    break
            if matched_entry is not None:
                break

        if matched_entry is not None:
            declared_data = matched_entry.get("data_destination") or matched_entry.get("data")
            norm_data = declared_data if declared_data in DESTINATIONS else None
            questions = matched_entry.get("questions")
            q_entry = questions.get(question_id) if isinstance(questions, dict) else None
            if isinstance(q_entry, dict):
                thresh = q_entry.get("min_confidence")
                cal = q_entry.get("calibration")
                if _is_valid_probability(thresh) and isinstance(cal, str) and cal.strip():
                    return float(thresh), norm_data
            return None, norm_data
        return None, None

    top_questions = policy.get("questions")
    if isinstance(top_questions, dict):
        q_entry = top_questions.get(question_id) or top_questions.get(short_key)
        if isinstance(q_entry, dict):
            thresh = q_entry.get("min_confidence")
            cal = q_entry.get("calibration")
            if _is_valid_probability(thresh) and (cal is None or (isinstance(cal, str) and cal.strip())):
                return float(thresh), None
        elif _is_valid_probability(q_entry):
            return float(q_entry), None

    return None, None


def _unpack_decide_scores(
    decide_scores: Union[Dict[str, Any], List[Any], Path, str],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Normalize decide score container into a flat dict keyed by question id or alias."""
    raw: Any = decide_scores
    if isinstance(decide_scores, Path):
        try:
            raw = json.loads(decide_scores.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None, "malformed"
    elif isinstance(decide_scores, str):
        try:
            raw = json.loads(decide_scores)
        except ValueError:
            return None, "malformed"

    if isinstance(raw, list):
        mapped: Dict[str, Any] = {}
        for item in raw:
            if isinstance(item, dict) and isinstance(item.get("question_id"), str):
                mapped[item["question_id"]] = item
        return mapped, None

    if not isinstance(raw, dict):
        return None, "malformed"

    if raw.get("isError") is True or "error" in raw:
        err_text = json.dumps(raw.get("error", "")).lower()
        return None, "timeout" if "timeout" in err_text else "unavailable"

    if isinstance(raw.get("answers"), dict):
        envelope_defaults = {
            k: raw[k]
            for k in ("backend", "model", "data_destination", "fallback_used", "fallback_info")
            if k in raw
        }
        merged: Dict[str, Any] = {}
        for key, answer in raw["answers"].items():
            if isinstance(answer, dict):
                merged[key] = {**envelope_defaults, **answer}
            else:
                merged[key] = answer
        return merged, None

    if isinstance(raw.get("question_id"), str) and ("probabilities" in raw or "method" in raw):
        return {raw["question_id"]: raw}, None

    return dict(raw), None


def _validate_score_envelope(
    envelope: Any,
    levels: List[str],
) -> Tuple[Optional[Dict[str, Any]], str]:
    """Validate normalized light-decision-mcp or decide score envelope."""
    if not isinstance(envelope, dict):
        return None, "malformed"

    if envelope.get("isError") is True or "error" in envelope:
        err_text = json.dumps(envelope.get("error", "")).lower()
        return None, "timeout" if "timeout" in err_text else "unavailable"

    if envelope.get("method") == "self-judgment":
        raw_reason = envelope.get("fallback_reason")
        if isinstance(raw_reason, str) and raw_reason.strip() and raw_reason != "none":
            return None, raw_reason.strip()
        return None, "self-judgment"

    raw_probs = envelope.get("probabilities")
    if not raw_probs and envelope.get("applied") is False:
        raw_reason = envelope.get("fallback_reason")
        if isinstance(raw_reason, str) and raw_reason.strip() and raw_reason != "none":
            return None, raw_reason.strip()

    if not isinstance(raw_probs, dict) or len(raw_probs) != len(levels):
        return None, "malformed"

    norm_probs: Dict[str, float] = {}
    if set(raw_probs.keys()) == set(levels):
        for label in levels:
            val = raw_probs[label]
            if not _is_valid_probability(val):
                return None, "malformed"
            norm_probs[label] = float(val)
    else:
        for idx, label in enumerate(levels):
            if idx in raw_probs and str(idx) not in raw_probs:
                val = raw_probs[idx]
            elif str(idx) in raw_probs and idx not in raw_probs:
                val = raw_probs[str(idx)]
            else:
                return None, "malformed"
            if not _is_valid_probability(val):
                return None, "malformed"
            norm_probs[label] = float(val)

    if abs(sum(norm_probs.values()) - 1.0) > 0.01:
        return None, "malformed"

    raw_score = envelope.get("score")
    raw_expected = envelope.get("expected_level")
    if raw_score is None and raw_expected is None:
        return None, "malformed"
    if raw_score is not None and not _is_finite_number(raw_score):
        return None, "malformed"
    if raw_expected is not None and not _is_finite_number(raw_expected):
        return None, "malformed"
    if raw_score is not None and raw_expected is not None:
        if abs(float(raw_score) - float(raw_expected)) > 0.02:
            return None, "malformed"

    reported_score = float(raw_score if raw_score is not None else raw_expected)
    if not (0.0 <= reported_score <= float(len(levels) - 1)):
        return None, "malformed"

    expected_from_probs = sum(idx * norm_probs[label] for idx, label in enumerate(levels))
    if abs(reported_score - expected_from_probs) > 0.02:
        return None, "malformed"

    raw_conf = envelope.get("confidence")
    if raw_conf is not None and not _is_valid_probability(raw_conf):
        return None, "malformed"

    raw_prov_conf = envelope.get("provider_confidence")
    if raw_prov_conf is not None and not _is_valid_probability(raw_prov_conf):
        return None, "malformed"

    raw_dest = envelope.get("data_destination") or envelope.get("data") or DEFAULT_LIMIT
    if not isinstance(raw_dest, str) or raw_dest not in DESTINATIONS:
        return None, "malformed"

    if envelope.get("fallback_used") is False:
        effective_backend = envelope.get("backend")
        effective_model = envelope.get("model")
    else:
        effective_backend = envelope.get("backend")
        effective_model = envelope.get("model")

    backend = str(effective_backend).strip() if isinstance(effective_backend, str) and effective_backend.strip() else None
    model = str(effective_model).strip() if isinstance(effective_model, str) and effective_model.strip() else None

    bin_idx = _bin_level(reported_score, len(levels))
    bin_label = levels[bin_idx]
    bin_conf = float(norm_probs[bin_label])

    return {
        "score": reported_score,
        "bin_idx": bin_idx,
        "bin_label": bin_label,
        "bin_conf": bin_conf,
        "probabilities": norm_probs,
        "provider_confidence": float(raw_prov_conf) if raw_prov_conf is not None else None,
        "backend": backend,
        "model": model,
        "data_destination": raw_dest,
    }, "none"


def _accept_shift(
    direction: str,
    conf: float,
    threshold: Optional[float],
    margin: float,
) -> Tuple[bool, str, str]:
    """Evaluate threshold and downgrade margin."""
    if threshold is None:
        return False, "uncalibrated", "uncalibrated"
    if conf < threshold:
        return False, "low-confidence", "low-confidence"
    if direction == "downgrade" and round(margin, 9) < DOWNGRADE_MARGIN:
        return (
            False,
            "low-confidence",
            f"low-confidence (score margin {margin:.2f} < {DOWNGRADE_MARGIN:.2f})",
        )
    return True, "none", "none"


def _own_decision_record(
    question_id: str,
    question: str,
    levels: List[str],
    final_answer: str,
    reason: str,
) -> Dict[str, Any]:
    return {
        "question_id": question_id,
        "question": question,
        "kind": "score",
        "options": list(levels),
        "answer": final_answer,
        "score": None,
        "probabilities": {},
        "confidence": None,
        "provider_confidence": None,
        "method": "self-judgment",
        "data_destination": "in-session",
        "backend": "agent",
        "model": None,
        "calibrated": False,
        "applied": True,
        "fallback_reason": reason,
        "final": final_answer,
    }


def _typed_decision_record(
    question_id: str,
    question: str,
    levels: List[str],
    parsed: Dict[str, Any],
    data_destination: str,
    calibrated: bool,
    accepted: bool,
    record_reason: str,
    baseline_answer: str,
) -> Dict[str, Any]:
    answer = parsed["bin_label"]
    return {
        "question_id": question_id,
        "question": question,
        "kind": "score",
        "options": list(levels),
        "answer": answer,
        "score": round(parsed["score"], 4),
        "probabilities": dict(parsed["probabilities"]),
        "confidence": round(parsed["bin_conf"], 4),
        "provider_confidence": parsed["provider_confidence"],
        "method": "typed-decision",
        "data_destination": data_destination,
        "backend": parsed["backend"] or "decide",
        "model": parsed.get("model"),
        "calibrated": calibrated,
        "applied": accepted,
        "fallback_reason": "none" if accepted else record_reason,
        "final": answer if accepted else baseline_answer,
    }


def build_deterministic_profile(task: TaskCharacteristics) -> AbstractTaskProfile:
    """Deterministic fallback mapping of task characteristics to abstract profile."""
    rec_tier = _complexity_to_tier(task.difficulty)
    reasoning = "high" if rec_tier == "high" else ("low" if rec_tier == "routine" else "medium")

    lat_sens = "high" if task.latency_sensitive else "medium"
    cost_sens = "high" if task.cost_sensitive else "medium"

    is_comp_auth = task.difficulty_source not in ("unknown", "heuristic") and bool(task.difficulty)
    comp_src = task.difficulty_source if is_comp_auth else "deterministic-fallback"
    comp_fallback = not is_comp_auth

    is_reas_auth = bool(task.reasoning_policy)
    if is_reas_auth:
        if task.reasoning_policy in ("highest-supported", "high"):
            reasoning = "high"
        elif task.reasoning_policy in ("lowest-supported", "minimal", "low"):
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


def _fallback_with_own_records(
    task: TaskCharacteristics,
    record_reason: str,
    summary_reason: str,
    ask_complexity: bool,
    ask_reasoning: bool,
) -> Tuple[AbstractTaskProfile, Optional[float], bool, str]:
    det_prof = build_deterministic_profile(task)
    records: List[Dict[str, Any]] = []
    if ask_complexity:
        records.append(
            _own_decision_record(
                COMPLEXITY_QUESTION,
                COMPLEXITY_TEXT,
                COMPLEXITY_LEVELS,
                det_prof.complexity_level,
                record_reason,
            )
        )
    if ask_reasoning:
        records.append(
            _own_decision_record(
                REASONING_QUESTION,
                REASONING_TEXT,
                REASONING_LEVELS,
                det_prof.reasoning_need,
                record_reason,
            )
        )
    det_prof.decisions = records
    return det_prof, None, True, summary_reason


def _evaluate_score_dimension(
    *,
    dim_name: str,
    question_id: str,
    alias_key: str,
    question_text: str,
    levels: List[str],
    baseline_value: str,
    rank_of: Callable[[str], int],
    unpacked: Dict[str, Any],
    policy: Optional[Dict[str, Any]],
    calibration_thresholds: Optional[Dict[str, float]],
    active_limit: Optional[str],
) -> Tuple[str, Optional[float], Optional[float], bool, DimensionProvenance, Dict[str, Any]]:
    """Shared validation, calibration, data-boundary, and DOWNGRADE_MARGIN pipeline for one score question."""
    raw_item = unpacked.get(question_id)
    if raw_item is None:
        raw_item = unpacked.get(alias_key)

    if raw_item is None:
        msg = f"unavailable: {dim_name} score absent"
        return (
            baseline_value,
            None,
            None,
            True,
            DimensionProvenance(
                dimension=dim_name,
                value=baseline_value,
                source="deterministic-fallback",
                fallback_used=True,
                fallback_reason=msg,
            ),
            _own_decision_record(question_id, question_text, levels, baseline_value, "unavailable"),
        )

    parsed, err = _validate_score_envelope(raw_item, levels)
    if parsed is None:
        msg = f"{err}: {dim_name} score not applied"
        return (
            baseline_value,
            None,
            None,
            True,
            DimensionProvenance(
                dimension=dim_name,
                value=baseline_value,
                source="deterministic-fallback",
                fallback_used=True,
                fallback_reason=msg,
            ),
            _own_decision_record(question_id, question_text, levels, baseline_value, err),
        )

    threshold, policy_data = _resolve_question_calibration(
        question_id,
        parsed["backend"],
        parsed.get("model"),
        policy,
        calibration_thresholds,
    )
    eff_data = (
        _farther_destination(parsed["data_destination"], policy_data)
        if policy_data
        else parsed["data_destination"]
    )
    if not _within_data_limit(eff_data, active_limit):
        msg = f"unavailable: data_destination '{eff_data}' exceeds limit '{active_limit}'"
        return (
            baseline_value,
            None,
            None,
            True,
            DimensionProvenance(
                dimension=dim_name,
                value=baseline_value,
                source="deterministic-fallback",
                fallback_used=True,
                fallback_reason=msg,
            ),
            _own_decision_record(question_id, question_text, levels, baseline_value, "unavailable"),
        )

    score_val = parsed["score"]
    conf_val = parsed["bin_conf"]
    cand_value = parsed["bin_label"]
    cand_rank = rank_of(cand_value)
    base_rank = rank_of(baseline_value)
    direction = "upgrade" if cand_rank > base_rank else ("hold" if cand_rank == base_rank else "downgrade")
    margin = (parsed["bin_idx"] + 0.5) - score_val
    accepted, rec_reason, detail_why = _accept_shift(direction, conf_val, threshold, margin)
    record = _typed_decision_record(
        question_id,
        question_text,
        levels,
        parsed,
        eff_data,
        threshold is not None,
        accepted,
        rec_reason,
        baseline_value,
    )
    if accepted:
        return (
            cand_value,
            score_val,
            conf_val,
            False,
            DimensionProvenance(
                dimension=dim_name,
                value=cand_value,
                confidence=conf_val,
                source="typed-decision",
                fallback_used=False,
            ),
            record,
        )

    rej = (
        f"{direction.capitalize()} {dim_name} from {baseline_value} to {cand_value} not applied: "
        f"{detail_why} (confidence {conf_val:.2f})"
    )
    return (
        baseline_value,
        score_val,
        conf_val,
        True,
        DimensionProvenance(
            dimension=dim_name,
            value=baseline_value,
            confidence=conf_val,
            source="deterministic-fallback",
            fallback_used=True,
            fallback_reason=rej,
        ),
        record,
    )


def extract_abstract_task_profile(
    task: TaskCharacteristics,
    decide_scores: Optional[Union[Dict[str, Any], List[Any], Path, str]] = None,
    use_typed_decisions: bool = True,
    project_root: Optional[Path] = None,
    policy: Optional[Dict[str, Any]] = None,
    calibration_thresholds: Optional[Dict[str, float]] = None,
    max_data_destination: Optional[str] = None,
) -> Tuple[AbstractTaskProfile, Optional[float], bool, Optional[str]]:
    """Extract abstract configuration intent from task traits and optional decide score payloads."""
    is_complexity_authoritative = (
        task.difficulty_source not in ("unknown", "heuristic") and bool(task.difficulty)
    )
    is_reasoning_authoritative = bool(task.reasoning_policy)

    if is_complexity_authoritative and is_reasoning_authoritative:
        return build_deterministic_profile(task), None, False, None

    ask_complexity = not is_complexity_authoritative
    ask_reasoning = not is_reasoning_authoritative

    if not use_typed_decisions:
        return _fallback_with_own_records(
            task, "unavailable", "Typed decisions disabled", ask_complexity, ask_reasoning
        )

    project_limit = read_decision_data_limit(project_root)
    active_limit = _stricter_limit(project_limit, max_data_destination)
    if active_limit == "off":
        return _fallback_with_own_records(
            task,
            "off",
            "No typed decision source used (Decision data 'off')",
            ask_complexity,
            ask_reasoning,
        )

    if decide_scores is None:
        return _fallback_with_own_records(
            task,
            "unavailable",
            "No decide score results provided; using deterministic baseline",
            ask_complexity,
            ask_reasoning,
        )

    unpacked, container_err = _unpack_decide_scores(decide_scores)
    if unpacked is None:
        err_code = container_err or "malformed"
        return _fallback_with_own_records(
            task,
            err_code,
            f"Decide score payload rejected ({err_code})",
            ask_complexity,
            ask_reasoning,
        )

    det_base = build_deterministic_profile(task)
    prov: Dict[str, DimensionProvenance] = {}
    decisions: List[Dict[str, Any]] = []
    fallback_dims: List[str] = []
    reported_confs: List[float] = []

    comp_score_val: Optional[float] = None
    comp_conf: Optional[float] = None
    reas_score_val: Optional[float] = None
    reas_conf: Optional[float] = None

    if is_complexity_authoritative:
        comp_fallback = False
        comp_level = task.difficulty
        rec_tier = _complexity_to_tier(comp_level)
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
        comp_level, comp_score_val, comp_conf, comp_fallback, comp_prov, comp_rec = _evaluate_score_dimension(
            dim_name="complexity",
            question_id=COMPLEXITY_QUESTION,
            alias_key="task_complexity",
            question_text=COMPLEXITY_TEXT,
            levels=COMPLEXITY_LEVELS,
            baseline_value=det_base.complexity_level,
            rank_of=lambda lvl: TIER_RANKS[_complexity_to_tier(lvl)],
            unpacked=unpacked,
            policy=policy,
            calibration_thresholds=calibration_thresholds,
            active_limit=active_limit,
        )
        rec_tier = _complexity_to_tier(comp_level)
        decisions.append(comp_rec)
        prov["complexity"] = comp_prov
        prov["tier"] = DimensionProvenance(
            dimension="tier",
            value=rec_tier,
            confidence=comp_prov.confidence,
            source=comp_prov.source,
            fallback_used=comp_prov.fallback_used,
            fallback_reason=comp_prov.fallback_reason,
        )
        if comp_fallback:
            fallback_dims.append("complexity")
        elif comp_conf is not None:
            reported_confs.append(comp_conf)

    if is_reasoning_authoritative:
        reas_fallback = False
        reasoning_need = det_base.reasoning_need
        prov["reasoning"] = DimensionProvenance(
            dimension="reasoning",
            value=reasoning_need,
            confidence=None,
            source="explicit-policy",
            fallback_used=False,
        )
    else:
        reasoning_need, reas_score_val, reas_conf, reas_fallback, reas_prov, reas_rec = (
            _evaluate_score_dimension(
                dim_name="reasoning",
                question_id=REASONING_QUESTION,
                alias_key="reasoning_need",
                question_text=REASONING_TEXT,
                levels=REASONING_LEVELS,
                baseline_value=det_base.reasoning_need,
                rank_of=lambda lvl: REASONING_RANKS[lvl],
                unpacked=unpacked,
                policy=policy,
                calibration_thresholds=calibration_thresholds,
                active_limit=active_limit,
            )
        )
        decisions.append(reas_rec)
        prov["reasoning"] = reas_prov
        if reas_fallback:
            fallback_dims.append("reasoning")
        elif reas_conf is not None:
            reported_confs.append(reas_conf)

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


def add_decide_cli_arguments(parser: argparse.ArgumentParser) -> None:
    """Register shared CLI arguments for normalized decide score intake and policy loading."""
    parser.add_argument("--decide-scores-json", default=None, help="Normalized decide score payload JSON")
    parser.add_argument("--decide-scores-file", type=Path, default=None, help="Path to decide score JSON file")
    parser.add_argument("--decision-policy-json", default=None, help="Calibration policy JSON object")
    parser.add_argument("--decision-policy-file", type=Path, default=None, help="Path to decision-policy.json")
    parser.add_argument(
        "--calibration-thresholds-json",
        default=None,
        help="Direct per-question min_confidence JSON mapping",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root whose Decision data line limits typed decide inputs",
    )
    parser.add_argument(
        "--max-data-destination",
        choices=list(LIMITS),
        default=None,
        help="Explicit maximum data destination override",
    )
    parser.add_argument("--no-typed-decisions", action="store_true", help="Do not apply typed decide scores")


def resolve_decide_cli_inputs(
    args: argparse.Namespace,
) -> Tuple[
    Optional[Union[Dict[str, Any], List[Any], Path, str]],
    Optional[Dict[str, Any]],
    Optional[Dict[str, float]],
]:
    """Extract (scores_input, policy_input, thresholds_input) from parsed CLI arguments."""
    scores_input: Optional[Union[Dict[str, Any], List[Any], Path, str]] = None
    if args.decide_scores_json is not None:
        scores_input = args.decide_scores_json
    elif args.decide_scores_file is not None:
        scores_input = args.decide_scores_file

    policy_input: Optional[Dict[str, Any]] = None
    if args.decision_policy_json is not None:
        policy_input = json.loads(args.decision_policy_json)
    elif args.decision_policy_file is not None:
        policy_input = load_decision_policy(args.decision_policy_file)
    elif args.calibration_thresholds_json is None and scores_input is not None:
        policy_input = load_decision_policy()

    thresholds_input: Optional[Dict[str, float]] = (
        json.loads(args.calibration_thresholds_json)
        if args.calibration_thresholds_json is not None
        else None
    )
    return scores_input, policy_input, thresholds_input


def main() -> int:
    parser = argparse.ArgumentParser(description="Abstract task profiler with normalized decide intake")
    parser.add_argument("--task-json", default="{}", help="TaskCharacteristics JSON object")
    add_decide_cli_arguments(parser)

    args = parser.parse_args()
    task_obj = TaskCharacteristics.from_dict(json.loads(args.task_json))
    scores_input, policy_input, thresholds_input = resolve_decide_cli_inputs(args)

    profile, confidence, fallback_used, fallback_reason = extract_abstract_task_profile(
        task=task_obj,
        decide_scores=scores_input,
        use_typed_decisions=not args.no_typed_decisions,
        project_root=args.project_root,
        policy=policy_input,
        calibration_thresholds=thresholds_input,
        max_data_destination=args.max_data_destination,
    )
    output = {
        "profile": profile.model_dump(),
        "decision_confidence": confidence,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
