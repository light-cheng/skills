# 变更记录

[English changelog](CHANGELOG.md)

所有变更都必须记录在实际版本/tag 对应的条目中，不能因为文档已起草就提前宣称 release。

## 未发布

- `light-travelpage`：地理地图新增手绘风格（`map.style: "sketch"`）。地点保持真实方位，密集区域连同海岸线局部放大；箭头和步骤序号按每天的 schedule 生成，行程改了地图跟着变。可选 `map.region.landmarks` 和 `map.modeWords`。总览、每天路线和手册当天地图都使用它；未设置的地区保持原样。
- `light-travelpage`（行为变化）：手册改为四个章节：行程 · 预订 · to-do · 材料，启用账本时再加账本，编号按实际显示的标签排。单独的路线章节取消：全程总览图放在 to-do 顶部，`#route` 打开它；手绘行程每天的手绘地图放在行程旁。每天标题和日期条显示星期。长文字分层：可选 `schedule[].detail`、票务 `guidance` 逐行显示、住宿 `cancellationPoints`/`navigationPoints`、to-do 粗体标签和要点，空一行后的部分显示为出示卡片并带「复制」按钮（`metadata.localLanguage` 设定卡片语言）。新增可选 `preTrip.cashBudget` 现金表和 `on-site` 票种。口袋卡列出全部住宿，旅途中「今晚」排第一。上次保存还在重试时不能重复提交 to-do。`handbook-design.md` 要求每次改 JS 或 CSS 都同时改 `index.html` 里的 `?v=`。未启用 to-do 时，总览图保留一个没有标签的章节，`#route` 仍能打开。出示卡片的字体随卡片语言变化。来自九州行程。

## 0.2.10 — 2026-10-17

- 经 pull request 路径发布：准确候选的 PR CI、合并后树检查、合并提交上的 CI、受保护的 annotated tag 和发布源的新鲜安装均已验证；见[发布收据](docs/evidence/releases/v0.2.10/RELEASE_RECEIPT.zh-CN.md)。标签指向 PR #13 的合并提交 `adffefc`。
- v0.2.10 发布准备：README、CATALOG、INSTALLATION、MAINTENANCE（中英）改为 v0.2.10 版本快照，安装命令标为模板；在 `docs/evidence/releases/v0.2.10/` 新增发布说明与发布清单。
- 阶段 7 演练修复（mdlinks 样例，Claude Code 与 pi）：`review-loop` 只有写明审查者、已跑轮数和每轮报告的位置，才交出干净结果；`light-implement` 的报告新增 `Reviewer:` 与 `Evidence:` 两行，没有审查报告时写 `not run`，不能写 `converged`（pi 上曾在没跑审查者的情况下宣称收敛）。`light-implement` 在工单已是 `claimed`、或 `Blocked by` 中有未 `resolved` 的工单时报告 `BLOCKED`，与 WORKFLOW 原有规定一致。`light-redirect` 在整个 SPEC 和所有未完成工单中查找会与变更矛盾的段落；批准后按当前 Host 给出 `project-spec`/`project-tickets` 的确切调用写法，不再说它们"没安装"；写完提案和记录答复后刷新 `plan.html`。`clarify` 与 `project-clarify` 不把用户没选的默认项写进已决定列表。`project-retro` 说某事"在别处待决"时要引用记录它的文件，否则标为未记录。`light-html-plan` 每次刷新都做视觉检查，做不了就写明。
- Skill 调用写法（与 Host 无关）：`SKILL.md`、references 和 description 中的技能名去掉 Codex 的 `$` 前缀（例如写 `project-tickets`，不写 `$project-tickets`）。在 Claude Code 上，Agent 会把 `$project-tickets` 原样给用户，而这种写法在那里无效；现在由 Agent 按当前 Host 的写法给出调用方式。`manuscript-ops` 的交接示例从只写 Codex 写法改为按当前 Host 渲染的逻辑调用；Codex 自己的 `agents/openai.yaml` 提示保留 `$`，哈希冻结的 `recap` 不变。README、CATALOG、快速开始、包指南和工作流文档（中英）改写为不带前缀的技能名，并加一行说明 Claude Code（`/name`）与 Codex（`$name`）的写法。钉住 `$` 措辞的测试去掉了这部分断言。
- `project-retro`：description 末尾加一句 "Use after …" 触发句（project-review 给出结论后、发布后、长时间或摩擦多的会话后，或用户要求时）；已记入其 ATTRIBUTION。
- `release-workflow`（行为变化）：发布文档检查改为读取 `<!-- release-state: {...} -->` 字段块（view、version 或 stable、发布说明的验证标题、发布清单的 `written: preparation`、可选的 `install_commands: template`），不再要求“Release snapshot”“Preparation snapshot”、写明收据在 main 的句子或带“template”的标题等固定措辞，正文可以自由书写。检查仍会在正文中找出未观察到的安装或发布成功、会过时的候选状态，以及没有依据的稳定版本说法。当前 main 的公开页面带 `"view": "current"`；v0.2.9 及之前的发布说明、发布清单和标签保留原有写法。字段列表见 `references/DOCUMENT-STATE.md`。
- `release-workflow`：RELEASE-STAGES 写明如何把最终 main 的 CI 运行记录为 `--final-ci` 所需的观察文件（需要 `kind: observed`），以及在工作树中 `git switch main` 失败时怎么做；两者都是 v0.2.9 发布时发现的。
- `release-workflow`：`RELEASE-STAGES.md` 中的推送命令给 SHA 变量加了花括号（`"${CANDIDATE_SHA}:refs/heads/..."`）。在 zsh 中 `"$CANDIDATE_SHA:refs/..."` 会触发 `:r` 修饰符，推送错误的 refspec；这是第一次走 pull request 路径发布（v0.2.9）时发现的。新增测试保证参考文档中没有 `$VAR:` 写法。

## 0.2.9 — 2026-10-16

- 经 pull request 路径发布：准确候选的 PR CI、合并树检查、合并提交上的 CI、受保护 annotated 标签、实际发布源的新鲜安装，以及 Claude Code 和 pi 上的真实 Host 冒烟；见[发布收据](docs/evidence/releases/v0.2.9/RELEASE_RECEIPT.zh-CN.md)。标签指向 PR #8 的合并提交 `ae11283`。
- v0.2.9 发布准备：README、CATALOG、INSTALLATION、MAINTENANCE（中英）改为 v0.2.9 版本快照；在 `docs/evidence/releases/v0.2.9/` 新增发布说明与发布清单，并新增 [v0.2.9 迁移说明](docs/MIGRATION-v0.2.9.zh-CN.md)。
- **所有者名称（需迁移）：** GitHub 账号 `LightDevCoder` 已改名为 `light-cheng`。现行链接和安装命令改为 `light-cheng`：README、快速开始、INSTALLATION 与 MIGRATION-v0.2.6/7/8（各加一行改名说明）、包与工作流指南、`agent-config` 参考文档、`ask-light` 集合映射、`light-travelpage`、`decision-map` 示例、`manuscript-ops` 依赖契约、CI 中克隆 `agent-config` 的地址和页眉 SVG。`kanban-worker/references/api.md` 记录一次只改名称的冻结修订（`docs/evidence/namespace-v0.2.9/`）。`agent-config` 的 schema 快照从 `light-cheng/agent-config` 的 `08e2122` 重新复制（light-cheng/agent-config#2）。历史证据、`.scratch` 归档、已发布版本的变更记录和 `project-review` 的迁移历史保留旧名称；CATALOG 写明来源是已退役的 `LightDevCoder/release-workflow` 仓库。
- `release-workflow`（行为变化）：新增 `scripts/repo_identity.py`；发布脚本从 `--repo`、`GITHUB_REPOSITORY`、`gh repo view` 或 `origin` 取得仓库，不再写死所有者。实时检查（已发布的 Release、observations）和当前模式的收据只接受解析出的仓库，旧所有者不再通过；历史审计仍能读取改名前的收据。这取代了 v0.2.8 同时接受两个所有者的临时修复。新增 `scripts/check_merged_candidate.py`，检查合并后的 pull request 是否把经 CI 验证的候选树放到了 `main`。各阶段新增 pull request 路径和保护 `main` 的建议；从 `main` 触发 `release-installation` 工作流作为必需的安装证据；新增可选的真实 Host 冒烟（`claude -p` 发现加一次 `eli5` 调用）；Release 正文写到临时目录；只运行一次 `pytest`，不再同时跑 `unittest`；去掉对 `trash` 的依赖。新增 `references/BROKEN-RELEASE.md`：标记坏版本、发布下一个补丁版本、记入收据。`SKILL.md` 和参考文档改写为直白文字。

## 0.2.8 — 2026-10-16

- 已发布：准确候选 CI、受保护的 annotated tag 和实际发布源的新鲜安装均已通过；见[发布收据](docs/evidence/releases/v0.2.8/RELEASE_RECEIPT.zh-CN.md)。标签指向 `c522857`。
- v0.2.8 发布准备：README、CATALOG、INSTALLATION、MAINTENANCE（中英）改为 v0.2.8 版本快照；在 `docs/evidence/releases/v0.2.8/` 新增发布说明与发布清单。集合测试改为从目录推出包数，并接受"上一版本"一行，不再要求冻结的当前稳定版本表述。
- `light-travelpage`（行为变化）：可选 AI 助手可连接 OpenAI 格式（chat completions 或 Responses）和 Anthropic Messages API；删除专为 CPA 写的连接方式和本机地址。新增 `scripts/ai-setup.mjs`，由页面主人在部署时选服务和模型：从 `/models` 识别格式，没有模型列表时接受手填模型 ID，要求一次真实的工具调用，然后把 `AI_BASE_URL`、`AI_API_KEY`、`AI_MODEL`、`AI_API_FORMAT` 写入 `.dev.vars` 或 Pages secrets；key 来自 `AI_API_KEY` 或隐藏输入。公开开关为 `provider: off|on`（`openai` 仍读作 `on`），旧的 `OPENAI_*` 设置继续有效，旅行者不能选择模型、格式或地址。自建或本机网关归可选能力 `light-travelpage-gw`（单独仓库）；`tests/test_composition.py` 接受这一外部可选目标。
- `eli5`：description 改为"a non-technical explanation"，并排除"为读者改写文档"；触发率评测发现 pi 会在这类改写时加载它。7 个 Port、`eli5` 与阶段 3 能力在 Claude Code 和 pi 上的触发率结果见 `docs/evidence/maintenance/2026-10-16-trigger-eval/`。
- 证据：`light-decide`、`light-redirect`、`light-html-plan` 及其联合接入的准入记录移入 `docs/evidence/admissions/`，决策来源审查移入 `docs/evidence/maintenance/2026-10-16-decision-sources/`。新增 `scripts/check_evidence_paths.py`：为证据脱敏（`<repo>`、`<tmp>`、`~`、形似 key 的值），并在 v0.2.7 之后新增的证据仍含个人路径或形似 key 的值时失败；`docs/MAINTENANCE.md` 写明何时运行。
- 跨会话交接与批准记录（阶段 4）：`project-clarify`（以及推荐 `project-clarify` 时的 `clarify`）提议把交接存到 `.scratch/<feature>/clarify-handoff.md`，用户确认后才写；`project-spec` 只拿到 slug 时读这个文件。SPEC 新增 `Approval:` 行（谁、何时、用户原话；批准前写 `pending`），`project-tickets` 在 SPEC 的 `## Comments` 下追加一行 `Tickets approved`，`project-review` 把两者原样引作 Charter 的批准证据。`project-tickets` 不接受写着 `Approval: pending` 的 SPEC，遇到没有这一行的旧 SPEC 先问用户，并且在所有工单文件写完后才加 `Tickets approved` 行。`ask-light` 能识别只放着 `clarify-handoff.md` 的 effort 目录，并路由到 `project-spec`。`project-init` 的 tracker 契约和 `docs/agents/issue-tracker.md` 都列出了它们；重跑 `project-init` 即可补上。新增 `tests/test_handoff_contracts.py`（阶段 6），检查包与包之间的交接：每个产物的写入方和读取方指向同一个路径或字段（clarify 交接、SPEC、批准记录、`US-<n>`、实现报告、`Plan gap:`、`Cause:`、`changes/`、`decisions.md`、`plan.html`）；只有 `docs/agents/triage-labels.md` 列出的负责方会把工单设为 `claimed` 或 `resolved`；只有 `light-redirect` 按用户的答复把变更提案设为 `approved` 或 `rejected`；`project-init` 的 tracker 块使用同一组工单状态。`project-tickets` 的 Wayfinding 说明现在写明由谁认领、由谁 resolve。
- 项目流程（阶段 4–5 对齐）：software-feature 流程以可选的 `project-clarify` 开头，`light-code-review` 在 `light-implement` 内经 `review-loop` 运行；SPEC 用户故事编号为 `US-<n>`，工单验收项引用它们，Charter 的每条 `AC-<n>` 写明覆盖的故事和工单；`project-review` 的发现登记表写明 `review-loop` 的 state 与 severity 如何对应；`<feature>` 为 `.scratch/` 下的规范占位名，`<effort>` 作为别名仍被接受（`project-init`、`ask-light`）；`docs/agents/triage-labels.md` 列出工单状态值。
- 准入（新检查）：`scripts/check_skill_names.py` 与 `tests/test_skill_names.py` 在包名与 `docs/reference/external-skill-names.json`（固定版本的 mattpocock/skills、anthropics/skills 及各 Port 的上游）或私有 `skills-3rdParty` 检出（如存在）中的 Skill 重名时失败。`humanizer` 和 `eli5` 记为已接受：两者都是所有者自己的 Skill。
- **改名（需迁移）：** `resolving-merge-conflicts` 改名为 `light-merge-conflicts`，不再与 mattpocock/skills 原版同名。行为和调用方式不变；旧名没有别名。见 [v0.2.8 迁移说明](docs/MIGRATION-v0.2.8.zh-CN.md)。
- `eli5`（重写）：从零重写为所有者编写的 Skill，结构全新（一个核心意思、一个类比、说明类比在哪里不成立），听众表放在 `references/audiences.md`。删除之前迁移来的副本及其 `ATTRIBUTION.md`。名称和模型调用方式不变。
- `ask-light`（真实 Claude Code 运行中发现）：不传 `--host-name` 时，脚本从环境识别 Claude Code，不再默认当作 Codex，调用写法显示为 `/skill`。项目安装和另一个 Host 的全局安装里都有同一个 Skill 时，校验采用 ask-light 所在集合里的那份，不再返回 `BLOCKED`；其他位置的重复副本仍然阻塞。
- `ask-light`、`agent-config`（`decision_source.py`）：`Decision data` 表头行不再被读成取值 `off`；能识别 `Decision data — off`（长短破折号）和标题 `## Decision data` 下一行写值的写法。标题后接普通文字时仍按 `off` 处理（失败时关闭）。
- 判定来源（行为变化）：`ask-light` 与 `agent-config` 不再依赖 TypeSafe Jev。脚本只在项目 `Decision data:` 允许的范围内询问判定客户端；**没写这一行时只问本机上的模型，所以原来用托管 Jev 服务的项目会停止调用它，直到加上 `Decision data: third-party`。** 阈值从代码移到用户策略文件 `~/.config/light/decision-policy.json`；只有问题 id 在那里校准过，答案才会被采用，否则沿用确定性基准，答案按 light-decide 格式保留（ask-light 在 `decisions`，agent-config 在 `abstract_profile.decisions`）。没给项目根时，脚本从当前目录往上找最近的 `docs/agents/light-project.md`；`Decision data:` 写成四个值以外的任何内容都按关闭处理；私网地址只有策略文件写明时才算 `private-network`；调用失败不重试。`agent-config` 保留一条结构规则：降档时分数还要明确落在下一档里。改名：`use_jev` → `use_typed_decisions`，`jev_confidence` → `decision_confidence`，`--no-jev` → `--no-typed-decisions`，来源标记 `jev` → `typed-decision`；`ask-light` 去掉 shadow 模式（未校准的来源现在就是这样工作）。
- `agent-config`：`agent_config_recommend` 新增 `project_root`（命令行 `--project-root`）和 `decision_policy`，分档时读取项目的 `Decision data:`；不传时只问本机来源。`evals/jev` 改用新接口，用临时项目和评测专用策略运行（`--decision-data`），本机判定服务不需要 key。
- `light-decide`：找不到来源且确实有用时，提出一次设置（`references/setup.md`）：先探查，再问用户，再推荐云端 API 或本机跑得动的本地模型，需要人手做的步骤推荐 `light-wizard`。用户同意前什么都不开始；拒绝会被记住。
- `project-init`：移除 TypeSafe Jev 接入（`--jev`、`--no-jev`、`--agent-target`、`--auto-install-sdk`、key 与 SDK 设置、`references/skills_cli_conventions.md`）。用户给出时记录 `Decision data:`（`decisionData`）。
- `manuscript-ops`：评估脚本把 `light-decide` 对问题 `manuscript-ops/route` 的结果作为 `semantic_result` 接收，只有 light-decide 已采用时才用；校准移到用户策略文件，新输入不再需要 `semantic_policy`。旧快照保留原来的 `decide` 结果和策略，照原样重放。
- `ask-light`：工作流与导航模式、批准后的转换、结果记录移到 `references/`；`SKILL.md` 从 206 行减到约 140 行。
- 删除 `docs/architecture/jev-integration-contract.md`。

- 新增 Skill（共 39 个包）：`light-decide`（`thinking/`）在工作流内回答有界判断，用允许的判定来源或 Agent 自己判断，并记到 `.scratch/<feature>/decisions.md`；`light-redirect`（`project/`）在已批准的计划不再成立时把改动提案写到 `.scratch/<feature>/changes/`，并记录用户的答复；`light-html-plan`（`project/`）用 `.scratch/<feature>/plan.html` 一个离线页面讲清计划现状，`assets/` 自带视觉系统。三者都由模型调用、都是可选的：缺少时调用方照原样工作。
- 计划信号：实现报告新增 `Plan gap:`；`project-review` 的 `FAIL` 记录 `Cause: implementation | direction`。`light-implement` 和 `project-review` 遇到计划缺口或方向性失败时调用 `light-redirect`，`plan.html` 存在时刷新它；`project-spec`、`project-tickets` 应用已批准的改动提案并标为 `applied`。
- `project-init`：指令文件指针多一行常驻说明（已批准的计划不再成立时，先调用 `light-redirect` 再改其要求），tracker 契约写明 `changes/`、`plan.html`、`plan-history/`。已有项目重跑 `project-init` 即可补上。
- `decision-map`：等用户答复的改动提案放在 `Not yet specified`，答复后移到 `Decisions so far`。
- 发布检查：`verify_release_installation.py` 按 39 个包检查；已发布版本的清单按它自己的 tag 计数。
- 维护流程：增加审查分量。已准入包的日常改动只需本地测试和所有者真实使用；完整审查只用于新准入、调用方式/依赖/attribution 变化、可执行脚本和发布。`AGENTS.md` 改用短句和主动语态，保留全部规则，并新增写作风格规则。
- `humanizer`：模式清单（§1–§35）和误报检查原样移到 `references/patterns.md`；`SKILL.md` 保留改写规则和流程。
- `ask-light`：决策原则和证据读法原样移到 `references/routing-judgment.md`。
- `light-implement`：`AgentConfigResult` 的处理改为指向 `references/WORKFLOW.md`，不在 `SKILL.md` 里重复。
- 测试：`tests/test_composition.py` 不再断言关键词，改为检查组合图——目标存在、Skill 只调用可由模型调用的能力、路由名称真实、公开示例不用旧名。
- README：Matt Port 改为 12 个（含 `project-retro`），旧名 `implement` 改为 `light-implement`，对齐快速上手注释。
- 工单生命周期：`light-implement` 改文件前先写 `Status: claimed`；`project-review` 在 `PASS` 后把工单标为 resolved（`FAIL`/`BLOCKED` 时在评论里写明阻塞原因）。此前没有任何 Skill 负责 resolve，被阻塞的工单永远进不了 frontier。
- 实现报告：`light-implement` 在已认领的工单下追加实现报告（范围、fixed point、验证、审查剩余 findings）。`project-review` 重跑其中的验证，并把未解决的 findings 作为 `Previous findings` 读入，换新会话后实现阶段的 findings 也能进入终审。
- Jev 评测：`evals/jev` 的 fixture 仍用旧名 `implement`，已修正；agent-config 的 14 个场景改写为规范 Host 证据加用户确认的 Profile，重新检查配置正确性（model、topology、effort）。effort 标注改为跟随 Profile 确认的 effort 策略，并受 Host 支持值约束。
- `agent-config`：`agent_config_recommend` 不再把 Profile 的 effort 写进调用方传入的任务对象，同一任务再规划时不会沿用上一次的 effort。

- `manuscript-ops`：按文稿管理需求选择路线，单独确定内容审阅；保留旧 Project 快照，修复普通文档与提取来源登记，提供可选的宿主决策 MCP 判断。本地回归和独立验收证据与发布、全局安装事实分别记录。
- `release-workflow`：增加双语固定树快照、当前 main 和 Release 正文的版本与状态检查；绑定外部观察及最终 main CI，明确区分本地模拟。没有发布新版本或全局部署。

- `release-workflow`：每次推送前核对最终暂存产物及收据/归档链接；绑定准确候选和最终证明提交等待 CI 成功，交代失败、修复和文件历史红叉。同一阶段的完整修复先收齐审阅和全部产物，再一次最终提交/推送；候选与收据阶段以及真实推送后故障分别记录。保留发布历史及通知设置。

- 测试（发布前审计）：删除只钉措辞、只断言自己写入的夹具文字、只转调另一个测试，或把被测逻辑写在测试文件里的测试（`review-loop`、`generic-review`、`project-retro`、`light-implement`、`decision-map` 和 `project-review` 各 profile 的"行为"测试）。检查路径、字段、状态码和组合边的测试保留。新增一条全集合测试，检查包文件里没有本机主目录路径；包数改为从 `skills/*/*/SKILL.md` 推出，不再写在多处。
- `check_public_docs.py`（行为变化）：命中实现术语时只打印 `WARNING:`，不再让检查失败。目录状态词按整词匹配，"adapters" 不再算作 ADAPT。README 写了适配器数量而 `harness-support.md` 没写时报错，不再和内置的 10 比较。
- `clarify`、`project-clarify`、`socratic`：删除 `scripts/session_state.py` 和 `scripts/frontier.py`。Agent 从不运行它们，只有测试调用。澄清流程写在各包的 `SKILL.md` 和 `references/` 里。`manuscript-ops` 在项目交接前改为通过 `references/WORKFLOW.md` 检查 `clarify`，通过 `references/conversation-contract.json` 检查 `socratic`。
- 中文文档（发布前审计）：`SKILL_ADMISSION.zh-CN.md` 和 `docs/zh-CN/workflows/recipes.md` 改为完整翻译，不再是指向英文页的摘要。`REVIEW_POLICY`、`MAINTENANCE`、`INSTALLATION`、`CATALOG`、`first-party-composition`、`specialized-workflows` 补回缺少的规则、链接和示例。中文页面改为链接中文页面，0.2.1 条目补上缺少的 TravelPage 一行。
- `light-diagnosing-bugs`、`light-tdd`、`light-prototype`、`light-research`、`light-wizard`、`light-writing-for-agents`、`light-merge-conflicts`：`description` 写明对应的 mattpocock/skills 原版，并提示二者只装一个。`docs/INSTALLATION.zh-CN.md` 说明原因：两份触发说法相同，合并冲突 Port 还曾与上游同名。
- `ask-light`：`SKILL.md` 从 124 行缩到 73 行。会话流程保留各步骤和硬规则；校验范围、顾问式解释清单和"不得虚构状态"的例子移到 `references/routing-judgment.md`。行为不变。
- `project-review`、`agent-config`、`light-redirect`：缩短 `SKILL.md`（106→84、94→82、89→77 行）。重复的规则改为链接：companion 健康检查指向 `companion-contract.md`，脚本入口参数移到 `host-evidence-schema.md#script-entry`，redirect 的答复处理和手工编辑移到 `PROPOSAL.md`。行为不变。
- 来源记录：`project-retro` 不再声称有行为测试套件（已在审计中删除），并记下 `AWAITING_SELECTION` 工作流状态；`project-clarify`、`decision-map`、`socratic` 改用当前包名称呼其路由（`light-research`、`light-prototype`、`light-to-questionnaire`）。
- `humanizer`：记录 `references/patterns.md` 里哪些引用示例来自维基百科（CC BY-SA 4.0）。

## 0.2.7 — 2026-10-07

- 12个Skill名称增加 `light-`，同步包身份、界面来源、内部引用、ask-light路由/状态/发现、归属与双语迁移文档。保留其他24个名称、36个包及职责/调用权限。不提供旧名alias，不自动迁移全局安装。
- 独立候选验收、真实Codex选择器/来源调用、准确CI、受保护annotatedtag与真实Codex/Claude项目、Codex全局及新名称单包安装通过。main验证器修正实际CLI全局目录；不可变标签与包内容保留。见[发布收据](docs/evidence/releases/v0.2.7/RELEASE_RECEIPT.zh-CN.md)。

## 0.2.6 — 2026-10-05

- `light-travelpage`：采用已选的旅行手册、系统衬线标题、点击即切换的每日页面和可见路线栏目。当天地图与安排同页；选择地点自动展开整组，保留其他点位，切换日期收起旧展开。次级栏目只剩材料时提供直达入口。
- `light-travelpage`：统一登录页、地图及票据弹窗、账本控件与可选 AI 面板。功能名称统一为 to-do，保留原始资料文字、双语草稿、航班及酒店卡片、受保护的原件与共享记录 ID。
- `light-travelpage`：生成前尚未选择 AI 时询问，默认关闭。启用后通过受保护的服务端 Chat Completions/Responses 接入使用已有 to-do、票据状态和账本动作；旅行源资料与商家订单保持只读。保留原请求重试、未发送及新输入草稿，初始化异常可见。
- `light-travelpage`：修复空日期草稿初始化，使用 DAY 标签。保留有来源的地理轮廓、电脑端航班翻页和受鉴权保护的 PNG 票据预览及 PDF 原件；保留此前撤回和各版历史审阅记录。
- 发布检查：使用独立版本目录验证最新候选识别，准备新版本时不再被固定上一版本号的测试阻断。

## 0.2.5 — 2026-09-24

### 变更 — 路由可靠性与发布验证

- `agent-config` Python 路由要求规范、未过期的 Host 证据和匹配的用户确认 Profile；目标档位不可用时停止，`highest-supported` 遵循 Host 已证实的推理强度顺序。
- `ask-light --mode semantic` 与主路由共用证据约束和最终校验；重复工单编号、已领取工作、项目歧义和未知审阅新鲜度均失败关闭。
- 工单生产者共用编号空间。`manuscript-ops` 在通用 `project-init` 初始化后负责自己的 Profile/状态，运行时只检查依赖接口。
- `code-review` 输出双轴规范 Findings；旅行页生成校验与首次同步共用待办契约。
- 远端标签或 Release 查询失败阻断事实证明。CI 发现完整 Python 测试，运行 Node 测试和生成旅程构建；同步中英文集合文档。

## 0.2.4 — 2026-09-21

### 变更 — 发布完整性加固与 Git 对象严格绑定

- **Git 对象发布证据绑定：** 将发布清单与发布说明的校验直接绑定至不可变的 Git tree 对象快照（`candidate_commit` 与 `refs/tags/vX.Y.Z^{commit}`），彻底防止工作区未提交或未跟踪文件穿透门禁。
- **发布后收据快照严格隔离：** 发布收据中的准入包总数校验强制绑定至发布时不可变候选快照（`release_revision`），防止后续 `main` 分支包增减漂移污染已发布版本的事实证明。
- **Fail-Closed 单向 Tag Preflight 门禁：** Tag 预检默认校验 `origin` 远端状态，网络或鉴权失败时严格阻塞（`BLOCKED`）；本地或远端已存在 Tag 时严格阻断，确保单向、安全发布。
- **严格 Annotated Tag 校验：** 强制要求发布 Tag 必须为 Annotated Tag 对象（`git cat-file -t` 返回 `tag`），全生命周期拒绝 lightweight tag。
- **独立 TAGGED 阶段复审支持：** 明确 `check_receipt_absence_in_candidate` 在传入 `revision` 时仅检查 Git 快照，允许在完成 post-publication attestation 后重新执行 `stage=tagged` 复核通过，杜绝工作区收据干扰。
- **零 Traceback 结构化失败机制：** 审计校验分支与规范显示路径，确保所有异常或错误均以标准 `VerificationResult` 结构化返回，杜绝 Python 未定义变量 traceback。
- **公开文档质量门禁：** 全面统一 `README.md`、`CATALOG.md`、`INSTALLATION.md` 中英文术语及调用/状态对称性，去除 AI 写作痕迹。

## 0.2.3 — 2026-09-21

### 变更 — 发布证据生命周期与清单架构解耦

- **发布前清单与发布后收据分离：** 彻底解耦发布前不可变规格（`RELEASE_MANIFEST.md`，直接固化于 Release Tag 快照内）与发布后验证事实证明（`RELEASE_RECEIPT.md`，存于 `main` 分支）。
- **形式化六阶段发布生命周期模型：** 确立明确的状态流转架构：`PREPARED → CI_VERIFIED → TAGGED → INSTALL_VERIFIED → PUBLISHED → ATTESTED`。
- **v0.2.2 发布后事实证明与历史溯源追加：** 详细记录 v0.2.2 发布的历史事实、初始 CI 在浅检出环境下的失败根因以及后续纠正性提交（`0862a19...`）。
- **自动化发布完整性校验机制增强：** 在 `scripts/verify_release_integrity.py` 中增加对 v0.2.3+ 的清单校验及收据目标 commit 比对，并在 `tests/test_release_integrity.py` 中新增密封单元测试。

### 重构 — `project-retro` 正向指令风格与状态驱动架构

- **正向职责与流程指令表达：** 将面向 Agent 的指令全面调整为目标、职责、流程、信息流与状态转换驱动的正向表达。
- **建议动作生命周期状态机：** 显式定义复盘结论交付状态为 `AWAITING_SELECTION`；在人类用户做出显式选择后，将选定项流转为 `APPROVED_ACTION` 进而进入有界执行。
- **工程审计沟通：** 严格基于已验证的代码库事实、当前 HEAD 状态与测试结果展开，聚焦系统、流程、信息架构、防护栏与工具经济性。
- **已闭环经验隔离与顺畅运行处理：** 明确 `[CLOSED]` 结论代表已有持久防护机制保护的历史经验，保留于复盘事实中但坚决排除在 Suggested Actions 之外；无复发性系统摩擦的常规任务直接完成，不触发复盘。

## 0.2.2 — 2026-09-20

### 新增 — TypeSafe Jev System One 语义加速最终收敛（`ask-light`, `agent-config`, `project-init`）

- **`ask-light` 活跃消费者查询规划与有界语义路由：** 引入活跃消费者查询规划架构，Python 证据引擎独占工作流法定权威。Jev Choice 严格仅在多合法候选时（`len(allowed_actions) > 1`）发送；单一候选集自动跳过 Choice。有界 Noul 仅在存在活跃消费者时触发（关键歧义用于引导至 `project-clarify` 或在存在模糊实现请求时提示澄清；深度推理升级用于提示 `agent-config`）。彻底移除执行意图相关查询；Jev 绝不赋予工作流流转授权，零价值查询自动跳过。提供紧凑状态脱敏构建（<350 字符），杜绝源码与文件树泄露。
- **`project-init` 规范 Skills CLI 映射与 Jev 生态接入：** 增加可选交互式接入门禁（`--jev` / `--no-jev`）。完全遵循 `vercel-labs/skills` v1.7.0 CLI 规范 Agent 标识映射（`pi`, `claude-code`, `cursor`, `codex`, `antigravity`, `grok`, `hermes-agent`）与规范项目作用域（`.agents/skills` 适用于 Cursor、Codex 与 Antigravity；`.pi/skills` 适用于 Pi 等）。未支持环境（如 DSH）严格确定性 Fail-Closed（`TARGET_UNRESOLVED`）。安全凭据解析（优先环境变量，其次项目 `.env`），写入本地凭据前强制校验 `.env` 已加入 `.gitignore`；支持全局技能复用。
- **`agent-config` 抽象任务画像与临时非对称降级防御：** 引入跨厂商解耦的抽象任务画像（routine, standard, high）与推理需求评估（low, medium, high）。无标签泄露的独立干净评测，权威输入完全由代码独占。执行临时非对称降级防御策略（置信度 `>= 0.75` 且边界裕度 `>= 0.15`，策略状态：`PROVISIONAL`）。真实评测实证（AC-02）安全拦截临界降级提议（分值 0.41，置信度 0.59），正确保留标准基线档位（`claude-3-5-sonnet`）。
- **Fail-Closed 与零外部依赖平滑降级：** 采用软依赖机制；未配置 `TYPESAFE_API_KEY` 或离线时，所有技能优雅退回确定性规则基准，保持全量测试套件零回归。

### 新增 — 七大职责分类目录归整（36 个已准入 Skill）

- 将全部 36 个 Skill 收纳至 `skills/` 下的七大分类目录：`project/`, `thinking/`, `engineering/`, `review/`, `knowledge/`, `writing/`, `productivity/`。
- 丰富各分类中英文集合指南，更新源码发现、安装指引与 CI 验证，完全保留宿主端平铺安装（`<skills-root>/<name>/`）与官方 CLI 选装（`--skill <name>`）兼容性。

### 变更 — 发布完整性与 Release Tag 不可变性政策

- 正式确立自 v0.2.2 起的发布 Tag 永久不可变性政策：已发布的 Tag 绝不强制移动、绝不重指向、绝不重写代码边界。
- 阐明并修复了 v0.2.1 在 Jev 集成演进周期中因 Tag 重指向产生的发布溯源问题。发布证据见：[v0.2.2 发布收据](docs/evidence/releases/v0.2.2/RELEASE_RECEIPT.zh-CN.md)。

## 0.2.1 — 2026-09-16

*(发布溯源说明：v0.2.1 最初于 2026-09-16 在 commit `70a48ef4c81b9b9f40604a43f2914e5467be4269` [收据记录为 `cb17b17c8227b7d7211e4bf5b72223703d987d60`] 正式发布，包含 project-retro、light-travelpage 与 agent-config 的 Profile 架构重构。在随后的 Jev 集成加固迭代周期中其 Tag 曾被移动以跟随开发演进 [`6f9d173`，后至 `27f16e4`]。v0.2.2 为最终收敛的 Jev 集成确立全新的不可变发布边界。)*

### 新增 — project-retro 技能与工作流复盘集成（第 36 个包）

- **project-retro 技能：** 新增第一方模型调用（model-invoked）Skill，用于对已完成的项目或编码会话进行复盘，识别智能体环境、自动化守护线、文件导航、工具经济性、引导指令及运行信息中的具体改进点。移植并适配自 Matt Pocock 的 `retro`（`959a8e9f1edc3adbe2f7e3054bb6fbefa6696260`），完整保留归属，运行时完全自包含无外部依赖。
- **工作流终点自主复盘评估：** 在项目工作流终点（`project-review` 完成最终验收或 `release-workflow` 执行完成后），由 Agent 自主判断是否触发复盘。检查执行中是否存在摩擦信号（导航瓶颈、缺失自动化检查、规范歧义、引导指令膨胀、工具效率低、运行信息缺失），有摩擦时触发 `project-retro` 输出结构化建议，顺畅无阻时干净跳过，不产生任何干扰与 token 开销。

### 新增 — Light-TravelPage（第 35 个包）

- **Light-TravelPage：** 收录第 35 个第一方包 `light-travelpage`（模型调用）：移动优先旅行页面生成与展示，支持中英双语切换、航班/住宿卡片、区域地图生成、离线优先费用账本及 Cloudflare Pages/Functions/D1 协同多端同步。
- 保留上游 MIT 素材和固定版本 ATTRIBUTION；增加冲突/幂等恢复、严格校验和 34 项测试。
- 更新：中英文切换、航班与住宿卡片、区域地图、精致衬线字体，以及固定位置的行程菜单。

### 重构 — agent-config Profile 权威、执行配置与 Companion 运行时

- **Profile 权威驱动的执行配置器：** 将 `skills/agent-config` 重构为基于真实宿主能力证据与用户确认 Profile 档位（`routine`、`standard`、`high`、`review`）的执行配置器，映射为适配的执行拓扑（单模型/多模型 × 单次/拆票；Case A、B、C、D）。返回规范的 `AgentConfigResult`（`READY`、`NEED_INPUT`、`NEED_PROJECT_TICKETS`、`BLOCKED`、`UNSUPPORTED`）。
- **Profile 权威优于模型强弱猜测：** 彻底剔除启发式模型打分（`routing_rank`）与从模型名称猜测智能。档位绑定与推理需求完全由用户在 Profile 中确认，并对照宿主真实呈现的模型进行校验。
- **宿主中立推理与 Effort 精准解析：** 抽象推理策略直接解析为宿主真实支持的具体参数值（`supported_reasoning_efforts` 或 `reasoning_effort_hierarchy`），严禁凭空捏造未支持值。
- **Companion MCP 运行时与 10 个原生适配器：** 制定可选 Companion MCP 运行时契约（`protocol_version: 1`，8 个规范 MCP 工具：`get_setup_status`、`inspect_host`、`get_profile`、`save_profile`、`preview_configuration`、`apply_configuration`、`validate_configuration`、`reset_profile`），覆盖 10 种原生 Harness（Codex、Claude Code、Antigravity / agy、DeepSeek Harness / DSH、OpenCode、ZCode、Cursor、Grok Build、Hermes、Pi）以及通用 plan-only 回退（Pi MCP 需单独安装扩展）。Companion 运行时维护于 `LightDevCoder/agent-config`。在无 Companion 时保持纯计划模式正常可用。
- **Companion 健康度与 Setup Gate：** 增加 Companion 健康探测语义（`agent-config setup --check`、实时 MCP 传输协议版本、规范工具 schema 校验）与非阻塞 Setup Gate（`agent-config setup`、`NEED_INPUT` / `UNSUPPORTED`），支持显式宿主探测与先预览后应用的变更控制。
- **Skill ↔ Companion 集成闭环：** 下游工作流消费规范化 `AgentConfigResult`；`implement` 保持 agent-config 为可选增强而不阻塞独立执行；`ask-light` 将 setup 意图路由至 `agent-config setup`，同时严格保持就绪工单路由至 `implement`、复杂拆分路由至 `project-tickets`。
- **Pi 集成与 MCP 修复：** 纳入 Pi 适配器，明确扩展、版本、项目信任、provider/model 和 effort 证据边界。

### 变更 — 自主权边界与工作流完成度

- 明确 `tdd`、`clarify`、`implement`、`review-loop`、`manuscript-ops` 的授权复用与阶段完成边界。保留明确批准、调用、审阅轮数和独立验收要求；仅允许有证据支持的可选路由回退。[范围与验证](docs/evidence/maintenance/2026-09-16-autonomy-boundaries.md)。

## 0.2.0 — 2026-08-28

### 新增 — 33 包 Light 工作流架构

- **Project Workflow（7）：** `project-init`（重构为最小初始化）、`project-clarify`、`project-spec`、`project-tickets`、`implement`、`project-review`、`release-workflow`（自 `LightDevCoder/release-workflow` 迁移）。
- **Clarification & Research（7）：** `socratic`（核心引擎，来自 Matt `grilling`）、`clarify`（`grill-me`）、`project-clarify`（`grill-with-docs`）、`decision-map`（`wayfinder`）、`research`、`prototype`、`to-questionnaire`——以 `socratic` 为共享引擎。
- **Planning（2）：** `project-spec`（`to-spec`）、`project-tickets`（`to-tickets`）。
- **Execution（5）：** `agent-config`（新增，host-agnostic，参照 Sol Advisor）、`implement`（Matt `implement` → 通用执行器）、`tdd`、`diagnosing-bugs`、`resolving-merge-conflicts`。
- **Review（4）：** `review-loop` 重构为轻量引擎 + `generic-review`（新增默认 reviewer）+ `code-review`（Adapt）+ `project-review`（新增，拥有冻结 baseline 与最终 `PASS`/`FAIL`/`BLOCKED`，自旧 `review-loop` 迁移）。
- **Productivity & Communication（4）：** `handoff`、`wizard`、`wait-what`、`writing-for-agents`（Matt PORT）。
- **Learning（3）：** `eli5`（源自上游 `DreambigOu/ELI5` @ `a766623`，经临时迁移 fork `LightDevCoder/ELI5`）、`teach`（PORT）、`language-learning`（保留）。
- **Router（1）：** `ask-light` 最后重构为跨 33 Skill 的 Light Workflow Router。
- **Specialized Workflows（8）：** `manuscript-ops`、`kb-init`、`learn-anything`、`language-learning`、`kanban-worker`、`recap`、`eli5`、`release-workflow`——已做 standalone + composition 验证，仅在真实缺口处加最小 handoff。

合计 **34** 个第一方 Skill（见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)）——下文的 33 包架构之外新增 `humanizer`。

已批准的 Matt PORT（11 个）各带 `ATTRIBUTION.md` 且无上游运行时依赖：`research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`。保留上游行为；Light 变更限于运行时解耦与 handoff 串联。

### 新增 — humanizer skill（第 34 个包）

- **humanizer skill：** 新的第一方 model-invoked Skill，将带有 AI 痕迹的中英文文本改写为自然行文，且不改变原意。改编自 blader/humanizer `e2e92e7`（版本 2.11.2），模式册逐字保留；新增 Language routing 节与 `references/zh-adaptation.md` 薄中文适配层（破折号/标题大写/弯引号/连字符合成词的中文覆盖规则、其余模式的中文映射与中文 AI 高频词表、反编造守则、中文误报豁免）。中文词汇参考 MIT 许可的 op7418/Humanizer-zh（`91f3d39`）。经 full-path `review-loop agent-skill` 验收准入——第 1 轮 `PASS`，一个 minor 归属措辞 finding 已修复；证据见 [docs/evidence/admissions/humanizer/](docs/evidence/admissions/humanizer/README.zh-CN.md)。

### 变更 — 发布后加固（agent-config / implement / ask-light）

- **agent-config 宿主中立化重构：** 将 `agent-config` 重构为区分当前可执行模型与模型可选择性（`model_selection` / `per_agent_model_selection`）。对于具备当前可执行模型但缺少模型选择器或子代理的宿主环境，安全降级至单模型多代理或单模型单代理路径，不再返回 `BOUNDARY`。
- **implement 中 agent-config 用户显式自选：** 重构 `implement` 使其绝不自动调用 `agent-config`。当编排（角色拆分、并行、评审隔离）有实质帮助时，向用户提供显式选择；用户拒绝或在无模型选择能力的宿主上运行时绝不阻塞正常实现。简单的独立任务直接执行，不打扰用户。
- **ask-light 模型主导混合顾问重构：** 将 `ask-light` 重构为模型主导的工作流顾问，采用五阶段架构：（1）请求意图解析（模型），（2）项目/宿主事实收集（代码），（3）候选 Skill 理解（模型 + 紧凑目录元数据），（4）最终工作流判断（模型），（5）选择验证与转换（代码 + 宿主能力）。
- **规范项目流对齐：** 在 `ask-light`、配方、地图与文档中恢复 `project-clarify → project-spec → project-tickets → implement → project-review` 规范链路，移除了在 `project-tickets` 前插入 SPEC-review 门禁的逻辑。
- **严格作用域与验证安全：** 增加严格作用域词汇校验（`current-workflow`、`independent`、`standalone`）、显式 `Skill: none` 仅在真实 accepted 阶段允许通过的验证，以及显式批准跨轮次的作用域保留与缺失/非法作用域 fail-closed 机制。
- **受信任宿主能力证据：** 明确已批准用户调用转换的受信任宿主能力通道要求，拒绝模型/上下文 JSON 伪造与未验证布尔值，在缺少真实宿主通道时安全降级为渲染精确调用（`host-transition-required`）。
- **内容验证的澄清就绪性：** 增强澄清就绪性判定，要求具备生产者契约标识与目标（`readyFor: project-spec`）。
- **ask_light.py 证据服务：** Python 辅助程序现纯粹作为事实证据、目录、配方与验证服务（`ask-light-evidence/1`）。移除了 `PROJECT_STATE_INTENT_PATTERN` 及所有基于正则/taskKind/评分的语义路由权威。返回结构化事实（projectContract、currentEffort、spec、tickets、review、artifactSignals）与作用域硬约束，不返回任何确定性 Skill 推荐。
- **工作流模式：** 重构 `recipes_result`（`--mode workflow`），发布带有步骤可用性与 handoff 的规范配方，移除了确定性正则胜者选择；由模型进行语义选择并锚定至当前实际状态。
- **全方位回归测试套件：** 覆盖评审事务一致性、源码/实现新鲜度、软件三字段基线验证、当前 effort 解析、发现与来源检查、严格作用域验证及 `agent-config`/`implement` 关系测试的完整矩阵。

### 变更

- **治理：** `AGENTS.md` 明确权威参照（Matt Pocock Skills 用于 Skill 写作；Sol Advisor 用于 `agent-config`）与 14 条维护规则（检查上游、不重写成熟 Skill、不重设 PORT、`SKILL.md` 精简、supporting-files 披露、不统一包形态、组合优于复制、不重复架构等），不膨胀为 SPEC。
- **准入：** `docs/SKILL_ADMISSION.zh-CN.md` 允许 SPEC 授权的 Port（需 attribution、Light 集成且无上游运行时依赖，`Port ≠ 任意复制`）。
- **审查：** `docs/REVIEW_POLICY.zh-CN.md` 区分 `reviewer`（→ findings） vs `review-loop`（引擎） vs `project-review`（最终验收），与 [Reviewer 契约](docs/REVIEWER_CONTRACT.zh-CN.md) 同步；final-acceptance 已从 `review-loop` 迁至 `project-review`。
- **维护：** `docs/MAINTENANCE.zh-CN.md` 更新为真实流程（add/update/rename/remove/port/adapt + 文档/目录/测试/attribution 同步 + release handoff）。
- **安装：** `docs/INSTALLATION.zh-CN.md` 同步 33 包（当前分支 33，最后稳定版 `v0.1.6` 9 包），明确 Light 主流程运行时不需要 `mattpocock/skills` 或 `sol-advisor`。
- **工作流：** `docs/zh-CN/workflows/` 负责仓库级组合（`project-workflow.md`、`clarification-system.md`、`execution.md`、`review-system.md`、`specialized-workflows.md`——各讲 `entry → handoff → stop → optional`，不复制 Skill 内流）。
- **头图：** `README.zh-CN.md` 首行改为 `Assets/header.png`；可编辑遗留头图仍在 `skills/docs/assets/skills-header.svg` / `.png`。
- **测试：** 保留有效行为测试；将锁旧架构的测试更新为 33 包、组合 handoff 与头图/双语检查。

### 变更 — Lean 架构重构

- **SKILL.md 作为最小可执行接口：** 全量重构 Skill（`agent-config`、`ask-light`、`clarify`、`code-review`、`decision-map`、`generic-review`、`implement`、`project-clarify`、`project-init`、`project-review`、`project-spec`、`project-tickets`、`review-loop`、`socratic`）现在直接暴露核心执行行为，条件性格式/示例/专项指导保留在 Skill 自有的 supporting files。
- **组合优于复制：** `review-loop` 是轻量评审引擎；`project-review` 拥有最终 `PASS`/`FAIL`/`BLOCKED`；调用方只命名 Skill，不再复述其内部 runbook。
- **测试：** 非契约的字面措辞断言已放宽；根 discovery/composition 测试已更新为 `project-review` 作为最终验收命令。
- **规划状态：** 旧 `.scratch/light-skills-refactor/` 已归档/废弃；`.scratch/light-skills-lean-refactor/` 成为唯一活动规划集，含逻辑重构分析与实施 tickets。
- **Frozen 完整性：** 五个 Frozen Skills（`eli5`、`language-learning`、`kb-init`、`kanban-worker`、`learn-anything`）保持逐字节不变并通过 hash 验证。2026-08-27 用户明确修改活动范围：`recap` 删除说明性正文，只保留一条手动执行语句。

### 变更 — 功能闭环

- **ask-light：** 新增 Light 自有 33-Skill 语义地图，分离逻辑路由与 host availability；UI metadata 改为可选；generic root 不再作为第一方来源；补齐 Codex/Claude/通用调用展示；Python router 成为全平台测试实现，PowerShell 保留为兼容 launcher。
- **项目 bootstrap：** `project-init` 现在幂等写入 `docs/agents/light-project.md` 与 issue-tracker 契约；下游 Project Skills 只消费所需字段。preset 有歧义时必须简要比较并给出推荐。
- **澄清：** 一次 `$clarify` 调用可通过普通回复持续推进；Socratic 状态默认仅内部维护，对话在有依据时给建议，完成前必须确认共同理解；unknown routing 只归 `socratic`。
- **Review 所有权：** 轻量 reviewer packet 只归 `review-loop`；acceptance registry 与 verdict 归 `project-review`；migration reference 明确为历史材料。
- **测试：** 新增代表性 top routing、空仓库 bootstrap/rerun、clarification lifecycle、本地 pointer、所有权与历史/runtime 边界测试；通过行为测试消除已修复的 prose coupling，而非恢复旧措辞。
- **recap：** 根据用户明确修订，`SKILL.md` 现在只含必需 frontmatter 与一条手动 `$recap` 执行语句；输出当前 session 的一句简洁摘要，不替换或压缩对话历史。

### 变更 — 核心工作流与 Socratic 修复

- **ask-light 工作流顾问：** `ask-light` 现在检查项目与工作流证据，说明当前阶段，带理由推荐下一个 Skill，支持集合导航，无需调用方注入根目录即可发现 Light 根，区分第一方来源与同目录的第三方包，并在用户批准后安全转换（Codex 上直接执行是中间状态；未发布版本的最终行为以上文当前 Host 转换策略为准）。
- **Socratic 前沿轮次：** `socratic` 现在把完整的可行动前沿作为一轮带编号的独立问题提出，附选项与推荐，并接受 `1B, 2A, 3C` 这样的批量回复；`clarify` 和 `project-clarify` 使用相同的轮次交互。
- **project-init 可用性：** bootstrap 现在把声明的相关能力分为 `available`、`unavailable` 或 `unknown`，从不静默把 `unknown` 提升为 `available`。
- **Reviewer 所有权：** `review-loop/references/reviewer-contract.md` 是唯一的规范运行时契约；`docs/REVIEWER_CONTRACT.md`（及 zh-CN）现在是面向人的摘要与指针。
- **页头：** README 主图仍为 `Assets/header.png`，作为新的仓库页头图。

### 变更 — Review 基线完整性

- **ask-light 软件固定点：** `software` Profile 的 verdict 现在只有在当前树仍与 Charter 产出的 `- Fixed point:` 身份一致时才可消费，且只看所记录的实现窗口触及的路径；窗口内的未提交或已提交漂移会把旧 verdict 判为过期，转入 `review-stale → project-review`；窗口外的改动从不使其失效；固定点缺失、无法解析或无法界定（repository-first）时失败关闭（`review-freshness-unknown`）。
- **ask-light 目录基线：** Charter 引用目录来源时，整个目录就是被审查的基线——记录的修订之后在目录内出现的文件（包括未跟踪文件）现在会让 verdict 过期；被引用目录之外的未跟踪文件，以及只引用文件时的同级文件，仍视为无关。
- **project-review 产出方契约：** `references/profiles/software.md` 记录持久的双基线记录；Charter 模板（`acceptance-charter.md`）新增仅限 software 的 `- Fixed point:` 行，`init` 工作流把它与基线一起冻结。
- **测试：** 新增 11 个基于 Git 的回归测试（17 个用例），覆盖 §13/§14 矩阵：新鲜 PASS、实现的未提交/已提交改动、无关改动隔离、过期 FAIL/BLOCKED、固定点缺失/无法解析/无法验证、目录内已跟踪文件修改/删除、新的未跟踪子文件、目录外噪声，以及文件来源的同级隔离。

> 历史说明：本节所述固定点规则经审计为失败开放（监控改动文件集合，且身份可被挽救），
> 已在**任何发布之前**被下文"软件 review 基线契约"取代。本节原样保留，
> 因为审计记录必须显示早先规则声称了什么，而不是重新标注它。

### 变更 — 软件 review 基线契约（在任何发布之前取代上文的双值固定点规则）

人工审计在早先未发布的规则下复现了错误的 `accepted` verdict：审查 diff 未触及的、早已存在的范围内文件，以及 PASS 之后在组件内新建的文件，都逃过了新鲜度检查，因为监控集合来自窗口内的改动路径；格式错误的固定点被部分挽救（丢弃无效 token、去重重复项）；而把候选版本冻结进不可变的 Charter，与已授权的"审查 → 有界修复 → 复审"生命周期相矛盾。作为产出方 + 消费方契约修复，全程失败关闭：

- **三字段软件基线（产出方 `project-review`）：** Charter 冻结 `- Fixed point:`（恰好一个完整提交 SHA——不可变的代码审查基点；冻结实际起界定作用的提交，绝不是可变的分支名）和 `- Implementation scope:`（以 `';'` 分隔的仓库相对字面路径——已批准的软件 `In scope` 的机器投影；稳定的组件根，绝不从改动路径、扩展名或公共目录推断；无法验证的目标为 `BLOCKED`，任一无效条目使整个字段被拒）。最终候选版本不在 `init` 时冻结：每个持久的 `PASS`/`FAIL`/`BLOCKED` 都在 `verdict.md` 上记录 `- Reviewed implementation revision:`，因此合法的 C1→C2 修复可以重新绑定验收而不修改 Charter。
- **消费方新鲜度不变量（`ask-light`）：** 软件 verdict 只有在以下条件全部满足时才可消费：三个身份都严格解析（不挽救、不去重）；基点与最终修订不同、能界定最终修订，且范围内改动非空；在冻结的范围内，已跟踪、已暂存、已提交和未跟踪的新增内容都仍与被审查的修订一致。范围内漂移会让任何旧 verdict 过期（`review-stale`）；范围外改动仍视为无关；整库范围 `.` 有意在 README 改动时过期（没有隐藏例外）；旧格式记录从不被接受（`review-freshness-unknown`），需要重新运行 `project-review`。
- **测试：** 基于 Git 的矩阵重写为 22 个方法、约 45 个用例：§10–§14 新鲜度矩阵（范围内改动/早已存在/新增/删除、范围外隔离、单文件范围、整库范围）、严格的固定点与最终修订语法、包括有效/无效混合的范围校验、基点/最终修订关系检查、FAIL/BLOCKED 绑定、旧记录不兼容、§16 自我过期防护，以及强制的"审查→修复→PASS"生命周期绑定到 C2。
- **文档：** `project-review` 的 references（software profile、Charter 模板、workflow、证据协议、迁移说明）定义该契约；`ask-light` 的 discovery-contract 只保留简明的消费方摘要。

### 变更 — 持久基线加固（单例字段、无歧义身份、被忽略文件的完整性）

人工审计在 `52d8638` 复现了三类错误 `accepted`：重复的规范持久字段按"首个匹配胜出"被消费（重复或缺失的 `Profile` 会静默跳过软件新鲜度检查）；多候选的 `Source revision or identity` 值被挽救为第一个可解析的 SHA；被 `.gitignore` / `.git/info/exclude` 从 `git status` 中隐藏的文件逃过了目录来源与实现范围的新鲜度检查。已失败关闭地修复：

- **单例持久字段：** 产出方拥有的规范字段（Charter 中的 `Source:`、`Source revision or identity:`、`Profile:`、`Fixed point:`、`Implementation scope:`；verdict 上的 `Reviewed implementation revision:`）是单例字段——出现次数是有效性的一部分。恰好出现一次才解析；零次或多次（即使是完全相同的重复）都失败关闭为 `review-freshness-unknown` / `review-ownership-unknown`，与字段顺序无关。`ask-light` 从不对权威字段采用"第一个值胜出"。
- **无歧义来源身份：** `Source revision or identity` 只有在恰好携带一个无歧义、可在本地解析的 Git 提交时才可用；无效+有效、有效+有效、重复值或重复字段都失败关闭，不做部分挽救。非 Git 身份仍不被消费方支持（失败关闭，未变）。
- **被忽略文件的完整性：** 目录来源与实现范围的新文件检测现在使用 `git ls-files --others`（字面 pathspec，不带 `--exclude-standard`），因此范围内被忽略的文件会像其他新增内容一样让 verdict 过期。Git ignore 控制的是状态展示，而不是范围归属；单文件范围、只引用文件的来源和范围外路径保持原有的窄语义。
- **产出方文档：** `project-review` 的 references（Charter 模板、software profile、workflow）写明单例规则，以及被审查范围的完整性包括被 Git 忽略的文件；`ask-light` 的 discovery-contract 记录消费方摘要。
- **测试：** 新增 19 个基于 Git 的回归方法（ask-light 套件共 122 个）：单例出现次数矩阵（含顺序无关性，以及经真实路由路径的持久记录篡改）、来源修订歧义矩阵、被忽略文件矩阵（范围内/范围外、单文件、整库、目录来源的子文件），以及有效基线的正向对照。

### 变更 — 持久 review 事务一致性（charter.md + state.md + verdict.md）

人工审计在 `38f4f9b` 复现了错误的 `accepted` verdict：`state.md` 处于活动/非终态（READY、CRITIC、REPAIR、EVALUATE）、缺失，或已更新到新的 Charter 修订但仍保留之前的 PASS verdict。`ask-light` 现在把 `charter.md` + `state.md` + `verdict.md` 作为一个一致的 review 事务来评估：

- **必须有状态文件：** `state.md` 必须存在，并给出规范的单例字段（`Status:`、`Charter revision:`、`Profile:`）。字段缺失或重复时失败关闭为 `review-state-unknown`。
- **活动状态压过旧 verdict：** 活动的 review 状态（`INIT`、`READY`、`CRITIC`、`REPAIR`、`EVALUATE`）立即路由到 `project-review`（阶段 `project-review`）；之前的任何 `verdict.md` 都不具权威性，从不被接受。
- **终态 State/Verdict 一致：** 终态 review 状态（`PASS`、`FAIL`、`BLOCKED`）要求有一致的 `verdict.md`；冲突时失败关闭为 `acceptance-unknown`。
- **Charter 修订与 Profile 一致：** `state.md` 的 `Charter revision` 和 `Profile` 都必须与 `charter.md` 一致；不一致时失败关闭为 `review-state-unknown`。
- **测试与冒烟：** 新增 15 个测试方法（pytest 套件共 300 个测试，ask-light 套件 137 个），覆盖完整的事务矩阵、重新打开生命周期、Charter 更新生命周期、C1→修复→C2 生命周期，以及在真实持久状态上的 24 个手动冒烟场景。

### 变更 — 终态 review 事务身份绑定（State 与 Verdict 的 Round、强制的 Verdict 身份、唯一结论）

修复了 `d414a3b` 处的错误 `accepted` 缺陷：终态 State（例如第 2 轮 PASS）可能接受旧轮次的 PASS verdict（第 1 轮），因为 `Round` 未被绑定，且 Verdict 侧的 Charter 修订和 Profile 是可选的。完成了持久 review 事务契约：

- **Round 绑定（`state.md` + `verdict.md`）：** `Round` 是 `state.md`（缺失/重复/格式错误时为 `review-state-unknown`）和终态 `verdict.md`（缺失/重复/格式错误/不一致时为 `acceptance-unknown`）中强制的规范单例字段。规范的产出方语法（`1`、`2`、`round-01`、`round-01 (final)`）被解析为规范化的 review 轮次身份。
- **强制的 Verdict 身份：** `Charter revision:` 和 `Profile:` 是终态 `verdict.md` 上强制的单例字段；缺失、重复或不一致时失败关闭为 `acceptance-unknown`。
- **唯一的终态结论语义：** 终态结论集合（`PASS`、`FAIL`、`BLOCKED`）必须解析为恰好一个无歧义的结论；多个或相互冲突的结论（`PASS+FAIL`、`PASS+BLOCKED`、`FAIL+BLOCKED`、`PASS+FAIL+BLOCKED`）失败关闭为 `acceptance-unknown`。
- **安全的收尾顺序：** 产出方文档（`WORKFLOW.md`）明确规定失败安全的收尾顺序（`写当前轮次 verdict → 校验持久字段 → 把状态设为终态`），确保中间状态失败关闭。
- **测试与冒烟：** 新增 6 个测试方法（pytest 套件共 306 个测试，ask-light 套件 143 个），覆盖完整的事务身份矩阵、Round 不一致、Verdict 身份要求、终态结论唯一性、SPEC §14 重新打开轮次生命周期，以及 24 个手动冒烟场景。

### No-Redesign 验证

对 18 个 `NO REWRITE/PORT` 按 `git diff` 逐个检查（SPEC §26）：`manuscript-ops`、`kb-init`、`learn-anything`、`language-learning`、`kanban-worker`、`eli5`、`release-workflow`、`research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`——仅在真实集成需求处加最小 handoff/attribution。`recap` 是上文单独记录、经用户批准的例外。

### 发布证据

- 本重构未创建新版本、tag 或 GitHub Release。
- 上文的 `humanizer` 准入与发布后加固内容扩展了 `v0.2.0` 发布线；tag 已重指至 commit `e063753`，且对已发布仓库的全新安装验证通过（CLI `1.5.23`；整集合——34 个包、257 个文件逐字节一致——及单包 `humanizer`）——见 [INSTALLATION_VERIFICATION_ADDENDUM.zh-CN.md](docs/evidence/releases/v0.2.0/INSTALLATION_VERIFICATION_ADDENDUM.zh-CN.md)。
- Discovery/composition/link/hero/双语与包契约检查：见 `tests/` 与 `python -m unittest discover`。

## 0.1.6 — 2026-08-19

### 新增

- 第一方 `kb-init` Skill：正式版知识库初始化包替换之前未发布的草稿。新增扩展核心原则（决策 provenance、开放决策 surfacing、depth before settlement）、readiness 检查、人类导航设计、research contract、connection setup/validation、backup/recovery 语义，以及 38 个回归 eval 用例。按 owner 决定，它仍是仅 user-invoked。
- 针对 `kb-init` 更新 contract 测试与双语使用指南。
- v0.1.6 发布九包集合：v0.1.1 的五个包、`recap` 与 `language-learning`（v0.1.2）、`kanban-worker`（v0.1.6 中由 `light-kanban-worker` 改名；首次发布于 v0.1.4），以及 `kb-init`。

### 变更

- `light-kanban-worker` 改名为 `kanban-worker`。包目录、`SKILL.md` name/frontmatter、`agents/openai.yaml`、测试、指南、目录、README 与安装面统一使用 `kanban-worker`。v0.1.4/v0.1.5 历史记录保留旧名并附迁移说明。
- `kb-init` 保持 explicit-only：`SKILL.md` 中 `disable-model-invocation: true`，`agents/openai.yaml` 中 `allow_implicit_invocation: false`。
- README、目录、安装指南、维护基线、discovery 测试与双语指南从 v0.1.5 八包发布边界更新为 v0.1.6 九包发布。

### Release 证据

- Release tag：`v0.1.6`，commit `e8c3589031bbc1cb76d7f928761ce3f60ebea3e1`。
- GitHub Actions `collection-quality`：release commit 上 PASS（run `32232850422`）。
- 整集合与单 Skill fresh installs：通用 `latest` 与 pinned `#v0.1.6` 形式 PASS；见 [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.zh-CN.md)。
- Host discovery：[DISCOVERY_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.6/DISCOVERY_VERIFICATION.zh-CN.md)。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.6
- 最终收据：[RELEASE_RECEIPT.zh-CN.md](docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.5 — 2026-08-17

### 变更

- `light-kanban-worker` 现在明确禁止同一 `LIGHT_KANBAN_AGENT_ID` 的 scheduled run 重叠执行：同一 agent id 任意时刻至多一个 invocation 活跃，上一 run 仍活跃时触发的唤醒必须 skip；不同 agent id 仍可并发。atomic claim 边界被准确记录——它保护的是两个不同 worker 同时 claim 同一张 To Do，并不是同一 agent identity 多个 invocation 的并发锁；并发控制属于 scheduler / agent runtime（`max concurrent runs = 1` 或等价的 skip-while-active 设置），worker 不新增 lock process、heartbeat 或 lease service。
- 首次注册现在明确要求 ID + name + avatar：本地图片通过 `POST /api/avatars` 上传并使用返回的 `/api/avatars/...` 路径 claim；已存在的 agent id 复用服务器保存的 name/avatar，后续唤醒无需重复 avatar。全新 agent id 缺 name 或 avatar 时报 identity configuration missing，不 claim、不改动任何任务。
- `agents/openai.yaml` default prompt 更新为可完成首次注册的 one-shot 形式（Agent ID / Name / Avatar），全新看板也能注册新身份。

### 测试

- worker contract 套件新增调度边界规则：same-agent 不得重叠、不同 agent 并发允许、atomic claim 边界、scheduler 拥有并发控制、无常驻 lock service、首次注册身份、身份复用、缺身份不得改动任务、本地 avatar 上传路径。
- 新增对抗性 negative fixtures `overlap-allowed-variant.md` 与 `avatar-optional-first-registration.md`，各自只违反一条规则且必须被拒绝。
- behavior 套件新增 Scenario G（同 agent 并发唤醒：run #1 活跃时第二个 run 不得开始处理，经 scheduler-guard fixture 验证——Light-Kanban 自身不提供 run lease）与 Scenario H（无 avatar 的新身份：不 claim、不改动、明确配置失败；提供合法 avatar 后注册与 claim 成功）。Scenarios A–F 保持不变并继续通过。
- release evidence 工作流澄清：receipt 现在区分 pre-release gate（candidate 测试、准入、catalog 同步——`READY FOR RELEASE`）与 post-release verification（已发布 tag 身份、fresh install、host discovery、release CI），已发布 tag 中不再出现令人困惑的 `PENDING` 标记。

### 证据

- Release tag：`v0.1.5`，commit `a56aa9d98de0b941ee2282144bc7e756ef5e48bd`。
- GitHub Actions `collection-quality`：release commit 上 `PASS`（run `31985455493`）。
- 契约变更的 `review-loop agent-skill` 验收：完全独立的 PASS（findings F-001/F-002/F-003/G-001 已修复）—— [AGENT_SKILL_REVIEW.zh-CN.md](docs/evidence/releases/v0.1.5/AGENT_SKILL_REVIEW.zh-CN.md)。
- Fresh installs：整集合与单 Skill、通用 `latest` 与 pinned `#v0.1.5` 形式，CLI `1.5.22` —— PASS；安装包与 tag 逐字节一致且套件可独立运行。见 [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.zh-CN.md)。
- Host discovery：[DISCOVERY_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.5/DISCOVERY_VERIFICATION.zh-CN.md)。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.5
- 最终收据（pre-release gate + post-release verification）：[RELEASE_RECEIPT.zh-CN.md](docs/evidence/releases/v0.1.5/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.4 — 2026-08-16

### 新增

- 新的第一方 model-invoked Skill `light-kanban-worker`：每次 scheduled agent 运行最多处理一张 Light-Kanban 任务——稳定 agent identity、先检查自己持有的 in-progress 任务与 `reviewFeedback` 再领取新任务、原子 claim 带有限次冲突重试、workspace 校验（不可访问的 workspace 变成 `block` 并带具体原因）、`complete` 交回人工验收。worker 绝不 archive、accept、delete、recycle、unblock，也绝不循环或常驻进程。因其涉及网络/文件系统/看板状态副作用，走完整准入路径（`review-loop agent-skill`），不走纯提示型快速通道。
- worker 包的 contract 与 behavior 测试套件，包含 positive fixtures 与 negative fixtures（对抗性单规则 fixture 文件）及 frontmatter YAML 安全门。
- ask-light behavior 套件新增 outside-readable-path negative 场景。

### 变更

- 版本文档同步：v0.1.4 为当前稳定 release，v0.1.3 及更早版本保持历史记录。README、目录、安装指南、维护基线、discovery 测试与 CI 更新为八包集合。
- 修复 ask-light scanner 的 `Test-PathUnder` 路径比较（硬编码 Windows 分隔符），该问题使 collection-quality workflow 自 v0.1.3 Python 移植起在 ubuntu-latest 上失败。

### Release 证据

- Release tag：`v0.1.4`，commit `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`。
- GitHub Actions `collection-quality`：release commit 上 `PASS`（run `31962459531`）。
- 整集合与单 Skill fresh installs：`PASS`（CLI `1.5.22`，通用 `latest` 与 pinned `#v0.1.4` 形式）。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.4
- 整集合与单 Skill fresh-install 证据：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包级证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.4/TEST_SUMMARY.zh-CN.md)。
- 准入：[light-kanban-worker 证据](docs/evidence/admissions/light-kanban-worker/README.zh-CN.md)。
- scanner code-review：[CODE_REVIEW.zh-CN.md](docs/evidence/releases/v0.1.4/CODE_REVIEW.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见 [发布收据](docs/evidence/releases)。

## 0.1.3 — 2026-08-10

### 变更

- 测试工具链从 Windows PowerShell 迁移为跨平台 Python：21 个 PowerShell 测试文件替换为 18 个 Python 套件（collection discovery、header assets、quick start、ask-light contract、project-init contract 与 behavior、recap 两个 contract、language-learning contract、review-loop 五个 profile 的 contract 与 behavior 套件及协议 helpers），保留断言集。
- ask-light behavior 套件在所有 host 直接执行可移植 Python router；`scripts/ask-light.ps1` 仅保留为轻量兼容 launcher。
- CI 迁至 `ubuntu-latest`（bash + python）；新增 retired-boundary 与 无 PowerShell 测试检查。
- 文档更新为新测试文件名与跨平台手动 fallback 片段；治理措辞不变。

### 证据

- [docs/evidence/releases/v0.1.3/](docs/evidence/releases/v0.1.3)

## 0.1.2 — 2026-08-10

### 新增

- 为 v0.1.2 准备第一方、仅 user-invoked 的 `recap` Skill。用户显式调用 `$recap` 后只返回一行当前 session 总结；不会运行工具、继续任务、修改文件、压缩历史或调用其他 Skill。
- 为 v0.1.2 准备第一方、仅 user-invoked 的 `language-learning` Skill。它通过六种学习模式辅导任意目标语言——每日课程、即时卡片、对话练习、语法解码、进度测验与沉浸翻译——并在多次调用之间复用会话上下文与已学词汇，而不是每次都重新询问。
- 新增低风险纯提示型准入快速通道：仅适用于 owner-authored、manual-only、只输出文本、无工具/副作用/runtime executable/外部依赖的 Skill；只需一个 fresh Evaluator，不再要求额外 Critic 或 Standards/Spec review。
- 发布通用 `latest` 安装命令（`npx skills add LightDevCoder/skills --yes --copy --agent '*'`）作为标准安装路径，并保留 pinned `#v0.1.2` 形式用于可复现安装。`recap` 与 `language-learning` 均由 fresh independent prompt-only fast-track Evaluator `PASS` 准入，见各自[准入证据](docs/evidence/admissions)。

### Release 证据

- Release tag：`v0.1.2`，commit `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.22`，通用 `latest` 与 pinned `#v0.1.2` 两种形式均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.2
- 整仓与单 Skill fresh-install 证据：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.2/TEST_SUMMARY.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见 [发布收据](docs/evidence/releases/v0.1.2/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.1 — 2026-07-26

### 新增

- 五个第一方 Skill 的双语用户指南、已验证的 workflow recipes 和可运行大小的 Quick Start 示例。
- `docs/evidence/releases/v0.1.1/` release 证据目录，以及覆盖结构、metadata、链接、双语配对、包测试、退休引用和头图的 CI 检查。
- 显式 `$ask-light next` 与 `$ask-light workflow` 模式，包含 bounded recipe、availability gap、handoff 字段和不执行测试。
- 可编辑 SVG 与 1600 × 480 PNG 头图：平面叠层的 `LightDevCoder` / `/skills` wordmark 和 serif slogan。

### 修复

- 为 user-invoked 的 `learn-anything`、`ask-light`、`project-init` 补齐 `policy.allow_implicit_invocation: false` 及对应 frontmatter。
- 修正安装语义：无 fragment 的仓库来源遵循 CLI 默认 revision，发布后 `#v0.1.1` 才是固定 target tag。

### Release 证据

- Release tag：`v0.1.1`，commit `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.20`，均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.1
- 整仓与单 Skill fresh-install 目标记录：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.1/TEST_SUMMARY.zh-CN.md)。
- 五个包组成的集合仍可安装，`collection-quality` 检查已通过。`review-loop agent-skill` acceptance gate 的独立 evaluator 证据仍为 `BLOCKED`；这不影响一般安装或使用。准确证据边界见[发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.0 — 2026-07-23

- 建立第一方治理基础并准入五个第一方 Skill。
- 已发布于 https://github.com/LightDevCoder/skills。
- 稳定 tag：v0.1.0。
- v0.1.0 的整集合与单 Skill 安装命令曾针对 fresh destination 和已发布包内容完成验证；这份历史证据与 v0.1.1 release 证据一并保留。
- 历史命令：`npx skills add LightDevCoder/skills` 和 `npx skills add LightDevCoder/skills --skill review-loop`。
- 历史安装明细：[v0.1.0 摘要](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md#历史-v010-摘要)。
