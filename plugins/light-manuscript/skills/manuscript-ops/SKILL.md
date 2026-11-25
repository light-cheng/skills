---
name: manuscript-ops
description: Write, revise, or govern manuscripts and bounded documents with source authority, concept grounding, format QA, and resumable lifecycle gates. Use for notes, SOPs, reports, manuals, technical books, translations, and multi-format deliverables (Markdown, DOCX, PDF, HTML, EPUB, PPTX).
---

# Manuscript Ops

Match writing governance to actual management needs. Separate workflow ceremony from content risk and format QA. Preserve source authority, approved scope, existing project files, and the identity of the assigned writer.

## 1. Select one route (`needs-v2`)

1. Read the current request, supplied materials, target deliverables, project rules, and confirmed decisions. Measure the manuscript task itself rather than unrelated workspace file counts. Existing approved `Project` state keeps its contract.
2. Apply [routing.md](references/routing.md) under `needs-v2` to choose `Quick`, `Structured`, or `Project`. High-stakes facts raise review requirements without forcing `Project` lifecycle overhead. Clarify only missing facts or decisions that materially change scope, authority, or deliverables.
3. When semantic interpretation of borderline task wording could change the route, optionally evaluate question ID `manuscript-ops/route` through `decide` ([semantic-routing.md](references/semantic-routing.md)). If `decide` is unavailable, `off`, uncalibrated, or uncertain, keep the task-grounded route.
4. Optionally record a deterministic read-only routing snapshot:

   ```text
   python scripts/assess_project.py --root <output-or-project-root> --answers <routing-input.json>
   ```

   Read only the references required by the selected route.

## 2. Quick or Structured: write, verify, and return

- **Quick**: complete the bounded low-risk edit, check factual and wording preservation, and return.
- **Structured**: hold a compact brief in context (audience and prerequisites, source authority, deliverables, required review axes) and draft the complete document.
- Enforce **Concept Grounding** ([review.md](references/review.md#concept-grounding)): every concept a section leans on must appear in the target-reader prerequisites or be grounded in an earlier section.
- Inspect sources and keep unresolved facts explicit; rewording never creates new operational claims or approvals.
- Follow [formats.md](references/formats.md) for the target format. Run required structural, safety/privacy/legal, terminology, image, render, and visual checks. For layout-sensitive deliverables (DOCX, PDF, EPUB, PPTX, HTML), render in a representative application and inspect pages or slides; report unavailable checks honestly.
- When bounded convergence is warranted, run `acceptance` at **Inline scale** (up to 3 review-and-repair rounds using a reviewer subagent started with a **fresh context window**; Graceful fallback: review against frozen criteria in a fresh session or report reviewer unavailability explicitly). Reviewers remain read-only.
- Deliver the artifact, observed checks, and open items, then stop. `Quick` and `Structured` never require `.manuscript-ops/`, Jujutsu bookmarks, gate receipts, or `validate_state.py`.

## 3. Project: run the governed lifecycle

Read [project-route.md](references/project-route.md) before initializing, resuming, or advancing gates:

- **Direct Brief intake**: accept any user-approved `ManuscriptBrief` directly. No upstream discovery skill is required. If scope or audience decisions remain open before Brief approval, resolve them directly with the user (or suggest Base workflow `/grill-with-docs` or `/to-spec` when installed, falling back to direct Brief scoping when absent). For primary-source gathering, use `research` when available, or dispatch a primary-source research subagent in a **fresh context window**.
- **Project configuration**: read `docs/agents/light-project.md` (`Decision data` and acceptance profile) if configured via `/light-setup`; otherwise proceed standalone with `Decision data: on-device` by default.
- **Independent milestone sign-off**: the assigned writer owns prose; `acceptance` at **Charter scale** (`Profile: manuscript`, storing frozen charters and durable acceptance state strictly under `.scratch/<feature>/acceptance/` or `.scratch/acceptance/<slug>/`) owns milestone convergence and independent Evaluator verdicts (`PASS`, `FAIL`, `BLOCKED`), dispatching reviewers and the independent Evaluator in **fresh context windows** ([handoffs.md](references/handoffs.md)).
- **Direction changes**: if an approved Brief, outline, or charter assumption stops holding (including `acceptance` returning `FAIL` with `Cause: direction`), invoke `redirect` to draft a Change proposal under `.scratch/<feature>/changes/` (Graceful fallback: halt and present a structured change proposal directly) and wait for human approval.
- **Version gates and validation**: manage dated gate bookmarks with [version-control.md](references/version-control.md) and validate state with `python scripts/validate_state.py --root <project-root> --check-vcs`. On any blocker, follow [failure-recovery.md](references/failure-recovery.md) and return preserved evidence plus the exact resume condition.

## Resources

- [Routing rules](references/routing.md) and [optional `decide` routing](references/semantic-routing.md)
- [Project workflow](references/project-route.md), [layout](references/project-layout.md), and [lifecycle](references/lifecycle.md)
- [Review profile and Concept Grounding](references/review.md)
- [Source and format contracts](references/formats.md)
- [State model and validator modules](references/state-model.md)
- [Version gates](references/version-control.md), [skill coordination](references/handoffs.md), and [failure recovery](references/failure-recovery.md)
