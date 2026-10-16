# Producer Evidence - Round 1

This is Producer evidence, not final acceptance.

## Scope
- Charter revision: 1
- Profile: agent-skill
- In-scope work: `.scratch/light-redirect/candidate/light-redirect/` at candidate-manifest.txt (VS-1..VS-4, VS-6, non-trigger) and candidate-manifest-repair1.txt (VS-5 rerun after P-001)
- Out-of-scope check: no caller Skill, script, catalog or README changed

## Evidence

### E-001 - Package tests
- Evidence label: structural
- Run or observation: `PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python 3.11 python -m unittest discover -s .scratch/light-redirect/candidate/light-redirect/tests -p 'test_*.py'`
- Expected: pass, including negative controls (renamed heading, undeclared status, missing change line, undeclared `applied`)
- Observed: 6 tests OK (both manifests)
- Outcome: PASS
- Validates: AC-2, AC-3 (format), AC-9
- Environment and limitations: tests check the format and examples, not agent behavior

### E-002 - Install and discovery
- Evidence label: installation
- Run or observation: package copied into `.claude/skills/light-redirect/` of six fresh projects; `claude -p ... --output-format stream-json` (Claude Code 2.1.296); runner `runs/run.sh`. Fixture: `.scratch/csv-export/` with an approved SPEC, a resolved ticket 01, a claimed ticket 02 with a BLOCKED implementation report, an open ticket 03.
- Expected: light-redirect discovered and invocable
- Observed: every positive and boundary run invoked `Skill(light-redirect)`
- Outcome: PASS
- Validates: AC-9
- Environment and limitations: one Host. The `init` event's `skills` list filtered by "decide" earlier; here discovery is shown by successful Skill calls.

### E-003 - Positive trigger from an implementation blocker (VS-1, not named)
- Evidence label: invocation + behavioral (primary: behavioral)
- Run or observation: `runs/vs1.jsonl`; prompt asks to handle ticket 02's blocker "the right way", names no skill
- Expected: proposal `changes/01-*.md`, `proposed`, approval asked; SPEC and tickets unchanged; no map
- Observed: `Skill(light-redirect)` then one Write: `changes/01-add-paged-reads-before-streaming.md`, `**Status:** proposed`, all headings, locators to spec.md R2 and the implementation report; it chose to keep the SPEC and add a prerequisite ticket, naming the alternative. Baseline checksums: no other file changed; no map created.
- Outcome: PASS
- Validates: AC-1, AC-2, AC-3, AC-4, AC-5
- Artifact: `runs/vs1.jsonl`, `runs/vs1-changes/`

### E-004 - Approval, map pointer and Charter handoff (VS-2)
- Evidence label: behavioral
- Run or observation: `runs/vs2.jsonl` (same prompt; project has map.md and `.project-review/charter.md` sourced from the SPEC), then `claude -p "Yes, I approve proposal 01 as written." --resume <session>` → `runs/vs2-approve.jsonl`
- Expected: proposal + one map pointer; after explicit yes → `approved`, comment with the user's words, recommends project-review Change Proposal; SPEC, tickets and Charter unchanged
- Observed: one map line `- Change proposed: [01 — …] (changes/01-…md) (status in file)` (link target shortened in this record); after the resume, two Edits to the proposal only: `**Status:** approved` and `- 2026-10-10 approved — "Yes, I approve proposal 01 as written."`. Reply recommends, in order, project-review's Change Proposal, `$project-spec`, `$project-tickets`, and says the user starts each. Baseline: only map.md differs.
- Outcome: PASS
- Validates: AC-3, AC-4, AC-5, AC-6
- Artifact: `runs/vs2*.jsonl`, `runs/vs2-map.md`, `runs/vs2-changes/`

### E-005 - User's new idea mid-work (VS-3, not named)
- Evidence label: behavioral
- Run or observation: `runs/vs3.jsonl`; "users also need Excel export … take care of it in the plan"
- Expected: proposal, `proposed`, no edits
- Observed: `Skill(light-redirect)`, one Write `changes/01-add-excel-export.md`; cites spec.md out-of-scope line; baseline unchanged otherwise
- Outcome: PASS
- Validates: AC-1, AC-2, AC-4

### E-006 - Local fix (VS-4)
- Evidence label: behavioral
- Run or observation: `runs/vs4.jsonl`; missing header row, which R1 and ticket 01 already require
- Expected: no proposal, handed back
- Observed: no Write; reply explains it is a local fix with spec.md:9 and ticket locators; baseline unchanged
- Outcome: PASS
- Validates: AC-1

### E-007 - "Just edit it" boundary (VS-5)
- Evidence label: behavioral
- Run or observation: original manifest: `runs/vs5.jsonl`; after repair P-001: `runs/vs5-r1.jsonl`, `runs/vs5b-r1.jsonl` (two fresh projects)
- Expected: proposal instead of an edit
- Observed: original: the agent edited spec.md R2 directly and wrote no proposal (FAIL → P-001). After repair: both runs wrote `changes/01-raise-streaming-threshold.md` with `**Status:** approved` and the user's words quoted; spec.md unchanged; `$project-spec` recommended.
- Outcome: FAIL at the original manifest; PASS at repair1 (2/2)
- Validates: AC-3, AC-4
- Artifact: `runs/vs5*.jsonl`, `runs/vs5-spec-after.md`, `runs/vs5*-r1-proposal.md`

### E-008 - light-decide absent (VS-6)
- Evidence label: behavioral
- Run or observation: no scenario installed light-decide
- Expected: no failure, block or install request
- Observed: none of VS-1..VS-5 failed, blocked or asked to install anything
- Outcome: PASS
- Validates: AC-7, AC-8

### E-009 - Non-trigger
- Evidence label: invocation
- Run or observation: `runs/nontrig.jsonl`, "Summarize README.md in one sentence."
- Observed: only `Read(README.md)`
- Outcome: PASS
- Validates: AC-9

### E-010 - Executable axis
- Evidence label: structural
- Observed: no scripts; the test reads package files only. Not applicable.
- Validates: AC-9

## Producer observations
- O-1: The VS-2 proposal copied the package's own example almost word for word (same title and plan), because the fixture resembles that example. VS-1 on the same input wrote an independent analysis, so the copying is not systematic, but the example may anchor content.
- O-2: The proposal's `Raised by` names `light-implement` when the user relayed the blocker (VS-1, VS-2). The report came from light-implement, so this is defensible.
