# Routing and MCP Tool Contracts

## Discovering `light-decision-mcp` in the active session

`light-decision-mcp` exposes 6 MCP tools. Depending on the host or hub (Magpie Library MCP or standalone stdio MCP), tool names appear bare (`status`, `yes_no`, `choose`, `score`, `decide`, `decide_batch`) or prefixed with the server identifier (such as `light-decision-mcp__status` or `mcp__light-decision-mcp__status`).

Verify availability from live session evidence before sending a judgment:

1. Check whether `light-decision-mcp` tools are registered in this session.
2. Call `status` (read-only, zero billable inference), passing `data_destination` or `multimodal: true` filters when narrowing candidates.
3. Select a backend with `ready: true` whose `data_destination` fits within the repository's `Decision data` ceiling and whose `circuit.state` is not `open` without a ready fallback.

A config file on disk alone is not availability evidence. Note that local on-device models that lazy-load weights on first call can take 2 to 10 seconds on cold start before reaching steady latency.

## The 6 `light-decision-mcp` tools

| Tool | Use when | Required inputs | Key optional inputs |
|---|---|---|---|
| `status` | Probing health, `data_destination`, `capabilities` (`images`, `web_grounding`), `available_models`, `circuit`, `limits`, and `setup_hint` | *(none)* | `backend`, `data_destination` (`on-device \| private-network \| third-party`), `multimodal` (`boolean`) |
| `yes_no` | Evaluating one binary (`noul`) gate | `state`, `question` | `true_description`, `false_description`, `images`, routing options |
| `choose` | Picking one option from `2..255` unordered choices | `state`, `question`, `options` (`string[]` or `{label: description}`) | `images`, routing options |
| `score` | Rating `state` on `2..255` ordered rubric levels (**lowest first**, index `0..N-1`) | `state`, `question`, `levels` (`string[]` or `{label, description}[]`) | `images`, routing options |
| `decide` | Answering multiple independent questions (`noul`, `choice`, `score`) over one shared `state` in a single pass (`1..64` questions, `<= 200,000` state chars) | `state`, `questions` (`Record<id, {type, instructions, criteria}>`) | `images`, routing options |
| `decide_batch` | Evaluating one `questions` map across `1..64` independent text/JSON `states` (`<= 512` `states * questions` items) with bounded concurrency | `states`, `questions` | `mode`, `backend`, `model`, `max_data_destination`, `web_grounding` |

### Shared routing arguments on inference calls

Every inference tool (`yes_no`, `choose`, `score`, `decide`, `decide_batch`) accepts:

- `max_data_destination` (`"on-device" | "private-network" | "third-party"`): **Always pass this** set to the effective ceiling for the run.
- `mode` (`"local_only" | "api_only" | "api_with_local_fallback"`):
  - Pass `"local_only"` whenever effective `max_data_destination` is `"on-device"`. This locks routing strictly to on-device backends (`local-opendecider`, local Magpie `ollama` / `mlx-serve` / `omlx`) so zero state leaves the machine.
  - Use `"api_with_local_fallback"` when `max_data_destination` permits the primary API backend and a local on-device backend is also ready for instant circuit-breaker fallback.
  - Use `"api_only"` when targeting a cloud or private-network backend where silent local fallback is undesired.
- `backend` (`string`): Explicit backend ID (such as `"magpie"`, `"local-opendecider"`, `"typesafe"`, `"perplexity"`, `"google-direct"`, `"openai-direct"`). When `backend` is specified explicitly, `light-decision-mcp` uses local fallback only if `mode: "api_with_local_fallback"` is also passed.
- `model` (`string`): Explicit model override (such as `"google/gemini-decision-1"`, `"openai/gpt-6-luna"`, `"pplx-decider-v1.3"`, or `"group/<decision-group>"`).
- `web_grounding` (`boolean`): Passed only when external web grounding is needed, supported by the backend (such as Perplexity), and allowed by `Decision data: third-party`.
- `allow_image_drop_on_fallback` (`boolean`, on `yes_no`, `choose`, `score`, `decide`): Keep `false` (default); see [Multimodal `images` safety gate](#multimodal-images-safety-gate).

### Wire question IDs and option descriptions

- Prefer `{ label: description }` maps in `choose` (`options`) and `{ label, description }[]` arrays in `score` (`levels`) whenever labels are terse, so the decision model sees explicit criteria per option.
- In `decide` and `decide_batch`, pass canonical `<caller>/<slug>` keys (such as `agent-config/task-complexity` and `agent-config/reasoning-need`) directly in `questions`: `light-decision-mcp` automatically aliases keys outside `/^[A-Za-z0-9_-]{1,64}$/` on the wire (`q_0`, `q_1`, ...) and restores the caller's exact keys in `answers`.
- Batch independent questions sharing the same `state` into one `decide` call rather than issuing serial single-question calls.

## Data-boundary guard and source selection order

Data destinations are ordered from nearest to farthest:

`on-device` < `private-network` < `third-party`

`Decision data` in `docs/agents/light-project.md` sets the maximum ceiling (`on-device` when omitted; self-judgment pass-through when `off` or unrecognized). If a resolved backend's `data_destination` exceeds `max_data_destination`, `light-decision-mcp` rejects the call before any network request with `data_boundary_exceeded`, and never escalates a local request to cloud.

Pick the first candidate that fits within `max_data_destination`:

1. **User-named backend/model for this run**, when `status` shows it ready and within `max_data_destination` (otherwise skip it and tell the caller why).
2. **Ready backend calibrated for `question_id`** in `~/.config/light/decision-policy.json` (see [`formats.md`](formats.md)).
3. **Ready uncalibrated backend** within `max_data_destination`: query it once to record the typed answer and probabilities, then apply agent self-judgment as `final` (`fallback_reason: uncalibrated`).
4. **Agent self-judgment** (`fallback_reason: unavailable`).

Break ties on any step in favor of the nearest `data_destination` (`on-device`, then `private-network`, then `third-party`). Query at most one route per live judgment; multi-backend comparison belongs only to user-requested offline calibration.

## Circuit breaker and mid-flight fallback provenance

In `api_with_local_fallback` mode (including mid-batch trips during `decide_batch`), `light-decision-mcp` tracks per-backend circuit health (`closed -> open -> half_open`) and switches immediately to the local `on-device` backend on availability faults (`timeout`, HTTP 429 `rate_limited`, HTTP 5xx `upstream_error`, `gateway_unreachable`, `network_error`, or `circuit_open`).

When mid-flight fallback triggers:

- `fallback_used` is `true` (and `decide_batch` reports `fallback_count` plus per-item `fallback_used`).
- Top-level `backend`, `model`, and `data_destination` reflect the **fallback backend that actually answered**, while `fallback_info` records `{ primary_backend, primary_model, reason, primary_status?, circuit_state }`.
- Always check calibration policy in [`formats.md`](formats.md) against the actual answering `backend` / `model`, never against `fallback_info.primary_backend`.

Caller errors (`invalid_arguments`, `data_boundary_exceeded`, `images_unsupported`) never trigger backend retries; handle any failed MCP call by falling back once to agent self-judgment.

## Multimodal `images` safety gate

`yes_no`, `choose`, `score`, and `decide` accept up to `4` images in `images`:

- Local regular files (`png`, `jpeg`, `webp`, `gif`, magic-byte verified, `<= 10 MB` per file)
- Inline base64 data URIs (`data:image/(png|jpeg|webp|gif);base64,...`, `<= 10 MB` decoded)
- `https://` URLs (`http://` and `file://` URLs are rejected)

Enforce two safety rules whenever a judgment includes `images`:

1. **Verify multimodal capability within the data ceiling first.** Call `status(multimodal: true)` (or inspect `capabilities.images` on ready backends within `max_data_destination`). Most local `on-device` System One models are text-only while multimodal models such as `google/gemini-decision-1`, `gpt-6-luna`, or Cloudflare Clef often route to `third-party`. If no image-capable backend is ready within `max_data_destination`, skip the MCP call and answer via in-session agent self-judgment with `fallback_reason: images-unsupported`.
2. **Refuse silent image drops on fallback.** Leave `allow_image_drop_on_fallback` set to `false` (default). If a cloud multimodal primary fails mid-call in `api_with_local_fallback` mode and the local fallback backend is text-only, `light-decision-mcp` refuses to strip `images` and fails fast with `fallback.skipped_reason: "images_unsupported"`. Catch that error and fall back to agent self-judgment (`fallback_reason: images-unsupported`) rather than evaluating blind text. Pass `allow_image_drop_on_fallback: true` only when the user or caller explicitly authorizes dropping images on fallback.
