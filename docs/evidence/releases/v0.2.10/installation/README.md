# Actual installation evidence

Hosted run [39009276312](https://github.com/light-cheng/skills/actions/runs/39009276312) ran the `release-installation` workflow from `main` (dispatched with `--ref main`) against tag `v0.2.10` (peeled commit `adffefc7e0895e490cd9190998d3f93c4391d87b`). The default branch resolved to the same commit. `result.json` records the source manifests and the complete installed manifests for every destination; `commands.json` records the exact argv, working directory and exit of all 12 commands.

`command-logs.zip` holds the raw command logs byte for byte. The logs are archived because terminal output ends with extra blank lines that repository whitespace checks reject.

All destinations belong to a fresh hosted Linux user, not to the maintainer's machine. This is installation evidence, not Linux Codex or Claude runtime evidence.
