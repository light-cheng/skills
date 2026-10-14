"""Behavior checks for wayfinding ops on the local markdown tracker."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path




class DecisionMapBehaviorTest(unittest.TestCase):
    def test_local_tracker_ops_are_usable(self) -> None:
        # Simulate the tracker ops described in docs/agents/issue-tracker.md
        # using only the file conventions the Skill declares.
        with tempfile.TemporaryDirectory(prefix="decision-map-behave-") as tmp:
            base = Path(tmp) / ".scratch" / "demo-effort"
            issues = base / "issues"
            issues.mkdir(parents=True)

            # create map.md
            map_md = base / "map.md"
            map_md.write_text(
                """## Destination
Demo destination

## Notes
Test notes

## Decisions so far

## Not yet specified

- Fog patch A

## Out of scope

""",
                encoding="utf-8",
            )

            # create two child tickets, 02 blocked by 01
            t01 = issues / "01-first-decision.md"
            t01.write_text("Type: grilling\nStatus: open\nBlocked by:\n\n## Question\nFirst?\n", encoding="utf-8")
            t02 = issues / "02-second-decision.md"
            t02.write_text("Type: research\nStatus: open\nBlocked by: 01\n\n## Question\nSecond?\n", encoding="utf-8")

            # Frontier = unblocked, unclaimed, open => only 01
            def frontier(base: Path):
                front = []
                for p in sorted((base / "issues").glob("*.md")):
                    text = p.read_text(encoding="utf-8")
                    status = "open" if "Status: open" in text else "claimed" if "Status: claimed" in text else "resolved" if "Status: resolved" in text else "unknown"
                    blocked_line = next((l for l in text.splitlines() if l.startswith("Blocked by:")), "Blocked by:")
                    blocked = [s.strip() for s in blocked_line.replace("Blocked by:", "").split(",") if s.strip()]
                    # check if blocked tickets resolved
                    blocked_resolved = True
                    for bn in blocked:
                        # find file with prefix bn
                        bf = next(issues.glob(f"{bn}-*.md"), None)
                        if bf is None or "Status: resolved" not in bf.read_text(encoding="utf-8"):
                            blocked_resolved = False
                    if status == "open" and blocked_resolved:
                        front.append(p.name)
                return front

            self.assertEqual(frontier(base), ["01-first-decision.md"])

            # Claim 01
            text = t01.read_text(encoding="utf-8").replace("Status: open", "Status: claimed")
            t01.write_text(text, encoding="utf-8")
            self.assertEqual(frontier(base), [])

            # Resolve 01
            text = t01.read_text(encoding="utf-8").replace("Status: claimed", "Status: resolved")
            text += "\n## Answer\nDone.\n"
            t01.write_text(text, encoding="utf-8")
            # append to Decisions so far
            map_text = map_md.read_text(encoding="utf-8")
            map_md.write_text(map_text.replace("## Decisions so far", "## Decisions so far\n\n- [First decision](issues/01-first-decision.md) — done."), encoding="utf-8")

            # Now frontier should be 02
            self.assertEqual(frontier(base), ["02-second-decision.md"])
            self.assertIn("First decision", map_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
