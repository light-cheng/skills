# Producer evidence — round 2

Target `manifest.txt` (63 files). `skills/` equals `snap-w7`. Repairs since round 1: E-001 (light-html-plan reads report `Outcome:` and `Plan gap:`; part 3 lists a plan gap no proposal answers yet), E-002 (skills/README line 17 past tense). Suite 636 passed; docs check PASS.

Scenarios on snap-w7 (`.scratch/stage3-step4/evals/b7-behaviour/`), all three Hosts, no limit interruptions:
- **BPGAP (new):** ticket 02's newest report has `Outcome: BLOCKED` and a `Plan gap:` (two drills vs A2), no proposal. Every Host adds a part-3 card for the plan gap (labelled e.g. "计划缺口，还没有改动提案") beside the SMS card (ask = 2); `css_exact: True`, 0 undefined classes.
- **BPAGE (rerun on final text):** part 3 keeps exactly the SMS decision (ask = 1) on every Host; `css_exact: True`.

Everything else carries over from round 1 (`../round-01/producer-evidence.md`): no other file changed between `manifest-repair1.txt` and this manifest except the two repairs above (`comm` of the two file lists and the snapshot diff show only light-html-plan source-protocol.md, writing.md and skills/README*.md).

C-003 (pi D3) remains open pending the user's decision.

## Repair 1 of round 2 (`manifest-repair1.txt`; Critic recheck C-011..C-013)
Text-only edits: light-html-plan SKILL part-3 summary names the open plan gap (writing.md and source-protocol already did; BPGAP exercised them on all three Hosts); MAP-CONTRACT example adds the rejected line shape; light-implement plan-gap bullet covers SPEC and conversation slices. Suite 636 passed; docs check PASS. No scenario rerun: the SKILL sentence restates the rule BPGAP already exercised, the MAP-CONTRACT line is documentation, and the slice case has no fixture (recorded as a limit).
