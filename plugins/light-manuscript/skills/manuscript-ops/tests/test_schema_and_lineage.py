"""Behavioral tests for schema.py and lineage.py modules and validate_state re-exports."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lineage  # noqa: E402
import schema  # noqa: E402
import validate_state  # noqa: E402

REGISTRY = json.loads((PACKAGE_ROOT / "assets" / "format-registry.json").read_text(encoding="utf-8"))
TSV_COLUMNS = (
    (PACKAGE_ROOT / "assets" / "templates" / "source-register.tsv")
    .read_text(encoding="utf-8")
    .strip()
    .split("\t")
)


def wrap(value: object, origin: str = "规则推导", evidence: str = "fixture") -> dict:
    return {"value": value, "origin": origin, "evidence": evidence}


def make_profile(root: Path, *, formats: list[str] | None = None, languages: list[str] | None = None) -> dict:
    for rel in ("docs", "manuscript", "deliverables"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    for doc in ("manuscript-brief.md", "outline.md", "source-map.md", "glossary.md"):
        p = root / "docs" / doc
        if not p.exists():
            p.write_text("# Placeholder\n", encoding="utf-8")
    return {
        "schema_version": "1",
        "date_version": wrap("2026.11.25"),
        "project_root": wrap(".", "资料发现"),
        "route": wrap("Project"),
        "paths": {
            "brief": wrap("docs/manuscript-brief.md"),
            "outline": wrap("docs/outline.md"),
            "source_map": wrap("docs/source-map.md"),
            "glossary": wrap("docs/glossary.md"),
            "manuscript": wrap("manuscript"),
            "deliverables": wrap("deliverables"),
        },
        "languages": wrap(languages or ["en"], "用户决定"),
        "formats": wrap(formats or ["markdown"], "用户决定"),
        "dependencies": wrap([], "资料发现"),
        "capabilities_snapshot": wrap(None, "资料发现"),
        "version_control": {
            "system": wrap("jj"),
            "tested_baseline": wrap("0.43.0"),
            "colocated": wrap(False),
            "remote_allowed": wrap(False),
        },
        "snapshot_max_age_hours": wrap(168),
        "unknowns": wrap([], "资料发现"),
    }


def write_brief(
    root: Path,
    *,
    approval_state: str = "approved",
    deliverable_rows: str = "| Guide | en | markdown | required | full | deliverables/guide.md |",
    authoritative_sources: str = "S1",
) -> Path:
    path = root / "docs" / "manuscript-brief.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# Manuscript Brief

- Schema version: 1
- Date version: 2026.11.25
- Approval state: {approval_state}

## Goal

Publish an operator guide.

## Audience and use

- Primary audience: Backend engineers
- Target-reader prerequisites: HTTP basics and JSON syntax
- Reading environment: Desktop browser and terminal
- Required accessibility or localization: Clear headings and alt text

## Scope

- Included: Setup and troubleshooting
- Excluded: Billing internals

## Source authority

- Authoritative sources: {authoritative_sources}
- Reference-only material: none
- Incoming draft status: none
- Prohibited or unavailable sources: unverified blog posts

## Framework

- Approved outline or outline acceptance rule: docs/outline.md accepted via outline gate
- Required terminology: docs/glossary.md
- Content boundaries: Operator tasks only

## Deliverables

| Deliverable | Language | Format | Reproducible | Visual QA | Stable path |
|---|---|---|---|---|---|
{deliverable_rows}

## Review and gates

- Applicable review axes: all core axes
- Required independent milestones: outline, source-lock, final
- Human gates: brief-approved, baseline, framework-approved, source-locked, final-approved

## Acceptance

- Content: Concept grounding and complete steps
- Sources: All claims cite authoritative sources
- Format: Markdown structural checks
- Privacy and safety: No internal secrets
- Reproducibility: Deterministic build

## Risks, assumptions, and open questions

- Risks: Outdated CLI flags
- Assumptions: Python 3.12 available
- Open questions: none

## Approval

- Approver: Lead Author
- Exact confirmation: Approved brief 2026.11.25 for initialization
- Confirmed at: 2026-11-25T01:00:00Z
""",
        encoding="utf-8",
    )
    return path


def make_docx_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", "<w:document/>")
    return buf.getvalue()


def source_row(root: Path, source_id: str, adapter: str, filename: str, contents: bytes) -> dict:
    target = root / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(contents)
    return {
        "source_id": source_id,
        "class": "authoritative",
        "adapter_id": adapter,
        "path_or_url": filename,
        "publisher_or_owner": "team",
        "retrieved_at": "2026-11-25T00:00:00Z",
        "sha256": hashlib.sha256(contents).hexdigest(),
        "privacy_class": "internal",
        "permitted_use": "factual,context",
        "exclusions": "style,incoming",
        "metadata_json": "{}",
        "derived_artifacts_json": "[]",
    }


def write_sources_tsv(root: Path, rows: list[dict], rel_path: str = "sources.tsv") -> str:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return rel_path


def test_schema_profile_and_brief_validation_positive_and_negative(tmp_path: Path) -> None:
    raw_profile = make_profile(tmp_path)
    write_brief(tmp_path)

    report = schema.Report(tmp_path)
    normalized = schema.validate_profile(raw_profile, report)
    adapters = schema.validate_format_registry(REGISTRY, normalized, report)
    brief = schema.validate_brief(normalized, adapters, report)
    assert report.errors == []
    assert report.status == "READY"
    assert brief is not None
    assert brief["deliverables"][0]["path"] == "deliverables/guide.md"

    # Negative profile checks: invalid origin, path escape, uppercase format
    bad_profile = make_profile(tmp_path)
    bad_profile["route"]["origin"] = "guessed"
    bad_profile["paths"]["brief"]["value"] = "../outside.md"
    bad_profile["formats"]["value"] = ["Markdown"]
    bad_report = schema.Report(tmp_path)
    schema.validate_profile(bad_profile, bad_report)
    codes = {e["code"] for e in bad_report.errors}
    assert {"PROFILE_ORIGIN", "PROFILE_PATH_ESCAPE", "PROFILE_LIST"}.issubset(codes)

    # Negative brief checks: pending approval and extension masquerading
    write_brief(
        tmp_path,
        approval_state="pending",
        deliverable_rows="| Guide | en | markdown | required | full | deliverables/guide.pdf |",
    )
    brief_report = schema.Report(tmp_path)
    schema.validate_brief(normalized, adapters, brief_report)
    brief_codes = {e["code"] for e in brief_report.errors}
    assert "BRIEF_APPROVAL" in brief_codes
    assert "BRIEF_DELIVERABLES" in brief_codes


def test_schema_routing_requires_needs_v2_and_checks_freshness(tmp_path: Path) -> None:
    from manuscript_ops_core import build_routing_snapshot

    answers = {
        "dimensions": {name: {"score": 1, "evidence": ["scoped"]} for name in schema.DIMENSIONS},
        "hard_triggers": {
            "explicit_project": True,
            "cross_session": True,
            "large_volume": False,
            "high_risk_facts": False,
            "locked_derivatives": False,
            "reproducible_multi_format": False,
            "independent_multi_thread_acceptance": False,
        },
        "task": {
            "scope": "long-form",
            "operation": "write",
            "lifecycle_required": True,
            "risk_axes": [],
            "deliverables": [{"format": "markdown", "purpose": "deliverable"}],
            "image_count": 0,
            "evidence": ["book project"],
        },
    }
    snap = build_routing_snapshot(tmp_path, answers=answers, captured_at="2026-11-25T00:00:00Z")
    profile = {"route": "Project", "snapshot_max_age_hours": 24}

    ok_report = validate_state.Report(tmp_path)
    validate_state.validate_routing(
        snap, profile, ok_report, datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
    )
    assert ok_report.errors == []

    # Reject missing or retired routing_policy
    for bad_policy in (None, "-".join(("score", "v1"))):
        bad_snap = json.loads(json.dumps(snap))
        if bad_policy is None:
            bad_snap.pop("routing_policy", None)
        else:
            bad_snap["routing_policy"] = bad_policy
        rep = validate_state.Report(tmp_path)
        validate_state.validate_routing(
            bad_snap, profile, rep, datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
        )
        assert "ROUTING_POLICY" in {e["code"] for e in rep.errors}

    # Stale snapshot and damaged review axes
    stale_snap = json.loads(json.dumps(snap))
    stale_snap["required_review_axes"] = ["intent-structure"]
    stale_rep = validate_state.Report(tmp_path)
    validate_state.validate_routing(
        stale_snap, profile, stale_rep, datetime(2026, 11, 28, 0, 0, tzinfo=timezone.utc)
    )
    assert {"SNAPSHOT_STALE", "ROUTING_REVIEW_AXES"}.issubset(
        {e["code"] for e in stale_rep.errors}
    )


def test_schema_format_registry_baseline_protection(tmp_path: Path) -> None:
    altered = json.loads(json.dumps(REGISTRY))
    next(a for a in altered["adapters"] if a["id"] == "pdf")["blocking_qa_gaps"] = False
    rep = schema.Report(tmp_path)
    schema.validate_format_registry(altered, {"formats": ["pdf"]}, rep)
    assert "FORMAT_BASELINE" in {e["code"] for e in rep.errors}


def test_lineage_source_register_identity_derivatives_and_authority(tmp_path: Path) -> None:
    rows = [
        source_row(tmp_path, "S1", "markdown", "sources/memo.md", b"# Confirmed memo\n"),
        source_row(tmp_path, "S2", "pdf", "sources/spec.pdf", b"%PDF-1.7\n%%EOF\n"),
        source_row(tmp_path, "S3", "docx", "sources/guide.docx", make_docx_bytes()),
    ]
    tsv = write_sources_tsv(tmp_path, rows)
    rep = lineage.Report(tmp_path) if hasattr(lineage, "Report") else schema.Report(tmp_path)
    res = lineage.validate_source_register(tsv, REGISTRY, rep)
    assert rep.errors == []
    assert res is not None and set(res["sources"]) == {"S1", "S2", "S3"}

    # Reject renamed OLE .doc pretending to be .docx and markdown pretending to be .pdf
    spoof_rows = [
        source_row(
            tmp_path,
            "BAD1",
            "docx",
            "sources/fake.docx",
            bytes.fromhex("d0cf11e0a1b11ae1") + b"ole-doc",
        ),
        source_row(tmp_path, "BAD2", "pdf", "sources/fake.pdf", b"# plain markdown\n"),
    ]
    bad_rep = schema.Report(tmp_path)
    lineage.validate_source_register(
        write_sources_tsv(tmp_path, spoof_rows, "bad.tsv"), REGISTRY, bad_rep
    )
    assert "SOURCE_FORMAT" in {e["code"] for e in bad_rep.errors}

    # Derivative cannot promote reference-only parent authority or permissions
    parent = source_row(tmp_path, " P1 ", "pdf", "sources/ref.pdf", b"%PDF-1.4\n%%EOF\n")
    parent.update(
        {
            "class": "reference-only",
            "permitted_use": "context",
            "exclusions": "factual,style,incoming",
        }
    )
    child = source_row(
        tmp_path, "C1", "json-text-extract", "sources/pages.json", b'{"pages":["ok"]}'
    )
    parent["derived_artifacts_json"] = json.dumps(
        [
            {
                "kind": "page_text_extract",
                "path": "./sources/pages.json",
                "sha256": child["sha256"],
                "parent_source_ids": ["P1"],
                "created_at": "2026-11-25T00:00:00Z",
            }
        ]
    )
    promo_rep = schema.Report(tmp_path)
    lineage.validate_source_register(
        write_sources_tsv(tmp_path, [parent, child], "promo.tsv"), REGISTRY, promo_rep
    )
    assert {"SOURCE_CLASS", "SOURCE_POLICY"}.issubset({e["code"] for e in promo_rep.errors})

    # Retaining parent limits passes cleanly
    child.update(
        {
            "class": "reference-only",
            "permitted_use": "context",
            "exclusions": "factual,style,incoming",
        }
    )
    clean_rep = schema.Report(tmp_path)
    lineage.validate_source_register(
        write_sources_tsv(tmp_path, [parent, child], "clean.tsv"), REGISTRY, clean_rep
    )
    assert clean_rep.errors == []


def test_lineage_batches_dag_prerequisites_and_source_authority(tmp_path: Path) -> None:
    inp = tmp_path / "manuscript" / "in.md"
    inp.parent.mkdir(parents=True, exist_ok=True)
    inp.write_bytes(b"frozen input\n")
    inp_hash = hashlib.sha256(b"frozen input\n").hexdigest()

    manifest = {
        "schema_version": "1",
        "date_version": "2026.11.25",
        "batches": [
            {
                "id": "b1",
                "label": "Chapter 1",
                "kind": "content",
                "scope": ["ch1"],
                "source_dependencies": [
                    {"source_id": "REF1", "use": "factual", "purpose": "claims"}
                ],
                "depends_on": ["b2"],
                "risk": "low",
                "review_axes": ["intent-structure"],
                "reviewable_volume": {"unit": "chapters", "target": 1, "rationale": "bounded"},
                "review_cadence": "incremental",
                "cumulative_regression": False,
                "regression_surface": [],
                "input_snapshot": {
                    "path": "manuscript/in.md",
                    "sha256": inp_hash,
                    "captured_at": "2026-11-25T00:00:00Z",
                },
                "outputs": [{"path": "manuscript/ch1.md", "sha256": None}],
                "status": "active",
                "user_gate": "not_required",
                "review_report": None,
                "user_confirmation": None,
            },
            {
                "id": "b2",
                "label": "Chapter 2",
                "kind": "outline",
                "scope": ["outline"],
                "source_dependencies": [],
                "depends_on": ["b1"],
                "risk": "low",
                "review_axes": ["intent-structure"],
                "reviewable_volume": {"unit": "docs", "target": 1, "rationale": "bounded"},
                "review_cadence": "incremental",
                "cumulative_regression": False,
                "regression_surface": [],
                "input_snapshot": None,
                "outputs": [{"path": "docs/outline.md", "sha256": None}],
                "status": "planned",
                "user_gate": "required",
                "review_report": None,
                "user_confirmation": None,
            },
        ],
    }
    rep = schema.Report(tmp_path)
    batches = lineage.validate_batches(manifest, {"date_version": "2026.11.25"}, rep)
    ref_row = source_row(tmp_path, "REF1", "markdown", "sources/ref.md", b"# ref\n")
    ref_row.update(
        {
            "class": "reference-only",
            "permitted_use": "context",
            "exclusions": "factual,style,incoming",
        }
    )
    src_res = lineage.validate_source_register(
        write_sources_tsv(tmp_path, [ref_row]), REGISTRY, rep
    )
    lineage.validate_batch_source_dependencies(batches, src_res, rep)
    codes = {e["code"] for e in rep.errors}
    assert {
        "BATCH_CYCLE",
        "BATCH_DEPENDENCY_STATUS",
        "BATCH_REGRESSION",
        "BATCH_SOURCE_POLICY",
        "BATCH_SOURCE_AUTHORITY",
    }.issubset(codes)
