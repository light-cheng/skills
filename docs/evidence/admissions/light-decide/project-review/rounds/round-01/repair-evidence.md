# Repair Evidence - Round 1

## Repair 1 (manifest candidate-manifest-repair1.txt)
- Findings: F-001..F-012
- Files: SKILL.md (steps 1, 2, 6), references/selection.md (rewritten: destination by where the model runs, unrecognized limit = off, availability evidence, policy names, calibration collect/measure), references/formats.md (applied, fallback table, score bins, one legal option, feature resolution, clock time, policy names, neutral backend name), tests (vocabulary parsed from references, confidence rule, four negative controls)
- Checks: package tests 7 OK (structural)
- Scenario rerun (behavioral/invocation), logs runs-repair1/: VS-1 status + one yes_no call, on-device, uncalibrated, clock time 22:00:18Z; VS-2 off holds; VS-3 declined, ticket open, no log; VS-4 unavailable; VS-5 none, no source asked; non-trigger no skill call
- Critic recheck: F-001..F-012 fixed; new F-013 (fixed by writing the manifest), F-014, F-015

## Repair 2 (manifest candidate-manifest-repair2.txt)
- Findings: F-014 (formats.md: score rules override general answer/options/confidence; options are bins, probabilities keyed by level; test skips score in confidence_errors), F-015 (selection.md step 1: named source outside limit or unavailable is skipped and the caller is told why)
- Checks: package tests 7 OK
- Scenario rerun at repair2 (runs-repair2/): first pass hit the account usage limit in VS-1 and VS-2 (kept as *.limit.jsonl, not counted); both rerun after the reset.
  - VS-1: status + one yes_no call, on-device, uncalibrated, final no, clock time 2026-10-10T00:02:19Z
  - VS-2: off holds; reply explains the named source was skipped and why (F-015); no decision call
  - VS-3: declined; ticket still open; no log
  - VS-4: unavailable; VS-5: none, no source asked; non-trigger: no skill call

## Repair 3 (manifest candidate-manifest-repair3.txt), after Evaluator
- E-001 (low, confirmed): formats.md `unavailable` row now also covers an error reply from the chosen source.
- E-004 (low, confirmed): formats.md Score: each bin includes its lower bound (0.5 → standard in the example), matching the Jev contract's half-open bins.
- E-002 (low, confirmed as Host limitation, no package repair): on Claude Code the user-level policy file read is outside the default directory scope; the package degrades to uncalibrated and tells the user. The calibrated path is unobserved; recorded as a limitation.
- E-003 (low, confirmed): temp projects deleted after the final recheck.
- Checks: package tests 7 OK. Text-only change to two table/paragraph lines; no scenario exercised these paths, so no rerun.
