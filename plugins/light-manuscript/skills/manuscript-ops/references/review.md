# Manuscript review profile and Concept Grounding

`manuscript-ops` defines the domain review profile (`ReviewMatrix`) and evidence contract for manuscripts, while `acceptance` (`Profile: manuscript`) owns convergence rounds, reviewer/Evaluator independence, finding lifecycle, and final `PASS`, `FAIL`, or `BLOCKED` verdicts.

## Concept Grounding

Every manuscript review (across `Structured` drafts, `Project` outlines, individual content batches, cumulative candidates, and derived editions) must enforce **Concept Grounding**:

1. **Rule**: Every domain concept, technical term, notation, abstraction, or mental model that a section leans on to explain new material must satisfy at least one of two conditions before the reader encounters it:
   - **Declared prerequisite**: explicitly listed in the approved Brief's target-reader prerequisites (baseline knowledge assumed before page one), or
   - **Earlier-section grounding**: explicitly introduced, defined, and grounded in an earlier section (or an earlier accepted prerequisite batch) that precedes the current section in reading order.
2. **What to flag**: Any ungrounded forward dependency (using a term, architecture part, formula symbol, or operational concept as if already understood when its definition appears only in a later section or nowhere at all) is a defect under `intent-structure` and `reader-accessibility`.
3. **Batch and reorganization safety**: When reviewing a batch incrementally or auditing an outline/chapter reordering, verify that every concept imported by the batch is grounded either in the Brief's reader prerequisites or in the accepted prerequisite batches (`depends_on`), never in a planned or parallel chapter that comes later in the book.
4. **Valid repairs**:
   - Introduce and ground the concept at its first point of reliance;
   - Reorder sections or batch dependencies so the grounding section precedes the dependent section; or
   - Obtain explicit user approval to add the concept to the Brief's target-reader prerequisites when the target audience genuinely already holds it.

## Manuscript axes

Every `Project` `ReviewMatrix` includes all nine canonical manuscript axes. Mark an axis `applicable: false` only with an explicit recorded `reason`:

- `intent-structure`: goal, completeness, section ordering, internal logic, reader task, and **Concept Grounding** across sections;
- `factual-sources`: source authority, citations, numbers, units, and provenance lineage;
- `terminology-localization`: glossary adherence, terminology stability, translation fidelity, and cross-language consistency;
- `reader-accessibility`: audience fit, prerequisite alignment (**Concept Grounding** against target-reader prerequisites), accessibility, tone, and localization;
- `safety-privacy-legal`: safety warnings, privacy redaction, legal/regulatory boundaries, and document metadata hygiene;
- `format-layout`: structural validity, layout, pagination, tables, fields, links, and navigation;
- `images`: figure selection, rights, placement, crop, captions, callout annotations, and alt text;
- `reproducibility-recovery`: deterministic generation inputs, hashes, gate receipts, and resumable state;
- `compatibility-round-trip`: target application compatibility and round-trip invariant preservation.

On `Project` routes, the eight non-image axes are mandatory positive-or-negative audits. `images` is mandatory whenever the Source Register includes `image-scan` entries, `pptx` is a selected format, or the active batch declares `images`.

## Evidence contract

Freeze the artifact snapshot (`captured_at` plus project-relative `{path, sha256}` entries) before invoking `acceptance`. Every applicable axis in `ReviewMatrix` names its `evidence_required`, and the JSON verdict envelope returned by `acceptance` (`provider: "acceptance"`, `profile: "manuscript"`) must include a `manuscript_evidence` array with at least one hashed evidence artifact for every applicable axis. Syntax validation alone never satisfies `format-layout` when real rendering and visual inspection are required.

## Delegating convergence and sign-off to `acceptance`

- **Bounded drafts (`Structured`)**: invoke `acceptance` at **Inline scale** with in-memory criteria (including Concept Grounding, source fidelity, and applicable format checks), running up to 3 `review -> findings -> repair -> re-review` rounds via a reviewer subagent in a **fresh context window**.
- **Milestone gates (`Project`)**: invoke `acceptance` at **Charter scale** (`init`, `run`, `resume`) with `Profile: manuscript`, storing the frozen Acceptance charter and JSON verdict envelope under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/` or `.manuscript-ops/reviews/`). After convergence, `acceptance` dispatches a separate independent Evaluator in a **fresh context window** to verify evidence per criterion and issue `PASS`, `FAIL` (recording `cause: "implementation" | "direction"`, routing `direction` to `redirect`), or `BLOCKED`.
- **Graceful fallback**: when `acceptance` is not installed in a standalone harness, freeze the review packet (`ReviewMatrix`, artifact hashes, Concept Grounding checklist, and format-QA artifacts) and dispatch a read-only reviewer/Evaluator subagent in a **fresh context window** (or ask the user to run the frozen Evaluator packet in a separate fresh session, recording `independence: "fresh_session"`). Never treat same-context self-review as independent acceptance; if no fresh context is available, record `independence: "degraded"` and return `BLOCKED`.
