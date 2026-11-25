---
name: acceptance
description: "Converge and verify code or non-code deliverables through bounded fresh-context review, repair, and execution evidence before issuing PASS, FAIL, or BLOCKED. Use before closing a ticket, pull request, or bounded draft (Inline scale), when signing off a full spec, milestone, skill package, or manuscript gate via init/run/resume (Charter scale), or when resuming an active .scratch/ acceptance run."
---

# Acceptance

`acceptance` is the unified convergence and sign-off discipline over code and non-code work. It drives deliverables through up to **3** bounded `review -> findings -> repair -> re-review` rounds using fresh-context reviewers, verifies real execution, test, or render evidence, and returns a terminal `PASS`, `FAIL`, or `BLOCKED` verdict.

`acceptance` complements Base workflow `code-review` without colliding with it: `code-review` inspects a git diff along `Standards` and `Spec` axes, while `acceptance` orchestrates bounded repair convergence, execution/render verification, and final sign-off.

## Pick the operating scale

Choose the lightest scale that matches the decision seam (honoring any default acceptance profile or strategy in `docs/agents/light-project.md` when present):

- **Inline scale** (default for a single ticket, pull request, or bounded non-code draft): holds target criteria and finding IDs in memory with **zero `.scratch/` file writes**, converges findings across up to 3 rounds, verifies execution/render outputs, and returns `PASS`, `FAIL`, or `BLOCKED`.
- **Charter scale** (`init`, `run`, `resume` for a full spec sign-off, milestone, `agent-skill` admission, or `manuscript-ops` Project gate): freezes an **Acceptance charter** and domain profile under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/` when standalone), runs bounded convergence, and dispatches a separate **fresh-context** independent **Evaluator** before recording a durable verdict and updating tracker tickets.

When invoked manually as `/acceptance init ...`, `/acceptance run ...`, or `/acceptance resume ...` (or when `.scratch/<feature>/acceptance/state.md` is active for the target), enter **Charter scale**.

## Shared invariants

1. **Fresh-context independence:** Launch every Critic/reviewer subagent and every Charter-scale Evaluator subagent with a **fresh context window**, never a fork of the active conversation or same-context role-play. If the host cannot provide a fresh subagent context, record `independence: unavailable` and return `BLOCKED` rather than simulating independent review.
2. **Role boundaries:** Reviewers and Evaluators are strictly read-only and never emit `PASS`, `FAIL`, or `BLOCKED`. Only the Producer modifies target files during an authorized in-scope repair. `acceptance` owns candidate dispositions (`confirmed`, `rejected`, `duplicate`, `out-of-scope`) and the terminal verdict.
3. **Reviewer resolution and Graceful fallback:**
   - **Software git diff:** Invoke `code-review` at the pinned fixed point when installed. When `code-review` is absent, run the built-in two-axis (`Standards` + `Spec`) fresh-context diff review in [reviewer-protocol.md](references/reviewer-protocol.md).
   - **Non-code or general deliverable:** Dispatch a fresh-context reviewer subagent with the four-field bounded packet and criteria checklist in [reviewer-protocol.md](references/reviewer-protocol.md), adding active profile axes when a profile applies.
4. **Anti-fake-convergence gate:** Issue `PASS` only when **both** conditions hold in the current run:
   - A fresh-context reviewer report returns `Findings: []` (with every prior `confirmed` finding verified `fixed` under its stable `F-###` ID).
   - Required tests, commands, runtime checks, or renders were actually executed and observed passing. Producer narrative, syntax-only checks substituting for required runtime/render verification, skipped scenarios, or reviewer timeouts never produce `PASS`.
5. **Three-round bound:** Run at most **3** convergence rounds by default. Start a new round only when at least one `confirmed` finding has a concrete, in-scope repair path. Stop early if two consecutive rounds make zero material progress or a repair requires changing approved requirements or scope.

## Inline scale workflow

Use Inline scale for routine single-ticket, PR, or draft convergence:

1. **Pin target and criteria in memory.** Capture the immutable target view (for software, verify `git rev-parse <fixed-point>` and non-empty `git diff <fixed-point>...HEAD`), approved acceptance criteria, explicit exclusions, and verification commands. If the target or criteria are missing or unreadable, return `BLOCKED` naming the missing input. Done when target identity and checkable criteria are explicit in memory with zero `.scratch/` writes.
2. **Verify baseline execution evidence.** Run the target's focused tests, CLI checks, or render inspections and record exact commands and observed outputs. Done when every required check has an observed outcome or an explicit environment blocker.
3. **Converge through up to 3 rounds.** Follow [reviewer-protocol.md](references/reviewer-protocol.md):
   - Dispatch a **fresh-context** read-only reviewer (`code-review` when installed for software diffs, or the built-in diff/criteria fallback) passing `Previous findings` (`none` on round 1; canonical `F-###` records on rechecks).
   - Validate each returned candidate as `confirmed`, `rejected`, `duplicate`, or `out-of-scope`. On `REVIEW-ERROR`, stop and return `BLOCKED`.
   - When `confirmed` in-scope findings exist and rounds remain, perform the minimal bounded repair, re-run verification commands, and re-run a **fresh-context** reviewer on the updated target.
   - If a gap proves the approved spec or ticket itself is wrong or contradictory, halt repairs immediately and classify `FAIL` (`Cause: direction`).
   Done when a fresh-context review reports zero open `confirmed` blocking findings and verification checks pass, or a stopping condition triggers.
4. **Return the verdict.** Report `PASS`, `FAIL` (including `Cause: implementation | direction`), or `BLOCKED` with rounds run, reviewer provenance, stable `F-###` dispositions, and executed verification evidence. On `FAIL` with `Cause: direction`, invoke `redirect` with the failure summary (Graceful fallback: if `redirect` is unavailable or declined, report the broken assumption and affected spec/ticket sections directly and stop).

## Charter scale workflow (`init` | `run` | `resume`)

Use Charter scale for full specs, milestones, skill package admission, and manuscript gates. Read [charter-workflow.md](references/charter-workflow.md) and [charter-and-evidence.md](references/charter-and-evidence.md) before writing durable records under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/`):

1. **`init`:** Inspect the approved source (`spec.md`, ticket graph, or brief) and `docs/agents/light-project.md` (when present). Select the domain profile from [generic.md](references/profiles/generic.md), [software.md](references/profiles/software.md), [manuscript.md](references/profiles/manuscript.md), [agent-skill.md](references/profiles/agent-skill.md), or [specification.md](references/profiles/specification.md). Freeze `charter.md` (including `Fixed point` and `Implementation scope` for `software`) and set `state.md` to `READY`. Missing or unapproved baseline sources return `BLOCKED`.
2. **`run`:** Collect labeled Producer evidence (`source`, `structural`, `behavioral`, `installation`, `invocation`, `runtime`, `manual`, `review`), drive up to 3 bounded convergence rounds via [reviewer-protocol.md](references/reviewer-protocol.md), and record stable `F-###` dispositions in `findings.md`. Once Critic findings converge (or no bounded in-scope repair path remains), dispatch a separate **fresh-context** read-only **Evaluator** to audit `charter.md`, `findings.md`, and round evidence criterion by criterion.
3. **Closeout, `redirect`, and tracker sync:** Write `verdict.md` first, verify singleton transaction fields (`Charter revision`, `Profile`, `Round`, `Verdict`, plus `Reviewed implementation revision` for `software` and `Cause: implementation | direction` on `FAIL`), then set `state.md` to terminal (`PASS`, `FAIL`, or `BLOCKED`). Update tracker issues per `docs/agents/issue-tracker.md` (`PASS` resolves local tickets with `## Answer` and updates `map.md` when present; `FAIL`/`BLOCKED` appends `## Comments`). When `Verdict: FAIL` has `Cause: direction`, invoke `redirect` with the `verdict.md` path (with inline handoff fallback if `redirect` is unavailable).
4. **`resume`:** Read `state.md`, `charter.md`, `findings.md`, and the latest round directory, verify transaction coherence (`BLOCKED` on conflict), refresh only stale or missing evidence, and continue from the recorded next action without rewriting prior round history.

## References

- [reviewer-protocol.md](references/reviewer-protocol.md): fresh-context reviewer packets, `code-review` delegation and built-in diff fallback, absorbed generic criteria review, normalized `F-###` schema, and Evaluator packet.
- [charter-workflow.md](references/charter-workflow.md): `init`/`run`/`resume` lifecycle, state machine, stopping rules, safe closeout ordering, `redirect` trigger, and tracker closeout.
- [charter-and-evidence.md](references/charter-and-evidence.md): `charter.md`, `state.md`, `findings.md`, `verdict.md`, `changes.md`, evidence labels, and rubric PASS gate.
- Profiles: [generic.md](references/profiles/generic.md), [software.md](references/profiles/software.md), [manuscript.md](references/profiles/manuscript.md), [agent-skill.md](references/profiles/agent-skill.md), [specification.md](references/profiles/specification.md).
