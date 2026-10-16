# Actual installation evidence

Hosted run [38865970321](https://github.com/LightDevCoder/skills/actions/runs/38865970321) ran the `release-installation` workflow from main `c522857` against tag `v0.2.8` (peeled commit `c522857bd37a1f61fb1af9a4ae5e6892a949f06c`). The default branch resolved to the same commit. `result.json` records the source manifests and the complete installed manifests for every destination; `commands.json` records the exact argv, working directory and exit of all 12 commands.

`command-logs.zip` holds the raw command logs byte for byte. The logs are archived because terminal output ends with extra blank lines that repository whitespace checks reject.

All destinations belong to a fresh hosted Linux user, not to the maintainer's machine. This is installation evidence, not Linux Codex or Claude runtime evidence. Local Host discovery on the maintainer's machine is recorded in [local-hosts.md](local-hosts.md).
