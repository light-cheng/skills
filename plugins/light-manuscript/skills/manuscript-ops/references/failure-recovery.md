# Failure and recovery

## Missing tool or independent context

When a required format provider, renderer, Jujutsu binary, or independent review context is unavailable on a gate that requires it, preserve all current artifacts and hashes and return `BLOCKED` with:

- the exact missing capability or context requirement;
- the milestone or QA check that requires it;
- preserved artifact and state paths;
- the smallest action needed to unblock and resume.

Never fabricate render evidence or treat same-context self-review as independent acceptance. When subagent dispatch is unavailable, prepare a frozen hash-bound review packet so the user can run the Evaluator in a separate fresh session (`independence: "fresh_session"`).

## Stale snapshot

Re-run `scripts/assess_project.py` or `scripts/probe_capabilities.py` whenever a routing or capability snapshot exceeds `snapshot_max_age_hours` or when scope, sources, deliverables, or host tools change. Never seal a gate against stale capability claims.

## Same-day version collision

Run:

```text
python scripts/next_version.py --date YYYY.MM.DD --root <project-root>
```

Apply the returned `YYYY.MM.DD-NN` suffix consistently across gate bookmarks, receipts, snapshots, and milestone filenames.

## Review fails to converge or hits a direction flaw

- Stop after 3 repair rounds (or earlier when no material progress occurs), preserve findings and evidence, and return `BLOCKED` so the user can supply missing sources, accept a documented non-critical risk, or revise scope.
- When `acceptance` returns `FAIL` with `cause: "direction"` (the approved Brief or outline itself is contradictory or unworkable), invoke `redirect` (or write a Change proposal under `.scratch/<feature>/changes/`) and wait for human Brief approval rather than retrying prose repairs.

## Render or visual QA unavailable

Preserve the generated deliverable and structural validator logs. Mark render/visual checks honestly, returning `DEGRADED` only when the approved Brief and adapter allow non-blocking degradation (`blocking_qa_gaps: false` outside final `READY` gates); otherwise return `BLOCKED`. Never report layout acceptance from syntax checks alone.

## Round-trip failure

Retain both the generated deliverable and the failed round-trip output with separate hashes. Identify lost invariants and either repair the generator, lock a specific target application with user approval, narrow the Brief deliverable contract with user approval, or return `BLOCKED`.

## Existing path mismatch

Update `project-profile.json` path mappings after verifying actual repository files. Never move or rename existing user files merely to match the default directory layout.

## Interrupted run

Read `.manuscript-ops/state.json` first, then inspect the active receipts, batch manifest, and latest `acceptance` report. Verify file hashes via `scripts/validate_state.py --root <project-root>` before continuing, and append successor snapshots rather than overwriting completed batches or sealed receipts.

## Jujutsu version or backend mismatch

If `ProjectProfile.version_control.system` is not `jj` (for example `git`), `validate_state.py --check-vcs` reports `VCS_GATES_UNSUPPORTED`; obtain user approval before initializing non-colocated `jj` or changing version settings. If the installed `jj` version differs from `0.43.0`, probe `--help` and test revset/bookmark commands in a disposable directory before sealing project gates; never auto-upgrade, add remotes, or run `--ignore-immutable`.
