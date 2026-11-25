#!/usr/bin/env python3
"""Validate manuscript-ops state without changing the project."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from gates import (
    required_review_axes,
    run_jj,
    run_jj_bytes,
    validate_acceptance_report,
    validate_jj,
    validate_publication_policy,
    validate_receipts,
    validate_review_matrix,
    validate_review_report,
    validate_review_scope,
    validate_version_control,
)
from lineage import (
    check_document_source_identity,
    validate_batch_source_dependencies,
    validate_batches,
    validate_brief_source_expectations,
    validate_source_register,
)
from manuscript_ops_core import ContractError, dump_json, parse_timestamp
from qa import (
    validate_capability_snapshot,
    validate_format_qa_entry,
    validate_generation_record,
    validate_qa_check,
    validate_ready_deliverable_qa,
)
from schema import (
    FINAL_PHASES,
    Report,
    read_required,
    string_array,
    unwrap_profile_value,
    valid_date_version,
    validate_brief,
    validate_format_registry,
    validate_hashed_path,
    validate_lifecycle_state,
    validate_profile,
    validate_routing,
    validate_snapshot_files,
    validate_timestamp,
)

__all__ = [
    "Report",
    "check_document_source_identity",
    "main",
    "parse_args",
    "read_required",
    "render_text",
    "required_review_axes",
    "run_jj",
    "run_jj_bytes",
    "string_array",
    "unwrap_profile_value",
    "valid_date_version",
    "validate_acceptance_report",
    "validate_batch_source_dependencies",
    "validate_batches",
    "validate_brief",
    "validate_brief_source_expectations",
    "validate_capability_snapshot",
    "validate_format_qa_entry",
    "validate_format_registry",
    "validate_generation_record",
    "validate_hashed_path",
    "validate_jj",
    "validate_lifecycle_state",
    "validate_profile",
    "validate_publication_policy",
    "validate_qa_check",
    "validate_ready_deliverable_qa",
    "validate_receipts",
    "validate_review_matrix",
    "validate_review_report",
    "validate_review_scope",
    "validate_routing",
    "validate_snapshot_files",
    "validate_source_register",
    "validate_timestamp",
    "validate_version_control",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check-jj", action="store_true")
    parser.add_argument(
        "--check-vcs",
        action="store_true",
        help="Check the declared Project version backend",
    )
    parser.add_argument("--now", help="RFC 3339 UTC timestamp for reproducible validation")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser.parse_args(argv)


def render_text(result: dict[str, Any]) -> str:
    lines = [f"status: {result['status']}", f"root: {result['root']}"]
    for label in ("errors", "warnings", "checks"):
        lines.append(f"{label}:")
        for item in result[label]:
            lines.append(f"  - {item['code']}: {item['message']}")
    return "\n".join(lines)


def validate_project_state(
    root: Path,
    *,
    check_vcs: bool = False,
    now_value: str | None = None,
) -> Report:
    resolved_root = root.resolve()
    report = Report(resolved_root)
    if not resolved_root.is_dir():
        report.error("ROOT_MISSING", f"project root does not exist: {resolved_root}")
        return report

    state_dir = resolved_root / ".manuscript-ops"
    if not state_dir.is_dir():
        report.error("STATE_DIR_MISSING", "missing .manuscript-ops directory")
        return report

    profile_raw = read_required(state_dir / "project-profile.json", report)
    snapshot = read_required(state_dir / "routing-snapshot.json", report)
    batches = read_required(state_dir / "batch-manifest.json", report)
    registry = read_required(state_dir / "format-registry.json", report)
    state = read_required(state_dir / "state.json", report)

    try:
        now = parse_timestamp(now_value) if now_value else datetime.now(timezone.utc)
    except (ContractError, ValueError) as exc:
        report.error("NOW_INVALID", str(exc))
        now = datetime.now(timezone.utc)

    profile = validate_profile(profile_raw, report) if profile_raw else {}
    if snapshot and profile:
        validate_routing(snapshot, profile, report, now)
    batch_index = validate_batches(batches, profile, report) if batches and profile else {}
    adapters = validate_format_registry(registry, profile, report) if registry else {}
    brief_result = (
        validate_brief(profile, adapters, report) if profile and adapters else None
    )
    lifecycle = (
        validate_lifecycle_state(state, batch_index, profile, report)
        if state and profile
        else {"required_gates": set()}
    )

    source_result: dict[str, Any] | None = None
    if lifecycle.get("source_register") and registry:
        source_result = validate_source_register(
            lifecycle["source_register"],
            registry,
            report,
        )
    validate_brief_source_expectations(brief_result, source_result, report)
    validate_batch_source_dependencies(batch_index, source_result, report)

    matrix_result: dict[str, Any] | None = None
    if lifecycle.get("review_matrix"):
        matrix_result = validate_review_matrix(lifecycle["review_matrix"], report)
    review_result: dict[str, Any] | None = None
    if lifecycle.get("latest_review_report"):
        review_result = validate_acceptance_report(
            lifecycle["latest_review_report"],
            report,
        )
    if matrix_result and review_result:
        if matrix_result["milestone"] != review_result["milestone"]:
            report.error(
                "REVIEW_BINDING",
                "ReviewMatrix and acceptance report milestones differ",
            )
        if matrix_result["snapshot"] != review_result["snapshot"]:
            report.error(
                "REVIEW_BINDING",
                "ReviewMatrix and acceptance report frozen snapshots differ",
            )
        if matrix_result.get("snapshot_captured_at") != review_result.get(
            "snapshot_captured_at"
        ):
            report.error(
                "REVIEW_BINDING",
                "ReviewMatrix and acceptance report snapshot capture times differ",
            )
        if matrix_result["applicable_axes"] != review_result["manuscript_axes"]:
            report.error(
                "REVIEW_BINDING",
                "acceptance manuscript evidence does not exactly cover the profile axes",
            )
        validate_review_scope(
            lifecycle,
            batch_index,
            profile,
            source_result,
            matrix_result,
            review_result,
            report,
        )

    capability_result: dict[str, Any] | None = None
    if lifecycle.get("capability_snapshot"):
        capability_result = validate_capability_snapshot(
            lifecycle["capability_snapshot"],
            profile,
            adapters,
            report,
            now,
        )
        profile_capability = profile.get("capabilities_snapshot")
        if isinstance(profile_capability, str) and (
            not capability_result or profile_capability != capability_result["path"]
        ):
            report.error(
                "PROFILE_CAPABILITIES",
                "ProjectProfile and LifecycleState capability snapshots differ",
            )

    lifecycle_qa: dict[str, dict[str, Any]] = {}
    for item in lifecycle.get("format_qa_records", []):
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
                    "STATE_FORMAT_QA",
                    "format QA record has no validated deliverable artifact",
                )
            elif artifact_id in lifecycle_qa:
                report.error(
                    "STATE_FORMAT_QA",
                    f"duplicate QA record for deliverable {artifact_id}",
                )
            else:
                lifecycle_qa[artifact_id] = normalized_qa

    if lifecycle.get("phase") in FINAL_PHASES:
        selected_formats = set(profile.get("formats", []))
        if not isinstance(profile.get("capabilities_snapshot"), str):
            report.error(
                "PROFILE_CAPABILITIES",
                "final ProjectProfile must bind the capability snapshot path",
            )
        validate_ready_deliverable_qa(
            brief_result,
            lifecycle_qa,
            "STATE_FORMAT_QA",
            "final lifecycle",
            report,
        )
        if capability_result:
            not_ready = sorted(
                adapter_id
                for adapter_id in selected_formats
                if capability_result["statuses"].get(adapter_id) != "READY"
            )
            if not_ready:
                report.error(
                    "STATE_CAPABILITIES",
                    f"selected final formats are not capability READY: {not_ready}",
                )

    receipts = validate_receipts(
        state_dir,
        lifecycle,
        profile,
        adapters,
        review_result,
        lifecycle_qa,
        capability_result,
        brief_result,
        source_result,
        report,
    )
    if check_vcs and profile:
        validate_version_control(profile, receipts, report)
    return report


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = validate_project_state(
        args.root,
        check_vcs=bool(args.check_jj or args.check_vcs),
        now_value=args.now,
    )
    result = report.as_dict()
    print(render_text(result) if args.format == "text" else dump_json(result))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
