# light-cheng/skills v0.2.9 发布收据

[English receipt](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 经 pull request 路径发布：准确候选的 PR CI、合并提交的树检查、合并提交上的 CI、受保护 annotated tag、真实发布源新鲜安装、真实 Host 冒烟和正式 GitHub Release 均已验证。本收据在公开发布后首次于 main 创建，标签中没有收据。

| 字段 | 值 |
| --- | --- |
| **仓库** | `light-cheng/skills` |
| **发布版本** | `v0.2.9` |
| **发布 Tag** | `v0.2.9` |
| **Annotated Tag 对象** | `34ef01aaaced67f6877994c3cb15ea46cf8a00fa` |
| **Tag 目标 Commit** | `ae11283bb0c943f1a27f4a32e1a1b5caba37c92c` |
| **发布 URL** | https://github.com/light-cheng/skills/releases/tag/v0.2.9 |
| **公开发布时间戳** | `2026-10-16T12:35:17Z` |
| **集合包数量** | 39 个已准入包，407 个包内文件 |
| **策略状态** | `PROVISIONAL` |
| **范围** | 现行链接与安装命令改为 `light-cheng`；`release-workflow` 改进（从检出仓库取仓库名、pull request 路径、区分必需与可选安装证据并加入真实 Host 冒烟、坏版本处理指南）；`agent-config` schema 从 `light-cheng/agent-config` 重新复制 |
| **候选** | `b2f0e5320e393514c00bf0b6bd82c8e75426f7e1`（PR #8 head）；标签目标是它在 main 上的合并提交，树同为 `f2c7d0bbdffeeed967634a7739b0b4768e11592b` |

| 门禁 | 状态 | 证据 |
| --- | --- | --- |
| **本地测试** | `PASS` | 在候选树上：627 个 pytest 通过、2 个跳过；编译；公开文档检查（默认与 `--tag v0.2.9 --stage prepared`）；证据脱敏；`prepared` 完整性检查 PASS；干净树导出后集合发现检查通过 |
| **GitHub Actions CI** | `PASS` | PR 运行 [38899769096](https://github.com/light-cheng/skills/actions/runs/38899769096) `collection-quality`，准确候选 `b2f0e5320e393514c00bf0b6bd82c8e75426f7e1`，completed、success；合并提交 `ae11283bb0c943f1a27f4a32e1a1b5caba37c92c` 上的 push 运行 [38899915938](https://github.com/light-cheng/skills/actions/runs/38899915938)，completed、success |
| **合并后的树** | `PASS` | `check_merged_candidate.py --candidate b2f0e53 --merged ae11283 --branch origin/main` PASS：合并提交带着候选的树 |
| **标签对象及解析** | `PASS` | 规则 23728847 对 `refs/tags/v*` 生效，禁止修改和删除，无绕过；preflight PASS；远端 annotated 对象与 peel 匹配发布提交（`tagged --check-remote` PASS） |
| **锁定版本全量全新安装** | `PASS` | [38900111822](https://github.com/light-cheng/skills/actions/runs/38900111822)，从 main 触发，来源 `light-cheng/skills#v0.2.9`：Codex、Claude Code 项目目标各 39 包 / 407 文件，与标签逐字节一致 |
| **最新主干全量全新安装** | `PASS` | 同一运行中的另一项目，来源 `light-cheng/skills`；默认分支解析为 `ae11283`；Codex、Claude Code 各 39 / 407 一致 |
| **原生Codex全局安装** | `PASS` | 同一运行：真实 `--global --agent codex` 写入 `/home/runner/.agents/skills`，39 / 407 与标签一致；未重设 HOME、CODEX_HOME |
| **单包安装** | `PASS` | 同一运行：`light-implement` 6 文件、`light-tdd` 5、`light-research` 3，各在新的 Codex 项目中安装，与标签一致 |
| **真实 Host 冒烟** | `PASS` | [本机记录](installation/local-hosts.md)：本机 `#v0.2.9` 安装在 Claude Code 与 pi 目录中逐字节一致；Claude Code 2.1.296 列出全部 39 个并调用了 `eli5`；pi 1.3.0 从新项目的 `.agents/skills` 加载了 `eli5` |
| **GitHub Release 发布** | `PASS` | [v0.2.9](https://github.com/light-cheng/skills/releases/tag/v0.2.9)，非草稿、非预发布，标为 latest，时间戳见上；正文所有链接可用 |

[安装清单](installation/result.json)和[命令](installation/commands.json)覆盖 6 个场景、8 个目标和 12 条成功命令；[原始日志](installation/command-logs.zip)已保留。Skills CLI 1.7.2，分发包 SHA256 `72f1805ea4f6c62b0532cb77a9f021e7930bb7ca962f87a3fbf985d1ada5d56d`。观察到的 CI 与发布记录：[候选 CI](candidate-ci.json)、[发布提交 CI](release-ci.json)、[安装 CI](installation-ci.json)、[发布](publication.json)。

这是第一次走 pull request 路径的发布。发现并处理的摩擦：文档中的父提交检查拒绝了已合并 main 的候选分支，因此在准备候选前改为祖先检查；在工作树中 main 已在别处检出时不能 `git switch main`，因此发布检出改为分离到发布提交；在 zsh 中文档里的 `git push origin "$CANDIDATE_SHA:refs/heads/..."` 会失败，因为变量后的 `:r` 是 zsh 修饰符，所以改用字面 SHA 推送，命令现在给变量加了花括号（`${CANDIDATE_SHA}`）；pi 用 `--mode json` 的 print 模式一直等待 stdin，直到被停止。

局限：维护者机器上没有安装 Codex，Codex 只由托管安装目标覆盖。pi 自己报出的 Skill 列表不完整；证据是它加载的 `SKILL.md` 路径。`main` 没有分支规则集保护，建议加上。安装证据不证明每个 Skill 的行为。不带版本的安装跟随 main；标签保留本快照。
