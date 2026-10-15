# 工作流 Recipes

[英文版 recipes](../../workflows/recipes.md)

这些 recipe 是有边界的文档和验证素材。它们只描述显式交接，不建立固定流水线、永久状态机或自动的多 Skill 编排器。每个包的 `SKILL.md` 仍是行为的权威。

## 来源与共同规则

- **第一方（39 个）：** 本仓库全部 Skill——`project-init`、`project-clarify`、`project-spec`、`project-tickets`、`light-implement`、`project-review`、`release-workflow`、`socratic`、`clarify`、`decision-map`、`light-research`、`light-prototype`、`light-to-questionnaire`、`agent-config`、`light-tdd`、`light-diagnosing-bugs`、`light-merge-conflicts`、`review-loop`、`generic-review`、`light-code-review`、`light-handoff`、`light-wizard`、`light-wait-what`、`light-writing-for-agents`、`light-teach`、`eli5`、`language-learning`、`recap`、`learn-anything`、`manuscript-ops`、`kb-init`、`kanban-worker`、`ask-light`、`humanizer`、`light-travelpage`、`project-retro`、`light-decide`、`light-redirect`、`light-html-plan`，通过 `LightDevCoder/skills` 安装（见 [CATALOG.zh-CN.md](../../../CATALOG.zh-CN.md)）。
- **已批准 PORT：** `light-research`、`light-prototype`、`light-tdd`、`light-handoff`、`light-diagnosing-bugs`、`light-wizard`、`light-teach`、`light-wait-what`、`light-to-questionnaire`、`light-writing-for-agents`、`light-merge-conflicts` 是带 `ATTRIBUTION.md` 的自包含第一方包，运行时不依赖上游（Port 保留 Matt 的行为，Light 只改交接和解耦）。
- **Matt 的历史名称：** `grill-me` → `clarify`、`grilling` → `socratic`、`grill-with-docs` → `project-clarify`、`wayfinder` → `decision-map`、`to-spec` → `project-spec`、`to-tickets` → `project-tickets`。这些名称只用于来源说明，工作流步骤以上面的 Light 名称为准。
- **私有的第三方修改版：** 放在 `skills-3rdParty` 里的包。私有根目录不存在时，属于可用性缺口，不能借机编造替代方案。

`socratic` 是模型调用的引擎；`clarify` 是面向用户的轻量入口，`project-clarify` 是了解项目的入口，`decision-map` 是大型工作的决策地图。`clarify → socratic`、`project-clarify → socratic`、`decision-map → socratic` 都是组合关系，不是各自独立的步骤。

每一行都写明交接产物和停止条件。"用户调用"指必须由用户明确选择该 Skill；"模型调用"指 Host 可以按包的策略调用它。专项审查的发现永远不会变成最终结论；recipe 一旦走到验收，最终的 `PASS`、`FAIL` 或 `BLOCKED` 由 `project-review`（经 `review-loop`）给出。

## 1. 软件功能

**进入条件：** 一个软件功能或实现目标已有明确的结果、约束和验收方向。

| 顺序 | Skill | 调用方式 | 输入 → 输出 | 交接 / 停止（stop） |
| --- | --- | --- | --- | --- |
| 0 | `project-clarify`（可选） | 用户调用 | 未定的用户决定 → 澄清交接 | 决定已澄清时跳过。 |
| 1 | `project-spec` | 用户调用 | 目标、约束和已澄清的决定 → 可追溯的 SPEC | SPEC 产物；切工单前停下等用户批准。 |
| 2 | `project-tickets` | 用户调用 | 已批准的 SPEC → 按依赖排序的追踪工单 | 工单图；不自动启动 `light-implement`。 |
| 3 | `light-implement` | 用户调用 | 一张未被阻塞的工单 → 有界的 diff 和测试，发现经 `review-loop`（`light-code-review`）收敛 | 提交证据；在工单范围处停止。 |
| 4 | `project-review` | 模型调用，经 `review-loop` 加 `light-code-review`/`generic-review` | 实现、测试和发现 → 最终结论 | 持久的 `PASS`/`FAIL`/`BLOCKED`；`PASS` 时 resolve 工单；停止。 |
| 5 | `light-handoff` | 用户调用 | 已接受的结果或阻塞 → 收尾或续作记录 | 收尾产物；由用户决定是否续作。 |

**受阻条件：** 缺少验收授权、工单未获批准、依赖未解决，或没有独立的 Evaluator。**证据：** SPEC、工单图、提交、针对性测试、专项审查发现、`project-review`/`review-loop` 的状态和结论，以及 `light-handoff`。

## 2. 新项目初始化

**进入条件：** 项目需要一个经确认的最小起点，还没有选定完整的交付路线。

| 顺序 | Skill | 调用方式 | 输入 → 输出 | 交接 / 停止（stop） |
| --- | --- | --- | --- | --- |
| 1 | `ask-light` | 用户调用 | 目标、项目类型、任务种类、产物、阻塞、可用性、调用控制 → 一个下一步 Skill 或 recipe | 推荐；等用户批准后按调用策略处理（模型调用的可以开始；用户调用的目标渲染为下一次显式调用）。 |
| 2 | `project-init` | 用户调用 | 已确认的预设和目标根目录 → 最小的指令更新及校验 | 初始化报告；在澄清、SPEC、实现和审查之前停止。 |
| 3 | 用户选择的下一项能力 | 按包的策略 | 已确认初始化的根目录 → 下一个显式产物 | 用户在 `project-clarify`、`project-spec`、`manuscript-ops`、`learn-anything` 或 `project-review` 中选择；没有隐式串联。 |

**受阻条件：** 缺少根目录、预设不明确、备用方案未确认、指令冲突，或能力不可用。**最终权限：** 下一个 Skill 由用户选择；之后的验收归 `project-review`。

## 3. 文稿项目

**进入条件：** 文稿、手册、书籍或多语言项目在来源、格式、批次、审阅或生产上有风险。

| 顺序 | Skill | 调用方式 | 输入 → 输出 | 交接 / 停止（stop） |
| --- | --- | --- | --- | --- |
| 1 | `manuscript-ops` | 模型调用或手动进入 | 根目录、六个路由维度、来源 → 路线和 RoutingSnapshot | 走 Project 路线时，选一个探查交接后停止。 |
| 2 | 经 `clarify` 或 `decision-map` 使用 `socratic` 引擎 | 用户调用的入口 | 未定的决定或跨会话的不确定 → 已确认的决定或地图 | 只有用户明确续作后才回到 `manuscript-ops`。 |
| 3 | `project-init` | 用户调用 | 已批准的文稿简报 → 映射好的最小项目状态 | 初始化证据；停止并等待。 |
| 4 | `project-review init` | 模型调用或手动进入 | 已批准的简报和验收来源 → 冻结的 Charter | Charter 和状态；批准前不开始生产。 |
| 5 | `manuscript-ops resume` | 模型调用或手动进入 | 已批准的 Charter 和项目状态 → 批次、锁定的来源、格式、质检 | 由用户控制的锁定和续作边界。 |
| 6 | `project-review`（manuscript Profile） | 模型调用，经 `review-loop` | 冻结的候选稿或定稿和格式质检 → 最终结论 | 在 `PASS`/`FAIL`/`BLOCKED` 处停止。 |

**受阻条件：** 缺少根目录、依赖、能力、简报、Charter、渲染或往返转换的证据。**证据：** RoutingSnapshot、简报、Profile、来源/批次/格式记录、质检、锁定回执、`project-review`/`review-loop` 的状态和结论。

## 4. 从资料提炼可复用 Skill

**进入条件：** 资料里可能有一个重复出现、有证据支撑的方法，而不只是一次性事件。

| 顺序 | Skill | 调用方式 | 输入 → 输出 | 交接 / 停止（stop） |
| --- | --- | --- | --- | --- |
| 1 | `learn-anything` | 用户调用 | 资料和出处 → 内部 Method Contract 或明确的缺口 | 在 `method_contract`、`not_promoted` 或 `BLOCKED` 处停止。 |
| 2 | 确定性的包生成器 | 有契约后的显式构建步骤 | Method Contract → created/updated/no-op/duplicate/blocked | 在生成器给出的确切状态处停止；不隐藏重复归属。 |
| 3 | `light-writing-for-agents` | 可选的模型调用知识 | 已批准的契约 → 编写要点 | 只作知识参考，绝不是运行时依赖。 |
| 4 | `project-review`（经 `review-loop`） | 模型调用 | 完整的包和准入依据 → 验收结论 | 在准入之前、拿到结论时停止。 |
| 5 | 准入与集合同步 | 维护者的显式操作 | 已接受的包 → 目录、测试、发布证据 | 完成全新安装和发布关口后停止。 |

**受阻条件：** 方法字段缺失、占位符未填、调用证据矛盾、重复的包无人归属、资源缺失，或审查者不可用。**最终权限：** 包的验收归 `project-review`；进入集合归准入治理。

## 5. Skill 维护与发布

见 [docs/MAINTENANCE.zh-CN.md](../../MAINTENANCE.zh-CN.md) 和 [docs/REVIEW_POLICY.zh-CN.md](../../REVIEW_POLICY.zh-CN.md)：归属与复用门槛 → 有界实现 → 测试和对抗夹具 → 脚本有改动时做 `light-code-review` → `project-review` 结论 → 集合同步 → 全新安装与发现 → 发布、打 tag、收尾。归属不明、测试失败、缺少独立审查、安装未验证或中英文未同步时，结果为 `BLOCKED`。结构检查不是运行时证明。

## 6. Bug 诊断与最终审查

`ask-light workflow` 还有两个有界 recipe：可复现的 bug 和最终验收审查。Bug 路线是 `light-diagnosing-bugs` → `light-implement` → `light-code-review` → `project-review`（经 `review-loop`）；最终审查路线只有 `project-review` 一步。两者在缺少复现或验收授权时停止，或在最终的 `PASS`/`FAIL`/`BLOCKED` 处停止，绝不自动调用用户调用的 Skill。

## 7. 独立的会话摘要

`recap` 是单步、由用户调用的停止边界。用户明确选择 `$recap`；它只使用当前会话的上下文，只输出一行，不调用任何其他能力，然后停止。它不创建交接、不压缩历史、不继续执行，也不给审查结论。
