# 01 — Drop JSON output so expsum renders only a table or CSV

**Status:** proposed
**Raised by:** light-implement · 2026-10-16
**Trigger:** "Actually, we've decided we don't need JSON output at all - drop it." (user, during `.scratch/expsum/issues/01-end-to-end.md#implementation-report--2026-10-16`)

## Why
The user no longer wants JSON output. The approved plan still requires it in three places:
- `.scratch/expsum/spec.md`, the "Render" bullet: "Render the summary as a table, CSV or JSON, chosen by `--format`."
- `.scratch/expsum/spec.md`, the "Acceptance" line: "`python -m expsum file.csv --format table|csv|json` works for all three dialects; tests cover … each format".
- `.scratch/expsum/issues/01-end-to-end.md`, the body: "the three renderers behind `--format`".

## Change
- SPEC: the "Render" bullet becomes "Render the summary as a table or CSV, chosen by `--format`." The "Acceptance" line becomes "`python -m expsum file.csv --format table|csv` works for all three dialects; tests cover each dialect, each format and invalid rows."
- Tickets: change acceptance `.scratch/expsum/issues/01-end-to-end.md` → "the three renderers behind `--format`" becomes "the table and CSV renderers behind `--format`".
- Charter: none
- Accept again: none

## Open decisions
- What should `--format json` do once JSON is gone? Recommendation: treat it like any other unknown format. argparse rejects it with a usage error and exit code 2, and no special handling is needed.

## Not changed
- Dialect detection (comma, semicolon, tab, quoted fields, UTF-8 BOM).
- Per-category monthly totals, with invalid rows reported and processing continuing.
- The `parse` / `aggregate` / `render` split, with the rule that adding a format needs no parser change.
- Tests for each dialect and invalid rows; the stdlib-only constraint.
- Ticket 01 stays a single ticket that covers the whole SPEC.

## Comments
