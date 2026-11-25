# Light Skills Glossary

Orthogonal agent skill plugins (`https://github.com/light-cheng/skills`) that extend coding and knowledge workflows without duplicating `mattpocock/skills`.

## Language

**Base workflow**:
The engineering and productivity skill set shipped by `mattpocock/skills` (`/setup-matt-pocock-skills`, `/grill-with-docs`, `/to-spec`, `/to-tickets`, `/implement`, `/implement-spec`, `/code-review`, `/pr`, `/retro`, `/wayfinder`). This repository never copies or forks a Base workflow skill.
_Avoid_: upstream ports, Matt baseline

**Core plugin (`light`)**:
The default pure-skills plugin defined in `.claude-plugin/plugin.json`, shipping 8 orthogonal skills under `skills/core/`: `light-setup`, `redirect`, `acceptance`, `agent-config`, `decide`, `humanizer`, `kb-init`, and `learn-anything`.
_Avoid_: first-party full collection

**Manuscript plugin (`light-manuscript`)**:
The optional pure-skills plugin defined under `plugins/light-manuscript/.claude-plugin/plugin.json` (with skill package at `plugins/light-manuscript/skills/manuscript-ops/`) and registered in `.claude-plugin/marketplace.json`, keeping book/publishing workflows out of the default coding context window.

**Graceful fallback**:
The rule that any skill referencing an external Base workflow capability (`code-review`, `research`, `writing-for-agents`, `wizard`) or companion MCP (`light-decision-mcp`, `agent-config`) uses it when available in the current session and falls back cleanly when absent.

**Change proposal**:
A durable markdown artifact under `.scratch/<feature>/changes/` (or tracker issue comment) produced by `redirect` when an approved spec, ticket graph, or acceptance charter no longer holds. Only human approval turns a Change proposal into spec or ticket edits.

**Bounded judgment**:
A closed-set question (`choice`, `yes_no`, or ordered `score`) evaluated by `decide` through `light-decision-mcp` (or self-judgment fallback) within the project's `Decision data` privacy boundary (`on-device` by default), logged to `.scratch/<feature>/decisions.md`.
_Avoid_: Jev query, semantic shadow mode

**Acceptance (`acceptance`)**:
The unified convergence and sign-off discipline that drives code or non-code deliverables through bounded review-and-repair rounds (up to 3 rounds, delegating code diffs to `code-review` when installed) and verifies real execution/render evidence before issuing `PASS`, `FAIL`, or `BLOCKED`. Runs inline in memory for routine slices, or freezes an **Acceptance charter** under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/`) with a fresh independent Evaluator for full specs and milestones.
_Avoid_: review-loop, project-review, generic-review
