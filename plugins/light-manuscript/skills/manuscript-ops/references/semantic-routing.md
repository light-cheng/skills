# Optional route judgment through `decide`

Use this optional path only when interpreting borderline task phrasing materially affects routing between `Quick` and `Structured` (for example, resolving whether non-critical unknowns require structured coordination). `decide` owns backend selection (`light-decision-mcp`), the repository's `Decision data` privacy boundary in `docs/agents/light-project.md` (`on-device` by default), per-question calibration policy (`~/.config/light/decision-policy.json`), and `.scratch/<feature>/decisions.md` logging. Never hardcode endpoints, model names, API keys, or SDK imports inside `manuscript-ops`.

## One bounded judgment

Prepare a minimal state containing the user's request, declared source relationships, target deliverables, and confirmed task facts. Exclude unrelated workspace files, secrets, and personal data.

Evaluate a single `choice` judgment with question ID `manuscript-ops/route` and options `["Quick", "Structured", "Project", "InsufficientInfo"]` using the route definitions in [routing.md](routing.md). Pass the normalized `decide` envelope to `scripts/assess_project.py` in `routing-input.json` as `semantic_result` (or pass a direct `light-decision-mcp` `choose` response alongside a calibrated `semantic_policy` object).

## Deterministic guardrails

`manuscript_ops_core.resolve_semantic_route` applies `semantic_result` only when:

1. It is a valid `typed-decision` probability distribution summing to `1.0` whose chosen option matches `confidence`.
2. Calibration and threshold checks succeeded (`calibrated: true`, `applied: true`, `fallback_reason: "none"`).
3. Deterministic workflow and review invariants hold:
   - A model judgment cannot downgrade a task with active `Project` lifecycle triggers out of `Project`, and cannot escalate a non-lifecycle task into `Project` (`workflow_constraint`).
   - A model judgment cannot downgrade a task to `Quick` when `scale`, `source_complexity`, `risk`, or `output_complexity` is non-zero or `high_risk_facts` is active (`required_review`).
   - `"InsufficientInfo"` preserves the deterministic baseline route (`insufficient_information`).

## Graceful fallback

When `decide` or `light-decision-mcp` is not installed, `Decision data` is `off`, the backend is unreachable or uncalibrated, confidence falls below policy threshold, or `method` is `"self-judgment"`, the assessor keeps the deterministic `needs-v2` task-grounded route and records the exact `fallback_reason` in `semantic_judgment`. Never report `BLOCKED` or request MCP setup merely because `decide` is unavailable.
