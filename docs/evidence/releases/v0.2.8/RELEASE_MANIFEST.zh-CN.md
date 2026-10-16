# LightDevCoder/skills v0.2.8 发布清单

[English Manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

**准备时快照：** 2026-10-16 为分支 `fix/ticket-handoff` 上的仓库候选写成，冻结准备时的范围与本地证据。准备之后观察到的事实（精确候选 CI、标签、全新安装、公开发布）记入发布后在 `main` 上创建的发布收据；本候选及其标签中不放收据。

| 字段 | 值 |
| --- | --- |
| **发布版本** | `v0.2.8` |
| **预期标签** | `refs/tags/v0.2.8` |
| **发布身份** | `refs/tags/v0.2.8^{commit}` |
| **发布范围** | 三个新的模型可调用 Skill（`light-decide`、`light-redirect`、`light-html-plan`）；决策来源脱离 TypeSafe Jev；项目流程交接记录（工单认领/resolve、实现报告、`Plan gap:`、`Cause:`、SPEC `Approval:`、保存的澄清交接）；`light-travelpage` 的 AI 支持 OpenAI 与 Anthropic 格式 API；`resolving-merge-conflicts` → `light-merge-conflicts`；`eli5` 重写；重名准入检查；证据脱敏检查 |
| **集合包数** | 39 个已准入包（v0.2.7 时 36 个，新增 3 个；改名 1 个） |
| **策略状态** | 判断阈值来自用户的 `~/.config/light/decision-policy.json`；默认没有任何校准 |
| **标签不可变** | 发布后带注释标签永久不可变 |
| **实现输入** | `.scratch/decision-provider/progress.md` 及其链接的已审设计（本地文件，不进标签） |
| **当前基线** | 准备时本地看到的 `origin/main`：`c03ab6ab8034e4a9208f76b2924ce4827cd5647a` |
| **上一稳定快照** | `v0.2.7`：`ef2d840b102df881bc8d6ae251af7db1ad3a21a7` |
| **兼容基线** | 保留 v0.2.7 中 36 个包的职责与调用类型（除一处改名）；旧版 `light-travelpage` 生成的页面保留其 `OPENAI_*` AI 设置；没有 `Decision data:` 的项目不再调用托管的 Jev 服务（见迁移说明） |

## 准备时的本地证据

- 仓库测试：586 个 pytest 测试通过；公开文档检查通过；v0.2.7 之后新增证据的脱敏检查通过。
- 准入与审查记录：[light-decide](../../admissions/light-decide/README.zh-CN.md)、[light-redirect](../../admissions/light-redirect/README.zh-CN.md)、[light-html-plan](../../admissions/light-html-plan/README.zh-CN.md)、[联合接入](../../admissions/joint-integration-v0.2.8/README.zh-CN.md)、[决策来源](../../maintenance/2026-10-16-decision-sources/README.zh-CN.md)。
- Claude Code 2.1.296 与 pi 1.2.0 上的触发率：[触发率评测](../../maintenance/2026-10-16-trigger-eval/README.zh-CN.md)。未运行 Codex。
- `light-travelpage` AI 改动：完整审查（Critic、`light-code-review`、新 Evaluator）；Evaluator 判定八条标准全部满足。准备时未运行真实 OpenAI/Anthropic 往返；模板测试 88/88，本地 Wrangler Functions + D1 在 Node 26.7.0 上对模拟上游运行。

## 后续发布关口

精确候选 CI、标签保护与预检、带注释标签身份、在 Claude Code、pi、Codex 上的固定标签与默认分支全新安装、完整的包/来源/内容检查、GitHub Release 公开发布及发布后证明仍待完成。每一步首次远端写入前都需要所有者批准。
