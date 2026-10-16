# light-cheng/skills v0.2.9 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md) · [Release Notes](RELEASE_NOTES.md)

Status: `VERIFIED` — Published through the pull-request path with exact-candidate PR CI, a tree check of the merged commit, CI on the merged commit, a protected annotated tag, actual fresh released-source installations, real-Host smokes and a public GitHub Release. This receipt is first created on main after publication. The tag contains no receipt.

| Field | Value |
| --- | --- |
| **Repository** | `light-cheng/skills` |
| **Release** | `v0.2.9` |
| **Release Tag** | `v0.2.9` |
| **Annotated Tag Object** | `34ef01aaaced67f6877994c3cb15ea46cf8a00fa` |
| **Tag Target Commit** | `ae11283bb0c943f1a27f4a32e1a1b5caba37c92c` |
| **Release URL** | https://github.com/light-cheng/skills/releases/tag/v0.2.9 |
| **Publication Timestamp** | `2026-10-16T12:35:17Z` |
| **Collection Package Count** | 39 admitted packages; 407 package files |
| **Policy Status** | `PROVISIONAL` |
| **Scope** | Live links and install commands move to `light-cheng`; `release-workflow` improvements (repository from the checkout, pull-request path, required vs optional install evidence with a real-Host smoke, broken-release guide); `agent-config` schemas re-copied from `light-cheng/agent-config` |
| **Candidate** | `b2f0e5320e393514c00bf0b6bd82c8e75426f7e1` (PR #8 head); tag target is its merge commit on main with the same tree `f2c7d0bbdffeeed967634a7739b0b4768e11592b` |

| Gate | Status | Evidence |
| --- | --- | --- |
| **Local Test Suite** | `PASS` | On the candidate tree: 627 pytest passed, 2 skipped; compile; public docs (default and `--tag v0.2.9 --stage prepared`); evidence redaction; `prepared` integrity gate PASS; clean tree export passes collection discovery |
| **GitHub Actions CI** | `PASS` | PR run [38899769096](https://github.com/light-cheng/skills/actions/runs/38899769096) `collection-quality` on exact candidate `b2f0e5320e393514c00bf0b6bd82c8e75426f7e1`, completed, success; push run [38899915938](https://github.com/light-cheng/skills/actions/runs/38899915938) on the merged commit `ae11283bb0c943f1a27f4a32e1a1b5caba37c92c`, completed, success |
| **Merged Tree** | `PASS` | `check_merged_candidate.py --candidate b2f0e53 --merged ae11283 --branch origin/main` PASS: the merge commit carries the candidate tree |
| **Tag Object & Resolution** | `PASS` | Ruleset 23728847 active on `refs/tags/v*`, forbids update and deletion, no bypass; preflight PASS; remote annotated object and peel match the release commit (`tagged --check-remote` PASS) |
| **Pinned Fresh Install** | `PASS` | [38900111822](https://github.com/light-cheng/skills/actions/runs/38900111822), dispatched from main, source `light-cheng/skills#v0.2.9`: Codex and Claude Code project targets each 39 packages / 407 files, exact tag bytes |
| **Generic Latest Fresh Install** | `PASS` | Same run, source `light-cheng/skills`, separate project; default branch resolved to `ae11283`; Codex and Claude Code each 39 / 407 exact |
| **Native Codex Global Install** | `PASS` | Same run: real `--global --agent codex` into `/home/runner/.agents/skills`, 39 / 407 exact tag; HOME and CODEX_HOME not overridden |
| **Single Skills** | `PASS` | Same run: `light-implement` 6 files, `light-tdd` 5, `light-research` 3, each in its own fresh Codex project, exact tag |
| **Real-Host Smoke** | `PASS` | [Local record](installation/local-hosts.md): local `#v0.2.9` install byte-identical for Claude Code and pi; Claude Code 2.1.296 listed all 39 and called `eli5`; pi 1.3.0 loaded `eli5` from the fresh project's `.agents/skills` |
| **GitHub Release Publication** | `PASS` | [v0.2.9](https://github.com/light-cheng/skills/releases/tag/v0.2.9), neither draft nor prerelease, marked latest, timestamp above; every body link resolves |

[Installed manifests](installation/result.json) and [commands](installation/commands.json) bind 6 scenarios, 8 destinations and 12 successful commands; [raw logs](installation/command-logs.zip) are kept. Skills CLI 1.7.2, distribution SHA256 `72f1805ea4f6c62b0532cb77a9f021e7930bb7ca962f87a3fbf985d1ada5d56d`. Observed CI and publication records: [candidate CI](candidate-ci.json), [release-commit CI](release-ci.json), [installation CI](installation-ci.json), [publication](publication.json).

This was the first release on the pull-request path. Friction found and handled: the documented parent check rejected a candidate whose branch had merged main, so the check became an ancestor check before the candidate was prepared; `git switch main` cannot run in a worktree while main is checked out elsewhere, so the release checkout detached at the release commit; in zsh the documented `git push origin "$CANDIDATE_SHA:refs/heads/..."` fails because `:r` after a variable is a zsh modifier, so the ref was pushed with a literal SHA and the commands now brace the variable (`${CANDIDATE_SHA}`); pi print mode with `--mode json` waited on stdin until stopped.

Limits: Codex is not installed on the maintainer's machine, so Codex is covered by the hosted installation targets only. pi's self-reported Skill list is incomplete; the loaded `SKILL.md` path is the evidence. `main` is not protected by a branch ruleset; protecting it is recommended. Installation evidence does not prove each Skill's behavior. An unqualified install follows main; the tag keeps this snapshot.
