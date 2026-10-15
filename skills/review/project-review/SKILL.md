---
name: project-review
description: Determine whether a completed project satisfies its approved target by freezing an acceptance baseline, composing reviewers, and issuing a final PASS/FAIL/BLOCKED. Use when project delivery needs final acceptance.
---

# Project Review

`project-review` is the **project-level final acceptance** capability. It is
model-invoked and may also be invoked by hand. It freezes the acceptance
baseline, drives read-only reviewers through `review-loop`, and issues the
final `PASS`, `FAIL` or `BLOCKED`. The Producer makes authorized repairs;
`project-review` never repairs artifacts itself.

## When to use

- The project has an approved target (SPEC, brief or ticket graph) and a
  bounded implementation to check: after `light-implement` or a batch of
  tickets, before `release-workflow`.
- Skill admission, when the acceptance source is a package's `SKILL.md` and
  its evidence.

When `docs/agents/light-project.md` exists, start from its review profile and
acceptance strategy, then freeze the actual acceptance source.

## Core behavior

1. Freeze the acceptance baseline and pick a Profile: [generic.md](references/profiles/generic.md),
   [software.md](references/profiles/software.md),
   [manuscript.md](references/profiles/manuscript.md),
   [agent-skill.md](references/profiles/agent-skill.md) or
   [specification.md](references/profiles/specification.md).
2. Invoke reviewers through `review-loop`: `generic-review` for ordinary
   artifacts, `light-code-review` for software diffs, an accepted domain
   reviewer when one exists. Reviewers only return findings.
3. Validate findings, direct only bounded in-scope repairs, and ask a fresh,
   independent Evaluator.
4. Issue the verdict when the stopping rules are met.

## Entry modes

Use one of three modes; details are in
[WORKFLOW.md](references/WORKFLOW.md):

- `init`: freeze the acceptance baseline and Profile before review.
- `review`: run one bounded evidence, critique, validation, repair, and
  evaluation round.
- `resume`: continue the next unfinished recorded action without rewriting
  prior evidence.

## Handoff and stop

- `PASS`: every frozen criterion has correctly labeled evidence and the fresh
  Evaluator accepts the baseline.
- `FAIL`: a frozen condition is unmet and cannot be resolved through a
  confirmed, in-scope, bounded repair.
- `BLOCKED`: required baseline, authority, environment, evidence, access, or
  independent context is unavailable; records conflict; or the repair limit
  stops safe convergence.

Default maximum is three rounds. Record durable state under
`.project-review/`; see [WORKFLOW.md](references/WORKFLOW.md) for the exact
state tree and resume rules. When the acceptance source is a tracker ticket,
resolve it after `PASS` and comment the blocker after `FAIL` or `BLOCKED`
([Ticket closeout](references/WORKFLOW.md#ticket-closeout)).

## Optional capabilities

- **A `FAIL` with `Cause: direction`** → after ticket closeout, call
  `light-redirect` with the `verdict.md` path. Unavailable or declined → the
  ticket's `FAIL` comment is the handoff.
- **`.scratch/<feature>/plan.html` exists** → after the verdict and ticket
  closeout, call `light-html-plan` to refresh it. Missing page or capability →
  skip.

## References

- [WORKFLOW.md](references/WORKFLOW.md) — init/review/resume, role packets, state tree.
- [acceptance-charter.md](references/acceptance-charter.md) — frozen baseline and Profile fields.
- [evidence-protocol.md](references/evidence-protocol.md) — evidence labels and records.
- [finding-schema.md](references/finding-schema.md) — finding identities, dispositions, registry.
- [review-rubric.md](references/review-rubric.md) — Core checks and Profile dimensions.
- [subagent-protocol.md](references/subagent-protocol.md) — Critic/Evaluator packets and independence.
- [stopping-rules.md](references/stopping-rules.md) — verdict transitions and repair limit.
- [migration.md](references/migration.md) — history only; not needed at runtime.
