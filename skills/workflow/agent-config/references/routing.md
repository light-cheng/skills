# Execution routing

This reference defines the 2x2 peer execution matrix, fresh-context worker rules, and `AgentConfigResult` handoffs across single-model and multi-model hosts.

## 1. The 2x2 peer execution matrix

| Model mode \ Task shape | `single-pass` | `decomposed` |
|---|---|---|
| **Single-model (`single`)** | **Case A:** Direct execution in the current session with confirmed model and resolved effort; zero synthetic roles. | **Case B (P0):** Controller in current session + worker subagents in **fresh context windows**, same confirmed model, resolved effort. |
| **Multi-model (`multi`)** | **Case C:** Single-session execution using the user-confirmed tier model and resolved effort matched to task difficulty. | **Case D (P0):** Controller on `high`/`review` tier + worker subagents in **fresh context windows**, each bound to its ticket's confirmed tier model and effort. |

Single-model mode is a first-class peer topology, not a degraded fallback. Both Case B and Case D are primary multi-ticket paths.

## 2. Operating rules per mode

### Case A: Single-model + Single-pass
- Execute directly in the active session using `single_model.model` and resolved `execution_effort`.
- Keep one clean execution loop; do not invent artificial Explorer, Planner, or Merger personas.
- Use a helper subagent (started with a **fresh context window**) only when isolating heavy read-only source reading protects the main context window.

### Case B: Single-model + Decomposed (P0)
- Require formal tickets first; if missing, stop with `readiness: NEED_PROJECT_TICKETS` and `handoff: "/to-tickets"` (**Graceful fallback** without `mattpocock/skills`: slice tickets directly into `.scratch/<feature>/issues/<NN>-<slug>.md` or tracker issues per `docs/agents/issue-tracker.md`).
- Keep the current session as Controller (ticket scheduling, integration review, git state).
- Dispatch each unblocked ticket to a worker subagent started with a **fresh context window** (never fork the Controller's conversation history), throttled to `concurrency`. If the host lacks subagents/threads, execute tickets serially.
- Use the single confirmed model throughout without inventing synthetic tier labels.

### Case C: Multi-model + Single-pass
- Map work-item difficulty (`routine`, `moderate`/`standard`, `demanding`/`high`, `critical`) to the user-confirmed tier (`routine`, `standard`, `high`) and resolve host effort.
- Execute directly in a single session without spawning extra subagents solely because multiple models exist.
- When independent verification is needed, run `acceptance` in a **fresh context window** using the `review` tier.

### Case D: Multi-model + Decomposed (P0)
- Require formal tickets first; if missing, emit `readiness: NEED_PROJECT_TICKETS` and `handoff: "/to-tickets"` (**Graceful fallback** without `mattpocock/skills`: slice tickets directly into `.scratch/<feature>/issues/<NN>-<slug>.md` or tracker issues per `docs/agents/issue-tracker.md`).
- Run the Controller in the current session on the confirmed `review` or `high` tier.
- Launch each ready ticket on the unblocked frontier in a worker subagent started with a **fresh context window** (up to `concurrency`), assigning:
  - `routine` ticket -> `routine` tier model + resolved effort
  - `moderate` / `standard` ticket -> `standard` tier model + resolved effort
  - `demanding` / `high` ticket -> `high` tier model + resolved effort
  - `critical` ticket -> `high` tier model + `highest-supported` effort
- Ensure concurrent workers own disjoint files or isolated worktrees before parallel dispatch.

## 3. Routing handoffs in `AgentConfigResult`

- `readiness: "READY"` + `task_shape: "single-pass"` -> `handoff: "/implement"` (**Graceful fallback** without `mattpocock/skills`: execute the bounded slice directly in the active session), non-null `execution_config`.
- `readiness: "READY"` + `task_shape: "decomposed"` -> `handoff: "/implement-spec"` (**Graceful fallback** without `mattpocock/skills`: run the Controller loop over `.scratch/<feature>/issues/`, dispatching **fresh-context** worker subagents across the unblocked frontier), non-null `execution_config`.
- `readiness: "NEED_PROJECT_TICKETS"` -> `handoff: "/to-tickets"` (**Graceful fallback**: write `.scratch/<feature>/issues/<NN>-<slug>.md` or native tracker issues), `execution_config: null`.
- `readiness: "NEED_INPUT"` -> `handoff: "setup"`, `execution_config: null`.
- `readiness: "BLOCKED" | "UNSUPPORTED"` -> `handoff: null`, `execution_config: null`.

Review convergence and final milestone sign-off always route to `acceptance` (delegating git code diffs to `code-review` when installed, with built-in fallback when absent).
