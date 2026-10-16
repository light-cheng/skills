# Light Skills v0.2.8 迁移说明

[English](MIGRATION-v0.2.8.md)

**状态：** 候选版。v0.2.8 尚未发布；本页说明将要发生的变化。

## 改名的包

| 原 Light 名称 | 新名称 | 类别 | 调用方式 |
| --- | --- | --- | --- |
| `resolving-merge-conflicts` | `light-merge-conflicts` | engineering | 模型调用 |

旧名与 mattpocock/skills 的原版相同，两套集合都装时，一个包会覆盖另一个。行为、职责和调用方式都不变。旧名没有可安装的别名或包装。安装路径变为 `<skills-root>/light-merge-conflicts/`；源码路径为 `skills/engineering/light-merge-conflicts/`。

## 决策来源不再调用 Jev

`ask-light` 和 `agent-config` 不再调用 TypeSafe Jev。`docs/agents/light-project.md` 里没有 `Decision data:` 一行的项目，只使用本机判断。要使用有类型的决策来源，请写上 `Decision data:`，并通过 `light-decide` 配置来源（见其 `references/setup.md`）。

## SPEC 批准行

SPEC 现在在标题下用一行 `Approval:` 记录批准，`project-tickets` 会在 SPEC 的 `## Comments` 下加一行 `Tickets approved`。0.2.8 之前写的 SPEC 没有 `Approval:` 行：`project-tickets` 会问它是否已批准，答"是"就补上这一行。写着 `Approval: pending` 的 SPEC 先回到 `project-spec` 批准。存在 `.scratch/<feature>/clarify-handoff.md` 的目录会被 `ask-light` 当作一个新功能。若另一个功能目录里仍有生效中的 SPEC，`ask-light` 会继续路由到那个目录：在 `docs/agents/light-project.md` 写上 `Current effort:`，或把已完成的 SPEC 标为 superseded。重跑 `project-init` 即可给已有项目补上新的 tracker 行（`clarify-handoff.md`、批准记录）。

## light-travelpage 的 AI 连接

可选的 AI 助手现在可以连接任何使用 OpenAI 或 Anthropic API 格式的服务，专为 CPA 写的配置已删除。已部署的页面无需改动：`ai-config.json` 里的 `provider: openai` 读作 `on`，服务器也仍然读取 `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_API_STYLE`。生成的页面自带运行时，所以 v0.2.8 之前生成的页面仍只读 `OPENAI_*`；不要对它运行新的配置脚本（脚本会拒绝）。要让这次旅行用上新设置或 Anthropic：用 `create.mjs --ai on` 生成新项目，用 `update.mjs` 套用现有行程，部署到同一个 Pages 项目和 D1 数据库，再请页面主人在自己的终端运行 `node <skill>/scripts/ai-setup.mjs <项目> --base-url <地址>`：它会识别格式、让页面主人选模型、验证一次真实的工具调用，然后写入 `AI_BASE_URL`、`AI_API_KEY`、`AI_MODEL`、`AI_API_FORMAT`。新页面用 `--ai on` 代替 `--ai openai`（旧写法仍可用）。放在页面主人电脑上或 Tunnel 后面的网关，归单独的可选包 `light-travelpage-gw`。

## 升级之前

记下目标 Host 和它的 Skill 根目录。动已安装的 `resolving-merge-conflicts` 之前，先确认它的来源：打开它的 `SKILL.md` 和 `ATTRIBUTION.md`，或查看符号链接指向。Light 的副本会写明 `LightDevCoder/skills`，Matt 的原版不会。其他来源的包保持不动。

在项目提示、`AGENTS.md`、可用性声明、脚本、自动化任务和安装器的 `--skill` 参数里，查找指向 Light 包的 `resolving-merge-conflicts`。

## 升级步骤

1. 把固定的 tag 安装到你使用的 Host 范围。
2. 确认旧的 `resolving-merge-conflicts` 目录是 Light 副本，并保存其内容或链接指向之后，再删除它。
3. 把 Light 引用从 `resolving-merge-conflicts` 改为 `light-merge-conflicts`，例如 `$resolving-merge-conflicts` 改为 `$light-merge-conflicts`。
4. 刷新发现，确认 Host 列出的 `light-merge-conflicts` 来自 Light 源。

```bash
npx skills add LightDevCoder/skills#v0.2.8
npx skills add LightDevCoder/skills#v0.2.8 --skill light-merge-conflicts
```

## 恢复

升级失败时，停止使用新入口，恢复保存的副本或链接指向，必要时重新安装 `#v0.2.7`。恢复旧目录之前，先确认它不会覆盖 Matt 的同名包。
