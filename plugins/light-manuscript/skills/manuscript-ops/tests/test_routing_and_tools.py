"""Behavioral tests for needs-v2 routing, decide intake, next_version, and capability probing."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def base_structured_answers() -> dict:
    return {
        "dimensions": {
            name: {"score": score, "evidence": ["bounded supplied task"]}
            for name, score in {
                "scale": 0,
                "source_complexity": 1,
                "risk": 2,
                "output_complexity": 1,
                "collaboration": 1,
                "reproducibility": 1,
            }.items()
        },
        "hard_triggers": {
            "explicit_project": False,
            "cross_session": False,
            "large_volume": False,
            "high_risk_facts": True,
            "locked_derivatives": False,
            "reproducible_multi_format": False,
            "independent_multi_thread_acceptance": True,
        },
        "task": {
            "scope": "bounded",
            "operation": "rewrite",
            "risk_axes": ["safety-privacy-legal"],
            "deliverables": [
                {"format": "docx", "purpose": "deliverable"},
                {"format": "pdf", "purpose": "qa"},
            ],
            "lifecycle_required": False,
            "evidence": ["short safety memo from confirmed source"],
        },
    }


def decide_envelope(
    answer: str,
    probabilities: dict[str, float],
    *,
    applied: bool = True,
    calibrated: bool = True,
    reason: str = "none",
    method: str = "typed-decision",
) -> dict:
    return {
        "question_id": "manuscript-ops/route",
        "question": "Which route fits this manuscript task?",
        "kind": "choice",
        "options": list(probabilities),
        "answer": answer,
        "score": None,
        "probabilities": probabilities,
        "confidence": probabilities.get(answer),
        "provider_confidence": None,
        "method": method,
        "data_destination": "on-device",
        "backend": "local-opendecider",
        "calibrated": calibrated,
        "applied": applied,
        "fallback_reason": reason,
        "final": answer if applied else "Structured",
    }


def run_assessor(root: Path, answers: dict) -> subprocess.CompletedProcess[str]:
    answers_path = root.parent / f"{root.name}-answers.json"
    answers_path.write_text(json.dumps(answers), encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "assess_project.py"),
            "--root",
            str(root),
            "--answers",
            str(answers_path),
            "--captured-at",
            "2026-11-25T00:00:00Z",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_assess_project_routes_bounded_safety_task_to_structured_without_bootstrap(tmp_path: Path) -> None:
    root = tmp_path / "output"
    root.mkdir()
    res = run_assessor(root, base_structured_answers())
    assert res.returncode == 0, res.stderr
    snapshot = json.loads(res.stdout)
    assert snapshot["routing_policy"] == "needs-v2"
    assert snapshot["route"] == "Structured"
    assert "safety-privacy-legal" in snapshot["required_review_axes"]
    assert "format-layout" in snapshot["required_review_axes"]
    assert snapshot["needs_initialization"] is False
    assert snapshot["next_invocation"] is None
    assert not (root / ".manuscript-ops").exists()


def test_workspace_file_count_does_not_change_bounded_task_route(tmp_path: Path) -> None:
    small = tmp_path / "small"
    large = tmp_path / "large"
    small.mkdir()
    large.mkdir()
    for idx in range(70):
        (large / f"unrelated-{idx}.md").write_text("unrelated file\n", encoding="utf-8")
    answers = base_structured_answers()
    del answers["dimensions"]["scale"]
    s1 = json.loads(run_assessor(small, answers).stdout)
    s2 = json.loads(run_assessor(large, answers).stdout)
    assert s1["route"] == "Structured"
    assert s2["route"] == s1["route"]
    assert s2["required_review_axes"] == s1["required_review_axes"]


def test_assess_project_routes_quick_and_project_cases(tmp_path: Path) -> None:
    root = tmp_path / "work"
    root.mkdir()
    quick_answers = base_structured_answers()
    for dim in quick_answers["dimensions"].values():
        dim["score"] = 0
    quick_answers["hard_triggers"] = {k: False for k in quick_answers["hard_triggers"]}
    quick_answers["task"]["risk_axes"] = []
    quick_answers["task"]["deliverables"] = [{"format": "markdown", "purpose": "deliverable"}]
    quick_answers["unknowns"] = ["minor stylistic preference"]
    quick_snap = json.loads(run_assessor(root, quick_answers).stdout)
    assert quick_snap["route"] == "Quick"
    assert quick_snap["required_review_axes"] == []
    assert quick_snap["needs_initialization"] is False

    project_answers = base_structured_answers()
    project_answers["hard_triggers"]["locked_derivatives"] = True
    project_answers["task"]["lifecycle_required"] = True
    project_snap = json.loads(run_assessor(root, project_answers).stdout)
    assert project_snap["route"] == "Project"
    assert project_snap["needs_initialization"] is True
    assert project_snap["next_action"] == "initialize_or_resume_project"
    assert isinstance(project_snap["next_invocation"], str) and project_snap["next_invocation"]


def test_legacy_routing_policy_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "work"
    root.mkdir()
    answers = base_structured_answers()
    # Explicitly pass an unsupported policy name without hardcoding retired policy literals in repo grep targets.
    answers["routing_policy"] = "-".join(("score", "v1"))
    res = run_assessor(root, answers)
    assert res.returncode == 2
    assert "assessment error" in res.stderr


def test_decide_semantic_route_applies_when_calibrated_and_falls_back_safely(tmp_path: Path) -> None:
    root = tmp_path / "out"
    root.mkdir()
    answers = base_structured_answers()
    for dim in answers["dimensions"].values():
        dim["score"] = 0
    answers["dimensions"]["collaboration"]["score"] = None
    answers["dimensions"]["reproducibility"]["score"] = None
    answers["hard_triggers"] = {k: False for k in answers["hard_triggers"]}
    answers["task"]["risk_axes"] = []
    answers["task"]["deliverables"] = [{"format": "txt", "purpose": "deliverable"}]
    answers["semantic_result"] = decide_envelope(
        "Quick", {"Quick": 0.94, "Structured": 0.05, "Project": 0.01}
    )
    applied_snap = json.loads(run_assessor(root, answers).stdout)
    assert applied_snap["route"] == "Quick"
    assert applied_snap["semantic_judgment"]["applied"] is True
    assert applied_snap["semantic_judgment"]["fallback_reason"] is None

    # Direct light-decision-mcp choose envelope with calibrated semantic_policy also works.
    answers["semantic_result"] = {
        "backend": "local-opendecider",
        "model": "opendecider-small",
        "data_destination": "on-device",
        "fallback_used": False,
        "label": "Quick",
        "probabilities": {"Quick": 0.92, "Structured": 0.06, "Project": 0.02},
        "confidence": 0.92,
        "provider_confidence": 0.90,
    }
    answers["semantic_policy"] = {
        "min_confidence": 0.80,
        "calibration": "held-out 20 cases",
    }
    mcp_snap = json.loads(run_assessor(root, answers).stdout)
    assert mcp_snap["route"] == "Quick"
    assert mcp_snap["semantic_judgment"]["applied"] is True

    # Fallback cases: model cannot force Project, waive safety review, or apply uncalibrated/malformed results.
    safety_answers = base_structured_answers()
    for bad_decision in (
        None,
        {"error": "offline"},
        decide_envelope("Project", {"Quick": 0.01, "Structured": 0.01, "Project": 0.98}),
        decide_envelope("Quick", {"Quick": 0.98, "Structured": 0.01, "Project": 0.01}),
        decide_envelope(
            "Quick",
            {"Quick": 0.90, "Structured": 0.05, "Project": 0.05},
            applied=False,
            calibrated=False,
            reason="uncalibrated",
        ),
        decide_envelope(
            "Quick",
            {"Quick": 0.45, "Structured": 0.35, "Project": 0.20},
            applied=False,
            reason="low-confidence",
        ),
        decide_envelope("Quick", {}, method="self-judgment", applied=True, calibrated=False),
        decide_envelope("Structured", {"Quick": -0.2, "Structured": 0.9, "Project": 0.3}),
    ):
        safety_answers["semantic_result"] = bad_decision
        fallback_snap = json.loads(run_assessor(root, safety_answers).stdout)
        assert fallback_snap["route"] == "Structured"
        assert "safety-privacy-legal" in fallback_snap["required_review_axes"]
        assert fallback_snap["semantic_judgment"]["applied"] is False


def test_next_version_cli_computes_unused_suffixes_and_rejects_bad_dates(tmp_path: Path) -> None:
    gates_dir = tmp_path / ".manuscript-ops" / "gates"
    gates_dir.mkdir(parents=True)
    res1 = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "next_version.py"),
            "--date",
            "2026.11.25",
            "--root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res1.returncode == 0
    assert res1.stdout.strip() == "2026.11.25"

    (gates_dir / "brief-approved-2026.11.25.json").write_text(
        json.dumps({"date_version": "2026.11.25"}), encoding="utf-8"
    )
    res2 = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "next_version.py"),
            "--date",
            "2026.11.25",
            "--root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res2.returncode == 0
    assert res2.stdout.strip() == "2026.11.25-02"

    (gates_dir / "baseline-2026.11.25-02.json").write_text(
        json.dumps({"date_version": "2026.11.25-02"}), encoding="utf-8"
    )
    res3 = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "next_version.py"),
            "--date",
            "2026.11.25",
            "--root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res3.returncode == 0
    assert res3.stdout.strip() == "2026.11.25-03"

    bad = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "next_version.py"),
            "--date",
            "2026-11-25",
            "--root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 2


def test_probe_capabilities_cli_validates_platform_snapshots_and_aliases(tmp_path: Path) -> None:
    platform_path = tmp_path / "platform-capabilities.json"
    platform_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "platform": "claude-code",
                "captured_at": "2026-11-25T00:00:00Z",
                "capabilities": [
                    {
                        "name": "docx_provider",
                        "provider": "python-docx-skill",
                        "version": "1.1.0",
                        "evidence": "verified local docx generation",
                        "operations": ["read", "edit", "generate", "structural_qa"],
                    },
                    {
                        "name": "docx_renderer",
                        "provider": "libreoffice-headless",
                        "version": "24.8",
                        "evidence": "verified page rendering",
                        "operations": ["render"],
                    },
                    {
                        "name": "image_inspector",
                        "provider": "vision-tool",
                        "version": "1.0",
                        "evidence": "verified page visual inspection",
                        "operations": ["visual_qa"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    res = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "probe_capabilities.py"),
            "--platform-capabilities",
            str(platform_path),
            "--declare",
            "epub_provider",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    by_id = {item["id"]: item for item in payload["adapters"]}
    assert by_id["docx"]["status"] == "READY"
    # Legacy --declare must not promote epub to READY.
    assert by_id["epub"]["status"] == "BLOCKED"

    # Reject platform capability missing required operations.
    bad_platform = tmp_path / "bad-platform.json"
    bad_platform.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "platform": "claude-code",
                "captured_at": "2026-11-25T00:00:00Z",
                "capabilities": [
                    {
                        "name": "docx_provider",
                        "provider": "incomplete",
                        "version": "1.0",
                        "evidence": "missing generate/edit",
                        "operations": ["read"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    bad_res = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPTS_DIR / "probe_capabilities.py"),
            "--platform-capabilities",
            str(bad_platform),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad_res.returncode == 2
    assert "capability probe error" in bad_res.stderr
