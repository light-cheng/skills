# Software Profile (`Profile: software`)

Select `software` when accepting executable code, scripts, libraries, services, or repository changes whose correctness depends on software behavior and git history.

## Review axes

Audit every applicable axis independently and record the axis on each `F-###` finding (`Not applicable` requires an explicit reason in `producer-evidence.md`):

1. **Standards:** conformance to documented repository standards (`CLAUDE.md`, `AGENTS.md`, `CODING_STANDARDS.md`, `CONTRIBUTING.md`) and structural code hygiene. Supplied by Base workflow `code-review` (`Standards` axis) when installed, or the built-in Standards diff reviewer in [reviewer-protocol.md](../reviewer-protocol.md) when absent.
2. **Spec:** faithful implementation of approved requirements, interfaces, and exclusions without unrequested scope creep. Supplied by Base workflow `code-review` (`Spec` axis) when installed, or the built-in Spec diff reviewer in [reviewer-protocol.md](../reviewer-protocol.md) when absent.
3. **Behavioral correctness:** assertion-bearing automated tests exercising changed success, boundary, failure, and regression paths (including negative/adversarial inputs where relevant).
4. **Operational safety:** input validation, error handling, backward compatibility, resource cleanup, and security/data-boundary hygiene within scope.

`code-review` reports are `review` evidence and candidate findings only; `code-review` never edits code or issues the final `PASS`, `FAIL`, or `BLOCKED` verdict.

## Three-part durable software identity (Charter scale)

Software acceptance binds the Charter to exact git state through three singleton fields (missing, short-SHA, globbed, or duplicated values fail closed as `BLOCKED`):

1. **`Fixed point` (in `charter.md` at `init`):** `- Fixed point: <full 40-character Git commit SHA>`. Resolve any branch/tag ref via `git rev-parse` at `init` and freeze the immutable base commit SHA from which `git diff <fixed-point>...HEAD` is reviewed. Never mutate `Fixed point` during repair rounds.
2. **`Implementation scope` (in `charter.md` at `init`):** `- Implementation scope: <repo-relative POSIX literal path>; ...` (for example `src/; tests/; package.json`). Establish scope strictly from approved spec/ticket component boundaries, never by reverse-engineering whichever files the current diff touched. Reject absolute paths, `..`, globs, or pathspec magic; if component boundaries cannot be established reliably, return `BLOCKED`. Keep `.scratch/` outside `Implementation scope` (avoid whole-repo `.` unless `.scratch/` itself is the software under test, since writing `.scratch/.../verdict.md` would otherwise dirty `.`).
3. **`Reviewed implementation revision` (in `verdict.md` at closeout):** `- Reviewed implementation revision: <full 40-character Git commit SHA>`. Because bounded repairs advance `HEAD` from `C1` to `C2`, record the exact committed `HEAD` evaluated by the final fresh Evaluator on `verdict.md` rather than in `charter.md`.

### Clean-scope and freshness rules

- The diff `git diff <fixed-point>...HEAD` must contain non-empty changes inside `Implementation scope`. Out-of-scope-only diffs fail software verification.
- Every Producer repair must stay inside `Implementation scope` and be **committed** before final re-review and Evaluator sign-off.
- Issue `PASS` only when `Implementation scope` contains **zero** uncommitted tracked, untracked, or ignored files (`git status --ignored -- <scope-paths>`). Ignored build/temp artifacts inside a reviewed component path count as drift; unrelated changes outside `Implementation scope` do not block.
- Any later edit, commit, untracked file, or ignored file inside `Implementation scope` stales a prior `PASS` and requires a fresh acceptance run.

## Evidence requirements and failure stops

- Required evidence ([charter-and-evidence.md](../charter-and-evidence.md)): `source` (approved spec/ticket + `Fixed point` SHA), `review` (`Standards` + `Spec` diff reports + independent Evaluator report), `behavioral` (focused assertion-bearing tests with exact commands and outputs), and `runtime` when integration/CLI/UI behavior cannot be proven by unit tests alone.
- Severity follows Core impact tiers (`Critical`: security/data loss/crash; `High`: broken `AC-<n>`, public interface regression, or hard repo-standard breach; `Medium`: material defect or missing boundary/error check; `Low`: minor maintainability note).
- Return `FAIL` or `BLOCKED` per [charter-workflow.md](../charter-workflow.md) when tests pass with zero assertions, required scenarios are skipped, `Implementation scope` is dirty at evaluation, or fixing a defect requires altering approved requirements or architecture (`FAIL` with `Cause: direction` -> `redirect`).
