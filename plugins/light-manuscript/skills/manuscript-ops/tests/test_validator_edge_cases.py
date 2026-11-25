"""Edge-case behavioral tests across schema, lineage, qa, gates, and CLI entrypoints."""

from __future__ import annotations

import csv
import hashlib
import json
import runpy
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import gates  # noqa: E402
import lineage  # noqa: E402
import qa  # noqa: E402
import schema  # noqa: E402

REGISTRY_PATH = PACKAGE_ROOT / "assets" / "format-registry.json"
REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
TSV_COLUMNS = (
    (PACKAGE_ROOT / "assets" / "templates" / "source-register.tsv")
    .read_text(encoding="utf-8")
    .strip()
    .split("\t")
)


def write_file_hashed(root: Path, rel: str, data: bytes | str) -> dict[str, str]:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = data.encode("utf-8") if isinstance(data, str) else data
    path.write_bytes(raw)
    return {"path": rel, "sha256": hashlib.sha256(raw).hexdigest()}


def test_runpy_validate_state_entrypoint_exposes_compatible_symbols(tmp_path: Path) -> None:
    ns = runpy.run_path(str(SCRIPTS_DIR / "validate_state.py"))
    for symbol in (
        "Report",
        "validate_profile",
        "validate_brief",
        "validate_routing",
        "validate_batches",
        "validate_format_registry",
        "validate_lifecycle_state",
        "validate_source_register",
        "validate_format_qa_entry",
        "validate_capability_snapshot",
        "validate_review_matrix",
        "validate_acceptance_report",
        "validate_review_report",
        "validate_receipts",
        "validate_version_control",
    ):
        assert symbol in ns
    rep = ns["Report"](tmp_path)
    assert rep.status == "READY"
    assert rep.exit_code == 0
    rep.warn("SAMPLE_WARN", "degraded warning")
    assert rep.status == "DEGRADED"
    assert rep.exit_code == 1


def test_validate_state_cli_handles_missing_root_and_missing_state_dir(tmp_path: Path) -> None:
    missing_root = tmp_path / "does-not-exist"
    r1 = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS_DIR / "validate_state.py"), "--root", str(missing_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r1.returncode == 2
    assert json.loads(r1.stdout)["errors"][0]["code"] == "ROOT_MISSING"

    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    r2 = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "validate_state.py"),
            "--root",
            str(empty_root),
            "--format",
            "text",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r2.returncode == 2
    assert "STATE_DIR_MISSING" in r2.stdout


def test_lineage_legacy_doc_transcript_ocr_and_brief_source_expectations(tmp_path: Path) -> None:
    ole_doc = write_file_hashed(
        tmp_path, "sources/orig.doc", bytes.fromhex("d0cf11e0a1b11ae1") + b"word97"
    )
    extracted = write_file_hashed(tmp_path, "sources/converted.txt", "extracted prose\n")
    audio = write_file_hashed(tmp_path, "sources/interview.mp3", b"ID3audio")
    transcript = write_file_hashed(tmp_path, "sources/interview.txt", "verbatim transcript\n")
    scan = write_file_hashed(tmp_path, "sources/scan.png", b"\x89PNG\r\n\x1a\nscan")
    ocr_txt = write_file_hashed(tmp_path, "sources/ocr.txt", "ocr output\n")

    rows = [
        {
            "source_id": "DOC1",
            "class": "authoritative",
            "adapter_id": "legacy-doc",
            "path_or_url": ole_doc["path"],
            "publisher_or_owner": "Archive",
            "retrieved_at": "2026-11-25T00:00:00Z",
            "sha256": ole_doc["sha256"],
            "privacy_class": "internal",
            "permitted_use": "factual,context",
            "exclusions": "none",
            "metadata_json": "{}",
            "derived_artifacts_json": json.dumps(
                [
                    {
                        "kind": "extracted_text",
                        "path": extracted["path"],
                        "sha256": extracted["sha256"],
                        "parent_source_ids": ["DOC1"],
                        "created_at": "2026-11-25T00:10:00Z",
                    }
                ]
            ),
        },
        {
            "source_id": "AUD1",
            "class": "authoritative",
            "adapter_id": "audio",
            "path_or_url": audio["path"],
            "publisher_or_owner": "Speaker",
            "retrieved_at": "2026-11-25T00:00:00Z",
            "sha256": audio["sha256"],
            "privacy_class": "internal",
            "permitted_use": "factual",
            "exclusions": "none",
            "metadata_json": json.dumps({"duration": "12m"}),
            "derived_artifacts_json": "[]",
        },
        {
            "source_id": "TR1",
            "class": "authoritative",
            "adapter_id": "transcript",
            "path_or_url": transcript["path"],
            "publisher_or_owner": "Speaker",
            "retrieved_at": "2026-11-25T00:05:00Z",
            "sha256": transcript["sha256"],
            "privacy_class": "internal",
            "permitted_use": "factual",
            "exclusions": "none",
            "metadata_json": json.dumps(
                {
                    "parent_source_id": "AUD1",
                    "engine_or_author": "whisper-large",
                    "language": "en",
                    "created_at": "2026-11-25T00:05:00Z",
                }
            ),
            "derived_artifacts_json": "[]",
        },
    ]
    tsv = tmp_path / "valid-sources.tsv"
    with tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    rep = schema.Report(tmp_path)
    src_result = lineage.validate_source_register("valid-sources.tsv", REGISTRY, rep)
    assert rep.errors == []
    assert src_result is not None

    # Brief declares reference-only material when none is registered -> BRIEF_SOURCE_BINDING
    lineage.validate_brief_source_expectations(
        {
            "source_expectations": {
                "authoritative": "DOC1",
                "reference-only": "style-guide.md",
                "incoming-draft": "none",
            }
        },
        src_result,
        rep,
    )
    assert "BRIEF_SOURCE_BINDING" in {e["code"] for e in rep.errors}

    # Orphan transcript and OCR derivative missing engine_or_author/language
    bad_rows = [
        {
            **rows[2],
            "metadata_json": json.dumps(
                {
                    "parent_source_id": "DOC1",
                    "engine_or_author": "whisper",
                    "language": "en",
                    "created_at": "2026-11-25T00:05:00Z",
                }
            ),
        },
        {
            "source_id": "IMG1",
            "class": "authoritative",
            "adapter_id": "image-scan",
            "path_or_url": scan["path"],
            "publisher_or_owner": "Scanner",
            "retrieved_at": "2026-11-25T00:00:00Z",
            "sha256": scan["sha256"],
            "privacy_class": "internal",
            "permitted_use": "factual",
            "exclusions": "none",
            "metadata_json": json.dumps({"capture_context": "lab notebook"}),
            "derived_artifacts_json": json.dumps(
                [
                    {
                        "kind": "ocr_text",
                        "path": ocr_txt["path"],
                        "sha256": ocr_txt["sha256"],
                        "parent_source_ids": ["IMG1"],
                        "created_at": "2026-11-25T00:10:00Z",
                    }
                ]
            ),
        },
    ]
    bad_tsv = tmp_path / "bad-sources.tsv"
    with bad_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(bad_rows)
    bad_rep = schema.Report(tmp_path)
    lineage.validate_source_register("bad-sources.tsv", REGISTRY, bad_rep)
    assert {"SOURCE_LINEAGE", "SOURCE_DERIVATIVE"}.issubset(
        {e["code"] for e in bad_rep.errors}
    )


def test_qa_capability_spoofing_and_unauthorized_sampling_rejected(tmp_path: Path) -> None:
    rep = schema.Report(tmp_path)
    adapters = schema.validate_format_registry(REGISTRY, {"formats": ["markdown"]}, rep)

    # Capability snapshot with spoofed process_probe, invalid derived_alias, and tampered status
    bad_cap = {
        "schema_version": "1",
        "captured_at": "2026-11-25T02:00:00Z",
        "registry": str(REGISTRY_PATH.resolve()),
        "declared_capabilities": ["legacy_cap"],
        "platform_snapshot": None,
        "observed": {
            "invented_tool": {
                "available": True,
                "provider": "fake",
                "version": "1.0",
                "evidence": "invented",
                "operations": ["render"],
                "source": "process_probe",
            },
            "rtf_capable_editor": {
                "available": True,
                "provider": "pandoc",
                "version": "3.0",
                "evidence": "unauthorized alias parent",
                "operations": ["read", "edit", "generate"],
                "source": "derived_alias:pandoc",
            },
        },
        "adapters": [
            {
                "id": "markdown",
                "format": "Markdown",
                "tier": 1,
                "status": "READY",
                "missing_required": [],
                "missing_render_or_visual_groups": [],
                "missing_validation_groups": [],
                "claim_limit": None,
            }
        ],
        "claim_warning": "warning present",
    }
    cap_entry = write_file_hashed(
        tmp_path, ".manuscript-ops/cap.json", json.dumps(bad_cap)
    )
    cap_rep = schema.Report(tmp_path)
    qa.validate_capability_snapshot(
        cap_entry["path"],
        {"formats": ["markdown"], "snapshot_max_age_hours": 24},
        adapters,
        cap_rep,
        datetime(2026, 11, 25, 3, 0, tzinfo=timezone.utc),
    )
    cap_codes = {e["code"] for e in cap_rep.errors}
    assert {"CAPABILITY_PROCESS", "CAPABILITY_EVIDENCE", "CAPABILITY_RECOMPUTE"}.issubset(
        cap_codes
    )
    assert "CAPABILITY_DECLARED" in {w["code"] for w in cap_rep.warnings}

    # Format QA: unauthorized sampled visual QA (Brief requires full) + self-referencing semantic/round-trip
    art = write_file_hashed(tmp_path, "deliverables/guide.md", "# Guide\n")
    brief_file = write_file_hashed(tmp_path, "docs/brief.md", "# Brief\n")
    log_file = write_file_hashed(tmp_path, "qa/lint.log", "ok\n")
    view_file = write_file_hashed(tmp_path, "qa/view.png", b"\x89PNG\r\n\x1a\nv")
    insp_file = write_file_hashed(tmp_path, "qa/insp.json", "{}")
    cmp_file = write_file_hashed(tmp_path, "qa/cmp.json", "{}")

    qa_rec = {
        "schema_version": "1",
        "format": "markdown",
        "status": "READY",
        "artifact": art,
        "provider": {"name": "md", "version": "1", "evidence": "ok"},
        "generation": {
            "mode": "reproducible",
            "tool": {"name": "gen", "version": "1", "evidence": "ok"},
            "command": ["gen"],
            "configuration": {
                "path": None,
                "sha256": None,
                "not_applicable_reason": "none",
            },
            "inputs": [brief_file],
            "output": art,
            "manual_disposition": None,
        },
        "checks": {
            "structural": {
                "status": "PASS",
                "evidence": "ok",
                "coverage": {
                    "mode": "full",
                    "unit": "checks",
                    "total": 1,
                    "inspected": 1,
                    "items": ["c1"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "validator_log", **log_file}],
            },
            "render": {
                "status": "PASS",
                "evidence": "ok",
                "coverage": {
                    "mode": "full",
                    "unit": "views",
                    "total": 2,
                    "inspected": 2,
                    "items": ["v1", "v2"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "rendered_output", **view_file}],
            },
            "visual": {
                "status": "PASS",
                "evidence": "sampled without full policy",
                "coverage": {
                    "mode": "sampled",
                    "unit": "views",
                    "total": 2,
                    "inspected": 1,
                    "items": ["v1"],
                    "sampling_authority": {
                        "path": brief_file["path"],
                        "sha256": brief_file["sha256"],
                        "deliverable": art["path"],
                        "policy": "sampled",
                    },
                },
                "evidence_artifacts": [{"kind": "inspection_record", **insp_file}],
            },
            "semantic": {
                "status": "PASS",
                "evidence": "self compare",
                "coverage": {
                    "mode": "full",
                    "unit": "sections",
                    "total": 1,
                    "inspected": 1,
                    "items": ["s1"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "comparison_report", **cmp_file}],
                "invariants": ["headings"],
                "reference_artifact": art,
            },
            "round_trip": {
                "status": "PASS",
                "evidence": "self round trip",
                "coverage": {
                    "mode": "full",
                    "unit": "files",
                    "total": 1,
                    "inspected": 1,
                    "items": ["f1"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "comparison_report", **cmp_file}],
                "output_artifact": art,
                "invariants": ["headings"],
            },
        },
        "completed_at": "2026-11-25T03:00:00Z",
    }
    qa_entry_file = write_file_hashed(tmp_path, "qa/rec.json", json.dumps(qa_rec))
    qa_rep = schema.Report(tmp_path)
    qa.validate_format_qa_entry(
        {
            "format": "markdown",
            "status": "READY",
            "evidence_path": qa_entry_file["path"],
            "sha256": qa_entry_file["sha256"],
            "rendered": True,
            "visually_inspected": True,
        },
        adapters,
        qa_rep,
        brief_result={
            "path": brief_file["path"],
            "sha256": brief_file["sha256"],
            "deliverables": [
                {
                    "path": art["path"],
                    "format": "markdown",
                    "reproducible": "required",
                    "visual_qa": "full",
                }
            ],
        },
    )
    qa_codes = {e["code"] for e in qa_rep.errors}
    assert {
        "FORMAT_QA_COVERAGE",
        "FORMAT_QA_SEMANTIC",
        "FORMAT_QA_ROUND_TRIP",
    }.issubset(qa_codes)


def test_gates_review_scope_enforces_mandatory_axes_and_candidate_outputs(tmp_path: Path) -> None:
    rep = schema.Report(tmp_path)
    gates.validate_review_scope(
        lifecycle={"phase": "candidate", "active_batch": "b-cand"},
        batches={
            "b-cand": {
                "review_axes": ["intent-structure"],
                "_validated_outputs": {"manuscript/candidate.md": "a" * 64},
            }
        },
        profile={"formats": ["pptx"]},
        source_result=None,
        matrix_result={
            "milestone": "batch",
            "applicable_axes": {"intent-structure"},
        },
        review_result={
            "manuscript_axes": set(),
            "snapshot": {},
        },
        report=rep,
    )
    codes = {e["code"] for e in rep.errors}
    assert {"REVIEW_APPLICABILITY", "REVIEW_EVIDENCE", "STATE_REVIEW_BINDING"}.issubset(
        codes
    )
