# Light Skills v0.2.9 migration

[简体中文](MIGRATION-v0.2.9.zh-CN.md)

**Status:** v0.2.9 is published. Pull-request CI on the exact candidate, the merged-tree check, the protected tag and fresh installs from the released source passed; see the [release receipt](evidence/releases/v0.2.9/RELEASE_RECEIPT.md).

## The repository owner name changed

The GitHub account `LightDevCoder` is now `light-cheng`. The repository, its tags and its content are the same. GitHub redirects the old name, so old commands still work today, but a redirect stops working if someone else registers the old account. Update your commands and links:

| Before | Now |
| --- | --- |
| `npx skills add LightDevCoder/skills` | `npx skills add light-cheng/skills` |
| `npx skills add LightDevCoder/skills#v0.2.8` | `npx skills add light-cheng/skills#v0.2.8` |
| `https://github.com/LightDevCoder/agent-config` | `https://github.com/light-cheng/agent-config` |

To update a clone, run `git remote set-url origin https://github.com/light-cheng/skills.git`.

No package is renamed, added or removed. Installed Skills keep their paths; reinstalling is optional.

## release-workflow

If you maintain a fork and use `release-workflow`, its scripts now find the repository from `--repo`, `GITHUB_REPOSITORY`, `gh repo view` or `origin` instead of a fixed name. Pass `--repo owner/name` in a fork with an `upstream` remote. The candidate now goes to `main` through a pull request; see the Skill's `references/RELEASE-STAGES.md`.
