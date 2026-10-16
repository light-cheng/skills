# light-cheng/skills v0.2.8 发布收据

[English receipt](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 准确候选 CI、受保护 annotated tag、真实发布源新鲜安装和正式 GitHub Release 均已验证。本收据在公开发布后首次于 main 创建，标签中没有收据。

| 字段 | 值 |
| --- | --- |
| **仓库** | `light-cheng/skills`（原名 `LightDevCoder/skills`，GitHub 会重定向旧名） |
| **发布版本** | `v0.2.8` |
| **发布 Tag** | `v0.2.8` |
| **Annotated Tag 对象** | `9c59b5823a89d3019afbd8043320b0fe5d1785e5` |
| **Tag 目标 Commit** | `c522857bd37a1f61fb1af9a4ae5e6892a949f06c` |
| **发布 URL** | https://github.com/light-cheng/skills/releases/tag/v0.2.8 （旧地址 https://github.com/LightDevCoder/skills/releases/tag/v0.2.8 会重定向） |
| **公开发布时间戳** | `2026-10-16T07:22:12Z` |
| **集合包数量** | 39 个已准入包，406 个包内文件 |
| **策略状态** | `PROVISIONAL` |
| **范围** | 新增三个 Skill（`light-decide`、`light-redirect`、`light-html-plan`）、决策来源脱离 Jev、项目流程记录、light-travelpage AI 支持 OpenAI 或 Anthropic 格式 API、改名为 `light-merge-conflicts`、eli5 重写 |
| **候选** | PR #7 在 main 上的合并提交；其树与已准备、已审查的 `1b67d24` 完全相同 |

| 门禁 | 状态 | 证据 |
| --- | --- | --- |
| **本地测试** | `PASS` | 在 `c522857` 上：586 pytest、编译、公开文档检查（默认与 `--tag v0.2.8 --stage prepared`）、证据脱敏；`prepared` 完整性检查 PASS；干净树导出后集合发现检查通过。工作副本中 unittest 211/212：唯一失败读的是 `.claude/worktrees/` 下未跟踪的旧工作树，不在提交的树里 |
| **GitHub Actions CI** | `PASS` | [38862458964](https://github.com/light-cheng/skills/actions/runs/38862458964) `collection-quality`，准确候选 `c522857bd37a1f61fb1af9a4ae5e6892a949f06c`，completed、success |
| **标签对象及解析** | `PASS` | 规则 23728847 对 `refs/tags/v*` 生效，禁止修改和删除，无绕过；preflight PASS；远端 annotated 对象与 peel 匹配候选（`tagged --check-remote` PASS） |
| **锁定版本全量全新安装** | `PASS` | [38890688595](https://github.com/light-cheng/skills/actions/runs/38890688595)，来源 `light-cheng/skills#v0.2.8`：Codex、Claude Code 项目目标各 39 包 / 406 文件，与标签逐字节一致 |
| **最新主干全量全新安装** | `PASS` | 同一运行中的另一项目，来源 `light-cheng/skills`；默认分支解析为 `c522857`；Codex、Claude Code 各 39 / 406 一致 |
| **原生Codex全局安装** | `PASS` | 同一运行：真实 `--global --agent codex` 写入 `/home/runner/.agents/skills`，39 / 406 与标签一致；未重设 HOME、CODEX_HOME |
| **单包安装** | `PASS` | 同一运行：`light-implement` 6 文件、`light-tdd` 5、`light-research` 3，各在新的 Codex 项目中安装，与标签一致 |
| **本机 Host 发现** | `PASS` | [本机记录](installation/local-hosts.md)：Claude Code 与 pi 从 `light-cheng/skills` 进行的锁定版、默认分支和 `light-merge-conflicts` 安装逐字节一致；Claude Code 2.1.296 与 pi 1.3.0 都从新项目看到了只在 v0.2.8 中存在的四个 Skill |
| **GitHub Release 发布** | `PASS` | [v0.2.8](https://github.com/light-cheng/skills/releases/tag/v0.2.8)，非 draft、非 prerelease，标为 latest，时间戳如上；正文链接全部可打开 |

[安装清单](installation/result.json)与[命令记录](installation/commands.json)绑定 6 个场景、8 个目标和 12 条成功命令；[原始日志](installation/command-logs.zip)保留。此前从旧名运行的 [38865970321](https://github.com/light-cheng/skills/actions/runs/38865970321) 结果相同，已[保留](installation/redirect-source/README.md)。Skills CLI 1.7.2，发行文件 SHA256 `72f1805ea4f6c62b0532cb77a9f021e7930bb7ca962f87a3fbf985d1ada5d56d`。实际 CI 与发布记录：[候选 CI](candidate-ci.json)、[安装 CI](installation-ci.json)、[发布](publication.json)。

仓库在发布前已从 `LightDevCoder/skills` 改名为 `light-cheng/skills`。main 上的安装命令改用新名；不可变标签里的发布说明和发布清单保留旧名，GitHub Release 正文已改为新名。原先要求旧账号名的发布检查现在只接受本仓库的新旧两个账号名；托管验证器从新名安装。包内容未改动。

局限：维护者机器上没有安装 Codex，Codex 只由托管安装目标覆盖，没有本机发现或运行证据。pi 的 print 模式只有在项目受信任（`--approve`）时才加载项目 Skill。安装证据不证明每个 Skill 的行为。`light-travelpage-gw` 不属于本次发布。不带版本的安装跟随 main；标签保留本快照。
