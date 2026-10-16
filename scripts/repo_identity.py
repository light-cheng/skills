"""Find the GitHub repository a release script works on.

The release scripts never hard-code an owner or name. A repository can be
renamed or moved, and GitHub then only redirects the old name. Resolution order:

1. an explicit ``--repo owner/name`` value;
2. ``GITHUB_REPOSITORY`` (set by GitHub Actions);
3. ``gh repo view`` in the checkout, which follows renames to the current name;
4. the ``origin`` remote URL of the checkout.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Callable, Mapping

REPO_PATTERN = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9_.-]+"
# Any GitHub release page. Documents keep the name that was current when they were
# written, so document checks accept every owner/name; live checks compare exactly.
RELEASE_URL_PATTERN = rf"https://github\.com/{REPO_PATTERN}/releases/tag/"

_REMOTE_FORMS = (
    re.compile(rf"^https://(?:[^@/]+@)?github\.com/({REPO_PATTERN}?)(?:\.git)?/?$"),
    re.compile(rf"^(?:ssh://)?git@github\.com[:/]({REPO_PATTERN}?)(?:\.git)?/?$"),
)

Runner = Callable[..., subprocess.CompletedProcess]


def validate_repository(value: str) -> str:
    """Return ``owner/name`` or raise ValueError."""
    value = value.strip()
    if not re.fullmatch(REPO_PATTERN, value) or value.endswith(".git") or ".." in value:
        raise ValueError(f"repository must look like owner/name, got {value!r}")
    return value


def parse_remote_url(url: str) -> str:
    """Turn a GitHub https or ssh remote URL into ``owner/name``."""
    for form in _REMOTE_FORMS:
        match = form.match(url.strip())
        if match:
            return validate_repository(match.group(1))
    raise ValueError(f"not a GitHub remote URL: {url!r}")


def remote_repository(cwd: Path, *, runner: Runner | None = None) -> str | None:
    """Return ``owner/name`` from the origin remote, or None when it is not GitHub."""
    try:
        proc = (runner or subprocess.run)(["git", "remote", "get-url", "origin"], cwd=cwd,
                                          capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return parse_remote_url(proc.stdout)
    except ValueError:
        return None


def gh_repository(cwd: Path, *, runner: Runner | None = None) -> str | None:
    """Ask the GitHub CLI for the current name; None when gh is missing or offline."""
    try:
        proc = (runner or subprocess.run)(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
                      cwd=cwd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return validate_repository(proc.stdout)
    except ValueError:
        return None


def resolve_repository(explicit: str | None = None, cwd: Path | None = None, *,
                       env: Mapping[str, str] | None = None,
                       runner: Runner | None = None) -> str:
    """Resolve ``owner/name``; raise ValueError when no source names a GitHub repository."""
    if explicit:
        return validate_repository(explicit)
    env = os.environ if env is None else env
    if env.get("GITHUB_REPOSITORY"):
        return validate_repository(env["GITHUB_REPOSITORY"])
    cwd = cwd or Path.cwd()
    found = gh_repository(cwd, runner=runner) or remote_repository(cwd, runner=runner)
    if not found:
        raise ValueError("cannot find the GitHub repository: pass --repo owner/name, "
                         "or run inside a checkout whose origin is on GitHub")
    return found


def release_url(repo: str, tag: str) -> str:
    return f"https://github.com/{validate_repository(repo)}/releases/tag/{tag}"


def is_release_url(url: object, tag: str, repo: str | None = None) -> bool:
    """True for the release page of ``tag``; with ``repo``, only on that repository."""
    if not isinstance(url, str):
        return False
    if repo:
        # GitHub owner and repository names are case-insensitive; the tag is not.
        prefix, expected = url.rsplit("/", 1)[0], release_url(repo, tag).rsplit("/", 1)[0]
        return url.endswith(f"/releases/tag/{tag}") and prefix.casefold() == expected.casefold()
    return bool(re.fullmatch(RELEASE_URL_PATTERN + re.escape(tag), url))
