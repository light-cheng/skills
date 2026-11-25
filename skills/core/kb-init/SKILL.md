---
name: kb-init
description: Interview, design, and initialize a durable personal or project knowledge base with historical provenance and maintenance operations.
disable-model-invocation: true
argument-hint: "[domain, goal, or target location]"
---

# KB Init

Design a knowledge base from the user's real workflow, synthesize an implementation SPEC only after the user explicitly ends the interview, and initialize the base only after explicit SPEC approval. Keep the workflow platform-agnostic across local files, databases, and connected software services.

## Core invariants

- **User-owned decisions**: Discover facts; leave architectural choices to the user. Preserve any choice the user reserves for case-by-case runtime control without inventing fallback defaults.
- **Workflow before platform recipes**: Derive storage, schemas, and navigation from concrete intake and retrieval scenarios rather than canned software templates. Prefer stable file, CLI, MCP, API, SDK, or import/export interfaces over GUI automation.
- **Historical provenance and active maintenance**:
  - Anchor every mutable factual or code claim to an explicit calendar date (`YYYY-MM-DD`) or `repo@commit` revision (never bare "currently").
  - Mark outdated claims `superseded` with a pointer to the newer record rather than erasing history silently when history matters.
  - Ship concrete `Ingest`, `Query`, and `Lint` maintenance operations.
- **Consumer and secret boundaries**:
  - Define outward export or query interfaces without designing downstream apps, reports, or dashboards unless scope is explicitly expanded.
  - Never ask users to paste API keys, tokens, or passwords into chat, docs, examples, or shell arguments; use OAuth/connector auth or an approved local secret store.

## External capabilities and graceful fallbacks

- **`research` (external or platform facts)**:
  - Read [references/research-contract.md](references/research-contract.md) whenever an open decision or Base Discovery depends on current, unfamiliar, or unverified facts, then invoke `research`.
  - **Graceful fallback**: when `research` is not installed, dispatch a **fresh-context** primary-source research subagent (start it with a fresh context window, never a fork of the current conversation) to verify official docs, specs, or first-party APIs and save cited findings under `.scratch/kb-init/research/` (or session scratch outside the target KB destination). If subagents are unavailable, verify primary sources inline under the same isolation rules or keep the decision `unresolved`.
- **`acceptance` (implementation verification)**:
  - During final validation, invoke `acceptance` at Inline scale (or Charter scale under `.scratch/` when milestone sign-off is requested) to verify the initialized base against the approved SPEC.
  - **Graceful fallback**: when `acceptance` is not installed, execute the end-to-end `Ingest`, `Query`, `Lint`, provenance, permission, and reconnection checks directly with live write/read-back evidence before handoff.

## Workflow

### 1. Interview and decision map

Read [references/interview-contract.md](references/interview-contract.md) before asking your first question.

- When invoked with little or no context, open directly with a plain-language question about what knowledge the user wants to keep and use rather than asking for a formal brief or technology stack.
- Prioritize user questions: when the user asks why, challenges a proposal, or requests a comparison, answer in plain terms first and keep the underlying decision open until the user decides.
- Track major design areas in an internal decision map:
  - **Status**: `unresolved | discussing | researching | settled | deferred | not-applicable`.
  - **Provenance**: `user-explicit | user-accepted-recommendation | verified-environment-fact | user-deferred | not-applicable` (keep inferred defaults or unasked structural questions `discussing` and surface them with tradeoffs).
  - **Depth bar**: before settling any high-impact choice, establish the real workflow, the user's priority or tradeoff, and at least one concrete future scenario. Reopen earlier choices whenever later facts invalidate them.
- **Conditional branches during the interview**:
  - *Direct human browsing*: when people will open or operate the base directly, read [references/human-navigation.md](references/human-navigation.md) before settling structure or navigation. Skip human navigation layers for Agent-only stores.
  - *Candidate software or service base*: read [references/base-discovery.md](references/base-discovery.md) before settling the base or connection route. Verify current official programmatic access, permissions, attachments, search, and backup guarantees without installing tools, authenticating, or creating target objects pre-approval.
  - *Research detour*: follow [references/research-contract.md](references/research-contract.md). Report research as running only after the harness confirms dispatch, read the completed report yourself before using it, and surface conflicts with earlier user choices explicitly instead of overwriting them.

### 2. Readiness gate and interview close

- Before using any closure-signaling wording (such as "last question", "wrapping up", or "ready to finalize"), run [references/readiness-check.md](references/readiness-check.md).
- Ask the smallest targeted question needed to close any gap in provenance, depth, exact destination, maintenance entry point, or `Ingest` / `Query` / `Lint` mechanisms.
- Once readiness passes, tell the user that design and implementation prerequisites are covered and invite further questions, revisions, research detours, or SPEC generation.
- **Completion criterion**: The user explicitly ends the interview and asks for the SPEC. Short acknowledgements, answering the latest question, or asking another question keep the interview open.

### 3. Design synthesis and implementation SPEC

Read [references/design-guide.md](references/design-guide.md) and [references/spec-guide.md](references/spec-guide.md).

- Synthesize three distinct models before mapping them onto the selected base without silently distorting user requirements:
  1. **Knowledge model**: unit shape, metadata, relations, `YYYY-MM-DD` / `repo@commit` provenance, `superseded` lifecycle, and `Ingest` / `Query` / `Lint` loops.
  2. **Human navigation model** (when humans browse directly): entry point, primary dimensions, scale behavior, and physical vs virtual views.
  3. **Base operating model**: native storage, connection route, permissions, automation limits, reconnection, and backup guarantees.
- Keep pre-SPEC `.scratch/` research notes out of final KB deliverables unless the user asks to retain them, and note accurately if harness rules wrote scratch research evidence locally.
- Present the SPEC (marking any remaining blocker explicitly rather than guessing) and **stop**.
- **Completion criterion**: The user gives explicit approval to implement. Questions or change requests keep the SPEC gate closed.

### 4. Connection and implementation

- **External connection**: when the approved base requires an app, CLI, connector, MCP, API, or SDK connection, read [references/connection-setup.md](references/connection-setup.md), prefer project-scoped configuration, and validate live read, write, read-back, search, and attachment operations before claiming connectivity.
- **Scaffolding**: build the approved structure, navigation views or indexes, discoverable maintenance entry point, and `Ingest`, `Query`, and `Lint` workflows without silent mechanism substitution or unrequested Git initialization.
- **Blocked steps**: if an environment limit blocks a base-specific step, complete all base-independent artifacts and state what remains, why, and the exact user or capability action that unblocks it.
- **Completion criterion**: Every approved artifact executable in the current environment exists at the target destination (and live connection probes pass when applicable), with any blocked step isolated and documented.

### 5. Validation and handoff

- **Validation**: verify end-to-end `Ingest`, `Query`, `Lint`, source and `YYYY-MM-DD` / `repo@commit` provenance, permissions, backup semantics, and reconnection against the SPEC via `acceptance` (or the inline operational fallback).
- **Handoff**: concisely report created paths/containers, `Ingest` / `Query` / `Lint` entry points, future session reconnection, automatic vs user-gated actions, backup guarantees (`offline snapshot`, `portable export`, or `recoverable backup`), and any remaining manual step.
- **Completion criterion**: Validation passes (or blocked manual steps have verified handoff artifacts) and the user receives a concise, jargon-free operating summary.
