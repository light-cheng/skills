# Base Discovery

Base Discovery turns a candidate storage environment or software platform into a verified operating model before the base or connection route is treated as `settled`. Keep it platform-agnostic: never rely on hardcoded software recipes, and never install tools, alter configuration, authenticate, or create target objects before SPEC approval.

Read this reference whenever a third-party software or service base becomes a serious candidate; apply it proportionally for local file trees or local databases.

## What to verify

### 1. Native storage and content handling

Determine what the base stores natively (files, Markdown notes, pages, database rows, collections, attachments, explicit relations) and which parts are user-visible versus internal. Verify how it stores, links, searches, exports, and migrates every non-text content type identified in the interview; if required media cannot be handled cleanly, consider a hybrid layout or reopen the base decision.

### 2. Current programmatic access

Determine the non-GUI interfaces officially supported as of the current date:

- direct filesystem or local database access;
- official CLI tools;
- MCP servers or harness connectors;
- REST/GraphQL APIs or SDKs;
- structured import/export formats.

Do not assume an interface exists or lock a third-party integration route from model memory alone when official APIs, connectors, permissions, or rate limits may have changed. Unless verified from primary sources in the current session, run a research detour via `research` (or its fresh-context primary-source subagent fallback) under [research-contract.md](research-contract.md). Never ask the user to hunt down public documentation links that the Agent can locate itself.

### 3. Authentication, least privilege, and secret safety

Determine required authorization flows, minimum permission scopes, project-scoped vs global configuration options, what future Agent sessions need to reconnect, and how credentials are supplied safely (OAuth, connector-managed auth, environment variables, or local secret stores). Never design a connection route that asks users to paste secrets into chat, prompts, maintenance docs, example files, or shell command arguments.

### 4. Read, write, query, and maintenance operations

Check which operations an Agent can perform programmatically to support `Ingest`, `Query`, and `Lint`:

- list, search, and read records and metadata;
- create, update, move/reorganize, and mark entries `superseded`;
- upload or reference attachments and maintain explicit relationships/links;
- manage schemas, fields, index notes, or saved views;
- run integrity/link checks and trigger exports or backups.

### 5. Export, portability, and backup guarantees

Verify export formats, attachment inclusion, and whether internal links, metadata, and provenance survive export. Match backup terminology to reality:

- **Offline snapshot**: downloaded copy suitable for local reading/inspection.
- **Portable export**: structured export suitable for migrating elsewhere, potentially with presentation or relation tradeoffs.
- **Recoverable backup**: capture paired with a reconstruction path that restores content, fields, relationships, and attachments. Never equate "downloaded successfully" with disaster recovery unless reconstruction is supported and testable.

## Separate product support from current Agent access

Record four facts distinctly:

1. what the platform officially supports (anchored to primary docs as of `YYYY-MM-DD`);
2. what the current Agent harness can execute right now;
3. what connector, CLI, SDK, or configuration is not yet installed;
4. what account selection or authorization only the user can grant after SPEC approval.

Compare the verified operating model against the user's workflow requirements. If the candidate base fails a material requirement, surface the gap and reopen the base decision rather than forcing a poor fit.
