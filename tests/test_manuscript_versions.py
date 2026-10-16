"""Version checks must follow the selected route and declared backend."""

from __future__ import annotations

import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/writing/manuscript-ops/scripts"
sys.path.insert(0, str(SCRIPTS))
VALIDATOR = runpy.run_path(str(SCRIPTS / "validate_state.py"))


class ManuscriptVersionTests(unittest.TestCase):
    def test_structured_task_does_not_require_a_jj_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = VALIDATOR["Report"](root)
            VALIDATOR["validate_version_control"](
                {"route": "Structured", "version_control": {"system": "jj"}}, [], report,
            )
            self.assertEqual(report.errors, [])
            self.assertIn("VCS_NOT_APPLICABLE", {c["code"] for c in report.checks})
            self.assertFalse((root / ".jj").exists())

    def test_git_project_reports_the_actual_missing_gate_guarantee(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
            report = VALIDATOR["Report"](root)
            VALIDATOR["validate_version_control"](
                {"route": "Project", "version_control": {"system": "git"}}, [], report,
            )
            codes = {item["code"] for item in report.errors}
            self.assertIn("VCS_GATES_UNSUPPORTED", codes)
            self.assertNotIn("JJ_MISSING", codes)
            self.assertEqual(report.status, "BLOCKED")


if __name__ == "__main__":
    unittest.main()
