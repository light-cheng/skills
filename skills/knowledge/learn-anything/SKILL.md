---
name: learn-anything
description: Distill a repeatable workflow, paper, or codebase technique into a portable agent skill package.
disable-model-invocation: true
argument-hint: "[source-path-or-topic] [--out <skills-dir>] [--update]"
---

# Learn Anything

Distill source material (session transcripts, engineering notes, papers, documentation, folder workflows,
or user corrections) into an idiomatic Agent Skill package only when the source proves a repeatable
operating method. Extract durable procedures and decision logic rather than passive summaries, and never
invent generic filler to mask missing evidence.

When the source fits a knowledge-base note (`/kb-init`) or a single repository rule (`CLAUDE.md` / `AGENTS.md`)
better than an operational skill, recommend that target with suggested inputs and stop rather than silently
invoking another user-invoked skill.

## Workflow

### 1. Gather Primary Evidence

Inspect `$ARGUMENTS` (or active session context when no path is passed) alongside referenced files, notes, and user corrections.

- Preserve operational specifics verbatim: exact commands, CLI flags, file paths, schemas, API identifiers, error strings, and repeated corrections (`use Y instead of X`).
- Invoke `research` when external docs, papers, specs, or broad codebase legwork are needed for primary sources.
- **Graceful fallback** (when `research` is absent): dispatch a subagent with a **fresh context window** (not a fork of the current conversation) to verify claims against primary sources (official docs, source code, specs, first-party APIs) and return cited findings.
- **Completion criterion**: Every claim, command, path, and decision rule required to evaluate the candidate method is grounded in primary source evidence.

### 2. Run the Method Contract and Source-Sufficiency Gate

Read [references/method-contract.md](references/method-contract.md) and evaluate the gathered evidence against all 11 Method Contract fields, artifact-type filters, placeholder traps, and destination rules before drafting:

- **`not_promoted`**: One-off session logs, single-incident postmortems, ad-hoc lookups, isolated one-line rules, or passive topic summaries without a repeatable procedure and decision tree. Write zero skill files.
- **`BLOCKED`**: Reusable method intent exists, but required contract fields lack primary source evidence, contain unresolved placeholders (`TODO`, `TBD`, `N/A`, `<fill-in>`, `[placeholder]`, or template boilerplate), conflict on invocation mode, miss local resources, or collide with an existing skill directory without `--update` authority. Write zero skill files.
- **`eligible`**: Every required Method Contract field (`purpose`, `triggers`, `invocation_type`, `inputs`, `ordered_method`, `decisions`, `constraints`, `failure_modes`, `outputs`, `resources`, `verification`) is backed by primary evidence with zero unresolved gaps. Hold the contract in working memory as an internal blueprint; never emit the contract itself as an installable skill.
- **Completion criterion**: Exactly one verdict (`not_promoted`, `BLOCKED`, or `eligible` with all 11 fields populated) is decided; non-eligible runs stop here and jump directly to the Output Contract.

### 3. Author the Skill Package

Resolve `<output-root>/<skill-name>/` (`skill-name` in kebab-case under 64 characters; default `<output-root>`
to `.claude/skills` or the user-supplied collection directory). Reject symlink traversal, and halt as `BLOCKED`
(`duplicate`) if `<output-root>/<skill-name>/` already exists without `--update` or explicit user approval.

Invoke `writing-for-agents` (and its `SKILL-MECHANICS.md` reference) to write `SKILL.md`, `agents/openai.yaml`,
and only the `references/` or `scripts/` files justified by the Method Contract. **Graceful fallback** (when
`writing-for-agents` is absent): apply these authoring mechanics directly:

1. **Invocation sync**: Use **model-invoked** only for autonomous reach (omit `disable-model-invocation` in
   `SKILL.md`, front-load one crisp trigger per branch in `description`, and set `allow_implicit_invocation: true`
   under `policy` in `agents/openai.yaml`). Use **user-invoked** for manual commands (set
   `disable-model-invocation: true`, quote `argument-hint` when arguments apply, write a concise human-facing
   one-line `description` without trigger lists, and set `policy.allow_implicit_invocation: false`). Always
   populate `interface.display_name` and `interface.short_description` in `agents/openai.yaml`.
2. **Progressive disclosure**: Keep `SKILL.md` focused on the ordered steps executed on every run; push branch-specific tables, schemas, or deep catalogs into `references/<topic>.md` behind explicit markdown links.
3. **Leading words and positive framing**: Anchor recurring behaviors with compact pretrained leading words, state positive target actions instead of weak prohibitions, and prune default-behavior no-ops.
4. **Step completion criteria**: End each ordered step with a checkable, high-demand completion criterion, and require a **fresh context window** whenever the generated skill dispatches subagents.
5. **Evidence fidelity and link hygiene**: Preserve exact commands, paths, error strings, and corrections; create
   no empty directories, placeholder files, or hidden manifests; verify every relative markdown link resolves on
   disk; write newly authored English prose without em-dashes.

- **Completion criterion**: `SKILL.md`, `agents/openai.yaml`, and justified resources exist inside `<output-root>/<skill-name>/` with synced invocation metadata and zero placeholder text.

### 4. Verify and Converge

1. Validate strict YAML frontmatter in `SKILL.md` (`name` matching directory basename, non-empty `description`)
   and `agents/openai.yaml` (`interface` fields, synced `policy.allow_implicit_invocation`), verify all relative
   markdown links resolve, and run workspace frontmatter or plugin validators when present.
2. Confirm every command, path, decision rule, constraint, failure mode, and verification gate from the Method
   Contract survived intact, and keep any target-repo durable runtime records under `.scratch/`.
3. Run `acceptance` at **Inline scale** (`agent-skill` criteria) on `<output-root>/<skill-name>/` when available
   and repair any findings; otherwise complete a self-verification check against Steps 2 and 3.
- **Completion criterion**: Static metadata/link checks and `acceptance` (or self-verification fallback) pass.

## Output Contract

- **`Status: created` or `Status: updated`**: Package path, invocation mode, written files, distilled Method Contract summary, and verification evidence.
- **`Status: not_promoted`**: Classification reason, concise learning summary preserving extracted commands,
  paths, and corrections, and the recommended home if any (`CLAUDE.md` / `AGENTS.md` or `/kb-init`).
- **`Status: BLOCKED`**: Missing Method Contract fields, placeholder values, invocation conflict, or duplicate destination path, plus the exact primary evidence or user decision needed to unblock authoring.
