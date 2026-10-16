---
name: release-workflow
description: Prepare, verify and attest a first-party Skills release, or audit an existing tag and its installation evidence. Use for a new release, fresh-install verification or release-evidence closeout; execute only the requested stages and authorized targets.
---

# Skills Collection Release Workflow

Release one version of this collection in stages. Each stage produces its own
evidence: a local candidate, CI on that exact commit, a protected tag, fresh
installs, a published GitHub Release and a receipt. One stage passing never
proves the next.

## Before you start

1. Find the repository with `gh repo view --json nameWithOwner`. The scripts do
   the same; never type an owner or repository name from memory. If `origin`
   still points at an old name that only redirects, tell the owner and update
   it only with their OK.
2. Settle the target version, the stages the owner asked for and the current
   stable version. Use `--mode historical` only to re-audit an existing tag.
3. Prepare and review the candidate locally first. Then, before the first remote
   write, show the owner the candidate commit, the tag, the package count and
   each action, and get their approval. Approval covers that target only.

Do not push, tag, publish, install globally or change Host settings outside
what the owner approved. A request to verify installs does not authorize a tag.

## Run the stages

```text
PREPARED → CI_VERIFIED → TAGGED → INSTALL_VERIFIED → PUBLISHED → ATTESTED
```

- [RELEASE-STAGES.md](references/RELEASE-STAGES.md): the commands for each stage,
  including the pull-request path to main.
- [VERIFICATION.md](references/VERIFICATION.md): fresh installs from the released
  tag, and the optional smoke test in a real Host.
- [DOCUMENT-STATE.md](references/DOCUMENT-STATE.md): what the Notes, Manifest,
  Receipt and public pages may say at each stage.
- [CLOSEOUT.md](references/CLOSEOUT.md): checking the exact tree you commit,
  waiting for CI on the exact commit, and the final report.
- [BROKEN-RELEASE.md](references/BROKEN-RELEASE.md): what to do when a published
  release turns out to be broken.

Rules that apply to every stage:

- CI counts only when the run's `headSha` is the commit you pushed and the run
  is completed and successful.
- The Manifest and Notes go into the candidate. The Receipt is written on main
  after publication and records only facts you observed.
- A local rehearsal with test doubles uses `--simulate` and reports
  `SIMULATED_PASS`. It is never a production pass.

## Stop and report

Stop when the requested stages pass, or at the first gate that fails or needs
the owner. Report the candidate and release commits, the tag, the CI runs, the
install and publication results, any failed attempt with its repair, and the
gates still open. A green push or a published Release alone is not done.
