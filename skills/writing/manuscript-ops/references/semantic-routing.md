# Optional structured decision MCP

Use this branch only when interpreting the task materially helps routing or
review selection and the current Host exposes typed decision tools. OpenDecider
and compatible tools are optional providers. Never bake in a local URL, model
name, API key, SDK installation or global configuration change.

## One bounded judgment

Prepare the original request, relevant source relationships, actual deliverables
and already-known facts. Do not send unrelated repository contents or the whole
reference library. Ask a Choice about Quick/Structured/Project using routing.md's
management definitions; ask narrow independent questions about source conflict
or lifecycle needs when needed. Include an insufficient-information option.
Batch independent questions once; repeated rescoring is not progress.

A Host can consume the result directly as evidence, or pass the `decide` payload
into the assessor as `semantic_result` (model plus `answers.route` containing
choice, probabilities and confidence). `semantic_policy` supplies a
`min_confidence` and non-empty `calibration_reference`. Without a measured policy,
record the recommendation but keep the task-grounded agent route.

The assessor validates the distribution and keeps deterministic workflow and
review constraints. A model cannot remove a known Project need, create a Project
without such evidence, waive high-risk review, or grant execution/approval rights.
Its observation reports whether it was applied and a precise fallback reason.

## Uncertainty and unavailable tools

Missing, failed, malformed, uncalibrated, low-confidence and contradictory results
fall back to the current agent's evidence-based judgment. Preserve unknowns.
Clarify only the materially missing fact; do not request model installation or
Project initialization. A model probability is not a proof of correctness.

## Validation

Measure on de-identified Chinese cases with expected routes/review requirements
frozen before inference. Separate calibration cases from a held-out set. Compare
old policy, current agent judgment and current policy with the actual MCP; record
raw choices, probability distributions, final decisions, fallbacks and latency.
Only promote a default preference when the comparison supports it. Simulated
failures prove fallback behavior, not model accuracy or real service invocation.
