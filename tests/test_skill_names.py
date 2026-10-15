from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_skill_names", ROOT / "scripts" / "check_skill_names.py")
NAMES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NAMES)

PINNED = "a" * 40
RECORD = {
    "sources": [{"repository": "someone/skills", "revision": PINNED, "names": ["tdd", "eli5"]}],
    "accepted": {"eli5": "owner's own rewrite"},
}


def write_skill(root: Path, relative: str, name: str) -> None:
    folder = root / relative
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: x\n---\n\nname: not-this\n", encoding="utf-8")


class SkillNameTests(unittest.TestCase):
    def test_the_collection_has_no_unrecorded_clash(self) -> None:
        record = json.loads(NAMES.RECORD.read_text(encoding="utf-8"))
        public = NAMES.skill_names(ROOT / "skills", "*/*/SKILL.md")
        root = NAMES.private_root(ROOT)
        private = NAMES.skill_names(root / "skills", "**/SKILL.md") if root else None
        self.assertEqual(NAMES.problems(public, record, private), [])

    def test_distinct_names_pass(self) -> None:
        self.assertEqual(NAMES.problems({"eli5", "light-tdd"}, RECORD, {"light-other"}), [])

    def test_a_public_clash_is_reported(self) -> None:
        found = NAMES.problems({"tdd", "eli5", "light-tdd"}, RECORD, set())
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].startswith("tdd: also named in someone/skills@aaaaaaa"))

    def test_a_private_clash_is_reported(self) -> None:
        found = NAMES.problems({"eli5", "light-wizard"}, RECORD, {"light-wizard"})
        self.assertEqual(found, ["light-wizard: also named in private skills-3rdParty; rename it or record the owner's reason under accepted"])

    def test_a_stale_accepted_entry_is_reported(self) -> None:
        found = NAMES.problems({"light-eli5"}, RECORD, set())
        self.assertEqual(found, ["eli5: listed under accepted but no longer clashes; remove the entry"])

    def test_a_private_only_acceptance_is_not_stale_when_private_names_were_not_checked(self) -> None:
        record = {"sources": [], "accepted": {"shared": "owner keeps both"}}
        self.assertEqual(NAMES.problems({"shared"}, record, None), [])
        self.assertEqual(NAMES.problems({"shared"}, record, {"shared"}), [])
        self.assertEqual(len(NAMES.problems({"shared"}, record, set())), 1)

    def test_unpinned_revisions_and_empty_reasons_are_reported(self) -> None:
        record = {"sources": [{"repository": "x/y", "names": []}], "accepted": {"eli5": " "}}
        found = NAMES.problems({"eli5"}, record, set())
        self.assertIn("x/y: revision must be a pinned 40-character commit SHA", found)
        self.assertIn("eli5: accepted without a reason", found)

    def test_names_come_from_frontmatter_and_skip_fixture_copies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            write_skill(skills, "cat/folder-name", "real-name")
            write_skill(skills, "owner/pkg/tests/fixtures/copy", "fixture-copy")
            self.assertEqual(NAMES.skill_names(skills, "*/*/SKILL.md"), {"real-name"})
            self.assertEqual(NAMES.skill_names(skills, "**/SKILL.md"), {"real-name"})

    def test_private_root_is_the_sibling_checkout_or_the_configured_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "skills"
            repo.mkdir()
            with patch.dict(os.environ, {"LIGHT_PRIVATE_SKILLS_ROOT": ""}):
                self.assertIsNone(NAMES.private_root(repo))
                (Path(tmp) / "skills-3rdParty" / "skills").mkdir(parents=True)
                self.assertEqual(NAMES.private_root(repo), Path(tmp) / "skills-3rdParty")
            elsewhere = Path(tmp) / "elsewhere"
            (elsewhere / "skills").mkdir(parents=True)
            with patch.dict(os.environ, {"LIGHT_PRIVATE_SKILLS_ROOT": str(elsewhere)}):
                self.assertEqual(NAMES.private_root(repo), elsewhere)


if __name__ == "__main__":
    unittest.main()
