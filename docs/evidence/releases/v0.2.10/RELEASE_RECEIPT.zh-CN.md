# light-cheng/skills v0.2.10 发布收据

[English receipt](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 经 pull request 路径发布：准确候选的 PR CI、合并提交的树检查、合并提交上的 CI、受保护 annotated tag、真实发布源新鲜安装和正式 GitHub Release 均已验证。本收据在公开发布后首次于 main 创建，标签中没有收据。

| 字段 | 值 |
| --- | --- |
| **仓库** | `light-cheng/skills` |
| **发布版本** | `v0.2.10` |
| **发布 Tag** | `v0.2.10` |
| **Annotated Tag 对象** | `6c50145b35692caf31afa9577b5814b5d616e089` |
| **Tag 目标 Commit** | `adffefc7e0895e490cd9190998d3f93c4391d87b` |
| **发布 URL** | https://github.com/light-cheng/skills/releases/tag/v0.2.10 |
| **公开发布时间戳** | `2026-10-17T06:18:20Z` |
| **集合包数量** | 39 个已准入包，407 个包内文件 |
| **策略状态** | `PROVISIONAL` |
| **范围** | 包和文档中与 Host 无关的技能调用写法（#12）；`release-workflow` 读取 `release-state` 字段块，阶段指南修正（#10、#11）；阶段 7 演练发现的项目流程修复，涉及 `review-loop`、`light-implement`、`light-redirect`、`clarify`、`project-clarify`、`project-retro` 与 `light-html-plan`（#13） |
| **候选** | `25441969216409697eba86cf4d71670e6404fbde`（PR #13 head）；标签目标是它在 main 上的合并提交，树同为 `1625f87abcb5be47fa7b76ddf987d52e74010d4a` |

| 门禁 | 状态 | 证据 |
| --- | --- | --- |
| **本地测试** | `PASS` | 准备阶段证据见[发布清单](RELEASE_MANIFEST.zh-CN.md)；发布后在标签目标提交上：641 个 pytest 通过 |
| **GitHub Actions CI** | `PASS` | PR 运行 [38964270894](https://github.com/light-cheng/skills/actions/runs/38964270894) `collection-quality`，准确候选 `25441969216409697eba86cf4d71670e6404fbde`，completed、success；合并提交 `adffefc7e0895e490cd9190998d3f93c4391d87b` 上的 push 运行 [39009026285](https://github.com/light-cheng/skills/actions/runs/39009026285)，completed、success |
| **合并后的树** | `PASS` | `check_merged_candidate.py --candidate 2544196 --merged adffefc --branch origin/main` PASS：合并提交带着候选的树 |
| **标签对象及解析** | `PASS` | 规则 23728847 对 `refs/tags/v*` 生效，禁止修改和删除，无绕过；preflight PASS；推送前本地 `tagged` 检查 PASS；远端 annotated 对象与 peel 匹配发布提交（`tagged --check-remote` PASS） |
| **锁定版本全量全新安装** | `PASS` | [39009276312](https://github.com/light-cheng/skills/actions/runs/39009276312)，从 main 触发，来源 `light-cheng/skills#v0.2.10`：Codex、Claude Code 项目目标各 39 包 / 407 文件，与标签逐字节一致 |
| **最新主干全量全新安装** | `PASS` | 同一运行中的另一项目，来源 `light-cheng/skills`；默认分支解析为 `adffefc`；Codex、Claude Code 各 39 / 407 一致 |
| **原生Codex全局安装** | `PASS` | 同一运行：真实 `--global --agent codex` 写入 `/home/runner/.agents/skills`，39 / 407 与标签一致；未重设 HOME、CODEX_HOME |
| **单包安装** | `PASS` | 同一运行：`light-implement` 6 文件、`light-tdd` 5、`light-research` 3，各在新的 Codex 项目中安装，与标签一致 |
| **GitHub Release 发布** | `PASS` | [v0.2.10](https://github.com/light-cheng/skills/releases/tag/v0.2.10)，非草稿、非预发布，标为 latest，时间戳见上；正文所有链接可用 |

[安装清单](installation/result.json)和[命令](installation/commands.json)覆盖 6 个场景、8 个目标和 12 条成功命令；[原始日志](installation/command-logs.zip)已保留。Skills CLI 1.7.2，分发包 SHA256 `72f1805ea4f6c62b0532cb77a9f021e7930bb7ca962f87a3fbf985d1ada5d56d`。观察到的 CI 与发布记录：[候选 CI](candidate-ci.json)、[发布提交 CI](release-ci.json)、[安装 CI](installation-ci.json)、[发布](publication.json)。

局限：本次发布没有做本机真实 Host 冒烟；改动技能的行为证据是清单中列出的阶段 7 演练及其在 Codex、pi 上的复测。安装证据不证明每个 Skill 的行为。`main` 受规则集 25257670 保护（必须经 pull request 且 `quality` 检查通过，禁止强推和删除，无绕过），因此本收据经 pull request 进入 main。不带版本的安装跟随 main；标签保留本快照。
