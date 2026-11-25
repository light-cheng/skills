# 0001. Rebuild `light-cheng/skills` as an Orthogonal Companion Plugin Over `mattpocock/skills`

Date: 2026-11-25
Status: Accepted

## Context

The legacy `light-cheng/skills` repository (archived locally at `../light-skills`, to be archived remotely as private `light-cheng/light-skills`) grew to 39 packages by combining 12 ported `mattpocock/skills` packages, 8 adapted workflow clones, vertical applications (`light-travelpage`, `kanban-worker`), fragmented review packages (`generic-review`, `review-loop`, `project-review`, `light-code-review`), and genuine originals. That middle ground created four problems:

1. Co-installing `mattpocock/skills` for missing capabilities (`implement-spec`, `codebase-design`, `domain-modeling`, `pr`) caused 8 pairs of duplicate model-invoked skills to load simultaneously and compete in the context window.
2. Ported packages pinned to an older revision drifted behind upstream bug fixes while early git history created poor open-source optics.
3. Heavy application assets (`light-travelpage`, 80 files), collection-internal release bureaucracy (`release-workflow`, 682 evidence files, SHA-256 prose locks), and >20 mirrored governance markdown files inflated installation size and maintenance cost.
4. Several small skills (`recap`, `eli5`, `language-learning`, `light-merge-conflicts`) had been overtaken by native frontier-model capabilities or built-in harness commands, while splitting review convergence (`review-loop`) from final sign-off (`project-review`) created naming ambiguity alongside upstream `code-review`.

## Decision

1. Start a clean `v1.0.0` Git history for `https://github.com/light-cheng/skills` with **zero copied `mattpocock/skills` files**. Delegate general software engineering flows directly to `mattpocock/skills` as the **Base workflow**.
2. Ship two pure-skills `.claude-plugin` bundles from `.claude-plugin/marketplace.json` (no auto-started `mcpServers` entries in `plugin.json`; supporting Claude Code, Codex 0.161+, and GitHub Copilot auto-updates alongside `npx skills add`):
   - **`light` (Core plugin, 8 skills under `skills/core/`)**: `light-setup`, `redirect`, `acceptance`, `agent-config`, `decide`, `humanizer`, `kb-init`, `learn-anything`.
   - **`light-manuscript` (Optional plugin, 1 skill at `plugins/light-manuscript/skills/manuscript-ops/`)**: `manuscript-ops` (placed inside the sub-plugin folder so `claude plugin validate` passes containment checks).
3. Merge `generic-review`, `review-loop`, and `project-review` into a single deep module named **`acceptance`** (zero naming collision or confusion with upstream `code-review`): inline 3-round convergence for routine slices, and frozen-charter independent-Evaluator sign-off under `.scratch/<feature>/acceptance/` for full specs, milestones, and manuscripts.
4. Drop the `light-` name prefix everywhere except `light-setup` (`redirect`, `decide`). Retire `light-html-plan` and `project-retro`.
5. Align `decide` and `agent-config` dynamically with `Light-Decision-MCP` (`decide`, `choose`, `yes_no`, `score`, `decide_batch`, `status`, plus `light-decision-mcp setup` / `ui`) and `agent-config` MCP, removing legacy `typesafe_sdk` imports and duplicated `decision_source.py`.
6. Keep all target-repo runtime records (`decisions.md`, `changes/`, `acceptance/`) inside `.scratch/` so target repo roots stay clean.
7. Keep root public documentation minimal: `README.md`, `README.zh-CN.md`, and `LICENSE` (MIT) only.
8. Move `kanban-worker` back to `light-kanban`, split `travelpage` into its own standalone repository, and guard this repo with three lightweight seams: strict YAML frontmatter + `claude plugin validate` + link checks, unit/negative tests on executable Python scripts (`agent-config`, `manuscript-ops`), and Changesets CI.

## Consequences

- Installing `mattpocock-skills` + `light` produces zero duplicate skills, zero `review` naming ambiguity (`code-review` vs `acceptance`), and ~77% fewer packages to maintain (39 down to 8 core + 1 optional).
- Users get seamless middleware hooks (`redirect`, `acceptance`, `agent-config`, `decide`) over Matt's `.scratch/` and GitHub Issues artifacts via a 3-line `CLAUDE.md` bridge written by `light-setup`.
- `manuscript-ops` drops its legacy hard-dependency check (`check_dependencies.py`) that previously required `clarify`, `socratic`, and `decision-map`, delegating milestone sign-off to `acceptance`.
- `humanizer` retains full MIT and CC BY-SA attribution (`ATTRIBUTION.md`) for `blader/humanizer`, `op7418/Humanizer-zh`, and Wikipedia.
