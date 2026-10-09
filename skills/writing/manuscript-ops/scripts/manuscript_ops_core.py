#!/usr/bin/env python3
"""Shared, dependency-free helpers for manuscript-ops read-only tools."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1"
ROUTING_POLICY = "needs-v2"
LEGACY_ROUTING_POLICY = "score-v1"
REVIEW_AXIS_IDS = {
    "intent-structure", "factual-sources", "terminology-localization",
    "reader-accessibility", "safety-privacy-legal", "format-layout",
    "images", "reproducibility-recovery", "compatibility-round-trip",
}

DIMENSIONS = (
    "scale",
    "source_complexity",
    "risk",
    "output_complexity",
    "collaboration",
    "reproducibility",
)

HARD_TRIGGERS = (
    "explicit_project",
    "cross_session",
    "large_volume",
    "high_risk_facts",
    "locked_derivatives",
    "reproducible_multi_format",
    "independent_multi_thread_acceptance",
)

SKIP_DIRS = {
    ".git",
    ".jj",
    ".hg",
    ".svn",
    ".tmp",
    ".venv",
    "build",
    "dist",
    "node_modules",
    "__pycache__",
}

SOURCE_GROUPS = {
    "text": {".txt", ".md", ".markdown", ".rst", ".tex", ".rtf"},
    "office": {".docx", ".pdf", ".odt", ".pptx", ".odp", ".xlsx", ".ods", ".csv"},
    "image": {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".svg"},
    "audio": {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"},
    "video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "web": {".html", ".htm", ".mhtml", ".eml", ".msg", ".epub"},
}

DATE_VERSION_RE = re.compile(r"(?<!\d)(\d{4}\.\d{2}\.\d{2})(?:-(\d{2}))?(?!\d)")


class ContractError(ValueError):
    """Raised when an input violates a public manuscript-ops contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ContractError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ContractError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _should_skip(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in relative.parts)


def inspect_repository(root: Path, max_files: int = 5000) -> dict[str, Any]:
    """Inspect file metadata only; never read manuscript contents."""
    root = root.resolve()
    if not root.exists():
        raise ContractError(f"project root does not exist: {root}")
    if not root.is_dir():
        raise ContractError(f"project root is not a directory: {root}")

    count = 0
    total_bytes = 0
    extensions: dict[str, int] = {}
    source_groups: set[str] = set()
    markers: list[str] = []
    truncated = False

    marker_names = {
        "AGENTS.md",
        "README.md",
        "IMPLEMENTATION_PLAN.md",
        "SOURCE_MAP.md",
        "pyproject.toml",
        "package.json",
    }

    for path in root.rglob("*"):
        if _should_skip(path, root) or not path.is_file():
            continue
        count += 1
        if count > max_files:
            truncated = True
            count = max_files
            break
        try:
            total_bytes += path.stat().st_size
        except OSError:
            pass
        suffix = path.suffix.lower() or "<none>"
        extensions[suffix] = extensions.get(suffix, 0) + 1
        for group, suffixes in SOURCE_GROUPS.items():
            if suffix in suffixes:
                source_groups.add(group)
        if path.name in marker_names:
            markers.append(path.relative_to(root).as_posix())

    vcs = []
    if (root / ".jj" / "repo").exists():
        vcs.append(".jj")
    if (root / ".git").is_file() or (root / ".git" / "HEAD").is_file():
        vcs.append(".git")
    if (root / ".hg" / "requires").is_file():
        vcs.append(".hg")
    if (root / ".svn" / "wc.db").is_file():
        vcs.append(".svn")

    ordered_extensions = sorted(extensions.items(), key=lambda item: (-item[1], item[0]))
    return {
        "file_count": count,
        "total_bytes": total_bytes,
        "extensions": dict(ordered_extensions[:25]),
        "source_groups": sorted(source_groups),
        "markers": sorted(markers),
        "version_control_markers": vcs,
        "scan_truncated": truncated,
        "max_files": max_files,
    }


def _automatic_dimensions(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    file_count = int(evidence["file_count"])
    total_bytes = int(evidence["total_bytes"])
    groups = list(evidence["source_groups"])

    if file_count <= 2 and total_bytes <= 1_000_000:
        scale_score = 0
    elif file_count <= 40 and total_bytes <= 20_000_000:
        scale_score = 1
    else:
        scale_score = 2

    if len(groups) <= 1 and file_count <= 2:
        source_score = 0
    elif len(groups) <= 3:
        source_score = 1
    else:
        source_score = 2

    dimensions = {
        name: {
            "score": None,
            "effective_score": 1,
            "unknown": True,
            "evidence": [
                "not established by read-only repository metadata; user evidence required"
            ],
        }
        for name in DIMENSIONS
    }
    dimensions["scale"].update(
        {
            "score": scale_score,
            "effective_score": scale_score,
            "unknown": False,
            "evidence": [
                f"{file_count} files",
                f"{total_bytes} bytes",
                f"scan_truncated={evidence['scan_truncated']}",
            ],
        }
    )
    dimensions["source_complexity"].update(
        {
            "score": source_score,
            "effective_score": source_score,
            "unknown": False,
            "evidence": [f"source groups: {', '.join(groups) if groups else 'none observed'}"],
        }
    )
    return dimensions


def inspect_task_sources(root: Path, task: dict[str, Any], max_files: int) -> dict[str, Any]:
    """Collect declared file inputs only; an output workspace is not a manuscript."""
    sources = task.get("source_paths", [])
    if not isinstance(sources, list) or not all(isinstance(value, str) and value for value in sources):
        raise ContractError("task.source_paths must be a string array of explicit input files")
    if len(sources) > max_files:
        raise ContractError("task.source_paths exceeds the bounded inspection limit")
    extensions: dict[str, int] = {}
    total_bytes = 0
    for value in sources:
        path = Path(value)
        path = path if path.is_absolute() else root / path
        if not path.is_file():
            raise ContractError(f"missing declared source file: {value}")
        total_bytes += path.stat().st_size
        suffix = path.suffix.lower() or "<none>"
        extensions[suffix] = extensions.get(suffix, 0) + 1
    vcs = [marker for marker in (".git", ".jj") if (root / marker).exists()]
    return {
        "root_exists": root.is_dir(), "inventory_scope": "declared_task_files",
        "file_count": len(sources), "total_bytes": total_bytes, "extensions": extensions,
        "source_groups": sorted(name for name, suffixes in SOURCE_GROUPS.items() if set(extensions) & suffixes),
        "markers": [], "version_control_markers": vcs,
        "scan_truncated": False, "max_files": max_files,
    }


def _normalize_dimension(name: str, raw: Any, fallback: dict[str, Any]) -> dict[str, Any]:
    if raw is None:
        return fallback
    if isinstance(raw, int):
        raw = {"score": raw}
    if not isinstance(raw, dict):
        raise ContractError(f"dimension {name!r} must be an integer, object, or null")

    score = raw.get("score")
    if score is not None and (isinstance(score, bool) or score not in (0, 1, 2)):
        raise ContractError(f"dimension {name!r} score must be 0, 1, 2, or null")
    evidence = raw.get("evidence", fallback.get("evidence", []))
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise ContractError(f"dimension {name!r} evidence must be a list of strings")
    if score is None:
        return {
            "score": None,
            "effective_score": 1,
            "unknown": True,
            "evidence": evidence,
        }
    return {
        "score": score,
        "effective_score": score,
        "unknown": False,
        "evidence": evidence,
    }


def select_route(
    dimensions: dict[str, dict[str, Any]],
    hard_triggers: dict[str, bool | None],
    unknowns: Iterable[str],
    *,
    policy: str = ROUTING_POLICY,
) -> tuple[int, str, list[str], bool]:
    """Separate workflow needs from review intensity; replay old gates explicitly."""
    total = sum(int(item["effective_score"]) for item in dimensions.values())
    active_triggers = [name for name, value in hard_triggers.items() if value is True]
    unresolved_triggers = [name for name, value in hard_triggers.items() if value is None]
    if policy not in {ROUTING_POLICY, LEGACY_ROUTING_POLICY}:
        raise ContractError(f"unknown routing policy: {policy!r}")
    if policy == ROUTING_POLICY:
        lifecycle_triggers = {
            "explicit_project", "cross_session", "large_volume",
            "locked_derivatives", "reproducible_multi_format",
        }
        if any(name in lifecycle_triggers for name in active_triggers):
            route = "Project"
        elif unresolved_triggers or any(
            item["unknown"] for item in dimensions.values()
        ) or any(dimensions[name]["score"] != 0 for name in (
            "scale", "source_complexity", "risk", "output_complexity",
        )) or hard_triggers.get("high_risk_facts") is True:
            route = "Structured"
        else:
            route = "Quick"
        return total, route, active_triggers, False
    boundary_escalation = bool(set(unknowns)) and total in (3, 7)
    # An unresolved hard trigger cannot safely be treated as false. Unlike an
    # unknown scored dimension, any one of these conditions would independently
    # force the Project route if confirmed.
    if (
        active_triggers
        or unresolved_triggers
        or total >= 8
        or (total == 7 and boundary_escalation)
    ):
        route = "Project"
    elif total >= 4 or (total == 3 and boundary_escalation):
        route = "Structured"
    else:
        route = "Quick"
    return total, route, active_triggers, boundary_escalation


def valid_probability(value: Any) -> bool:
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def resolve_semantic_route(
    baseline: str,
    dimensions: dict[str, dict[str, Any]],
    hard_triggers: dict[str, bool | None],
    result: Any,
    policy: Any,
) -> tuple[str, dict[str, Any]]:
    """Consume a Host decision; never call a service or infer execution authority."""
    observation: dict[str, Any] = {"applied": False, "fallback_reason": "not_provided"}
    if result is None:
        return baseline, observation
    try:
        answer = result["answers"]["route"]
        choice = answer["choice"]
        probabilities = answer["probabilities"]
        confidence = answer["confidence"]
        if (
            not isinstance(probabilities, dict)
            or not {"Quick", "Structured", "Project"}.issubset(probabilities)
            or set(probabilities) - {"Quick", "Structured", "Project", "InsufficientInfo"}
            or choice not in probabilities
            or not all(valid_probability(value) for value in probabilities.values())
            or not valid_probability(confidence)
            or abs(sum(probabilities.values()) - 1) > 0.001
            or abs(probabilities[choice] - confidence) > 0.001
            or abs(max(probabilities.values()) - confidence) > 0.001
        ):
            raise ValueError("invalid decision distribution")
        observation.update({"model": result.get("model"), "choice": choice, "confidence": confidence})
    except (TypeError, KeyError, ValueError, AttributeError):
        observation["fallback_reason"] = "malformed_result"
        return baseline, observation
    if choice == "InsufficientInfo":
        observation["fallback_reason"] = "insufficient_information"
        return baseline, observation
    if not isinstance(policy, dict) or not valid_probability(policy.get("min_confidence")) or not isinstance(policy.get("calibration_reference"), str) or not policy["calibration_reference"].strip():
        observation["fallback_reason"] = "uncalibrated_policy"
        return baseline, observation
    if confidence < policy["min_confidence"]:
        observation["fallback_reason"] = "low_confidence"
        return baseline, observation
    if (baseline == "Project" and choice != baseline) or (baseline != "Project" and choice == "Project"):
        observation["fallback_reason"] = "workflow_constraint"
        return baseline, observation
    if choice == "Quick" and any(dimensions[name]["score"] != 0 for name in ("scale", "source_complexity", "risk", "output_complexity")):
        observation["fallback_reason"] = "required_review"
        return baseline, observation
    if choice == "Quick" and hard_triggers.get("high_risk_facts") is True:
        observation["fallback_reason"] = "required_review"
        return baseline, observation
    observation.update({"applied": True, "fallback_reason": None})
    return choice, observation


def routing_review_axes(route: str, dimensions: dict, hard_triggers: dict, task: Any) -> list[str]:
    """Compute mandatory content and format checks independently of initialization."""
    if not isinstance(task, dict):
        raise ContractError("task must be an object")
    review_axes = task.get("risk_axes", [])
    if not isinstance(review_axes, list) or not all(isinstance(axis, str) for axis in review_axes):
        raise ContractError("task.risk_axes must be a string array")
    if set(review_axes) - REVIEW_AXIS_IDS:
        raise ContractError("task.risk_axes contains an unknown manuscript review axis")
    review_axes = set(review_axes)
    if dimensions["risk"]["score"] == 2 or hard_triggers.get("high_risk_facts") is True:
        review_axes.add("safety-privacy-legal")
    if route != "Quick":
        review_axes.update({"intent-structure", "reader-accessibility"})
    if (dimensions["risk"]["score"] != 0 or dimensions["source_complexity"]["score"] != 0
            or hard_triggers.get("high_risk_facts") is True):
        review_axes.add("factual-sources")
    deliverables = task.get("deliverables", [])
    if not isinstance(deliverables, list) or any(not isinstance(item, dict) or not isinstance(item.get("format"), str) or item.get("purpose", "deliverable") not in {"deliverable", "qa"} for item in deliverables):
        raise ContractError("task.deliverables must contain format/purpose objects")
    if any(item.get("format") not in {"txt", "markdown"} for item in deliverables):
        review_axes.add("format-layout")
    images = task.get("image_count", 0)
    if not isinstance(images, int) or isinstance(images, bool) or images < 0:
        raise ContractError("task.image_count must be a non-negative integer")
    if images or any(item.get("format") == "pptx" for item in deliverables):
        review_axes.add("images")
    if route == "Project":
        review_axes.update(REVIEW_AXIS_IDS - {"images"})
    return sorted(review_axes)


def build_routing_snapshot(
    root: Path,
    answers: dict[str, Any] | None = None,
    captured_at: str | None = None,
    max_files: int = 5000,
) -> dict[str, Any]:
    answers = answers or {}
    policy = answers.get("routing_policy", ROUTING_POLICY)
    task = answers.get("task", {})
    if not isinstance(task, dict):
        raise ContractError("task must be an object")
    if policy == ROUTING_POLICY:
        repository_evidence = inspect_task_sources(root, task, max_files)
    else:
        repository_evidence = inspect_repository(root, max_files=max_files)
        repository_evidence["root_exists"] = True
    if policy == LEGACY_ROUTING_POLICY:
        dimensions = _automatic_dimensions(repository_evidence)
    else:
        dimensions = {
            name: {
                "score": None, "effective_score": 1, "unknown": True,
                "evidence": ["workspace metadata does not establish this task dimension"],
            }
            for name in DIMENSIONS
        }
        scope = task.get("scope", "unknown")
        if scope not in {"bounded", "long-form", "unknown"}:
            raise ContractError("task.scope must be bounded, long-form, or unknown")
        if scope != "unknown":
            score = 0 if scope == "bounded" else 2
            dimensions["scale"] = {
                "score": score, "effective_score": score, "unknown": False,
                "evidence": [f"task scope: {scope}; unrelated workspace files excluded"],
            }
    answer_dimensions = answers.get("dimensions", {})
    if not isinstance(answer_dimensions, dict):
        raise ContractError("dimensions must be an object")
    for name in DIMENSIONS:
        dimensions[name] = _normalize_dimension(
            name,
            answer_dimensions.get(name),
            dimensions[name],
        )

    raw_triggers = answers.get("hard_triggers", {})
    if not isinstance(raw_triggers, dict):
        raise ContractError("hard_triggers must be an object")
    hard_triggers: dict[str, bool | None] = {}
    for name in HARD_TRIGGERS:
        value = raw_triggers.get(name)
        if not (isinstance(value, bool) or value is None):
            raise ContractError(f"hard trigger {name!r} must be true, false, or null")
        hard_triggers[name] = value
    lifecycle = task.get("lifecycle_required")
    if lifecycle is not None and not isinstance(lifecycle, bool):
        raise ContractError("task.lifecycle_required must be a boolean or null")
    if policy == ROUTING_POLICY and lifecycle is True:
        hard_triggers["cross_session"] = True

    derived_triggers: dict[str, bool] = {}
    if dimensions["scale"]["score"] is not None:
        derived_triggers["large_volume"] = dimensions["scale"]["score"] == 2
    if dimensions["risk"]["score"] is not None:
        derived_triggers["high_risk_facts"] = dimensions["risk"]["score"] == 2
    for name, active in derived_triggers.items():
        if active and name in raw_triggers and raw_triggers[name] is False:
            raise ContractError(
                f"hard trigger {name!r} cannot be false when its paired dimension scores 2"
            )
        if active:
            hard_triggers[name] = True
        elif name not in raw_triggers:
            hard_triggers[name] = False

    unknowns = list(answers.get("unknowns", []))
    if not all(isinstance(item, str) for item in unknowns):
        raise ContractError("unknowns must be a list of strings")
    for name, value in dimensions.items():
        if value["unknown"] and name not in unknowns:
            unknowns.append(name)
    for name, value in hard_triggers.items():
        if value is None and f"hard_trigger:{name}" not in unknowns:
            unknowns.append(f"hard_trigger:{name}")

    total, route, active_triggers, boundary_escalation = select_route(
        dimensions,
        hard_triggers,
        unknowns,
        policy=policy,
    )
    semantic_result = answers.get("semantic_result")
    semantic_policy = answers.get("semantic_policy")
    if policy == ROUTING_POLICY:
        route, semantic_judgment = resolve_semantic_route(
            route, dimensions, hard_triggers, semantic_result, semantic_policy,
        )
    else:
        semantic_judgment = {"applied": False, "fallback_reason": "legacy_policy"}

    reasons = [f"effective six-dimension total is {total}"]
    if active_triggers:
        reasons.append(f"hard trigger(s): {', '.join(active_triggers)}")
    unresolved_triggers = [
        name for name, value in hard_triggers.items() if value is None
    ]
    if unresolved_triggers and policy == LEGACY_ROUTING_POLICY:
        reasons.append(
            "unresolved hard trigger(s) require Project: "
            + ", ".join(unresolved_triggers)
        )
    if boundary_escalation:
        reasons.append("unknown item at a routing boundary requires upward routing")
    if unknowns:
        reasons.append(f"unknowns preserved: {', '.join(sorted(set(unknowns)))}")
    review_axes = routing_review_axes(route, dimensions, hard_triggers, task)
    reasons.append(f"{policy}: workflow requirements select {route}; risk sets review requirements")

    next_actions = {
        "Quick": ("perform_bounded_task", None),
        "Structured": ("prepare_lightweight_brief_and_review_plan", None),
        "Project": (
            "handoff_discovery",
            "Activate clarify for one-session decisions or decision-map for multi-session fog using host syntax; then activate manuscript-ops with resume.",
        ),
    }
    next_action, next_invocation = next_actions[route]

    return {
        "schema_version": SCHEMA_VERSION,
        "routing_policy": policy,
        "task": task,
        "semantic_result": semantic_result,
        "semantic_policy": semantic_policy,
        "semantic_judgment": semantic_judgment,
        "captured_at": captured_at or utc_now(),
        "root": str(root.resolve()),
        "dimensions": dimensions,
        "hard_triggers": hard_triggers,
        "repository_evidence": repository_evidence,
        "unknowns": sorted(set(unknowns)),
        "total": total,
        "route": route,
        "required_review_axes": sorted(review_axes),
        "needs_initialization": route == "Project",
        "reasons": reasons,
        "next_action": next_action,
        "next_invocation": next_invocation,
    }


def extract_date_versions(values: Iterable[str]) -> set[str]:
    versions: set[str] = set()
    for value in values:
        for match in DATE_VERSION_RE.finditer(value):
            base, suffix = match.groups()
            try:
                date.fromisoformat(base.replace(".", "-"))
            except ValueError:
                continue
            if suffix is not None and int(suffix) < 2:
                continue
            versions.add(base if suffix is None else f"{base}-{suffix}")
    return versions


def next_date_version(base_date: str, existing_values: Iterable[str]) -> str:
    try:
        date.fromisoformat(base_date.replace(".", "-"))
    except ValueError as exc:
        raise ContractError("date must use a valid YYYY.MM.DD value") from exc
    if not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", base_date):
        raise ContractError("date must use YYYY.MM.DD")

    existing = extract_date_versions(existing_values)
    same_day = {
        version
        for version in existing
        if version == base_date or version.startswith(f"{base_date}-")
    }
    if not same_day:
        return base_date
    observed_suffixes = [
        1 if version == base_date else int(version.rsplit("-", 1)[1])
        for version in same_day
    ]
    suffix = max(2, max(observed_suffixes) + 1)
    return f"{base_date}-{suffix:02d}"


def ensure_within_root(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    resolved = (root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ContractError(f"path escapes project root: {candidate}") from exc
    return resolved


def dump_json(data: Any, pretty: bool = True) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2 if pretty else None,
        sort_keys=False,
    )
