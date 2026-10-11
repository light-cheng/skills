# Formats

## Normalized result

Every judgment returns these fields, whichever source answered:

```yaml
question_id: light-implement/offer-agent-config
question: Does this ticket need a stronger model setup before work starts?
kind: yes_no
options: [yes, no]
answer: yes
score: null
probabilities: {yes: 0.83, no: 0.17}
confidence: 0.83
provider_confidence: 0.66
method: typed-decision
data: on-device
backend: local-decider
calibrated: false
applied: false
fallback_reason: uncalibrated
final: no
```

- `answer` is the source's answer. `final` is what the caller acts on.
- For `kind: score`, the [Score](#score) rules replace the `answer`, `options`
  and `confidence` rules here.
- `applied` is true when `final` was taken from `answer` by policy: a
  calibrated typed decision that met its threshold, or a self-judgment. It is
  false when a typed answer was recorded but not used.
- `confidence` is computed here from `probabilities`: the probability of
  `answer`. For `yes_no` that is `max(p_yes, 1 - p_yes)`.
- `provider_confidence` is the backend's own value, kept as reported. Backends
  define it differently, so policy never reads it.

### Score

For `kind: score`, the caller supplies the ordered levels and the bins that
group them (for example `0–0.5 routine, 0.5–1.5 standard, 1.5–3 high`).
`options` lists the bins. `probabilities` is keyed by level. Each bin includes
its lower bound, so a `score` of exactly 0.5 falls in `standard` here.

- `score` is the expected value `sum(level_index * probability)`.
- `answer` is the bin that contains `score`. Never use the most probable
  level instead.
- `confidence` is the total probability of the levels inside that bin.

Without bins, each level is its own bin and `answer` is the level nearest to
`score`. Every other kind sets `score: null`.

### Self-judgment and fallback

Self-judgment sets `probabilities: {}`, `confidence: null`,
`provider_confidence: null`, `method: self-judgment`, `data: in-session`,
`backend: agent`, `calibrated: false`, `applied: true`, and `answer` equals
`final`.

`fallback_reason` says why the final answer did not come from a calibrated
typed decision:

| Value | When |
|---|---|
| `none` | A calibrated typed decision met its threshold; or self-judgment was asked for by the user or caller within the limit; or only one option was legal |
| `off` | The data limit is `off` or unrecognized |
| `unavailable` | No source within the limit had evidence of availability, or the chosen source returned an error |
| `timeout` | The chosen source did not answer in time |
| `malformed` | The chosen source returned something that does not fit the options |
| `low-confidence` | A calibrated source answered below its threshold |
| `uncalibrated` | The chosen source has no calibration for this question id |

### One legal option

Return the option as a self-judgment with `options` holding that one value and
`fallback_reason: none`. Ask no source. Log the row like any other judgment.

## Decision log

Write to `.scratch/<feature>/decisions.md`. Take `<feature>` from the caller.
When the caller gives none, use the only directory under `.scratch/` if there
is exactly one. Otherwise return the row to the caller instead of writing it.
Never create `.scratch/` or a feature directory for the log.

The log is a Markdown table. Write the header once, then append one row per
judgment. Never rewrite a row.

```markdown
| time | question_id | question | kind | answer | confidence | method | data | backend | applied | reason | final |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-10T08:15:00Z | light-implement/offer-agent-config | Does this ticket need a stronger model setup before work starts? | yes_no | yes | 0.83 | typed-decision | on-device | local-decider | false | uncalibrated | no |
```

- `time` is the current UTC time in ISO 8601, read from the system clock (for
  example `date -u +%Y-%m-%dT%H:%M:%SZ`). Never estimate it.
- Write `-` for an empty value. Escape a `|` inside a cell as `\|`.
- Keep the question in plain words. It is shown to the user as written.

## Policy file

Thresholds belong to the user's machine, not to a project:
`~/.config/light/decision-policy.json`. `light-decide` reads it and never
writes it.

```json
{
  "version": 1,
  "backends": {
    "local-decider": {
      "names": ["local-decider", "decider-mcp"],
      "data": "on-device",
      "questions": {
        "ask-light/material-ambiguity": {
          "min_confidence": 0.65,
          "calibration": "labeled comparison, 2026-10-10, 22 cases"
        }
      }
    }
  }
}
```

- The key is the backend name the user chose. `names` lists every name the
  Host reports for the same backend on either call path, so an MCP call and a
  script call find the same entry.
- A source is calibrated for a question id when its entry has both
  `min_confidence` and a non-empty `calibration`.
- A missing or unreadable file means every source is uncalibrated.
- `data` records this backend's destination. When evidence from the run
  differs, the farther of the two counts.
