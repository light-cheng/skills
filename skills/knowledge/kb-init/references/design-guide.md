# Knowledge Base Design Guide

Turn the settled interview decisions, Base Discovery facts, and readiness checks into a coherent, durable knowledge-base architecture. Do not restart the interview here; if synthesis uncovers a genuine contradiction between settled choices, surface the contradiction explicitly and reopen only the affected decision.

## Keep the three models distinct

### 1. Knowledge model

Defines canonical domain semantics independent of storage quirks:

- scope, exclusions, and what one atomic knowledge unit represents;
- required metadata fields, relationships, and attachment placement;
- historical provenance (`YYYY-MM-DD` and `repo@commit` anchors) and source traceability;
- lifecycle states, including how outdated claims become `superseded`;
- ongoing `Ingest`, `Query`, and `Lint` maintenance loops.

### 2. Human navigation model (when people directly use the base)

Include this model only when humans browse, review, or edit the base directly:

- what a person sees first upon opening the base;
- primary browse dimensions (one or two dimensions matching real recall);
- how recent items and older knowledge are surfaced at scale;
- which navigation is physical hierarchy versus virtual views, filters, or index pages.

Canonical storage and human navigation need not match: a flat canonical collection can expose rich saved views or index notes, and a nested folder layout can still require cross-cutting search or topic indexes. Skip human navigation surfaces when the base is strictly Agent-operated.

### 3. Base operating model

Maps the knowledge and navigation models onto the chosen platform without silently distorting user requirements:

- native storage units (files, pages, rows, objects, attachments, relations);
- verified Agent connection route, authentication, and project vs global config scope;
- supported programmatic operations, automation limits, and future session reconnection;
- backup, export, and migration guarantees.

## Historical provenance and anti-rot rules

Knowledge bases rot silently when mutable facts are written as timeless truths or when history is overwritten without a trail. Build these provenance rules into the schema, templates, and authoritative maintenance guide:

### Anchor every mutable factual or code claim to `YYYY-MM-DD` or `repo@commit`

- Every factual assertion about changing systems, external platform capabilities, pricing/limits, metrics, team processes, or repository behavior must carry an explicit calendar date (`YYYY-MM-DD`, such as `as of 2026-11-25` or `verified_at: 2026-11-25`) or an immutable code revision (`repo@commit`, such as `acme/api@4f8c2a1`, optionally paired with a release tag).
- Never write bare relative-time phrasing such as "currently", "now", "at present", "recently", or undated present-tense code/platform claims ("the worker retries three times") without an explicit date or `repo@commit` anchor.
- Reserve unanchored statements strictly for timeless definitions or invariants that cannot drift independently of the note.

### Mark outdated claims `superseded` instead of erasing history

- When newer evidence, a later `repo@commit`, or a revised decision invalidates an earlier claim and historical evolution, auditability, or prior context matters, mark the outdated entry or claim `superseded` with a direct pointer to the replacing record and the transition date or commit (for example frontmatter `status: superseded`, `superseded_by: <id-or-path>`, `superseded_at: YYYY-MM-DD`, or inline `[superseded 2026-11-25 -> <new-entry>]`).
- Keep `superseded` material distinguishable from active truth in default `Query` and human browse views (via status filters, dedicated archive views, or explicit callouts) so readers and Agents neither lose historical context nor mistake superseded claims for active ones.
- Use silent in-place overwrite only for typographical fixes, formatting cleanup, or explicitly ephemeral scratch state where historical lineage carries zero value.

### Preserve exact source traceability when required

- When derived notes summarize or extract from retained source inputs, bind them via stable source IDs, explicit relation fields, canonical URLs paired with retrieval dates (`YYYY-MM-DD`), or `repo@commit` file paths rather than loose title or date matching.

## Core wiki maintenance operations (`Ingest`, `Query`, `Lint`)

Every knowledge base must define explicit executors, interfaces, and authority boundaries for three ongoing operational loops alongside base-specific export and backup:

### `Ingest` (raw source -> anchored, linked knowledge)

1. Capture or register incoming source material with stable source identity and explicit `YYYY-MM-DD` or `repo@commit` provenance.
2. Extract, normalize, or author canonical knowledge units following the base's schema and attachment rules, converting any relative-time wording ("currently", "today") into concrete `YYYY-MM-DD` or `repo@commit` anchors at write time.
3. Update relevant cross-links, relationships, topic indexes, or browse metadata so new entries are reachable immediately.
4. Check existing entries touched by the same topic or component: when new evidence contradicts an older claim, mark the outdated claim `superseded` with a forward pointer to the new entry (or flag the conflict for user review when policy requires human sign-off).

### `Query` (retrieval -> provenance-aware synthesis)

1. Traverse indexes, saved views, metadata filters, full-text/semantic search, and source links to retrieve relevant active entries while respecting `superseded` status boundaries (consulting `superseded` entries intentionally when answering historical "what changed and why" questions).
2. Surface the `YYYY-MM-DD` or `repo@commit` anchors and source links alongside retrieved answers so humans and Agents can judge freshness immediately.
3. When authorized by the user's maintenance rules, file durable syntheses, comparisons, or newly discovered knowledge gaps back into the base as anchored notes without mutating raw source artifacts.

### `Lint` (health check -> anti-rot, contradiction, and integrity audit)

Run periodically or on demand to keep the base trustworthy as it scales:

1. **Provenance audit**: flag mutable factual or code claims missing an explicit `YYYY-MM-DD` or `repo@commit` anchor, including any bare "currently" / "now" phrasing.
2. **Staleness and contradiction audit**: surface active claims whose anchored `repo@commit` or `YYYY-MM-DD` is outperformed by newer ingested sources, and either transition confirmed outdated claims to `superseded` (with forward pointers) or queue them for verification.
3. **Structural and link audit**: detect broken internal links, missing attachments, orphan entries omitted from required indexes or browse views, broken source-traceability references, and schema/field drift.
4. **Autonomy split**: separate repairs the Agent may apply automatically (such as index refresh or formatting normalization) from structural merges, deletions, or disputed `superseded` transitions that require user confirmation.

## Operational, boundary, and recovery discipline

- **Simplest complete architecture**: Include every structure needed for real `Ingest`, `Query`, `Lint`, navigation, traceability, reconnection, and backup workflows, and omit ceremonial layers that serve no workflow.
- **Explicit operational mechanisms**: Assign every core workflow an executor (Agent rule, base-native feature, CLI/API/MCP call, script, or user action), required permissions, and a concrete verification check.
- **Consumer boundary**: Design export schemas, query surfaces, or stable IDs needed by downstream consumers, stopping at the interface boundary rather than designing downstream reports, dashboards, or apps.
- **Honest backup semantics**: Label backup paths accurately as an **offline snapshot** (local inspection copy), **portable export** (migration bundle, possibly with fidelity tradeoffs), or **recoverable backup** (tested reconstruction of content, structure, relations, and attachments). Never call an untested file dump disaster recovery.
- **Discoverable maintenance entry point**: Place authoritative operating rules where future Agent sessions and maintainers will reliably find them in the chosen base without forcing one hardcoded filename across all platforms.
- **Decision provenance and partial implementation**: Keep user requirements, accepted recommendations, verified facts, low-risk implementation details, and user-reserved runtime choices distinct. Separate implementation work into *complete now*, *prepared now and executable after connection/authorization*, and *genuinely blocked*.
