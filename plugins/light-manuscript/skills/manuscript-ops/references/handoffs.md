# Skill coordination and graceful fallbacks

`manuscript-ops` works both alongside the `light` Core plugin plus `mattpocock/skills` (**Base workflow**) and standalone via `npx skills add light-cheng/skills`. Every external skill integration degrades cleanly without private clones or hard-locked dependency scripts.

## Host-neutral invocation

Render logical skill calls using the active harness syntax (`/skill-name` in Claude Code and slash-command hosts, `$skill-name` in Codex, or explicit skill activation in other Agent Skills clients). Every subagent dispatched during manuscript work (delegated writer, reviewer, independent Evaluator, or primary-source researcher) must start with a **fresh context window**, never a fork of the active writer conversation.

## Brief intake and optional discovery

Accept any user-approved `ManuscriptBrief` directly without gating on upstream discovery artifacts.

- **Open scope before Brief approval**: clarify bounded questions directly with the user, or suggest `/grill-with-docs` or `/to-spec` when the Base workflow is installed.
- **External primary-source gathering**: invoke `research` when installed; otherwise dispatch a primary-source research subagent in a **fresh context window** to collect dated or hash-bound primary sources for `source-register.tsv`.
- **Project setup preferences**: read `docs/agents/light-project.md` (`Decision data` and default acceptance profile) when created by `/light-setup`. When absent, default to `Decision data: on-device` and `Profile: manuscript` without blocking initialization.

## Milestone convergence and sign-off (`acceptance`)

- **Structured route**: invoke `acceptance` at **Inline scale** for bounded review-and-repair convergence (up to 3 rounds via a **fresh-context** reviewer subagent).
- **Project route**: invoke `acceptance` at **Charter scale** (`init`, `run`, `resume`) with `Profile: manuscript`, storing the frozen **Acceptance charter** and durable acceptance records strictly under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/`; `.manuscript-ops/reviews/` may store or mirror only the machine JSON milestone receipt referencing that `.scratch/` charter). After convergence, `acceptance` dispatches an independent Evaluator in a **fresh context window** to verify `manuscript_evidence` across all applicable axes and issue `PASS`, `FAIL`, or `BLOCKED`.
- **Graceful fallback when `acceptance` is absent**: freeze the manuscript review packet (`ReviewMatrix`, artifact SHA-256 snapshot, Concept Grounding rules, and format-QA records) and run bounded review plus independent evaluation in separate **fresh context windows** (or ask the user to run the Evaluator packet in a new session, recording `independence: "fresh_session"`). If no independent fresh context is available, record `independence: "degraded"` and return `BLOCKED`.

## Direction changes (`redirect`)

When an approved Brief, outline, or Acceptance charter stops holding (or `acceptance` returns `FAIL` with `cause: "direction"`), invoke `redirect` to write a **Change proposal** under `.scratch/<feature>/changes/` (or comment on the active tracker issue per `docs/agents/issue-tracker.md`) and halt until human approval updates the Brief. If `redirect` is not installed, halt active writing, write the structured Change proposal directly to `.scratch/<feature>/changes/`, and wait for explicit user approval.

## Optional route judgment (`decide`)

For borderline routing ambiguity, call `decide` (`light-decision-mcp`) with question ID `manuscript-ops/route` ([semantic-routing.md](semantic-routing.md)). When `decide` is absent, `off`, or uncalibrated, keep the deterministic `needs-v2` route automatically.

## Installing companion plugins

When the user wants the full companion workflow (`acceptance`, `redirect`, `decide`, `light-setup`), recommend installing the `light` Core plugin alongside `light-manuscript` from the `light-cheng` plugin marketplace or via:

```text
npx skills add light-cheng/skills
```

Never install plugins or packages automatically during manuscript execution.
