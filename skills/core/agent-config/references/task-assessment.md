# Task assessment and normalized `decide` intake

Task shape, difficulty, and reasoning need are semantic properties of the work. Never use word count or prompt length as a proxy for complexity.

## 1. Task shape (`single-pass` vs `decomposed`)

| Task shape | Meaning | Criteria |
|---|---|---|
| `single-pass` | Safely completed in one continuous session. | Single cohesive concern or bounded module; compact verification surface; state fits cleanly in one context window. |
| `decomposed` | Partitioned into dependency-ordered or parallel tickets. | Multiple independently verifiable slices; explicit cross-layer dependencies (schema -> service -> UI); risk of context degradation if attempted in one pass. |

**Anti-wordcount rule:** A short 300-word brief spanning schema migration, auth middleware, and API cutover is `decomposed`; a 3,000-word specification updating one parser table is `single-pass`.

## 2. Work-item difficulty and tier mapping

| Difficulty | Semantic criteria | Tier mapping | Effort guidance |
|---|---|---|---|
| `routine` | Mechanical edits, clear templates, local blast radius, trivial verification (typos, config keys, boilerplate tests). | `routine` | `lowest-supported` / low |
| `moderate` (`standard`) | Established patterns, bounded feature slice or bug fix, clear interfaces, standard unit/integration tests. | `standard` | medium / `default` |
| `demanding` (`high`) | Cross-module seams, concurrency or state-machine invariants, high ambiguity, non-trivial debugging. | `high` | high / `highest-supported` |
| `critical` | Security boundaries, irreversible migrations, core correctness invariants, high failure impact. | `high` | `highest-supported` |

**Monotonicity and cost invariants:**
- A higher-risk or harder ticket never receives a lower tier or lower resolved effort than an easier ticket on the same host.
- Cost sensitivity (`cost_sensitive: true`) is recorded for tie-breaking among equal candidates and never downgrades capability tier or reasoning need.

## 3. Normalized `decide` (`light-decision-mcp`) score intake

When `difficulty_source` is already authoritative (`explicit-user`, `verified-ticket`, `deterministic-policy`), code owns complexity; when `reasoning_policy` is explicit, code/policy owns reasoning. Only non-authoritative dimensions consult `decide`.

### Question contracts
- `agent-config/task-complexity` (`score`): ordered levels `["routine", "standard", "high", "critical"]`
  - Expected score bins: `[0.0, 0.5)` -> `routine` (`routine` tier), `[0.5, 1.5)` -> `standard` (`standard` tier), `[1.5, 2.5)` -> `high` (`high` tier), `[2.5, 3.0]` -> `critical` (`high` tier).
- `agent-config/reasoning-need` (`score`): ordered levels `["low", "medium", "high"]`
  - Expected score bins: `[0.0, 0.5)` -> `low`, `[0.5, 1.5)` -> `medium`, `[1.5, 2.0]` -> `high`.

Build a label-clean state (`task_title`, `task_description`, `cost_sensitive`, `latency_sensitive`) without leaking ground-truth difficulty labels or source diffs.

### Validation, calibration, and `DOWNGRADE_MARGIN`
`scripts/abstract_profiler.py` validates each normalized `light-decision-mcp` score payload (`probabilities` keyed by level label or `0..N-1` index, `score` / `expected_level`, `confidence`, `provider_confidence`, `backend`, `model`, `data_destination`):
1. **Data boundary:** Enforces `Decision data` from `docs/agents/light-project.md` (`on-device` default; `off` disables typed decisions).
2. **Distribution & expected value:** Requires finite probabilities in `[0, 1]` summing to `1.0` (`±0.01`) and `score` / `expected_level` matching `sum(i * p_i)` (`±0.02`). Invalid payloads fall back as `malformed`.
3. **Calibration gate:** Applies a score only when calibrated in `~/.config/light/decision-policy.json` (or explicit `calibration_thresholds`) and bin probability meets `min_confidence` (otherwise `uncalibrated` or `low-confidence`).
4. **Conservative downgrade margin (`DOWNGRADE_MARGIN = 0.15`):** Any downward shift below the deterministic baseline must also sit at least `0.15` below the upper edge of the lower bin (`(bin_idx + 0.5) - score >= 0.15`). Borderline downgrades are rejected in favor of `build_deterministic_profile`.
