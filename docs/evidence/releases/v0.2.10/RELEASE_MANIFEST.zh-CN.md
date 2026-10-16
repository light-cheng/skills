# light-cheng/skills v0.2.10 发布清单

<!-- release-state: {"view": "manifest", "version": "v0.2.10", "written": "preparation"} -->

[English Manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

**准备时快照：** 2026-10-17 为分支 `claude/project-thread-r7zodw`（pull request #13）上的仓库候选版本撰写。它冻结准备时的范围和本地证据。准备之后观察到的事实（pull request CI、合并、标签、新鲜安装、发布）写入发布后在 `main` 上创建的发布收据；候选版本和标签中都不包含收据。

| 字段 | 值 |
| --- | --- |
| **发布版本** | `v0.2.10` |
| **预期标签** | `refs/tags/v0.2.10` |
| **发布身份** | `refs/tags/v0.2.10^{commit}` |
| **发布范围** | 包和文档中与 Host 无关的技能调用写法（#12）；`release-workflow` 读取 `release-state` 字段块，阶段指南修正（#10、#11）；阶段 7 演练发现的项目流程修复，涉及 `review-loop`、`light-implement`、`light-redirect`、`clarify`、`project-clarify`、`project-retro` 与 `light-html-plan`（#13） |
| **集合包数量** | 39 个已准入包（与 v0.2.9 相同） |
| **策略状态** | 与 v0.2.9 相同 |
| **标签不可变性** | 发布后 annotated 标签永久不可变 |
| **当前基线** | 准备时本地看到的 `origin/main`：`c5d2bd511a82fc8b788f4016b6b60c8a198c4845` |
| **上一稳定快照** | `v0.2.9`：`ae11283bb0c943f1a27f4a32e1a1b5caba37c92c` |
| **兼容基线** | 保留 v0.2.9 全部 39 个包的名称、职责和调用类型；无需迁移 |

## 准备时的本地证据

- 拉取发布标签后的仓库测试：除 2 个跳过的测试外，pytest 全部通过；`--tag v0.2.10 --stage prepared` 的公开文档检查通过。
- 在 mdlinks 样例上的阶段 7 演练：Claude Code 走完从 `project-init` 到 `project-retro` 的完整流程，pi 走完 `clarify` 到 `light-implement`，共发现 5 个中级及以上问题。
- 在 `183768b` 上用 Codex 和 pi 复测这 5 个问题：两个 Host 上都没有复现。一个限制：Codex 上的工单顺序检查读到了较旧的全局安装，所以 `light-implement` 新增的那一行只在 pi 上验证过。
- 本准备提交之前，修复提交上的 pull request CI（`quality`）已通过。

## 后续发布关卡

准确候选版本上的 pull request CI、带树检查的合并、合并提交上的 CI、标签保护与预检、annotated 标签身份、托管安装工作流、GitHub Release 发布以及发布后的证明仍未完成。
