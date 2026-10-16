# Optional route judgment through light-decide

Use this branch only when interpreting the task materially helps routing or
review selection. `light-decide` owns the source choice, the project's
`Decision data:` limit, calibration and the decision log. Never bake in a local
URL, model name, API key, SDK installation or global configuration change.

## One bounded judgment

Prepare the original request, relevant source relationships, actual deliverables
and already-known facts. Do not send unrelated repository contents or the whole
reference library. Ask one `choice` with question id `manuscript-ops/route` and
options `Quick`, `Structured`, `Project`, `InsufficientInfo`, using routing.md's
management definitions. Ask narrow independent questions about source conflict
or lifecycle needs only when needed. Repeated rescoring is not progress.

Pass the normalized result to the assessor as `semantic_result`. The assessor
uses the answer only when light-decide applied it (a calibrated typed decision
that met its threshold). A self-judgment, an unapplied answer or a malformed
result keeps the task-grounded route, and the observation records why.

The assessor validates the distribution and keeps deterministic workflow and
review constraints. A model cannot remove a known Project need, create a Project
without such evidence, waive high-risk review, or grant execution/approval rights.

## Older snapshots

A snapshot written before light-decide stores the Host `decide` payload
(`answers.route`) and a `semantic_policy` with `min_confidence` and
`calibration_reference`. The validator replays it with those values. Do not
rewrite it.

## Uncertainty and unavailable tools

Missing, failed, malformed, uncalibrated, low-confidence and contradictory results
fall back to the current agent's evidence-based judgment. Preserve unknowns.
Clarify only the materially missing fact; do not request model installation or
Project initialization. A model probability is not a proof of correctness.

## Validation

Measure on de-identified Chinese cases with expected routes/review requirements
frozen before inference. Separate calibration cases from a held-out set, and
record thresholds in the user's policy file through light-decide calibration.
Simulated failures prove fallback behavior, not model accuracy or real service
invocation.
