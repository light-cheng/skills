# Execution plan examples

Worked examples across the four peer modes defined in [routing.md](routing.md) and [plan-schema.md](plan-schema.md).

## Example 1: Case C (Multi-model + Single-pass)

```markdown
Readiness: READY
Scope: current-item
Provider mode: tiered-multi-model
Task shape: single-pass
Execution status: executable
Apply mode: plan-only

Reason: Multi-model profile confirmed; bounded parser bug fix maps to standard tier with medium effort in a single session.

## Host summary
- Current model: model-beta (available)
- Selectable models / tiers: model-alpha (routine), model-beta (standard), model-gamma (high, review)
- Reasoning control: available (low, medium, high)
- Context & execution: subagents available, fresh context windows available, concurrency cap 3
- Adapter: none (plan-only)

## Task assessment
- Task shape: single-pass
- Assessment rationale: Confined AST parser edge-case fix verified by existing unit suite.
- Work-item difficulty: moderate (standard)

## Execution config

| Phase | Model / tier | Effort | Context | Purpose |
|---|---|---|---|---|
| Implementation | model-beta (standard) | medium | current-session | Implement parser fix and unit tests |

## Review strategy
- Review type: Independent Review
- Review model & effort: model-gamma (review), effort: high, context: fresh context window
- Review handoff: Converge via acceptance (using code-review on the git diff when installed) and proceed via /implement.

## Limitations / unknowns
- Running in working tree without separate worktree isolation.
```

## Example 2: Case D (Multi-model + Decomposed)

```markdown
Readiness: READY
Scope: ticket-graph
Provider mode: tiered-multi-model
Task shape: decomposed
Execution status: executable
Apply mode: plan-only

Reason: Multi-model host with 4 formal tickets; Controller runs on model-gamma while ready tickets dispatch to fresh-context workers matched by tier.

## Host summary
- Current model: model-gamma (available)
- Selectable models / tiers: model-alpha (routine), model-beta (standard), model-gamma (high, review)
- Reasoning control: available (low, medium, high)
- Context & execution: subagents available, fresh context windows available, concurrency cap 3
- Adapter: codex (plan-only)

## Task assessment
- Task shape: decomposed
- Assessment rationale: Four isolated tickets with explicit blocking edges across schema, endpoint, auth policy, and cutover.
- Work-item difficulty: routine to critical

## Execution config

### Work-item routing

| Ticket | Difficulty | Model / tier | Effort | Context | Dependencies | Review |
|---|---|---|---|---|---|---|
| 01-schema-types | routine | model-alpha (routine) | low | fresh-worker-1 | None (Ready) | Controller Review |
| 02-api-endpoint | moderate | model-beta (standard) | medium | fresh-worker-2 | None (Ready) | Controller Review |
| 03-auth-policy | demanding | model-gamma (high) | high | fresh-worker-3 | None (Ready) | Independent Review |
| 04-audit-cutover | critical | model-gamma (high) | high | fresh-worker-4 | Blocked by 01, 02, 03 | Independent Review |

### Coordination
- Controller: model-gamma (high), effort: high, context: current-session
- Concurrency cap: 3 concurrent fresh-context workers (tickets 01, 02, 03 run in parallel worktrees)
- Frontier: 01, 02, 03 ready; 04 scheduled after merge
- Integration: Execute graph via /implement-spec; Controller integrates worker branches and runs acceptance before closing milestone

## Review strategy
- Review type: Controller Review per slice plus fresh-context Independent Review via acceptance
- Review model & effort: model-gamma (review), effort: high, context: fresh context window
- Review handoff: acceptance (Charter scale for full spec sign-off)

## Limitations / unknowns
- Ticket 04 waits on clean integration of 01, 02, and 03.
```

## Example 3: Case A (Single-model + Single-pass)

```markdown
Readiness: READY
Scope: current-item
Provider mode: fixed-single-model
Task shape: single-pass
Execution status: executable
Apply mode: plan-only

Reason: Single-model host on bounded config refactor; execute directly in current session at highest-supported effort (high).

## Host summary
- Current model: model-alpha (available)
- Selectable models / tiers: fixed single model
- Reasoning control: available (low, high)
- Context & execution: subagents unavailable, concurrency cap 1
- Adapter: none (plan-only)

## Task assessment
- Task shape: single-pass
- Assessment rationale: Single-module constant extraction with direct unit test check.
- Work-item difficulty: routine

## Execution config

| Phase | Model / tier | Effort | Context | Purpose |
|---|---|---|---|---|
| Implementation | model-alpha | high | current-session | Direct single-pass implementation via /implement |

## Review strategy
- Review type: Self-check (or fresh-context reviewer if subagents become available)
- Review model & effort: model-alpha, effort: high
- Review handoff: Verify tests and run acceptance when closing work

## Limitations / unknowns
- Host does not expose subagent dispatch; review independence noted under limitations.
```

## Example 4: Case B (Single-model + Decomposed)

```markdown
Readiness: READY
Scope: ticket-graph
Provider mode: fixed-single-model
Task shape: decomposed
Execution status: executable
Apply mode: plan-only

Reason: Single-model host with subagent support and 3 formal tickets; Controller dispatches each ready ticket into a fresh context window using model-alpha.

## Host summary
- Current model: model-alpha (available)
- Selectable models / tiers: fixed single model
- Reasoning control: unavailable (host default)
- Context & execution: subagents available, fresh context windows available, concurrency cap 2
- Adapter: none (plan-only)

## Task assessment
- Task shape: decomposed
- Assessment rationale: Three decoupled storage, service, and CLI tickets with an explicit merge barrier on ticket 03.
- Work-item difficulty: moderate to demanding

## Execution config

### Work-item routing

| Ticket | Difficulty | Model / tier | Effort | Context | Dependencies | Review |
|---|---|---|---|---|---|---|
| 01-db-layer | moderate | model-alpha | default | fresh-worker-A | None (Ready) | Controller Review |
| 02-service-layer | moderate | model-alpha | default | fresh-worker-B | None (Ready) | Controller Review |
| 03-cli-entry | demanding | model-alpha | default | fresh-worker-C | Blocked by 01, 02 | Independent Review |

### Coordination
- Controller: model-alpha, context: current-session
- Concurrency cap: 2 concurrent fresh-context workers (01 and 02 run first)
- Frontier: 01 and 02 ready
- Integration: Coordinate via /implement-spec; run acceptance before closing

## Review strategy
- Review type: Controller Review per ticket plus fresh-context acceptance sign-off
- Review model & effort: model-alpha, context: fresh context window
- Review handoff: acceptance

## Limitations / unknowns
- Single model used across Controller and workers; no separate model tiering on this host.
```
