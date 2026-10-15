# 第一方审查策略

[English review policy](REVIEW_POLICY.md)

本策略分配第一方 Skill 的审查角色和证据要求；静态检查、specialist finding 或 Producer 自报不能替代 final acceptance。

## Reviewer vs review-loop vs project-review

| 角色 | 是什么 | 做什么 | 绝不做 |
| --- | --- | --- | --- |
| **Reviewer**（`generic-review` · `light-code-review` · 领域 reviewer） | 只读 specialist；见 [运行时 reviewer 契约](../skills/review/review-loop/references/reviewer-contract.md) 或 [人类摘要](REVIEWER_CONTRACT.zh-CN.md) | 检查有界 target + requirements，返回规范化 `Findings: []` | 修复目标、指挥 Producer、改需求或签发 verdict |
| **`review-loop`** | 轻量收敛引擎 | 解析 reviewer、调用、收 findings、交回 Producer、重跑，干净或达 repair 上限时停止 | 拥有冻结 baseline 或项目最终 `PASS`/`FAIL`/`BLOCKED`（属 `project-review`） |
| **`project-review`** | 项目级最终验收拥有者 | 冻结 Charter/baseline、组合 reviewer（`generic-review`/`light-code-review`/领域）、经 `review-loop` 驱动收敛并签发最终 `PASS`/`FAIL`/`BLOCKED` | 替代 reviewer 方法或捏造缺失的验收标准 |

不要把最终验收塞回 `review-loop`。 reviewer 的 finding 只有经 acceptance owner 判断后才成为 verdict。

## 一项改动需要多重的审查

选最轻的那一行；拿不准时往重一档。

| 改动 | 要做的 | 可以省掉的 |
| --- | --- | --- |
| **日常改动**：已准入包的文字、示例、references 或行为，调用方式、依赖、attribution 和安装面都不变，也没有新增或修改可执行脚本 | 本地跑该包测试和全套测试；所有者在真实使用中试一遍；在 `CHANGELOG.md` 记一行。 | Charter、Critic、冻结 baseline、证据目录、独立 Evaluator。 |
| **仅文档**：README、目录、指南、治理文档 | 跑 `python scripts/check_public_docs.py` 和全套测试；检查链接和中英文对应。 | 上面全部。 |
| **完整审查**：新准入；改变调用方式、依赖、attribution 或安装面；任何可执行脚本、共享测试设施或安装器的改动；改名、弃用或删除 | 按下面的 Profile 表执行。 | 无。 |
| **Release candidate** | 其中每项完整审查改动的包级验收，加上 [维护](MAINTENANCE.zh-CN.md) 里的发布门禁。 | 无。 |

日常改动一旦发现涉及脚本、调用方式或依赖，就转为完整审查。所有者试用是真实使用，不能替代失败的测试。发布与已发布安装验证从不省略。

## Profile 与审查

| 变更 | 必需 final acceptance | specialist evidence |
| --- | --- | --- |
| 符合条件的低风险纯提示型 Skill | 按 [准入](SKILL_ADMISSION.zh-CN.md) 的快速通道，由一个新开的独立 Evaluator 审 | structure/metadata、隔离 copy/discovery、deterministic 正负 contract tests、显式调用/non-trigger、同步 docs；无 Critic 或 `light-code-review`。 |
| 新增第一方 Skill，或对其做完整审查级改动 | `project-review`（`agent-skill` Profile，经 `review-loop`） | structural、fresh-install、behavioral、invocation、attribution。 |
| 包含 executable script | `project-review`（经 `review-loop` + `light-code-review`） | focused/negative/adversarial tests 与 `light-code-review` findings。 |
| Skill 内的软件 artifact | `project-review` 拥有 verdict，`review-loop` 为引擎 | `light-code-review` 提供 Standards/Spec findings。 |
| 文稿/specification artifact | `project-review` 选 `manuscript`/`specification` Profile | artifact-specific 证据与 specialist findings。 |
| Release candidate | 包级验收 + Program 级验收 | verified release installation 与文档同步证据。 |

`generic-review` 为无 specialist 时的默认 reviewer。`light-code-review` 为有界 `git diff` 的 specialist（Standards + Spec），只读。

符合条件的纯提示型 Skill，其自包含的校验测试本身不触发"可执行脚本"那一行。如果测试会运行产品代码、共享辅助代码、安装器、hook、子进程、网络访问或其他运行时行为，就不能走快速通道，必须做专项审查。

## 证据与独立性

Producer Evidence 须写明精确命令、环境、输入输出、revision、范围与限制。 reviewer 按 [运行时 reviewer 契约](../skills/review/review-loop/references/reviewer-contract.md)（人类摘要：[REVIEWER_CONTRACT.zh-CN.md](REVIEWER_CONTRACT.zh-CN.md)）的输入包（`Target`·`Requirements`·`Relevant context`·`Previous findings`）返回 `id`/`severity`/`location`/`problem`/`reason`（可选 `suggestion`），绝不直接写 `PASS`/`FAIL`/`BLOCKED`。Producer 负责修复；Evaluator 须是新开且独立的。快速通道省略单独 Critic；完整路径需要一个新开的独立 Evaluator，依据冻结基线和可采信证据作出判断。

## Repair、verdict 与边界

`project-review` 仅对已确认、范围内、可在 repair 上限内收敛的 finding 要求 Producer 做有界修复；需改需求、改架构、多张新 ticket、缺 authority/environment/evidence 或 independent review 不可用时，以 `FAIL`/`BLOCKED` 停止。

最终 verdict 由 **`project-review`** 签发，绝不由 reviewer 或 `review-loop` 签发：

- **PASS：** 全部冻结条件与证据满足。
- **FAIL：** 范围内条件在 repair 窗口内未满足。
- **BLOCKED：** authority/environment/evidence/independent review 不可用。

仅有结构检查、keyword 匹配、模拟 fixture 或零断言测试时，不得声称 behavior/runtime proof。

## 记录与发布边界

保存冻结 source、reviewer findings、repairs、跨轮 evidence、最终 Evaluator 与 verdict；Skill 链接到准入证据，release/项目链接到受影响包记录与已验证安装证据。审查者只产出 `Findings: []`，结论由验收负责方给出。

Release、目录或安装命令在必需 verdict 与 checks 齐全前不得暗示已验收。见 [准入](SKILL_ADMISSION.zh-CN.md) 和 [维护](MAINTENANCE.zh-CN.md)。

历史说明：曾嵌在 `review-loop` 中的 final-acceptance 能力（`frozen baseline`、`PASS/FAIL/BLOCKED`、`scope-change boundary`）已迁移至 `project-review`（§25 Phase 7），`review-loop` 现为轻量引擎。
