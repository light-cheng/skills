"""Task-level routing regressions through the portable assessor CLI."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSESSOR = ROOT / "skills/writing/manuscript-ops/scripts/assess_project.py"


def short_task() -> dict:
    return {
        "dimensions": {
            name: {"score": score, "evidence": ["bounded, supplied task"]}
            for name, score in {
                "scale": 0, "source_complexity": 1, "risk": 2,
                "output_complexity": 1, "collaboration": 1, "reproducibility": 1,
            }.items()
        },
        "hard_triggers": {
            "explicit_project": False, "cross_session": False,
            "large_volume": False, "high_risk_facts": True,
            "locked_derivatives": False, "reproducible_multi_format": False,
            "independent_multi_thread_acceptance": True,
        },
        "task": {
            "scope": "bounded", "operation": "rewrite",
            "risk_axes": ["safety-privacy-legal"],
            "deliverables": [{"format": "docx", "purpose": "deliverable"},
                             {"format": "pdf", "purpose": "qa"}],
            "lifecycle_required": False,
            "evidence": ["one short memo; existing technical meaning is confirmed"],
        },
    }



def route_judgment(answer, probabilities, applied=True, reason="none", method="typed-decision"):
    """A light-decide normalized result for question manuscript-ops/route."""
    return {
        "question_id": "manuscript-ops/route", "question": "Which route fits this manuscript task?",
        "kind": "choice", "options": list(probabilities), "answer": answer, "score": None,
        "probabilities": probabilities, "confidence": probabilities.get(answer), "provider_confidence": None,
        "method": method, "data": "on-device", "backend": "fixture", "calibrated": applied,
        "applied": applied, "fallback_reason": reason, "final": answer if applied else "Structured",
    }

class ManuscriptRoutingTests(unittest.TestCase):
    def assess(self, root: Path, answers: dict) -> dict:
        answer_path = root.parent / "answers.json"
        answer_path.write_text(json.dumps(answers), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-B", str(ASSESSOR), "--root", str(root),
             "--answers", str(answer_path)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_short_safety_rewrite_needs_review_not_project_bootstrap(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "output"
            root.mkdir()
            snapshot = self.assess(root, short_task())
            self.assertEqual(snapshot["route"], "Structured")
            self.assertIn("safety-privacy-legal", snapshot["required_review_axes"])
            self.assertFalse(snapshot["needs_initialization"])
            self.assertIsNone(snapshot["next_invocation"])
            self.assertFalse((root / ".manuscript-ops").exists())
            self.assertFalse((root / "AGENTS.md").exists())

    def test_workspace_size_does_not_change_the_same_bounded_task(self):
        with tempfile.TemporaryDirectory() as directory:
            small = Path(directory) / "small"
            large = Path(directory) / "large"
            small.mkdir()
            large.mkdir()
            for index in range(65):
                (large / f"unrelated-{index}.md").write_text("other work")
            answers = short_task()
            del answers["dimensions"]["scale"]
            first = self.assess(small, answers)
            second = self.assess(large, answers)
            self.assertEqual(first["route"], "Structured")
            self.assertEqual(second["route"], first["route"])
            self.assertEqual(second["required_review_axes"], first["required_review_axes"])

    def test_old_snapshot_keeps_its_original_project_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            answers = short_task()
            answers["routing_policy"] = "score-v1"
            snapshot = self.assess(root, answers)
            self.assertEqual(snapshot["route"], "Project")
            snapshot.pop("routing_policy")  # Actual old snapshots predate this field.
            sys.path.insert(0, str(ASSESSOR.parent))
            validator = runpy.run_path(str(ASSESSOR.parent / "validate_state.py"))
            report = validator["Report"](root)
            validator["validate_routing"](
                snapshot, {"route": "Project", "snapshot_max_age_hours": 24},
                report, datetime.now(timezone.utc),
            )
            self.assertEqual(report.errors, [])

    def test_optional_model_can_resolve_noncritical_unknowns_without_granting_a_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "output"
            root.mkdir()
            answers = short_task()
            for dimension in answers["dimensions"].values():
                dimension["score"] = 0
            answers["dimensions"]["collaboration"]["score"] = None
            answers["dimensions"]["reproducibility"]["score"] = None
            answers["hard_triggers"] = {name: False for name in answers["hard_triggers"]}
            answers["task"]["risk_axes"] = []
            answers["task"]["deliverables"] = [{"format": "txt", "purpose": "deliverable"}]
            answers["semantic_result"] = route_judgment("Quick", {"Quick": 0.95, "Structured": 0.04, "Project": 0.01})
            resolved = self.assess(root, answers)
            self.assertEqual(resolved["route"], "Quick")
            self.assertTrue(resolved["semantic_judgment"]["applied"])
            self.assertEqual(resolved["semantic_judgment"]["model"], "fixture")
            self.assertFalse(resolved["needs_initialization"])

            # An older snapshot's decide payload and policy still replay unchanged.
            answers["semantic_policy"] = {"min_confidence": 0.8, "calibration_reference": "fixture-policy"}
            answers["semantic_result"] = {
                "model": "fixture", "answers": {"route": {
                    "choice": "Quick", "confidence": 0.95,
                    "probabilities": {"Quick": 0.95, "Structured": 0.04, "Project": 0.01},
                }},
            }
            self.assertTrue(self.assess(root, answers)["semantic_judgment"]["applied"])

    def test_new_output_directory_is_not_a_missing_project_prerequisite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "new-output"
            snapshot = self.assess(root, short_task())
            self.assertEqual(snapshot["route"], "Structured")
            self.assertFalse(snapshot["repository_evidence"]["root_exists"])
            self.assertFalse(root.exists())

    def test_frozen_chinese_cases_keep_the_expected_routes_and_review(self):
        cases = json.loads((ROOT / "tests/fixtures/manuscript_routing_cases.json").read_text())["cases"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "output"
            root.mkdir()
            for case in cases:
                with self.subTest(case=case["id"]):
                    result = self.assess(root, case["answers"])
                    self.assertEqual(result["route"], case["expected_route"])
                    self.assertEqual(result["needs_initialization"], case["expected_route"] == "Project")
                    self.assertEqual(result["required_review_axes"], sorted(case["expected_review_axes"]))
                    if case["answers"]["dimensions"]["risk"]["score"] == 2:
                        self.assertIn("safety-privacy-legal", result["required_review_axes"])
                    if case["answers"]["task"]["image_count"]:
                        self.assertIn("images", result["required_review_axes"])

    def test_damaged_review_axis_returns_a_field_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = self.assess(root, short_task())
            sys.path.insert(0, str(ASSESSOR.parent))
            validator = runpy.run_path(str(ASSESSOR.parent / "validate_state.py"))
            for axes in ([{}], [], ["intent-structure"]):
                with self.subTest(axes=axes):
                    snapshot["required_review_axes"] = axes
                    report = validator["Report"](root)
                    validator["validate_routing"](snapshot, {"route": "Structured", "snapshot_max_age_hours": 24},
                                                    report, datetime.now(timezone.utc))
                    self.assertIn("ROUTING_REVIEW_AXES", {error["code"] for error in report.errors})

    def test_model_failure_or_contradiction_never_waives_safety_or_adds_initialization(self):
        decisions = (
            None, {"error": "unavailable"},
            route_judgment("Project", {"Quick": 0.005, "Structured": 0.005, "Project": 0.99}),
            route_judgment("Quick", {"Quick": 0.99, "Structured": 0.005, "Project": 0.005}),
            route_judgment("Quick", {"Quick": 0.9, "Structured": 0.05, "Project": 0.05}, applied=False, reason="uncalibrated"),
            route_judgment("Quick", {"Quick": 0.4, "Structured": 0.3, "Project": 0.3}, applied=False, reason="low-confidence"),
            route_judgment("Structured", {"Quick": -1, "Structured": 0.99, "Project": 1.01}),
            route_judgment("Quick", {}, method="self-judgment"),
            route_judgment("Quick", {"Quick": 0.99, "Structured": 0.005, "Project": 0.005}) | {"calibrated": False},
            {**route_judgment("Quick", {"Quick": 0.99, "Structured": 0.005, "Project": 0.005}), "options": ["Quick"], "method": "self-judgment"},
            {"answers": {"route": {"choice": "Quick", "confidence": 0.99,
                "probabilities": {"Quick": 0.99, "Structured": 0.005, "Project": 0.005}}}},
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "output"
            root.mkdir()
            for decision in decisions:
                with self.subTest(decision=decision):
                    answers = short_task()
                    answers["semantic_result"] = decision
                    answers["semantic_policy"] = {"min_confidence": 0.8, "calibration_reference": "fixture-policy"}
                    result = self.assess(root, answers)
                    self.assertEqual(result["route"], "Structured")
                    self.assertFalse(result["needs_initialization"])
                    self.assertIn("safety-privacy-legal", result["required_review_axes"])
                    self.assertFalse(result["semantic_judgment"]["applied"])

    def test_irrelevant_unknown_does_not_escalate_a_known_low_risk_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "output"
            root.mkdir()
            answers = short_task()
            for value in answers["dimensions"].values(): value["score"] = 0
            answers["hard_triggers"] = {key: False for key in answers["hard_triggers"]}
            answers["task"]["risk_axes"] = []
            answers["task"]["deliverables"] = [{"format": "markdown", "purpose": "deliverable"}]
            answers["unknowns"] = ["optional stylistic preference"]
            self.assertEqual(self.assess(root, answers)["route"], "Quick")


if __name__ == "__main__":
    unittest.main()
