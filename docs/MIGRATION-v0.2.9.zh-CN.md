# Light Skills v0.2.9 迁移说明

[English](MIGRATION-v0.2.9.md)

**状态：** v0.2.9 已公开发布。准确候选的 pull request CI、合并树检查、受保护标签和实际发布源的新鲜安装均已通过；见[发布收据](evidence/releases/v0.2.9/RELEASE_RECEIPT.zh-CN.md)。

## 仓库所有者名称已更改

GitHub 账号 `LightDevCoder` 现已改名为 `light-cheng`。仓库、tag 和内容都不变。GitHub 会把旧名称跳转到新名称，所以旧命令目前仍可用；但如果有人注册了旧账号，跳转就会失效。请更新你的命令和链接：

| 以前 | 现在 |
| --- | --- |
| `npx skills add LightDevCoder/skills` | `npx skills add light-cheng/skills` |
| `npx skills add LightDevCoder/skills#v0.2.8` | `npx skills add light-cheng/skills#v0.2.8` |
| `https://github.com/LightDevCoder/agent-config` | `https://github.com/light-cheng/agent-config` |

更新本地克隆：运行 `git remote set-url origin https://github.com/light-cheng/skills.git`。

没有包改名、新增或删除。已安装的 Skill 路径不变；可以不重装。

## release-workflow

如果你维护分叉并使用 `release-workflow`，它的脚本现在从 `--repo`、`GITHUB_REPOSITORY`、`gh repo view` 或 `origin` 找仓库，不再使用固定名称。分叉中有 `upstream` remote 时请传 `--repo owner/name`。候选版本现在通过 pull request 进入 `main`；见该 Skill 的 `references/RELEASE-STAGES.md`。
