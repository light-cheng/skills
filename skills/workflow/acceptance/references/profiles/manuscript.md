# Manuscript Profile (`Profile: manuscript`)

Select `manuscript` when accepting a book, multi-chapter manuscript, outline, semantic batch, locked-source milestone, translation/derived edition, or rendered publication deliverable (including `manuscript-ops` Project gates).

## Review axes

Audit every axis independently and tag each `F-###` finding with its axis. On Project gates, axes 1-6 and 8-10 require explicit positive-or-negative audit entries even when clean; axis 7 (Images and figures) requires an explicit applicability record when untriggered and a full audit when image sources, slide decks (PPTX), or batch figures are in scope:

1. **Reader task, structure, Concept Grounding, and internal logic:** audience fit, scope, chapter/section sequencing, cross-references, and **Concept Grounding** (every technical or domain concept leaned on by a section is either declared in target-reader prerequisites or explicitly grounded in an earlier section).
2. **Source authority, provenance, claims, citations, numbers, and units:** factual claims trace to registered authoritative sources within permitted use; reference-only/incoming notes are never cited as authority; units, numbers, and derivative source hashes hold.
3. **Terminology, glossary, style, and cross-language consistency:** approved glossary terms, transliterations, register rules, and cross-edition alignments hold without drift.
4. **Reader fit, accessibility, tone, and localization:** reading level, navigation cues, callouts, accessibility text, and localization match the approved `ManuscriptBrief`.
5. **Safety, privacy, legal/regulatory boundaries, and metadata:** redactions, disclaimers, rights/attribution notices, and embedded document metadata satisfy policy.
6. **Format structure, layout, pagination, tables, links, and navigation:** target deliverables contain intact styles, headings, tables, links, fields, and page/slide flow rather than raw source syntax alone.
7. **Images and figures:** source/rights, placement, resolution/crop, captions, callouts, and alt text match the brief (or record explicit non-applicability).
8. **Lifecycle, semantic batches, human gates, and locked-source integrity:** prerequisite gates and batch snapshots match lifecycle state; translations and derived formats bind the approved locked source.
9. **Generation reproducibility, hashes, version gates, and recovery:** build tools, versions, commands, input/output SHA-256 hashes, gate receipts, and any approved manual-edit dispositions are recorded and resumable.
10. **Compatibility, rendering, visual QA, semantic QA, and round-trip checks:** required target renderers/adapters run against the exact snapshot; **syntax-only checks never substitute for required render or visual QA**.

## Evidence and `manuscript-ops` gate integration

Each evidence item carries one primary label from [charter-and-evidence.md](../charter-and-evidence.md):

- Approved `ManuscriptBrief` and frozen `charter.md` (`source`), plus project-relative deliverable paths, SHA-256 hashes, and snapshot timestamp (`structural`).
- Source register, provenance lineage, glossary coverage, and lifecycle/batch/gate receipts (`source` / `structural`).
- Executed build, render, visual inspection, semantic verification, and round-trip checks with exact tool commands or documented `manual` visual audit (`behavioral` / `runtime` / `manual`).
- Separate fresh-context Critic and independent Evaluator reports (`review`) preserving the raw Core `Independence: full | degraded | unavailable` value so `manuscript-ops` can map it without loss (`full -> native`, `degraded -> fresh_session | degraded`, `unavailable -> BLOCKED`).
- When `manuscript-ops` consumes a JSON gate envelope alongside `.scratch/<feature>/acceptance/` (or project-configured `.scratch/` acceptance path), bind the same snapshot SHA-256 hashes, `Verdict: PASS | FAIL | BLOCKED`, raw `independence`, and one `manuscript_evidence` projection entry per applicable axis above while keeping `charter.md`, `state.md`, `findings.md`, and `verdict.md` authoritative for acceptance state.

## Severity and failure stops

- **Critical:** unlawful/unsafe content, privacy leak, fabricated or unauthorized source claim, corrupt deliverable, or broken primary reader task.
- **High:** missing brief/source/language/format seam, ungrounded core concept blocking comprehension, bypassed source-lock or lifecycle gate, or missing required render/visual QA evidence.
- **Medium:** material terminology drift, layout/table/figure defect, accessibility gap, or missing reproducibility metadata (blocks `PASS` without recorded post-review user exception).
- **Low:** minor editorial or diagnostic note.

Return `FAIL` or `BLOCKED` per [charter-workflow.md](../charter-workflow.md) when syntax checks are offered in place of required render/visual QA, translations read unlocked sources, hashes/lineage mismatch, a required renderer is unavailable (`BLOCKED`), or meeting the brief requires changing audience, languages, formats, or source authority (`FAIL` with `Cause: direction` -> `redirect`).
