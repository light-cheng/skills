# Companion MCP contract

This reference specifies the optional `agent-config` companion MCP protocol (`protocol_version: 1`) maintained in `light-cheng/agent-config`, along with the session-local `plan-only` **Graceful fallback** when the companion is absent.

## 1. Protocol versioning and health semantics

The `agent-config` skill and companion MCP server share a versioned boundary:

- `protocol_version: 1`: Companion MCP tool contract version.
- `profile_version: 1`: User-confirmed profile schema version.
- `adapter_id`: Host adapter identifier (one of the 10 native adapters in [harness-support.md](harness-support.md) or `generic`).
- `host_id`: Identifier of the active agent host environment.

A companion instance counts as `ready` / `healthy` only when all three checks hold:
1. **Protocol match:** Compatible MCP transport handshake and exact contract match (`protocol_version === 1`).
2. **Complete 8-tool surface:** All eight canonical tools (`get_setup_status`, `inspect_host`, `get_profile`, `save_profile`, `preview_configuration`, `apply_configuration`, `validate_configuration`, `reset_profile`) are exposed with matching request and response schemas.
3. **Live reachability:** The server responds to live tool calls without timeout or transport error (`registration != reachability != health`).

Missing tools, schema drift, or version mismatch classify the companion as `stale` or `unsupported`, never `ready`.

## 2. Standard MCP tool surface (8 tools)

### `get_setup_status`
Returns whether the active host and workspace have a valid, non-stale user-confirmed profile.
- **Inputs:** optional `scope` (`"project"` default or `"global"`), `workspace`, `host_id`.
- **Output:** `{ configured, protocol_version: 1, profile_version: 1, host_id, adapter_id, scope, stale, stale_reasons, companion_registered, companion_status }`.

### `inspect_host`
Queries the active Host Adapter for factual model availability, `supported_effort_values`, and execution capabilities ([host-evidence-schema.md](host-evidence-schema.md)).
- **Inputs:** optional `workspace`, `host_id`.
- **Rule:** Reports factual presence and discrete options only; never emits intelligence rankings or `routing_rank`.

### `get_profile`
Reads the stored user-confirmed profile for the active host and workspace scope.
- **Inputs:** optional `scope` (`"project"` | `"global"`), `workspace`, `host_id`.
- **Output:** Profile object matching [profile-schema.md](profile-schema.md), or `null` when unconfigured.

### `save_profile`
Validates a user-confirmed profile against `profile_version: 1` and current host inventory, then persists it atomically.
- **Inputs:** required `profile`, optional `workspace`.
- **Rule:** Rejects unavailable model IDs, unsupported effort values, or host mismatches without partial writes.

### `preview_configuration`
Generates a deterministic `FrozenMutationPreview` before any host configuration file or runtime setting is modified.
- **Inputs:** required `config` (`ExecutionConfig`), optional `workspace`, `host_id`.
- **Output:** `{ preview_id, preview_hash, adapter_id, host_identity, scope, target, baseline_hash, mutation: { diff, patch, files }, created_at, expires_at }`.
- **Rule:** Freezes target paths, scope, baseline hash, and diff at preview time.

### `apply_configuration`
Applies a previously generated and user-approved preview via the Host Adapter.
- **Inputs:** required `preview_id`, optional `workspace`.
- **Rule:** Verifies `preview_id` is unexpired, unapplied, and matches the on-disk `baseline_hash`. Aborts fail-closed (`STALE_PREVIEW`) on any baseline drift.

### `validate_configuration`
Reads back real host state on disk or in runtime and compares it against a canonical `expected_config` or workspace/host-bound `preview_id`.
- **Inputs:** `expected_config` and/or `preview_id`, optional `workspace`, `host_id`.
- **Output:** `{ valid, workspace, message, details? }`.

### `reset_profile`
Clears stored profile configuration for the active host and workspace scope.
- **Inputs:** optional `scope` (`"project"` | `"global"`), `workspace`, `host_id`.
- **Output:** `{ success: true, cleared: true, reset: true, host_id, scope }`.

## 3. Preview-before-apply mutation gate

Host mutations follow a strict five-step sequence:

```text
inspect_host / get_profile
  -> preview_configuration (produces FrozenMutationPreview + diff)
  -> explicit user approval of preview
  -> apply_configuration (verifies baseline_hash + expiry)
  -> validate_configuration (verifies post-apply host state)
```

Never call `apply_configuration` without an approved `preview_id`, and always run `validate_configuration` after apply.

## 4. Graceful fallback when companion is absent

Plugin manifests in `light-cheng/skills` ship skills only and never auto-spawn MCP servers. When `agent-config` runs without a reachable companion MCP:

1. Check live tool availability rather than assuming static config files mean a server is running.
2. Do not run `npm install`, start background daemons, or edit host files silently.
3. Offer two clear choices:
   - Run `agent-config setup` ([setup.md](setup.md)) to preview and register the companion MCP.
   - Continue immediately in session-local `plan-only` mode.
4. In session-local `plan-only` mode, ask the user to confirm single-model vs multi-model tier mapping and effort preferences for the current session, then emit a complete plan (`mode: "plan-only"`, `setup_state.companion: "missing"`). Downstream workflows (`/implement`, `/implement-spec`, `/to-tickets`, `acceptance`) proceed without disruption.
