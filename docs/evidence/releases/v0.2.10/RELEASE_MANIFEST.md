# light-cheng/skills v0.2.10 Release Manifest

<!-- release-state: {"view": "manifest", "version": "v0.2.10", "written": "preparation"} -->

[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md)

**Preparation snapshot:** written on 2026-10-17 for the repository candidate on branch `claude/project-thread-r7zodw` (pull request #13). It freezes the scope and local evidence at preparation. Facts observed after preparation (pull-request CI, merge, tag, fresh installation, publication) belong in the release receipt created on `main` after publication; no receipt belongs in this candidate or its tag.

| Field | Value |
| --- | --- |
| **Release Version** | `v0.2.10` |
| **Expected Tag** | `refs/tags/v0.2.10` |
| **Release Identity** | `refs/tags/v0.2.10^{commit}` |
| **Release Scope** | Host-neutral Skill calls in packages and docs (#12); `release-workflow` reads `release-state` field blocks and its stage guide is corrected (#10, #11); project-flow fixes from the stage 7 rehearsal in `review-loop`, `light-implement`, `light-redirect`, `clarify`, `project-clarify`, `project-retro` and `light-html-plan` (#13) |
| **Collection Package Count** | 39 admitted packages (unchanged from v0.2.9) |
| **Policy Status** | Unchanged from v0.2.9 |
| **Tag Immutability** | Annotated tag permanently immutable after publication |
| **Current Base** | `origin/main` at `c5d2bd511a82fc8b788f4016b6b60c8a198c4845` as seen locally at preparation |
| **Previous Stable Snapshot** | `v0.2.9` at `ae11283bb0c943f1a27f4a32e1a1b5caba37c92c` |
| **Compatibility Baseline** | Names, responsibilities and invocation types of the 39 v0.2.9 packages kept; no migration |

## Local evidence at preparation

- Repository suite with release tags fetched: all pytest tests passed except the 2 skipped; public documentation check passed for `--tag v0.2.10 --stage prepared`.
- Stage 7 rehearsal on the mdlinks sample: the full flow from `project-init` to `project-retro` on Claude Code, and `clarify` to `light-implement` on pi, found five medium-or-higher problems.
- Retest of those five on Codex and pi at `183768b`: none recurred on either Host. One limit: on Codex the ticket-order check read an older global install, so the new `light-implement` line was exercised on pi only.
- Pull-request CI (`quality`) passed on the fix commits before this preparation commit.

## Subsequent release gates

Pull-request CI on the exact candidate, merge with a tree check, CI on the merged commit, tag protection and preflight, annotated tag identity, the hosted installation workflow, GitHub Release publication and post-publication attestation remain open.
