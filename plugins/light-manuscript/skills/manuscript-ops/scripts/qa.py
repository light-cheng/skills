#!/usr/bin/env python3
"""Format QA, sampling authority, generation lineage, and capability snapshot validation."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from manuscript_ops_core import ContractError, ensure_within_root, sha256_file
from probe_capabilities import (
    DERIVED_ALIAS_PARENTS,
    PROCESS_OPERATIONS,
    adapter_status as recompute_adapter_status,
    load_platform_capabilities,
    observe as observe_process_capabilities,
)
from schema import (
    CANONICAL_CAPABILITY_MAP,
    CAPABILITY_OPERATIONS,
    Report,
    read_required,
    string_array,
    validate_hashed_path,
    validate_timestamp,
)


def validate_qa_check(
    adapter_id: str,
    check_name: str,
    check: dict[str, Any],
    artifact_path: str | None,
    brief_result: dict[str, Any] | None,
    report: Report,
) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "reference_artifact": None,
        "output_artifact": None,
    }
    status = check.get("status")
    coverage = check.get("coverage")
    evidence_artifacts = check.get("evidence_artifacts")
    if not isinstance(coverage, dict):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} requires structured coverage",
        )
        coverage = {}
    mode = coverage.get("mode")
    unit = coverage.get("unit")
    total = coverage.get("total")
    inspected = coverage.get("inspected")
    items = coverage.get("items")
    authority = coverage.get("sampling_authority")
    if not isinstance(unit, str) or not unit.strip():
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} coverage requires a unit",
        )
    if (
        not isinstance(total, int)
        or isinstance(total, bool)
        or total < 0
        or not isinstance(inspected, int)
        or isinstance(inspected, bool)
        or inspected < 0
        or inspected > total
    ):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} has invalid total/inspected coverage",
        )
    if not string_array(items):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} coverage items must be a string array",
        )
        items = []
    elif len(items) != len(set(items)):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} coverage items must be unique",
        )
    if (
        isinstance(inspected, int)
        and not isinstance(inspected, bool)
        and len(items) != inspected
    ):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} inspected count must equal listed items",
        )

    if status == "NOT_APPLICABLE":
        if mode != "not_applicable" or total != 0 or inspected != 0 or items:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} NOT_APPLICABLE requires zero not_applicable coverage",
            )
        if authority is not None:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} NOT_APPLICABLE cannot retain sampling authority",
            )
    else:
        allowed_modes = (
            {"full", "sampled"}
            if status == "PASS"
            else {"full", "sampled", "partial"}
        )
        if mode not in allowed_modes or not isinstance(total, int) or total < 1:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} has invalid positive coverage mode",
            )
        if mode == "full":
            if inspected != total:
                report.error(
                    "FORMAT_QA_COVERAGE",
                    f"{adapter_id}.{check_name} full coverage must inspect every item",
                )
            if authority is not None:
                report.error(
                    "FORMAT_QA_COVERAGE",
                    f"{adapter_id}.{check_name} full coverage cannot retain sampling authority",
                )
        elif mode == "sampled":
            if not isinstance(authority, dict):
                report.error(
                    "FORMAT_QA_COVERAGE",
                    f"{adapter_id}.{check_name} sampled coverage requires Brief authority",
                )
            else:
                authority_path = validate_hashed_path(
                    authority.get("path"),
                    authority.get("sha256"),
                    "FORMAT_QA_SAMPLING",
                    report,
                )
                if set(authority) != {
                    "path",
                    "sha256",
                    "deliverable",
                    "policy",
                }:
                    report.error(
                        "FORMAT_QA_COVERAGE",
                        f"{adapter_id}.{check_name} sampling authority must contain "
                        "path, sha256, deliverable, and policy",
                    )
                if brief_result:
                    normalized_authority = (
                        authority_path.relative_to(report.root).as_posix()
                        if authority_path
                        else None
                    )
                    if (
                        normalized_authority != brief_result.get("path")
                        or str(authority.get("sha256", "")).lower()
                        != brief_result.get("sha256")
                    ):
                        report.error(
                            "FORMAT_QA_COVERAGE",
                            f"{adapter_id}.{check_name} sampling authority is not the approved Brief",
                        )
                    deliverable = next(
                        (
                            item
                            for item in brief_result.get("deliverables", [])
                            if isinstance(item, dict)
                            and item.get("path") == artifact_path
                        ),
                        None,
                    )
                    if (
                        not deliverable
                        or deliverable.get("visual_qa") != "sampled"
                        or authority.get("deliverable") != artifact_path
                        or authority.get("policy") != "sampled"
                    ):
                        report.error(
                            "FORMAT_QA_COVERAGE",
                            f"{adapter_id}.{check_name} sampled coverage is not "
                            "authorized by the deliverable's approved Brief policy",
                        )
                else:
                    report.error(
                        "FORMAT_QA_COVERAGE",
                        f"{adapter_id}.{check_name} sampling cannot be verified without the approved Brief",
                    )
        elif mode == "partial" and authority is not None:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} partial failure coverage cannot claim sampling authority",
            )

    if not isinstance(evidence_artifacts, list):
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} evidence_artifacts must be an array",
        )
        evidence_artifacts = []
    normalized_evidence_paths: set[str] = set()
    evidence_kinds: set[str] = set()
    for evidence_artifact in evidence_artifacts:
        if not isinstance(evidence_artifact, dict):
            report.error(
                "FORMAT_QA_EVIDENCE_ARTIFACT",
                f"{adapter_id}.{check_name} evidence artifact must be an object",
            )
            continue
        evidence_kind = evidence_artifact.get("kind")
        if evidence_kind not in {
            "validator_log",
            "rendered_output",
            "inspection_record",
            "comparison_report",
        }:
            report.error(
                "FORMAT_QA_EVIDENCE_ARTIFACT",
                f"{adapter_id}.{check_name} evidence artifact has invalid kind",
            )
        else:
            evidence_kinds.add(evidence_kind)
        validated = validate_hashed_path(
            evidence_artifact.get("path"),
            evidence_artifact.get("sha256"),
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            report,
        )
        if validated:
            normalized_evidence = validated.relative_to(report.root).as_posix()
            if normalized_evidence in normalized_evidence_paths:
                report.error(
                    "FORMAT_QA_EVIDENCE_ARTIFACT",
                    f"{adapter_id}.{check_name} repeats evidence artifact {normalized_evidence}",
                )
            normalized_evidence_paths.add(normalized_evidence)
    if status in {"PASS", "FAIL"} and not evidence_artifacts:
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} PASS/FAIL requires hashed evidence artifacts",
        )
    required_evidence_kind = {
        "structural": "validator_log",
        "render": "rendered_output",
        "visual": "inspection_record",
        "semantic": "comparison_report",
        "round_trip": "comparison_report",
    }[check_name]
    if status == "PASS" and required_evidence_kind not in evidence_kinds:
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} PASS requires {required_evidence_kind} evidence",
        )
    if status == "NOT_APPLICABLE" and evidence_artifacts:
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} NOT_APPLICABLE cannot retain evidence artifacts",
        )

    if check_name in {"semantic", "round_trip"} and status == "PASS":
        if not string_array(check.get("invariants"), nonempty=True):
            report.error(
                "FORMAT_QA_INVARIANTS",
                f"{adapter_id}.{check_name} PASS requires compared invariants",
            )
    if check_name == "semantic":
        reference = check.get("reference_artifact")
        if status == "PASS":
            if not isinstance(reference, dict):
                report.error(
                    "FORMAT_QA_SEMANTIC",
                    f"{adapter_id}.semantic PASS requires a hash-bound reference artifact",
                )
            else:
                validated_reference = validate_hashed_path(
                    reference.get("path"),
                    reference.get("sha256"),
                    "FORMAT_QA_SEMANTIC",
                    report,
                )
                if validated_reference:
                    normalized_reference = validated_reference.relative_to(
                        report.root
                    ).as_posix()
                    if artifact_path and normalized_reference == artifact_path:
                        report.error(
                            "FORMAT_QA_SEMANTIC",
                            f"{adapter_id}.semantic reference must be distinct from the output artifact",
                        )
                    normalized["reference_artifact"] = {
                        "path": normalized_reference,
                        "sha256": str(reference.get("sha256", "")).lower(),
                    }
        elif reference is not None:
            report.error(
                "FORMAT_QA_SEMANTIC",
                f"{adapter_id}.semantic reference_artifact is allowed only for PASS",
            )
    if check_name == "round_trip":
        output = check.get("output_artifact")
        if status == "PASS":
            if not isinstance(output, dict):
                report.error(
                    "FORMAT_QA_ROUND_TRIP",
                    f"{adapter_id}.round_trip PASS requires a hashed output artifact",
                )
            else:
                validated_output = validate_hashed_path(
                    output.get("path"),
                    output.get("sha256"),
                    "FORMAT_QA_ROUND_TRIP",
                    report,
                )
                if (
                    validated_output
                    and artifact_path
                    and validated_output.relative_to(report.root).as_posix()
                    == artifact_path
                ):
                    report.error(
                        "FORMAT_QA_ROUND_TRIP",
                        f"{adapter_id}.round_trip output must be distinct from the input artifact",
                    )
                if validated_output:
                    normalized["output_artifact"] = {
                        "path": validated_output.relative_to(report.root).as_posix(),
                        "sha256": str(output.get("sha256", "")).lower(),
                    }
        elif output is not None:
            report.error(
                "FORMAT_QA_ROUND_TRIP",
                f"{adapter_id}.round_trip output_artifact is allowed only for PASS",
            )
    return normalized


def validate_generation_record(
    generation: Any,
    artifact_path: str | None,
    artifact_sha256: str | None,
    brief_result: dict[str, Any] | None,
    adapter_id: str,
    report: Report,
) -> dict[str, Any] | None:
    if not isinstance(generation, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} READY evidence requires a generation record",
        )
        return None
    mode = generation.get("mode")
    if mode not in {"reproducible", "manual"}:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation mode must be reproducible or manual",
        )
    tool = generation.get("tool")
    if not isinstance(tool, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires tool identity",
        )
    else:
        for field in ("name", "version", "evidence"):
            if not isinstance(tool.get(field), str) or not tool[field].strip():
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} generation tool requires {field}",
                )
    command = generation.get("command")
    if not string_array(command, nonempty=True):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires an exact command or ordered action array",
        )
    configuration = generation.get("configuration")
    if not isinstance(configuration, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires configuration provenance",
        )
    else:
        configuration_path = configuration.get("path")
        configuration_hash = configuration.get("sha256")
        not_applicable_reason = configuration.get("not_applicable_reason")
        if configuration_path is None and configuration_hash is None:
            if (
                not isinstance(not_applicable_reason, str)
                or not not_applicable_reason.strip()
            ):
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} generation must hash-bind configuration or "
                    "record why none exists",
                )
        else:
            validate_hashed_path(
                configuration_path,
                configuration_hash,
                "FORMAT_QA_GENERATION_CONFIG",
                report,
            )
            if not_applicable_reason is not None:
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} hashed configuration cannot also be not_applicable",
                )
    inputs = generation.get("inputs")
    normalized_inputs: dict[str, str] = {}
    if not isinstance(inputs, list) or not inputs:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires hash-bound inputs",
        )
    else:
        for input_artifact in inputs:
            if not isinstance(input_artifact, dict):
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} generation input must be an object",
                )
                continue
            validated_input = validate_hashed_path(
                input_artifact.get("path"),
                input_artifact.get("sha256"),
                "FORMAT_QA_GENERATION_INPUT",
                report,
            )
            if validated_input:
                normalized_path = validated_input.relative_to(report.root).as_posix()
                if normalized_path in normalized_inputs:
                    report.error(
                        "FORMAT_QA_GENERATION",
                        f"{adapter_id} repeats generation input {normalized_path}",
                    )
                normalized_inputs[normalized_path] = str(
                    input_artifact.get("sha256", "")
                ).lower()
    output = generation.get("output")
    if not isinstance(output, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires a hash-bound output",
        )
    else:
        validated_output = validate_hashed_path(
            output.get("path"),
            output.get("sha256"),
            "FORMAT_QA_GENERATION_OUTPUT",
            report,
        )
        if validated_output and (
            validated_output.relative_to(report.root).as_posix() != artifact_path
            or str(output.get("sha256", "")).lower() != artifact_sha256
        ):
            report.error(
                "FORMAT_QA_GENERATION",
                f"{adapter_id} generation output differs from the QA artifact",
            )
    manual_disposition = generation.get("manual_disposition")
    if mode == "manual":
        if not isinstance(manual_disposition, str) or not manual_disposition.strip():
            report.error(
                "FORMAT_QA_GENERATION",
                f"{adapter_id} manual generation requires a reproducibility disposition",
            )
    elif manual_disposition is not None:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} reproducible generation cannot retain a manual disposition",
        )
    deliverable = next(
        (
            item
            for item in (brief_result or {}).get("deliverables", [])
            if isinstance(item, dict) and item.get("path") == artifact_path
        ),
        None,
    )
    if deliverable is None:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation is not bound to an approved Brief deliverable",
        )
    elif deliverable.get("reproducible") == "required" and mode != "reproducible":
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} deliverable requires reproducible generation",
        )
    return {
        "mode": mode,
        "inputs": normalized_inputs,
    }


def validate_format_qa_entry(
    item: Any,
    adapters: dict[str, dict[str, Any]],
    report: Report,
    brief_result: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        report.error("FORMAT_QA", "format QA entry must be an object")
        return None
    adapter_id = item.get("format")
    if adapter_id not in adapters:
        report.error("FORMAT_QA", f"unknown format QA adapter: {adapter_id!r}")
        return None
    if item.get("status") not in {"READY", "DEGRADED", "BLOCKED"}:
        report.error("FORMAT_QA", f"{adapter_id} has invalid QA status")
    evidence_path = validate_hashed_path(
        item.get("evidence_path"),
        item.get("sha256"),
        "FORMAT_QA",
        report,
    )
    for field in ("rendered", "visually_inspected"):
        if not isinstance(item.get(field), bool):
            report.error("FORMAT_QA", f"{adapter_id}.{field} must be boolean")
    visual_operation = adapters[adapter_id]["operations"]["visual_qa"]
    if item.get("status") == "READY" and visual_operation != "not_applicable":
        if (
            item.get("rendered") is not True
            or item.get("visually_inspected") is not True
        ):
            report.error(
                "FORMAT_QA",
                f"{adapter_id} READY requires render and visual inspection",
            )
    evidence: dict[str, Any] | None = None
    artifact_path: str | None = None
    artifact_sha256: str | None = None
    completed_at: datetime | None = None
    check_results: dict[str, dict[str, Any]] = {}
    generation_result: dict[str, Any] | None = None
    if evidence_path:
        if evidence_path.suffix.lower() != ".json":
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} QA evidence must be JSON",
            )
        else:
            evidence = read_required(evidence_path, report)
    if evidence is not None:
        if evidence.get("schema_version") != "1":
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} evidence schema_version must be 1",
            )
        if evidence.get("format") != adapter_id:
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} evidence format differs",
            )
        if evidence.get("status") != item.get("status"):
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} evidence status differs",
            )
        completed_at = validate_timestamp(
            evidence.get("completed_at"),
            "FORMAT_QA_EVIDENCE_TIME",
            report,
        )
        artifact = evidence.get("artifact")
        if not isinstance(artifact, dict):
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} evidence requires artifact",
            )
        else:
            validated_artifact = validate_hashed_path(
                artifact.get("path"),
                artifact.get("sha256"),
                "FORMAT_QA_ARTIFACT",
                report,
            )
            if validated_artifact:
                artifact_path = validated_artifact.relative_to(report.root).as_posix()
                artifact_sha256 = str(artifact.get("sha256", "")).lower()
        provider = evidence.get("provider")
        if not isinstance(provider, dict):
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} evidence requires provider",
            )
        else:
            for field in ("name", "version", "evidence"):
                if (
                    not isinstance(provider.get(field), str)
                    or not provider[field].strip()
                ):
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id} provider requires {field}",
                    )
        checks = evidence.get("checks")
        required_checks = {"structural", "render", "visual", "semantic", "round_trip"}
        if not isinstance(checks, dict) or set(checks) != required_checks:
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} evidence must define {sorted(required_checks)} checks",
            )
        else:
            for check_name, check in checks.items():
                if not isinstance(check, dict) or check.get("status") not in {
                    "PASS",
                    "FAIL",
                    "NOT_APPLICABLE",
                }:
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id}.{check_name} has invalid status",
                    )
                    continue
                if (
                    not isinstance(check.get("evidence"), str)
                    or not check["evidence"].strip()
                ):
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id}.{check_name} requires evidence",
                    )
                check_results[check_name] = validate_qa_check(
                    adapter_id,
                    check_name,
                    check,
                    artifact_path,
                    brief_result,
                    report,
                )
            if item.get("status") == "READY" or evidence.get("generation") is not None:
                generation_result = validate_generation_record(
                    evidence.get("generation"),
                    artifact_path,
                    artifact_sha256,
                    brief_result,
                    adapter_id,
                    report,
                )
            if item.get("status") == "READY":
                for check_name in ("structural", "semantic"):
                    if checks.get(check_name, {}).get("status") != "PASS":
                        report.error(
                            "FORMAT_QA_EVIDENCE",
                            f"{adapter_id} READY requires {check_name}=PASS",
                        )
                if visual_operation != "not_applicable":
                    for check_name in ("render", "visual"):
                        if checks.get(check_name, {}).get("status") != "PASS":
                            report.error(
                                "FORMAT_QA_EVIDENCE",
                                f"{adapter_id} READY requires {check_name}=PASS",
                            )
                round_trip = adapters[adapter_id]["operations"]["round_trip"]
                expected_round_trip = (
                    "NOT_APPLICABLE"
                    if round_trip in {"unsupported", "not_applicable"}
                    else "PASS"
                )
                if checks.get("round_trip", {}).get("status") != expected_round_trip:
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id} READY requires round_trip={expected_round_trip}",
                    )
            if item.get("rendered") is not (
                checks.get("render", {}).get("status") == "PASS"
            ):
                report.error(
                    "FORMAT_QA_EVIDENCE",
                    f"{adapter_id} rendered flag differs from evidence",
                )
            if item.get("visually_inspected") is not (
                checks.get("visual", {}).get("status") == "PASS"
            ):
                report.error(
                    "FORMAT_QA_EVIDENCE",
                    f"{adapter_id} visually_inspected flag differs from evidence",
                )
    return {
        "format": adapter_id,
        "status": item.get("status"),
        "evidence_path": (
            evidence_path.relative_to(report.root).as_posix() if evidence_path else None
        ),
        "sha256": str(item.get("sha256", "")).lower(),
        "rendered": item.get("rendered"),
        "visually_inspected": item.get("visually_inspected"),
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "completed_at": completed_at,
        "semantic_reference": check_results.get("semantic", {}).get(
            "reference_artifact"
        ),
        "generation": generation_result,
    }


def validate_capability_snapshot(
    path_value: Any,
    profile: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
    report: Report,
    now: datetime,
) -> dict[str, Any] | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("STATE_CAPABILITIES", str(exc))
        return None
    snapshot = read_required(path, report)
    if not snapshot:
        return None
    if snapshot.get("schema_version") != "1":
        report.error("CAPABILITY_SCHEMA", "capability snapshot schema_version must be 1")
    captured = validate_timestamp(
        snapshot.get("captured_at"),
        "CAPABILITY_TIMESTAMP",
        report,
    )
    max_age = profile.get("snapshot_max_age_hours")
    if captured and isinstance(max_age, (int, float)) and not isinstance(max_age, bool):
        age_hours = (now - captured).total_seconds() / 3600
        if age_hours < -1:
            report.error(
                "CAPABILITY_FUTURE",
                f"capability snapshot is {abs(age_hours):.1f} hours in the future",
            )
        elif age_hours > max_age:
            report.error(
                "CAPABILITY_STALE",
                f"capability snapshot age {age_hours:.1f}h exceeds {max_age}h",
            )
        else:
            report.ok("CAPABILITY_FRESH", f"capability snapshot age {age_hours:.1f}h")
    if not isinstance(snapshot.get("registry"), str) or not snapshot["registry"]:
        report.error(
            "CAPABILITY_REGISTRY",
            "capability snapshot requires registry provenance",
        )
    declared = snapshot.get("declared_capabilities")
    if not string_array(declared):
        report.error("CAPABILITY_DECLARED", "declared_capabilities must be an array")
    elif declared:
        report.warn(
            "CAPABILITY_DECLARED",
            "legacy declared capabilities cannot establish final acceptance",
        )
    platform_snapshot = snapshot.get("platform_snapshot")
    validated_platform_observed: dict[str, dict[str, Any]] = {}
    if platform_snapshot is not None:
        if not isinstance(platform_snapshot, dict):
            report.error(
                "CAPABILITY_PLATFORM",
                "platform_snapshot must be null or a hash-bound object",
            )
        else:
            platform_path = validate_hashed_path(
                platform_snapshot.get("path"),
                platform_snapshot.get("sha256"),
                "CAPABILITY_PLATFORM",
                report,
            )
            capability_map = platform_snapshot.get("capability_map")
            if not isinstance(capability_map, dict):
                report.error(
                    "CAPABILITY_PLATFORM",
                    "platform_snapshot requires capability_map provenance",
                )
                capability_map_hash = None
            else:
                capability_map_hash = capability_map.get("sha256")
                if (
                    not isinstance(capability_map.get("path"), str)
                    or not capability_map["path"].strip()
                    or capability_map_hash != sha256_file(CANONICAL_CAPABILITY_MAP)
                ):
                    report.error(
                        "CAPABILITY_PLATFORM",
                        "platform snapshot capability map differs from the packaged canonical map",
                    )
            if platform_path and capability_map_hash:
                try:
                    validated_platform_observed, provenance = (
                        load_platform_capabilities(
                            platform_path,
                            CANONICAL_CAPABILITY_MAP,
                        )
                    )
                except (ContractError, OSError, json.JSONDecodeError) as exc:
                    report.error("CAPABILITY_PLATFORM", str(exc))
                else:
                    if (
                        provenance is None
                        or platform_snapshot.get("platform") != provenance.get("platform")
                        or platform_snapshot.get("captured_at")
                        != provenance.get("captured_at")
                        or str(platform_snapshot.get("sha256", "")).lower()
                        != provenance.get("sha256")
                    ):
                        report.error(
                            "CAPABILITY_PLATFORM",
                            "platform snapshot provenance differs from its hashed source",
                        )
                    platform_captured = validate_timestamp(
                        provenance.get("captured_at") if provenance else None,
                        "CAPABILITY_PLATFORM_TIMESTAMP",
                        report,
                    )
                    if (
                        platform_captured
                        and isinstance(max_age, (int, float))
                        and not isinstance(max_age, bool)
                    ):
                        platform_age_hours = (
                            now - platform_captured
                        ).total_seconds() / 3600
                        if platform_age_hours < -1:
                            report.error(
                                "CAPABILITY_PLATFORM_FUTURE",
                                f"platform capability evidence is {abs(platform_age_hours):.1f} hours in the future",
                            )
                        elif platform_age_hours > max_age:
                            report.error(
                                "CAPABILITY_PLATFORM_STALE",
                                f"platform capability evidence age {platform_age_hours:.1f}h exceeds {max_age}h",
                            )
                        else:
                            report.ok(
                                "CAPABILITY_PLATFORM_FRESH",
                                f"platform capability evidence age {platform_age_hours:.1f}h",
                            )
    observed = snapshot.get("observed")
    if not isinstance(observed, dict):
        report.error(
            "CAPABILITY_OBSERVED",
            "capability snapshot requires observed evidence",
        )
    else:
        live_process_observed: dict[str, dict[str, Any]] = {}
        if any(
            isinstance(item, dict) and item.get("source") == "process_probe"
            for item in observed.values()
        ):
            try:
                live_process_observed = observe_process_capabilities(set())
            except Exception as exc:
                report.error(
                    "CAPABILITY_PROCESS",
                    f"cannot reproduce process capability probe: {exc}",
                )
        for name, item in observed.items():
            if not isinstance(name, str) or not name or not isinstance(item, dict):
                report.error(
                    "CAPABILITY_OBSERVED",
                    "observed capability entries are invalid",
                )
                continue
            available = item.get("available")
            if not isinstance(available, bool):
                report.error("CAPABILITY_OBSERVED", f"{name}.available must be boolean")
            operations = item.get("operations")
            if not isinstance(operations, list) or not all(
                isinstance(operation, str) and operation in CAPABILITY_OPERATIONS
                for operation in operations
            ):
                report.error(
                    "CAPABILITY_OPERATIONS",
                    f"{name} has invalid operations",
                )
            if available:
                for field in ("provider", "version", "evidence", "source"):
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"available capability {name} requires {field}",
                        )
                source = item.get("source")
                if source not in {
                    "process_probe",
                    "platform_snapshot",
                    "legacy_declare",
                } and not (
                    isinstance(source, str) and source.startswith("derived_alias:")
                ):
                    report.error(
                        "CAPABILITY_EVIDENCE",
                        f"available capability {name} has unknown evidence source {source!r}",
                    )
                if source == "platform_snapshot":
                    if validated_platform_observed.get(name) != item:
                        report.error(
                            "CAPABILITY_PLATFORM",
                            f"{name} does not match the hash-bound platform snapshot",
                        )
                elif source == "process_probe":
                    if (
                        name not in PROCESS_OPERATIONS
                        or item.get("operations") != PROCESS_OPERATIONS.get(name)
                        or live_process_observed.get(name) != item
                    ):
                        report.error(
                            "CAPABILITY_PROCESS",
                            f"{name} does not match the live, fixed process-probe contract",
                        )
                elif isinstance(source, str) and source.startswith("derived_alias:"):
                    source_name = source.split(":", 1)[1]
                    parent = observed.get(source_name)
                    allowed_parents = DERIVED_ALIAS_PARENTS.get(name, ())
                    if source_name not in allowed_parents:
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"{name} is not an allowed alias of {source_name!r}",
                        )
                    elif not isinstance(parent, dict) or not parent.get("available"):
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"{name} derived alias has no available parent {source_name!r}",
                        )
                    elif {
                        key: value for key, value in item.items() if key != "source"
                    } != {
                        key: value for key, value in parent.items() if key != "source"
                    }:
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"{name} derived alias differs from parent {source_name!r}",
                        )
    platform_names = (
        {
            name
            for name, item in observed.items()
            if isinstance(item, dict) and item.get("source") == "platform_snapshot"
        }
        if isinstance(observed, dict)
        else set()
    )
    if platform_names != set(validated_platform_observed):
        report.error(
            "CAPABILITY_PLATFORM",
            "observed platform capabilities do not exactly match the hash-bound platform snapshot",
        )

    capability_adapters = snapshot.get("adapters")
    statuses: dict[str, str] = {}
    if not isinstance(capability_adapters, list):
        report.error(
            "CAPABILITY_ADAPTERS",
            "capability snapshot requires adapter results",
        )
    else:
        for item in capability_adapters:
            if not isinstance(item, dict):
                report.error("CAPABILITY_ADAPTERS", "adapter result must be an object")
                continue
            adapter_id = item.get("id")
            if adapter_id not in adapters or adapter_id in statuses:
                report.error(
                    "CAPABILITY_ADAPTERS",
                    f"unknown or duplicate capability adapter {adapter_id!r}",
                )
                continue
            status = item.get("status")
            if status not in {"READY", "DEGRADED", "BLOCKED"}:
                report.error(
                    "CAPABILITY_ADAPTERS",
                    f"{adapter_id} has invalid status",
                )
                continue
            statuses[adapter_id] = status
            for field in (
                "missing_required",
                "missing_render_or_visual_groups",
                "missing_validation_groups",
            ):
                if not isinstance(item.get(field), list):
                    report.error(
                        "CAPABILITY_ADAPTERS",
                        f"{adapter_id}.{field} must be an array",
                    )
            if status == "READY" and item.get("claim_limit") is not None:
                report.error(
                    "CAPABILITY_ADAPTERS",
                    f"{adapter_id} READY cannot retain a claim limit",
                )
            if status != "READY" and (
                not isinstance(item.get("claim_limit"), str)
                or not item["claim_limit"].strip()
            ):
                report.error(
                    "CAPABILITY_ADAPTERS",
                    f"{adapter_id} {status} requires a claim limit",
                )
            if isinstance(observed, dict):
                recomputed = recompute_adapter_status(adapters[adapter_id], observed)
                for field in (
                    "status",
                    "missing_required",
                    "missing_render_or_visual_groups",
                    "missing_validation_groups",
                    "claim_limit",
                ):
                    if item.get(field) != recomputed.get(field):
                        report.error(
                            "CAPABILITY_RECOMPUTE",
                            f"{adapter_id}.{field} differs from observed capability evidence",
                        )
    missing_selected = sorted(set(profile.get("formats", [])) - set(statuses))
    if missing_selected:
        report.error(
            "CAPABILITY_ADAPTERS",
            f"selected formats are absent from capability results: {missing_selected}",
        )
    if not isinstance(snapshot.get("claim_warning"), str) or not snapshot[
        "claim_warning"
    ].strip():
        report.error(
            "CAPABILITY_WARNING",
            "capability snapshot requires its claim warning",
        )
    report.ok("CAPABILITY_SNAPSHOT", path.relative_to(report.root).as_posix())
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "statuses": statuses,
        "captured_at": snapshot.get("captured_at"),
        "captured_time": captured,
    }


def validate_ready_deliverable_qa(
    brief_result: dict[str, Any] | None,
    qa_by_artifact: dict[str, dict[str, Any]],
    code: str,
    label: str,
    report: Report,
) -> None:
    deliverables = {
        item["path"]: item
        for item in (brief_result or {}).get("deliverables", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    missing = sorted(set(deliverables) - set(qa_by_artifact))
    unexpected = sorted(set(qa_by_artifact) - set(deliverables))
    if missing:
        report.error(code, f"{label} lacks QA for deliverables: {missing}")
    if unexpected:
        report.error(
            code,
            f"{label} contains QA for unapproved deliverables: {unexpected}",
        )
    for deliverable_path, deliverable in deliverables.items():
        qa_record = qa_by_artifact.get(deliverable_path)
        if qa_record and qa_record.get("format") != deliverable.get("format"):
            report.error(
                code,
                f"{label} QA format for {deliverable_path} differs from the approved Brief",
            )
    if any(item.get("status") != "READY" for item in qa_by_artifact.values()):
        report.error(code, f"{label} cannot retain DEGRADED or BLOCKED format QA")
