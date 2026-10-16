# v0.2.8 — 计划变更、判断与计划页

[English Release Notes](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

本版本快照 v0.2.8 把集合从 36 个 Skill 增加到 39 个，并收紧项目流程在各阶段之间的交接。[发布清单](RELEASE_MANIFEST.zh-CN.md)记录准备时的范围和本地证据；实际观察到的 CI、安装与发布事实记录在 `main` 上的发布收据中。

## 新 Skill

- `light-decide`（thinking）：在工作流中回答有边界的判断——在几个合法选项中选一个、回答是或否、给出等级——通过允许的决策来源或 Agent 自己的判断，并记录到 `.scratch/<feature>/decisions.md`。它从不决定批准、结论或权限。
- `light-redirect`（project）：已批准的计划不再成立时，在 `.scratch/<feature>/changes/` 写一份只有用户能批准的变更提案；由 `project-spec` 和 `project-tickets` 应用。
- `light-html-plan`（project）：用一张离线 HTML 页面 `.scratch/<feature>/plan.html` 展示计划进展，自带视觉系统。

三者都是可选能力：缺失时调用方保持原有行为。

## 你会注意到的变化

- **决策来源脱离 Jev。** `ask-light` 与 `agent-config` 不再调用 TypeSafe Jev。没有 `Decision data:` 一行的项目只使用本机模型。阈值移到 `~/.config/light/decision-policy.json`。`project-init` 不再配置 Jev。
- **项目流程记录。** 工单生命周期写明：`light-implement` 认领工单并追加实现报告（含 `Plan gap:`）；`project-review` 在 `PASS` 后 resolve，在 `FAIL` 时记录 `Cause:`。SPEC 新增 `Approval:` 行，工单图的批准也记入 SPEC；澄清交接可存到 `.scratch/<feature>/clarify-handoff.md`，供之后的会话使用。
- **light-travelpage 的 AI。** 可选助手可连接任何 OpenAI 或 Anthropic 格式的 API。页面主人在部署时运行 `scripts/ai-setup.mjs`，识别格式、选择模型并验证一次真实工具调用；旅行者不能更换模型。专为 CPA 写的配置已删除；v0.2.8 之前生成的页面继续使用其 `OPENAI_*` 设置。
- **改名。** `resolving-merge-conflicts` 改为 `light-merge-conflicts`，不再与 mattpocock/skills 原版同名。名字对应 mattpocock/skills 的 7 个 Port 在 description 里写明"二选一安装"。
- **eli5** 作为所有者自己的 Skill 从零重写。

## 升级说明

升级前请阅读 [v0.2.8 迁移说明](https://github.com/LightDevCoder/skills/blob/main/docs/MIGRATION-v0.2.8.zh-CN.md)：更新 `resolving-merge-conflicts` 引用；若项目依赖托管的 Jev 服务，添加 `Decision data: third-party`；重跑 `project-init` 补上新的 tracker 行。

## 安装

从实际 v0.2.8 发布源进行的新鲜安装已通过。锁定标签即可复现安装：

```bash
npx skills add LightDevCoder/skills#v0.2.8
npx skills add LightDevCoder/skills#v0.2.8 --skill light-decide
```

## 验证

准备时的本地证据列在[发布清单](RELEASE_MANIFEST.zh-CN.md)中。准确候选 CI 和受保护的 annotated tag 均已验证。在新的托管 Linux 用户上，Codex、Claude Code 项目的锁定版与默认分支全量安装、原生 Codex 全局范围和三个单包都与来源逐字节一致（39 个包、406 个文件）。本机 Claude Code 和 pi 安装同样一致，两个 Host 都从新项目发现了新 Skill；pi 需要项目受信任。维护者机器上没有安装 Codex。详情见 main 上的发布后收据。完整[变更记录](https://github.com/LightDevCoder/skills/blob/main/CHANGELOG.zh-CN.md)列出全部改动。
