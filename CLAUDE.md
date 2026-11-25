# Light Skills

Orthogonal agent skill plugins at `https://github.com/light-cheng/skills`, built to run standalone (with graceful fallback) or alongside `mattpocock/skills` with zero skill collisions.

## Layout

Skills live in two promoted plugin buckets:

- `skills/core/<name>/`: the 8 skills shipped by the root plugin `light` (`.claude-plugin/plugin.json`): `light-setup`, `redirect`, `acceptance`, `agent-config`, `decide`, `humanizer`, `kb-init`, `learn-anything`.
- `plugins/light-manuscript/skills/manuscript-ops/`: shipped separately as the optional plugin `light-manuscript` (`plugins/light-manuscript/.claude-plugin/plugin.json`) and registered in `.claude-plugin/marketplace.json`.
- `.claude/skills/`: private maintainer-only skills for this repository (never listed in public plugin manifests).

Public documentation at the repository root consists strictly of `README.md`, `README.zh-CN.md`, and `LICENSE` (MIT). Do not add separate `CATALOG.md` or governance policy matrices.

## Authoring invariants

- Every `SKILL.md` is either **user-invoked** (`disable-model-invocation: true` in frontmatter plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`, with `argument-hint` where arguments apply) or **model-invoked** (default). Keep both metadata files in sync.
- Plugin manifests ship skills only (no auto-spawned `mcpServers` entries in `plugin.json`); `decide` and `agent-config` bind dynamically to `light-decision-mcp` and `agent-config` MCP when present and degrade gracefully when absent.
- Every skill that dispatches a subagent instructs starting it with a **fresh context window**, not a fork of the current conversation.
- Cross-collection references (`code-review`, `research`, `writing-for-agents`, `wizard`) always include a **graceful fallback** so every skill works both with and without `mattpocock/skills` installed.
- Durable artifacts written into target user repositories (`decisions.md`, `changes/`, `acceptance/`) live under `.scratch/` so they never pollute a target repository's root working tree.
- Preserve required third-party notices (`ATTRIBUTION.md` / `LICENSE`) in packages with upstream lineage (`humanizer`).
- No prose or SHA-256 byte locks in tests. Automated checks test only strict YAML frontmatter parsing, `claude plugin validate`, internal links, and deterministic runtime scripts (`agent-config`, `manuscript-ops`).
- No em-dashes in newly authored English prose; rewrite with colons, commas, parentheses, or conjunctions.

## Agent skills

### Issue tracker

Issues and specs are tracked as local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical five triage roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`GLOSSARY.md` and `docs/adr/` at the repo root). See `docs/agents/domain.md`.
