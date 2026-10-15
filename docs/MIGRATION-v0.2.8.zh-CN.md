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
