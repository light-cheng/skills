# Optional AI connection

Read this reference when the traveler chooses AI for a new page or asks to configure an existing AI page. Preserve choices and authorization already given. Enabling the generator is a local source change; connecting a service, storing its key and deploying are separate actions that each need the owner's approval.

## Generate and scope

```bash
node <skill>/scripts/create.mjs <new-project-directory>             # off (default)
node <skill>/scripts/create.mjs <new-project-directory> --ai off    # explicit off
node <skill>/scripts/create.mjs <new-project-directory> --ai on     # enabled
```

`ai-config.json` contains only `provider: off|on`. It says whether the page shows an AI entry and nothing else: the service, key, model and API format live only in server settings. Pages generated before v0.2.8 say `openai`, which still reads as `on`. The build adds the AI entry, dialog and client only for `on`. Off builds contain no AI entry or client, and the protected AI handler returns 404 before accessing D1 or an upstream. Generation and build never call the model. Editing `ai-config.json` and rebuilding changes an existing page's switch; source updates preserve it.

The enabled page keeps the complete handbook: flight/stay cards, itinerary, geographic maps, original tickets, ledger and task checks. Its assistant reads authored trip context and can add/update tasks, check existing ticket status, add ledger travelers and record expenses. Actions follow enabled modules. It cannot rewrite itinerary, bookings, maps or original attachments. It cannot purchase, pay, cancel or change merchant orders. The UI reports the exact confirmed actions separately from the model's prose.

All browser traffic stays on this page's origin: `/api/ai/<tripId>` and the existing `/api/trip/<tripId>`. The existing group session, same-origin check and trip identity protect both handlers. A traveler's request carries only `mutationId`, `expectedRevision` and `message`; any other field, such as a model or endpoint, is rejected. AI prepares a plan, validates it with `applyChanges`, durably caches the plan, then submits that exact plan to `handleTrip` with `expectedRevision` and `mutationId`. A stale revision returns 409. An identical retry reuses the plan and D1 mutation receipt instead of adding another expense. Reusing an ID for different content returns 409. Apply `0002_ai_requests.sql` through the same scoped D1 migration flow; it adds a table and does not reset state.

## Connect a service (page owner, at deployment)

The page owner chooses one HTTPS API service that speaks the OpenAI or the Anthropic format: OpenAI, Anthropic, or any compatible provider or gateway. The key must never enter the conversation, a command argument or a shell line the Agent runs. Give the owner the exact command and ask them to run it in their own terminal: the script then asks for the key at a hidden prompt and lets them pick the format and model from lists. If the Agent runs it instead, the owner first exports `AI_API_KEY` in that environment themselves, and the Agent passes `--format` and `--model` (taken from the script's printed list), because there is no terminal to pick in.

```bash
node <skill>/scripts/ai-setup.mjs <project-directory> --base-url https://api.anthropic.com/v1                  # local .dev.vars
node <skill>/scripts/ai-setup.mjs <project-directory> --base-url <url> --target pages --project-name <name>    # Pages secrets
```

The script:

1. checks that the project was generated with v0.2.8 or later and refuses a symlinked `.dev.vars` or `ai-config.json`;
2. reads `GET <base>/models` with OpenAI-style and Anthropic-style authentication and tells the formats apart (an OpenAI list marks items `object: "model"`, an Anthropic list `type: "model"`). If the service answers both ways, the owner picks one in the terminal, or passes `--format openai-chat|openai-responses|anthropic-messages`; if it answers neither, pass `--format` and `--model`;
3. lists the models for the owner to pick, or takes `--model <id>` when there is no list;
4. sends one request with one tool and requires a real tool call back. A listed model is only discovery evidence. If chat completions returns no tool call, try `--format openai-responses`;
5. only after that, writes `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL` and `AI_API_FORMAT` to ignored `.dev.vars` (mode 0600; older `OPENAI_*` lines are removed) or to Pages secrets through `wrangler pages secret bulk` on stdin, and sets `ai-config.json` to `on`.

It prints the format, model and round-trip result, never the key. Then rebuild (`npm run build`) and restart the local preview, or rebuild and deploy for Pages: the AI entry appears only in the next build. Older `OPENAI_*` Pages secrets stay in place but are ignored once `AI_BASE_URL` is set; the owner may delete them with `npx wrangler pages secret delete <NAME> --project-name <name>`. A service on the owner's own computer or behind a Tunnel is not reachable from a deployed page; that setup belongs to the optional `light-travelpage-gw` capability (see the Skill's Optional capabilities). Without it, use a service the deployed page can reach over HTTPS.

The base must be an HTTP(S) API prefix, without embedded credentials, query parameters or a final `/chat/completions`, `/responses`, `/messages` or `/models` path. An origin with no path becomes `/v1`; a supplied custom prefix is preserved. The server uses the whole `AI_*` set when `AI_BASE_URL` is set and otherwise the whole older `OPENAI_*` set (`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_API_STYLE` = `chat-completions` or `responses`); it never mixes fields from both. A page generated before v0.2.8 carries its own older runtime, which reads only `OPENAI_*`: leave it as it is. To use the new setup or Anthropic for that trip, generate a new project with `create.mjs --ai on`, apply the existing trip with `update.mjs`, and deploy it to the same Pages project and D1 database.

Keep keys, `.dev.vars`, `.env*`, raw source documents, extraction notes and local source paths out of the client, `dist/` and commits. The build copies an explicit asset list and a validated public switch. Keep deliberate protected trip/ticket publication within the original [deployment contract](deployment.md).

## API requirements and limits

- **`openai-chat`**: `POST <base>/chat/completions` with `messages`, JSON-schema `tools` and assistant `tool_calls`; later requests include `role: tool` and the matching `tool_call_id`.
- **`openai-responses`**: `POST <base>/responses`, `function_call` output, matching `function_call_output` input, and preserved prior response items, including encrypted reasoning when provided. The adapter uses `store: false` and keeps that continuation only on the server. Some current OpenAI models call tools only through Responses; check the [official function calling guide](https://developers.openai.com/api/docs/guides/function-calling) for the selected model.
- **`anthropic-messages`**: `POST <base>/messages` with `x-api-key` and `anthropic-version: 2023-06-01`, a top-level `system` prompt, tools as `{name, description, input_schema}`, `tool_use` blocks in the reply and `tool_result` blocks (all results of one turn in one user message) in the next request. A reply cut at `max_tokens` saves nothing.

A text-only endpoint cannot perform these actions, and neither a protocol name nor a "compatible" label proves a usable model: the setup round trip does.

The shipped UI accepts text. It sends authored trip context and current shared records to the configured service only after a traveler submits a request. Original PDF/image bytes and API credentials are excluded from model context. Image understanding is not shipped: adding it requires a vision-capable model, protected upload handling and a real image test.

Expense amounts use integer cents, known traveler IDs and the ledger's existing base currency (`CNY` until configured). A foreign expense requires the user's actual converted base amount; the assistant cannot invent an exchange rate. Missing or ambiguous facts remain pending. Tool loops are bounded; a model failure before plan completion saves no shared change.

## Verify the chosen environment

1. Build both switch modes in fresh generated projects. Off must show no AI entry/client and must make no upstream request. Inspect enabled `dist/` for only the public switch, ordinary page assets and AI UI; server transport and credentials remain outside it.
2. Use synthetic local group secrets and the existing local D1 binding. Apply migrations locally, build and run `npm run preview` from the generated root. Test unauthenticated 401, wrong trip 403, foreign Origin 403, a real tool-created task, visible task refresh, expense cents, stale-revision 409 and the identical retry without duplicates.
3. Keep labels separate: mocked transport plus SQLite tests prove the tested contracts; local Wrangler proves local Functions/D1 integration; the setup round trip and a real tool-created task prove only that service, model and format; authenticated hosted sessions prove remote behavior. The owner's browser trial and content approval are separate gates. Report any unavailable gate directly.

For a quick local trial after configuration: “添加 to-do：出发前带上雨衣”, “把带上雨衣这项 to-do 标为完成”, “有哪些票据还未标记购票？”. To test expenses, first add actual test travelers and specify payer, participants, currency and amount. Use “修改明天的酒店预订” as a boundary test: it must explain the read-only limit and make no booking claim.
