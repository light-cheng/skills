# Release stage procedures

Run only the stages the owner asked for. Before any remote write, confirm the
exact target and that the owner approved it. Local-only work stops before the
first push. [DOCUMENT-STATE.md](DOCUMENT-STATE.md) says how to record facts; a
passing local rehearsal never proves a production release.

The scripts find the GitHub repository themselves (`--repo owner/name`, then
`GITHUB_REPOSITORY`, then `gh repo view`, then the `origin` remote). Checks of
the published Release compare against that repository and fail when none is
found. In a fork with an `upstream` remote, `gh` may pick upstream: pass
`--repo` there. Use `"$REPO"` from this command in the examples:

```bash
REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
```

## The three release documents

All three live in `docs/evidence/releases/vX.Y.Z/`, each in English and Chinese.

| Document | Written when | Says |
| --- | --- | --- |
| `RELEASE_NOTES` | PREPARED, frozen in the tag | What changed, breaking changes, migration. |
| `RELEASE_MANIFEST` | PREPARED, frozen in the tag | Version, scope, package count, policy status, expected tag `refs/tags/vX.Y.Z^{commit}`, local checks. It does not contain its own commit SHA and does not link to the receipt, which does not exist yet. |
| `RELEASE_RECEIPT` | ATTESTED, first created on main | Observed facts: tag object and commit, CI run, install results, Release URL and time. Never in the candidate or the tag. |

## 1. PREPARED — build the candidate

1. Add the version to `CHANGELOG.md` and `CHANGELOG.zh-CN.md`.
2. Update README, CATALOG, INSTALLATION and MAINTENANCE in both languages as
   snapshots of the target version. Current-stable facts stay on main; history
   at preparation time goes into the Manifest.
3. Write the Manifest and the Notes. Do not create a Receipt.
4. Finish every path and link, then follow the
   [final-artifact checks](CLOSEOUT.md#verify-final-artifacts). Stage the
   candidate and bind the checks to its exact tree:
   ```bash
   git add <candidate-files>
   git diff --exit-code
   VERIFIED_TREE="$(git write-tree)"
   git diff --cached --check
   python3 -m pytest -q
   python3 -m compileall -q skills tests scripts
   python3 scripts/check_public_docs.py --tag vX.Y.Z --stage prepared
   git diff --check
   ```
   `pytest` also runs the `unittest` test classes; a separate
   `python3 -m unittest discover` run repeats the same tests.
5. Confirm the tree did not change, then commit:
   ```bash
   git diff --exit-code
   test "$(git write-tree)" = "$VERIFIED_TREE"
   git commit -m "release: prepare vX.Y.Z"
   CANDIDATE_SHA="$(git rev-parse HEAD)"
   test "$(git rev-parse HEAD^{tree})" = "$VERIFIED_TREE"
   ```
6. On the clean working tree, check the PREPARED state:
   ```bash
   python3 scripts/verify_release_integrity.py \
     --tag vX.Y.Z \
     --release-commit "$CANDIDATE_SHA" \
     --stage prepared --mode current
   ```

## 2. CI_VERIFIED — CI on the exact commit, then main

Use the pull-request path. Use the direct push only when main is unprotected
and the owner chooses it for this release.

### Pull-request path (recommended)

1. Base the candidate on the current tip of main, so the PR's test merge has
   the same tree as the candidate:
   ```bash
   git fetch origin main
   test "$(git rev-parse "$CANDIDATE_SHA^")" = "$(git rev-parse origin/main)"
   git push origin "$CANDIDATE_SHA:refs/heads/release/vX.Y.Z"
   gh pr create --repo "$REPO" --base main --head release/vX.Y.Z --title "release: prepare vX.Y.Z" --body-file <notes>
   ```
   If main moved, rebase the candidate, repeat the PREPARED checks and use the
   new `CANDIDATE_SHA`.
2. Wait for `collection-quality` on the exact candidate commit and require
   `headSha` = `CANDIDATE_SHA`, `status: completed`, `conclusion: success`:
   ```bash
   gh run list --repo "$REPO" --commit "$CANDIDATE_SHA" --workflow collection-quality --json databaseId,headSha,status,conclusion,event --limit 1
   gh run watch <run-id> --repo "$REPO" --exit-status
   gh run view <run-id> --repo "$REPO" --json headSha,status,conclusion
   ```
3. Merge the PR (merge commit or squash; the owner picks). Record the commit it
   created on main and prove it carries the candidate tree:
   ```bash
   git fetch origin main
   RELEASE_SHA="$(gh pr view release/vX.Y.Z --repo "$REPO" --json mergeCommit --jq .mergeCommit.oid)"
   python3 scripts/check_merged_candidate.py --candidate "$CANDIDATE_SHA" --merged "$RELEASE_SHA" --branch origin/main
   ```
   `BLOCKED` means main changed between CI and merge. Do not tag. Rebuild the
   candidate on the new main and start this stage again.
4. Wait for the push run of `collection-quality` on `RELEASE_SHA` with the same
   three checks. `RELEASE_SHA` is the commit you tag; from here on pass it as
   `--release-commit`.

### Direct push (main unprotected, owner's choice)

Push the candidate to main, wait for CI on `CANDIDATE_SHA` as in step 2, and
set `RELEASE_SHA="$CANDIDATE_SHA"`.

Either way, a missing, queued, failed or unreadable run does not pass; follow
[CI completion](CLOSEOUT.md#wait-for-the-exact-commit).

**Protect main.** Recommend that the owner adds a branch ruleset for main that
requires a pull request, requires the `collection-quality` check, and blocks
force pushes and deletion. The owner changes repository settings; you do not.

## 3. TAGGED — protected annotated tag

Recheck the owner's approval for this repository, version and commit. A
different target needs a new approval.

1. Check that tags are protected on GitHub:
   ```bash
   python3 scripts/check_release_tag_protection.py
   ```
   It requires an active `tag` ruleset covering `refs/tags/v*` that restricts
   `deletion` and `update`, with no bypass actors. Otherwise report `BLOCKED`
   and stop.
2. Run the tag preflight. It checks that the commit exists, the working tree
   is clean, the ruleset passes, and the tag exists neither locally nor on origin:
   ```bash
   python3 scripts/check_release_tag_preflight.py \
     --tag vX.Y.Z \
     --release-commit "$RELEASE_SHA"
   ```
3. Create the annotated tag on the release commit. The tag holds the Manifest
   and Notes, never a Receipt:
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z — <title>" "$RELEASE_SHA"
   ```
4. Check the local tag:
   ```bash
   python3 scripts/verify_release_integrity.py \
     --tag vX.Y.Z \
     --release-commit "$RELEASE_SHA" \
     --stage tagged --mode current
   ```
   If this fails, do not push the tag. Delete the local tag
   (`git tag -d vX.Y.Z`) and fix the cause.
5. Push the tag:
   ```bash
   git push origin vX.Y.Z
   ```
6. Confirm `git cat-file -t refs/tags/vX.Y.Z` prints `tag` (annotated, not a
   commit), then bind the remote tag to the release commit:
   ```bash
   python3 scripts/verify_release_integrity.py --tag vX.Y.Z --release-commit "$RELEASE_SHA" --stage tagged --mode current --check-remote
   ```

A pushed tag cannot be moved or deleted. If anything after this point is wrong,
follow [BROKEN-RELEASE.md](BROKEN-RELEASE.md).

## 4. INSTALL_VERIFIED — fresh installs from the tag

The required evidence is the `release-installation` workflow. Run it from main,
so a verifier fixed on main applies without touching the tag:

```bash
gh workflow run release-installation.yml --repo "$REPO" --ref main -f tag=vX.Y.Z -f expected_commit="$RELEASE_SHA"
```

Wait for the run, then download its `release-installation-evidence` artifact.
Its `result.json` becomes the `installation` observation. The manual command
matrix and the real-Host smoke in [VERIFICATION.md](VERIFICATION.md) are
optional extra evidence; neither replaces the workflow result.

## 5. PUBLISHED — GitHub Release

GitHub renders Release bodies with links relative to the repository root, so
sibling links in the Notes would 404. The body script turns them into full URLs
on the current repository.

1. Prepare the body in a temporary directory:
   ```bash
   BODY="$(mktemp -d)/release-body-vX.Y.Z.md"
   python3 scripts/prepare_release_body.py \
     --tag vX.Y.Z \
     --output "$BODY"
   ```
2. Publish:
   ```bash
   gh release create vX.Y.Z --repo "$REPO" \
     --title "vX.Y.Z — <title>" \
     --notes-file "$BODY"
   ```
3. Open `gh release view vX.Y.Z --repo "$REPO"` and check that every link works.

## 6. ATTESTED — receipt on main

1. On main, create `RELEASE_RECEIPT.md` and `RELEASE_RECEIPT.zh-CN.md` with
   `Status: VERIFIED` or a documented failure. Record the tag object and
   commit SHAs, the CI run IDs and results, the pinned and latest install
   results, the Release URL and its publication time. Link back to the Manifest
   and Notes.
2. Update the docs and catalog to name the new stable release.
3. Finish every copy and link, then follow the
   [final-artifact checks](CLOSEOUT.md#verify-final-artifacts) on the staged
   attestation. Commit it as `docs(release): attest vX.Y.Z publication` and
   record `ATTESTATION_SHA`. If main is protected, this commit goes through a
   pull request like the candidate did.
4. On the clean tree, run the full gate:
   ```bash
   python3 scripts/verify_release_integrity.py \
     --tag vX.Y.Z \
     --release-commit "$RELEASE_SHA" \
     --stage attested --mode current \
     --check-remote
   ```
5. Only after it passes, push the attestation commit to `origin/main`.
6. Wait for CI on `ATTESTATION_SHA` as in
   [CI completion](CLOSEOUT.md#wait-for-the-exact-commit). Every later repair
   repeats the local checks and exact-commit CI; keep the earlier failures.
7. ATTESTED is reached only when that final commit passes CI. Then write the
   [closeout report](CLOSEOUT.md#report-the-whole-release).
