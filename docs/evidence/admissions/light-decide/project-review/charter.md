# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-10-09T21:55:00Z

## Acceptance baseline
- Source: .scratch/decision-provider/design-stage3.md §1.2 and §7 (decision table), plus user decisions recorded in .scratch/decision-provider/handoff-20261010-part3.md ("阶段 3 第 1 步进展")
- Source revision or identity: candidate .scratch/light-decide/candidate/light-decide/ as hashed in rounds/round-01/candidate-manifest.txt
- Approval state: approved
- Approval evidence: design-stage3.md §7 "用户确认" (2026-10-10); user chat 2026-10-10: default data limit on-device; tie-break by nearest destination; one source per judgment, comparison only on labeled eval sets; "go-head" for full review

## Review Profile
- Profile: agent-skill
- Selection reason: new first-party model-invoked Skill package admission (AGENTS.md "New admission"; not eligible for fast track because it reads and writes project files)

## Original goal
A shared model-invoked capability that any workflow Skill can call when it reaches a bounded discrete judgment. It picks an allowed, verified decision source, applies the user's calibration policy, logs the judgment, and returns a normalized result, without granting authority.

## User-visible outcome
Workflow Skills can hand a bounded judgment to light-decide; the user can see every judgment in `.scratch/<feature>/decisions.md` in plain words, with how sure the source was and where the data went.

## In scope
- The package files listed in the manifest.
- Its contract with callers (optional, caller records first, returns only, grants nothing).

## Out of scope
- Caller pointer lines (`## Optional capabilities`) in other Skills (stage 3 step 4).
- Script changes in ask-light, agent-config, manuscript-ops (step 5).
- Catalog/README/discovery-test updates for admission (done after PASS).
- Accuracy of any decision backend.

## Acceptance criteria
- AC-1: Scope. Judges only bounded judgments (choice / yes_no / score); leaves user decisions, approvals of SPEC/ticket graph/change proposals, finding dispositions, PASS/FAIL/BLOCKED and permissions to the user or evidence; with one legal option asks no source.
- AC-2: Data limit. Reads `Decision data: on-device | private-network | third-party | off` from `docs/agents/light-project.md`; missing line = on-device; `off` is hard and cannot be lifted or widened by the user in the run; the user may narrow it or name a source within it; unknown destination counts as third-party.
- AC-3: Source selection. Order: user-named source → calibrated → uncalibrated (asked, recorded, own judgment final) → self-judgment; ties broken by nearest destination; exactly one source per judgment; availability needs evidence from this run (not config alone, not `loaded:false`).
- AC-4: Two call paths (script → SDK; agent → MCP → direct or to script); no URL/key/local model name in the package.
- AC-5: Normalized result with method (`typed-decision | self-judgment`), data destination, backend, `confidence` computed from probabilities, `provider_confidence` kept raw, score by expected value not argmax, `applied`, `fallback_reason`, `final`.
- AC-6: Policy. User-level `~/.config/light/decision-policy.json`, read-only for light-decide; calibrated means `min_confidence` + non-empty `calibration` per question id; applied only when calibrated and confident; timeout/error/malformed fall back without retry loops.
- AC-7: Log. One parseable row per judgment in `.scratch/<feature>/decisions.md`; plain-word question; never rewritten; no automatic back-fill of correctness; no active feature → row returned instead of written.
- AC-8: Caller contract (design §1.2 rules 1–4) stated in the package itself; never starts a user-invoked Skill; grants nothing.
- AC-9: Package quality per agent-skill Profile: valid frontmatter and metadata (model-invoked on both surfaces), resolving links, short SKILL.md with details in references, AGENTS.md writing style, assertion-bearing package tests with a negative control, clean-copy install and discovery.

## Required evidence
- Structural: package tests; link resolution; frontmatter/metadata (structural).
- Installation: clean copy into a fresh project's `.claude/skills/`, discovered by Claude Code (installation).
- Invocation: positive trigger and non-trigger observed in a fresh Claude Code run (invocation).
- Behavioral: VS-1..VS-5 in fresh Claude Code runs (behavioral).
- Review: generic-review Critic findings; fresh Evaluator (review).
- Executable axis: not applicable — the package ships no scripts; its tests read only its own files.

## Required validation scenarios
- VS-1 success: no `Decision data:` line, local decision MCP available, no policy file → one on-device source asked, answer recorded, own judgment final with reason `uncalibrated`, one row logged.
- VS-2 boundary: `Decision data: off` and the user asks to use the decision MCP → no source asked, reason `off`.
- VS-3 boundary: a caller asks light-decide to decide PASS/FAIL or approve a SPEC → declines and hands back.
- VS-4 missing dependency: no decision source available → self-judgment, reason `unavailable`, no BLOCKED, no install request.
- VS-5 no-op: only one legal option → returned without asking a source.
Cleanup: temp projects deleted; no write to ~/.config/light.

## Constraints, assumptions, and risks
- Host for discovery is Claude Code 2.1.296 on this machine; other Hosts are not observed (limitation, recorded).
- The decision MCP (opendecider) is user-level; runs must not change MCP config.
- Behavioral runs use a model; outcomes are observations, not guarantees.

## Approved exceptions
- None
