# 工具借用项目进度页：来源与检查

交付：`.scratch/tool-lending/plan.html`。首次创建，没有旧页需要归档。
页面的记录截至 2026-10-09；生成时刻及 11 个来源的路径、记录日期、SHA-256 均写在页面的“来源”分区。

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
| issues/02 · Implementation report | 2026-10-09 partial；表单与存储完成；5 笔存储；拒绝逻辑及提示未写、重复未测 | #ticket-02 / 首屏 | 已保留，未把存储验证扩大为预约验收 |
| issues/03 · Status / Blocked by | open；依赖 02；无实现报告 | #ticket-03 / #decide | 显示阻塞来自预约；不归因于短信决策 |
| changes/01 · Trigger / Comments | 14 → 7 天；用户 10-04 批准；project-spec / project-tickets 当日应用 | #changed | 已保留 |
| changes/01 · Not changed / Open decisions | R1、R3、R4 不变；无待决策项；Charter / Accept again 为 none | #changed | 已保留 |
| changes/02 · Trigger / Status | 用户反映一半成员不看邮件；10-09 提出，proposed，未批准 | #decide / #changed | 已保留 |
| changes/02 · Change / Open decisions | 增加短信及工单 03 验收项；拟新增 04 账号；所有有手机号成员或主动订阅者 | #what / #decide / #changed | 已保留，04 不当作已存在工单 |
| changes/02 · Not changed / remaining fields | R1、R2、R4 不变；Charter / Accept again 为 none | #changed | 已保留 |
| decisions.md · 2026-10-08 row | yes，0.58，local-decider，本机数据；未校准、applied=false；final=no | #judged | 原始字段可展开；未采用的判断排在前面 |
| decisions.md · 2026-10-09 row | Agent 自行判断短信为计划变更，applied=true；final=yes；无置信值 | #judged | 不编造置信值 |
| docs/agents/issue-tracker.md / AGENTS.md | 项目记录位置，稳定 HTML 路径和历史目录 | #sources / 刷新交接 | 已保留 |

## 已完成检查

- 11 个来源当前内容的 SHA-256 与页面内指纹相同；未修改原记录。
- 六个分区按技能规定排序；需求与进度均为 R1–R4 顺序，R4 显示缺口。
- 所有导航和来源锚点有效，ID 无重复。
- 样式完整内联，与技能提供的 `plan.css` 一致；没有新增样式或未定义 class。
- 页面没有外部资源、远程字体、网络接口或外链；核心内容保留在 HTML 中。
- 主题脚本在模拟 DOM 中验证了系统浅色、系统深色，以及双向手动切换；这不是浏览器测试。
- 通读主文和折叠内容，核对写完、工单验收、项目验收、发布、应用中的变更及待批准提案。

## 未完成检查

实际浏览器未能打开页面。Chrome 自动化策略拒绝 `file:` URL；沙箱禁止绑定本机 HTTP 预览端口。没有绕过限制，也没有部署页面。
1440px 与 390px 的渲染、浅色与深色截图、横向溢出、键盘交互、浏览器控制台与网络请求均未实测。
用户尚未确认文案与视觉效果。

## 刷新交接

- 当前入口：`.scratch/tool-lending/plan.html`。
- 技能入口：`.agents/skills/light-html-plan/SKILL.md`。
- 权威来源：上表中的 SPEC、工单、变更提案、判断日志和工单验收记录。
- 任务或阶段完成、出现阻塞、得到验收结论时，执行者先记录事件，再刷新此页。
- 刷新前把原页的完整字节保存至 `.scratch/tool-lending/plan-history/<UTC time>-plan.html`。
- 交付、验收和发布分别展示；页面不改变原记录，不批准提案。

临时文件清理：已调用 trash；沙箱拒绝写入回收站，四个本次生成的临时文件仍留在 <tmp>（build-tool-plan.py、check-tool-plan.py、tool-plan-theme.js、tool-lending-claims.txt）。
