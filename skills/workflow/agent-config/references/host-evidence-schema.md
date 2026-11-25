# Host evidence schema and script entry

Supply a fresh, structured host observation (as returned by companion `inspect_host`, conforming to `host-capabilities.schema.json`) rather than a remembered model list. Observations older than 24 hours are rejected as stale.

## 1. Canonical `HostCapabilities` snapshot

```json
{
  "host_id": "codex",
  "adapter_id": "codex",
  "workspace": "/path/to/project",
  "observed_at": "2026-11-25T00:00:00Z",
  "platform": "darwin-arm64",
  "available_models": [
    {
      "id": "model-alpha",
      "label": "Model Alpha",
      "state": "available",
      "features": ["tools", "reasoning"],
      "evidence": {
        "kind": "host-runtime",
        "locator": "host runtime model registry",
        "observed_at": "2026-11-25T00:00:00Z"
      }
    }
  ],
  "supported_effort_values": ["low", "medium", "high"],
  "default_effort_value": "medium",
  "capabilities": {
    "model_selection": {
      "state": "available",
      "scopes": ["current-session", "new-session", "per-agent"],
      "evidence": { "kind": "host-runtime", "locator": "cli --model and subagent config" }
    },
    "subagents": {
      "state": "available",
      "evidence": { "kind": "host-runtime", "locator": "subagent runner" }
    },
    "threads": {
      "state": "available",
      "evidence": { "kind": "host-runtime", "locator": "fresh context window dispatch" }
    },
    "parallelism": {
      "state": "available",
      "evidence": { "kind": "host-runtime", "locator": "concurrent worker pool" }
    },
    "concurrency": {
      "state": "available",
      "max_concurrency": 3,
      "evidence": { "kind": "host-runtime", "locator": "host pool limit" }
    },
    "reasoning": {
      "state": "available",
      "evidence": { "kind": "host-runtime", "locator": "effort parameter" }
    },
    "per_agent_model_selection": {
      "state": "available",
      "evidence": { "kind": "host-runtime", "locator": "per-subagent model parameter" }
    },
    "configuration_mutation": {
      "state": "available",
      "supports_native_files": true,
      "supports_session_mutation": false,
      "evidence": { "kind": "host-config", "locator": ".codex/config.toml" }
    }
  }
}
```

## 2. Evidence rules

- `state` is strictly `"available"`, `"unavailable"`, or `"unknown"`.
- Verified `evidence.kind` values are `"host-runtime"`, `"host-config"`, `"host-schema"`, `"adapter-probe"`, and `"user-confirmed"`. Synthetic placeholder kinds (such as `fallback-default`) and intelligence ranking fields (such as `routing_rank`) are invalid.
- `supported_effort_values` lists the ordered discrete effort strings accepted by the host runtime, paired with `capabilities.reasoning.state === "available"`.

## Script entry

`scripts/agent_config.py` validates canonical Host and Profile evidence and optionally consumes normalized `decide` (`light-decision-mcp`) score envelopes:

```bash
python3 skills/workflow/agent-config/scripts/agent_config.py \
  --host-json '<HostCapabilities JSON>' \
  --profile-json '<Profile JSON>' \
  --task-json '{"shape":"decomposed","formal_tickets_exist":true,"difficulty":"standard","difficulty_source":"unknown"}' \
  --decide-scores-file /path/to/decide-scores.json \
  --decision-policy-file ~/.config/light/decision-policy.json \
  --project-root /path/to/project
```

Key flags (shared with standalone `scripts/abstract_profiler.py` for task-only profiling):
- `--host-json`, `--profile-json`, `--task-json`: Canonical JSON inputs; missing, stale, or mismatched evidence returns `readiness: "NEED_INPUT"`.
- `--active-session-json`: Optional fresh (within 5 minutes) runtime evidence identifying the active session model when a `single` profile runs on a host with `model_selection.state === "available"`.
- `--decide-scores-json` / `--decide-scores-file`: Normalized `light-decision-mcp` `score` or multi-question `decide` payload (`answers` or direct map for `agent-config/task-complexity` and `agent-config/reasoning-need`).
- `--decision-policy-json` / `--decision-policy-file` / `--calibration-thresholds-json`: Per-question `min_confidence` calibration rules.
- `--project-root` / `--max-data-destination`: Enforces the project's `Decision data` boundary (`on-device` | `private-network` | `third-party` | `off`).
- `--no-typed-decisions`: Forces `build_deterministic_profile` without consulting `decide` scores.
- `--approval` (`unknown` | `approved` | `declined`) or `--no-preview-approval`: Tracks user preview consent.
