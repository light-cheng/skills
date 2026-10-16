# 01 — Make ticket 02 wait for ticket 01, and decide whether the SPEC grows to cover its extra output formats

**Status:** rejected
**Raised by:** light-implement · 2026-10-16
**Trigger:** .scratch/expsum/issues/02-formats-and-dialects.md#implementation-report--2026-10-16

## Why
- Ticket 02 asks to "Restructure `expsum` into `parse`, `aggregate` and `render` modules"
  (`issues/02-formats-and-dialects.md`, body), but no `expsum` package exists yet
  (`git ls-files` at 1b4303f lists no `expsum/` or `tests/`). That code comes from ticket 01
  (`issues/01-parse-and-sum.md`), which is still `Status: ready-for-agent`. Ticket 02 still says
  `Blocked by: none`.
- The approved SPEC asks only for a summary "printed as a table" (`spec.md`, line 3), and its
  acceptance item is "`python -m expsum file.csv` prints totals per category per month; invalid
  rows are reported, not fatal" (`spec.md`, line 4). Ticket 02 adds a `--format` flag with CSV and
  JSON output, and detection of semicolon/tab separators, quoted fields and a BOM. None of that
  is in the SPEC.

## Change
- SPEC: depends on open decision 1 — option A adds a requirement for `--format table|csv|json`
  (default `table`) and for CSV dialect detection (comma/semicolon/tab, quoted fields, BOM), with
  a matching acceptance item; option B leaves the SPEC unchanged
- Tickets: change Blocked by `.scratch/expsum/issues/02-formats-and-dialects.md` → `Blocked by: 01`
- Tickets: depends on open decision 1 — option A leaves ticket 02's acceptance as written;
  option B changes ticket 02's acceptance to cover only the `parse`/`aggregate`/`render` split
  with table output, and drops the CSV/JSON formats and dialect detection
- Charter: none (no `.project-review/charter.md` exists)
- Accept again: none (no ticket is resolved)

## Open decisions
1. Should expsum support more than a table and more than comma-separated input?
   - **A — Grow the SPEC** (recommended if you need these exports or have real semicolon/tab
     files): add `--format` (table/CSV/JSON) and dialect detection to the SPEC, and keep ticket 02
     as written.
   - **B — Keep the SPEC as is**: cut ticket 02 down to the module split with table output only,
     and leave the formats and dialects for a later change.

## Not changed
- Ticket 01 (`issues/01-parse-and-sum.md`): scope, status and acceptance stay as they are.
- The SPEC's existing table output, invalid-row reporting and `python -m expsum file.csv` entry point.
- The standard-library-only constraint (`docs/agents/light-project.md`).

## Comments
- 2026-10-16 rejected — "I reject the proposal. Leave the SPEC and tickets as they are."
