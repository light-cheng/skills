# Knowledge Base Interview Contract

Design the knowledge base from the user's real workflow through a natural conversation rather than a rigid form. The eight coverage areas below are minimum design concerns, not fixed user-facing headings or a mandatory question sequence.

## Conversation rules

- Speak in plain language matched to the user's domain; explain database, API, schema, or information-architecture terms by the practical problem they solve.
- When the user responds with a question, objection, or request for comparison:
  1. answer the question directly and explain relevant tradeoffs;
  2. keep the underlying decision open (curiosity is not approval);
  3. return to the paused decision afterward.
- When the user reserves a choice for case-by-case runtime control (for example, "I will decide sharing permissions each time"), record that governance boundary as settled and omit default values for that choice.
- Take as many turns as needed for clarity; never compress important architectural choices into a rushed bundle just to finish in fewer turns.

## Decision depth and open-decision surfacing

**Coverage** means a topic was mentioned; **depth** means the choice can be implemented without guesswork. Before marking any high-impact decision `settled`, establish three layers:

1. **Real workflow**: what people and Agents will actually do day to day.
2. **Priority or tradeoff**: what matters most and which compromise is acceptable.
3. **Concrete scenario**: how the choice behaves in a realistic future case (for example, finding or updating a six-month-old note once the base holds hundreds or thousands of entries).

Whenever your own reasoning uncovers an unasked question that would materially change knowledge structure, human navigation, base selection, storage layout, `Ingest` / `Query` / `Lint` automation, permissions, historical provenance, migration, backup, or connection routes, keep it `discussing` and surface it directly (either as a focused question or as a concrete recommendation with tradeoffs for user acceptance). Reserve autonomous Agent choices strictly for low-risk implementation details that do not narrow user behavior or portability.

## Minimum coverage areas

### 1. Purpose, users, and outcomes

Clarify what domain the base serves, who reads and maintains it (solo user, user + Agent, small team, broader org), whether humans will open and browse the base directly or interact primarily through an Agent, and what concrete outcomes it supports. Explore downstream uses only far enough to define what the knowledge base itself must store or expose.

### 2. Content and record types

Identify the actual material entering the base (prose notes, structured records, docs, spreadsheets, webpages, code/config, screenshots, diagrams, audio, video, attachments, or generated syntheses) and what one meaningful unit of knowledge looks like, including whether non-text attachments are passive files or first-class searchable items.

### 3. Base and storage environment

Discuss candidate bases after usage and content are clear, unless the user already has a candidate. Cover local vs remote access, collaboration, offline/mobile needs, attachment volume, expected scale, version history, access control, automation, portability, and cost/platform constraints. When the user is unsure, compare a few plain-language directions and recommend one; keep the base open until accepted. Trigger [base-discovery.md](base-discovery.md) once a candidate becomes serious.

### 4. Canonical structure and human navigation

Separate canonical storage organization (collections/folders, granularity, naming, fields, tags, links/relations, structured vs free-form sections) from how humans browse. When people will directly browse or operate the base, read [human-navigation.md](human-navigation.md) and test at least one realistic old-knowledge retrieval scenario before settling structure. When the base is Agent-only, optimize for reliable retrieval and maintenance without unnecessary human dashboards.

### 5. Intake (`Ingest`), source traceability, and historical provenance

Clarify where new material originates, whether raw inputs are staged or retained, whether derived entries require exact source traceability (stable source IDs, canonical URLs with retrieval dates, or `repo@commit` paths rather than loose date/title labels), and how historical evolution matters:

- how mutable facts and code behaviors are anchored (`YYYY-MM-DD` dates or `repo@commit` revisions);
- when outdated claims should remain auditable as `superseded` with pointers to newer entries versus when ephemeral notes are simply replaced.

### 6. Retrieval (`Query`), analysis, and consumer boundary

Explore realistic six-month-later `Query` scenarios: full-text or semantic search, field/date filtering, following links, cross-record comparison, aggregation, Agent Q&A, whether reusable syntheses are filed back into the base, and outward exports. Apply the consumer boundary test: *does this decision change the knowledge base itself, or only a downstream report/app/dashboard that consumes it?* Stop at the interface contract unless the user explicitly expands scope.

### 7. Maintenance (`Lint`) and Agent autonomy

Clarify who creates and updates entries, how duplicates, contradictions, and stale claims are handled during `Ingest` and `Lint` health checks, and the exact autonomy boundary: what the Agent may execute automatically (new notes, index updates, routine lint flags) versus what requires explicit user confirmation (deletions, merges, category restructures, or disputed `superseded` transitions). Avoid inventing confirmation gates the user did not ask for.

### 8. Boundaries, migration, backup, and growth

Cover existing material to migrate vs leave untouched, private or sensitive content excluded from Agent access, expected scale over time, exit/portability needs, and exact backup expectations (distinguishing an offline snapshot, a portable export, and a recoverable disaster-recovery backup; never assume Git unless decided).

## Research detours and decision dependencies

Use external research for verifiable facts, never to replace user preferences. Follow [research-contract.md](research-contract.md) whenever capability, integration, limit, or export facts need verification, then return to the paused decision. Treat decisions as a dependency tree: avoid locking downstream choices before prerequisites hold, and reopen earlier decisions whenever Base Discovery, scale, attachment rules, or migration facts invalidate them.

## Settlement standard and closure discipline

A high-impact decision is `settled` only when workflow, priority/tradeoff, and a concrete scenario are understood (including human navigation when applicable) and its source is one of:

- `user-explicit`
- `user-accepted-recommendation`
- `verified-environment-fact` (an environment fact such as current directory or existing `.git` is context, not an automatic destination or versioning decision unless accepted by the user)
- `user-deferred`
- `not-applicable`

Run [readiness-check.md](readiness-check.md) before using any closure-signaling phrasing ("last question", "final few questions", "almost ready for SPEC"). Even after readiness passes, wait for the user to explicitly end the interview.
