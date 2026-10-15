# 第 5 步 Critic round 1（Claude 子 agent，只读，2026-10-11）——处理结果

目标 `a706177..f2f3af2`。全部 13 条在主会话核实后处理：

| ID | 级别 | 处理 |
|---|---|---|
| C-001 | medium | 已修：`Decision data` 行宽松识别（大小写、加粗、反引号、表格、代码块内忽略），非四值一律 off（未识别）。测试 8 种写法。 |
| C-002 | medium | 已修：没给项目根时，从当前目录往上找最近的 `docs/agents/light-project.md`（到 git 根为止）；子目录也能找到。agent-config SKILL.md 改写。 |
| C-003 | medium | 已修：分档器返回 light-decide 统一格式的 Score 记录，放在 `abstract_profile.decisions`；来源不可用、超时、格式错也有记录。 |
| C-004 | medium | 已修：`fallback_used` 按 `fallback_reason != none` 判断。 |
| C-005 | medium | 已修：答案未采用时，推荐的 `confidence` 为 None、`probabilities` 为基准；原始分布留在 `semantic_judgments` 和 `decisions`。 |
| C-006 | low/med | 已修：降档余量从高一档的边界算（`(level+0.5) - score`）；文字写明"score within the downgrade margin"。 |
| C-007 | low/med | 已修：`RetryPolicy(max_retries=0)`；实测服务不通时 0.02 s 退回。 |
| C-008 | low | 已修：后端名只用 `hostname:port`，不含账号口令。 |
| C-009 | low | 已修：策略文件类型检查（backends/names/questions/阈值非布尔且在 0–1）。 |
| C-010 | low | 不改：SDK 字段说明写明 `score` = "probability-weighted average of the rubric levels"（见 evidence/live-probe），与 formats.md 一致。 |
| C-011 | low | 已修：删掉无用的 `choices_dict`；agent-config 现在用到 `typed_result`/`own_result`；加测试保证两份 `decision_source.py` 一致。 |
| C-012 | low | 已修：manuscript-ops 要求 `calibrated` 与 `fallback_reason == none`；自判（含单选项）直接记 `self_judgment`。 |
| C-013 | low | 已修：评测两个维度统一用 0.5；删掉 `skills-jev-lab/.env`；只有本机地址才用占位 key；临时目录退出时删除。 |

另：主会话按 selection.md 加了一条——私网地址只有在策略文件写明 `private-network` 时才算 private-network，否则算 third-party。

复跑：全套 619 passed / 1 skipped；文档检查 PASS；本机 e2e 与 live 评测结果与修改前一致（35/36）。
下一步：同一 Critic 复查（SendMessage 给原 agent），再开新的 Evaluator。

## Round 2（同一 Critic 复查 a706177..fb55a11）
- C-001..C-013：9 条完全正确；C-010 维持不改；C-003 对格式正确的回复完整；C-001、C-013 正确但带出新问题。
- N-1（medium）：收窄 try 后，NaN/inf 分数或非数值概率会让分档器崩溃 → 已修：分数要求有限数，所有级别概率要求 0–1 的非布尔数，否则走 malformed。测试 4 种坏回复。
- N-2（low）：评测策略没写 `data`、名字规则和脚本不一致 → 已修：评测条目写 `data: <decision_data>`，名字用脚本的 `_endpoint_name`。
- N-3（low，失败时关闭）：任何提到 "decision data" 的行都被当成设置 → 已修：只认标签形式（行首、可带列表符号/强调/表格竖线，后接 `:` 或 `|`）。测试补 3 种写法。
- 附加：`Decision data: private-network` 但策略没声明私网时，ask-light 的说明里提示要在策略里写 `data: private-network`。
- 顺带修：`fd41d91` 第 5 步改名误把 `evals/jev` 路径改坏，fixture 隔离测试一直被跳过；现在不跳过。
- 复跑：621 passed / 0 skipped；文档检查 PASS。提交 见 git log "handle malformed scores"。
