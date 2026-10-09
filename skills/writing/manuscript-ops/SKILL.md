---
name: manuscript-ops
description: Write or revise bounded documents with appropriate source, content, image and format checks; manage resumable manuscript projects when batches, locked editions or lifecycle gates are actually required. Use for notes, SOPs, reports, manuals, books and derived formats.
---

# Manuscript Ops

Choose the writing workflow from the task's management needs. Determine content
review and format checks separately. Preserve source authority, approved scope,
existing files and the identity of the assigned writer.

## Select one route

1. Read the current request, supplied materials, deliverables, relevant
   instructions and already-confirmed decisions. Measure the manuscript task,
   not unrelated workspace files. An existing approved Project keeps its contract.
2. Use [routing.md](references/routing.md) to select Quick, Structured or Project.
   Content risk raises review requirements; unknowns remain explicit. Clarify
   only a missing decision or source that materially affects the task.
3. When semantic interpretation is useful and a structured decision MCP is
   exposed, follow [semantic-routing.md](references/semantic-routing.md).
   Reuse the Host's tools; missing tools or an uncertain answer leave the current
   agent to judge from evidence. Do not install a service or require setup.
4. The optional read-only assessor accepts task-grounded answers:

   ```text
   python scripts/assess_project.py --root <output-or-project-root> --answers <routing-input.json>
   ```

   New snapshots use `needs-v2`; old snapshots without a policy use `score-v1`
   when validating their existing gates. Read only the resources of the chosen route.

## Quick or Structured: write, check and return

- **Quick:** complete the bounded low-risk text edit and applicable content checks.
- **Structured:** keep a compact task brief (purpose, source authority, outputs,
  required review) in the task context or an existing record. Write the whole
  document; outline and body may be checked together.
- Inspect sources and resolve material conflicts. Keep unknown technical facts
  pending. A rewrite cannot acquire new operating instructions, claims or
  approval through wording changes.
- Use [formats.md](references/formats.md) and the selected format provider.
  Run the content, safety/privacy/legal, terminology, image and layout checks
  the task requires. For DOCX/PDF and other layout-sensitive output, render it
  in a real application and inspect the pages. Report unavailable checks honestly.
- A delegated writer inherits the confirmed materials, output location and
  authorization of its bounded task. Reviewers stay read-only. Create only
  the necessary output/QA files in an authorized location.
- Deliver the completed artifact, observed checks and precise unresolved items;
  **return here**. These routes do not require generic `project-init`, a Project
  Profile, a Review Charter, Jujutsu, gate receipts or `validate_state.py`.

## Project: preserve the governed lifecycle

Read [Project route](references/project-route.md) before initializing,
resuming or advancing Project gates. Reuse an approved Brief and existing state;
hand off only decisions or generic bootstrap actually missing. `clarify` is the
user-facing entry to `socratic`, not an extra consecutive discovery step.

The assigned writer owns the manuscript. `project-review` owns independent
acceptance and verdicts; this Skill supplies the manuscript evidence and consumes
them. An existing authorization remains valid within its scope. Later snapshot
approval and other user-invoked Skill calls retain their own boundaries.

Use the supported declared version backend and [version-control.md](references/version-control.md).
Do not substitute a timestamp snapshot for receipt-bound gates or repeatedly
produce records that cannot remove a known dependency failure. On a blocked gate,
read [failure-recovery.md](references/failure-recovery.md) and return the precise
state, preserved evidence and smallest resume condition to the caller.

## Resources

- [State and templates](references/state-model.md): Project schema, provenance,
  receipts and compatibility; templates are linked from the Project workflow.
- [Source and format contracts](references/formats.md): document inputs,
  conversion lineage, format capabilities, real rendering and QA boundaries.
- [Review profile](references/review.md): manuscript axes for Project acceptance.
- [Handoffs](references/handoffs.md): exact dependency calls and resume conditions.
