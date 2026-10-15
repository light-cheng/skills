# Routing judgment

Read this during the judgment stage of the session flow in `SKILL.md`: before choosing a next Skill and when reading the evidence packet. These are guides for reasoning from actual contracts, not a lookup table.

## Decision principles

```text
No real project / fuzzy standalone idea            → clarify
Real initialized project, unresolved user decisions → project-clarify
Large / foggy / multi-session decision space        → decision-map
Missing external fact                               → light-research
Answer requires seeing runnable behavior/UI/state   → light-prototype
Information belongs to another person               → light-to-questionnaire
Already-clarified project material                  → project-spec
Active / approved SPEC ready for slicing            → project-tickets
Ready unblocked ticket                              → light-implement
Hard bug needing a reproducible loop                → light-diagnosing-bugs
Implementation/review acceptance needed             → project-review
Explicit release intent after accepted work         → release-workflow
```

Boundary reasoning that matters most:

- `project-init` records the project frame; it does not clarify
  requirements. Research establishes external/project facts; it does not
  settle user-owned product decisions. `project-spec` consumes
  already-clarified material. When goal and outputs are recorded but
  user-owned decisions are not shown as settled, `project-clarify` fits and
  `project-spec` is premature.
- Canonical project flow is `project-clarify → project-spec → project-tickets → light-implement → project-review`.
  With an active SPEC and no implementation tickets, the canonical next step is
  `project-tickets` to break the specification into dependency-ordered tracer-bullet tickets.
  Do not insert `project-review` before `project-tickets` merely because a SPEC exists.
- Ticket frontier: at least one ready unblocked ticket is a strong
  current-workflow fact for `light-implement`. Unresolved tickets with **zero**
  ready frontier items must not be presented as implementable work.
- An accepted current effort is a terminal fact **for that effort** — answer
  “current effort is complete; no mandatory next workflow step” for a
  current-workflow question, but route a new-work request by its own
  maturity instead of returning a global terminal state.
- An uninitialized repository recommends `project-init` for current-workflow
  questions but never blocks a standalone request (ELI5 routes to `eli5`).
- An active review owns the current workflow round (`project-review`); a
  word like “spec” inside the user's sentence does not turn it into
  `project-spec`. The reverse also holds: an explicit independent request
  (“先不管当前主流程，我只想单独 review 这个 diff”) routes to `light-code-review`
  even while a project review is active — mention the active review, do not
  hijack the request.
- `light-implement` vs `agent-config`: `light-implement` is the bounded executor;
  `agent-config` is an optional execution-planning enhancement. When the
  current project has a ready implementation item, current-workflow next
  routes to `light-implement` (even for complex tasks; `light-implement` decides whether
  to offer `agent-config` and the user decides whether to accept). Route
  directly to `agent-config` only when execution configuration or setup intent
  itself is the user's explicit goal:
  - setup intent: `agent-config setup`, "配置当前 Harness 模型", "配置模型档位", "重新配置 Agent Config";
  - execution queries: "这个任务用哪个模型", "这些工单怎么分 Agent", "这个 Harness 怎么跑这批 tickets", "哪个模型执行/给多少 effort", "execution topology / model tier routing".
  Ready unblocked tickets strictly route to `light-implement`; breaking an active SPEC into tickets strictly routes to `project-tickets`.
  `light-implement` remains valid even when `agent-config`, model selectors, or
  multi-agent capabilities are unavailable or declined.

## Reading the evidence

- **Hard evidence overrides imagination.** Never claim a SPEC when
  `spec.exists` is false. Never claim acceptance when review freshness is
  stale or unknown. Never claim execution for an unavailable Skill.
- **Hard constraints are scoped.** `hardConstraints[]` carry
  `appliesTo: current-workflow`, an `ownerSkill` where the workflow
  has a deterministic owner (uninitialized → `project-init`, active review /
  stale review / unknown review state → `project-review`), and `blocking`.
  They constrain current-workflow recommendations only; they never block an
  explicit independent task, a new effort, or a standalone request.
- **The conversation is first-class evidence.** The filesystem is not the
  entire world: a clarification handoff completed earlier in this
  conversation, a research result just produced, or a rejected direction are
  all evidence. Deterministic inspection supplements this context; it does
  not erase it.
- **Clarification readiness is content-validated.** Persisted handoffs count
  only when their content matches the `project-clarify` contract
  (`Status: ready-for-next-stage` + `Recommended next explicit invocation:`);
  a filename containing “clarif” proves nothing. Because `project-clarify`
  returns its handoff in conversation by default, absence of a persisted
  record means readiness cannot be proven from files — not that clarification
  never happened. If the user states clarification happened but no usable
  handoff exists, report that gap instead of inventing readiness.
- **Research artifacts are candidates.** `docs/research/*` paths prove
  existence only — not relevance or completeness. Read a relevant research
  document when it materially affects the recommendation.
- **Review state is visible at every stage.** The packet exposes the durable
  review transaction (ownership, status, verdict, freshness) before tickets
  exist; use the producer-owned review contract to determine what it applies
  to.

## Scopes for validation

- `current-workflow`: the user asks what to do next in this project. Hard
  constraints bind.
- `independent`: an explicit task, a named Skill, or a new effort.
- `standalone`: a request that needs no project workflow.

A `RECOMMEND` result always carries a real Skill unless the project is
legitimately terminal.

## Explaining the recommendation

For current-project questions, answer from the observed facts:

- what the project appears to be doing;
- where the current effort is;
- what is already finished;
- what is actually unresolved;
- why the recommended Skill fits **now**;
- why the most obvious neighboring Skill is premature or unnecessary.

Never give "Light Skill Map matched pattern …" as the user-facing reason.
