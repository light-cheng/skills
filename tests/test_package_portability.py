"""Installed packages must not carry paths from the author's machine."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_PATH = re.compile(r"/Users/[^/\s]+/|/home/[^/\s]+/|[A-Z]:\\Users\\")


class PackagePortabilityTest(unittest.TestCase):
    def test_package_files_contain_no_local_home_paths(self) -> None:
        offenders = []
        for path in sorted((ROOT / "skills").rglob("*")):
            if not path.is_file() or "tests" in path.relative_to(ROOT).parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if LOCAL_PATH.search(text):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [])

    def test_local_path_pattern_catches_home_directories(self) -> None:
        for sample in ("/Users/alice/project", "/home/bob/x", "C:\\Users\\carol\\x"):
            self.assertRegex(sample, LOCAL_PATH)
        self.assertNotRegex("~/project and <repo>/skills", LOCAL_PATH)


if __name__ == "__main__":
    unittest.main()
