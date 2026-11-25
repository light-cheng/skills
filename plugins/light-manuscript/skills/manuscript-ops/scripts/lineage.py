#!/usr/bin/env python3
"""Source intake identity, derivative lineage, and batch dependency validation."""

from __future__ import annotations

import csv
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from gates import validate_acceptance_report
from manuscript_ops_core import (
    REVIEW_AXIS_IDS,
    ContractError,
    ensure_within_root,
    load_json,
    sha256_file,
)
from schema import (
    BATCH_REVIEW_MILESTONES,
    FORCE_CUMULATIVE_BATCH_KINDS,
    SHA256_RE,
    SOURCE_USES,
    Report,
    string_array,
    valid_date_version,
    validate_hashed_path,
    validate_timestamp,
)


def check_document_source_identity(
    source_id: str,
    adapter_id: str,
    path: Path,
    report: Report,
) -> None:
    """Check intake identity only; source reading and content acceptance are separate."""
    try:
        path = ensure_within_root(report.root, path)
        if not path.is_file():
            return
        with path.open("rb") as handle:
            prefix = handle.read(1024)
        ole = bytes.fromhex("d0cf11e0a1b11ae1")
        valid = True
        containers = {
            "docx": "word/document.xml",
            "pptx": "ppt/presentation.xml",
            "xlsx": "xl/workbook.xml",
        }
        if adapter_id == "legacy-doc":
            valid = prefix.startswith(ole)
        elif adapter_id == "pdf":
            valid = prefix.startswith(b"%PDF-")
        elif adapter_id in containers:
            with zipfile.ZipFile(path) as archive:
                valid = containers[adapter_id] in archive.namelist()
        elif adapter_id in {"txt", "markdown"}:
            valid = not prefix.startswith((ole, b"PK\x03\x04", b"%PDF-"))
        elif adapter_id == "rtf":
            valid = prefix.lstrip().startswith(b"{\\rtf")
        if not valid:
            report.error(
                "SOURCE_FORMAT",
                f"{source_id} bytes do not match declared {adapter_id} intake identity",
            )
    except (ContractError, OSError, zipfile.BadZipFile) as exc:
        report.error("SOURCE_FORMAT", f"{source_id}: {exc}")


def validate_source_register(
    path_value: Any,
    registry: dict[str, Any],
    report: Report,
) -> dict[str, Any] | None:
    if not isinstance(path_value, str):
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("SOURCE_REGISTER_PATH", str(exc))
        return None
    if not path.is_file():
        report.error("SOURCE_REGISTER_MISSING", f"missing source register: {path_value}")
        return None
    required_columns = {
        "source_id",
        "class",
        "adapter_id",
        "path_or_url",
        "publisher_or_owner",
        "retrieved_at",
        "sha256",
        "privacy_class",
        "permitted_use",
        "exclusions",
        "metadata_json",
        "derived_artifacts_json",
    }
    adapters = {
        item["id"]: {
            **item,
            "required_metadata": ["path", "sha256"],
            "derivatives": [
                "converted_document",
                "extracted_text",
                "page_text_extract",
                "processed_image",
            ],
        }
        for item in registry.get("adapters", [])
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("extensions")
    }
    adapters.update(
        {
            item["id"]: item
            for item in registry.get("source_adapters", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
    )
    adapters["legacy-doc"] = {
        "extensions": [".doc"],
        "required_metadata": ["path", "sha256"],
        "derivatives": ["converted_document", "extracted_text", "processed_image"],
    }
    adapters["json-text-extract"] = {
        "extensions": [".json"],
        "required_metadata": ["path", "sha256"],
        "derivatives": [],
    }
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if set(reader.fieldnames or []) != required_columns:
            report.error(
                "SOURCE_REGISTER_COLUMNS",
                "source register columns do not match the contract",
            )
            return None
        rows = list(reader)
        seen: set[str] = set()
        row_adapters: dict[str, str] = {}
        for line_number, row in enumerate(rows, start=2):
            source_id = row["source_id"].strip()
            if not source_id or source_id in seen:
                report.error(
                    "SOURCE_ID",
                    f"invalid or duplicate source_id at line {line_number}",
                )
            seen.add(source_id)
            row_adapters[source_id] = row["adapter_id"]

        def artifact_key(path_val: Any, digest: Any) -> tuple[str, str] | None:
            if not isinstance(path_val, str) or not isinstance(digest, str):
                return None
            try:
                local = ensure_within_root(report.root, Path(path_val))
            except ContractError:
                return None
            return (str(local), digest)

        row_by_id = {row["source_id"].strip(): row for row in rows}
        declared_derivatives: dict[tuple[str, str], list[dict[str, str]]] = {}
        declared_extractions: dict[tuple[str, str], list[dict[str, str]]] = {}
        for parent in rows:
            try:
                artifacts = json.loads(parent["derived_artifacts_json"] or "[]")
            except json.JSONDecodeError:
                continue
            if not isinstance(artifacts, list):
                continue
            parent_id_norm = parent["source_id"].strip()
            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    continue
                raw_parent_ids = artifact.get("parent_source_ids")
                if not isinstance(raw_parent_ids, list):
                    continue
                norm_parent_ids = [
                    pid.strip() for pid in raw_parent_ids if isinstance(pid, str)
                ]
                if parent_id_norm not in norm_parent_ids:
                    continue
                key = artifact_key(artifact.get("path"), artifact.get("sha256"))
                if key is None:
                    continue
                parents = [
                    row_by_id[pid] for pid in norm_parent_ids if pid in row_by_id
                ]
                declared_derivatives.setdefault(key, []).extend(parents)
                if artifact.get("kind") in ("page_text_extract", "extracted_text"):
                    declared_extractions.setdefault(key, []).extend(parents)

        for row in rows:
            source_id = row["source_id"].strip()
            if row["class"] not in {
                "authoritative",
                "reference-only",
                "incoming-draft",
            }:
                report.error("SOURCE_CLASS", f"{source_id} has invalid authority class")
            adapter_id = row["adapter_id"]
            adapter = adapters.get(adapter_id)
            if adapter is None:
                report.error(
                    "SOURCE_ADAPTER",
                    f"{source_id} has unknown adapter {adapter_id!r}",
                )
                continue
            if adapter_id == "json-text-extract":
                key = artifact_key(row["path_or_url"], row["sha256"])
                parents = [
                    parent
                    for parent in (declared_extractions.get(key, []) if key else [])
                    if parent["source_id"].strip() != source_id
                    and parent["adapter_id"] != adapter_id
                ]
                if not parents:
                    report.error(
                        "SOURCE_LINEAGE",
                        f"{source_id} JSON extraction requires a declared, hash-bound source parent",
                    )
                try:
                    extracted = load_json(
                        ensure_within_root(report.root, Path(row["path_or_url"]))
                    )
                    if not isinstance(extracted, (dict, list)):
                        report.error(
                            "SOURCE_FORMAT",
                            f"{source_id} extraction must contain a JSON object or array",
                        )
                except ContractError as exc:
                    report.error("SOURCE_FORMAT", str(exc))
            if adapter.get("extensions"):
                local_source = row["path_or_url"]
                if re.match(r"^[a-z]+://", local_source, re.I):
                    report.error(
                        "SOURCE_FORMAT",
                        f"{source_id} document requires a hash-bound local snapshot",
                    )
                elif Path(local_source).suffix.lower() not in adapter["extensions"]:
                    report.error(
                        "SOURCE_FORMAT",
                        f"{source_id} file suffix does not match {adapter_id}",
                    )
                else:
                    check_document_source_identity(
                        source_id,
                        adapter_id,
                        Path(local_source),
                        report,
                    )
            for field in (
                "path_or_url",
                "publisher_or_owner",
                "retrieved_at",
                "sha256",
                "privacy_class",
                "permitted_use",
                "exclusions",
            ):
                if not row[field].strip():
                    report.error("SOURCE_POLICY", f"{source_id} requires {field}")
            permitted_tokens = {
                token.strip().lower()
                for token in row["permitted_use"].split(",")
                if token.strip()
            }
            excluded_tokens = {
                token.strip().lower()
                for token in row["exclusions"].split(",")
                if token.strip()
            }
            key = artifact_key(row["path_or_url"], row["sha256"])
            parents = declared_derivatives.get(key, []) if key else []
            authority_rank = {
                "incoming-draft": 0,
                "reference-only": 1,
                "authoritative": 2,
            }
            for parent in parents:
                parent_id_norm = parent["source_id"].strip()
                if parent_id_norm == source_id:
                    continue
                if authority_rank.get(row["class"], -1) > authority_rank.get(
                    parent["class"], -1
                ):
                    report.error(
                        "SOURCE_CLASS",
                        f"{source_id} derivative cannot promote parent {parent_id_norm}'s authority",
                    )
                parent_uses = {
                    token.strip().lower()
                    for token in parent["permitted_use"].split(",")
                    if token.strip()
                }
                parent_exclusions = {
                    token.strip().lower()
                    for token in parent["exclusions"].split(",")
                    if token.strip() and token.strip().lower() != "none"
                }
                if not permitted_tokens.issubset(
                    parent_uses
                ) or not parent_exclusions.issubset(excluded_tokens):
                    report.error(
                        "SOURCE_POLICY",
                        f"{source_id} derivative must retain parent {parent_id_norm}'s permitted uses and exclusions",
                    )
            if (
                not permitted_tokens
                or "none" in permitted_tokens
                or not permitted_tokens.issubset(SOURCE_USES)
            ):
                report.error(
                    "SOURCE_POLICY",
                    f"{source_id} permitted_use must be a comma-separated subset of {sorted(SOURCE_USES)}",
                )
            if not excluded_tokens or (
                excluded_tokens != {"none"}
                and not excluded_tokens.issubset(SOURCE_USES)
            ):
                report.error(
                    "SOURCE_POLICY",
                    f"{source_id} exclusions must be none or a comma-separated subset of {sorted(SOURCE_USES)}",
                )
            normalized_exclusions = (
                set() if excluded_tokens == {"none"} else excluded_tokens
            )
            overlap = sorted(permitted_tokens & normalized_exclusions)
            if overlap:
                report.error(
                    "SOURCE_POLICY",
                    f"{source_id} both permits and excludes uses: {overlap}",
                )
            validate_timestamp(row["retrieved_at"], "SOURCE_RETRIEVED_AT", report)
            if not SHA256_RE.fullmatch(row["sha256"]):
                report.error(
                    "SOURCE_HASH",
                    f"{source_id} requires a SHA-256 content hash",
                )
            try:
                metadata = json.loads(row["metadata_json"] or "{}")
                derivatives = json.loads(row["derived_artifacts_json"] or "[]")
            except json.JSONDecodeError as exc:
                report.error("SOURCE_METADATA_JSON", f"{source_id}: {exc}")
                continue
            if not isinstance(metadata, dict) or not isinstance(derivatives, list):
                report.error(
                    "SOURCE_METADATA_JSON",
                    f"{source_id} metadata/derivatives have wrong shapes",
                )
                continue
            common = {
                "url": row["path_or_url"],
                "path": row["path_or_url"],
                "publisher": row["publisher_or_owner"],
                "retrieved_at": row["retrieved_at"],
                "sha256": row["sha256"],
                "privacy_class": row["privacy_class"],
                "capture_or_hash": metadata.get("capture_or_hash") or row["sha256"],
                "export_hash": metadata.get("export_hash") or row["sha256"],
            }
            combined = {**common, **metadata}
            missing = [
                name
                for name in adapter.get("required_metadata", [])
                if combined.get(name) in (None, "", [])
            ]
            if missing:
                report.error(
                    "SOURCE_METADATA",
                    f"{source_id} missing adapter metadata: {missing}",
                )
            if adapter_id == "transcript":
                parent_source_id = metadata.get("parent_source_id")
                norm_parent = (
                    parent_source_id.strip()
                    if isinstance(parent_source_id, str)
                    else ""
                )
                if (
                    not norm_parent
                    or norm_parent == source_id
                    or row_adapters.get(norm_parent) not in {"audio", "video"}
                ):
                    report.error(
                        "SOURCE_LINEAGE",
                        f"{source_id} transcript must reference a registered audio/video parent_source_id",
                    )
            allowed_derivatives = set(adapter.get("derivatives", []))
            for derivative in derivatives:
                if not isinstance(derivative, dict):
                    report.error(
                        "SOURCE_DERIVATIVE",
                        f"{source_id} derivative entries must be objects",
                    )
                    continue
                kind = derivative.get("kind")
                if kind not in allowed_derivatives:
                    report.error(
                        "SOURCE_DERIVATIVE",
                        f"{source_id} has unsupported derivative kind {kind!r}",
                    )
                parent_ids = derivative.get("parent_source_ids")
                norm_pids = (
                    [pid.strip() for pid in parent_ids if isinstance(pid, str)]
                    if isinstance(parent_ids, list)
                    else []
                )
                if not string_array(parent_ids, nonempty=True) or source_id not in norm_pids:
                    report.error(
                        "SOURCE_LINEAGE",
                        f"{source_id} derivative must link its registered parent",
                    )
                validate_hashed_path(
                    derivative.get("path"),
                    derivative.get("sha256"),
                    "SOURCE_DERIVATIVE",
                    report,
                )
                validate_timestamp(
                    derivative.get("created_at"),
                    "SOURCE_DERIVATIVE_TIME",
                    report,
                )
                if kind in {"ocr_text", "transcript", "cleaned_transcript"}:
                    for field in ("engine_or_author", "language"):
                        if (
                            not isinstance(derivative.get(field), str)
                            or not derivative[field].strip()
                        ):
                            report.error(
                                "SOURCE_DERIVATIVE",
                                f"{source_id} {kind} requires {field}",
                            )
            local_value = row["path_or_url"]
            expected_hash = row["sha256"]
            if (
                local_value
                and expected_hash
                and not re.match(r"^[a-z]+://", local_value, re.I)
            ):
                validate_hashed_path(local_value, expected_hash, "SOURCE_FILE", report)
        report.ok("SOURCE_REGISTER", f"{len(seen)} source record(s)")
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "sources": {
            row["source_id"].strip(): {
                "class": row["class"],
                "adapter_id": row["adapter_id"],
                "privacy_class": row["privacy_class"],
                "permitted_use": {
                    token.strip().lower()
                    for token in row["permitted_use"].split(",")
                    if token.strip().lower() in SOURCE_USES
                },
                "exclusions": (
                    set()
                    if row["exclusions"].strip().lower() == "none"
                    else {
                        token.strip().lower()
                        for token in row["exclusions"].split(",")
                        if token.strip().lower() in SOURCE_USES
                    }
                ),
            }
            for row in rows
            if row["source_id"].strip()
        },
    }


def validate_brief_source_expectations(
    brief_result: dict[str, Any] | None,
    source_result: dict[str, Any] | None,
    report: Report,
) -> None:
    if not brief_result or not source_result:
        return
    sources = source_result.get("sources", {})
    observed_classes = {
        source.get("class")
        for source in sources.values()
        if isinstance(source, dict)
    }
    none_values = {"none", "n/a", "not applicable", "not_applicable"}
    for source_class, statement in brief_result.get(
        "source_expectations",
        {},
    ).items():
        if (
            isinstance(statement, str)
            and statement.strip().lower() not in none_values
            and source_class not in observed_classes
        ):
            report.error(
                "BRIEF_SOURCE_BINDING",
                f"Brief declares {source_class} material but the Source Register has none",
            )


def validate_batches(
    manifest: dict[str, Any],
    profile: dict[str, Any],
    report: Report,
) -> dict[str, dict[str, Any]]:
    if manifest.get("schema_version") != "1":
        report.error("BATCH_SCHEMA", "BatchManifest schema_version must be 1")
    if not valid_date_version(manifest.get("date_version")):
        report.error("BATCH_VERSION", "BatchManifest date_version is invalid")
    if manifest.get("date_version") != profile.get("date_version"):
        report.error(
            "BATCH_VERSION",
            "BatchManifest and ProjectProfile date versions differ",
        )
    batches = manifest.get("batches")
    if not isinstance(batches, list) or not batches:
        report.error("BATCHES_MISSING", "BatchManifest requires at least one batch")
        return {}
    ids = [item.get("id") for item in batches if isinstance(item, dict)]
    if len(ids) != len(batches) or any(
        not isinstance(item, str) or not item for item in ids
    ):
        report.error("BATCH_ID", "every batch requires a non-empty string id")
        return {}
    if len(ids) != len(set(ids)):
        report.error("BATCH_DUPLICATE", "batch ids must be unique")
        return {
            item["id"]: item
            for item in batches
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    known = set(ids)
    by_id = {item["id"]: item for item in batches}
    normalized_outputs_by_id: dict[str, dict[str, str | None]] = {}
    graph: dict[str, list[str]] = {}
    live_batches: list[str] = []
    for item in batches:
        batch_id = item["id"]
        required = {
            "label",
            "kind",
            "scope",
            "source_dependencies",
            "depends_on",
            "risk",
            "review_axes",
            "reviewable_volume",
            "review_cadence",
            "cumulative_regression",
            "regression_surface",
            "input_snapshot",
            "outputs",
            "status",
            "user_gate",
            "review_report",
            "user_confirmation",
        }
        missing_fields = sorted(required - set(item))
        if missing_fields:
            report.error("BATCH_FIELDS", f"{batch_id} missing fields: {missing_fields}")
        if not isinstance(item.get("label"), str) or not item["label"]:
            report.error("BATCH_LABEL", f"{batch_id} requires a label")
        if item.get("kind") not in {
            "outline",
            "content",
            "candidate",
            "source-lock",
            "derivative",
            "final",
        }:
            report.error("BATCH_KIND", f"{batch_id} has invalid kind")
        if not string_array(item.get("scope"), nonempty=True):
            report.error("BATCH_SCOPE", f"{batch_id} requires semantic scope")
        source_dependencies = item.get("source_dependencies")
        if not isinstance(source_dependencies, list):
            report.error(
                "BATCH_SOURCES",
                f"{batch_id} source_dependencies must be an array",
            )
        else:
            source_ids: set[str] = set()
            for dependency in source_dependencies:
                if not isinstance(dependency, dict):
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency entries must be objects",
                    )
                    continue
                source_id = dependency.get("source_id")
                if (
                    not isinstance(source_id, str)
                    or not source_id.strip()
                    or source_id in source_ids
                ):
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency IDs must be non-empty and unique",
                    )
                else:
                    source_ids.add(source_id)
                if dependency.get("use") not in {
                    "factual",
                    "context",
                    "style",
                    "incoming",
                }:
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency {source_id!r} has invalid use",
                    )
                if (
                    not isinstance(dependency.get("purpose"), str)
                    or not dependency["purpose"].strip()
                ):
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency {source_id!r} requires a purpose",
                    )
        deps = item.get("depends_on")
        if not string_array(deps):
            report.error(
                "BATCH_DEPENDENCY",
                f"{batch_id} depends_on must be a string array",
            )
            deps = []
        missing = sorted(set(deps) - known)
        if missing:
            report.error(
                "BATCH_DEPENDENCY",
                f"{batch_id} references missing batches: {missing}",
            )
        graph[batch_id] = deps
        if item.get("risk") not in {"low", "medium", "high", "critical"}:
            report.error("BATCH_RISK", f"{batch_id} has invalid risk")
        if not string_array(item.get("review_axes"), nonempty=True):
            report.error("BATCH_AXES", f"{batch_id} requires review axes")
        else:
            unknown_axes = sorted(set(item["review_axes"]) - REVIEW_AXIS_IDS)
            if unknown_axes:
                report.error(
                    "BATCH_AXES",
                    f"{batch_id} references unknown review axes: {unknown_axes}",
                )
        volume = item.get("reviewable_volume")
        if not isinstance(volume, dict):
            report.error(
                "BATCH_VOLUME",
                f"{batch_id} reviewable_volume must be an object",
            )
        else:
            if not isinstance(volume.get("unit"), str) or not volume["unit"]:
                report.error("BATCH_VOLUME", f"{batch_id} volume requires a unit")
            target = volume.get("target")
            if (
                not isinstance(target, (int, float))
                or isinstance(target, bool)
                or target <= 0
            ):
                report.error(
                    "BATCH_VOLUME",
                    f"{batch_id} volume target must be positive",
                )
            if not isinstance(volume.get("rationale"), str) or not volume["rationale"]:
                report.error(
                    "BATCH_VOLUME",
                    f"{batch_id} volume requires a rationale",
                )
        cadence = item.get("review_cadence")
        if cadence not in {"incremental", "cumulative"}:
            report.error("BATCH_CADENCE", f"{batch_id} has invalid review cadence")
        cumulative = item.get("cumulative_regression")
        if not isinstance(cumulative, bool) or cumulative is not (
            cadence == "cumulative"
        ):
            report.error(
                "BATCH_REGRESSION",
                f"{batch_id} cadence and cumulative flag disagree",
            )
        if item.get("kind") in FORCE_CUMULATIVE_BATCH_KINDS and cadence != "cumulative":
            report.error(
                "BATCH_REGRESSION",
                f"{batch_id} kind {item.get('kind')} requires cumulative review",
            )
        surface = item.get("regression_surface")
        if not string_array(surface):
            report.error(
                "BATCH_REGRESSION",
                f"{batch_id} regression_surface must be an array",
            )
        if cadence == "cumulative" and not surface:
            report.error(
                "BATCH_REGRESSION",
                f"{batch_id} cumulative review needs a regression surface",
            )
        status = item.get("status")
        if status not in {"planned", "active", "review", "accepted", "blocked"}:
            report.error("BATCH_STATUS", f"{batch_id} has invalid status")
        elif status in {"active", "review"}:
            live_batches.append(batch_id)

        outputs = item.get("outputs")
        normalized_outputs: dict[str, str | None] = {}
        if not isinstance(outputs, list) or not outputs:
            report.error("BATCH_OUTPUTS", f"{batch_id} requires intended outputs")
        else:
            for output in outputs:
                if not isinstance(output, dict):
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output entries must be path/hash objects",
                    )
                    continue
                output_value = output.get("path")
                output_hash = output.get("sha256")
                if not isinstance(output_value, str) or not output_value.strip():
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output requires a non-empty path",
                    )
                    continue
                try:
                    resolved_output = ensure_within_root(
                        report.root,
                        Path(output_value),
                    )
                    normalized_output = resolved_output.relative_to(
                        report.root
                    ).as_posix()
                except (ContractError, ValueError) as exc:
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output path is unsafe: {exc}",
                    )
                    continue
                if Path(output_value).is_absolute() or normalized_output in {"", "."}:
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output path must be project-relative",
                    )
                    continue
                if normalized_output in normalized_outputs:
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} repeats output {normalized_output}",
                    )
                    continue
                if status in {"review", "accepted"}:
                    validated_output = validate_hashed_path(
                        output_value,
                        output_hash,
                        "BATCH_OUTPUT",
                        report,
                    )
                    if validated_output:
                        normalized_outputs[normalized_output] = str(output_hash).lower()
                elif output_hash is None:
                    normalized_outputs[normalized_output] = None
                else:
                    validated_output = validate_hashed_path(
                        output_value,
                        output_hash,
                        "BATCH_OUTPUT",
                        report,
                    )
                    if validated_output:
                        normalized_outputs[normalized_output] = str(output_hash).lower()
        normalized_outputs_by_id[batch_id] = normalized_outputs

        input_snapshot = item.get("input_snapshot")
        input_snapshot_time: datetime | None = None
        if input_snapshot is None:
            if status in {"active", "review", "accepted", "blocked"}:
                report.error(
                    "BATCH_SNAPSHOT",
                    f"{batch_id} status {status} requires a frozen input snapshot",
                )
        elif not isinstance(input_snapshot, dict):
            report.error(
                "BATCH_SNAPSHOT",
                f"{batch_id} input_snapshot must be null or a hashed snapshot object",
            )
        else:
            validate_hashed_path(
                input_snapshot.get("path"),
                input_snapshot.get("sha256"),
                "BATCH_SNAPSHOT",
                report,
            )
            input_snapshot_time = validate_timestamp(
                input_snapshot.get("captured_at"),
                "BATCH_SNAPSHOT_TIME",
                report,
            )
        user_gate = item.get("user_gate")
        if user_gate not in {"required", "not_required"}:
            report.error("BATCH_USER_GATE", f"{batch_id} has invalid user_gate")

        review_reference = item.get("review_report")
        batch_review: dict[str, Any] | None = None
        if review_reference is not None:
            if not isinstance(review_reference, dict):
                report.error(
                    "BATCH_REVIEW",
                    f"{batch_id} review_report must be null or a hash-bound object",
                )
            else:
                review_path = validate_hashed_path(
                    review_reference.get("path"),
                    review_reference.get("sha256"),
                    "BATCH_REVIEW",
                    report,
                )
                if review_path:
                    batch_review = validate_acceptance_report(
                        review_path.relative_to(report.root).as_posix(),
                        report,
                    )
                    if (
                        batch_review
                        and batch_review.get("sha256")
                        != str(review_reference.get("sha256", "")).lower()
                    ):
                        report.error(
                            "BATCH_REVIEW",
                            f"{batch_id} acceptance result hash differs from parsed result",
                        )
        if status == "accepted":
            if not batch_review:
                report.error(
                    "BATCH_REVIEW",
                    f"{batch_id} accepted status requires a hash-bound acceptance result",
                )
            else:
                expected_milestone = BATCH_REVIEW_MILESTONES.get(item.get("kind"))
                if batch_review.get("milestone") != expected_milestone:
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} accepted review must use milestone {expected_milestone}",
                    )
                if batch_review.get("verdict") != "PASS":
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} accepted review must return PASS",
                    )
                missing_axes = sorted(
                    set(item.get("review_axes", []))
                    - set(batch_review.get("manuscript_axes", set()))
                )
                if missing_axes:
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} review omits required axes: {missing_axes}",
                    )
                for output_path, output_hash in normalized_outputs.items():
                    if (
                        output_hash is None
                        or batch_review.get("snapshot", {}).get(output_path)
                        != output_hash
                    ):
                        report.error(
                            "BATCH_REVIEW",
                            f"{batch_id} review snapshot does not bind output {output_path}",
                        )
                if (
                    input_snapshot_time
                    and batch_review.get("snapshot_captured_time")
                    and batch_review["snapshot_captured_time"] < input_snapshot_time
                ):
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} review snapshot predates its frozen input snapshot",
                    )

        confirmation = item.get("user_confirmation")
        if status == "accepted" and user_gate == "required":
            if not isinstance(confirmation, dict):
                report.error(
                    "BATCH_USER_GATE",
                    f"{batch_id} accepted status requires user confirmation",
                )
            else:
                for field in ("actor", "exact_statement"):
                    if (
                        not isinstance(confirmation.get(field), str)
                        or not confirmation[field].strip()
                    ):
                        report.error(
                            "BATCH_USER_GATE",
                            f"{batch_id} confirmation requires {field}",
                        )
                confirmation_time = validate_timestamp(
                    confirmation.get("confirmed_at"),
                    "BATCH_USER_GATE_TIME",
                    report,
                )
                if (
                    confirmation_time
                    and batch_review
                    and isinstance(batch_review.get("completed_at"), datetime)
                    and confirmation_time < batch_review["completed_at"]
                ):
                    report.error(
                        "BATCH_USER_GATE_TIME",
                        f"{batch_id} was confirmed before specialist review completed",
                    )
        elif confirmation is not None:
            report.error(
                "BATCH_USER_GATE",
                f"{batch_id} may record user_confirmation only when an accepted batch requires it",
            )

    if len(live_batches) > 1:
        report.error(
            "BATCH_ACTIVE",
            f"BatchManifest has multiple active/review batches: {sorted(live_batches)}",
        )

    for batch_id, item in by_id.items():
        if item.get("status") not in {"active", "review", "accepted"}:
            continue
        unaccepted = sorted(
            dependency
            for dependency in graph.get(batch_id, [])
            if dependency in by_id and by_id[dependency].get("status") != "accepted"
        )
        if unaccepted:
            report.error(
                "BATCH_DEPENDENCY_STATUS",
                f"{batch_id} cannot advance before prerequisites are accepted: {unaccepted}",
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(dep) for dep in graph.get(node, []) if dep in graph):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(visit(node) for node in graph):
        report.error("BATCH_CYCLE", "batch dependency graph contains a cycle")
    else:
        report.ok("BATCH_GRAPH", f"{len(ids)} batches with an acyclic dependency graph")
    return {
        batch_id: {
            **item,
            "_validated_outputs": normalized_outputs_by_id.get(batch_id, {}),
        }
        for batch_id, item in by_id.items()
    }


def validate_batch_source_dependencies(
    batches: dict[str, dict[str, Any]],
    source_result: dict[str, Any] | None,
    report: Report,
) -> None:
    if not source_result:
        return
    sources = source_result.get("sources", {})
    for batch_id, batch in batches.items():
        dependencies = batch.get("source_dependencies")
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                continue
            source_id = dependency.get("source_id")
            norm_id = source_id.strip() if isinstance(source_id, str) else source_id
            source = sources.get(norm_id)
            if source is None:
                report.error(
                    "BATCH_SOURCE_BINDING",
                    f"{batch_id} references unregistered source {source_id!r}",
                )
                continue
            source_class = source.get("class")
            use = dependency.get("use")
            if use not in source.get("permitted_use", set()):
                report.error(
                    "BATCH_SOURCE_POLICY",
                    f"{batch_id} use {use!r} is not permitted for source {source_id!r}",
                )
            if use in source.get("exclusions", set()):
                report.error(
                    "BATCH_SOURCE_POLICY",
                    f"{batch_id} use {use!r} is explicitly excluded for source {source_id!r}",
                )
            if use == "factual" and source_class != "authoritative":
                report.error(
                    "BATCH_SOURCE_AUTHORITY",
                    f"{batch_id} cannot use {source_id!r} ({source_class}) as factual authority",
                )
            elif use in {"context", "style"} and source_class == "incoming-draft":
                report.error(
                    "BATCH_SOURCE_AUTHORITY",
                    f"{batch_id} must label incoming draft {source_id!r} with use=incoming",
                )
            elif use == "incoming" and source_class != "incoming-draft":
                report.error(
                    "BATCH_SOURCE_AUTHORITY",
                    f"{batch_id} use=incoming requires an incoming-draft source: {source_id!r}",
                )
