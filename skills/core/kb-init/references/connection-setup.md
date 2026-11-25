# Connection Setup and Validation

Use this reference only after the user explicitly approves the SPEC and only when the chosen base requires a separate application, CLI, connector, MCP, API, or SDK connection rather than direct local file access.

## Secret and configuration guardrails

- Follow the connection route justified during Base Discovery; if the route is unavailable or outdated, stop and re-verify via [research-contract.md](research-contract.md) instead of silently swapping architectures.
- Prefer stable programmatic routes over GUI automation, and prefer project-scoped configuration over global harness changes (global changes require explicit approval in the SPEC).
- Never ask the user to paste API keys, tokens, passwords, or secrets into chat, prompts, maintenance docs, example files, or shell command arguments. Never echo secret values in logs, screenshots, or validation output.
- Use OAuth or connector-managed auth when supported; otherwise guide the user to store credentials in an approved local environment file, keychain, or secret store read directly at runtime without printing values. If a real secret is found in an example file, log, or history, sanitize the exposed copy when safe and advise credential rotation. If the current harness offers no safe non-chat credential path, stop the connection step and report the limitation.

## Execution sequence

1. **Inspect current environment**: Check connector/MCP availability, CLI/SDK binaries, network reachability, credential presence (configured vs missing, never printing values), and target workspace/container identity. Distinguish *not installed*, *not authorized*, and *unsupported*.
2. **Complete Agent-manageable setup**: Write approved project configuration, install approved project-scoped dependencies, prepare client/import scripts, and scaffold local support files.
3. **Request only minimal human actions**: Ask the user strictly for steps only they can perform (selecting an account/workspace, approving OAuth/permissions, approving an installation, or supplying a private internal endpoint). Never ask for public docs links you can research yourself.
4. **Validate live operations**: Config files or installed CLIs alone never prove connectivity. Run the smallest safe live checks covering every operation the approved KB needs:
   - resolve the intended target workspace or container;
   - read existing state;
   - create or write a real approved initialization item (or clean up a temporary probe only when deletion is safe and approved);
   - read back the written item;
   - test update, search/query, and attachment handling where required by `Ingest`, `Query`, or `Lint`.
5. **Handle partial or failed setup cleanly**: If any step fails, preserve all base-independent structures, templates, and scripts; report the exact failed check and cause (permission, network, missing tool, or unsupported operation); state the exact action that unblocks it; and keep connection status marked incomplete.
6. **Record secret-free reconnection guidance**: Document in the base's maintenance entry point the connection mechanism, non-secret workspace/container identifiers, required permission scopes, config file path, and health-check command so future Agent sessions reconnect reliably.
