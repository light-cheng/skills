# Producer Evidence - Round 2

This is Producer evidence, not final acceptance. It answers the round-1 Evaluator findings E-001..E-004 with runs at the current files.

## Scope
- Charter revision: 1 (unchanged)
- Profile: agent-skill
- Target: candidate-manifest.txt (= round-01 candidate-manifest-repair5.txt); every installed copy in the runs was diffed equal to it before running.
- Fixture generator: `runs/lr-gen.py`; runner: `runs/run.sh`; fresh projects; Claude Code 2.1.296; all runs exit 0.

## Evidence

### R2-E-001 - Charter seam with a change that really alters a Charter item (E-001; VS-2)
- Evidence label: behavioral
- Setup: vs2, vs2b — ticket 02 report adds that `ReportDB` is a vendored third-party library that cannot change; project has map.md and `.project-review/charter.md` with AC-2 "R2 holds: a 200,000-row report streams with memory under 100 MB".
- Turn 1 (blocker prompt, skill not named): `Skill(light-redirect)`; proposal rewrites R2; `- Charter: .project-review/charter.md, AC-2 …`; one map line; `proposed`. Baseline: only map.md changed.
- Turn 2 (NEW session: "I approve change proposal 01 … Go with your recommendations on any open decisions."): `Skill(light-redirect)`; status `approved`; comment with the user's words; the recommended answers recorded as the user's explicit choice. Reply: "Next steps, in order: 1. project-review → Change Proposal … use this recorded approval as the decision evidence. 2. $project-spec … 3. $project-tickets". SPEC, tickets, Charter unchanged.
- Outcome: PASS (2/2)
- Validates: AC-2, AC-3, AC-5, AC-6, VS-2

### R2-E-002 - Hand-edit rule at its own text (E-002; VS-5)
- Evidence label: behavioral
- Turn 1 (vs5, vs5b: "just edit the SPEC … Don't bother with a proposal"): proposal written, `approved` with the user's words, changes only R2 (`Tickets`, `Charter`, `Accept again`: none). SPEC unchanged. No hand edit offered as the default; both replies name `$project-spec` as the route and mention that the user may insist again (observation O-2).
- Turn 2 (resume: "Yes, but just change the line in the SPEC by hand yourself …"): the agent edited only R2 (diff with an untouched spec: only R2 differs); proposal `applied` with comment `"<user's words>" Edited by hand, not through project-spec or project-tickets.`; no Charter exists; no ticket edited.
- Outcome: PASS (2/2)
- Validates: AC-3, AC-4 (with the user decision on F-005)

### R2-E-003 - Review FAIL caused by direction, and numbering (E-003)
- Evidence label: behavioral
- Setup: vs6 — `.project-review/verdict.md` FAIL whose basis says the code meets R1 but R1 is wrong for the users; `changes/01-…` already exists (applied).
- Observed: `Skill(light-redirect)` from an unnamed prompt; new proposal `changes/02-csv-for-semicolon-locale-spreadsheets.md`, `proposed`; changes R1; `Accept again: .scratch/csv-export/issues/01-csv-endpoint.md`; Charter AC-1 named; next steps "project-review's Change Proposal, then $project-spec and $project-tickets"; proposal 01 untouched.
- Outcome: PASS
- Validates: AC-1 (third trigger), AC-2 (next unused NN), AC-6
- Limitation: the "conflicting tickets" trigger is still not run.

### R2-E-004 - Rejection (E-004)
- Evidence label: behavioral
- Setup: vs7 — blocker prompt, then a NEW session: "I reject change proposal 01 … We will buy a better database driver next quarter instead."
- Observed: `Skill(light-redirect)`; status `rejected`; comment with the user's words; reply explains the plan stays as approved and ticket 02 remains blocked; nothing else changed.
- Outcome: PASS
- Validates: AC-3, AC-6 (rejected branch)
- Limitation: the `$project-clarify` branch (an open decision needing research or a longer interview) is not run.

## Observations
- O-2: In the first "just edit" turn, both replies told the user they could insist again on a hand edit, after naming `$project-spec` as the route. The user decision allows the hand edit after a second explicit insistence; it does not say whether the agent should mention that option.

## Turn-2 prompts (G-002)
- vs2-p2, vs2b-p2 (new session): "I approve change proposal 01 in .scratch/csv-export/changes/. Go with your recommendations on any open decisions."
- vs7-p2 (new session): "I reject change proposal 01 in .scratch/csv-export/changes/. We will buy a better database driver next quarter instead."
- vs5-p2, vs5b-p2 (resume of each p1 session): "Yes, but just change the line in the SPEC by hand yourself, I don't want to run another skill." The vs5 comment quotes it without the leading "Yes, but"; the agent trimmed the quote.
