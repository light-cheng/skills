# light-cheng/skills v0.2.9 Release Manifest

[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md)

**Preparation snapshot:** written on 2026-10-16 for the repository candidate on branch `release/v0.2.9`. It freezes the scope and local evidence at preparation. Facts observed after preparation (pull-request CI, merge, tag, fresh installation, publication) belong in the release receipt created on `main` after publication; no receipt belongs in this candidate or its tag.

| Field | Value |
| --- | --- |
| **Release Version** | `v0.2.9` |
| **Expected Tag** | `refs/tags/v0.2.9` |
| **Release Identity** | `refs/tags/v0.2.9^{commit}` |
| **Release Scope** | Live links and install commands move from `LightDevCoder` to `light-cheng`; `release-workflow` improvements (repository resolved from the checkout, pull-request path with `check_merged_candidate.py`, required vs optional install evidence with a real-Host smoke, broken-release guide, plain-prose rewrite); `agent-config` schema snapshot re-copied from `light-cheng/agent-config` |
| **Collection Package Count** | 39 admitted packages (unchanged from v0.2.8) |
| **Policy Status** | Unchanged from v0.2.8 |
| **Tag Immutability** | Annotated tag permanently immutable after publication |
| **Implementation Input** | `.scratch/release-v029/plan.md` (local, not part of the tag) |
| **Current Base** | `origin/main` at `ec19ed68cb434cf7410df4a55b235244d167845a` as seen locally at preparation |
| **Previous Stable Snapshot** | `v0.2.8` at `c522857bd37a1f61fb1af9a4ae5e6892a949f06c` |
| **Compatibility Baseline** | Names, responsibilities and invocation types of the 39 v0.2.8 packages kept; old `LightDevCoder/...` commands still redirect |
| **Companion Revision** | `light-cheng/agent-config` at `08e212208b45059b4e82636f9b3c444354ae9efe` (light-cheng/agent-config#2) |

## Local evidence at preparation

- Repository suite: 627 pytest tests passed, 2 skipped; public documentation check passed; evidence redaction check passed.
- `release-workflow` scripts: `light-code-review` (two rounds plus a recheck after merging v0.2.8) and an independent Evaluator (two rounds plus a recheck); their findings were fixed or accepted with reasons in the branch history.
- Real-Host smoke trial: `npx skills add light-cheng/skills#v0.2.7 --agent claude-code` in a fresh directory, then one `claude -p` run (Claude Code 2.1.296): all 36 installed packages were in the session's Skill list and the run called `eli5`.
- Companion contract tests (16) passed against `light-cheng/agent-config` at the pinned revision.

## Subsequent release gates

Pull-request CI on the exact candidate, merge with a tree check, CI on the merged commit, tag protection and preflight, annotated tag identity, the hosted installation workflow, real-Host smokes on Claude Code and pi, GitHub Release publication and post-publication attestation remain open.
