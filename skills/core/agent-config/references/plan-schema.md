# Execution plan schema

`agent-config` returns a structured `AgentConfigResult` envelope paired with an adaptive Markdown execution plan scaled to `task_shape`.

## 1. `AgentConfigResult` envelope

```json
{
  "readiness": "READY",
  "mode": "plan-only",
  "approval": "unknown",
  "setup_state": {
    "companion": "ready",
    "profile": "persisted"
  },
  "handoff": "/implement",
  "execution_config": {
    "model": "model-beta",
    "resolved_effort": "medium",
    "topology": "Case C",
    "worker_models": {}
  },
  "justification": "Selected model-beta for standard tier (topology: Case C, effort: medium)."
}
```

- `readiness`: `"READY" | "NEED_INPUT" | "NEED_PROJECT_TICKETS" | "BLOCKED" | "UNSUPPORTED"`.
- `execution_config`: Non-null strictly when `readiness === "READY"`; `null` for every other readiness state.
- `handoff`: Recommended next stage (`"/implement"` for ready `single-pass`, `"/implement-spec"` for ready `decomposed`, `"/to-tickets"` for `NEED_PROJECT_TICKETS`, `"setup"` for `NEED_INPUT`, or `null` when blocked/unsupported).

## 2. Markdown plan header and core sections

```text
Readiness: READY | NEED_INPUT | NEED_PROJECT_TICKETS | BLOCKED | UNSUPPORTED
Scope: current-item | spec-assessment | ticket-frontier | ticket-graph
Provider mode: tiered-multi-model | fixed-single-model
Task shape: single-pass | decomposed
Execution status: executable | waiting-on-dependencies | blocked-gate
Apply mode: plan-only | adapter-available-awaiting-approval | applied

Reason: <concise summary of mode, tier, effort, and topology>
```

Follow the header with five concise sections:
1. **`## Host summary`**: Current/selectable models, user-confirmed tiers, `supported_effort_values`, subagent/fresh-context support, concurrency cap, and active adapter.
2. **`## Task assessment`**: `single-pass` vs `decomposed`, semantic rationale (never word count), work-item difficulty, and whether `decide` or deterministic profiling supplied the tier.
3. **`## Execution config`**:
   - **Single-pass (Cases A & C):** Compact phase table (`Implementation` in `current-session`, optional read-only helper in a **fresh context window**). Omit artificial wave or ownership tables.
   - **Decomposed (Cases B & D):** Per-ticket routing table (`Ticket`, `Difficulty`, `Model / tier`, `Effort`, `Context` in a **fresh context window**, `Dependencies`, `Review`) plus `Coordination` (`Controller`, `Concurrency cap`, `Frontier`, `Integration`), adding an ownership matrix or waves only when shared paths or cap throttling require them.
4. **`## Review strategy`**: `Self-check`, `Controller Review`, or `Independent Review` (launched in a **fresh context window**), assigned `review` tier model and effort, and convergence handoff to `acceptance` (delegating git code diffs to `code-review` when installed).
5. **`## Limitations / unknowns`**: Any unverified host capabilities, `plan-only` constraints, or blocked dependencies.
