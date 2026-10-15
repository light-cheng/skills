# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-10-10T05:34:00Z

## Acceptance baseline
- Source: .scratch/decision-provider/design-stage3.md §1.2, §3 and §7 (Q6 name, Q7 no small-change exemption), plus the user decisions recorded in .scratch/decision-provider/handoff-20261010-part3.md
- Source revision or identity: candidate .scratch/light-redirect/candidate/light-redirect/ as hashed in rounds/round-01/candidate-manifest.txt (later repairs get their own manifests)
- Approval state: approved
- Approval evidence: design-stage3.md §7 "用户确认" (2026-10-10); user "go-ahead" for stage 3 step 2 (2026-10-10)

## Review Profile
- Profile: agent-skill
- Selection reason: new first-party model-invoked Skill package that writes project files; not eligible for the fast track

## Original goal
A model-invoked capability that turns a discovered direction problem after SPEC approval into a written change proposal the user approves, without changing the SPEC, tickets or code itself.

## User-visible outcome
When the plan should change, the user gets one readable proposal under `.scratch/<feature>/changes/`, is asked to approve or reject it, and is told which skill applies it.

## In scope
- The package files in the manifest and its contract with callers.

## Out of scope
- Teaching project-spec / project-tickets to apply proposals and set `applied` (stage 3 step 4).
- Caller pointer lines; light-html-plan reading `changes/`; admission into skills/ (joint batch).
- decision-map (unchanged; it owns the pre-SPEC fog).

## Acceptance criteria
- AC-1: Triggers. Fires for the four direction triggers (missing/wrong requirement found in implementation, review failure caused by direction, user's new idea or change of mind mid-work, conflicting tickets). A local fix is handed back with no proposal.
- AC-2: Proposal file. Written to `.scratch/<feature>/changes/<NN>-<slug>.md` with the next unused NN, the template's fields and headings, plain words, and a locator or quote for each claim; names every affected SPEC section, ticket action, re-acceptance and what stays unchanged.
- AC-3: Status. Starts `proposed`; becomes `approved` or `rejected` only from the user's explicit answer, recorded under `## Comments`; `applied` is set by the applying skill, never by light-redirect.
- AC-4: No edits. Never edits the SPEC, tickets, code or a Charter; no size exemption — even a "small" change goes through a proposal.
- AC-5: Map pointer. When `.scratch/<feature>/map.md` exists, appends one pointer line to `Decisions so far` once; never creates a map.
- AC-6: Handoff. Approved + Charter under `.project-review/` → recommends project-review's Change Proposal; otherwise recommends `$project-spec` / `$project-tickets` with the proposal path; unsettled user decision → recommends `$project-clarify`; rejected → back to caller. Recommends, never starts, user-invoked skills.
- AC-7: light-decide is optional for the direction question; its absence changes nothing.
- AC-8: Caller contract (optional, caller records first, returns only, grants nothing) stated in the package.
- AC-9: Package quality per agent-skill Profile (metadata on both surfaces, links, short SKILL.md, references, writing style, assertion-bearing tests with negative controls, clean install and discovery).

## Required evidence
- Structural: package tests, links, metadata.
- Installation: clean copy in fresh projects' `.claude/skills/`, discovered by Claude Code.
- Invocation: positive triggers (skill not named) and a non-trigger.
- Behavioral: VS-1..VS-6.
- Review: generic-review Critic, fresh Evaluator.
- Executable axis: not applicable — no scripts; tests read package files only.

## Required validation scenarios
- VS-1 success (implementation trigger, not named): ticket 02 has a BLOCKED implementation report showing a SPEC requirement cannot hold → proposal `changes/01-...md`, status `proposed`, approval asked; SPEC and tickets unchanged; no map created.
- VS-2 approval with map and Charter: project has `map.md` and `.project-review/charter.md` whose source is the SPEC → proposal + one map pointer; after the user's explicit "yes" in a resumed session → `approved`, comment line with the user's words, recommends project-review's Change Proposal; SPEC, tickets and Charter unchanged.
- VS-3 user's new idea mid-work (not named) → proposal, `proposed`.
- VS-4 local fix → no proposal, handed back.
- VS-5 boundary: user asks to "just edit the SPEC, it's tiny" via light-redirect → proposal instead of an edit.
- VS-6 missing dependency: light-decide is not installed in any scenario; no run fails or blocks because of it.
- Non-trigger: unrelated request → no invocation.
Cleanup: temp projects deleted after the Evaluator.

## Constraints, assumptions, and risks
- Host: Claude Code 2.1.296 on macOS only.
- `claude -p` cannot answer mid-run; approval is tested by resuming the session with the user's reply.

## Approved exceptions
- None
