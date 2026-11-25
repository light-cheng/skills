# Specification Profile (`Profile: specification`)

Select `specification` when accepting a `spec.md`, architectural brief, ticket graph, ADR, or formal requirements contract whose claims must be verified for authority, completeness, and testability before implementation starts.

## Review axes

Audit every applicable axis independently and tag each `F-###` finding with its axis (`Not applicable` requires an explicit reason in `producer-evidence.md`):

1. **Authority and baseline integrity:** authoritative source documents, revisions, approval status, decision owner, and source precedence (when multiple authorities exist) are explicit.
2. **Scope and target traceability:** every in-scope capability, module seam, and explicit Out-of-Scope exclusion traces to an approved source decision rather than unstated assumptions.
3. **Criteria and ticket traceability:** every user story or requirement maps to stable, numbered acceptance criteria or tickets (`Blocked by` dependencies form a valid DAG with zero orphan stories).
4. **Terminology and ambiguity control:** domain terms match `GLOSSARY.md` (when present); units, thresholds, privacy boundaries, and preconditions allow a single interpretation rather than vague qualifiers.
5. **Contradiction and decision coherence:** competing constraints, cross-ticket interface assumptions, and fallback paths agree without silent conflicts.
6. **Testability and verification design:** criteria specify observable outcomes, clean module seams, positive and negative cases, and appropriate evidence classes (`structural`, `behavioral`, `runtime`) without brittle prose/checksum locks.
7. **Change and handoff resumability:** open questions, dependencies, and tracker conventions (`docs/agents/issue-tracker.md`) allow downstream `/to-tickets`, `/implement`, or `/implement-spec` sessions to execute with fresh context.

## Evidence requirements and failure stops

Required labeled evidence ([charter-and-evidence.md](../charter-and-evidence.md)):
- `source`: frozen specification revision, upstream decision records, and approval status.
- `structural`: traceability check (user stories <-> criteria/tickets, dependency DAG check, link and glossary alignment).
- `behavioral` (when the specification includes executable schemas, prototypes, or CLI contracts): focused validation examples covering success, boundary, and missing-input cases.
- `review`: fresh-context Critic report and separate fresh-context Evaluator criterion audit.

Severity follows Core impact tiers (`Critical`: unsafe, impossible, or contradictory requirement that would cause harm if built; `High`: missing authority, untraceable user story, cyclic/broken ticket graph, or unresolved ambiguity blocking deterministic implementation; `Medium`: missing negative-case seam, undefined term, or incomplete handoff detail; `Low`: minor cross-reference polish). Unresolved authority conflicts or missing user decisions return `BLOCKED` or `FAIL` (`Cause: direction` -> `redirect`) rather than Reviewer-invented requirements.
