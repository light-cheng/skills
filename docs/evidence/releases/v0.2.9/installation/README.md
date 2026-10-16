# Actual installation evidence

Hosted run [38900111822](https://github.com/light-cheng/skills/actions/runs/38900111822) ran the `release-installation` workflow from `main` (dispatched with `--ref main`, as RELEASE-STAGES now says) against tag `v0.2.9` (peeled commit `ae11283bb0c943f1a27f4a32e1a1b5caba37c92c`). The verifier resolved the repository as `light-cheng/skills` from `GITHUB_REPOSITORY`. The default branch resolved to the same commit. `result.json` records the source manifests and the complete installed manifests for every destination; `commands.json` records the exact argv, working directory and exit of all 12 commands.

`command-logs.zip` holds the raw command logs byte for byte. The logs are archived because terminal output ends with extra blank lines that repository whitespace checks reject.

All destinations belong to a fresh hosted Linux user, not to the maintainer's machine. This is installation evidence, not Linux Codex or Claude runtime evidence. The real-Host smokes on the maintainer's machine are in [local-hosts.md](local-hosts.md).
