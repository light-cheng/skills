# light-cheng/skills v0.2.10 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md) · [Release Notes](RELEASE_NOTES.md)

Status: `VERIFIED` — Published through the pull-request path with exact-candidate PR CI, a tree check of the merged commit, CI on the merged commit, a protected annotated tag, actual fresh released-source installations and a public GitHub Release. This receipt is first created on main after publication. The tag contains no receipt.

| Field | Value |
| --- | --- |
| **Repository** | `light-cheng/skills` |
| **Release** | `v0.2.10` |
| **Release Tag** | `v0.2.10` |
| **Annotated Tag Object** | `6c50145b35692caf31afa9577b5814b5d616e089` |
| **Tag Target Commit** | `adffefc7e0895e490cd9190998d3f93c4391d87b` |
| **Release URL** | https://github.com/light-cheng/skills/releases/tag/v0.2.10 |
| **Publication Timestamp** | `2026-10-17T06:18:20Z` |
| **Collection Package Count** | 39 admitted packages; 407 package files |
| **Policy Status** | `PROVISIONAL` |
| **Scope** | Host-neutral Skill calls in packages and docs (#12); `release-workflow` reads `release-state` field blocks and its stage guide is corrected (#10, #11); project-flow fixes from the stage 7 rehearsal in `review-loop`, `light-implement`, `light-redirect`, `clarify`, `project-clarify`, `project-retro` and `light-html-plan` (#13) |
| **Candidate** | `25441969216409697eba86cf4d71670e6404fbde` (PR #13 head); tag target is its merge commit on main with the same tree `1625f87abcb5be47fa7b76ddf987d52e74010d4a` |

| Gate | Status | Evidence |
| --- | --- | --- |
| **Local Test Suite** | `PASS` | Preparation evidence in the [release manifest](RELEASE_MANIFEST.md); on the tag target after publication: 641 pytest passed |
| **GitHub Actions CI** | `PASS` | PR run [38964270894](https://github.com/light-cheng/skills/actions/runs/38964270894) `collection-quality` on exact candidate `25441969216409697eba86cf4d71670e6404fbde`, completed, success; push run [39009026285](https://github.com/light-cheng/skills/actions/runs/39009026285) on the merged commit `adffefc7e0895e490cd9190998d3f93c4391d87b`, completed, success |
| **Merged Tree** | `PASS` | `check_merged_candidate.py --candidate 2544196 --merged adffefc --branch origin/main` PASS: the merge commit carries the candidate tree |
| **Tag Object & Resolution** | `PASS` | Ruleset 23728847 active on `refs/tags/v*`, forbids update and deletion, no bypass; preflight PASS; local `tagged` gate PASS before the push; remote annotated object and peel match the release commit (`tagged --check-remote` PASS) |
| **Pinned Fresh Install** | `PASS` | [39009276312](https://github.com/light-cheng/skills/actions/runs/39009276312), dispatched from main, source `light-cheng/skills#v0.2.10`: Codex and Claude Code project targets each 39 packages / 407 files, exact tag bytes |
| **Generic Latest Fresh Install** | `PASS` | Same run, source `light-cheng/skills`, separate project; default branch resolved to `adffefc`; Codex and Claude Code each 39 / 407 exact |
| **Native Codex Global Install** | `PASS` | Same run: real `--global --agent codex` into `/home/runner/.agents/skills`, 39 / 407 exact tag; HOME and CODEX_HOME not overridden |
| **Single Skills** | `PASS` | Same run: `light-implement` 6 files, `light-tdd` 5, `light-research` 3, each in its own fresh Codex project, exact tag |
| **GitHub Release Publication** | `PASS` | [v0.2.10](https://github.com/light-cheng/skills/releases/tag/v0.2.10), neither draft nor prerelease, marked latest, timestamp above; every body link resolves |

[Installed manifests](installation/result.json) and [commands](installation/commands.json) bind 6 scenarios, 8 destinations and 12 successful commands; [raw logs](installation/command-logs.zip) are kept. Skills CLI 1.7.2, distribution SHA256 `72f1805ea4f6c62b0532cb77a9f021e7930bb7ca962f87a3fbf985d1ada5d56d`. Observed CI and publication records: [candidate CI](candidate-ci.json), [release-commit CI](release-ci.json), [installation CI](installation-ci.json), [publication](publication.json).

Limits: no local real-Host smoke was run for this release; behaviour evidence for the changed Skills is the stage 7 rehearsal and its Codex and pi retest listed in the manifest. Installation evidence does not prove each Skill's behavior. `main` is protected by ruleset 25257670 (pull request and the `quality` check required, force pushes and deletion blocked, no bypass), so this receipt reaches main through a pull request. An unqualified install follows main; the tag keeps this snapshot.
