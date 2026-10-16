# 决策来源脱离 Jev（v0.2.8）

[English](README.md)

`ask-light`、`agent-config`、`light-decide`、`project-init`、`manuscript-ops` 不再依赖 TypeSafe Jev（第 5 步）。完整审查：两轮 Critic，再由新 Evaluator 复核。

- [Critic 第 1 轮及处理](review/critic-round1.md)
- [Evaluator 第 1–3 轮](review/evaluator-verdict.md)：第 1 轮 FAIL → 修复；第 2 轮 BLOCKED（缺真实 Host 证据）；第 3 轮 **PASS**（2026-10-16），依据两个真实 Claude Code 2.1.296 场景
- 真实 Host 运行：[场景 1——无来源、只提一次 setup、记住拒绝](evidence/host-claude-s1/transcript.md) · [场景 2——来源未校准时保持基准](evidence/host-claude-s2/transcript.md) · [已知缺口：提案、拒绝、light-implement 调 light-decide](evidence/host-claude-gaps/transcript.md)
- 本机决策服务运行：[实测](evidence/live-probe-20261011.md)、[端到端](evidence/e2e-final.txt)、live 评测（`evidence/eval-live-opendecider-*.json`）

路径已脱敏（`<repo>`、`<tmp>`、`~`），一处形似 key 的值替换为 `sk-<redacted>`。本机决策服务地址（`127.0.0.1:8001`）保留，因为运行实际用的就是它。
