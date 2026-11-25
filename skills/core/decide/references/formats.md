# Normalized Formats, Calibration Policy, and Decision Log

## `light-decision-mcp` normalized wire envelope

Every `light-decision-mcp` backend (Magpie gateway, OpenDecider, Google Gemini Decisions, TypeSafe Jev, Perplexity Decisions, OpenAI Decisions, and custom gateways), including mid-flight local fallbacks, normalizes responses to a single schema:

```json
{
  "backend": "magpie",
  "model": "google/gemini-decision-1",
  "data_destination": "third-party",
  "fallback_used": false,
  "level": 2,
  "label": "high",
  "expected_level": 1.85,
  "score": 1.85,
  "probabilities": { "low": 0.02, "medium": 0.11, "high": 0.87 },
  "confidence": 0.87,
  "provider_confidence": 0.91,
  "latency_ms": 182.4,
  "usage": { "input_tokens": 42, "output_tokens": 0, "total_tokens": 42 }
}
```

Per-tool answer fields inside the envelope:

- **`yes_no` (`noul`)**: `answer` (`"yes" | "no"`), `probability_yes`, `probabilities` (`{ "yes": p, "no": 1 - p }`), `confidence` (`max(p_yes, 1 - p_yes)`), `provider_confidence`.
- **`choose` (`choice`)**: `choice` (winning option key), `probabilities` (`{ [option]: p }`), `confidence` (`probabilities[choice]`), `provider_confidence`.
- **`score`**:
  - `level`: integer `0..N-1` (`argmax` index over ordered `levels`, lowest first).
  - `label`: `levels[level]` label string.
  - `expected_level` and `score`: identical probability-weighted expected floats `sum(i * p_i)` over `i = 0..N-1`.
  - `probabilities`: complete map keyed by level label (`{ [levels[i]]: p_i }`).
  - `confidence`: `probabilities[label]` (deterministic, rounded to 4 decimals); `provider_confidence` retains the upstream model's raw confidence (`null` when omitted) and is never used for policy thresholds.
- **`decide`**: returns `{ backend, model, data_destination, fallback_used, fallback_info?, answers: { [question_id]: <answerFields> }, latency_ms, usage?, warnings? }`.
- **`decide_batch`**: returns `{ backend, model, data_destination, fallback_used, fallback_count, results: [{ index, answers, backend, model, data_destination, fallback_used, fallback_info?, error? }], latency_ms }`.

Before trusting any typed answer, verify distribution sanity: every probability is finite in `[0, 1]`, `probabilities` keys match the requested options or levels, probabilities sum to `1.0` within `0.05`, and for `score` `abs(score - sum(i * p_i)) <= 0.01`. Treat any violation as `fallback_reason: malformed`.

## Policy-gated `decide` caller result

`decide` combines the `light-decision-mcp` answer envelope with calibration gating and returns a structured result per question:

```yaml
question_id: agent-config/task-complexity
question: How complex is this engineering task across scope, coupling, and verification risk?
kind: score
options: [routine, standard, high, critical]
level: 2
label: high
expected_level: 1.85
score: 1.85
answer: high
probabilities: {routine: 0.02, standard: 0.11, high: 0.87, critical: 0.0}
confidence: 0.87
provider_confidence: 0.91
method: typed-decision
data_destination: on-device
backend: local-opendecider
model: opendecider-small
fallback_used: false
calibrated: true
min_confidence: 0.65
applied: true
fallback_reason: none
final: high
```

### Field rules by question kind

- **`answer` vs `final`**: `answer` is the source's raw decision (`"yes" | "no"`, `choice`, or `score` label/bin). `final` is the policy-gated decision the caller acts on (`answer` when `applied: true`, or agent self-judgment when `applied: false`).
- **`yes_no` and `choice`**: set `level: null`, `label: null`, `expected_level: null`, and `score: null`.
- **`score` without caller bins**: `options` equals the ordered `levels`, `answer` defaults to `label` (while preserving exact `level`, `expected_level`, `score`, and `probabilities` so downstream callers such as `agent-config` can evaluate continuous expected values and `DOWNGRADE_MARGIN = 0.15`), and `confidence` is `probabilities[label]`.
- **`score` with caller-supplied bins**: when a caller defines half-open `[lower, upper)` intervals over `score` (`expected_level`), `options` lists the bin names, `answer` is the bin containing `score` (lower-bound inclusive, never the argmax `label` if they differ), and `confidence` is the sum of `probabilities` for all levels belonging to that bin.
- **Self-judgment and single-option short-circuit**: sets `method: self-judgment`, `data_destination: in-session`, `backend: agent`, `model: null`, `fallback_used: false`, `level: null`, `label: null`, `expected_level: null`, `score: null`, `probabilities: {}`, `confidence: null`, `provider_confidence: null`, `calibrated: false`, `min_confidence: null`, `applied: true`, and `answer` equal to `final`.

### Canonical question IDs across `light` skills

- `redirect/is-direction-change` (`yes_no`): borderline scope shift vs routine implementation fix in `redirect`.
- `agent-config/task-complexity` (`score`, levels `["routine", "standard", "high", "critical"]`): abstract task tier input in `agent-config`.
- `agent-config/reasoning-need` (`score`, levels `["low", "medium", "high"]`): effort policy input in `agent-config`.
- `manuscript-ops/route` (`choice`): `needs-v2` stage routing in `manuscript-ops`.

### `fallback_reason` values

| Value | When |
|---|---|
| `none` | A calibrated typed decision met `min_confidence`; only one option was legal; or the caller/user explicitly requested self-judgment |
| `off` | `Decision data` in `docs/agents/light-project.md` is `off` or unrecognized |
| `unavailable` | `light-decision-mcp` is absent, no backend is ready within `max_data_destination`, `data_boundary_exceeded`, circuit open without fallback, or upstream error |
| `images-unsupported` | Request carries `images`, and either no multimodal backend fits within `max_data_destination` or fallback refused silent image drop (`images_unsupported`) |
| `timeout` | The backend timed out without a fallback response |
| `malformed` | Response failed probability, option-key, or expected-score validation |
| `uncalibrated` | Answering backend/model lacks a calibration entry for `question_id` in `~/.config/light/decision-policy.json` |
| `low-confidence` | Answering backend/model is calibrated for `question_id`, but `confidence < min_confidence` |

## Calibration policy (`~/.config/light/decision-policy.json`)

Calibration thresholds are machine-local and live at `~/.config/light/decision-policy.json` (never inside a project repository). `decide` reads this file on every typed judgment and writes to it only with explicit user approval during setup or calibration.

```json
{
  "version": 1,
  "backends": {
    "local-opendecider": {
      "names": ["local-opendecider", "opendecider-small"],
      "data": "on-device",
      "questions": {
        "redirect/is-direction-change": {
          "min_confidence": 0.70,
          "calibration": "labeled comparison, 2026-11-25, 24 cases"
        },
        "agent-config/task-complexity": {
          "min_confidence": 0.65,
          "calibration": "labeled comparison, 2026-11-25, 30 cases"
        }
      }
    }
  }
}
```

- **Matching**: Match the actual answering `response.backend` or `response.model` against each entry's key or `names` list. When `response.fallback_used` is `true`, match strictly against the fallback backend/model that produced the answer, never `fallback_info.primary_backend`.
- **Calibrated criterion**: An entry is calibrated for `question_id` only when `questions[question_id].min_confidence` is a finite number in `[0, 1]` and `questions[question_id].calibration` is a non-empty string.
- **Missing or unreadable file**: Every backend is treated as uncalibrated (`calibrated: false`, `applied: false`, `fallback_reason: uncalibrated`).
- **Destination floor**: If `data` in the policy entry and `response.data_destination` differ, enforce the farther (less private) destination against `Decision data`. If that exceeds the project ceiling, reject the typed answer with `fallback_reason: unavailable`.
- **Refusal marker**: Top-level `"setup": "declined"` means the user declined decision setup on this machine; never re-offer setup while set.

### Running calibration (only when requested by the user)

1. **Curate labeled cases**: Gather candidate judgments from `.scratch/**/decisions.md` (rows where `answer` and `final` diverged are high-signal candidates, paired with settled cases). Have the user assign ground-truth labels before re-running any backend.
2. **Measure on held-out split**: Evaluate candidate backends with `decide_batch`, keeping threshold-selection cases separate from held-out verification cases. If dispatching a helper subagent to evaluate batches, start it with a **fresh context window**. Write `min_confidence` and `calibration` notes into `~/.config/light/decision-policy.json` only after user approval, and never rewrite historical rows in `decisions.md`.

## Decision log under `.scratch/`

Resolve the log path without ever polluting the repository root:

1. `.scratch/<feature>/decisions.md` when the caller supplies `<feature>` or `.scratch/` contains a single active feature directory.
2. `.scratch/decisions.md` when no `<feature>` directory is active.
3. Return the formatted row to the caller instead of writing only if the workspace is read-only. Never write `decisions.md` to the repository root.

Write the Markdown table header once when creating the file, then append one row per judgment (never rewrite or backfill prior rows):

```markdown
| time | question_id | question | kind | answer | score | confidence | method | data_destination | backend | model | fallback_used | applied | reason | final |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-25T05:51:00Z | redirect/is-direction-change | Does this API mismatch invalidate the approved ticket contract? | yes_no | yes | - | 0.88 | typed-decision | on-device | local-opendecider | opendecider-small | false | false | uncalibrated | yes |
```

- `time`: Current UTC timestamp in ISO 8601 read from the system clock (such as `date -u +%Y-%m-%dT%H:%M:%SZ`), never estimated.
- Formatting: Write `-` for `null` or empty values, escape `|` inside any cell as `\|`, keep `question` in plain human-readable words, and never log credentials, endpoints with tokens, or raw source diffs. For multi-question `decide` or `decide_batch` calls, append one row per question (indexing batch states as `<question_id>#<index>` when logging batch runs).
