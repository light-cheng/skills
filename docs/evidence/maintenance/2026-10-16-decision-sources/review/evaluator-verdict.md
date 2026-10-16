# 第 5 步独立 Evaluator（新开 Claude 子 agent，只读）

## Round 1（目标 a706177..35e4018）——FAIL
- AC-1..AC-10：AC-7、AC-8、AC-9、AC-10 met；AC-1、AC-3、AC-5 对格式正确的回复 met；AC-2 部分；AC-4、AC-6 脚本/文本 met，**Host 层面未取证**。
- 缺陷：D1 ask-light 格式错的 Choice 回复会崩（medium）；D2 agent-config 不一致/越界的 Score 能触发降档（medium，危险方向）；D3 yes/no 值没校验（NaN、布尔、7）；D4 `## Decision data: off`、`1.`、`>`、`=` 写法被忽略，多行取第一行；D5 私网服务没有 key 就不可用；D6 SDK 超时没记成 timeout；D7 测试名里的 Jev、SKILL.md 少空行。
- 转 PASS 的条件：修 D1–D4 并加测试；在最终提交上重跑本机实测；**至少一个真实 Host 上的证据**（light-decide 无来源时只提一次 setup、没同意不做事、记住拒绝；ask-light / agent-config 未校准时保持基准，判断不当作批准或 Profile 确认）。

## 处理（提交见 git log "reject malformed typed replies"）
- D1/D3：`valid_distribution` / `valid_probability`（decision_source）——Choice 概率必须正好覆盖合法选项、每项 0–1、和为 1；yes/no 值必须是 0–1 的有限非布尔数；否则 `malformed`。
- D2：Score 回复必须是合法分布，且报告的 score 与期望值相差 ≤ 0.02、在 [0, n−1] 内；否则 `malformed`。测试造数函数改为生成自洽回复（修正了几组本身不可能的测试数据）。
- D4：标签可带 `>`、`#`、`1.`、列表符号、强调、表格竖线，分隔符 `:`、`|`、`=`；多行时取最严格的值；任何一行值不认识 → off。
- D5：策略声明为 private-network 的服务也用占位 key。
- D6：异常类名含 timeout 也算 `timeout`。
- D7：测试名去 Jev（剩余 docstring 与 `evals/jev` 路径保留）；SKILL.md 补空行；light-decide 第 3 步改为"Setup only looks until the user says yes; it changes nothing before."（化解 AC-6 的表述张力）。
- 本机实测在最终代码上重跑（2026-10-11T12:37Z）：e2e 与修改前相同；live 评测 35/36，复杂度 0 个 fallback——真实回复都通过了新校验。证据 `.scratch/step5/evidence/eval-live-opendecider-20261011-final.json`。
- 全套 624 passed / 0 skipped；文档检查 PASS。

## 仍缺（BLOCKED 项）
真实 Host 证据（Claude Code / pi / Codex 任一）。需要 `claude -p` 或 pi/Codex 真实运行，耗额度；**做之前先问用户**。

## Round 2（同一 Evaluator 复核 a706177..bd25baf）——BLOCKED
- D1–D5 已修（逐条用探针复现确认）；D6 部分修（类名含 timeout 即算；没设显式客户端超时，用 SDK 默认值，可接受）；D7 测试名已改，约 10 处 docstring/注释仍提 Jev（有意保留）。
- AC-1、2、3、5、7、8、9、10 met；AC-4、AC-6 脚本/文本 met，**真实 Host 未取证**。
- 新观察（都是 low，不卡）：N1 表头写成 `| Decision data | Value |` 会整份读成 off（失败时关闭）；N2 破折号分隔 `Decision data — off`、或标题下一行才写值，仍按缺省 on-device 读（失败时放开，但只到本机）；N4 最终代码的 e2e 没留证据文件 → 已补 `.scratch/step5/evidence/e2e-final.txt`（bd25baf，12:39Z）和 `eval-live-opendecider-bd25baf.json`。
- **转 PASS 只差一次真实 Host 运行**（Claude Code / pi / Codex 任一，用户批准后）：
  1. light-decide 无来源时自判、只提一次 setup、没同意不改任何东西、记住拒绝；
  2. Agent 按 ask-light、agent-config 文本运行，来源未校准时保持确定性基准，从不把判断当作批准或 Profile 确认。

## Round 3 (2026-10-16, fresh Claude Evaluator): PASS

Host evidence on Claude Code 2.1.296: `evidence/host-claude-s1/` (scenario 1: no source → self-judgment, one setup offer after looking, nothing changed before consent, refusal recorded as `Decision data: off` and honoured in a new session) and `evidence/host-claude-s2/` (scenario 2: ask-light waits for approval and renders `/project-clarify`; agent-config returns NEED_INPUT without a Profile; light-decide with an available, uncalibrated OpenDecider records `applied: false`, own judgment final). AC-4 and AC-6 met.

Prompts: s1 turn 1 format judgment; turn 2 "dozens of times a week" + include-metrics; turn 3 "No, I don't want to set up a decision source."; turn 4 "This project only."; turn 5 (new session) tone judgment. s2 ask-light "/ask-light What should I do next…"; approval "Yes, go ahead."; agent-config plan for ticket 01; direct light-decide ask-light/next-action.

Found and fixed by the Host run: ask-light assumed Codex and blocked on a project + global duplicate install (`8317357`). Findings F1 (missing on-device default in ask-light / agent-config text) fixed; F2 (agent-config profiler not exercised with a confirmed Profile) covered by script tests only; F3 prompts and commit added here.

Known gaps now covered (`evidence/host-claude-gaps/`): G1 ticket/SPEC plan gap → light-redirect proposal, ticket claimed, no code; G2 rejection recorded, nothing else changed; G3 light-implement → light-decide `light-implement/offer-agent-config`, uncalibrated, not applied; G4 scope change in conversation → proposal, SPEC untouched. Low follow-up: eleven SKILL.md files render invocations as `$skill` (Codex form) even on Claude Code.
