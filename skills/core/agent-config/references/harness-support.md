# Harness support matrix and adapter boundaries

This reference documents native host adapter coverage in the `agent-config` companion runtime (`light-cheng/agent-config`) and the generic `plan-only` fallback.

## 1. Native coding-agent harnesses (10)

| Harness | Config path | Companion MCP registration |
|---|---|---|
| **Codex CLI** | `.codex/config.toml` or `$CODEX_HOME/config.toml` | `.codex/config.toml` (`[mcp_servers.agent-config]`) |
| **Claude Code** | `.mcp.json` or `~/.claude.json` | `.mcp.json` (project) / `~/.claude.json` (user) |
| **Antigravity (`agy`)** | `.gemini/config.json` | `.gemini/config.json` |
| **DeepSeek Harness (`DSH`)** | `cordis.patch.yml` or `$DSH_HOME/profiles/<name>/cordis.patch.yml` | `@deepseek-ai/dsh-mcp-client` in `cordis.patch.yml` |
| **OpenCode** | `opencode.json` / `opencode.jsonc` | `opencode.json` / `opencode.jsonc` |
| **ZCode** | `.zcode/config.json` / `~/.zcode/cli/config.json` | `.zcode/config.json` (`mcp.servers["agent-config"]`) |
| **Cursor** | `.cursor/settings.json` | `.cursor/mcp.json` |
| **Grok Build** | `.grok/config.toml` | `.grok/config.toml` |
| **Hermes** | `~/.hermes/config.json` | `~/.hermes/config.json` |
| **Pi Coding Agent** | `.pi/settings.json` / `~/.pi/agent/settings.json` | `.pi/mcp.json` / `~/.pi/agent/mcp.json` (requires enabled `npm:pi-mcp-adapter`, project trust, and reload) |

## 2. Native adapter responsibilities and boundaries

Each native adapter implements factual host operations without guessing model intelligence:
- Identify host and adapter version, active workspace, available models, and discrete `supported_effort_values`.
- Report `subagents`, `threads`, `parallelism`, and `concurrency` as `available`, `unavailable`, or `unknown` backed by verified evidence ([host-evidence-schema.md](host-evidence-schema.md)).
- Support read-only preview (`preview_configuration`), user-approved atomic apply (`apply_configuration`), and read-back verification (`validate_configuration`) per [companion-contract.md](companion-contract.md).

## 3. Generic `plan-only` fallback

When no native adapter matches the active host (or when Pi lacks project trust or `pi-mcp-adapter`, or when the companion MCP is absent):
- Operate in read-only `plan-only` mode (`mode: "plan-only"`).
- Produce the full adaptive execution plan so the user or Controller can apply model, effort, and fresh-context worker choices manually.
- Never return `UNSUPPORTED` merely because an automated file-mutation adapter is absent, and never attempt speculative writes to unfamiliar config files.
