from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_evidence_paths", ROOT / "scripts" / "check_evidence_paths.py")
PATHS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATHS)

REPO = "/Users/ana/work/skills"
HOME = "/Users/ana"


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                   env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
                        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "PATH": "/usr/bin:/bin"})


class RedactTests(unittest.TestCase):
    def test_repo_tmp_and_home_paths_become_placeholders(self) -> None:
        text = (f"ran {REPO}/skills/x/SKILL.md in /private/tmp/claude-501/abc/proj and "
                f"/var/folders/zz/T/tmp1/out with {HOME}/.config/light/policy.json")
        self.assertEqual(PATHS.redact(text, REPO, HOME),
                         "ran <repo>/skills/x/SKILL.md in <tmp>/abc/proj and "
                         "<tmp>/tmp1/out with ~/.config/light/policy.json")

    def test_redaction_is_idempotent_and_leaves_other_text(self) -> None:
        once = PATHS.redact(f"{REPO}/a and https://example.com/Users/x", REPO, HOME)
        self.assertEqual(PATHS.redact(once, REPO, HOME), once)
        self.assertIn("https://example.com/Users/x", once)

    def test_key_shaped_values_lose_their_value(self) -> None:
        fake = "sk-" + "A1b2" * 6
        self.assertEqual(PATHS.redact(f"key {fake} and Bearer {'x' * 20}", REPO, HOME),
                         "key sk-<redacted> and Bearer <redacted>")

    def test_findings_name_each_personal_path(self) -> None:
        self.assertEqual(PATHS.personal_paths("see <repo>/a and ~/b"), [])
        self.assertEqual(PATHS.personal_paths("see /Users/ana/b\nand /home/bo/c"), ["/Users/ana/", "/home/bo/"])
        self.assertEqual(PATHS.personal_paths("left in /private/tmp/claude-501/x"), ["/private/tmp/"])
        self.assertEqual(PATHS.personal_paths("CI ran in /home/runner/work/skills"), [])


class BoundaryTests(unittest.TestCase):
    def test_a_longer_sibling_path_is_not_the_repo_or_home(self) -> None:
        # Only the whole segment matches; the sibling's own name stays visible to the check.
        out = PATHS.redact(f"{REPO}-old/x and {REPO}X and /Users/ana-b/x and /Users/ana.b/x", REPO, HOME)
        self.assertEqual(out, "~/work/skills-old/x and ~/work/skillsX and /Users/ana-b/x and /Users/ana.b/x")
        self.assertEqual(PATHS.personal_paths(out), ["/Users/ana-b/", "/Users/ana.b/"])

    def test_tmp_inside_a_url_or_word_is_left_alone(self) -> None:
        for text in ("https://example.com/tmp/x", "a/tmp/b", "/tmp.txt", "/tmp-foo/x"):
            with self.subTest(text=text):
                self.assertEqual(PATHS.redact(text, REPO, HOME), text)
        self.assertEqual(PATHS.redact("in /tmp/x", REPO, HOME), "in <tmp>/x")

    def test_every_var_folders_directory_is_redacted(self) -> None:
        for sub in ("T", "C", "X"):
            with self.subTest(sub=sub):
                out = PATHS.redact(f"/var/folders/ab/cdef123/{sub}/y", REPO, HOME)
                self.assertEqual(out, "<tmp>/y")
                self.assertEqual(PATHS.personal_paths(out), [])

    def test_personal_paths_in_other_spellings_are_found(self) -> None:
        cases = {
            "file:///Users/ana/x": "/Users/ana/",
            "PATH=/usr/bin:/Users/ana/bin": "/Users/ana/",
            "x:/Users/ana/x": "x:/Users/ana/",  # read as a drive letter; still found
            "C:/Users/ana/x": "C:/Users/ana/",
            "C:\\Users\\ana\\x": "C:/Users/ana/",
            '"C:\\\\Users\\\\ana\\\\x"': "C:/Users/ana/",
            '"\\/Users\\/ana\\/x"': "/Users/ana/",
            "/mnt/c/Users/ana/x": "/mnt/c/Users/ana/",
            "**/Users/ana/x**": "/Users/ana/",
            "*/home/bo/x*": "/home/bo/",
            "_/Users/ana/x_": "/Users/ana/",
            "\u201c/Users/ana/x\u201d": "/Users/ana/",
            "cd a;/Users/ana/x": "/Users/ana/",
            "!/Users/ana/x #/Users/ana/x $/Users/ana/x @/Users/ana/x": "/Users/ana/",
        }
        for text, prefix in cases.items():
            with self.subTest(text=text):
                self.assertEqual(PATHS.personal_paths(text), [prefix])

    def test_a_bearer_token_with_base64_characters_is_fully_redacted(self) -> None:
        out = PATHS.redact("Authorization: Bearer eyJhbGciOi.payload.sig/+=abcdefg end", REPO, HOME)
        self.assertEqual(out, "Authorization: Bearer <redacted> end")


class CheckTests(unittest.TestCase):
    def test_only_evidence_added_since_the_baseline_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q")
            old = root / "docs/evidence/old.md"
            old.parent.mkdir(parents=True)
            old.write_text("legacy /Users/ana/x\n", encoding="utf-8")
            git(root, "add", "-A"); git(root, "commit", "-qm", "base"); git(root, "tag", "v1")
            old.write_text("legacy /Users/ana/x edited\n", encoding="utf-8")
            (root / "docs/evidence/new-clean.md").write_text("ran in <repo>\n", encoding="utf-8")
            self.assertEqual(PATHS.check(root, "v1"), [])
            (root / "docs/evidence/sub").mkdir()
            (root / "docs/evidence/sub/new.md").write_text("ran in /Users/ana/work\n", encoding="utf-8")
            git(root, "add", "-A"); git(root, "commit", "-qm", "add")
            (root / "docs/evidence/untracked.json").write_text('{"p": "/var/folders/aa/T/x"}', encoding="utf-8")
            (root / "docs/evidence/key.md").write_text("token sk-" + "Z9y8" * 5 + "\n", encoding="utf-8")
            self.assertEqual(PATHS.check(root, "v1"), [
                "docs/evidence/key.md: key-shaped value",
                "docs/evidence/sub/new.md: /Users/ana/",
                "docs/evidence/untracked.json: /var/folders/",
            ])

    def test_renamed_staged_and_non_utf8_files_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q")
            old = root / "docs/evidence/old.md"
            old.parent.mkdir(parents=True)
            old.write_text("legacy record " * 20 + "\n", encoding="utf-8")
            git(root, "add", "-A"); git(root, "commit", "-qm", "base"); git(root, "tag", "v1")
            git(root, "mv", "docs/evidence/old.md", "docs/evidence/renamed.md")
            (root / "docs/evidence/renamed.md").write_text("legacy record " * 20 + "\n/Users/ana/x\n", encoding="utf-8")
            git(root, "commit", "-qam", "rename")
            (root / "docs/evidence/staged.md").write_text("/Users/bo/x\n", encoding="utf-8")
            git(root, "add", "docs/evidence/staged.md")
            (root / "docs/evidence/latin.md").write_bytes("caf\xe9 /Users/cy/x\n".encode("latin-1"))
            (root / "docs/evidence/image.png").write_bytes(b"\x89PNG\0 /Users/dd/x")
            self.assertEqual(PATHS.check(root, "v1"), [
                "docs/evidence/latin.md: /Users/cy/",
                "docs/evidence/renamed.md: /Users/ana/",
                "docs/evidence/staged.md: /Users/bo/",
            ])

    def test_exit_codes(self) -> None:
        script = str(ROOT / "scripts" / "check_evidence_paths.py")
        run = lambda *args: subprocess.run([sys.executable, script, *args], capture_output=True, text=True).returncode
        self.assertEqual(run("--check", "--since", "no-such-tag-anywhere"), 2)
        self.assertEqual(run("--check", "--since"), 2)
        self.assertEqual(run(), 2)
        with tempfile.TemporaryDirectory() as tmp:
            dirty = Path(tmp) / "e.md"
            dirty.write_text("seen at /Users/zz/x\n", encoding="utf-8")
            self.assertEqual(run("--apply", str(dirty)), 1)  # a personal path --apply cannot map is reported
            clean = Path(tmp) / "c.md"
            clean.write_text("ran in " + os.path.expanduser("~") + "/x\n", encoding="utf-8")
            self.assertEqual(run("--apply", str(clean)), 0)
            self.assertEqual(clean.read_text(encoding="utf-8"), "ran in ~/x\n")

    def test_a_missing_git_is_a_usage_error(self) -> None:
        from unittest import mock
        with mock.patch.object(PATHS.subprocess, "run", side_effect=FileNotFoundError("git")):
            self.assertEqual(PATHS.main(["--check"]), 2)

    def test_the_repository_evidence_is_clean(self) -> None:
        try:
            problems = PATHS.check(ROOT, PATHS.BASELINE)
        except subprocess.CalledProcessError as error:
            self.fail(f"git could not compare with {PATHS.BASELINE} (fetch tags?): {error.stderr}")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
