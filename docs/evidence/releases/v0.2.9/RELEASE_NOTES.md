# v0.2.9 — New Owner Name and a Sturdier Release Workflow

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md)

This release snapshot v0.2.9 keeps the same 39 Skills. It moves every live link and install command to the renamed GitHub account and makes `release-workflow` safer to run. The [release manifest](RELEASE_MANIFEST.md) records the preparation-time scope and local evidence; observed CI, installation and publication facts are recorded in the release receipt on `main`.

## Changes you will notice

- **New owner name.** The GitHub account `LightDevCoder` is now `light-cheng`. README, INSTALLATION, the migration guides, package guides, quick start and the packages that link to this collection or its companions (`agent-config`, `ask-light`, `light-travelpage`, `manuscript-ops`, `decision-map`, `kanban-worker`) use `light-cheng`. Old commands still redirect; update them anyway (see the [v0.2.9 migration guide](https://github.com/light-cheng/skills/blob/main/docs/MIGRATION-v0.2.9.md)). Historical evidence keeps the name it was written with.
- **release-workflow.** The release scripts find the repository from the checkout instead of a fixed name, and live checks accept only that repository. The candidate reaches `main` through a pull request, and a new check proves the merged commit carries the CI-verified tree. Installation evidence names the required hosted workflow and adds an optional real-Host smoke test. A new guide says what to do when a published release is broken. The Skill and its references are rewritten in plain prose.
- **agent-config companion.** The schema snapshot is re-copied from `light-cheng/agent-config`; only the schema `$id`s change.

## Installation

Installation from the actual v0.2.9 source passed in fresh environments. Select the fixed tag for a reproducible install:

```bash
npx skills add light-cheng/skills#v0.2.9
npx skills add light-cheng/skills#v0.2.9 --skill release-workflow
```

## Verification

Local evidence at preparation is listed in the [release manifest](RELEASE_MANIFEST.md). Pull-request CI on the exact candidate, CI on the merged commit, the merged-tree check and the protected annotated tag are verified. On a fresh hosted Linux user, pinned and default whole installs for Codex and Claude Code projects, native Codex global scope and three single Skills each matched their source bytes (39 packages, 407 files). Locally, Claude Code listed all 39 Skills from a fresh install and both Claude Code and pi ran `eli5` from it. Codex is not installed on the maintainer's machine. The post-release receipt on main has the details. The full [changelog](https://github.com/light-cheng/skills/blob/main/CHANGELOG.md) lists every change.
