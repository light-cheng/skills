# Human Navigation

Read and apply this reference whenever people will directly open, browse, review, or edit the knowledge base. Skip human navigation design when the user interacts with the store exclusively through an Agent.

Human navigation defines how a person moves through the base without relying on an Agent for every lookup. Keep it distinct from both canonical storage layout and programmatic Agent/API access: avoid turning a human-facing base into an unnavigable flat dump just because flat writes are easy for automation, and avoid forcing deep physical folder trees when saved views, filters, or index pages fit better.

## 1. Establish the human role

Clarify:

- how often people open the base directly versus asking an Agent;
- whether direct sessions focus on browsing, searching, reviewing an inbox, or editing;
- which devices or surfaces (desktop editor, web workspace, mobile) matter in practice.

## 2. Design the entry point and primary browse dimensions

Ask what the person naturally expects to see and do first upon opening the base (for example: recent additions, an inbox/review queue, major topics, time-ordered views, projects, entities/authors, active vs `superseded`/archived status, or search-first). Do not assume a dashboard or homepage unless it serves that entry habit.

Identify the **one or two primary browse dimensions** that match how the user actually remembers things, adding secondary views only when justified by real lookups.

## 3. Separate physical hierarchy from virtual navigation

A user who browses by year/month or by topic does not automatically need nested physical directories. Compare:

- **Physical hierarchy** (folders, separate workspaces/tables): choose only when physical separation solves a real storage, permission, performance, or maintenance boundary.
- **Virtual navigation** (saved views, metadata filters, grouped tables, index/MOC notes, backlinks, search scopes): prefer when it delivers the desired human browsing paths without fragmenting canonical records or complicating `Ingest` and `Lint`.

## 4. Test old-knowledge retrieval at scale

Test the proposed structure against at least one concrete growth scenario before treating navigation as settled:

- How will the user locate an item from six or twelve months ago once the base holds 500 or 5,000 entries?
- Do they recall approximate time, topic/domain, source/author, or project context first?
- How are `superseded` or archived entries kept out of the way during everyday browsing while remaining reachable when auditing history?

Account for practical readability within the chosen base (visible card/table metadata, naming clarity, sort order, default active-only filters, and preview density) without drifting into custom UI product design.

## Settlement bar

Treat human-facing structure and navigation as `settled` only when you can state clearly:

1. what the person sees first;
2. the one or two primary browse dimensions;
3. how older knowledge is found after substantial growth (and how `superseded` history is filtered or marked);
4. which elements are physical storage structure versus virtual views, filters, or index pages;
5. explicit user choice or explicit user acceptance of the recommended navigation model.
