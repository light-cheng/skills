#!/usr/bin/env python3
"""Check that a merged pull request put the reviewed candidate tree on main.

On the pull-request path the candidate commit gets CI on its branch, then GitHub
merges it. A merge or squash creates a new commit on main. This check passes only
when that main commit carries exactly the candidate's tree and is reachable from
the main branch, so the CI-verified content is what gets tagged.

Example:
    python3 scripts/check_merged_candidate.py \\
      --candidate "$CANDIDATE_SHA" --merged "$MAIN_SHA" --branch origin/main
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def git(root: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        return 1, str(error)
    return proc.returncode, proc.stdout.strip()


def full_commit(root: Path, ref: str) -> str | None:
    code, out = git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return out if code == 0 and len(out) == 40 else None


def check(root: Path, candidate: str, merged: str, branch: str) -> list[str]:
    """Return problems; an empty list means the merged commit carries the candidate."""
    candidate_sha, merged_sha = full_commit(root, candidate), full_commit(root, merged)
    problems = []
    if not candidate_sha:
        problems.append(f"candidate {candidate!r} is not a commit in this checkout")
    if not merged_sha:
        problems.append(f"merged commit {merged!r} is not a commit in this checkout; fetch main first")
    if problems:
        return problems
    branch_sha = full_commit(root, branch)
    if not branch_sha:
        return [f"branch {branch!r} is not available; fetch it first"]
    if git(root, "merge-base", "--is-ancestor", merged_sha, branch_sha)[0] != 0:
        problems.append(f"merged commit {merged_sha} is not on {branch}")
    candidate_tree = git(root, "rev-parse", f"{candidate_sha}^{{tree}}")[1]
    merged_tree = git(root, "rev-parse", f"{merged_sha}^{{tree}}")[1]
    if candidate_tree != merged_tree:
        problems.append(
            f"merged commit tree {merged_tree} differs from candidate tree {candidate_tree}; "
            "main moved or the merge changed content. Update the branch, rerun CI, and merge again")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", required=True, help="The commit that passed pull-request CI.")
    parser.add_argument("--merged", required=True, help="The commit the merge created on main.")
    parser.add_argument("--branch", default="origin/main", help="Branch the merged commit must be on (default: origin/main).")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository checkout (default: current directory).")
    args = parser.parse_args()
    problems = check(args.root, args.candidate, args.merged, args.branch)
    for problem in problems:
        print(f"[BLOCKED] {problem}")
    if problems:
        print("RESULT: BLOCKED — do not tag; the merged commit is not the verified candidate content.")
        return 1
    print(f"RESULT: PASS — {full_commit(args.root, args.merged)} on {args.branch} carries the candidate tree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
