#!/usr/bin/env python3
"""Schema, profile, brief, routing, format-registry, and lifecycle state validation."""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from manuscript_ops_core import (
    DIMENSIONS,
    HARD_TRIGGERS,
    REVIEW_AXIS_IDS,
    ROUTING_POLICY,
    ContractError,
    ensure_within_root,
    load_json,
    parse_timestamp,
    resolve_semantic_route,
    routing_review_axes,
    select_route,
    sha256_file,
    utc_now,
)

CANONICAL_FORMAT_REGISTRY = (
    Path(__file__).resolve().parents[1] / "assets" / "format-registry.json"
)
CANONICAL_CAPABILITY_MAP = (
    Path(__file__).resolve().parents[1] / "assets" / "platform-capability-map.json"
)
CANONICAL_ADAPTER_FIELDS = {
    "format",
    "tier",
    "extensions",
    "media_types",
    "operations",
    "required_dependencies",
    "optional_dependencies",
    "validation_dependencies",
    "blocking_qa_gaps",
    "validation",
    "degradation",
}
ALLOWED_ORIGINS = {"资料发现", "用户决定", "规则推导"}
ALLOWED_CAPABILITIES = {"supported", "conditional", "unsupported", "not_applicable"}
OPERATION_KEYS = {"read", "edit", "generate", "render", "visual_qa", "round_trip"}
TIER1_IDS = {"txt", "markdown", "docx", "pdf", "html", "epub", "pptx"}
SOURCE_ADAPTER_IDS = {"web", "email", "image-scan", "audio", "video", "transcript"}
CORE_PROJECT_REVIEW_AXES = REVIEW_AXIS_IDS - {"images"}
GATE_ALIASES = {
    "brief-approved": "current-brief",
    "baseline": "current-baseline",
    "framework-approved": "current-framework",
    "source-locked": "current-source-locked",
    "final-approved": "current-final",
    "publish-approved": "current-publish",
}
PHASE_GATES = {
    "brief-approved": {"brief-approved"},
    "initialized": {"brief-approved", "baseline"},
    "framework-approved": {"brief-approved", "baseline", "framework-approved"},
    "working": {"brief-approved", "baseline", "framework-approved"},
    "candidate": {"brief-approved", "baseline", "framework-approved"},
    "source-locked": {"brief-approved", "baseline", "framework-approved", "source-locked"},
    "deriving": {"brief-approved", "baseline", "framework-approved", "source-locked"},
    "final-approved": {
        "brief-approved",
        "baseline",
        "framework-approved",
        "source-locked",
        "final-approved",
    },
    "published": {
        "brief-approved",
        "baseline",
        "framework-approved",
        "source-locked",
        "final-approved",
        "publish-approved",
    },
    "archived": {
        "brief-approved",
        "baseline",
        "framework-approved",
        "source-locked",
        "final-approved",
        "publish-approved",
    },
}
MATRIX_PHASES = set(PHASE_GATES) - {"brief-approved", "initialized"}
REPORT_PHASES = {
    "framework-approved",
    "candidate",
    "source-locked",
    "deriving",
    "final-approved",
    "published",
    "archived",
}
FINAL_PHASES = {"final-approved", "published", "archived"}
REVIEW_GATES = {"framework-approved", "source-locked", "final-approved"}
GATE_REVIEW_MILESTONES = {
    "framework-approved": "outline",
    "source-locked": "source-lock",
    "final-approved": "final",
}
PHASE_REVIEW_GATE = {
    "framework-approved": "framework-approved",
    "source-locked": "source-locked",
    "deriving": "source-locked",
    "final-approved": "final-approved",
    "published": "final-approved",
    "archived": "final-approved",
}
REVIEW_MILESTONES = {"outline", "batch", "candidate", "source-lock", "final"}
PHASE_ACTIVE_BATCH_KINDS = {
    "brief-approved": set(),
    "initialized": {"outline"},
    "framework-approved": {"content"},
    "working": {"content"},
    "candidate": {"candidate"},
    "source-locked": {"source-lock", "derivative"},
    "deriving": {"derivative"},
    "final-approved": {"final"},
    "published": set(),
    "archived": set(),
}
FORCE_CUMULATIVE_BATCH_KINDS = {"outline", "candidate", "final"}
CAPABILITY_OPERATIONS = {
    "read",
    "edit",
    "generate",
    "render",
    "visual_qa",
    "round_trip",
    "structural_qa",
    "standards_validation",
    "runtime_qa",
    "accessibility_qa",
    "version_control",
}
DATE_VERSION_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}(?:-\d{2})?$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SOURCE_USES = {"factual", "context", "style", "incoming"}
BRIEF_REPRODUCIBILITY_POLICIES = {"required", "not_required"}
BRIEF_VISUAL_QA_POLICIES = {"full", "sampled", "not_applicable"}
BATCH_REVIEW_MILESTONES = {
    "outline": "outline",
    "content": "batch",
    "candidate": "candidate",
    "source-lock": "source-lock",
    "derivative": "batch",
    "final": "final",
}


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []
        self.checks: list[dict[str, str]] = []

    def ok(self, code: str, message: str) -> None:
        self.checks.append({"code": code, "message": message})

    def warn(self, code: str, message: str) -> None:
        self.warnings.append({"code": code, "message": message})

    def error(self, code: str, message: str) -> None:
        self.errors.append({"code": code, "message": message})

    @property
    def status(self) -> str:
        if self.errors:
            return "BLOCKED"
        if self.warnings:
            return "DEGRADED"
        return "READY"

    @property
    def exit_code(self) -> int:
        return 2 if self.errors else (1 if self.warnings else 0)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1",
            "validated_at": utc_now(),
            "root": str(self.root),
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks": self.checks,
        }


def read_required(path: Path, report: Report) -> dict[str, Any] | None:
    if not path.is_file():
        report.error("MISSING_STATE_FILE", f"missing {path.relative_to(report.root)}")
        return None
    try:
        value = load_json(path)
    except ContractError as exc:
        report.error("INVALID_JSON", str(exc))
        return None
    if not isinstance(value, dict):
        report.error("INVALID_STATE_OBJECT", f"{path} must contain a JSON object")
        return None
    report.ok("JSON_VALID", str(path.relative_to(report.root)))
    return value


def valid_date_version(value: Any) -> bool:
    if not isinstance(value, str) or not DATE_VERSION_RE.fullmatch(value):
        return False
    if value[-3:-2] == "-" and int(value[-2:]) < 2:
        return False
    try:
        datetime.strptime(value[:10], "%Y.%m.%d")
    except ValueError:
        return False
    return True


def validate_timestamp(value: Any, code: str, report: Report) -> datetime | None:
    try:
        return parse_timestamp(str(value))
    except (ContractError, ValueError) as exc:
        report.error(code, f"invalid timestamp {value!r}: {exc}")
        return None


def validate_hashed_path(
    relative: Any,
    expected: Any,
    code_prefix: str,
    report: Report,
) -> Path | None:
    if not isinstance(relative, str) or not relative:
        report.error(f"{code_prefix}_PATH", "evidence path must be a non-empty string")
        return None
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        report.error(f"{code_prefix}_HASH", f"invalid SHA-256 for {relative}")
        return None
    try:
        target = ensure_within_root(report.root, Path(relative))
    except ContractError as exc:
        report.error(f"{code_prefix}_PATH", str(exc))
        return None
    if not target.is_file():
        report.error(f"{code_prefix}_MISSING", f"missing evidence file: {relative}")
        return None
    observed = sha256_file(target)
    if observed.lower() != expected.lower():
        report.error(f"{code_prefix}_MISMATCH", f"hash mismatch: {relative}")
        return None
    report.ok(f"{code_prefix}_HASH", relative)
    return target


def string_array(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and item for item in value)
    )


def unwrap_profile_value(
    wrapper: Any,
    label: str,
    report: Report,
    *,
    allow_null: bool = False,
) -> Any:
    if not isinstance(wrapper, dict):
        report.error("PROFILE_WRAPPER", f"{label} must be a provenance wrapper")
        return None
    if wrapper.get("origin") not in ALLOWED_ORIGINS:
        report.error("PROFILE_ORIGIN", f"{label} has an invalid origin")
    evidence = wrapper.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        report.error("PROFILE_EVIDENCE", f"{label} requires provenance evidence")
    if "value" not in wrapper:
        report.error("PROFILE_VALUE", f"{label} has no value")
        return None
    value = wrapper["value"]
    if value is None and not allow_null:
        report.error("PROFILE_VALUE", f"{label} cannot be null")
    if "confirmed_at" in wrapper:
        validate_timestamp(wrapper["confirmed_at"], "PROFILE_CONFIRMED_AT", report)
    return value


def validate_snapshot_files(
    snapshot: Any,
    code: str,
    report: Report,
) -> tuple[dict[str, str], datetime | None, str | None]:
    normalized: dict[str, str] = {}
    if not isinstance(snapshot, dict):
        report.error(code, "artifact_snapshot must be an object")
        return normalized, None, None
    captured_value = snapshot.get("captured_at")
    captured = validate_timestamp(captured_value, f"{code}_TIME", report)
    files = snapshot.get("files")
    if not isinstance(files, list) or not files:
        report.error(f"{code}_FILES", "frozen snapshot requires at least one file")
        return normalized, captured, (
            captured_value if isinstance(captured_value, str) else None
        )
    for entry in files:
        if not isinstance(entry, dict):
            report.error(f"{code}_FILES", "snapshot file entry must be an object")
            continue
        path = validate_hashed_path(entry.get("path"), entry.get("sha256"), code, report)
        if path:
            relative = path.relative_to(report.root).as_posix()
            if relative in normalized:
                report.error(f"{code}_FILES", f"duplicate snapshot path: {relative}")
            normalized[relative] = str(entry["sha256"]).lower()
    return normalized, captured, (
        captured_value if isinstance(captured_value, str) else None
    )


def validate_profile(profile: dict[str, Any], report: Report) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    if profile.get("schema_version") != "1":
        report.error("PROFILE_SCHEMA", "ProjectProfile schema_version must be 1")

    for field in (
        "date_version",
        "project_root",
        "route",
        "languages",
        "formats",
        "dependencies",
        "capabilities_snapshot",
        "snapshot_max_age_hours",
        "unknowns",
    ):
        normalized[field] = unwrap_profile_value(
            profile.get(field),
            field,
            report,
            allow_null=field == "capabilities_snapshot",
        )

    if not valid_date_version(normalized.get("date_version")):
        report.error("PROFILE_VERSION", "date_version must be a valid YYYY.MM.DD[-NN]")

    root_value = normalized.get("project_root")
    if isinstance(root_value, str):
        try:
            resolved_root = ensure_within_root(report.root, Path(root_value))
            if resolved_root != report.root:
                report.error("PROFILE_ROOT", "project_root does not resolve to validator root")
        except ContractError as exc:
            report.error("PROFILE_ROOT", str(exc))
    else:
        report.error("PROFILE_ROOT", "project_root must be a string")

    if normalized.get("route") != "Project":
        report.error("PROFILE_ROUTE", "machine project state requires route=Project")

    paths = profile.get("paths")
    normalized_paths: dict[str, str] = {}
    if not isinstance(paths, dict) or not paths:
        report.error("PROFILE_PATHS", "ProjectProfile paths must be a non-empty object")
    else:
        for role, wrapper in paths.items():
            value = unwrap_profile_value(wrapper, f"paths.{role}", report)
            if not isinstance(value, str) or not value:
                report.error("PROFILE_PATH_VALUE", f"path role {role!r} requires a path")
                continue
            try:
                resolved = ensure_within_root(report.root, Path(value))
            except ContractError as exc:
                report.error("PROFILE_PATH_ESCAPE", str(exc))
                continue
            if not resolved.exists():
                report.warn(
                    "PROFILE_PATH_MISSING",
                    f"mapped role {role!r} does not exist yet: {value}",
                )
            normalized_paths[role] = value
    normalized["paths"] = normalized_paths

    for field in ("languages", "formats"):
        value = normalized.get(field)
        if (
            not isinstance(value, list)
            or not value
            or not all(isinstance(item, str) and item for item in value)
        ):
            report.error("PROFILE_LIST", f"{field} must be a non-empty string array")
        elif len(value) != len(set(value)):
            report.error("PROFILE_LIST", f"{field} values must be unique")
        elif any(item != item.strip().lower() for item in value):
            report.error(
                "PROFILE_LIST",
                f"{field} values must use normalized lowercase identifiers",
            )
    dependencies = normalized.get("dependencies")
    if not isinstance(dependencies, list):
        report.error("PROFILE_DEPENDENCIES", "dependencies must be an array")
    unknowns = normalized.get("unknowns")
    if not isinstance(unknowns, list) or not all(
        isinstance(item, str) for item in unknowns
    ):
        report.error("PROFILE_UNKNOWNS", "unknowns must be a string array")

    capability = normalized.get("capabilities_snapshot")
    if capability is not None:
        if not isinstance(capability, str) or not capability:
            report.error(
                "PROFILE_CAPABILITIES",
                "capabilities_snapshot must be null or a path",
            )
        else:
            try:
                target = ensure_within_root(report.root, Path(capability))
                if not target.is_file():
                    report.warn(
                        "PROFILE_CAPABILITIES",
                        f"capability snapshot not found: {capability}",
                    )
            except ContractError as exc:
                report.error("PROFILE_CAPABILITIES", str(exc))

    max_age = normalized.get("snapshot_max_age_hours")
    if (
        not isinstance(max_age, (int, float))
        or isinstance(max_age, bool)
        or max_age <= 0
    ):
        report.error("PROFILE_FRESHNESS", "snapshot_max_age_hours must be positive")

    vcs = profile.get("version_control")
    normalized_vcs: dict[str, Any] = {}
    if not isinstance(vcs, dict):
        report.error("PROFILE_VCS", "version_control must be an object")
    else:
        expected = {"system", "tested_baseline", "colocated", "remote_allowed"}
        if set(vcs) != expected:
            report.error("PROFILE_VCS", f"version_control keys must be {sorted(expected)}")
        for field in expected:
            normalized_vcs[field] = unwrap_profile_value(
                vcs.get(field),
                f"version_control.{field}",
                report,
            )
        if not isinstance(normalized_vcs.get("system"), str):
            report.error("PROFILE_VCS", "version_control.system must be a string")
        if not isinstance(normalized_vcs.get("tested_baseline"), str):
            report.error(
                "PROFILE_VCS", "version_control.tested_baseline must be a string"
            )
        for field in ("colocated", "remote_allowed"):
            if not isinstance(normalized_vcs.get(field), bool):
                report.error("PROFILE_VCS", f"version_control.{field} must be boolean")
    normalized["version_control"] = normalized_vcs
    report.ok("PROFILE_PROVENANCE", "all configurable Profile values checked")
    return normalized


def validate_brief(
    profile: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
    report: Report,
) -> dict[str, Any] | None:
    brief_value = profile.get("paths", {}).get("brief")
    if not isinstance(brief_value, str):
        report.error("BRIEF_PATH", "ProjectProfile has no resolved Brief path")
        return None
    try:
        path = ensure_within_root(report.root, Path(brief_value))
    except ContractError as exc:
        report.error("BRIEF_PATH", str(exc))
        return None
    if not path.is_file():
        report.error("BRIEF_MISSING", f"missing approved ManuscriptBrief: {brief_value}")
        return None
    if path.suffix.lower() != ".md":
        report.error("BRIEF_FORMAT", "ManuscriptBrief must use the Markdown contract")
        return None
    text = path.read_text(encoding="utf-8")
    headings = {
        "## Goal",
        "## Audience and use",
        "## Scope",
        "## Source authority",
        "## Framework",
        "## Deliverables",
        "## Review and gates",
        "## Acceptance",
        "## Risks, assumptions, and open questions",
        "## Approval",
    }
    missing_headings = sorted(heading for heading in headings if heading not in text)
    if missing_headings:
        report.error("BRIEF_STRUCTURE", f"Brief omits headings: {missing_headings}")
    fields = {
        match.group(1).strip(): match.group(2).strip()
        for match in re.finditer(r"^- ([^:\n]+):[ \t]*(.*)$", text, re.MULTILINE)
    }
    required_fields = {
        "Schema version",
        "Date version",
        "Approval state",
        "Primary audience",
        "Reading environment",
        "Required accessibility or localization",
        "Included",
        "Excluded",
        "Authoritative sources",
        "Reference-only material",
        "Incoming draft status",
        "Prohibited or unavailable sources",
        "Approved outline or outline acceptance rule",
        "Required terminology",
        "Content boundaries",
        "Applicable review axes",
        "Required independent milestones",
        "Human gates",
        "Content",
        "Sources",
        "Format",
        "Privacy and safety",
        "Reproducibility",
        "Risks",
        "Assumptions",
        "Open questions",
        "Approver",
        "Exact confirmation",
        "Confirmed at",
    }
    missing_fields = sorted(
        field for field in required_fields if not fields.get(field, "").strip()
    )
    if (
        "Target-reader prerequisites" in fields
        and not fields["Target-reader prerequisites"].strip()
    ):
        missing_fields.append("Target-reader prerequisites")
        missing_fields.sort()
    if missing_fields:
        report.error("BRIEF_FIELDS", f"Brief has unresolved fields: {missing_fields}")
    if fields.get("Schema version") != "1":
        report.error("BRIEF_SCHEMA", "Brief Schema version must be 1")
    if fields.get("Date version") != profile.get("date_version"):
        report.error("BRIEF_VERSION", "Brief and ProjectProfile date versions differ")
    if fields.get("Approval state", "").lower() != "approved":
        report.error("BRIEF_APPROVAL", "Brief Approval state must be approved")
    brief_confirmed_at = validate_timestamp(
        fields.get("Confirmed at"),
        "BRIEF_CONFIRMATION_TIME",
        report,
    )

    deliverable_rows: list[list[str]] = []
    normalized_deliverables: list[dict[str, str]] = []
    in_deliverables = False
    for line in text.splitlines():
        if line == "## Deliverables":
            in_deliverables = True
            continue
        if in_deliverables and line.startswith("## "):
            break
        if in_deliverables and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if (
                len(cells) == 6
                and cells[0] != "Deliverable"
                and not all(set(cell) <= {"-", ":"} for cell in cells)
            ):
                deliverable_rows.append(cells)
    if not deliverable_rows or any(not all(row) for row in deliverable_rows):
        report.error(
            "BRIEF_DELIVERABLES",
            "Brief requires at least one complete deliverable row",
        )
    else:
        languages = {str(value).lower() for value in profile.get("languages", [])}
        formats = {str(value).lower() for value in profile.get("formats", [])}
        row_languages = {row[1].lower() for row in deliverable_rows}
        row_formats = {row[2].lower() for row in deliverable_rows}
        if languages != row_languages:
            report.error(
                "BRIEF_DELIVERABLES",
                "Brief deliverable languages must exactly match ProjectProfile languages",
            )
        if formats != row_formats:
            report.error(
                "BRIEF_DELIVERABLES",
                "Brief deliverable formats must exactly match ProjectProfile formats",
            )
        seen_paths: set[str] = set()
        for row in deliverable_rows:
            name, language, format_id, reproducible, visual_qa, stable_path = row
            try:
                resolved = ensure_within_root(report.root, Path(stable_path))
                normalized_path = resolved.relative_to(report.root).as_posix()
            except (ContractError, ValueError) as exc:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} has an unsafe stable path: {exc}",
                )
                continue
            if Path(stable_path).is_absolute() or normalized_path in {"", "."}:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} stable path must be project-relative",
                )
                continue
            if normalized_path in seen_paths:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"duplicate deliverable stable path: {normalized_path}",
                )
                continue
            seen_paths.add(normalized_path)
            adapter = adapters.get(format_id.lower())
            if adapter is None:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} references unknown format {format_id!r}",
                )
            else:
                path_suffix = Path(normalized_path).suffix.lower()
                extensions = {
                    str(extension).lower()
                    for extension in adapter.get("extensions", [])
                    if isinstance(extension, str)
                }
                if extensions and path_suffix not in extensions:
                    report.error(
                        "BRIEF_DELIVERABLES",
                        f"deliverable {name!r} path {normalized_path!r} does not match "
                        f"{format_id.lower()} extensions {sorted(extensions)}",
                    )
                suffix_owners = {
                    adapter_key
                    for adapter_key, candidate in adapters.items()
                    if path_suffix
                    and path_suffix
                    in {
                        str(extension).lower()
                        for extension in candidate.get("extensions", [])
                        if isinstance(extension, str)
                    }
                }
                if suffix_owners and format_id.lower() not in suffix_owners:
                    report.error(
                        "BRIEF_DELIVERABLES",
                        f"deliverable {name!r} suffix {path_suffix!r} belongs to "
                        f"{sorted(suffix_owners)}, not {format_id.lower()}",
                    )
            reproducibility_policy = reproducible.strip().lower()
            if reproducibility_policy not in BRIEF_REPRODUCIBILITY_POLICIES:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} Reproducible must be required or not_required",
                )
            visual_qa_policy = visual_qa.strip().lower()
            if visual_qa_policy not in BRIEF_VISUAL_QA_POLICIES:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} Visual QA must be full, sampled, or not_applicable",
                )
            normalized_deliverables.append(
                {
                    "name": name,
                    "language": language.lower(),
                    "format": format_id.lower(),
                    "reproducible": reproducibility_policy,
                    "visual_qa": visual_qa_policy,
                    "path": normalized_path,
                }
            )
    report.ok("BRIEF_APPROVED", brief_value)
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "approver": fields.get("Approver", "").strip(),
        "exact_confirmation": fields.get("Exact confirmation", "").strip(),
        "confirmed_at": fields.get("Confirmed at", "").strip(),
        "confirmed_time": brief_confirmed_at,
        "deliverables": normalized_deliverables,
        "source_expectations": {
            "authoritative": fields.get("Authoritative sources", "").strip(),
            "reference-only": fields.get("Reference-only material", "").strip(),
            "incoming-draft": fields.get("Incoming draft status", "").strip(),
        },
    }


def validate_routing(
    snapshot: dict[str, Any],
    profile: dict[str, Any],
    report: Report,
    now: datetime,
) -> None:
    if snapshot.get("schema_version") != "1":
        report.error("ROUTING_SCHEMA", "RoutingSnapshot schema_version must be 1")
    dimensions = snapshot.get("dimensions")
    normalized_dimensions: dict[str, dict[str, Any]] = {}
    if not isinstance(dimensions, dict) or set(dimensions) != set(DIMENSIONS):
        report.error(
            "ROUTING_DIMENSIONS",
            "routing snapshot must contain exactly six dimensions",
        )
    else:
        for name in DIMENSIONS:
            item = dimensions[name]
            if not isinstance(item, dict):
                report.error("ROUTING_DIMENSION", f"{name} must be an object")
                continue
            score = item.get("score")
            effective = item.get("effective_score")
            unknown = item.get("unknown")
            evidence = item.get("evidence")
            if score is not None and (isinstance(score, bool) or score not in (0, 1, 2)):
                report.error("ROUTING_SCORE", f"{name}.score must be 0, 1, 2, or null")
            if not isinstance(unknown, bool):
                report.error("ROUTING_UNKNOWN", f"{name}.unknown must be boolean")
            expected_effective = 1 if score is None else score
            if effective != expected_effective:
                report.error(
                    "ROUTING_EFFECTIVE",
                    f"{name}.effective_score must be {expected_effective}",
                )
            if unknown is not (score is None):
                report.error(
                    "ROUTING_UNKNOWN",
                    f"{name}.unknown is inconsistent with score",
                )
            if (
                not isinstance(evidence, list)
                or not evidence
                or not all(isinstance(value, str) and value for value in evidence)
            ):
                report.error("ROUTING_EVIDENCE", f"{name}.evidence must be non-empty")
            if (
                (score is None or score in (0, 1, 2))
                and effective == expected_effective
                and isinstance(unknown, bool)
            ):
                normalized_dimensions[name] = item

    hard_triggers = snapshot.get("hard_triggers")
    valid_triggers = isinstance(hard_triggers, dict) and set(hard_triggers) == set(
        HARD_TRIGGERS
    )
    if not valid_triggers:
        report.error(
            "ROUTING_TRIGGERS",
            "routing snapshot must contain exactly all hard triggers",
        )
    else:
        for name, value in hard_triggers.items():
            if not (isinstance(value, bool) or value is None):
                report.error(
                    "ROUTING_TRIGGER_VALUE",
                    f"{name} must be true, false, or null",
                )
                valid_triggers = False

    unknowns = snapshot.get("unknowns")
    if not isinstance(unknowns, list) or not all(
        isinstance(item, str) for item in unknowns
    ):
        report.error("ROUTING_UNKNOWNS", "unknowns must be a string array")
        unknowns = []
    else:
        required_unknowns = {
            name
            for name, item in normalized_dimensions.items()
            if item.get("unknown") is True
        }
        if isinstance(hard_triggers, dict):
            required_unknowns.update(
                f"hard_trigger:{name}"
                for name, value in hard_triggers.items()
                if value is None
            )
        missing_unknowns = sorted(required_unknowns - set(unknowns))
        if missing_unknowns:
            report.error(
                "ROUTING_UNKNOWNS",
                f"missing unknown markers: {missing_unknowns}",
            )

    policy = snapshot.get("routing_policy")
    if policy != ROUTING_POLICY:
        report.error(
            "ROUTING_POLICY",
            f"unsupported routing policy: {policy!r}; expected {ROUTING_POLICY!r}",
        )
        return

    if len(normalized_dimensions) == len(DIMENSIONS) and valid_triggers:
        if (
            normalized_dimensions["scale"]["score"] == 2
            and not hard_triggers["large_volume"]
        ):
            report.error(
                "ROUTING_DERIVED_TRIGGER",
                "scale score 2 requires large_volume=true",
            )
        if (
            normalized_dimensions["risk"]["score"] == 2
            and not hard_triggers["high_risk_facts"]
        ):
            report.error(
                "ROUTING_DERIVED_TRIGGER",
                "risk score 2 requires high_risk_facts=true",
            )
        total, route, _, _ = select_route(
            normalized_dimensions,
            hard_triggers,
            unknowns,
            policy=policy,
        )
        route, judgment = resolve_semantic_route(
            route,
            normalized_dimensions,
            hard_triggers,
            snapshot.get("semantic_result"),
            snapshot.get("semantic_policy"),
        )
        if snapshot.get("semantic_judgment") != judgment:
            report.error(
                "ROUTING_SEMANTIC",
                "stored judgment differs from the bounded decision replay",
            )
        if snapshot.get("needs_initialization") is not (route == "Project"):
            report.error(
                "ROUTING_INITIALIZATION",
                "initialization is required only for Project",
            )
        axes = snapshot.get("required_review_axes")
        if not isinstance(axes, list) or any(
            not isinstance(axis, str) or axis not in REVIEW_AXIS_IDS for axis in axes
        ):
            report.error(
                "ROUTING_REVIEW_AXES",
                "required_review_axes must name manuscript axes",
            )
        else:
            try:
                expected_axes = routing_review_axes(
                    route,
                    normalized_dimensions,
                    hard_triggers,
                    snapshot.get("task", {}),
                )
                if axes != expected_axes:
                    report.error(
                        "ROUTING_REVIEW_AXES",
                        f"required_review_axes must match the task's mandatory checks: {expected_axes}",
                    )
            except ContractError as exc:
                report.error("ROUTING_TASK", str(exc))
        if snapshot.get("total") != total:
            report.error(
                "ROUTING_TOTAL",
                f"stored total does not match recomputed total {total}",
            )
        if snapshot.get("route") != route:
            report.error(
                "ROUTING_ROUTE",
                f"stored route does not match recomputed route {route}",
            )
        if profile.get("route") != route:
            report.error(
                "ROUTING_PROFILE",
                "RoutingSnapshot route and ProjectProfile route differ",
            )
        expected_action = {
            "Quick": "perform_bounded_task",
            "Structured": "prepare_lightweight_brief_and_review_plan",
            "Project": "initialize_or_resume_project",
        }[route]
        if snapshot.get("next_action") != expected_action:
            report.error(
                "ROUTING_NEXT_ACTION",
                f"next_action must be {expected_action}",
            )
        invocation = snapshot.get("next_invocation")
        if route == "Project" and (not isinstance(invocation, str) or not invocation):
            report.error(
                "ROUTING_NEXT_INVOCATION",
                "Project route requires a next_invocation summary",
            )
        if route != "Project" and invocation is not None:
            report.error(
                "ROUTING_NEXT_INVOCATION",
                f"{route} route must not set next_invocation",
            )
        report.ok("ROUTING_RECOMPUTED", f"{total} -> {route}")

    if not isinstance(snapshot.get("reasons"), list) or not snapshot["reasons"]:
        report.error("ROUTING_REASONS", "routing reasons must be non-empty")
    if not isinstance(snapshot.get("repository_evidence"), dict):
        report.error("ROUTING_REPOSITORY", "repository_evidence must be an object")
    try:
        snapshot_root = Path(str(snapshot.get("root"))).resolve()
        if snapshot_root != report.root:
            report.error("ROUTING_ROOT", "snapshot root differs from validator root")
    except (OSError, TypeError, ValueError):
        report.error("ROUTING_ROOT", "snapshot root is invalid")

    captured = validate_timestamp(
        snapshot.get("captured_at"),
        "ROUTING_TIMESTAMP",
        report,
    )
    max_age = profile.get("snapshot_max_age_hours")
    if captured and isinstance(max_age, (int, float)) and not isinstance(max_age, bool):
        age_hours = (now - captured).total_seconds() / 3600
        if age_hours < -1:
            report.error(
                "SNAPSHOT_FUTURE",
                f"routing snapshot is {abs(age_hours):.1f} hours in the future",
            )
        elif age_hours > max_age:
            report.error(
                "SNAPSHOT_STALE",
                f"routing snapshot age {age_hours:.1f}h exceeds {max_age}h",
            )
        else:
            report.ok("SNAPSHOT_FRESH", f"routing snapshot age {age_hours:.1f}h")


def validate_format_registry(
    registry: dict[str, Any],
    profile: dict[str, Any],
    report: Report,
) -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != "1":
        report.error("FORMAT_SCHEMA", "format registry schema_version must be 1")
    adapters = registry.get("adapters")
    if not isinstance(adapters, list) or not adapters:
        report.error("FORMAT_REGISTRY", "format registry must contain adapters")
        return {}
    by_id: dict[str, dict[str, Any]] = {}
    for adapter in adapters:
        if not isinstance(adapter, dict):
            report.error("FORMAT_ADAPTER", "every adapter must be an object")
            continue
        adapter_id = adapter.get("id")
        if not isinstance(adapter_id, str) or not adapter_id:
            report.error("FORMAT_ID", "every adapter requires an id")
            continue
        if adapter_id in by_id:
            report.error("FORMAT_DUPLICATE", f"duplicate adapter id: {adapter_id}")
        by_id[adapter_id] = adapter
        if not isinstance(adapter.get("format"), str) or not adapter["format"]:
            report.error("FORMAT_NAME", f"{adapter_id} requires a format name")
        if adapter.get("tier") not in {1, 2}:
            report.error("FORMAT_TIER", f"{adapter_id} tier must be 1 or 2")
        if not string_array(adapter.get("extensions")):
            report.error("FORMAT_EXTENSIONS", f"{adapter_id} extensions must be an array")
        if not string_array(adapter.get("media_types")):
            report.error(
                "FORMAT_MEDIA_TYPES",
                f"{adapter_id} media_types must be an array",
            )
        operations = adapter.get("operations")
        if not isinstance(operations, dict) or set(operations) != OPERATION_KEYS:
            report.error(
                "FORMAT_OPERATIONS",
                f"{adapter_id} must define all six operations",
            )
        elif any(value not in ALLOWED_CAPABILITIES for value in operations.values()):
            report.error(
                "FORMAT_CAPABILITY",
                f"{adapter_id} has an invalid capability value",
            )
        for field in ("required_dependencies", "optional_dependencies"):
            if not string_array(adapter.get(field)):
                report.error(
                    "FORMAT_DEPENDENCIES",
                    f"{adapter_id}.{field} must be an array",
                )
        validation_dependencies = adapter.get("validation_dependencies")
        if not isinstance(validation_dependencies, list):
            report.error(
                "FORMAT_DEPENDENCIES",
                f"{adapter_id}.validation_dependencies must be an array",
            )
        else:
            for requirement in validation_dependencies:
                if (
                    not isinstance(requirement, dict)
                    or not string_array(requirement.get("alternatives"), nonempty=True)
                    or requirement.get("operation") not in CAPABILITY_OPERATIONS
                ):
                    report.error(
                        "FORMAT_DEPENDENCIES",
                        f"{adapter_id} has an invalid validation dependency group",
                    )
        if not string_array(adapter.get("validation"), nonempty=True):
            report.error("FORMAT_VALIDATION", f"{adapter_id} requires validation steps")
        if not isinstance(adapter.get("degradation"), str) or not adapter["degradation"]:
            report.error("FORMAT_DEGRADATION", f"{adapter_id} requires degradation rules")
        if not isinstance(adapter.get("blocking_qa_gaps"), bool):
            report.error(
                "FORMAT_BLOCKING_POLICY",
                f"{adapter_id} requires blocking_qa_gaps",
            )

    extension_owners: dict[str, list[str]] = {}
    for adapter_id, adapter in by_id.items():
        for extension in adapter.get("extensions", []):
            if not isinstance(extension, str):
                continue
            normalized_extension = extension.strip().lower()
            if not normalized_extension.startswith(".") or normalized_extension in {
                ".",
                "..",
            }:
                report.error(
                    "FORMAT_EXTENSIONS",
                    f"{adapter_id} has invalid extension {extension!r}",
                )
                continue
            extension_owners.setdefault(normalized_extension, []).append(adapter_id)
    for extension, owners in sorted(extension_owners.items()):
        if len(owners) > 1:
            report.error(
                "FORMAT_EXTENSION_COLLISION",
                f"extension {extension} is claimed by multiple adapters: {sorted(owners)}",
            )

    missing = sorted(TIER1_IDS - set(by_id))
    if missing:
        report.error("FORMAT_TIER1", f"missing Tier 1 adapters: {missing}")
    else:
        report.ok("FORMAT_TIER1", "all Tier 1 adapters present")

    source_adapters = registry.get("source_adapters")
    source_ids: set[str] = set()
    if not isinstance(source_adapters, list):
        report.error("SOURCE_ADAPTERS", "source_adapters must be an array")
    else:
        for adapter in source_adapters:
            if not isinstance(adapter, dict) or not isinstance(adapter.get("id"), str):
                report.error("SOURCE_ADAPTER", "every source adapter requires an id")
                continue
            source_ids.add(adapter["id"])
            if not string_array(adapter.get("required_metadata"), nonempty=True):
                report.error(
                    "SOURCE_METADATA",
                    f"{adapter['id']} requires metadata fields",
                )
            if not string_array(adapter.get("derivatives")):
                report.error(
                    "SOURCE_DERIVATIVES",
                    f"{adapter['id']} derivatives must be an array",
                )
    if source_ids != SOURCE_ADAPTER_IDS:
        report.error(
            "SOURCE_ADAPTERS",
            "source adapter catalog is incomplete or contains unknown ids",
        )

    try:
        canonical = load_json(CANONICAL_FORMAT_REGISTRY)
    except ContractError as exc:
        report.error("FORMAT_BASELINE", str(exc))
        canonical = {}
    canonical_adapters = {
        item.get("id"): item
        for item in canonical.get("adapters", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for adapter_id, baseline in canonical_adapters.items():
        observed = by_id.get(adapter_id)
        if observed is None:
            report.error(
                "FORMAT_BASELINE",
                f"local format registry omits canonical adapter {adapter_id}",
            )
            continue
        changed = sorted(
            field
            for field in CANONICAL_ADAPTER_FIELDS
            if observed.get(field) != baseline.get(field)
        )
        if changed:
            report.error(
                "FORMAT_BASELINE",
                f"{adapter_id} weakens or changes canonical fields: {changed}",
            )
    canonical_sources = {
        item.get("id"): item
        for item in canonical.get("source_adapters", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    observed_sources = (
        {
            item.get("id"): item
            for item in source_adapters
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        if isinstance(source_adapters, list)
        else {}
    )
    if observed_sources != canonical_sources:
        report.error(
            "FORMAT_BASELINE",
            "local source-adapter contract differs from the packaged canonical baseline",
        )
    if canonical_adapters and not any(
        item["code"] == "FORMAT_BASELINE" for item in report.errors
    ):
        report.ok(
            "FORMAT_BASELINE",
            f"local registry preserves {len(canonical_adapters)} canonical adapters",
        )

    formats = profile.get("formats")
    if isinstance(formats, list):
        unknown_formats = sorted(set(formats) - set(by_id))
        if unknown_formats:
            report.error("PROFILE_FORMATS", f"unknown selected formats: {unknown_formats}")
    return by_id


def validate_lifecycle_state(
    state: dict[str, Any],
    batches: dict[str, dict[str, Any]],
    profile: dict[str, Any],
    report: Report,
) -> dict[str, Any]:
    if state.get("schema_version") != "1":
        report.error("STATE_SCHEMA", "state schema_version must be 1")
    if not valid_date_version(state.get("date_version")):
        report.error("STATE_VERSION", "state date_version is invalid")
    if state.get("date_version") != profile.get("date_version"):
        report.error("STATE_VERSION", "state and ProjectProfile date versions differ")
    phase = state.get("phase")
    if phase not in PHASE_GATES:
        report.error("STATE_PHASE", f"invalid lifecycle phase: {phase!r}")
        expected_gates: set[str] = set()
    else:
        expected_gates = PHASE_GATES[phase]
    required_gates = state.get("required_gates")
    if not string_array(required_gates, nonempty=True):
        report.error("STATE_GATES", "required_gates must be a non-empty string array")
        required_gates = []
    unknown_gates = sorted(set(required_gates) - set(GATE_ALIASES))
    if unknown_gates:
        report.error("STATE_GATES", f"unknown required gates: {unknown_gates}")
    missing_gates = sorted(expected_gates - set(required_gates))
    if missing_gates:
        report.error("STATE_GATES", f"phase {phase} omits required gates: {missing_gates}")
    extra_gates = sorted(set(required_gates) - expected_gates)
    if extra_gates:
        report.error("STATE_GATES", f"phase {phase} includes later gates: {extra_gates}")
    active_receipts = state.get("active_receipts")
    if not isinstance(active_receipts, dict):
        report.error("STATE_RECEIPTS", "active_receipts must be an object")
        active_receipts = {}
    else:
        if set(active_receipts) != set(required_gates):
            report.error(
                "STATE_RECEIPTS",
                "active_receipts keys must exactly match required_gates",
            )
        for gate, bookmark in active_receipts.items():
            if gate not in GATE_ALIASES:
                report.error("STATE_RECEIPTS", f"unknown active receipt gate {gate!r}")
            elif (
                not isinstance(bookmark, str)
                or not bookmark
                or not bookmark.startswith(f"{gate}-")
                or not valid_date_version(bookmark[len(gate) + 1 :])
            ):
                report.error(
                    "STATE_RECEIPTS",
                    f"{gate} active receipt must name a dated gate bookmark",
                )

    active_batch = state.get("active_batch")
    live_batches = sorted(
        batch_id
        for batch_id, batch in batches.items()
        if batch.get("status") in {"active", "review"}
    )
    if active_batch is not None:
        batch = batches.get(active_batch)
        if batch is None:
            report.error("STATE_BATCH", f"unknown active_batch: {active_batch}")
        elif phase in PHASE_ACTIVE_BATCH_KINDS:
            allowed_kinds = PHASE_ACTIVE_BATCH_KINDS[phase]
            if batch.get("kind") not in allowed_kinds:
                report.error(
                    "STATE_BATCH_PHASE",
                    f"phase {phase} cannot activate batch kind {batch.get('kind')!r}",
                )
            if batch.get("status") not in {"active", "review"}:
                report.error(
                    "STATE_BATCH_STATUS",
                    f"active batch {active_batch} must have status active or review",
                )
        if live_batches != [active_batch]:
            report.error(
                "STATE_BATCH_BINDING",
                f"active_batch must exactly match the sole active/review batch: {live_batches}",
            )
    elif phase in {"candidate", "deriving"}:
        report.error("STATE_BATCH", f"phase {phase} requires an active batch")
    elif live_batches:
        report.error(
            "STATE_BATCH_BINDING",
            f"BatchManifest has active/review work but LifecycleState has no active_batch: {live_batches}",
        )
    source_register = state.get("source_register")
    if not isinstance(source_register, str) or not source_register:
        report.error("STATE_SOURCES", "source_register must be a path")
    for field in ("review_matrix", "latest_review_report", "capability_snapshot"):
        value = state.get(field)
        if value is not None and (not isinstance(value, str) or not value):
            report.error("STATE_PATH", f"{field} must be null or a path")
    if phase in MATRIX_PHASES and not state.get("review_matrix"):
        report.error("STATE_REVIEW_MATRIX", f"phase {phase} requires a ReviewMatrix")
    if phase in REPORT_PHASES and not state.get("latest_review_report"):
        report.error("STATE_REVIEW_REPORT", f"phase {phase} requires a ReviewReport")
    if phase in FINAL_PHASES:
        if not state.get("capability_snapshot"):
            report.error(
                "STATE_CAPABILITIES",
                f"phase {phase} requires a capability snapshot",
            )
        if (
            not isinstance(state.get("format_qa_records"), list)
            or not state["format_qa_records"]
        ):
            report.error(
                "STATE_FORMAT_QA",
                f"phase {phase} requires format QA records",
            )
    elif not isinstance(state.get("format_qa_records"), list):
        report.error("STATE_FORMAT_QA", "format_qa_records must be an array")
    validate_timestamp(state.get("updated_at"), "STATE_UPDATED_AT", report)
    report.ok("STATE_PHASE", f"phase={phase}, required gates={len(required_gates)}")
    return {
        "phase": phase,
        "date_version": state.get("date_version"),
        "required_gates": set(required_gates),
        "active_receipts": active_receipts,
        "active_batch": active_batch,
        "source_register": source_register,
        "review_matrix": state.get("review_matrix"),
        "latest_review_report": state.get("latest_review_report"),
        "capability_snapshot": state.get("capability_snapshot"),
        "format_qa_records": state.get("format_qa_records", []),
    }
