# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-10-11

## Acceptance baseline
- Source: `.scratch/decision-provider/design-stage3.md` §1, §2.6, §3.3, §4, §7 (触发 rows, 准入); `.scratch/decision-provider/handoff-20261010-part4.md` decisions 5–7 and "下一步 2"; `.scratch/decision-provider/handoff-20261011-part5.md` §6; `.scratch/stage3-step4/plan.md`.
- Source revision or identity: working tree of branch `fix/ticket-handoff` on top of `e3ba9f7`; the reviewed tree is frozen per round as a manifest under `rounds/round-NN/`.
- Fixed point: e3ba9f7 (light-code-review base for the script changes)
- Implementation scope: skills/project/project-init/scripts/bootstrap.py; skills/project/project-init/tests/test_project_init_behavior.py; scripts/verify_release_installation.py; scripts/verify_release_integrity.py; tests/test_release_installation.py; tests/test_release_integrity.py
- Approval state: approved
- Approval evidence: design §7 "用户确认" (2026-10-10); user in this session: step 3 accepted, "可以单独提交，然后开始第四步", map seam "同意" (CP-S4-001).

## Review Profile
- Profile: agent-skill
- Selection reason: admission of three model-invoked first-party Skills plus caller and contract changes; the two script changes also get light-code-review findings under the software rules.

## Original goal
Wire the three optional capabilities into the Light main flow so they fire when their event happens, and admit them into the collection: light-decide at bounded judgments, light-redirect when the approved plan no longer holds, light-html-plan when a plan page exists and work moves.

## User-visible outcome
In a project set up by project-init, the Agent writes a change proposal (instead of editing the plan) when the plan no longer holds, refreshes `plan.html` after recorded events, logs bounded judgments, and the collection lists 39 Skills.

## In scope
- The three packages under `skills/` (light-decide → `thinking/`, light-redirect and light-html-plan → `project/`), including step-4 edits to them (light-redirect description, map seam, optional section; light-html-plan E-001 and E-013).
- Caller and contract edits: light-implement (SKILL, WORKFLOW §7, EXAMPLES), project-review (SKILL, WORKFLOW, stopping-rules), project-spec, project-tickets (SKILL, TICKET-CONTRACT), decision-map MAP-CONTRACT, project-init (bootstrap.py, initialization-contract, tests), ask-light light-skill-map.json and its count tests.
- Collection docs and checks: README, CATALOG (en, zh), category READMEs, INSTALLATION, MAINTENANCE, CHANGELOG, tests/test_composition.py and the count tests, scripts/verify_release_installation.py, scripts/verify_release_integrity.py.
- Trigger-rate eval set and its two waves (`.scratch/stage3-step4/evals/`).

## Out of scope
- light-decide pointer lines in ask-light, agent-config and manuscript-ops and their script changes (step 5).
- Release, tag, push, fresh-install verification of the 39-package collection.
- Re-reviewing the three packages' step-3 content beyond the step-4 edits.

## Acceptance criteria
- AC-1 Admission. The three packages sit in their categories with metadata and invocation policy matching their model-invoked type; catalog, category READMEs, README, INSTALLATION, MAINTENANCE and CHANGELOG describe 39 packages without claiming a release or verified installation for the three; full suite and docs check pass.
- AC-2 Triggers. The eval set covers every capability with positive and negative cases on Claude Code, pi and Codex, never naming a Skill. After integration, light-redirect positives trigger at least as often as the baseline on every Host, the conflicting-ticket case (R4) is no longer edited directly on Claude Code, and no negative case gains a trigger on any Host. light-html-plan and light-decide rates are reported with their misses explained.
- AC-3 Standing line. project-init writes the light-redirect line inside its pointer once, upgrades an older pointer on rerun without duplicating it, preserves manual notes, and its tracker contract names `changes/`, `plan.html` and `plan-history/`. Focused and negative tests exist; light-code-review reports no open blocking finding.
- AC-4 Plan signals. The implementation report has `Plan gap:`; a `FAIL` verdict records `Cause: implementation | direction`; project-review intake and light-html-plan read them; light-implement and project-review call light-redirect on them.
- AC-5 Optional pointers. Every caller lists each capability it may call under `## Optional capabilities` with its fallback; composition edges cover them and a test fails when a fallback is missing.
- AC-6 Applying proposals. project-spec and project-tickets apply only an `approved` proposal, exactly its lines, and set `applied` only when both its SPEC and Tickets lines are done.
- AC-7 Map seam. A waiting proposal is a line under the map's `Not yet specified`; after the user's answer the line moves to `Decisions so far`; decision-map's contract says so.
- AC-8 Page fixes. light-html-plan lists in part 3 only tickets whose record names a user decision, describes a ticket waiting on another ticket in part 2, and links an in-card question to its part-3 card.
- AC-9 Release checks. The installation verifier expects 39 packages; a published manifest is counted against its own tag and an untagged candidate against the working tree, each with a test that fails when the behaviour is reverted.

## Required evidence
- Full suite and docs check output (observed).
- Trigger waves w1-baseline and w2-after: transcripts, prompts, `signals.py` scores (observed, per Host).
- Behaviour runs for AC-4, AC-6, AC-7, AC-8 on Claude Code, with pi or Codex where noted (observed).
- Mutation checks for the new tests (observed).
- light-code-review findings on the script changes (review).

## Required validation scenarios
- VS-1 Trigger waves: 14 cases × (Claude Code ×2, pi, Codex), before and after; projects isolated per run; fixtures built from frozen snapshots.
- VS-2 Map seam: a project with `map.md`; the user changes their mind → proposal + line under `Not yet specified`; the user approves in a resumed session → line under `Decisions so far`.
- VS-3 Apply: an approved proposal with a SPEC line only → `$project-spec` edits the SPEC and marks it applied; one with SPEC and Tickets lines → after `$project-spec` alone it is not yet applied.
- VS-4 Plan gap: `$light-implement` on a ticket that asks for something the SPEC rules out → report has a non-`none` `Plan gap:` and a proposal is written.
- VS-5 Page: ticket 03 carries a `BLOCKED` comment naming the user's SMS decision → part 3 lists it; ticket 02 waiting on review sits in part 2; the R3 card's flag links to its part-3 card.

## Constraints, assumptions, and risks
- Codex and pi are test hosts only; reviewers are fresh Claude subagents.
- One model family runs Producer, Claude Code subjects and reviewers; one fixture domain.
- Session usage limits interrupt Claude Code runs; interrupted runs are kept apart and rerun from the same snapshot.

## Approved exceptions
- AC-2, negative case D3 on pi: after integration one of three pi runs read light-decide's `SKILL.md` (before: none of three), with no decision row and no file written; light-decide's text is unchanged across the waves. Approved by the user on 2026-10-11 (answer to the C-003 question: "批准为例外"). Recorded as a limit in the verdict.
