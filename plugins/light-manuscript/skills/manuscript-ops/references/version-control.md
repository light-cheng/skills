# Project version gates

## Selection

Inherit an existing supported repository backend when present. `Quick` and `Structured` routes use no version gates (`VCS_NOT_APPLICABLE`). On `Project` routes, `validate_state.py --check-vcs` (or compatibility flag `--check-jj`) dispatches on `ProjectProfile.version_control.system`. Backends without receipt-bound gate verification (such as plain `git`) report `VCS_GATES_UNSUPPORTED` (`BLOCKED`) rather than `JJ_MISSING` or a false `PASS`.

For a new `Project` route, initialize local non-colocated Jujutsu after probing `jj --version`:

```text
jj git init --no-colocate <project-root>
```

The end-to-end tested baseline is `jj 0.43.0`; other versions emit a `JJ_VERSION` warning requiring command probing. Configure a local author identity if absent, and never add a Git remote unless `remote_allowed: true` is explicitly approved in the Profile and Publish gate.

## Inspection commands

Before pausing or sealing a gate, inspect repository state using read-only commands:

```text
jj --ignore-working-copy status
jj --ignore-working-copy log
jj --ignore-working-copy bookmark list
jj --ignore-working-copy git remote list
```

## Date versions and gate bookmarks

Use `YYYY.MM.DD`, incrementing to `YYYY.MM.DD-02`, `-03`, and so on via `scripts/next_version.py` whenever a gate receipt or bookmark already uses that date.

Create immutable dated bookmarks (`brief-approved-2026.11.25`, `baseline-2026.11.25`, `framework-approved-2026.11.25`, `source-locked-2026.11.25`, `final-approved-2026.11.25`, `publish-approved-2026.11.25`) alongside mutable aliases (`current-brief`, `current-baseline`, `current-framework`, `current-source-locked`, `current-final`, `current-publish`).

Configure repository-local `revset-aliases."immutable_heads()"` so dated gate bookmarks are immutable while `current-*` aliases remain movable:

```text
builtin_immutable_heads()
| bookmarks(glob:"brief-approved-*")
| bookmarks(glob:"baseline-*")
| bookmarks(glob:"framework-approved-*")
| bookmarks(glob:"source-locked-*")
| bookmarks(glob:"final-approved-*")
| bookmarks(glob:"publish-approved-*")
```

Never pass `--ignore-immutable` in a manuscript project.

## Receipt seal sequence

1. Freeze gated manuscript files and review/QA evidence in a content revision.
2. Compute SHA-256 digests and start a child seal revision without modifying gated files.
3. Record the parent content revision's `change_id` and `commit_id` in the new `GateReceipt` JSON file inside the child revision.
4. Point the dated bookmark at the child seal revision and advance the matching `current-*` alias to it.
5. Verify with `scripts/validate_state.py --root <project-root> --check-vcs` that the bookmark holds exact `GateReceipt` bytes, its parent matches the recorded Jujutsu IDs, and every gated file at that parent matches its recorded SHA-256.
6. Start a fresh working change for subsequent work. To update a sealed gate, create a new dated version and receipt rather than rewriting an immutable bookmark.
