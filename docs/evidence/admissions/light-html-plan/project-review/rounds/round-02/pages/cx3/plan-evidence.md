# 工具借用项目进度页：来源与检查

交付：`.scratch/tool-lending/plan.html`。本次按工单 02 的最新实现报告刷新，保留原设计。旧页已逐字节归档至 `.scratch/tool-lending/plan-history/20261010T111215349030Z-plan.html`。
页面的记录截至 2026-10-10；更新时间及 11 个来源的路径、记录日期、SHA-256 均写在页面的“来源”分区。

## 来源与页面对应

| 原记录 | 保留的要求或事实 | 页面位置 | 核对 |
| --- | --- | --- | --- |
| spec.md · Approval / Goal | 用户 2026-10-02 批准；网页替代纸质工具借用登记 | #what | 已保留 |
| spec.md · R1 / A1 | 在库、借出、应归还日期；20 件工具核对 | #what / #ticket-01 | 已保留 |
| spec.md · R2 / A2 | 一个取用日，提前至多 7 天；同工具同日一笔；重复时明确拒绝 | #what / #ticket-02 | 已保留 |
| spec.md · R3 / A3 | 每笔次日到期借用，前一晚发一次邮件 | #what / #ticket-03 | 已保留 |
| spec.md · R4 | 志愿者用手机登记；1 分钟内显示可借 | #what / #gap-r4 | 明确显示无工单、无执行证据 |
| spec.md · Out of scope | 不做逾期费用、押金、配送 | #what | 已保留 |
| issues/01 · Status / Blocked by | resolved；无依赖 | #ticket-01 | 已验收；不推导项目验收或发布 |
| issues/01 · Implementation report | 2026-10-05 done；页面与导入；20/20 一致；无剩余问题 | #ticket-01 | 已保留 |
| issues/01 · Answer | PASS 指向 2026-10-06 verdict | #ticket-01 / #src-verdict | 已核对目标和状态 |
| .project-review/state.md / verdict.md | 均为 PASS，目标仅工单 01；Charter revision 1、Round 1 相同 | #ticket-01 / #sources | 验收有效，仅限工单 01 |
| issues/02 · Status / Blocked by | claimed；依赖 01，01 已解决 | #ticket-02 | 已保留 |
| issues/02 · Implementation report | 最新 2026-10-10 done；表单、存储、拒绝逻辑及提示均已写完；同工具同日第二笔被拒绝，提示原文可查；原有 5 笔预约仍保留；无剩余问题 | #ticket-02 / 首屏 | 已保留，显示已写完、待验收；7 天窗口无专项验证记录；claimed 状态未改 |
| issues/03 · Status / Blocked by | open；依赖 02；无实现报告 | #ticket-03 / #decide | 依赖仍为 02；说明 02 已写完但未验收；不归因于短信决策 |
| changes/01 · Trigger / Comments | 14 → 7 天；用户 10-04 批准；project-spec / project-tickets 当日应用 | #changed | 已保留 |
| changes/01 · Not changed / Open decisions | R1、R3、R4 不变；无待决策项；Charter / Accept again 为 none | #changed | 已保留 |
| changes/02 · Trigger / Status | 用户反映一半成员不看邮件；10-09 提出，proposed，未批准 | #decide / #changed | 已保留 |
| changes/02 · Change / Open decisions | 增加短信及工单 03 验收项；拟新增 04 账号；所有有手机号成员或主动订阅者 | #what / #decide / #changed | 已保留，04 不当作已存在工单 |
| changes/02 · Not changed / remaining fields | R1、R2、R4 不变；Charter / Accept again 为 none | #changed | 已保留 |
| decisions.md · 2026-10-08 row | yes，0.58，local-decider，本机数据；未校准、applied=false；final=no | #judged | 原始字段可展开；未采用的判断排在前面 |
| decisions.md · 2026-10-09 row | Agent 自行判断短信为计划变更，applied=true；final=yes；无置信值 | #judged | 不编造置信值 |
| docs/agents/issue-tracker.md / AGENTS.md | 项目记录位置，稳定 HTML 路径和历史目录 | #sources / 刷新交接 | 已保留 |

## 本次变更

- 工单 02 改为“已写完、待验收”；写完日期为 2026-10-10，验收和发布仍无记录。
- 首屏下一步改为验收工单 02；统计和工单 03 的依赖说明同步更新。
- 预约证据改为最新报告的重复拒绝结果、提示原文和 5 笔预约仍保留；保留 7 天窗口缺少专项验证的说明。
- 更新快照日期、读取时间及工单 02 的 SHA-256。SPEC、工单、提案、判断和验收原记录均未修改。

## 已完成检查

- 11 个来源当前内容的 SHA-256 与页面内指纹相同；替换前后再次核对，原记录未变。
- 归档文件与替换前原页逐字节相同；当前入口与已核对的候选页逐字节相同。
- 通读全部 HTML 文案，包括折叠内容；对照上表核对要求、依赖、提案与判断。
- 所有导航和来源锚点有效，ID 无重复。
- 样式完整内联，与技能提供的 `plan.css` 一致；没有新增样式或未定义 class。
- 原主题脚本保持原样；项目范围、待决策、变更和系统判断四个分区逐字保持原样。
- 页面没有外部资源、远程字体、网络接口或外链；核心内容保留在 HTML 中。

## 未完成检查

本次 Playwright 预览无法启动：本机没有对应的 Chromium 浏览器文件。随后尝试通过 Chrome 打开本地候选页，浏览器安全策略拒绝 `file:` 协议。未绕过此限制。
1440px 与 390px 的渲染、浅色与深色截图、横向溢出、键盘交互、浏览器控制台与网络请求均未实测。
用户尚未确认文案与视觉效果。

## 刷新交接

- 当前入口：`.scratch/tool-lending/plan.html`。
- 技能入口：`.agents/skills/light-html-plan/SKILL.md`。
- 权威来源：上表中的 SPEC、工单、变更提案、判断日志和工单验收记录。
- 任务或阶段完成、出现阻塞、得到验收结论时，执行者先记录事件，再刷新此页。
- 刷新前把原页的完整字节保存至 `.scratch/tool-lending/plan-history/<UTC time>-plan.html`。
- 交付、验收和发布分别展示；页面不改变原记录，不批准提案。

本次候选文件已替换当前入口，未留下本次新建的临时文件。此前创建页面时记录的四个 <tmp> 临时文件不属于本次刷新。

## 本次替换身份

- 替换成功（UTC）：`2026-10-10T11:12:15+00:00`。
- 旧页 SHA-256：`9f47fedff0eb47a27f5fb2ad4d8488af4f901dd2680eeda95f4384826d1f574d`。
- 当前页 SHA-256：`e4b1bea465ad696121c600921e1d4749a1f0eaf000d186d36f980896833fd450`。
