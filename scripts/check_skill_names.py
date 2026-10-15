#!/usr/bin/env python3
"""Check that Light package names do not reuse another collection's Skill names.

Sources: docs/reference/external-skill-names.json (public collections, pinned) and,
when present, the private skills-3rdParty checkout next to this repository or the
path in LIGHT_PRIVATE_SKILLS_ROOT. A clash is allowed only when the record lists the
name under "accepted" with the owner's reason. An accepted name that no longer
clashes is reported too, so the record stays honest.

Exit 0 when clean, 1 when a problem is found.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "reference" / "external-skill-names.json"
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
_NAME = re.compile(r"(?m)^name:\s*['\"]?([A-Za-z0-9._-]+)")
_NOT_PACKAGES = {"tests", "fixtures", "templates", "examples"}
_REVISION = re.compile(r"^[0-9a-f]{40}$")


def skill_names(skills_dir: Path, pattern: str) -> set[str]:
    """Frontmatter names of every SKILL.md under skills_dir matching the glob pattern.

    Copies inside tests, fixtures, templates or examples are not packages.
    """
    names = set()
    for skill in skills_dir.glob(pattern):
        if _NOT_PACKAGES & set(skill.relative_to(skills_dir).parts[:-1]):
            continue
        front = _FRONTMATTER.search(skill.read_text(encoding="utf-8", errors="replace"))
        match = _NAME.search(front.group(1)) if front else None
        names.add(match.group(1) if match else skill.parent.name)
    return names


def private_root(repo: Path) -> Path | None:
    configured = os.environ.get("LIGHT_PRIVATE_SKILLS_ROOT", "").strip()
    candidate = Path(configured) if configured else repo.parent / "skills-3rdParty"
    return candidate if (candidate / "skills").is_dir() else None


def problems(public: set[str], record: dict, private: set[str] | None) -> list[str]:
    """Clashes, malformed record entries and stale acceptances. private=None means not checked."""
    found = []
    external: dict[str, list[str]] = {}
    for source in record.get("sources", []):
        repository, revision = source.get("repository", "?"), str(source.get("revision", ""))
        if not _REVISION.match(revision):
            found.append(f"{repository}: revision must be a pinned 40-character commit SHA")
        for name in source.get("names", []):
            external.setdefault(name, []).append(f"{repository}@{revision[:7]}")
    public_sources = set(external)
    for name in private or ():
        external.setdefault(name, []).append("private skills-3rdParty")
    accepted = record.get("accepted", {})
    for name, reason in sorted(accepted.items()):
        if not str(reason).strip():
            found.append(f"{name}: accepted without a reason")
    for name in sorted(public & set(external)):
        if name not in accepted:
            found.append(f"{name}: also named in {', '.join(external[name])}; rename it or record the owner's reason under accepted")
    for name in sorted(set(accepted) - (public & set(external))):
        # Without the private checkout, a public name may still clash with a private package.
        if private is None and name in public and name not in public_sources:
            continue
        found.append(f"{name}: listed under accepted but no longer clashes; remove the entry")
    return found


def main() -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    public = skill_names(ROOT / "skills", "*/*/SKILL.md")
    root = private_root(ROOT)
    private = skill_names(root / "skills", "**/SKILL.md") if root else None
    found = problems(public, record, private)
    if root is None:
        print("note: no private skills-3rdParty checkout found; private names not checked")
    for line in found:
        print(f"ERROR: {line}")
    print("RESULT:", "FAIL" if found else "PASS", f"({len(public)} public names checked)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
