# Setting Up `light-decision-mcp`

Read this guide when the user explicitly asks to configure, inspect, or troubleshoot `light-decision-mcp`, or after returning a self-judgment when all three conditions hold:

1. No `light-decision-mcp` backend within `Decision data` reported `ready: true` in this session.
2. This workflow or upcoming judgments in the session would clearly benefit from typed decisions.
3. Setup has not been declined (`Decision data` is not `off` in `docs/agents/light-project.md`, and `~/.config/light/decision-policy.json` does not set `"setup": "declined"`).

When triggered during a live workflow, complete, log, and return the current judgment by self-judgment first. Inspect read-only state before asking questions, and modify nothing until the user approves.

## 1. Check live state and delegate hardware advising to the CLI

Do not probe CPU, RAM, GPU, or disk with ad-hoc shell heuristics. `light-decision-mcp` ships a built-in hardware-aware advisor, setup wizard, secret store, and loopback admin UI:

```bash
# Read-only host hardware, runtime ecosystem, and backend health check
light-decision-mcp doctor

# Read-only local and cloud model recommendations matched to measured hardware
light-decision-mcp recommend

# Confirmation-gated interactive local and cloud backend setup
light-decision-mcp setup

# Loopback-only (127.0.0.1:4395, CSRF-protected) visual admin console & playground
light-decision-mcp ui

# Store or inspect direct provider API keys (0600 secrets.json or macOS Keychain)
light-decision-mcp key set PERPLEXITY_API_KEY --keychain
light-decision-mcp key list
```

*(When running from a local checkout instead of a global binary, invoke `node /absolute/path/to/Light-Decision-MCP/bin/cli.mjs <command>`.)*

Summarize what `status` or `light-decision-mcp doctor` / `recommend` found in one or two sentences, and state the core boundary trade-off:

- **On-device local backends** (`local-opendecider`, Magpie local `ollama` / `mlx-serve` / `omlx`): satisfy the default `Decision data: on-device` ceiling with zero payload leaving the machine and zero marginal API cost, typically text-only.
- **Cloud or gateway backends** (Magpie gateway routing to `google/gemini-decision-1`, TypeSafe `Jev`, OpenAI `gpt-6-luna`, Perplexity `pplx-decider-*`, OpenRouter, or LiteLLM Proxy): support multimodal `images` and optional `web_grounding`, and require `Decision data: third-party` (or `private-network` for a self-hosted LAN gateway) in `docs/agents/light-project.md`.

## 2. Register with Magpie or standalone stdio MCP

### Magpie plugin (recommended when Magpie is installed; zero API keys stored in plugin)

```bash
# Install from GitHub or a local checkout
magpie plugin add github:light-cheng/Light-Decision-MCP
# or: magpie plugin add /absolute/path/to/Light-Decision-MCP

# Verify plugin and 6 MCP tools
magpie plugin list
magpie tools

# Optional: register a cloud decision provider key in Magpie
magpie provider add google <YOUR_GOOGLE_AI_STUDIO_API_KEY>
```

Enable `light-decision-mcp` for your agent in **Magpie -> Library -> MCP**, or adjust routing in Magpie's embedded **Light Decision** plugin page.

### Standalone stdio MCP (Claude Desktop, Claude Code, Codex, Cursor, CC Switch)

Point the client's `mcpServers` entry at `bin/stdio.mjs` (referencing keys strictly by `apiKeyEnv` in `~/.config/light-decision-mcp/config.json` or storing them via `light-decision-mcp key set <ENV_VAR>`, never plaintext keys in repository files):

```json
{
  "mcpServers": {
    "light-decision-mcp": {
      "command": "node",
      "args": ["/absolute/path/to/Light-Decision-MCP/bin/stdio.mjs"]
    }
  }
}
```

## 3. Human-only dashboard and credential steps (`wizard` with Graceful fallback)

Creating third-party API keys, signing into provider dashboards, or approving large model weight downloads are human-owned steps:

- **When `wizard` is installed**: Offer `wizard` by name and invoke it after user confirmation to generate a stage-by-stage interactive walkthrough with hidden secret entry and verification checks.
- **Graceful fallback (when `wizard` is absent or declined)**: Present this concise inline checklist directly:
  1. Obtain the provider API key in your browser dashboard, or review the local model size reported by `light-decision-mcp recommend`.
  2. Save credentials outside chat and outside git using `magpie provider add <provider> <API_KEY>` (Magpie) or `light-decision-mcp key set <ENV_VAR> --keychain` (direct stdio), or run `light-decision-mcp setup` in your terminal for local `opendecider` provisioning.
  3. If using a `private-network` or `third-party` backend, update `Decision data:` in `docs/agents/light-project.md` (via `/light-setup` or with explicit user approval).
  4. Verify readiness with `light-decision-mcp doctor` and a read-only MCP `status` call (`ready: true`).

## 4. Record policy metadata or remember a refusal

After user approval:

- Register backend aliases (`names` and `data`, leaving `questions` empty until calibrated; see [`formats.md`](formats.md)) in `~/.config/light/decision-policy.json`, or print the snippet if `~/.config/light/` is outside host write access.
- Update `docs/agents/light-project.md` only with user approval. Never write API keys, gateway URLs, or local model paths into skill files or repositories.

When the user declines setup, ask once whether to record the refusal for **this repository** (`Decision data: off` in `docs/agents/light-project.md`) or **this machine** (`"setup": "declined"` at the top level of `~/.config/light/decision-policy.json`), save only with their approval, and do not offer setup again while that setting remains.
