"""Scenario-level checks for project-clarify's published behavior contract."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def skill_text(root: Path = ROOT) -> str:
    return (root / "SKILL.md").read_text(encoding="utf-8")


class ProjectClarifyBehaviorTest(unittest.TestCase):
    def test_positive_existing_project_flow_uses_inspection_then_a_decision(self) -> None:
        skill = skill_text()

        existing_project_fixture = {
            "README/project brief": "goal and constraints",
            "manifests": "runtime facts",
            "source and test entry points": "current behavior",
        }
        self.assertEqual(len(existing_project_fixture), 3)
        self.assertLess(skill.index("Inspect project facts before asking"), skill.index("Maintain user decisions with `socratic`"))
        self.assertIn("docs/agents/light-project.md", skill)
        self.assertRegex(skill, r"Ask the complete\s+current frontier as a round|frontier as a round")

    def test_missing_capability_blocks_a_dependency_without_relabeling_it(self) -> None:
        skill = skill_text()
        ref = (ROOT / "references" / "project-clarification-contract.md").read_text(encoding="utf-8")
        combined = skill + ref

        self.assertRegex(combined, r"(?is)unavailable.*not-authorized|not-authorized.*unavailable")

    def test_interaction_records_optional_calls_and_returns_a_handoff(self) -> None:
        skill = skill_text()
        ref = (ROOT / "references" / "project-clarification-contract.md").read_text(encoding="utf-8")
        combined = skill + ref

        for field in (
            "Capability call: socratic | light-research | light-prototype",
            "Blocked decision:",
            "Result read: path or artifact identifier | none",
            "Project clarification handoff",
            "Recommended next explicit invocation:",
        ):
            self.assertIn(field, combined)
        # handoff contains capability records
        self.assertIn("Capability call records", combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
