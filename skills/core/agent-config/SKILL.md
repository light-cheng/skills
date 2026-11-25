---
name: agent-config
description: Right-size execution topology, user-confirmed capability tier, and host-supported reasoning effort across single-model and multi-model agent harnesses. Use before multi-ticket or complex work where model tier, effort, or worker topology matters, when configuring or repairing host profiles (agent-config setup), or when previewing and applying host configuration through the agent-config MCP server.
---

# Agent Config

`agent-config` maps verified Agent Host capabilities and a user-confirmed profile to a right-sized execution topology, capability tier (`routine`, `standard`, `high`, `review`), and resolved reasoning effort. It supports single-model and multi-model hosts as equal peers, binds dynamically to the optional `agent-config` companion MCP server when present, and degrades cleanly to session-local `plan-only` mode when absent.

## Setup gate

- **Explicit setup (`agent-config setup`):** Run the setup questionnaire and companion bootstrap flow in [setup.md](references/setup.md). Setup prepares or repairs the host registration and user-confirmed profile, then stops without planning current work.
- **Execution planning (default):** Check live companion health via `get_setup_status` per [companion-contract.md](references/companion-contract.md). When the `agent-config` companion MCP is absent, unreachable, or stale, offer setup or continue in session-local `plan-only` mode using user-confirmed session inputs (**Graceful fallback**). Never auto-install packages, spawn daemons, or edit host config files silently.

## Steps

1. **Verify host evidence and profile.** Inspect active models, `supported_effort_values`, subagent/thread support, and concurrency limits via `inspect_host` and `get_profile` (or collect user-confirmed session inputs when running `plan-only`). Done when every candidate model and capability is backed by current host evidence ([host-evidence-schema.md](references/host-evidence-schema.md)) and user-confirmed tier bindings ([profile-schema.md](references/profile-schema.md)).
2. **Assess task shape.** Classify the work semantically as `single-pass` or `decomposed` using [task-assessment.md](references/task-assessment.md), judging structural coupling and independent slices rather than word count. If `decomposed` and formal tickets do not yet exist, return `readiness: NEED_PROJECT_TICKETS`, `handoff: "/to-tickets"`, and `execution_config: null`. Done when task shape is classified and ticket existence is verified.
3. **Profile difficulty, tier, and effort.** Map work difficulty (`routine`, `standard`, `high`, `critical`) to the profile's confirmed tiers and resolve abstract effort policies (`lowest-supported`, `default`, `highest-supported`) strictly to discrete values present in the host's `supported_effort_values`. When task complexity or reasoning need is not already authoritative, optionally evaluate `agent-config/task-complexity` and `agent-config/reasoning-need` via `decide` (see Optional `decide` intake) and run `scripts/agent_config.py` ([host-evidence-schema.md](references/host-evidence-schema.md#script-entry)). Done when target model and resolved effort are verified legal on the host.
4. **Select peer execution topology.** Pick one of the four peer modes in [routing.md](references/routing.md):
   - **Case A (Single-model + Single-pass):** Execute directly in the current session with the confirmed model and resolved effort, without inventing synthetic sub-roles.
   - **Case B (Single-model + Decomposed):** Keep the current session as Controller and dispatch each ready ticket to a worker subagent started with a **fresh context window** (never a fork of the current conversation), using the single confirmed model and resolved effort within the host concurrency cap.
   - **Case C (Multi-model + Single-pass):** Execute in a single session using the user-confirmed tier model and resolved effort matched to task difficulty, reserving the `review` tier for independent verification when needed.
   - **Case D (Multi-model + Decomposed):** Keep the Controller on the `high` or `review` tier and dispatch each ready ticket to a worker subagent started with a **fresh context window**, binding each worker to its ticket's confirmed tier model and resolved effort.
5. **Emit plan and preview-before-apply.** Render the adaptive plan and `AgentConfigResult` envelope per [plan-schema.md](references/plan-schema.md). Keep `mode: plan-only` unless the user explicitly requests host configuration mutation and approves the diff from `preview_configuration`, followed by `apply_configuration` and `validate_configuration`. Done when the plan (and post-apply validation, if applied) is returned.

## Core invariants

- **User-confirmed tiers only:** Record factual model availability from host evidence; bind models to `routine`, `standard`, `high`, and `review` tiers strictly from user confirmation, never from model names or guessed rankings.
- **Single-model is a first-class peer:** Treat Case A and Case B as primary topologies with full effort and fresh-context worker orchestration.
- **Verified discrete effort:** Emit only effort strings present in the host's `supported_effort_values` (never emit unverified literal `"max"`).
- **Fresh-context workers and reviewers:** Launch every delegated worker or independent reviewer subagent with a **fresh context window**, never a conversation fork.

## Optional `decide` intake (`light-decision-mcp`)

When `difficulty_source` is `unknown` or `heuristic`, or when `reasoning_policy` is unset:
- Invoke `decide` (`light-decision-mcp` `score` or `decide` tool) within the repository's `Decision data` boundary (`docs/agents/light-project.md`, defaulting to `on-device`) for:
  - `agent-config/task-complexity` with ordered levels `["routine", "standard", "high", "critical"]`
  - `agent-config/reasoning-need` with ordered levels `["low", "medium", "high"]`
- Pass the normalized score envelope into `scripts/agent_config.py` (`--decide-scores-json` or `--decide-scores-file`) alongside `~/.config/light/decision-policy.json` (`--decision-policy-file`) or explicit `--calibration-thresholds-json`.
- **Graceful fallback:** `scripts/abstract_profiler.py` validates finite probability distributions summing to `1.0` and expected-score consistency, requires per-question calibration, enforces `DOWNGRADE_MARGIN = 0.15` on downward shifts, and falls back deterministically (`build_deterministic_profile`) whenever `decide` is unavailable, `Decision data: off`, uncalibrated, malformed, or below threshold/margin.

## Handoff

Return `AgentConfigResult` (`readiness`, `mode`, `setup_state`, `handoff`, `execution_config`):
- `readiness: READY` -> recommend `/implement` for `single-pass` work or `/implement-spec` for `decomposed` ticket graphs (an already active caller resumes within its authorized scope; standalone runs report the recommendation and stop).
- `readiness: NEED_PROJECT_TICKETS` -> recommend `/to-tickets` with `execution_config: null`.
- `readiness: NEED_INPUT` -> recommend `setup` (`agent-config setup`) with `execution_config: null`.
- Route review convergence and milestone sign-off to `acceptance` (which delegates git code diffs to `code-review` when installed and falls back to its built-in diff and criteria review when absent).

## References

- [setup.md](references/setup.md): Setup questionnaire, tier binding, effort resolution, and `agent-config setup` CLI bootstrap
- [routing.md](references/routing.md): 2x2 peer execution modes (Cases A, B, C, D), fresh-context worker dispatch, and handoffs
- [task-assessment.md](references/task-assessment.md): Task shape, difficulty rubric, anti-wordcount rule, and `decide` score intake
- [companion-contract.md](references/companion-contract.md): 8-tool `agent-config` MCP protocol v1, preview-apply gate, and Graceful fallback
- [harness-support.md](references/harness-support.md): 10 native coding-agent adapters and generic `plan-only` fallback
- [profile-schema.md](references/profile-schema.md): Host- and workspace-scoped `profile_version: 1` schema and stale triggers
- [host-evidence-schema.md](references/host-evidence-schema.md): Canonical `inspect_host` schema and `scripts/agent_config.py` CLI flags
- [plan-schema.md](references/plan-schema.md): Execution plan layout, `AgentConfigResult` contract, and `acceptance` review sizing
- [examples.md](references/examples.md): Worked execution plans across Cases A, B, C, and D
