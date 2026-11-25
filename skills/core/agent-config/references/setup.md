# Setup questionnaire and companion bootstrap

`agent-config setup` prepares or repairs companion MCP registration and user-confirmed execution profiles. Setup never plans or dispatches current task work; once the profile is saved (or declined), setup ends cleanly.

## 1. Companion bootstrap CLI (`agent-config setup`)

When the optional `agent-config` companion MCP is not yet registered or healthy, use the standalone CLI from `light-cheng/agent-config` with explicit user consent:

- `agent-config setup --check`: Runs a live MCP transport and contract probe. Exits `0` only when the companion is registered, reachable, on `protocol_version === 1`, and exposing all 8 canonical tools ([companion-contract.md](companion-contract.md)); exits `1` otherwise (`registration != reachability != health`).
- `agent-config setup --preview`: Read-only inspection that outputs a unified diff and target file ownership block for host MCP registration.
- `agent-config setup --apply --yes`: Atomically writes the previewed registration only after explicit user approval (`--yes` is required; bare `--apply` refuses to mutate files and exits `1`), followed by `agent-config setup --check` to verify live health.
- Additional flags: `--workspace <path>`, `--host <host_id>`, `--scope <project|global>`, `--json`.

If the `agent-config` CLI is not installed and the user wants persistent profiles, show the manual install steps from `light-cheng/agent-config` (`npm ci && npm run build && npm install -g .`) and wait for user action. If the user declines companion setup, continue in session-local `plan-only` mode.

## 2. Host inspection and mode selection

1. Call `inspect_host` (when companion is healthy) or gather current session facts (`host_id`, available models, supported effort strings, concurrency cap).
2. Present the detected host summary concisely:
   ```text
   Host: <host_id> (<adapter_id>)
   Workspace: <workspace_path>
   Available models: <model IDs>
   Supported effort values: <e.g. low, medium, high>
   ```
3. Ask the user to choose the operating mode:
   - **Single model (`model_mode: "single"`):** One model executes all tasks and tickets, right-sized via resolved effort and fresh-context workers.
   - **Multiple selectable models (`model_mode: "multi"`):** Specific user-chosen models bind to abstract tiers (`routine`, `standard`, `high`, `review`).

## 3. Single-model profile flow

1. Confirm the active model identifier (`single_model.model`).
2. Select `execution_effort` and `review_effort` policies (`highest-supported`, `default`, `lowest-supported`, or a concrete value from `supported_effort_values`).
3. Confirm `capabilities` (`subagents`, `threads`, `parallelism`, `concurrency`).
4. Show the profile summary matching [profile-schema.md](profile-schema.md) and call `save_profile` upon user confirmation.

## 4. Multi-model tier binding flow

1. Display `available_models` from `inspect_host` without ranking or recommending models by name.
2. Ask the user to bind an available model ID (`source: "user-confirmed"`) and effort policy to each abstract tier:
   - `routine`: Low uncertainty, mechanical edits, config updates, straightforward tests.
   - `standard`: Typical feature slices, standard bug fixes, module-level changes.
   - `high`: Cross-cutting architecture, concurrency invariants, subtle debugging, critical paths.
   - `review`: Controller integration review and fresh-context independent verification.
   *(Multiple tiers may share the same model ID.)*
3. Confirm `capabilities` (`subagents`, `threads`, `parallelism`, `concurrency`).
4. Preview the resulting [profile-schema.md](profile-schema.md) document and call `save_profile` after explicit user confirmation.

## 5. Effort policy resolution rules

Abstract policies decouple saved profiles from vendor-specific effort strings:

- `highest-supported`: Resolves to the last element of the host's ordered `supported_effort_values` (for example `"high"` on `["low", "medium", "high"]`, `"deep"` on `["standard", "deep"]`, or `"max"` only when `"max"` is explicitly listed in `supported_effort_values`).
- `lowest-supported` (or `minimal`): Resolves to the first element of `supported_effort_values`.
- `default`: Uses `default_effort_value` when supported by the host, otherwise omits an explicit override.
- **Anti-literal-max invariant:** Never emit literal `"max"` unless `"max"` appears in the host's verified `supported_effort_values`.
