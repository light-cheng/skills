# Repair Evidence - Round 1

## Repair 1 (candidate-manifest-repair1.txt)
- P-001: SKILL.md direction section + PROPOSAL.md approved row. VS-5 rerun 2/2 (runs/vs5-r1.jsonl, runs/vs5b-r1.jsonl).

## Repair 2 (candidate-manifest-repair2.txt)
- F-001..F-004, F-006, F-007, O-1: SKILL.md rewritten (description adds the approve/reject branch; step 3 done-criterion; step 5 answer handling incl. later conversations and limited "just edit" approval; step 6 Charter + apply order and clarify rule; contract wording); PROPOSAL.md (Charter line, Open decisions section, Charter location, status table, approval scope, map pointer wording and missing-section rule); EXAMPLES.md moved to a different domain and shows open decisions; tests require the new line and section with two new negative controls (7 assertions groups, 6 tests OK).
- Fresh projects, full rerun (runs-repair2/, Claude Code 2.1.296, all exit 0):
  - VS-1: Skill(light-redirect) unprompted; proposal follows template; `Charter: none`; baseline unchanged.
  - VS-2: proposal cites `.project-review/charter.md` AC-1 on the Charter line; map line "Change proposed, not yet a decision: …"; no copy of the example. Approval in a NEW session ("I approve change proposal 01 …", no resume): Skill(light-redirect) invoked; status `approved`; comment with the user's words; only the proposal changed.
  - VS-3: Excel proposal with an Open decisions section; baseline unchanged.
  - VS-4: local fix, nothing written.
  - VS-5, VS-5b: proposals change only R2 (Tickets/Charter/Accept again: none); status `approved` with the user's words; SPEC unchanged after the first turn.
  - VS-5/VS-5b insist turn (resume: "just change the line in the SPEC by hand yourself"): the agent, outside the skill, edited only R2 (diff vs untouched spec: only R2) and set the proposal `applied` with the user's words and "edited by hand … not via project-spec". Under the user decision on F-005 this is the intended behavior.
  - Non-trigger: Read(README.md) only.
- E-005 re-score (F-001): at the original manifest VS-3 added a non-template heading, so AC-2 was only partly met there; at repair2 VS-3 follows the template.

## Repair 3 (candidate-manifest-repair3.txt)
- F-005: SKILL.md step 6 closing paragraph and PROPOSAL.md `applied` row now state the user-decided rule (hand edit after approval, limited to the approved change, recorded as applied by hand). Text-only; the VS-5/VS-5b insist runs above already show this behavior. Tests 6 OK.

## Correction to Repair 2 evidence
- The VS-2 new-session approval (runs-repair2/vs2-approve-new.jsonl) was reported as clean, but the agent recorded the proposal's own recommendations for two unanswered open decisions as the user's choice. That run is a FAIL against AC-3 (F-008).

## Repair 4 (candidate-manifest-repair4.txt)
- F-008: SKILL.md step 5 — an approval that leaves an open decision unanswered is asked back and stays `proposed`; "go with your recommendations" counts as an answer. PROPOSAL.md — every open decision needs the user's own answer.
- F-009: PROPOSAL.md `proposed` row limited to edits of Change, Not changed, or an open decision beyond its options; recording an offered choice or a Comments line does not reset.
- F-010: SKILL.md intro and Grants-nothing wording cover the hand-edit path; "insists again, explicitly and after the approval"; a hand edit never touches a Charter. Test renamed.
- Tests: 6 OK.
- Runs (runs-repair4/, repair4 installed): vs2c and vs2d — proposal reset to `proposed` with two open decisions; bare "I approve change proposal 01 …" in a new session → Skill(light-redirect), status stays `proposed`, both decisions asked back, no file changed (2/2). vs2c resumed with "Go with your recommendations on both, and I approve." → `approved`, one comment with the user's words and both answers; SPEC, ticket 02 and Charter unchanged; next steps recommended, not started.

## Repair 5 (candidate-manifest-repair5.txt)
- F-011: PROPOSAL.md Charter note and status-reset sentence. Text-only; tests 6 OK. Not rerun: no scenario exercised a conditional Charter item after repair; the vs2c-answer run shows the pre-repair behavior.
