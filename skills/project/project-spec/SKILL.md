---
name: project-spec
description: Turn already-clarified outputs from project-clarify or decision-map into a formal project SPEC without reopening an interview. Use only when the user explicitly invokes $project-spec; it returns to project-clarify when a blocking user decision remains and hands off to project-tickets when ready.
disable-model-invocation: true
---

# Project Spec

`project-spec` is an explicit, user-invoked planning stage. Run it only after
an explicit `$project-spec` request. It turns already-clarified material into
one formal SPEC that `project-tickets` can slice.

## Core behavior

1. **Gather and validate** the clarification handoff or map answers plus a
   light repo inspection. When `docs/agents/light-project.md` exists, consume
   its goal, outputs, domain-context locators, and working area before reading
   the named glossary, ADRs, and seams. Use settled facts and decisions as-is.
2. **Check the blocking-decision gate.** If a truly blocking user-owned
   decision remains, stop spec work and return to `project-clarify` (or the
   map) with the exact blocker and context pointer.
3. **Synthesize and publish** one bounded SPEC using
   [OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md), to
   `.scratch/<feature>/spec.md`. Confirm the publish when seams affect scoping.
4. **Stop and recommend** explicit `$project-tickets`.

**Applying a change proposal.** When the user passes an `approved` proposal
from `.scratch/<feature>/changes/`, apply exactly its `SPEC:` line to the
published SPEC. When its `Tickets:` line is `none` or a
`Tickets applied` line is already under `## Comments`, set `**Status:**` to
`applied` with a status line; otherwise add `- <date> SPEC applied — project-spec`.
A proposal in any other status, or a change it does not list, goes back to the
user unchanged.

```text
project-spec → project-tickets
```

## Optional capabilities

- **`.scratch/<feature>/plan.html` exists** → after publishing, call
  `light-html-plan` to refresh it. Missing page or capability → skip.

## References

- [WORKFLOW.md](references/WORKFLOW.md) — full step sequence and seam check.
- [OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md) — required SPEC shape.
- [EXAMPLES.md](references/EXAMPLES.md) — dog-food and boundary examples.
