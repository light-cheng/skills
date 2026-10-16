#!/usr/bin/env python3
"""Keep personal paths out of new evidence under docs/evidence/.

Evidence added after the baseline release must not name the author's machine.
Before an evidence file is committed, `--apply` rewrites its paths:

- the repository root becomes `<repo>`;
- a temporary directory (`/tmp`, `/private/tmp`, macOS `/var/folders/.../T`) becomes `<tmp>`;
- the home directory becomes `~`.

`--check` fails when an evidence file added since the baseline tag still holds a
personal path or a value shaped like an API key (`sk-...`, `Bearer ...`). Evidence that existed at the baseline is history and is not rewritten.

usage: check_evidence_paths.py --check [--since <tag>]
       check_evidence_paths.py --apply <file>...
Exit 0 when clean, 1 when a personal path is found, 2 on a usage or git error.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "v0.2.7"  # evidence added after this release must be redacted
EVIDENCE = "docs/evidence"

# A path starts anywhere except right after a letter, digit, ".", "~", "%" or "-", so it is
# never the middle of a URL (https://host/Users/x), a word (a/tmp) or a longer name. Markdown
# emphasis, quotes and file:// may come before it.
_START = r"(?<![A-Za-z0-9.~%-])"
# A path segment ends at a separator, space, quote, bracket or punctuation, so /Users/ana-b is not /Users/ana.
_END = r"(?=$|[/\\\s\"'`<>()\[\]{},;:|])"
_SEP = r"(?:\\\\|\\/|\\|/)"  # /, \, \\ (escaped in JSON) or \/ (escaped slash)
_NAME = r"[^/\\\s\"'`<>]+"
_TMP = re.compile(_START + r"(?:(?:/private)?/var/folders/[^/\s]+/[^/\s]+(?:/[A-Z])?|(?:/private)?/tmp(?:/claude-\d+)?)" + _END, re.M)
# /home/runner/ is the GitHub Actions runner, recorded by CI evidence; it names no person.
_PERSONAL = re.compile(
    _START + r"((?:[A-Za-z]:|/mnt/[a-z])?" + _SEP + r"Users" + _SEP + _NAME + _SEP
    + r"|" + _SEP + r"home" + _SEP + r"(?!runner" + _SEP + r")" + _NAME + _SEP
    + r"|(?:/private)?/tmp/|(?:/private)?/var/folders/)", re.M)
# Key-shaped values; evidence keeps the name and drops the value ("sk-<redacted>").
_KEY = re.compile(r"\b(?:sk-(?!<)[A-Za-z0-9_-]{16,}|Bearer (?!<)[A-Za-z0-9._~+/=-]{16,})")


def _replace_path(text: str, path: str, placeholder: str) -> str:
    # file:///Users/ana/x becomes file://~/x: not a valid URL, but it keeps the scheme readable.
    return re.sub(_START + re.escape(path) + _END, placeholder, text, flags=re.M)


def redact(text: str, repo: str, home: str) -> str:
    """Replace the repository root, temporary directories, the home directory and key-shaped values."""
    for root in sorted({repo, os.path.realpath(repo)}, key=len, reverse=True):
        text = _replace_path(text, root, "<repo>")
    text = _TMP.sub("<tmp>", text)
    for path in sorted({home, os.path.realpath(home)}, key=len, reverse=True):
        text = _replace_path(text, path, "~")
    return _KEY.sub(lambda m: "sk-<redacted>" if m.group(0).startswith("sk-") else "Bearer <redacted>", text)


def personal_paths(text: str) -> list[str]:
    """Each distinct personal path prefix, separators shown as "/", in order of first appearance."""
    found: list[str] = []
    for match in _PERSONAL.finditer(text):
        prefix = re.sub(_SEP, "/", match.group(1))
        prefix = re.sub(r"^/private(?=/var/folders/|/tmp/)", "", prefix) if prefix.startswith("/private/var") else prefix
        if prefix not in found:
            found.append(prefix)
    return found


def _git(root: Path, *args: str) -> list[str]:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    return [line for line in result.stdout.splitlines() if line]


def added_evidence(root: Path, since: str) -> list[str]:
    """Evidence files that did not exist at `since`: committed, staged or untracked.

    Renames count as added, so moving an old file does not exempt new content.
    """
    added = set(_git(root, "diff", "--no-renames", "--name-only", "--diff-filter=A", since, "--", EVIDENCE))
    added |= set(_git(root, "ls-files", "--others", "--exclude-standard", "--", EVIDENCE))
    return sorted(path for path in added if (root / path).is_file())


def check(root: Path, since: str) -> list[str]:
    problems = []
    for relative in added_evidence(root, since):
        data = (root / relative).read_bytes()
        if b"\0" in data:
            continue  # images and other binary evidence carry no path text
        text = data.decode("utf-8", errors="surrogateescape")
        problems += [f"{relative}: {prefix}" for prefix in personal_paths(text)]
        if _KEY.search(text):
            problems.append(f"{relative}: key-shaped value")
    return problems


def main(argv: list[str]) -> int:
    if argv[:1] == ["--apply"] and len(argv) > 1:
        home = os.path.expanduser("~")
        # Also the unresolved repository path, when it was reached through a symlink.
        repos = {str(Path(__file__).absolute().parents[1]), os.environ.get("PWD", "")}
        repos = [path for path in repos if path and Path(path).resolve() == ROOT]
        left = 0
        for name in argv[1:]:
            path = Path(name)
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
            redacted = text
            for repo in repos:
                redacted = _replace_path(redacted, repo, "<repo>")
            redacted = redact(redacted, str(ROOT), home)
            if redacted != text:
                path.write_text(redacted, encoding="utf-8", errors="surrogateescape")
                print(f"redacted {name}")
            for prefix in personal_paths(redacted):
                print(f"still present in {name}: {prefix}")
                left += 1
        return 1 if left else 0
    if argv[:1] == ["--check"] and len(argv) in (1, 3) and (len(argv) == 1 or argv[1] == "--since"):
        since = argv[2] if len(argv) == 3 else BASELINE
        try:
            problems = check(ROOT, since)
        except subprocess.CalledProcessError as error:
            print(f"git failed: {error.stderr.strip()} (are tags fetched?)", file=sys.stderr)
            return 2
        except OSError as error:
            print(f"cannot run git: {error}", file=sys.stderr)
            return 2
        for problem in problems:
            print(f"finding: {problem}")
        print("RESULT: FAIL" if problems else f"RESULT: PASS — evidence added since {since} has no personal paths or key-shaped values")
        return 1 if problems else 0
    print(__doc__.split("usage:", 1)[1].split("Exit", 1)[0].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
