# light-cheng/skills v0.2.8 Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md) · [Release Notes](RELEASE_NOTES.md)

Status: `VERIFIED` — Published with exact-candidate CI, a protected annotated tag, actual fresh released-source installations and a public GitHub Release. This receipt is first created on main after publication. The tag contains no receipt.

| Field | Value |
| --- | --- |
| **Repository** | `light-cheng/skills` (formerly `LightDevCoder/skills`; GitHub redirects the old name) |
| **Release** | `v0.2.8` |
| **Release Tag** | `v0.2.8` |
| **Annotated Tag Object** | `9c59b5823a89d3019afbd8043320b0fe5d1785e5` |
| **Tag Target Commit** | `c522857bd37a1f61fb1af9a4ae5e6892a949f06c` |
| **Release URL** | https://github.com/light-cheng/skills/releases/tag/v0.2.8 (old address https://github.com/LightDevCoder/skills/releases/tag/v0.2.8 redirects) |
| **Publication Timestamp** | `2026-10-16T07:22:12Z` |
| **Collection Package Count** | 39 admitted packages; 406 package files |
| **Policy Status** | `PROVISIONAL` |
| **Scope** | Three new Skills (`light-decide`, `light-redirect`, `light-html-plan`), decision sources without Jev, project-flow records, light-travelpage AI for OpenAI- or Anthropic-format APIs, rename to `light-merge-conflicts`, eli5 rewrite |
| **Candidate** | Merge commit of PR #7 on main; its tree equals the prepared and reviewed tree of `1b67d24` |

| Gate | Status | Evidence |
| --- | --- | --- |
| **Local Test Suite** | `PASS` | On `c522857`: 586 pytest, compile, public docs (default and `--tag v0.2.8 --stage prepared`), evidence redaction; `prepared` integrity gate PASS; clean tree export passes collection discovery. unittest 211/212 in the working copy: the one failure reads an untracked old worktree under `.claude/worktrees/`, not the committed tree |
| **GitHub Actions CI** | `PASS` | [38862458964](https://github.com/light-cheng/skills/actions/runs/38862458964) `collection-quality`, exact candidate `c522857bd37a1f61fb1af9a4ae5e6892a949f06c`, completed, success |
| **Tag Object & Resolution** | `PASS` | Ruleset 23728847 active on `refs/tags/v*`, forbids update and deletion, no bypass; preflight PASS; remote annotated object and peel match the candidate (`tagged --check-remote` PASS) |
| **Pinned Fresh Install** | `PASS` | [38890688595](https://github.com/light-cheng/skills/actions/runs/38890688595), source `light-cheng/skills#v0.2.8`: Codex and Claude Code project targets each 39 packages / 406 files, exact tag bytes |
| **Generic Latest Fresh Install** | `PASS` | Same run, source `light-cheng/skills`, separate project; default branch resolved to `c522857`; Codex and Claude Code each 39 / 406 exact |
| **Native Codex Global Install** | `PASS` | Same run: real `--global --agent codex` into `/home/runner/.agents/skills`, 39 / 406 exact tag; HOME and CODEX_HOME not overridden |
| **Single Skills** | `PASS` | Same run: `light-implement` 6 files, `light-tdd` 5, `light-research` 3, each in its own fresh Codex project, exact tag |
| **Local Host Discovery** | `PASS` | [Local record](installation/local-hosts.md): pinned, default and `light-merge-conflicts` installs from `light-cheng/skills` for Claude Code and pi byte-identical; Claude Code 2.1.296 and pi 1.3.0 both list the four v0.2.8-only Skills from the fresh project |
| **GitHub Release Publication** | `PASS` | [v0.2.8](https://github.com/light-cheng/skills/releases/tag/v0.2.8), neither draft nor prerelease, marked latest, timestamp above; every body link resolves |

[Installed manifests](installation/result.json) and [commands](installation/commands.json) bind 6 scenarios, 8 destinations and 12 successful commands; [raw logs](installation/command-logs.zip) are kept. A first run from the old name ([38865970321](https://github.com/light-cheng/skills/actions/runs/38865970321)) passed with the same results and is [kept](installation/redirect-source/README.md). Skills CLI 1.7.2, distribution SHA256 `72f1805ea4f6c62b0532cb77a9f021e7930bb7ca962f87a3fbf985d1ada5d56d`. Observed CI and publication records: [candidate CI](candidate-ci.json), [installation CI](installation-ci.json), [publication](publication.json).

The repository was renamed from `LightDevCoder/skills` to `light-cheng/skills` before publication. Install commands on main now use the new name; the immutable tag keeps its Notes and Manifest with the old name, and the Release body was updated to the new name. Release checks that required the old owner now accept both owners for this repository and nothing else; the hosted verifier installs from the new name. Package content was not touched.

Limits: Codex is not installed on the maintainer's machine, so Codex is covered by the hosted installation targets only, not by local discovery or runtime. pi print mode loads project Skills only with project trust (`--approve`). Installation evidence does not prove each Skill's behavior. `light-travelpage-gw` is not part of this release. An unqualified install follows main; the tag keeps this snapshot.
