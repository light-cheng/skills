"""Behavioral tests for qa.py, gates.py, acceptance integration, and validate_state CLI."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import gates  # noqa: E402
import qa  # noqa: E402
import schema  # noqa: E402
import validate_state  # noqa: E402

REGISTRY_PATH = PACKAGE_ROOT / "assets" / "format-registry.json"
CAP_MAP_PATH = PACKAGE_ROOT / "assets" / "platform-capability-map.json"
REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
TSV_COLUMNS = (
    (PACKAGE_ROOT / "assets" / "templates" / "source-register.tsv")
    .read_text(encoding="utf-8")
    .strip()
    .split("\t")
)
CORE_AXES = sorted(
    {
        "intent-structure",
        "factual-sources",
        "terminology-localization",
        "reader-accessibility",
        "safety-privacy-legal",
        "format-layout",
        "reproducibility-recovery",
        "compatibility-round-trip",
    }
)


def write_hashed(root: Path, rel_path: str, content: bytes | str) -> dict[str, str]:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = content.encode("utf-8") if isinstance(content, str) else content
    target.write_bytes(raw)
    return {"path": rel_path, "sha256": hashlib.sha256(raw).hexdigest()}


def build_complete_project(root: Path) -> dict[str, dict[str, str]]:
    """Build a valid published Project fixture using .scratch/<feature>/acceptance/ records."""
    from manuscript_ops_core import build_routing_snapshot

    state_dir = root / ".manuscript-ops"
    (state_dir / "gates").mkdir(parents=True)
    (state_dir / "snapshots").mkdir(parents=True)
    (state_dir / "format-qa").mkdir(parents=True)
    (state_dir / "sources").mkdir(parents=True)

    # 1. Authoritative source + Source Register
    src_file = write_hashed(root, "sources/authoritative/spec.md", "# Primary Specification\n")
    tsv_path = state_dir / "sources" / "source-register.tsv"
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerow(
            {
                "source_id": "S1",
                "class": "authoritative",
                "adapter_id": "markdown",
                "path_or_url": src_file["path"],
                "publisher_or_owner": "Engineering",
                "retrieved_at": "2026-11-25T00:00:00Z",
                "sha256": src_file["sha256"],
                "privacy_class": "internal",
                "permitted_use": "factual,context",
                "exclusions": "style,incoming",
                "metadata_json": "{}",
                "derived_artifacts_json": "[]",
            }
        )
    source_reg_entry = {
        "path": ".manuscript-ops/sources/source-register.tsv",
        "sha256": hashlib.sha256(tsv_path.read_bytes()).hexdigest(),
    }

    # 2. Core manuscript documents and deliverable
    outline_entry = write_hashed(root, "docs/outline.md", "# Outline\n1. Prerequisites\n2. Guide\n")
    write_hashed(root, "docs/source-map.md", "# Source Map\nS1 -> Guide\n")
    write_hashed(root, "docs/glossary.md", "# Glossary\nGate: Milestone check\n")
    locked_ms = write_hashed(root, "manuscript/locked-guide.md", "# Operator Guide\nVerified text.\n")
    deliverable = write_hashed(root, "deliverables/guide.md", "# Operator Guide\nVerified text.\n")

    brief_text = """# Manuscript Brief

- Schema version: 1
- Date version: 2026.11.25
- Approval state: approved

## Goal

Deliver a reproducible operator guide.

## Audience and use

- Primary audience: Site reliability engineers
- Target-reader prerequisites: POSIX shell fundamentals
- Reading environment: Terminal and browser
- Required accessibility or localization: Clear structure

## Scope

- Included: Deployment and rollback
- Excluded: Hardware procurement

## Source authority

- Authoritative sources: S1
- Reference-only material: none
- Incoming draft status: none
- Prohibited or unavailable sources: none

## Framework

- Approved outline or outline acceptance rule: docs/outline.md
- Required terminology: docs/glossary.md
- Content boundaries: Operational steps only

## Deliverables

| Deliverable | Language | Format | Reproducible | Visual QA | Stable path |
|---|---|---|---|---|---|
| Operator Guide | en | markdown | required | sampled | deliverables/guide.md |

## Review and gates

- Applicable review axes: eight mandatory core axes
- Required independent milestones: outline, source-lock, final
- Human gates: all six project gates

## Acceptance

- Content: Concept grounding and completeness
- Sources: S1 factual alignment
- Format: Markdown structural, render, sampled visual, semantic, and round-trip QA
- Privacy and safety: Internal safe
- Reproducibility: Deterministic generator

## Risks, assumptions, and open questions

- Risks: Stale commands
- Assumptions: Local renderer available
- Open questions: none

## Approval

- Approver: Chief Editor
- Exact confirmation: Approved Operator Guide Brief 2026.11.25
- Confirmed at: 2026-11-25T01:00:00Z
"""
    brief_entry = write_hashed(root, "docs/manuscript-brief.md", brief_text)

    # 3. Format registry & capability snapshot
    write_hashed(
        root,
        ".manuscript-ops/format-registry.json",
        REGISTRY_PATH.read_text(encoding="utf-8"),
    )
    platform_caps = {
        "schema_version": "1",
        "platform": "claude-code",
        "captured_at": "2026-11-25T02:00:00Z",
        "capabilities": [
            {
                "name": "browser",
                "provider": "headless-chromium",
                "version": "130.0",
                "evidence": "rendered markdown preview",
                "operations": ["render", "runtime_qa"],
            },
            {
                "name": "image_inspector",
                "provider": "vision-check",
                "version": "1.0",
                "evidence": "inspected rendered view",
                "operations": ["visual_qa"],
            },
        ],
    }
    platform_entry = write_hashed(
        root, ".manuscript-ops/platform-capabilities.json", json.dumps(platform_caps, indent=2)
    )
    from probe_capabilities import adapter_status, load_platform_capabilities

    plat_obs, plat_prov = load_platform_capabilities(
        root / platform_entry["path"], CAP_MAP_PATH
    )
    # Build deterministic observed map without machine-specific process_probe entries.
    observed = {
        name: plat_obs[name]
        for name in plat_obs
    }
    for alias_name in (
        "rtf_capable_editor",
        "spreadsheet_application",
        "microsoft_365_connector",
        "google_workspace_connector",
        "apple_iwork_application",
    ):
        observed[alias_name] = {
            "available": False,
            "evidence": None,
            "provider": None,
            "version": None,
            "operations": [],
            "source": None,
        }
    cap_snapshot = {
        "schema_version": "1",
        "captured_at": "2026-11-25T02:05:00Z",
        "registry": str(REGISTRY_PATH.resolve()),
        "declared_capabilities": [],
        "platform_snapshot": {
            **plat_prov,
            "path": platform_entry["path"],
        },
        "observed": observed,
        "adapters": [adapter_status(item, observed) for item in REGISTRY["adapters"]],
        "claim_warning": "Structured platform snapshot verified.",
    }
    cap_entry = write_hashed(
        root, ".manuscript-ops/capability-snapshot.json", json.dumps(cap_snapshot, indent=2)
    )

    # 4. ProjectProfile & baseline profile snapshot
    def wrap(val: object, origin: str = "规则推导", ev: str = "fixture") -> dict:
        return {"value": val, "origin": origin, "evidence": ev}

    profile_data = {
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
        "languages": wrap(["en"], "用户决定"),
        "formats": wrap(["markdown"], "用户决定"),
        "dependencies": wrap([], "资料发现"),
        "capabilities_snapshot": wrap(cap_entry["path"], "资料发现"),
        "version_control": {
            "system": wrap("jj"),
            "tested_baseline": wrap("0.43.0"),
            "colocated": wrap(False),
            "remote_allowed": wrap(False),
        },
        "snapshot_max_age_hours": wrap(168),
        "unknowns": wrap([], "资料发现"),
    }
    write_hashed(
        root, ".manuscript-ops/project-profile.json", json.dumps(profile_data, indent=2)
    )
    baseline_profile_entry = write_hashed(
        root,
        ".manuscript-ops/snapshots/baseline-profile-2026.11.25.json",
        json.dumps(profile_data, indent=2),
    )

    # 5. Routing snapshot
    routing_snap = build_routing_snapshot(
        root,
        answers={
            "dimensions": {
                name: {"score": 1, "evidence": ["scoped guide"]}
                for name in schema.DIMENSIONS
            },
            "hard_triggers": {
                "explicit_project": True,
                "cross_session": True,
                "large_volume": False,
                "high_risk_facts": False,
                "locked_derivatives": True,
                "reproducible_multi_format": False,
                "independent_multi_thread_acceptance": False,
            },
            "task": {
                "scope": "bounded",
                "operation": "write",
                "lifecycle_required": True,
                "risk_axes": [],
                "deliverables": [{"format": "markdown", "purpose": "deliverable"}],
                "image_count": 0,
                "evidence": ["explicit governed guide"],
            },
        },
        captured_at="2026-11-25T01:05:00Z",
    )
    write_hashed(
        root, ".manuscript-ops/routing-snapshot.json", json.dumps(routing_snap, indent=2)
    )

    # 6. Format QA evidence and record
    val_log = write_hashed(root, ".manuscript-ops/format-qa/lint.log", "markdownlint: 0 errors\n")
    rendered_view = write_hashed(root, ".manuscript-ops/format-qa/page-1.png", b"\x89PNG\r\n\x1a\nview")
    visual_note = write_hashed(root, ".manuscript-ops/format-qa/visual.json", '{"page_1":"clean"}')
    cmp_report = write_hashed(root, ".manuscript-ops/format-qa/compare.json", '{"headings":"match"}')
    rt_out = write_hashed(root, ".manuscript-ops/format-qa/roundtrip.md", "# Operator Guide\nVerified text.\n")

    qa_record = {
        "schema_version": "1",
        "format": "markdown",
        "status": "READY",
        "artifact": deliverable,
        "provider": {"name": "markdown-pipeline", "version": "1.0", "evidence": "local build"},
        "generation": {
            "mode": "reproducible",
            "tool": {"name": "cp-builder", "version": "1.0", "evidence": "scripted"},
            "command": ["cp", locked_ms["path"], deliverable["path"]],
            "configuration": {
                "path": None,
                "sha256": None,
                "not_applicable_reason": "direct locked markdown copy",
            },
            "inputs": [locked_ms],
            "output": deliverable,
            "manual_disposition": None,
        },
        "checks": {
            "structural": {
                "status": "PASS",
                "evidence": "headings and links valid",
                "coverage": {
                    "mode": "full",
                    "unit": "checks",
                    "total": 2,
                    "inspected": 2,
                    "items": ["headings", "links"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "validator_log", **val_log}],
            },
            "render": {
                "status": "PASS",
                "evidence": "rendered in headless browser",
                "coverage": {
                    "mode": "full",
                    "unit": "views",
                    "total": 1,
                    "inspected": 1,
                    "items": ["view-1"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "rendered_output", **rendered_view}],
            },
            "visual": {
                "status": "PASS",
                "evidence": "sampled page visual check per Brief",
                "coverage": {
                    "mode": "sampled",
                    "unit": "views",
                    "total": 2,
                    "inspected": 1,
                    "items": ["view-1"],
                    "sampling_authority": {
                        "path": brief_entry["path"],
                        "sha256": brief_entry["sha256"],
                        "deliverable": deliverable["path"],
                        "policy": "sampled",
                    },
                },
                "evidence_artifacts": [{"kind": "inspection_record", **visual_note}],
            },
            "semantic": {
                "status": "PASS",
                "evidence": "matches locked manuscript",
                "coverage": {
                    "mode": "full",
                    "unit": "sections",
                    "total": 1,
                    "inspected": 1,
                    "items": ["sec-1"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "comparison_report", **cmp_report}],
                "invariants": ["headings", "steps"],
                "reference_artifact": locked_ms,
            },
            "round_trip": {
                "status": "PASS",
                "evidence": "round-trip preserved markdown AST",
                "coverage": {
                    "mode": "full",
                    "unit": "files",
                    "total": 1,
                    "inspected": 1,
                    "items": ["guide.md"],
                    "sampling_authority": None,
                },
                "evidence_artifacts": [{"kind": "comparison_report", **cmp_report}],
                "output_artifact": rt_out,
                "invariants": ["headings", "code_blocks"],
            },
        },
        "completed_at": "2026-11-25T03:00:00Z",
    }
    qa_record_entry = write_hashed(
        root, ".manuscript-ops/format-qa/guide-md.json", json.dumps(qa_record, indent=2)
    )
    qa_index_entry = {
        "format": "markdown",
        "status": "READY",
        "evidence_path": qa_record_entry["path"],
        "sha256": qa_record_entry["sha256"],
        "rendered": True,
        "visually_inspected": True,
    }

    # 7. Acceptance Charter & Milestone Verdicts under .scratch/<feature>/acceptance/
    charter_entry = write_hashed(
        root,
        ".scratch/operator-guide/acceptance/charter.md",
        "# Acceptance Charter\nProfile: manuscript\n",
    )

    def write_acceptance_verdict(
        milestone: str, snapshot_files: list[dict[str, str]], completed_at: str
    ) -> dict[str, str]:
        payload = {
            "schema_version": "1",
            "provider": "acceptance",
            "profile": "manuscript",
            "milestone": milestone,
            "charter": charter_entry,
            "artifact_snapshot": {
                "captured_at": completed_at,
                "files": snapshot_files,
            },
            "verdict": {"result": "PASS"},
            "completed_at": completed_at,
            "manuscript_evidence": [
                {
                    "axis": axis,
                    "evidence": [{"kind": "manuscript_artifact", **snapshot_files[0]}],
                }
                for axis in CORE_AXES
            ],
        }
        return write_hashed(
            root,
            f".scratch/operator-guide/acceptance/{milestone}-verdict.json",
            json.dumps(payload, indent=2),
        )

    outline_verdict = write_acceptance_verdict(
        "outline", [outline_entry, brief_entry], "2026-11-25T02:10:00Z"
    )
    source_lock_verdict = write_acceptance_verdict(
        "source-lock", [source_reg_entry, locked_ms], "2026-11-25T02:30:00Z"
    )
    final_snapshot_files = [deliverable, locked_ms, qa_record_entry]
    final_verdict = write_acceptance_verdict(
        "final", final_snapshot_files, "2026-11-25T03:10:00Z"
    )

    # 8. ReviewMatrix matching final acceptance report
    review_matrix = {
        "schema_version": "1",
        "profile": "manuscript",
        "milestone": "final",
        "artifact_snapshot": {
            "captured_at": "2026-11-25T03:10:00Z",
            "files": final_snapshot_files,
        },
        "axes": [
            {
                "id": axis_id,
                "label": axis_id,
                "applicable": axis_id != "images",
                "reason": "no images in markdown guide" if axis_id == "images" else "core project audit",
                "evidence_required": [] if axis_id == "images" else ["verified in frozen snapshot"],
            }
            for axis_id in sorted(schema.REVIEW_AXIS_IDS)
        ],
    }
    matrix_entry = write_hashed(
        root, ".manuscript-ops/reviews/final-matrix.json", json.dumps(review_matrix, indent=2)
    )

    # 9. BatchManifest with accepted final batch
    batch_manifest = {
        "schema_version": "1",
        "date_version": "2026.11.25",
        "batches": [
            {
                "id": "batch-final",
                "label": "Final Guide",
                "kind": "final",
                "scope": ["all"],
                "source_dependencies": [
                    {"source_id": "S1", "use": "factual", "purpose": "operator commands"}
                ],
                "depends_on": [],
                "risk": "medium",
                "review_axes": CORE_AXES,
                "reviewable_volume": {"unit": "chapters", "target": 2, "rationale": "short guide"},
                "review_cadence": "cumulative",
                "cumulative_regression": True,
                "regression_surface": ["deliverables/guide.md"],
                "input_snapshot": {
                    **locked_ms,
                    "captured_at": "2026-11-25T02:40:00Z",
                },
                "outputs": [deliverable],
                "status": "accepted",
                "user_gate": "required",
                "review_report": final_verdict,
                "user_confirmation": {
                    "actor": "Chief Editor",
                    "exact_statement": "Accepted final batch",
                    "confirmed_at": "2026-11-25T03:20:00Z",
                },
            }
        ],
    }
    write_hashed(
        root, ".manuscript-ops/batch-manifest.json", json.dumps(batch_manifest, indent=2)
    )

    # 10. Six GateReceipts
    def write_receipt(gate: str, alias: str, extra: dict, confirmed_at: str, created_at: str) -> dict[str, str]:
        base = {
            "schema_version": "1",
            "gate": gate,
            "date_version": "2026.11.25",
            "created_at": created_at,
            "bookmark": f"{gate}-2026.11.25",
            "current_alias": alias,
            "jujutsu": {
                "version": "jj 0.43.0",
                "change_id": f"chg-{gate}",
                "commit_id": f"cmt-{gate}",
                "remote_count": 0,
            },
            "files": [brief_entry],
            "baseline_profile": {"required": False, "path": "", "sha256": ""},
            "locked_source": {"required": False, "path": "", "sha256": ""},
            "capability_snapshot": {"required": False, "path": "", "sha256": ""},
            "format_qa": [],
            "publication": {"required": False, "target": None, "final_receipt": None},
            "review": {
                "required": False,
                "report_path": "",
                "report_sha256": "",
                "verdict": "NOT_REQUIRED",
                "upstream_independence": "not_applicable",
                "independence": "not_applicable",
                "evaluator_fresh": False,
            },
            "user_confirmation": {
                "actor": "Chief Editor",
                "exact_statement": f"Confirmed {gate}",
                "confirmed_at": confirmed_at,
            },
        }
        base.update(extra)
        return write_hashed(
            root,
            f".manuscript-ops/gates/{gate}-2026.11.25.json",
            json.dumps(base, indent=2),
        )

    write_receipt(
        "brief-approved",
        "current-brief",
        {
            "files": [brief_entry],
            "user_confirmation": {
                "actor": "Chief Editor",
                "exact_statement": "Approved Operator Guide Brief 2026.11.25",
                "confirmed_at": "2026-11-25T01:00:00Z",
            },
        },
        "2026-11-25T01:00:00Z",
        "2026-11-25T01:01:00Z",
    )
    write_receipt(
        "baseline",
        "current-baseline",
        {
            "files": [brief_entry, baseline_profile_entry],
            "baseline_profile": {"required": True, **baseline_profile_entry},
        },
        "2026-11-25T01:15:00Z",
        "2026-11-25T01:16:00Z",
    )
    write_receipt(
        "framework-approved",
        "current-framework",
        {
            "files": [outline_entry, brief_entry],
            "review": {
                "required": True,
                "report_path": outline_verdict["path"],
                "report_sha256": outline_verdict["sha256"],
                "verdict": "PASS",
                "upstream_independence": "full",
                "independence": "native",
                "evaluator_fresh": True,
            },
        },
        "2026-11-25T02:15:00Z",
        "2026-11-25T02:16:00Z",
    )
    write_receipt(
        "source-locked",
        "current-source-locked",
        {
            "files": [source_reg_entry, locked_ms],
            "locked_source": {"required": True, **locked_ms},
            "review": {
                "required": True,
                "report_path": source_lock_verdict["path"],
                "report_sha256": source_lock_verdict["sha256"],
                "verdict": "PASS",
                "upstream_independence": "full",
                "independence": "native",
                "evaluator_fresh": True,
            },
        },
        "2026-11-25T02:35:00Z",
        "2026-11-25T02:36:00Z",
    )
    final_receipt_entry = write_receipt(
        "final-approved",
        "current-final",
        {
            "files": [deliverable, locked_ms, qa_record_entry],
            "capability_snapshot": {"required": True, **cap_entry},
            "format_qa": [qa_index_entry],
            "review": {
                "required": True,
                "report_path": final_verdict["path"],
                "report_sha256": final_verdict["sha256"],
                "verdict": "PASS",
                "upstream_independence": "full",
                "independence": "native",
                "evaluator_fresh": True,
            },
        },
        "2026-11-25T03:30:00Z",
        "2026-11-25T03:31:00Z",
    )
    write_receipt(
        "publish-approved",
        "current-publish",
        {
            "files": [deliverable, locked_ms, qa_record_entry],
            "capability_snapshot": {"required": True, **cap_entry},
            "format_qa": [qa_index_entry],
            "publication": {
                "required": True,
                "target": {
                    "kind": "release",
                    "visibility": "internal",
                    "identifier": "ops-portal-v1",
                    "action": "publish-bundle",
                    "evidence": "approved internal release ticket",
                },
                "final_receipt": final_receipt_entry,
            },
        },
        "2026-11-25T03:45:00Z",
        "2026-11-25T03:46:00Z",
    )

    # 11. LifecycleState
    state_payload = {
        "schema_version": "1",
        "date_version": "2026.11.25",
        "phase": "published",
        "required_gates": [
            "brief-approved",
            "baseline",
            "framework-approved",
            "source-locked",
            "final-approved",
            "publish-approved",
        ],
        "active_receipts": {
            "brief-approved": "brief-approved-2026.11.25",
            "baseline": "baseline-2026.11.25",
            "framework-approved": "framework-approved-2026.11.25",
            "source-locked": "source-locked-2026.11.25",
            "final-approved": "final-approved-2026.11.25",
            "publish-approved": "publish-approved-2026.11.25",
        },
        "active_batch": None,
        "source_register": source_reg_entry["path"],
        "review_matrix": matrix_entry["path"],
        "latest_review_report": final_verdict["path"],
        "capability_snapshot": cap_entry["path"],
        "format_qa_records": [qa_index_entry],
        "updated_at": "2026-11-25T03:50:00Z",
    }
    write_hashed(root, ".manuscript-ops/state.json", json.dumps(state_payload, indent=2))
    return {
        "deliverable": deliverable,
        "locked_ms": locked_ms,
        "qa_record": qa_record_entry,
        "final_verdict": final_verdict,
    }


def install_fake_jj(bin_dir: Path, project_root: Path) -> None:
    """Create an executable fake `jj` binary to exercise the external VCS subprocess seam."""
    (project_root / ".jj" / "repo").mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    jj_script = bin_dir / "jj"
    jj_script.write_text(
        f"""#!{sys.executable}
import sys
from pathlib import Path

args = sys.argv[1:]
# Strip --ignore-working-copy and -R <root>
clean = []
i = 0
root = Path(".")
while i < len(args):
    if args[i] == "--ignore-working-copy":
        i += 1
    elif args[i] == "-R":
        root = Path(args[i + 1])
        i += 2
    else:
        clean.append(args[i])
        i += 1

gates = [
    "brief-approved",
    "baseline",
    "framework-approved",
    "source-locked",
    "final-approved",
    "publish-approved",
]
aliases = {{
    "current-brief": "brief-approved-2026.11.25",
    "current-baseline": "baseline-2026.11.25",
    "current-framework": "framework-approved-2026.11.25",
    "current-source-locked": "source-locked-2026.11.25",
    "current-final": "final-approved-2026.11.25",
    "current-publish": "publish-approved-2026.11.25",
}}

if clean == ["--version"]:
    print("jj 0.43.0")
elif clean[:2] == ["config", "list"]:
    print("builtin_immutable_heads() | " + " | ".join(f'bookmarks(glob:"{{g}}-*")' for g in gates))
elif clean == ["git", "remote", "list"]:
    pass
elif clean == ["bookmark", "list"]:
    for g in gates:
        print(f"{{g}}-2026.11.25: seal-{{g}}")
    for a, target in aliases.items():
        g = target.rsplit("-2026.11.25", 1)[0]
        print(f"{{a}}: seal-{{g}}")
elif clean[:2] == ["log", "-r"]:
    rev = clean[2]
    tmpl = clean[-1]
    if rev in aliases:
        rev = aliases[rev]
    if rev.startswith("parents(") and rev.endswith(")"):
        bm = rev[len("parents("):-1]
        gate = bm.rsplit("-2026.11.25", 1)[0]
        print(f"cmt-{{gate}}" if tmpl == "commit_id" else f"chg-{{gate}}")
    else:
        gate = rev.rsplit("-2026.11.25", 1)[0]
        if tmpl == "commit_id":
            print(f"seal-{{gate}}")
        else:
            print("true")
elif clean[:3] == ["file", "show", "-r"]:
    rel_path = clean[4]
    sys.stdout.buffer.write((root / rel_path).read_bytes())
else:
    sys.exit(1)
""",
        encoding="utf-8",
    )
    jj_script.chmod(jj_script.stat().st_mode | stat.S_IXUSR)


def test_end_to_end_validate_state_cli_ready_json_text_and_jj_gates(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    build_complete_project(project)
    bin_dir = tmp_path / "bin"
    install_fake_jj(bin_dir, project)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

    res_json = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "validate_state.py"),
            "--root",
            str(project),
            "--check-vcs",
            "--now",
            "2026-11-25T04:00:00Z",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert res_json.returncode == 0, res_json.stdout + res_json.stderr
    payload = json.loads(res_json.stdout)
    assert payload["status"] == "READY"
    assert payload["errors"] == []
    check_codes = {c["code"] for c in payload["checks"]}
    assert {
        "ACCEPTANCE_RESULT",
        "JJ_IMMUTABLE_CONFIG",
        "JJ_GATE_RECEIPT_HASH",
        "JJ_GATE_FILE_HASH",
        "JJ_ALIAS_TARGET",
    }.issubset(check_codes)

    res_text = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "validate_state.py"),
            "--root",
            str(project),
            "--now",
            "2026-11-25T04:00:00Z",
            "--format",
            "text",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert res_text.returncode == 0
    assert "status: READY" in res_text.stdout


def test_acceptance_gate_report_validates_provider_charter_cause_and_evidence(tmp_path: Path) -> None:
    doc = write_hashed(tmp_path, "docs/outline.md", "# Outline\n")
    charter = write_hashed(tmp_path, ".scratch/feat/acceptance/charter.md", "# Charter\n")

    # Valid FAIL report with Cause: direction
    fail_report_data = {
        "schema_version": "1",
        "provider": "acceptance",
        "profile": "manuscript",
        "milestone": "outline",
        "charter": charter,
        "artifact_snapshot": {"captured_at": "2026-11-25T01:00:00Z", "files": [doc]},
        "verdict": {"result": "FAIL", "cause": "direction"},
        "completed_at": "2026-11-25T01:05:00Z",
        "manuscript_evidence": [
            {"axis": "intent-structure", "evidence": [{"kind": "outline", **doc}]}
        ],
    }
    fail_entry = write_hashed(
        tmp_path, ".scratch/feat/acceptance/verdict.json", json.dumps(fail_report_data)
    )
    rep = schema.Report(tmp_path)
    parsed = gates.validate_acceptance_report(fail_entry["path"], rep)
    assert rep.errors == []
    assert parsed is not None
    assert parsed["verdict"] == "FAIL"
    assert parsed["cause"] == "direction"

    # Negative: wrong provider, invalid cause on PASS, missing evidence
    bad_data = json.loads(json.dumps(fail_report_data))
    bad_data["provider"] = "unknown-tool"
    bad_data["verdict"] = {"result": "PASS", "cause": "unknown"}
    bad_data["manuscript_evidence"] = []
    bad_entry = write_hashed(
        tmp_path, ".scratch/feat/acceptance/bad.json", json.dumps(bad_data)
    )
    bad_rep = schema.Report(tmp_path)
    gates.validate_acceptance_report(bad_entry["path"], bad_rep)
    codes = {e["code"] for e in bad_rep.errors}
    assert {"ACCEPTANCE_PROVIDER", "ACCEPTANCE_CAUSE", "ACCEPTANCE_EVIDENCE"}.issubset(codes)


def test_qa_and_gate_negative_tampering_blocks_project(tmp_path: Path) -> None:
    project = tmp_path / "tampered"
    project.mkdir()
    refs = build_complete_project(project)

    # Break locked-source lineage in QA record and confirmation chronology in final receipt
    qa_path = project / refs["qa_record"]["path"]
    qa_data = json.loads(qa_path.read_text(encoding="utf-8"))
    other_ref = write_hashed(project, "manuscript/unlocked.md", "# Unlocked draft\n")
    qa_data["checks"]["semantic"]["reference_artifact"] = other_ref
    qa_data["generation"]["mode"] = "manual"
    qa_data["generation"]["manual_disposition"] = "hand-edited"
    qa_bytes = json.dumps(qa_data, indent=2).encode("utf-8")
    qa_path.write_bytes(qa_bytes)
    new_qa_hash = hashlib.sha256(qa_bytes).hexdigest()

    # Update state.json & receipts to new QA hash, and set premature user confirmation
    state_path = project / ".manuscript-ops" / "state.json"
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    state_data["format_qa_records"][0]["sha256"] = new_qa_hash
    state_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")

    for gate_name in ("final-approved", "publish-approved"):
        rpath = project / ".manuscript-ops" / "gates" / f"{gate_name}-2026.11.25.json"
        rdata = json.loads(rpath.read_text(encoding="utf-8"))
        rdata["format_qa"][0]["sha256"] = new_qa_hash
        for f in rdata["files"]:
            if f["path"] == refs["qa_record"]["path"]:
                f["sha256"] = new_qa_hash
        if gate_name == "final-approved":
            rdata["user_confirmation"]["confirmed_at"] = "2026-11-25T02:00:00Z"
        rpath.write_text(json.dumps(rdata, indent=2), encoding="utf-8")

    res = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "validate_state.py"),
            "--root",
            str(project),
            "--now",
            "2026-11-25T04:00:00Z",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 2
    out = json.loads(res.stdout)
    assert out["status"] == "BLOCKED"
    err_codes = {e["code"] for e in out["errors"]}
    assert {
        "FORMAT_QA_GENERATION",
        "FORMAT_QA_SOURCE_LINEAGE",
        "GATE_CONFIRMATION_TIME",
    }.issubset(err_codes)


def test_version_control_route_and_backend_boundaries(tmp_path: Path) -> None:
    # Structured task does not require jj
    rep_struct = validate_state.Report(tmp_path)
    validate_state.validate_version_control(
        {"route": "Structured", "version_control": {"system": "jj"}}, {}, rep_struct
    )
    assert rep_struct.errors == []
    assert "VCS_NOT_APPLICABLE" in {c["code"] for c in rep_struct.checks}

    # Git Project reports VCS_GATES_UNSUPPORTED, not JJ_MISSING
    git_root = tmp_path / "git-proj"
    git_root.mkdir()
    subprocess.run(["git", "init", "-q", str(git_root)], check=True, capture_output=True)
    rep_git = validate_state.Report(git_root)
    validate_state.validate_version_control(
        {"route": "Project", "version_control": {"system": "git"}}, {}, rep_git
    )
    git_codes = {e["code"] for e in rep_git.errors}
    assert "VCS_GATES_UNSUPPORTED" in git_codes
    assert "JJ_MISSING" not in git_codes
    assert rep_git.status == "BLOCKED"
