# Final checks, CI and the closing report

Use this before you push a candidate, an attestation or any repair, and before
you call a release complete. Local checks, the published tag and the final CI
on main are three separate pieces of evidence.

## Make one repair per stage

Inside one stage, collect the whole repair before you commit: code, generated
files, both languages, links, status and evidence. Review it against the staged
tree; you do not need a public commit to review. Default to one commit and one
push per stage, after the final checks pass. Keep intermediate notes in your
local task record.

The candidate and the receipt are always separate commits, because the receipt
records a publication that happens in between. Do not squash a whole release
into one commit or write future facts early.

If you made unpublished checkpoint commits yourself, you may combine them within
the owner's approved scope, keeping the reviewed package bytes and rechecking the
final tree. Never rewrite published history, tags, the owner's commits or
anyone else's work. If you are unsure who owns a commit, keep it and say why.

A failure found after a push needs a new repair commit and new CI. Keep the
failed commit and run, and explain them. Do not delay a needed fix to keep the
commit count low.

## Verify final artifacts

1. Finish generated files, copies, renames and log archives first. Point every
   link at the path that will be committed, in both receipt languages. Keep raw
   logs byte-for-byte; an archive may hold logs with trailing whitespace that
   repository checks would reject.
2. Read the current release pages: README, catalog, installation, maintenance
   and migration. At PREPARED they describe the target version; at ATTESTED
   they name the confirmed stable version. Leave historical snapshots as they
   are.
3. Stage the files and bind the checks to that exact tree. Working-directory
   files can include untracked or ignored files the commit will not have, so
   also export the tree and run the discovery test on the export:

   ```bash
   git diff --exit-code
   VERIFIED_TREE="$(git write-tree)"
   git diff --cached --check
   python3 -m pytest -q
   python3 -m compileall -q skills tests scripts
   python3 scripts/check_public_docs.py --tag vX.Y.Z --stage prepared
   VERIFY_DIR="$(mktemp -d)"
   mkdir "$VERIFY_DIR/exported"
   git archive --output="$VERIFY_DIR/tree.tar" "$VERIFIED_TREE"
   tar -xf "$VERIFY_DIR/tree.tar" -C "$VERIFY_DIR/exported"
   (cd "$VERIFY_DIR/exported" && python3 -m pytest -q tests/test_collection_discovery.py)
   rm -rf -- "$VERIFY_DIR"
   ```

   Record the tree ID and the result before you remove the export. The
   discovery test resolves every Markdown link, receipts included, against the
   committed files. Both the export and the test must pass.
4. Before committing, require no unstaged changes and the same `git write-tree`
   value. After committing, require `git rev-parse HEAD^{tree}` to equal
   `VERIFIED_TREE`. Any later edit, or a hook that changes the commit, means
   you check the new tree again before you push.

A run that passed before an archive or link edit is not evidence for what you
push afterwards. If a required check fails, stop before the push, make the
smallest approved repair and check again.

## Wait for the exact commit

After each push, record the full SHA and find the `collection-quality` run for
that commit — not the newest green run on the repository:

```bash
REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
gh run list --repo "$REPO" --commit <pushed-sha> --workflow collection-quality --json databaseId,headSha,status,conclusion --limit 1
gh run watch <run-id> --repo "$REPO" --exit-status
gh run view <run-id> --repo "$REPO" --json headSha,status,conclusion
```

Require the matching `headSha`, `status: completed` and `conclusion: success`.
Queued, running, failed, cancelled, missing or unreadable runs do not pass. If
reading fails, retry; never invent a result. If CI fails, read its log, keep the
failed commit and run, repair within the approval, and repeat the final checks
and CI on the new commit. An earlier candidate success never stands in for the
final attestation run.

The receipt records publication facts you already observed. Keep the final
attestation SHA and run in your local record and final report, not in the
receipt: writing them into the receipt creates a new commit that needs its own CI.
If publication happened but attestation is not verified yet, report exactly
that and keep working within scope.

## Report the whole release

Report:

- the version and tag;
- the candidate commit and the release commit it was tagged on (the same commit
  on the direct-push path), with their CI runs;
- the install and publication results, including any Host smoke;
- the final main commit and its successful CI run;
- every failed attempt: its commit or run, the cause, the repair and the run
  that replaced it.

The owner should learn about a failure and its fix from your report, not from a
GitHub email.

A GitHub file page shows the checks of the last commit that changed that file.
Before calling a red badge a current failure, compare that commit with the
current branch and its CI; explain both if they differ. Do not rerun unchanged
bad content, rewrite a tag, skip checks or make a cosmetic commit to turn a
badge green.

The release is complete only with correct links and current docs, all local
checks, exact-commit CI for the candidate, a protected remote tag, fresh
installs from the released source, a public Release with working links, and
exact-commit CI for the final attestation.
