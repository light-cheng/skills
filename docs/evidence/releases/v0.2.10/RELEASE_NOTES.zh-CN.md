# v0.2.10 — 适用于所有 Host 的技能调用与更可靠的项目流程

<!-- release-state: {"view": "notes", "version": "v0.2.10", "verification": "验证", "install_commands": "template"} -->

[English Release Notes](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

本版本快照 v0.2.10 仍是同样的 39 个 Skill。技能调用现在在所有 Host 上都能用，不再只适用于 Codex；项目流程也不再允许审查、计划变更或澄清声称比实际更多的结果。[发布清单](RELEASE_MANIFEST.zh-CN.md)记录准备时的范围和本地证据；实际观察到的 CI、安装与发布事实记录在 `main` 上的发布收据中。

## 你会注意到的变化

- **适用于任何 Host 的技能调用。** 包、description 和文档中的技能名去掉 Codex 的 `$` 前缀，由 Agent 按当前 Host 的写法给出调用（Claude Code 用 `/name`，Codex 用 `$name`）。以前 Claude Code 上的 Agent 可能让用户输入 `$project-tickets`，而这在那里无效。`manuscript-ops` 的交接示例改为逻辑调用。Codex 自己的 `agents/openai.yaml` 和冻结的 `recap` 保留 `$`。
- **审查证据。** `review-loop` 只有写明审查者、已跑轮数和每轮报告位置时，才报告干净结果。`light-implement` 的报告新增 `Reviewer:` 与 `Evidence:` 两行；没有审查报告时只能写 `not run`，不能写 `converged`。
- **工单顺序。** 工单已是 `claimed`，或它依赖的工单还没 `resolved` 时，`light-implement` 以 `BLOCKED` 停下。
- **计划变更。** `light-redirect` 在整个 SPEC 和所有未完成工单中查找会与变更矛盾的段落。批准后它按当前 Host 给出 `project-spec` 或 `project-tickets` 的确切调用，不再说它们"没安装"，并刷新 `plan.html`。
- **澄清。** `clarify` 与 `project-clarify` 只把用户选定的内容列为已决定；Agent 自己会选的默认项仍作为待定问题。
- **较小的修复。** `project-retro` 新增触发句，说某事"在别处待决"时要引用记录它的文件。`light-html-plan` 每次刷新都做视觉检查，做不了就写明。`release-workflow` 改为读取隐藏的 `release-state` 字段块，不再依赖固定的发布措辞；阶段指南补充了最终 CI 观察记录、工作树和 zsh 安全的推送命令。

没有新增、删除或改名的包，因此无需迁移。除了项目安装，也请更新全局安装（例如 `~/.agents/skills` 下的副本）：Host 可能先读到旧的全局副本。

## 安装

锁定 tag 可复现安装：

```bash
npx skills add light-cheng/skills#v0.2.10
npx skills add light-cheng/skills#v0.2.10 --skill light-implement
```

## 验证

准备时的本地证据，包括阶段 7 演练及其在 Codex 和 pi 上的复测，列在[发布清单](RELEASE_MANIFEST.zh-CN.md)中。Pull request CI、标签、新鲜安装与发布在准备之后观察，并记录在 `main` 上的发布收据中。完整的[变更记录](https://github.com/light-cheng/skills/blob/main/CHANGELOG.zh-CN.md)列出全部变化。
