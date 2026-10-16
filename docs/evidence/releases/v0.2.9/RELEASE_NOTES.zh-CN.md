# v0.2.9 — 新的所有者名称与更稳的发布流程

[English Release Notes](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

本版本快照 v0.2.9 仍是同样的 39 个 Skill。它把所有现行链接和安装命令改到改名后的 GitHub 账号，并让 `release-workflow` 运行得更安全。[发布清单](RELEASE_MANIFEST.zh-CN.md)记录准备时的范围和本地证据；实际观察到的 CI、安装与发布事实记录在 `main` 上的发布收据中。

## 你会注意到的变化

- **新的所有者名称。** GitHub 账号 `LightDevCoder` 已改名为 `light-cheng`。README、INSTALLATION、各迁移说明、包指南、快速开始，以及链接到本集合或其配套仓库的包（`agent-config`、`ask-light`、`light-travelpage`、`manuscript-ops`、`decision-map`、`kanban-worker`）都改用 `light-cheng`。旧命令仍会跳转，但请更新（见 [v0.2.9 迁移说明](https://github.com/light-cheng/skills/blob/main/docs/MIGRATION-v0.2.9.zh-CN.md)）。历史证据保留写成时的名称。
- **release-workflow。** 发布脚本从检出的仓库找仓库名，不再写死；实时检查只接受这个仓库。候选提交通过 pull request 进入 `main`，新增的检查证明合并后的提交带着经 CI 验证的同一棵树。安装证据写明必需的托管工作流，并新增可选的真实 Host 冒烟测试。新增一份指南，说明发布后发现版本有问题时怎么办。该 Skill 及其参考文档改写为直白的文字。
- **agent-config 配套仓库。** schema 快照从 `light-cheng/agent-config` 重新复制；只有 schema 的 `$id` 变化。

## 安装

在收据确认实际发布源之前，以下为模板：

```bash
npx skills add light-cheng/skills#v0.2.9
npx skills add light-cheng/skills#v0.2.9 --skill release-workflow
```

## 验证

准备时的本地证据列在[发布清单](RELEASE_MANIFEST.zh-CN.md)中。发布后 main 上的收据记录 CI、受保护标签、全新安装和公开发布。完整[变更记录](https://github.com/light-cheng/skills/blob/main/CHANGELOG.zh-CN.md)列出全部变更。
