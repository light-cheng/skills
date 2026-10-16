# light-cheng/skills v0.2.9 发布清单

[English Manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

**准备时快照：** 2026-10-16 为分支 `release/v0.2.9` 上的仓库候选写成，冻结准备时的范围与本地证据。准备之后观察到的事实（pull request CI、合并、标签、全新安装、公开发布）记入发布后在 `main` 上创建的发布收据；本候选及其标签中不放收据。

| 字段 | 值 |
| --- | --- |
| **发布版本** | `v0.2.9` |
| **预期标签** | `refs/tags/v0.2.9` |
| **发布身份** | `refs/tags/v0.2.9^{commit}` |
| **发布范围** | 现行链接与安装命令从 `LightDevCoder` 改为 `light-cheng`；`release-workflow` 改进（从检出仓库解析仓库名、带 `check_merged_candidate.py` 的 pull request 路径、区分必需与可选的安装证据并加入真实 Host 冒烟、坏版本处理指南、改写为直白文字）；`agent-config` schema 快照从 `light-cheng/agent-config` 重新复制 |
| **集合包数量** | 39 个已准入包（与 v0.2.8 相同） |
| **策略状态** | 与 v0.2.8 相同 |
| **标签不可变性** | 发布后注释标签永久不可变 |
| **实现依据** | `.scratch/release-v029/plan.md`（本地文件，不在标签中） |
| **当前基线** | 准备时本地所见 `origin/main` 为 `ec19ed68cb434cf7410df4a55b235244d167845a` |
| **上一稳定快照** | `v0.2.8`，提交 `c522857bd37a1f61fb1af9a4ae5e6892a949f06c` |
| **兼容基线** | 保留 v0.2.8 中 39 个包的名称、职责和调用方式；旧的 `LightDevCoder/...` 命令仍会跳转 |
| **配套仓库版本** | `light-cheng/agent-config`，提交 `08e212208b45059b4e82636f9b3c444354ae9efe`（light-cheng/agent-config#2） |

## 准备时的本地证据

- 仓库测试：627 个 pytest 测试通过，2 个跳过；公开文档检查通过；证据脱敏检查通过。
- `release-workflow` 脚本：`light-code-review`（两轮，合并 v0.2.8 后复查一次）和独立 Evaluator（两轮，复查一次）；发现的问题已修复，或在分支历史中说明理由后接受。
- 真实 Host 冒烟试跑：在全新目录运行 `npx skills add light-cheng/skills#v0.2.7 --agent claude-code`，再运行一次 `claude -p`（Claude Code 2.1.296）：安装的 36 个包都出现在会话的 Skill 列表中，且调用了 `eli5`。
- 配套契约测试（16 个）在固定版本的 `light-cheng/agent-config` 上通过。

## 后续发布关口

精确候选的 pull request CI、带树检查的合并、合并提交上的 CI、标签保护与预检、注释标签身份、托管安装工作流、Claude Code 与 pi 的真实 Host 冒烟、GitHub Release 公开发布以及发布后证明仍待完成。
