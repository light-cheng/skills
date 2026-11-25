---
name: light-setup
description: Configure a repository's Light workflow bridge and route across Base workflow, Light skills, and session phase boundaries.
argument-hint: "[setup | question or workflow phase]"
disable-model-invocation: true
---

# Light Setup

Entry point for initializing Light in a repository (**Setup mode**) and choosing the next skill or context boundary (**Route mode**).

- Run **Setup mode** when passed `setup`, or when asked to configure Light for the current repository.
- Run **Route mode** when asked which skill fits next, how Light pairs with the Base workflow, or how to cross a session boundary.

## Setup mode

Configure the repository idempotently after inspecting existing files and confirming choices with the user:

1. **Inspect existing state.** Check `CLAUDE.md`, `AGENTS.md`, `docs/agents/` (`issue-tracker.md`, `domain.md`, `triage-labels.md`, `light-project.md`), `.scratch/`, and whether `/setup-matt-pocock-skills` is installed or has already run.
2. **Check Base workflow prerequisites (with Graceful fallback).**
   - When `docs/agents/issue-tracker.md` already exists, layer directly over it and preserve `## Agent skills` and `docs/agents/*.md`.
   - When `docs/agents/issue-tracker.md` is absent and `setup-matt-pocock-skills` is installed, offer `/setup-matt-pocock-skills` first if the user wants GitHub/GitLab tracker or domain-doc scaffolding; otherwise proceed standalone using `.scratch/<feature>/` local markdown as the Graceful fallback.
3. **Confirm project defaults.** Lead with recommended defaults and ask only what arguments or existing files have not settled:
   - **`Decision data`**: privacy ceiling for `decide` (`on-device | private-network | third-party | off`; default: **`on-device`**).
   - **`Acceptance profile`** (optional): default Charter-scale profile for `acceptance` (`generic | software | manuscript | agent-skill | specification`; omit when unneeded).
   - **Instruction target**: prefer whichever root file already contains `## Agent skills`; otherwise edit `CLAUDE.md` if present, else `AGENTS.md` if present, or ask which one to create when neither exists (never create a second instruction file alongside an existing one).
4. **Preview and write idempotently.** Show the draft edits, get user confirmation, then update in place without duplicating headings or overwriting unrelated sections:
   - In the selected `CLAUDE.md` or `AGENTS.md`, insert or replace `## Light workflow` with this 3-line middleware bridge:
     ```markdown
     ## Light workflow

     - Project settings (`Decision data` boundary and optional default acceptance profile) live in `docs/agents/light-project.md`; durable runtime records stay under `.scratch/` (falling back to `.scratch/<feature>/` local markdown when `docs/agents/issue-tracker.md` is absent).
     - Invoke `redirect` whenever an approved spec, ticket graph, or acceptance charter stops holding; halt implementation and record a Change proposal before editing downstream plans.
     - Run `acceptance` to converge review rounds and verify real execution, test, or render evidence before closing tickets, pull requests, or milestones.
     ```
   - Create or update `docs/agents/light-project.md`:
     ```markdown
     # Light Project

     - Decision data: on-device
     - Acceptance profile: software
     - Working area: .scratch
     ```
     Omit `Acceptance profile:` when unset, and preserve any user notes outside these fields on rerun.

Done when every confirmed target is written with a single `## Light workflow` section, surrounding content is intact, and updated paths plus Base workflow status are reported.

## Route and phase-boundary mode

Before stating a specific skill's detailed rules or advising to skip a step, read its `SKILL.md` when installed. Inspect `docs/agents/` and `.scratch/` only when answering "what next?" for the active repository; answer general workflow or boundary questions directly.

### Main flow: Base workflow + Light

1. **Clarify and plan**: `/wayfinder` (multi-session foggy effort) or `/grill-with-docs` (in-repo interview updating `GLOSSARY.md` and `docs/adr/`, or `/grill-me` outside a repo; `/research` or a primary-source subagent started with a **fresh context window**; `/prototype` for runnable design checks) -> `/to-spec` -> `/to-tickets`. Keep interview through `/to-tickets` in one unbroken window inside the ~150k Smart Zone. *Graceful fallback without `mattpocock/skills`*: settle open decisions in chat, write `.scratch/<feature>/spec.md`, and slice dependency-ordered `.scratch/<feature>/issues/<NN>-<slug>.md` tickets directly.
2. **Configure execution (optional)**: Reach for `agent-config` when the user asks for capability tiering (`routine`, `standard`, `high`, `review`), topology selection (`single session` vs `controller-workers` starting each worker subagent with a **fresh context window**), or `agent-config` MCP host setup. Ready unblocked tickets route directly to `/implement` or `/implement-spec` unless execution configuration itself is the goal.
3. **Implement and adapt**: `/implement` (one ticket per fresh session, driving `/tdd`) or `/implement-spec` (parallel implementer subagents, each started with a **fresh context window**, across the ready frontier; standalone fallback: execute unblocked `.scratch/<feature>/issues/` tickets sequentially). When an approved spec, ticket graph, or charter stops holding, `redirect` halts implementation and files a **Change proposal** under `.scratch/<feature>/changes/` (or tracker) for human approval before `/to-spec` or `/to-tickets` updates.
4. **Converge, sign off, and ship**: `/code-review` (Standards + Spec diff check) and `acceptance` (**Inline scale**: up to 3 review-and-repair rounds via a reviewer subagent started with a **fresh context window**, delegating git diffs to `code-review` with built-in diff fallback, plus verified test/execution/render evidence; **Charter scale**: frozen `.scratch/<feature>/acceptance/` charter + independent Evaluator subagent started with a **fresh context window** returning `PASS | FAIL | BLOCKED`) -> `/pr` -> `/retro`.
5. **On-ramps and shared vocabulary**: `/triage` prepares incoming external issues; `/diagnosing-bugs` reproduces hard regressions red-first before fixing; `/improve-codebase-architecture` (using `codebase-design` and `domain-modeling`) surfaces module-deepening work; `wizard` scripts human-only credential or dashboard steps (Graceful fallback: inline step-by-step human checklist).

### Orthogonal and standalone skills

- **`decide`** (model-invoked): **Bounded judgment** (`choice`, `yes_no`, `score`) via `light-decision-mcp` within `Decision data` limits (self-judgment fallback), logged to `.scratch/<feature>/decisions.md`.
- **`humanizer`** (model-invoked): Bilingual EN/ZH anti-AI-slop rewriting, plus register-routed **Technical / Clarity Mode** (ASD-STE100 and 简明技术中文) for specs, SOPs, and engineering docs.
- **`/kb-init`** (user-invoked): Initialize or maintain (`Ingest / Query / Lint`) a knowledge base with explicit date or `repo@commit` provenance, delegating source gathering to `research` (Graceful fallback: dispatch a primary-source subagent started with a **fresh context window**).
- **`/learn-anything`** (user-invoked): Gate candidate material through the Method Contract & Source-Sufficiency Gate and author reusable skills via `writing-for-agents` (Graceful fallback: built-in authoring checklist covering progressive disclosure, invocation sync, and `agents/openai.yaml`).
- **`manuscript-ops`** (optional `light-manuscript` plugin): Multi-phase book and publication workflows from an approved brief with `needs-v2` routing, Concept Grounding review, and `acceptance` milestone gates.

### Phase boundaries and transition

When choosing how to cross a session boundary (`Continue` -> clear context -> `handoff` -> `Subagent` started with a **fresh context window** -> compact context), managing the ~150k Smart Zone, or trading off primary artifacts against summaries, read [`references/phase-boundaries.md`](references/phase-boundaries.md).

Done when you recommend **one** primary skill (plus at most one close neighbor) grounded in observed state, render the exact host command (`/<skill>` in Claude Code, `$<skill>` in Codex, or `Skill: <skill>`) for any user-invoked target, and wait for user approval before starting the next step.
