# Method Contract and Source-Sufficiency Gate

The **Method Contract** separates source evaluation from skill authoring. Raw notes, transcripts, papers, and codebase tours often narrate what happened once without proving how a future agent should act, branch, and verify results across runs. Build the Method Contract in working memory first; draft zero package files until every gate check below passes, and never write the Method Contract itself as an installable skill or hidden manifest file.

## Artifact-Type Filter (`eligible` vs `not_promoted`)

Promote a candidate into a skill only when it encodes a recurring operational procedure with at least two ordered steps, explicit decision logic, and checkable verification. Return `Status: not_promoted` (with a concise learning summary preserving useful commands, paths, decisions, and corrections) when the input belongs in a lighter or different form:

- **One-off narration or incident postmortem**: A single-incident root-cause log, release-specific hotfix transcript, one-time data backfill, or ad-hoc lookup/translation (`unique to this incident`, `just this release`, `one-off cutover`).
- **Passive topic summary**: Literature notes, weekly digests, architecture tours, or conceptual explainers that describe a system or paper without prescribing an actionable multi-step agent procedure.
- **Single-line repository rule**: An isolated project invariant (`always pass --frozen-lockfile`, `run pytest -q before committing`) with no multi-step workflow or branching logic. Recommend adding a concise line to `CLAUDE.md` or `AGENTS.md` instead of minting a skill.
- **Durable domain reference**: Factual synthesis or historical system context meant to be queried and maintained as notes rather than executed as a procedure. Recommend `/kb-init` or repository documentation instead.

**False-demotion guard**: Judge artifact type from the source's overall intent, purpose, triggers, and scope. Keep a complete repeatable method eligible when prose contrasts itself with non-methods (`no longer a one-off`, `not a passive summary`) or when a failure mode warns against outputs that contain `no procedure`.

## Required Method Contract Fields

All 11 fields below must be grounded in primary source evidence before entering Step 3 (`Author the Skill Package`). Missing evidence in any field halts execution with `Status: BLOCKED`:

| Field | Required Primary Evidence | Fails Gate (`BLOCKED`) When |
| :--- | :--- | :--- |
| `purpose` | Concrete, recurring operational outcome the skill produces. | Vague (`help with testing`) or purely descriptive (`notes on X`). |
| `triggers` | Distinct situations or signals that call for the method (one trigger per branch for `model-invoked`; human reach scenario for `user-invoked`). | Missing, generic (`when useful`), or indistinguishable from default behavior. |
| `invocation_type` | Exactly one of `user-invoked` or `model-invoked`, derived from explicit user intent or clear operational mechanics (`user-invoked` for manual commands, setup flows, or zero-context-load utilities; `model-invoked` when the agent or another skill must fire it autonomously). | Source demands both manual-only and autonomous firing on one skill without authorizing a split, or side-effect safety leaves invocation mode ambiguous. |
| `inputs` | Source artifacts, arguments, paths, tools, environment state, or credentials needed before starting. | Unspecified prerequisites or unverified assumptions. |
| `ordered_method` | At least 2 ordered, repeatable steps stripped of one-time session detours, each with an observable completion condition. | Single action step, unordered brainstorm bullets, or narrative history. |
| `decisions` | Branching rules, thresholds, or trade-offs that change what the agent does during execution. | Decisions left as `decide per case` without governing criteria. |
| `constraints` | Scope limits, safety invariants, path boundaries, and distilled user corrections (`use Y instead of X`). | Empty or filled with generic filler (`follow best practices`). |
| `failure_modes` | Concrete failure states, exact error signals, or blocker conditions and the required stop or recovery action. | Omitted or hand-waved (`handle errors gracefully`). |
| `outputs` | Exact files, edits, verdicts, or reports produced; durable runtime scratch artifacts in target repos placed under `.scratch/`. | Vague deliverable (`return helpful output`). |
| `resources` | Explicit `none`, or specific bundled `references/`, `scripts/`, or `assets/` justified by the method and verified to exist inside the authorized source root. | Relative resource file missing on disk, escaping source root, or mixing `none` with file paths. |
| `verification` | Concrete commands, validator checks, test assertions, render checks, or review criteria proving the output works. | Uncheckable bound (`ensure high quality`, `looks good`). |

## Source-Sufficiency and Placeholder Traps (`BLOCKED`)

Halt with `Status: BLOCKED` whenever a candidate has reusable-method intent but hits any sufficiency trap below. Never invent generic workflow steps, constraints, or quality checks to paper over missing evidence:

- **Unresolved draft tokens**: Treat standalone or inline placeholders (`TODO`, `TBD`, `N/A`, `unknown`, `coming soon`, `...`, `<fill-in>`, `<placeholder>`, `[TBD]`) inside `purpose`, `triggers`, `inputs`, `ordered_method`, `decisions`, `outputs`, `resources`, or `verification` as missing evidence even when section headings are present.
- **Template boilerplate**: Reject placeholder prose such as `insert workflow steps here`, `standard constraints apply`, or `add verification checks` as missing evidence.
- **Guardrail mention exception**: A `constraints`, `failure_modes`, or `verification` rule that names literal marker tokens as a condition to forbid or catch (for example, `Fail verification if generated files contain TODO or TBD markers`) is valid operational evidence rather than an unresolved placeholder.
- **External vs bundled resources**: Copy relative helper scripts, templates, or reference files into the new package only when they exist inside an explicitly supplied source directory and stay within package path bounds. Document external CLIs, MCP tools, or host-specific absolute paths as prerequisites under `inputs` rather than copying host files blindly.

## Mining Signal from Transcripts and Corrections

- **Strip session residue**: Discard dead-end debugging turns, typos, transient branch names, and timestamps; retain only the converged sequence and the decision rules that separated working paths from dead ends.
- **Promote user corrections into hard rules**: Repeated feedback (`stop mocking the parser, run the real fixture`, `quote argument-hint in YAML`) carries high operational signal. Encode the positive target action in `ordered_method` and `constraints`, and encode the failure signal in `failure_modes` and `verification` with exact flags, paths, and error strings intact.
- **Keep naming portable**: Derive a kebab-case skill name (`^[a-z0-9]+(?:-[a-z0-9]+)*$`, 63 characters max) from the reusable capability rather than a ticket number, sprint label, or date. Strip project-specific names unless the user is deliberately authoring a repo-private skill under `.claude/skills/`.

## Destination and Update Safety

- **Clean creation (`created`)**: Write `<output-root>/<skill-name>/` only when the destination path does not exist and neither `<output-root>` nor any parent segment inside the package boundary traverses an untrusted symlink.
- **Collision guard (`BLOCKED: duplicate`)**: When `<output-root>/<skill-name>/` already exists and the user has not passed `--update` or explicitly authorized updating that skill, stop before writing and report `Status: BLOCKED` (`duplicate`) with the existing path so unowned skills are never overwritten silently.
- **Authorized update (`updated`)**: When `--update` or explicit user confirmation is present, inspect the existing package first, update `SKILL.md`, `agents/openai.yaml`, and contract-justified `references/` or `scripts/` cleanly, preserve unrelated user-authored files, and keep zero hidden tracking manifests inside the skill directory.
