# Profile schema (`profile_version: 1`)

A profile stores user-confirmed execution settings scoped to a specific `host_id` and `workspace`. It is persisted via companion `save_profile` or supplied in-session during `session-local` / `plan-only` operation.

## 1. Governance invariants

1. **User-confirmed bindings only:** Models and tiers are chosen explicitly by the user during setup ([setup.md](setup.md)), never inferred from marketing names or ranked automatically.
2. **Host and workspace isolation:** Settings confirmed for one `host.id` or `scope.workspace` never silently apply to another host or project.
3. **Fail-closed on drift:** If a bound model disappears from `available_models`, the profile is marked `stale` rather than silently substituting another model.

## 2. Canonical structure

```json
{
  "profile_version": 1,
  "host": {
    "id": "codex",
    "adapter": "codex"
  },
  "scope": {
    "type": "project",
    "workspace": "/path/to/project"
  },
  "model_mode": "multi",
  "tiers": {
    "routine": {
      "model": "model-alpha",
      "source": "user-confirmed",
      "effort": { "value": "low" }
    },
    "standard": {
      "model": "model-beta",
      "source": "user-confirmed",
      "effort": { "value": "medium" }
    },
    "high": {
      "model": "model-gamma",
      "source": "user-confirmed",
      "effort": { "policy": "highest-supported" }
    },
    "review": {
      "model": "model-gamma",
      "source": "user-confirmed",
      "effort": { "policy": "highest-supported" }
    }
  },
  "capabilities": {
    "subagents": "available",
    "threads": "available",
    "parallelism": "available",
    "concurrency": 3
  }
}
```

For `model_mode: "single"`, omit `tiers` and provide `single_model`:

```json
{
  "model_mode": "single",
  "single_model": {
    "model": "model-alpha",
    "execution_effort": { "policy": "highest-supported" },
    "review_effort": { "policy": "highest-supported" }
  }
}
```

## 3. Effort policy objects

Each effort field uses either an abstract policy (`{ "policy": "highest-supported" | "default" | "lowest-supported" }`) or an explicit host-supported value (`{ "value": "<host-discrete-string>" }`). Custom policy entries (`{ "policy": "custom", "value": "<host-discrete-string>" }`) must supply a non-empty value verified against `supported_effort_values`.

## 4. Stale profile conditions

A profile is flagged `stale: true` only when factual host state conflicts with the saved profile (configured model missing from `available_models`, `host.id` or `host.adapter` mismatch, or required capability regression). Elapsed wall-clock time alone never marks a profile stale.
