from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ClarifyPublicContractTest(unittest.TestCase):
    def test_wrapper_composes_engine_without_deep_reference(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertFalse((ROOT / "references" / "ROUTING.md").exists())
        self.assertNotIn("../../socratic/references", skill + workflow)

    def test_frontier_is_presented_as_a_round_with_batch_replies(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        combined = skill + workflow
        for token in ("Q1", "Q2", "1B, 2A, 3C", "1B; 2A, but only locally;"):
            self.assertIn(token, combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
