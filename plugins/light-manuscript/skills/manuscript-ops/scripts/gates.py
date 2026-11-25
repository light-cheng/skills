#!/usr/bin/env python3
"""Acceptance integration, review matrices, gate receipts, publication bindings, and VCS gates."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from manuscript_ops_core import (
    REVIEW_AXIS_IDS,
    ContractError,
    ensure_within_root,
    load_json,
    sha256_file,
)
from qa import validate_format_qa_entry, validate_ready_deliverable_qa
from schema import (
    CORE_PROJECT_REVIEW_AXES,
    FINAL_PHASES,
    GATE_ALIASES,
    GATE_REVIEW_MILESTONES,
    PHASE_REVIEW_GATE,
    REPORT_PHASES,
    REVIEW_GATES,
    REVIEW_MILESTONES,
    Report,
    read_required,
    string_array,
    valid_date_version,
    validate_hashed_path,
    validate_profile,
    validate_snapshot_files,
    validate_timestamp,
)


def validate_review_matrix(path_value: Any, report: Report) -> dict[str, Any] | None:
    """Validate the manuscript-specific review profile supplied to `acceptance`."""
    if not isinstance(path_value, str):
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("REVIEW_PROFILE_PATH", str(exc))
        return None
    matrix = read_required(path, report)
    if not matrix:
        return None
    if matrix.get("schema_version") != "1":
        report.error(
            "REVIEW_PROFILE_SCHEMA",
            "manuscript review profile schema_version must be 1",
        )
    if matrix.get("profile") != "manuscript":
        report.error(
            "REVIEW_PROFILE_TYPE",
            "review profile must identify the manuscript profile",
        )
    if matrix.get("milestone") not in REVIEW_MILESTONES:
        report.error(
            "REVIEW_PROFILE_MILESTONE",
            "manuscript review profile milestone is invalid",
        )
    snapshot, snapshot_captured_time, snapshot_captured_at = validate_snapshot_files(
        matrix.get("artifact_snapshot"),
        "REVIEW_PROFILE_SNAPSHOT",
        report,
    )
    axes = matrix.get("axes")
    if not isinstance(axes, list):
        report.error(
            "REVIEW_PROFILE_AXES",
            "manuscript review profile axes must be an array",
        )
        return None
    ids = [axis.get("id") for axis in axes if isinstance(axis, dict)]
    if len(ids) != len(set(ids)):
        report.error(
            "REVIEW_PROFILE_AXES",
            "manuscript review profile axis ids must be unique",
        )
    missing = sorted(REVIEW_AXIS_IDS - set(ids))
    if missing:
        report.error(
            "REVIEW_PROFILE_AXES",
            f"manuscript review profile omitted axes: {missing}",
        )
    for axis in axes:
        if not isinstance(axis, dict):
            report.error(
                "REVIEW_PROFILE_AXIS",
                "every manuscript review axis must be an object",
            )
            continue
        axis_id = axis.get("id", "<unknown>")
        if axis_id not in REVIEW_AXIS_IDS:
            report.error(
                "REVIEW_PROFILE_AXIS",
                f"{axis_id} is not a manuscript review axis",
            )
        applicable = axis.get("applicable")
        if not isinstance(applicable, bool):
            report.error(
                "REVIEW_PROFILE_APPLICABILITY",
                f"{axis_id} applicability is unresolved",
            )
        if not isinstance(axis.get("reason"), str) or not axis["reason"].strip():
            report.error(
                "REVIEW_PROFILE_REASON",
                f"{axis_id} requires an applicability reason",
            )
        evidence_required = axis.get("evidence_required")
        if not string_array(evidence_required):
            report.error(
                "REVIEW_PROFILE_EVIDENCE",
                f"{axis_id} evidence_required must be a string array",
            )
        elif applicable is True and not evidence_required:
            report.error(
                "REVIEW_PROFILE_EVIDENCE",
                f"{axis_id} requires at least one evidence requirement",
            )
    report.ok("REVIEW_PROFILE", f"validated {len(axes)} manuscript axes")
    applicable_axes = {
        axis["id"]
        for axis in axes
        if isinstance(axis, dict)
        and isinstance(axis.get("id"), str)
        and axis.get("applicable") is True
    }
    return {
        "path": path.relative_to(report.root).as_posix(),
        "milestone": matrix.get("milestone"),
        "snapshot": snapshot,
        "snapshot_captured_at": snapshot_captured_at,
        "snapshot_captured_time": snapshot_captured_time,
        "applicable_axes": applicable_axes,
        "axes": set(ids),
    }


def _validate_manuscript_evidence(
    evidence: Any,
    report: Report,
) -> set[str]:
    if not isinstance(evidence, list) or not evidence:
        report.error(
            "ACCEPTANCE_EVIDENCE",
            "acceptance result requires non-empty manuscript_evidence entries",
        )
        return set()
    axes: set[str] = set()
    for entry in evidence:
        if not isinstance(entry, dict):
            report.error(
                "ACCEPTANCE_EVIDENCE",
                "manuscript evidence entry must be an object",
            )
            continue
        axis = entry.get("axis")
        if not isinstance(axis, str) or axis not in REVIEW_AXIS_IDS or axis in axes:
            report.error(
                "ACCEPTANCE_EVIDENCE",
                f"manuscript evidence has unknown or duplicate axis {axis!r}",
            )
            continue
        axes.add(axis)
        artifacts = entry.get("evidence")
        if not isinstance(artifacts, list) or not artifacts:
            report.error(
                "ACCEPTANCE_EVIDENCE",
                f"{axis} requires at least one hashed evidence artifact",
            )
            continue
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                report.error(
                    "ACCEPTANCE_EVIDENCE",
                    f"{axis} evidence artifacts must be objects",
                )
                continue
            if (
                not isinstance(artifact.get("kind"), str)
                or not artifact["kind"].strip()
            ):
                report.error(
                    "ACCEPTANCE_EVIDENCE",
                    f"{axis} evidence artifacts require a kind",
                )
            validate_hashed_path(
                artifact.get("path"),
                artifact.get("sha256"),
                "ACCEPTANCE_EVIDENCE",
                report,
            )
    return axes


def validate_acceptance_report(
    path_value: Any,
    report: Report,
    _visited: set[str] | None = None,
) -> dict[str, Any] | None:
    """Validate the manuscript integration envelope emitted by `acceptance`."""
    _ = _visited
    if not isinstance(path_value, str):
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("ACCEPTANCE_PATH", str(exc))
        return None
    if not path.is_file():
        report.error("ACCEPTANCE_MISSING", f"missing acceptance result: {path_value}")
        return None
    if path.suffix.lower() != ".json":
        report.error(
            "ACCEPTANCE_MACHINE",
            "LifecycleState and GateReceipt must reference the JSON acceptance result",
        )
        return None
    review = read_required(path, report)
    if not review:
        return None
    if review.get("schema_version") != "1":
        report.error("ACCEPTANCE_SCHEMA", "acceptance result schema_version must be 1")
    if review.get("provider") != "acceptance":
        report.error(
            "ACCEPTANCE_PROVIDER",
            "review result must identify acceptance as provider",
        )
    if review.get("profile") != "manuscript":
        report.error(
            "ACCEPTANCE_PROFILE",
            "acceptance result must use the manuscript profile",
        )
    milestone = review.get("milestone")
    if milestone not in REVIEW_MILESTONES:
        report.error("ACCEPTANCE_MILESTONE", "acceptance result milestone is invalid")

    charter = review.get("charter")
    charter_path: str | None = None
    if charter is not None:
        if not isinstance(charter, dict):
            report.error(
                "ACCEPTANCE_CHARTER",
                "charter reference must be null or a path/sha256 object",
            )
        else:
            validated_charter = validate_hashed_path(
                charter.get("path"),
                charter.get("sha256"),
                "ACCEPTANCE_CHARTER",
                report,
            )
            if validated_charter:
                charter_path = validated_charter.relative_to(report.root).as_posix()

    snapshot, snapshot_captured_time, snapshot_captured_at = validate_snapshot_files(
        review.get("artifact_snapshot"),
        "ACCEPTANCE_SNAPSHOT",
        report,
    )
    verdict = review.get("verdict")
    result = verdict.get("result") if isinstance(verdict, dict) else verdict
    if result not in {"PASS", "FAIL", "BLOCKED"}:
        report.error(
            "ACCEPTANCE_VERDICT",
            "acceptance result must expose PASS, FAIL, or BLOCKED",
        )
    cause: str | None = None
    if isinstance(verdict, dict) and verdict.get("cause") is not None:
        raw_cause = verdict.get("cause")
        if raw_cause not in {"implementation", "direction"} or result != "FAIL":
            report.error(
                "ACCEPTANCE_CAUSE",
                "verdict.cause is permitted only on FAIL and must be implementation or direction",
            )
        else:
            cause = raw_cause

    completed_at = validate_timestamp(
        review.get("completed_at"),
        "ACCEPTANCE_COMPLETED_AT",
        report,
    )
    manuscript_axes = _validate_manuscript_evidence(
        review.get("manuscript_evidence"),
        report,
    )
    report.ok("ACCEPTANCE_RESULT", path_value)
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "milestone": milestone,
        "charter_path": charter_path,
        "snapshot": snapshot,
        "snapshot_captured_at": snapshot_captured_at,
        "snapshot_captured_time": snapshot_captured_time,
        "axes": manuscript_axes,
        "manuscript_axes": manuscript_axes,
        "verdict": result,
        "cause": cause,
        "completed_at": completed_at,
    }


validate_review_report = validate_acceptance_report


def required_review_axes(
    profile: dict[str, Any],
    source_result: dict[str, Any] | None,
    active_batch: dict[str, Any] | None,
) -> set[str]:
    required = set(CORE_PROJECT_REVIEW_AXES)
    if source_result and any(
        source.get("adapter_id") == "image-scan"
        for source in source_result.get("sources", {}).values()
        if isinstance(source, dict)
    ):
        required.add("images")
    if active_batch and isinstance(active_batch.get("review_axes"), list):
        required.update(
            axis for axis in active_batch["review_axes"] if axis in REVIEW_AXIS_IDS
        )
    if "pptx" in set(profile.get("formats", [])):
        required.add("images")
    return required


def validate_review_scope(
    lifecycle: dict[str, Any],
    batches: dict[str, dict[str, Any]],
    profile: dict[str, Any],
    source_result: dict[str, Any] | None,
    matrix_result: dict[str, Any],
    review_result: dict[str, Any],
    report: Report,
) -> None:
    active_batch = batches.get(lifecycle.get("active_batch"))
    mandatory_axes = required_review_axes(profile, source_result, active_batch)
    omitted_mandatory = sorted(mandatory_axes - matrix_result["applicable_axes"])
    if omitted_mandatory:
        report.error(
            "REVIEW_APPLICABILITY",
            f"Project review marked mandatory axes inapplicable: {omitted_mandatory}",
        )
    missing_domain_evidence = sorted(
        matrix_result["applicable_axes"] - review_result["manuscript_axes"]
    )
    if missing_domain_evidence:
        report.error(
            "REVIEW_EVIDENCE",
            f"acceptance result omits manuscript evidence for: {missing_domain_evidence}",
        )
    if lifecycle.get("phase") != "candidate":
        return
    if matrix_result["milestone"] != "candidate":
        report.error(
            "STATE_REVIEW_BINDING",
            "candidate phase requires a candidate milestone review",
        )
    if not active_batch:
        return
    for normalized_output, output_hash in active_batch.get(
        "_validated_outputs",
        {},
    ).items():
        if (
            output_hash is None
            or review_result["snapshot"].get(normalized_output) != output_hash
        ):
            report.error(
                "STATE_REVIEW_BINDING",
                f"candidate review snapshot does not hash-bind batch output {normalized_output}",
            )


def validate_publication_policy(
    publication: Any,
    gate: str,
    report: Report,
) -> dict[str, Any] | None:
    if not isinstance(publication, dict):
        report.error("GATE_PUBLICATION", f"{gate} requires publication policy")
        return None
    if gate != "publish-approved":
        if (
            publication.get("required") is not False
            or publication.get("target") is not None
            or publication.get("final_receipt") is not None
        ):
            report.error(
                "GATE_PUBLICATION",
                f"{gate} must record publication as not required",
            )
        return None
    if publication.get("required") is not True:
        report.error(
            "GATE_PUBLICATION",
            "publish-approved requires publication.required=true",
        )
    target = publication.get("target")
    if not isinstance(target, dict):
        report.error(
            "GATE_PUBLICATION",
            "publish-approved requires a structured publication target",
        )
    else:
        if target.get("kind") not in {
            "repository",
            "release",
            "deployment",
            "installation",
            "distribution",
            "other",
        }:
            report.error("GATE_PUBLICATION", "publication target kind is invalid")
        if target.get("visibility") not in {
            "public",
            "private",
            "internal",
            "local",
        }:
            report.error(
                "GATE_PUBLICATION",
                "publication target visibility is invalid",
            )
        for field in ("identifier", "action", "evidence"):
            if not isinstance(target.get(field), str) or not target[field].strip():
                report.error(
                    "GATE_PUBLICATION",
                    f"publication target requires {field}",
                )
    final_receipt = publication.get("final_receipt")
    parsed_final_receipt: dict[str, Any] | None = None
    final_receipt_path: Path | None = None
    final_created_at: datetime | None = None
    final_confirmed_at: datetime | None = None
    if not isinstance(final_receipt, dict):
        report.error(
            "GATE_PUBLICATION",
            "publish-approved requires a hash-bound final receipt",
        )
    else:
        final_receipt_path = validate_hashed_path(
            final_receipt.get("path"),
            final_receipt.get("sha256"),
            "GATE_PUBLICATION_FINAL",
            report,
        )
        if final_receipt_path:
            parsed_final_receipt = read_required(final_receipt_path, report)
            if (
                not parsed_final_receipt
                or parsed_final_receipt.get("gate") != "final-approved"
            ):
                report.error(
                    "GATE_PUBLICATION",
                    "publication final_receipt must reference a final-approved receipt",
                )
            else:
                final_created_at = validate_timestamp(
                    parsed_final_receipt.get("created_at"),
                    "GATE_PUBLICATION_FINAL_TIME",
                    report,
                )
                final_confirmation = parsed_final_receipt.get("user_confirmation")
                if not isinstance(final_confirmation, dict):
                    report.error(
                        "GATE_PUBLICATION_FINAL_TIME",
                        "publication final receipt has no user confirmation",
                    )
                else:
                    final_confirmed_at = validate_timestamp(
                        final_confirmation.get("confirmed_at"),
                        "GATE_PUBLICATION_FINAL_TIME",
                        report,
                    )
    return {
        "final_bookmark": (
            parsed_final_receipt.get("bookmark") if parsed_final_receipt else None
        ),
        "final_path": (
            final_receipt_path.relative_to(report.root).as_posix()
            if final_receipt_path
            else None
        ),
        "final_sha256": (
            str(final_receipt.get("sha256", "")).lower()
            if isinstance(final_receipt, dict)
            else None
        ),
        "final_created_at": final_created_at,
        "final_confirmed_at": final_confirmed_at,
        "target": target if isinstance(target, dict) else None,
    }


def validate_receipts(
    state_dir: Path,
    lifecycle: dict[str, Any],
    profile: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
    lifecycle_review: dict[str, Any] | None,
    lifecycle_qa: dict[str, dict[str, Any]],
    lifecycle_capability: dict[str, Any] | None,
    brief_result: dict[str, Any] | None,
    source_result: dict[str, Any] | None,
    report: Report,
) -> dict[str, Any]:
    receipts: list[dict[str, Any]] = []
    gates_dir = state_dir / "gates"
    if not gates_dir.is_dir():
        report.error("GATES_MISSING", "missing .manuscript-ops/gates directory")
        return {"all": receipts, "active": {}, "metadata": {}}
    seen_gates: set[str] = set()
    seen_bookmarks: set[str] = set()
    by_bookmark: dict[str, dict[str, Any]] = {}
    receipt_metadata: dict[str, dict[str, str]] = {}
    receipt_file_sets: dict[str, dict[str, str]] = {}
    publication_bindings: dict[str, dict[str, Any]] = {}
    locked_source_bindings: dict[str, dict[str, str]] = {}
    for path in sorted(gates_dir.rglob("*.json")):
        try:
            receipt = load_json(path)
        except ContractError as exc:
            report.error("GATE_JSON", str(exc))
            continue
        if not isinstance(receipt, dict):
            report.error("GATE_OBJECT", f"{path} must contain an object")
            continue
        gate = receipt.get("gate")
        if gate not in GATE_ALIASES:
            report.error("GATE_TYPE", f"invalid gate type in {path}")
            continue
        seen_gates.add(gate)
        if receipt.get("schema_version") != "1":
            report.error("GATE_SCHEMA", f"{path} schema_version must be 1")
        date_version = receipt.get("date_version")
        if not valid_date_version(date_version):
            report.error("GATE_VERSION", f"invalid date version in {path}")
        bookmark = receipt.get("bookmark")
        expected_bookmark = f"{gate}-{date_version}"
        if bookmark != expected_bookmark:
            report.error("GATE_BOOKMARK", f"{path} bookmark must be {expected_bookmark}")
        elif bookmark in seen_bookmarks:
            report.error("GATE_DUPLICATE", f"duplicate gate bookmark: {bookmark}")
        else:
            seen_bookmarks.add(bookmark)
            by_bookmark[bookmark] = receipt
            receipt_metadata[bookmark] = {
                "path": path.resolve().relative_to(report.root).as_posix(),
                "sha256": sha256_file(path),
            }
        if isinstance(bookmark, str) and path.stem != bookmark:
            report.error(
                "GATE_FILENAME",
                f"receipt filename {path.name} must match bookmark {bookmark}",
            )
        expected_alias = GATE_ALIASES[gate]
        if receipt.get("current_alias") != expected_alias:
            report.error("GATE_ALIAS", f"{path} current_alias must be {expected_alias}")
        created_time = validate_timestamp(
            receipt.get("created_at"),
            "GATE_CREATED_AT",
            report,
        )

        jj = receipt.get("jujutsu")
        if not isinstance(jj, dict):
            report.error("GATE_JJ", f"{path} requires Jujutsu evidence")
        else:
            for field in ("version", "change_id", "commit_id"):
                if not isinstance(jj.get(field), str) or not jj[field]:
                    report.error("GATE_JJ", f"{path} missing jujutsu.{field}")
            remote_count = jj.get("remote_count")
            if (
                not isinstance(remote_count, int)
                or isinstance(remote_count, bool)
                or remote_count < 0
            ):
                report.error("GATE_JJ", f"{path} has invalid remote_count")
            if remote_count and not profile.get("version_control", {}).get(
                "remote_allowed", False
            ):
                report.error("GATE_JJ_REMOTE", f"{path} records a forbidden remote")

        files = receipt.get("files")
        normalized_files: dict[str, str] = {}
        if not isinstance(files, list) or not files:
            report.error("GATE_FILES", f"receipt has no files: {path}")
        else:
            for entry in files:
                if not isinstance(entry, dict):
                    report.error("GATE_FILE_ENTRY", f"invalid file entry in {path}")
                    continue
                target = validate_hashed_path(
                    entry.get("path"),
                    entry.get("sha256"),
                    "GATE_FILE",
                    report,
                )
                if target:
                    normalized_files[target.relative_to(report.root).as_posix()] = str(
                        entry["sha256"]
                    ).lower()
        if isinstance(bookmark, str):
            receipt_file_sets[bookmark] = normalized_files

        baseline_profile = receipt.get("baseline_profile")
        baseline_required = gate == "baseline"
        if (
            not isinstance(baseline_profile, dict)
            or baseline_profile.get("required") is not baseline_required
        ):
            report.error(
                "GATE_BASELINE_PROFILE",
                f"{gate} baseline_profile.required must be {baseline_required}",
            )
        elif baseline_required:
            baseline_profile_path = validate_hashed_path(
                baseline_profile.get("path"),
                baseline_profile.get("sha256"),
                "GATE_BASELINE_PROFILE",
                report,
            )
            if baseline_profile_path:
                relative_profile_snapshot = baseline_profile_path.relative_to(
                    report.root
                ).as_posix()
                if not relative_profile_snapshot.startswith(
                    ".manuscript-ops/snapshots/"
                ):
                    report.error(
                        "GATE_BASELINE_PROFILE",
                        "baseline Profile snapshot must be stored under .manuscript-ops/snapshots/",
                    )
                if (
                    normalized_files.get(relative_profile_snapshot)
                    != str(baseline_profile.get("sha256", "")).lower()
                ):
                    report.error(
                        "GATE_BASELINE_PROFILE",
                        "baseline receipt files do not bind its Profile snapshot",
                    )
                baseline_payload = read_required(baseline_profile_path, report)
                baseline_date = (
                    baseline_payload.get("date_version")
                    if isinstance(baseline_payload, dict)
                    else None
                )
                baseline_normalized = (
                    validate_profile(baseline_payload, report)
                    if isinstance(baseline_payload, dict)
                    else {}
                )
                if (
                    not baseline_payload
                    or baseline_payload.get("schema_version") != "1"
                    or not isinstance(baseline_payload.get("paths"), dict)
                    or not baseline_payload.get("paths")
                    or not isinstance(baseline_payload.get("version_control"), dict)
                    or not isinstance(baseline_date, dict)
                    or not valid_date_version(baseline_date.get("value"))
                    or not baseline_normalized.get("paths")
                    or not baseline_normalized.get("version_control")
                ):
                    report.error(
                        "GATE_BASELINE_PROFILE",
                        "baseline Profile snapshot lacks the dated path/VCS configuration",
                    )
        elif baseline_profile.get("path") not in {"", None} or baseline_profile.get(
            "sha256"
        ) not in {"", None}:
            report.error(
                "GATE_BASELINE_PROFILE",
                f"{gate} cannot retain baseline Profile evidence",
            )

        locked_source = receipt.get("locked_source")
        locked_source_required = gate == "source-locked"
        if (
            not isinstance(locked_source, dict)
            or locked_source.get("required") is not locked_source_required
        ):
            report.error(
                "GATE_LOCKED_SOURCE",
                f"{gate} locked_source.required must be {locked_source_required}",
            )
        elif locked_source_required:
            locked_source_path = validate_hashed_path(
                locked_source.get("path"),
                locked_source.get("sha256"),
                "GATE_LOCKED_SOURCE",
                report,
            )
            if locked_source_path:
                normalized_locked_source = locked_source_path.relative_to(
                    report.root
                ).as_posix()
                locked_source_hash = str(locked_source.get("sha256", "")).lower()
                if normalized_files.get(normalized_locked_source) != locked_source_hash:
                    report.error(
                        "GATE_LOCKED_SOURCE",
                        "source-lock receipt files do not bind the locked manuscript",
                    )
                manuscript_value = profile.get("paths", {}).get("manuscript")
                if isinstance(manuscript_value, str):
                    try:
                        manuscript_root = ensure_within_root(
                            report.root,
                            Path(manuscript_value),
                        )
                        inside_mapping = (
                            locked_source_path == manuscript_root
                            if manuscript_root.is_file()
                            else locked_source_path.is_relative_to(manuscript_root)
                        )
                    except (ContractError, OSError, ValueError):
                        inside_mapping = False
                    if not inside_mapping:
                        report.error(
                            "GATE_LOCKED_SOURCE",
                            "locked manuscript is outside the Profile manuscript mapping",
                        )
                else:
                    report.error(
                        "GATE_LOCKED_SOURCE",
                        "ProjectProfile has no manuscript mapping for source lock",
                    )
                if isinstance(bookmark, str):
                    locked_source_bindings[bookmark] = {
                        "path": normalized_locked_source,
                        "sha256": locked_source_hash,
                    }
        elif locked_source.get("path") not in {"", None} or locked_source.get(
            "sha256"
        ) not in {"", None}:
            report.error(
                "GATE_LOCKED_SOURCE",
                f"{gate} cannot retain locked-source evidence",
            )

        publication_binding = validate_publication_policy(
            receipt.get("publication"),
            gate,
            report,
        )
        if isinstance(bookmark, str) and publication_binding:
            publication_bindings[bookmark] = publication_binding

        capability = receipt.get("capability_snapshot")
        capability_time: datetime | None = None
        if not isinstance(capability, dict) or not isinstance(
            capability.get("required"), bool
        ):
            report.error("GATE_CAPABILITY", f"{path} has invalid capability evidence")
        elif capability["required"]:
            capability_path = validate_hashed_path(
                capability.get("path"),
                capability.get("sha256"),
                "GATE_CAPABILITY",
                report,
            )
            if capability_path:
                capability_payload = read_required(capability_path, report)
                if capability_payload:
                    capability_time = validate_timestamp(
                        capability_payload.get("captured_at"),
                        "GATE_CAPABILITY_TIME",
                        report,
                    )

        qa = receipt.get("format_qa")
        qa_by_artifact: dict[str, dict[str, Any]] = {}
        if not isinstance(qa, list):
            report.error("GATE_FORMAT_QA", f"{path} format_qa must be an array")
        else:
            for item in qa:
                normalized_qa = validate_format_qa_entry(
                    item,
                    adapters,
                    report,
                    brief_result,
                )
                if normalized_qa:
                    artifact_id = normalized_qa.get("artifact_path")
                    if not artifact_id:
                        report.error(
                            "GATE_FORMAT_QA",
                            f"{gate} QA record has no validated artifact",
                        )
                    elif artifact_id in qa_by_artifact:
                        report.error(
                            "GATE_FORMAT_QA",
                            f"{gate} repeats QA for deliverable {artifact_id}",
                        )
                    else:
                        qa_by_artifact[artifact_id] = normalized_qa
        if gate in {"final-approved", "publish-approved"}:
            validate_ready_deliverable_qa(
                brief_result,
                qa_by_artifact,
                "GATE_FORMAT_QA",
                gate,
                report,
            )
            if not isinstance(capability, dict) or capability.get("required") is not True:
                report.error(
                    "GATE_CAPABILITY",
                    f"{gate} requires a hashed capability snapshot",
                )

        review = receipt.get("review")
        should_review = gate in REVIEW_GATES
        parsed_review: dict[str, Any] | None = None
        if not isinstance(review, dict) or review.get("required") is not should_review:
            report.error("GATE_REVIEW", f"{gate} review.required must be {should_review}")
        elif should_review:
            review_path = validate_hashed_path(
                review.get("report_path"),
                review.get("report_sha256"),
                "GATE_REVIEW",
                report,
            )
            parsed_review = validate_acceptance_report(review.get("report_path"), report)
            if review.get("verdict") != "PASS":
                report.error("GATE_REVIEW", f"{gate} requires an acceptance PASS")
            if parsed_review:
                expected_milestone = GATE_REVIEW_MILESTONES[gate]
                if parsed_review["milestone"] != expected_milestone:
                    report.error(
                        "GATE_REVIEW",
                        f"{gate} requires milestone {expected_milestone}",
                    )
                if review.get("verdict") != parsed_review.get("verdict"):
                    report.error(
                        "GATE_REVIEW_MISMATCH",
                        f"{gate} receipt verdict differs from the hashed acceptance result",
                    )
                for artifact_path, artifact_hash in parsed_review["snapshot"].items():
                    if normalized_files.get(artifact_path) != artifact_hash:
                        report.error(
                            "GATE_REVIEW_ARTIFACT",
                            f"{gate} receipt does not bind reviewed artifact {artifact_path}",
                        )
                if gate == "framework-approved":
                    outline_value = profile.get("paths", {}).get("outline")
                    if not isinstance(outline_value, str):
                        report.error(
                            "GATE_FRAMEWORK_ARTIFACT",
                            "ProjectProfile has no mapped outline artifact",
                        )
                    else:
                        try:
                            outline_path = ensure_within_root(
                                report.root,
                                Path(outline_value),
                            )
                            normalized_outline = outline_path.relative_to(
                                report.root
                            ).as_posix()
                        except (ContractError, ValueError) as exc:
                            report.error("GATE_FRAMEWORK_ARTIFACT", str(exc))
                        else:
                            if not outline_path.is_file():
                                report.error(
                                    "GATE_FRAMEWORK_ARTIFACT",
                                    "framework gate requires the mapped outline to be a file",
                                )
                            outline_hash = normalized_files.get(normalized_outline)
                            if (
                                not outline_hash
                                or parsed_review["snapshot"].get(normalized_outline)
                                != outline_hash
                            ):
                                report.error(
                                    "GATE_FRAMEWORK_ARTIFACT",
                                    "framework receipt and review must hash-bind the mapped outline",
                                )
                if gate == "source-locked" and isinstance(bookmark, str):
                    locked_binding = locked_source_bindings.get(bookmark)
                    if (
                        not locked_binding
                        or parsed_review["snapshot"].get(locked_binding["path"])
                        != locked_binding["sha256"]
                    ):
                        report.error(
                            "GATE_LOCKED_SOURCE",
                            "source-lock review does not hash-bind the locked manuscript",
                        )
            if review_path and str(review_path.relative_to(report.root)) != str(
                Path(review.get("report_path"))
            ):
                report.error(
                    "GATE_REVIEW",
                    f"{gate} review path normalization differs",
                )
        else:
            if review.get("verdict") != "NOT_REQUIRED":
                report.error(
                    "GATE_REVIEW",
                    f"{gate} review verdict must be NOT_REQUIRED",
                )

        if gate in {"final-approved", "publish-approved"}:
            for artifact_id, qa_entry in qa_by_artifact.items():
                artifact_path = qa_entry.get("artifact_path")
                artifact_hash = qa_entry.get("artifact_sha256")
                if (
                    not artifact_path
                    or not artifact_hash
                    or normalized_files.get(artifact_path) != artifact_hash
                ):
                    report.error(
                        "GATE_FORMAT_QA_ARTIFACT",
                        f"{gate} receipt does not bind QA artifact {artifact_id}",
                    )
                if (
                    parsed_review
                    and parsed_review["snapshot"].get(artifact_path) != artifact_hash
                ):
                    report.error(
                        "GATE_REVIEW_ARTIFACT",
                        f"{gate} review snapshot does not bind QA artifact {artifact_id}",
                    )

        confirmation = receipt.get("user_confirmation")
        confirmation_time: datetime | None = None
        if not isinstance(confirmation, dict):
            report.error("GATE_CONFIRMATION", f"{path} requires user confirmation")
        else:
            for field in ("actor", "exact_statement"):
                if (
                    not isinstance(confirmation.get(field), str)
                    or not confirmation[field].strip()
                ):
                    report.error(
                        "GATE_CONFIRMATION",
                        f"{path} missing confirmation {field}",
                    )
            confirmation_time = validate_timestamp(
                confirmation.get("confirmed_at"),
                "GATE_CONFIRMATION_TIME",
                report,
            )
        if created_time and confirmation_time and created_time < confirmation_time:
            report.error(
                "GATE_CONFIRMATION_TIME",
                f"{gate} receipt was created before its user confirmation",
            )
        evidence_times = [
            parsed_review.get("completed_at") if parsed_review else None,
            capability_time,
            *[item.get("completed_at") for item in qa_by_artifact.values()],
        ]
        if confirmation_time and any(
            isinstance(evidence_time, datetime) and evidence_time > confirmation_time
            for evidence_time in evidence_times
        ):
            report.error(
                "GATE_CONFIRMATION_TIME",
                f"{gate} was confirmed before its review, capability, or format-QA evidence completed",
            )
        if gate == "publish-approved" and publication_binding and confirmation_time:
            final_times = (
                publication_binding.get("final_confirmed_at"),
                publication_binding.get("final_created_at"),
            )
            if any(
                isinstance(final_time, datetime) and final_time > confirmation_time
                for final_time in final_times
            ):
                report.error(
                    "GATE_PUBLICATION_CHRONOLOGY",
                    "publish approval was confirmed before the referenced final approval receipt existed",
                )
        receipts.append(receipt)

    required = lifecycle.get("required_gates", set())
    missing = sorted(required - seen_gates)
    if missing:
        report.error("GATES_REQUIRED", f"missing required gate receipts: {missing}")
    ahead = sorted(seen_gates - required)
    if ahead:
        report.error(
            "GATES_PHASE",
            f"gate receipts are ahead of lifecycle state: {ahead}",
        )
    if not receipts:
        report.error("GATES_EMPTY", "no gate receipts found")
    else:
        report.ok("GATES_PRESENT", f"{len(receipts)} phase-consistent receipt(s)")
    active: dict[str, dict[str, Any]] = {}
    for gate, bookmark in lifecycle.get("active_receipts", {}).items():
        receipt = by_bookmark.get(bookmark)
        if receipt is None:
            report.error(
                "GATE_ACTIVE_MISSING",
                f"active receipt {bookmark!r} for {gate} was not found",
            )
            continue
        if receipt.get("gate") != gate:
            report.error(
                "GATE_ACTIVE_TYPE",
                f"active receipt {bookmark!r} is not a {gate} receipt",
            )
            continue
        active[gate] = receipt

    active_brief = active.get("brief-approved")
    if active_brief and brief_result:
        brief_files = receipt_file_sets.get(active_brief["bookmark"], {})
        if brief_files.get(brief_result["path"]) != brief_result["sha256"]:
            report.error(
                "BRIEF_GATE_BINDING",
                "active brief-approved receipt does not bind the approved ManuscriptBrief",
            )
        brief_confirmation = active_brief.get("user_confirmation", {})
        expected_confirmation = {
            "actor": brief_result.get("approver"),
            "exact_statement": brief_result.get("exact_confirmation"),
            "confirmed_at": brief_result.get("confirmed_at"),
        }
        if any(
            brief_confirmation.get(field) != expected
            for field, expected in expected_confirmation.items()
        ):
            report.error(
                "BRIEF_GATE_CONFIRMATION",
                "active brief-approved receipt confirmation differs from the approved ManuscriptBrief",
            )

    active_source = active.get("source-locked")
    if active_source and source_result:
        source_files = receipt_file_sets.get(active_source["bookmark"], {})
        if source_files.get(source_result["path"]) != source_result["sha256"]:
            report.error(
                "SOURCE_GATE_BINDING",
                "active source-locked receipt does not bind the current Source Register",
            )
        source_review = active_source.get("review", {})
        parsed_source_review = validate_acceptance_report(
            source_review.get("report_path"),
            report,
        )
        if (
            parsed_source_review
            and parsed_source_review["snapshot"].get(source_result["path"])
            != source_result["sha256"]
        ):
            report.error(
                "SOURCE_GATE_BINDING",
                "source-lock acceptance snapshot does not bind the current Source Register",
            )
    if active_source and lifecycle_qa:
        locked_binding = locked_source_bindings.get(active_source.get("bookmark"))
        if not locked_binding:
            report.error(
                "SOURCE_GATE_BINDING",
                "active source-lock receipt has no locked manuscript binding",
            )
        else:
            for artifact_id, qa_entry in lifecycle_qa.items():
                if qa_entry.get("semantic_reference") != locked_binding:
                    report.error(
                        "FORMAT_QA_SOURCE_LINEAGE",
                        f"{artifact_id} semantic QA does not compare the active locked manuscript",
                    )
                generation_inputs = (
                    qa_entry.get("generation", {}).get("inputs", {})
                    if isinstance(qa_entry.get("generation"), dict)
                    else {}
                )
                if (
                    generation_inputs.get(locked_binding["path"])
                    != locked_binding["sha256"]
                ):
                    report.error(
                        "FORMAT_QA_SOURCE_LINEAGE",
                        f"{artifact_id} generation inputs do not bind the active locked manuscript",
                    )

    active_publish = active.get("publish-approved")
    active_final = active.get("final-approved")
    if active_publish:
        binding = publication_bindings.get(active_publish.get("bookmark"), {})
        active_final_metadata = (
            receipt_metadata.get(active_final.get("bookmark"))
            if active_final
            else None
        )
        if (
            not active_final
            or binding.get("final_bookmark") != active_final.get("bookmark")
            or not active_final_metadata
            or binding.get("final_path") != active_final_metadata.get("path")
            or binding.get("final_sha256") != active_final_metadata.get("sha256")
        ):
            report.error(
                "GATE_PUBLICATION_BINDING",
                "active publish-approved receipt does not path/hash-bind the active final-approved receipt",
            )

    expected_review_gate = PHASE_REVIEW_GATE.get(lifecycle.get("phase"))
    if (
        lifecycle.get("phase") in REPORT_PHASES
        and lifecycle_review
        and lifecycle_review.get("verdict") != "PASS"
    ):
        report.error(
            "STATE_REVIEW_VERDICT",
            f"phase {lifecycle.get('phase')} requires acceptance PASS",
        )
    if expected_review_gate and lifecycle_review:
        receipt = active.get(expected_review_gate)
        receipt_review = receipt.get("review", {}) if receipt else {}
        if not receipt or receipt_review.get("report_path") != lifecycle_review["path"]:
            report.error(
                "STATE_REVIEW_BINDING",
                f"latest acceptance report is not bound by active {expected_review_gate}",
            )
        elif (
            str(receipt_review.get("report_sha256", "")).lower()
            != lifecycle_review["sha256"]
        ):
            report.error(
                "STATE_REVIEW_BINDING",
                "latest acceptance report hash differs from its active gate receipt",
            )
    if lifecycle.get("phase") in FINAL_PHASES:
        for gate in (
            {"final-approved", "publish-approved"}
            if lifecycle.get("phase") in {"published", "archived"}
            else {"final-approved"}
        ):
            receipt = active.get(gate)
            if not receipt:
                continue
            receipt_qa = {
                item["artifact_path"]: item
                for item in (
                    validate_format_qa_entry(
                        entry,
                        adapters,
                        report,
                        brief_result,
                    )
                    for entry in receipt.get("format_qa", [])
                )
                if item and item.get("artifact_path")
            }
            if receipt_qa != lifecycle_qa:
                report.error(
                    "STATE_FORMAT_QA_BINDING",
                    f"lifecycle format QA differs from active {gate} receipt",
                )
            capability = receipt.get("capability_snapshot", {})
            if not lifecycle_capability or (
                capability.get("path") != lifecycle_capability["path"]
                or str(capability.get("sha256", "")).lower()
                != lifecycle_capability["sha256"]
            ):
                report.error(
                    "STATE_CAPABILITY_BINDING",
                    f"lifecycle capability snapshot differs from active {gate} receipt",
                )
    return {
        "all": receipts,
        "active": active,
        "metadata": receipt_metadata,
    }


def run_jj(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    command = ["jj", "--ignore-working-copy", "-R", str(root), *args]
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def run_jj_bytes(
    root: Path,
    *args: str,
) -> subprocess.CompletedProcess[bytes] | None:
    command = ["jj", "--ignore-working-copy", "-R", str(root), *args]
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            cwd=root,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def validate_version_control(
    profile: dict[str, Any],
    receipts: dict[str, Any] | list[dict[str, Any]],
    report: Report,
) -> None:
    if profile.get("route") != "Project":
        report.ok("VCS_NOT_APPLICABLE", "lightweight writing has no version gate")
        return
    system = profile.get("version_control", {}).get("system")
    if system == "jj":
        receipt_index = (
            receipts
            if isinstance(receipts, dict)
            else {"all": receipts, "active": {}, "metadata": {}}
        )
        validate_jj(profile, receipt_index, report)
    else:
        report.error(
            "VCS_GATES_UNSUPPORTED",
            f"no receipt-bound gate verifier for declared backend {system!r}; do not substitute Jujutsu checks or snapshot PASS",
        )


def validate_jj(
    profile: dict[str, Any],
    receipt_index: dict[str, Any],
    report: Report,
) -> None:
    if not (report.root / ".jj" / "repo").exists():
        report.error("JJ_MISSING", "Project route has no valid .jj repository")
        return
    version = run_jj(report.root, "--version")
    if not version or version.returncode != 0:
        report.error("JJ_UNAVAILABLE", "cannot execute jj for this repository")
        return
    observed_version = version.stdout.strip()
    baseline = profile.get("version_control", {}).get("tested_baseline")
    if isinstance(baseline, str) and baseline not in observed_version:
        report.warn("JJ_VERSION", f"command probing required for {observed_version}")
    else:
        report.ok("JJ_VERSION", observed_version)

    immutable_config = run_jj(
        report.root,
        "config",
        "list",
        "--repo",
        'revset-aliases."immutable_heads()"',
        "-T",
        "value",
    )
    if not immutable_config or immutable_config.returncode != 0:
        report.error(
            "JJ_IMMUTABLE_CONFIG",
            "cannot read repository-local immutable_heads configuration",
        )
    else:
        configured = immutable_config.stdout
        required_patterns = [f"{gate}-*" for gate in GATE_ALIASES]
        missing_patterns = [
            pattern for pattern in required_patterns if pattern not in configured
        ]
        if missing_patterns:
            report.error(
                "JJ_IMMUTABLE_CONFIG",
                f"immutable_heads omits dated gate patterns: {missing_patterns}",
            )
        if "current-" in configured:
            report.error(
                "JJ_ALIAS_IMMUTABLE",
                "immutable_heads must not include mutable current-* aliases",
            )
        if not missing_patterns and "current-" not in configured:
            report.ok(
                "JJ_IMMUTABLE_CONFIG",
                "repository config protects dated gates and excludes current aliases",
            )

    remotes = run_jj(report.root, "git", "remote", "list")
    if not remotes or remotes.returncode != 0:
        report.error("JJ_REMOTE_CHECK", "could not list Jujutsu Git remotes")
    else:
        lines = [line for line in remotes.stdout.splitlines() if line.strip()]
        remote_policy = profile.get("version_control", {}).get("remote_allowed", False)
        if lines and not remote_policy:
            report.error("JJ_REMOTE_POLICY", f"unexpected remote(s): {lines}")
        else:
            report.ok(
                "JJ_REMOTE_POLICY",
                f"{len(lines)} remote(s), policy={remote_policy}",
            )

    bookmarks = run_jj(report.root, "bookmark", "list")
    if not bookmarks or bookmarks.returncode != 0:
        report.error("JJ_BOOKMARK_CHECK", "could not list Jujutsu bookmarks")
        return
    names = {
        line.split(":", 1)[0].strip()
        for line in bookmarks.stdout.splitlines()
        if ":" in line and not line.startswith(" ")
    }

    def revision_value(revision: str, template: str) -> str | None:
        result = run_jj(
            report.root,
            "log",
            "-r",
            revision,
            "--no-graph",
            "-T",
            template,
        )
        if not result or result.returncode != 0:
            return None
        return result.stdout.strip()

    active_bookmarks = {
        receipt["bookmark"]
        for receipt in receipt_index.get("active", {}).values()
        if isinstance(receipt, dict) and isinstance(receipt.get("bookmark"), str)
    }
    for receipt in receipt_index.get("all", []):
        if not isinstance(receipt, dict):
            report.error("JJ_RECEIPT_SCHEMA", "GateReceipt must be an object")
            continue
        bookmark = receipt.get("bookmark")
        alias = receipt.get("current_alias")
        if (
            not isinstance(bookmark, str)
            or not bookmark
            or not isinstance(alias, str)
            or not alias
        ):
            report.error(
                "JJ_RECEIPT_SCHEMA",
                "GateReceipt requires string bookmark and current_alias",
            )
            continue
        if bookmark not in names:
            report.error("JJ_GATE_MISSING", f"missing gate bookmark: {bookmark}")
            continue
        seal_commit = revision_value(bookmark, "commit_id")
        if not seal_commit:
            report.error("JJ_GATE_RESOLVE", f"cannot resolve gate bookmark: {bookmark}")
            continue
        receipt_jj = receipt.get("jujutsu")
        if not isinstance(receipt_jj, dict):
            report.error(
                "JJ_RECEIPT_SCHEMA",
                f"{bookmark} requires a Jujutsu evidence object",
            )
            receipt_jj = {}
        receipt_commit = receipt_jj.get("commit_id")
        content_commit = revision_value(f"parents({bookmark})", "commit_id")
        if not content_commit or content_commit != receipt_commit:
            report.error(
                "JJ_RECEIPT_COMMIT",
                f"receipt content commit is not the parent of seal {bookmark}",
            )
        gate_change = revision_value(f"parents({bookmark})", "change_id")
        receipt_change = receipt_jj.get("change_id")
        if not gate_change or gate_change != receipt_change:
            report.error(
                "JJ_RECEIPT_CHANGE",
                f"receipt content change is not the parent of seal {bookmark}",
            )
        immutable = revision_value(bookmark, 'if(immutable, "true", "false")')
        if immutable != "true":
            report.error("JJ_GATE_MUTABLE", f"dated gate is not immutable: {bookmark}")
        else:
            report.ok("JJ_GATE_IMMUTABLE", bookmark)
        receipt_metadata = receipt_index.get("metadata", {}).get(bookmark)
        if not isinstance(receipt_metadata, dict):
            report.error(
                "JJ_GATE_RECEIPT_MISSING",
                f"no local receipt metadata for {bookmark}",
            )
        else:
            receipt_path = receipt_metadata.get("path")
            gated_receipt = (
                run_jj_bytes(
                    report.root,
                    "file",
                    "show",
                    "-r",
                    bookmark,
                    receipt_path,
                )
                if isinstance(receipt_path, str)
                else None
            )
            if not gated_receipt or gated_receipt.returncode != 0:
                report.error(
                    "JJ_GATE_RECEIPT_MISSING",
                    f"{bookmark} does not contain its GateReceipt",
                )
            elif (
                hashlib.sha256(gated_receipt.stdout).hexdigest()
                != receipt_metadata.get("sha256")
            ):
                report.error(
                    "JJ_GATE_RECEIPT_HASH",
                    f"{bookmark} contains different GateReceipt bytes",
                )
            else:
                report.ok("JJ_GATE_RECEIPT_HASH", bookmark)
        receipt_files = receipt.get("files")
        if not isinstance(receipt_files, list):
            report.error(
                "JJ_RECEIPT_SCHEMA",
                f"{bookmark} requires a files array",
            )
            receipt_files = []
        for file_entry in receipt_files:
            if (
                not isinstance(file_entry, dict)
                or not isinstance(file_entry.get("path"), str)
                or not isinstance(file_entry.get("sha256"), str)
            ):
                continue
            file_path = Path(file_entry["path"]).as_posix()
            gated_file = run_jj_bytes(
                report.root,
                "file",
                "show",
                "-r",
                content_commit or f"parents({bookmark})",
                file_path,
            )
            if not gated_file or gated_file.returncode != 0:
                report.error(
                    "JJ_GATE_FILE_MISSING",
                    f"{bookmark} does not contain gated file {file_path}",
                )
                continue
            observed_hash = hashlib.sha256(gated_file.stdout).hexdigest()
            if observed_hash != file_entry["sha256"].lower():
                report.error(
                    "JJ_GATE_FILE_HASH",
                    f"{bookmark} bytes differ from receipt hash for {file_path}",
                )
            else:
                report.ok(
                    "JJ_GATE_FILE_HASH",
                    f"{bookmark} parent:{file_path}",
                )
        if bookmark in active_bookmarks:
            if alias not in names:
                report.error("JJ_ALIAS_MISSING", f"missing current alias: {alias}")
            else:
                alias_commit = revision_value(alias, "commit_id")
                if alias_commit != seal_commit:
                    report.error(
                        "JJ_ALIAS_TARGET",
                        f"{alias} does not point to {bookmark}",
                    )
                else:
                    report.ok("JJ_ALIAS_TARGET", f"{alias} -> {bookmark}")
    report.ok("JJ_BOOKMARK_CHECK", f"observed {len(names)} bookmark(s)")
