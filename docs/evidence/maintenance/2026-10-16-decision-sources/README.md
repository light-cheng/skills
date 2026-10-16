# Decision sources without Jev (v0.2.8)

[中文记录](README.zh-CN.md)

`ask-light`, `agent-config`, `light-decide`, `project-init` and `manuscript-ops` stopped depending on TypeSafe Jev (step 5). Full review: two Critic rounds, then a fresh Evaluator.

- [Critic round 1 and its handling](review/critic-round1.md)
- [Evaluator rounds 1–3](review/evaluator-verdict.md): round 1 FAIL → repaired; round 2 BLOCKED (real Host evidence missing); round 3 **PASS** (2026-10-16) on two real Claude Code 2.1.296 scenarios
- Real Host runs: [scenario 1 — no source, one setup offer, refusal remembered](evidence/host-claude-s1/transcript.md) · [scenario 2 — uncalibrated source keeps the baseline](evidence/host-claude-s2/transcript.md) · [known gaps: proposals, refusal, light-implement calling light-decide](evidence/host-claude-gaps/transcript.md)
- Local decision server runs: [live probe](evidence/live-probe-20261011.md), [end-to-end](evidence/e2e-final.txt), live evaluations (`evidence/eval-live-opendecider-*.json`)

Paths are redacted (`<repo>`, `<tmp>`, `~`) and one key-shaped value is replaced with `sk-<redacted>`. The local decision server address (`127.0.0.1:8001`) is kept because it is what the runs used.
