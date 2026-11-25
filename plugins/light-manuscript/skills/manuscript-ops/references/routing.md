# Writing routes

## Policy: `needs-v2`

Classify the deliverable, source relationships, output purpose, and actual management requirements under `needs-v2` (the sole supported routing policy). Workspace file count, a single writer delegation, independent content review, or a QA-only PDF render never create a `Project` lifecycle requirement on their own.

| Route | Use when | Completion |
| --- | --- | --- |
| `Quick` | Bounded low-risk text edit with clear meaning and plain-text/Markdown output | Edit, verify meaning and wording, deliver, and return |
| `Structured` | Bounded draft, rewrite, SOP, or report needing source, concept-grounding, safety, image, or format/render QA | Keep a compact brief, write the document, run required review and real render checks, deliver, and return |
| `Project` | Explicitly requested, or genuine multi-session batched writing, locked source derivatives, or reproducible interdependent editions | Execute the governed `Project` lifecycle with receipts and milestone gates |

Safety, privacy, legal, and regulated facts require rigorous content and source verification (`safety-privacy-legal` and `factual-sources`), whether the route is `Structured` or `Project`. Shortness never waives required review. Material unknowns require source evidence or a user decision; unrelated stylistic unknowns do not escalate a bounded edit into `Project`.

The six dimensions (`scale`, `source_complexity`, `risk`, `output_complexity`, `collaboration`, `reproducibility`) are scored `0`, `1`, `2`, or `null` (unknown) from declared task facts. Their numeric sum is explanatory context and never forces `Project` by itself. Only true lifecycle triggers (`explicit_project`, `cross_session`, `large_volume`, `locked_derivatives`, `reproducible_multi_format`, or `task.lifecycle_required: true`) select `Project`.

## Assessor input and output

Use [routing-input.json](../assets/templates/routing-input.json) with `scripts/assess_project.py`:

- `routing_policy`: must be `"needs-v2"`.
- `task.scope`: `"bounded"`, `"long-form"`, or `"unknown"`.
- `task.lifecycle_required`: boolean or `null` recording whether cross-session resumable batch/gate management is genuinely needed.
- `task.source_paths`: explicit input files to inspect (excluding unrelated repository files).
- `task.deliverables`: `{format, purpose}` entries distinguishing `"deliverable"` from `"qa"`.
- `task.risk_axes`: canonical manuscript review axis IDs triggered by domain risk.

The read-only assessor emits JSON to stdout with `route`, `required_review_axes`, `needs_initialization`, `unknowns`, `reasons`, `next_action`, and optional `next_invocation`. It never writes files, creates directories, or invokes other skills.

## Examples

| Task | Route and required checks |
| --- | --- |
| Fix typos in one supplied paragraph | `Quick`; wording and fact-preservation check |
| Rewrite a short high-voltage maintenance memo from confirmed material into DOCX | `Structured`; `factual-sources`, `safety-privacy-legal`, `intent-structure`, `reader-accessibility`, `format-layout`, and real page render QA |
| Draft a sourced departmental report with two diagrams | `Structured`; source, concept-grounding, `images`, and target format checks |
| Write a 12-chapter technical manual across sessions with batch gates | `Project`; resumable `.manuscript-ops/` state, batch manifest, and Charter-scale `acceptance` |
| Lock a Chinese master manuscript and derive English and print/EPUB editions | `Project`; `source-locked` gate, hash-bound derivative lineage, and per-deliverable format QA |
