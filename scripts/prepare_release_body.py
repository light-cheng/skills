#!/usr/bin/env python3
"""Prepare GitHub Release Body.

Transforms local evidence Markdown (e.g. docs/evidence/releases/vX.Y.Z/RELEASE_NOTES.md)
into a GitHub Release-compatible body:
1. Detects sibling relative links (e.g. RELEASE_NOTES.zh-CN.md, RELEASE_MANIFEST.md, RELEASE_RECEIPT.md).
2. Expands them to canonical full GitHub URLs (https://github.com/<repo>/blob/<branch>/docs/evidence/releases/<tag>/<file>),
   preventing 404 errors on GitHub Release pages which evaluate relative links against repository root.
3. Outputs to stdout or an output file suitable for `gh release create --notes-file`.
"""

from __future__ import annotations

import argparse
import re
import sys
import json
import posixpath
from pathlib import Path
from dataclasses import replace
from urllib.parse import urlsplit, urlunsplit

from repo_identity import resolve_repository, validate_repository
from release_context import ReleaseContext, apply_observations, validate_document, document_links
from verify_release_integrity import git_read_text, resolve_commit_sha, check_release_receipt_consistency, run_git

REPO_ROOT = Path(__file__).resolve().parent.parent


def transform_release_notes_for_web(
    text: str,
    tag: str,
    repo: str,
    branch: str = "main",
) -> str:
    """Expand sibling relative links to full repository URLs for GitHub Release rendering."""
    source_dir = f"docs/evidence/releases/{tag}"

    # Match markdown links: [text](target)
    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()

        # Keep absolute URLs, anchors, mailto unchanged
        if re.match(r"^(?:https?://|mailto:|#)", target, re.IGNORECASE):
            return match.group(0)

        parsed = urlsplit(target)
        resolved = posixpath.normpath(parsed.path if parsed.path.startswith("docs/evidence/releases/")
                                     else posixpath.join(source_dir, parsed.path))
        link_ref = "main" if posixpath.basename(resolved).startswith("RELEASE_RECEIPT") else branch
        url = f"https://github.com/{repo}/blob/{link_ref}/{resolved}"
        return f"[{label}]({urlunsplit((*urlsplit(url)[:3], parsed.query, parsed.fragment))})"

    # Pattern: [label](target)
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    return pattern.sub(replace_link, text)


def validate_release_body_links(body: str, tag: str) -> tuple[bool, list[str]]:
    """Validate that a release body does not contain bare relative links that 404 on GitHub Releases."""
    errors: list[str] = []
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for match in pattern.finditer(body):
        label = match.group(1)
        target = match.group(2).strip()

        # Absolute URLs and anchors are safe
        if re.match(r"^(?:https?://|mailto:|#)", target, re.IGNORECASE):
            continue

        # Any relative link without scheme will be evaluated against repository root by GitHub Releases
        errors.append(
            f"Bare relative link detected: [{label}]({target}). "
            f"GitHub Releases evaluates relative links against repository root, causing 404 Not Found. "
            f"Use full URL: https://github.com/<repo>/blob/main/docs/evidence/releases/{tag}/{target.lstrip('./')}"
        )

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a GitHub Release body from release notes.")
    parser.add_argument("--tag", required=True, help="Release tag (e.g. v0.2.4).")
    parser.add_argument("--repo", type=validate_repository, default=None,
                        help="GitHub owner/name for links (default: GITHUB_REPOSITORY, then gh, then the origin remote).")
    parser.add_argument("--branch", default=None, help="Ref for immutable artifact links (default: target tag; Receipts always use main).")
    parser.add_argument("--root", type=Path, default=None, help="Repository root (default: current Git checkout).")
    parser.add_argument("--revision", help="Fixed source tree/ref for release Notes (default: refs/tags/<tag>).")
    parser.add_argument("--release-commit", help="Full release candidate SHA to bind observations.")
    parser.add_argument("--observations", type=Path, help="Recorded CI/install/publication observations, same format as the integrity guard.")
    parser.add_argument("--simulate", action="store_true", help="Allow explicitly marked test-double observations for a local rehearsal.")
    parser.add_argument("--input", default=None, help="Path to input release notes file (default: docs/evidence/releases/<tag>/RELEASE_NOTES.md).")
    parser.add_argument("--output", default=None, help="Path to write transformed release body (default: stdout).")
    parser.add_argument("--validate-only", action="store_true", help="Only validate release body for broken relative links.")
    parser.add_argument("--stage", choices=["prepared", "install_verified", "published", "attested"], default="install_verified",
                        help="Observed lifecycle stage; body semantics are checked in every mode.")

    args = parser.parse_args()

    root = (args.root or Path.cwd()).resolve()
    revision = args.revision or f"refs/tags/{args.tag}"
    relative_input = f"docs/evidence/releases/{args.tag}/RELEASE_NOTES.md"
    input_path = Path(args.input) if args.input else Path(relative_input)
    if args.input:
        if not input_path.is_file():
            print(f"ERROR: Input release notes file not found: {input_path}", file=sys.stderr)
            return 1
        content = input_path.read_text(encoding="utf-8")
    else:
        content = git_read_text(revision, relative_input, cwd=root)
        if content is None:
            print(f"ERROR: Notes missing from fixed source {revision}:{relative_input}; use --revision for a prepared tree.", file=sys.stderr)
            return 1
    candidate = resolve_commit_sha(args.release_commit or revision, cwd=root)
    repo = None
    if not args.validate_only:
        try:
            repo = resolve_repository(args.repo, root)
        except ValueError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
    context = ReleaseContext(args.tag, args.stage, revision=revision, repository=repo)
    if args.observations:
        try:
            observations = json.loads(args.observations.read_text(encoding="utf-8"))
            if not isinstance(observations, dict):
                raise ValueError("observations must be a JSON object")
            context, observation_errors = apply_observations(context, observations, candidate or "UNKNOWN",
                                                              str(args.observations), simulate=args.simulate)
        except (OSError, ValueError) as error:
            observation_errors = [f"[OBSERVATION_ERROR] {error}"]
        if observation_errors:
            for error in observation_errors:
                print(error, file=sys.stderr)
            return 1
    elif args.stage in ("published", "attested") and candidate:
        receipt = check_release_receipt_consistency(args.tag, release_commit=candidate, receipt_revision="HEAD", repo_root=root)
        if receipt.passed:
            context = replace(context, install_verified=True, published=True, evidence_source=f"HEAD:docs/evidence/releases/{args.tag}/RELEASE_RECEIPT.md")
    semantic_errors = validate_document(content, str(input_path), "release-body", context)
    code, paths, _ = run_git(["ls-tree", "-r", "--name-only", revision], cwd=root)
    files = set(paths.splitlines()) if code == 0 else None
    semantic_errors.extend(document_links(content, relative_input, context, files))
    if semantic_errors:
        print("Release body semantic validation FAILED:", file=sys.stderr)
        for error in semantic_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.validate_only:
        valid, errors = validate_release_body_links(content, args.tag)
        if not valid:
            print(f"Validation FAILED for {input_path}:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        print("Validation PASSED: All links are safe.")
        return 0

    transformed = transform_release_notes_for_web(
        text=content,
        tag=args.tag,
        repo=repo,
        branch=args.branch or args.tag,
    )

    valid, errors = validate_release_body_links(transformed, args.tag)
    errors.extend(document_links(transformed, relative_input, context, None))
    valid = valid and not errors
    if not valid:
        print(f"ERROR: Transformed release body still has invalid links:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(transformed, encoding="utf-8")
        print(f"Successfully prepared release body at: {out_path}", file=sys.stderr)
        if context.simulated:
            print("SIMULATED: External verification facts are test doubles; this body is for a local rehearsal.", file=sys.stderr)
    else:
        sys.stdout.write(transformed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
