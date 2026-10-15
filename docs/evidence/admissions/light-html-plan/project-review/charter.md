# Acceptance Charter

## Revision
- Charter revision: 3
- Supersedes: revision 2 (archived as `baselines/charter-r2.md`): AC-3 "expands to" → "shows" per CP-003. Revision 2 superseded revision 1 (archived as `baselines/charter-r1.md`), after user decision CP-002 (built-in visual system). Revision 1 history: The earlier Codex review under `.scratch/light-html-plan/.project-review/` (Charter revision 7, CP-005) stays as history; its user feedback is an input, its A13 gate (Codex native discovery) is carried as a limitation below.
- Created at: 2026-10-10

## Acceptance baseline
- Source: `.scratch/decision-provider/design-stage3.md` §4 and §7 (Q8, Q8 附, 准入, 触发：推广); handoff `.scratch/decision-provider/handoff-20261010-part4.md` step 1; user browser feedback `.scratch/light-html-plan/evidence/real-spec-resume/browser-feedback-20261010.md`.
- Source revision or identity: candidate `.scratch/light-html-plan/candidate/light-html-plan/` as hashed in `rounds/round-01/candidate-manifest.txt` (later repairs get their own manifests). Pre-change baseline: `rounds/round-01/baseline-manifest.txt`.
- Approval state: approved
- Approval evidence: design-stage3.md §7 "用户确认" (2026-10-10); handoff part 4 names this step as next.

## Review Profile
- Profile: agent-skill
- Selection reason: model-invoked first-party Skill that reads and writes project files; not eligible for the fast track (design §4 H5).

## Original goal
A model-invoked capability that turns a Light project's records into one offline HTML page showing what the project is, how far it got, what waits on the user, what changed since approval, and what the system judged — and refreshes that page safely after recorded events.

## User-visible outcome
The user opens `.scratch/<feature>/plan.html` and, mostly from diagrams and short lines, sees the project's state in five fixed parts, in plain words.

## In scope
- The package files in the manifest.
- `docs/agents/issue-tracker.md` lines for `plan.html` and `plan-history/`, and the `$decision-map` rename.

## Out of scope
- `bootstrap.py` tracker template (moved to the step 4 batch, which already changes `bootstrap.py`).
- Caller pointer lines, trigger-rate eval sets, admission into `skills/` (step 4).
- Whether the page reads plainly and looks good: the user judges this by reading the page. Agents report observations only.

## Acceptance criteria
- AC-1 Five parts. Every created page has the five parts in the fixed order; an empty part says "目前没有" (or the reader-language equivalent).
- AC-2 Part 1. Framework diagram where each block shows the component name and what changes, with change size (重点改动/小改/新能力/不改) as text and colour.
- AC-3 Part 2. Each work item shows 在做什么/已完成/没完成/证据; 写完, 验收 and 发布 are shown separately and never widened (a resolved ticket is not project acceptance or release).
- AC-4 Parts 3–5. `proposed` proposals and open decisions are in part 3; proposals with status and approver in part 4; logged judgments in part 5 with the plain question first, low-confidence/fallback first, ids only as source, and an unused (`applied: false`) answer not presented as what the work followed.
- AC-5 Source fidelity. No invented status, percentage or date; sources listed with path, date and SHA-256; source files byte-unchanged.
- AC-6 Refresh. Writes the stable entry at `.scratch/<feature>/plan.html`; before replacing, saves the exact old bytes in `plan-history/`; keeps design and unrelated content; on an unreadable source leaves the old entry unchanged and reports it.
- AC-7 Single offline file: no external requests, works at 1440px and 390px, light and dark, no horizontal overflow, keyboard-usable disclosures.
- AC-8 Boundaries: no approvals, no ticket or proposal state change, no user-invoked Skill started, no install, no publish; never declares its own writing or look as passed.
- AC-10 Visual system. Pages inline `assets/plan.css`, use only its classes, follow the skeleton's layouts (hero with the waiting card on the right; part 1 and part 2 cards side by side, aligned by component when tickets map one-to-one; decision, change and judgment cards side by side), and collapse to one column at phone width.
- AC-9 Package quality per agent-skill Profile: metadata on both surfaces, links, short SKILL.md, references, writing style, assertion-bearing tests with negative controls, clean install and discovery, attribution updated.

## Required evidence
- Structural: package tests; repo docs check and full suite.
- Installation: clean copy in fresh projects' `.claude/skills/`, discovered by Claude Code.
- Invocation: positive triggers without naming the Skill, and a non-trigger.
- Behavioral: VS-1..VS-5 on the current text.
- Rendering: built-in browser at 1440px and 390px, light and dark, on the VS-1 page.
- Review: generic-review Critic, a second Critic on pi (another model family), then a fresh Evaluator on Codex (gpt-6.1-sol, high).
- Executable axis: not applicable — no scripts; tests read package files only.

## Required validation scenarios
Fixture domain: a neighbourhood tool-lending library (deliberately unlike the resume-website and payment-reminder examples).
- VS-1 Full records, not named: spec, three tickets (one resolved after PASS, one claimed with an implementation report, one blocked), two change proposals (one applied, one proposed with an open decision), a decisions.md with an unused typed answer and a self-judgment, a PASS verdict. Ask for an HTML overview of where the project stands → page at `.scratch/<feature>/plan.html` meeting AC-1..AC-5, AC-7.
- VS-2 Sparse records: only spec.md → parts 2–5 say none so far; no invented progress.
- VS-3 Refresh after an event: VS-1 project plus a new implementation report → caller asks to refresh → history copy byte-equal to the old page; new state shown; design kept.
- VS-4 Failed refresh: a needed source is unreadable → old page unchanged, failure reported.
- VS-5 Non-trigger: a plain request to summarise the SPEC in bullets → no invocation, no HTML.
- Key boundaries (VS-1, VS-3) run twice.

## Constraints, assumptions, and risks
- Hosts: Claude Code 2.1.296 (claude-opus-5-5), pi 1.1.0 (Gemini default), Codex CLI 0.162.0-alpha.17.2 with `gpt-6.1-sol` at reasoning effort high (the only Codex model the user allows). Codex discovery addresses the old A13 gap.
- Producer, Critic and Evaluator share a model family.

## Approved exceptions
- None
