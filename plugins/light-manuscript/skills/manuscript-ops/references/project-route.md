# Project manuscript workflow

Read only after selecting `Project` or resuming an existing approved `Project` state. `Quick` and `Structured` tasks do not use this lifecycle.

## 1. Accept or scope the ManuscriptBrief

1. **Reuse any approved Brief directly**: if the user supplies an approved `ManuscriptBrief` (or existing planning record mapped to the Brief contract) with resolved scope, audience, source authority, deliverables, and acceptance criteria, proceed directly to initialization. Do not require any external discovery skill.
2. **Resolve genuinely open scope**: if material scope, source authority, or deliverable decisions are still open:
   - Settle bounded open questions directly with the user and record them in [manuscript-brief.md](../assets/templates/manuscript-brief.md), or
   - Suggest Base workflow `/grill-with-docs` or `/to-spec` when installed for deep multi-session scoping (Graceful fallback: run structured Brief Q&A directly in session).
   - When external primary-source gathering is needed before locking scope, invoke `research` when available, or dispatch a primary-source research subagent in a **fresh context window**.
3. **Check project preferences**: if `docs/agents/light-project.md` exists (created by `/light-setup`), honor its `Decision data` limit and default acceptance profile. If absent, continue standalone using `Decision data: on-device` and `Profile: manuscript` (optionally mentioning `/light-setup` without blocking).

## 2. Initialize or map the project

Ask for human approval of the initialization gate once the Brief is approved. Create the standard structure in [project-layout.md](project-layout.md) for a new project, or keep every existing file in place and map logical roles inside `project-profile.json`.

Copy and populate only the templates needed for the active phase:

- [Manuscript Brief](../assets/templates/manuscript-brief.md)
- [Lifecycle State](../assets/templates/state.json)
- [Project Profile](../assets/templates/project-profile.json)
- [Batch Manifest](../assets/templates/batch-manifest.json)
- [Manuscript Review Profile](../assets/templates/review-matrix.json)
- [Gate Receipt](../assets/templates/gate-receipt.json)
- [Source Register](../assets/templates/source-register.tsv)
- [Platform Capability Snapshot](../assets/templates/platform-capabilities.json)
- [Format QA Record](../assets/templates/format-qa-record.json)

Follow [state-model.md](state-model.md). Wrap every configurable `ProjectProfile` leaf with `value`, `origin` (`资料发现`, `用户决定`, or `规则推导`), and `evidence`. Store an immutable copy of the baseline Profile under `.manuscript-ops/snapshots/` and bind it in the `baseline` receipt.

## 3. Advance through semantic layers and batches

Follow the semantic order in [lifecycle.md](lifecycle.md):

```text
authoritative sources -> reference-only material -> optional incoming draft
-> outline -> working draft -> frozen review draft -> candidate
-> locked source -> translation/derived edition -> final -> archive
```

Keep the assigned writer as the sole prose author. Partition batches by semantic cohesion, prerequisite order (respecting **Concept Grounding**), source dependencies, risk, and reviewable context volume. Freeze `input_snapshot` before activating a batch, keep at most one `active` or `review` batch at a time, and accept prerequisites before advancing dependents.

## 4. Run `acceptance` at manuscript milestones

Construct `review-matrix.json` using [review.md](review.md). All eight non-image axes are mandatory positive-or-negative audits on `Project`; add `images` whenever the Source Register includes `image-scan`, PPTX is a deliverable, or the active batch requires it.

At `outline`, accepted `batch`, `candidate`, `source-lock`, and `final` milestones, invoke `acceptance` at **Charter scale** (`init`, `run`, `resume`) with `Profile: manuscript` ([handoffs.md](handoffs.md)):

- Store the frozen Acceptance charter and JSON verdict envelope (`provider: "acceptance"`, `profile: "manuscript"`) under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/` or `.manuscript-ops/reviews/`).
- Ensure both convergence reviewers and the independent Evaluator run in **fresh context windows**.
- If `acceptance` returns `FAIL` with `Cause: direction`, invoke `redirect` to draft a Change proposal under `.scratch/<feature>/changes/` and wait for human Brief/charter approval before resuming.

## 5. Probe capabilities and record per-deliverable Format QA

Read [formats.md](formats.md) and [format-registry.json](../assets/format-registry.json). Probe capabilities without modifying the environment:

```text
python scripts/probe_capabilities.py --platform-capabilities <path>
```

Use [platform-capability-map.json](../assets/platform-capability-map.json) to map host tools to logical operations. Generate one artifact-bound QA record per Brief deliverable path, including reproducible generation lineage, coverage counts, Brief-authorized sampling (when `sampled`), distinct locked-source semantic comparison, and distinct round-trip output where applicable. Syntax checks never substitute for real rendering and visual inspection.

## 6. Seal gates and validate state

Create dated Jujutsu gate bookmarks (`brief-approved-YYYY.MM.DD`, `baseline-*`, `framework-approved-*`, `source-locked-*`, `final-approved-*`, `publish-approved-*`) and mutable `current-*` aliases per [version-control.md](version-control.md). Use `scripts/next_version.py` on same-day collisions.

Before pausing or closing any milestone, run:

```text
python scripts/validate_state.py --root <project-root> --check-vcs
```

Report status accurately (`implemented`, `verified`, `independently accepted`, `blocked`, `not tested`, `out of scope`). Follow [failure-recovery.md](failure-recovery.md) whenever a check returns `DEGRADED` or `BLOCKED`.
