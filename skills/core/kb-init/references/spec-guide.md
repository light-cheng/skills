# Knowledge Base Implementation SPEC Guide

Produce the SPEC only after the user explicitly ends the interview. Write for the base's owner using their domain language, explaining technical choices through the workflow problems they solve. Separate user requirements, accepted recommendations, verified environment facts (`YYYY-MM-DD` anchored), low-risk implementation choices, user-reserved runtime boundaries, and deferred or blocked items. Never disguise an unresolved blocker or Agent-only inference as a settled user decision.

## Required SPEC sections

Adapt headings to fit the domain, covering every applicable contract below:

1. **Objective, users, and scope**: Problem solved, human vs Agent roles, included content/media types, atomic unit shape, and explicit non-goals (stopping at outward export/query interfaces rather than designing downstream consumer apps, reports, or dashboards).
2. **Base decision and operating path**: Selected base, accepted tradeoffs, and verified Base Discovery facts: native storage units, programmatic interface, authentication, read/write/search/attachment support, current harness capability vs post-approval setup, and known limits.
3. **Exact destination and connection plan**: Concrete local path or remote target (or how the target container is chosen during approved setup). When an external connection is required, specify the route, project vs global config scope, safe credential path (OAuth/connector auth or local secret store, never chat or shell-argument secrets), user authorization actions, fallback if a connector is unavailable, and live connection validation steps.
4. **Canonical knowledge structure**: Collections/directories/tables, metadata fields, naming, relationships, indexes, attachment placement, and structured vs free-form sections (include a concise tree or schema example when helpful).
5. **Human navigation and presentation (when people directly use the base)**: Entry point, one or two primary browse dimensions, recent vs older retrieval at scale, active vs `superseded` filtering, and physical hierarchy vs virtual views/indexes. Include only user-decided or user-accepted navigation choices; omit this section for Agent-only stores.
6. **Historical provenance and source traceability**:
   - How mutable factual and code claims are anchored (`YYYY-MM-DD` calendar dates or `repo@commit` revisions, banning bare "currently").
   - How outdated claims transition to `superseded` with an explicit pointer to the newer record (versus rare ephemeral state where silent replacement is intentional).
   - When source retention applies, how raw sources receive stable IDs and link cleanly to derived entries.
7. **Operational mechanism matrix**: Concrete executor, interface, permissions, and verification for each core workflow:

   | Workflow | Behavior | Executor | Interface / Mechanism | Authority / Dependency | Verification |
   |---|---|---|---|---|---|
   | `Ingest` | Capture source, anchor `YYYY-MM-DD` / `repo@commit`, link, flag contradictions | ... | ... | ... | ... |
   | `Query` | Traverse views/search/links, cite anchors, respect `superseded` status | ... | ... | ... | ... |
   | `Lint` | Audit unanchored claims, stale/`superseded` drift, broken links, orphans | ... | ... | ... | ... |
   | `Export` | Expose clean outward data/files at consumer boundary | ... | ... | ... | ... |
   | `Backup` | Execute snapshot, portable export, or recoverable backup | ... | ... | ... | ... |

   Add `Migration` or domain-specific workflows when applicable; omit rows that genuinely do not apply.
8. **Agent authority and maintenance entry point**: Actions the Agent runs autonomously vs actions requiring user approval, plus the exact discoverable location where future Agent sessions read the authoritative maintenance rules.
9. **Migration and backup/recovery semantics**: Source material to migrate vs leave untouched; exact backup guarantee (`offline snapshot`, `portable export`, or `recoverable backup`, including reconstruction verification when recoverability is claimed, and never adding Git unless decided).
10. **Implementation plan, deliverables, and validation**:
    - Split work into *executable immediately after approval*, *connection/user-authorization steps*, and *blocked items* (with prepared artifacts and unblocking steps).
    - List concrete deliverables (excluding pre-SPEC `.scratch/` research notes unless the user chose to keep them).
    - Define end-to-end validation checks across `Ingest`, `Query`, `Lint`, human navigation (when applicable), source/date/`repo@commit` provenance, permissions, reconnection, and backup/export, executed through `acceptance` when installed or inline operational checks when absent.

## Hard approval gate

Close the SPEC with an explicit stop stating that no knowledge-base structure, connection configuration, or maintenance implementation has started yet (noting accurately if pre-SPEC research notes exist in `.scratch/`), and wait for explicit user approval before executing Phase 4. Questions or revision requests keep the SPEC in review.
