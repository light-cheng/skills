# Findings registry

Per-ticket reviewers report findings only. The Core records the remaining final-acceptance gap below; observed CLI installation is not converted to native discovery.

## V-F001 — confirmed, fixed in visual recheck round 2

Historical main #index-caption contained desktop-only “右侧Q1” on mobile. See ../evidence/visual-revision/visual-review-round-01.md. Current fresh recheck actually inspected two-page wide/narrow/light/dark and interaction views and confirmed the wording absent. Evidence: ../evidence/composition/visual-review-round-02.md and its immutable target manifest. User palette rejection remains historical CP-002; this review is not user taste approval.

Final current-copy recheck: ../evidence/language-revision-20261009/review-round-03.md. State remains fixed; current six-page copy/visual loop converged at its final round 3/3.

## F-A13 — confirmed, unresolved environment/evidence gap

- Severity: high
- Location: ../evidence/ticket03/installation/native-discovery.json; native-stderr.txt
- Requirement: Charter AC-A1–A13 / SPEC A13 require native discovery of the clean installed candidate, not just installation or CLI inventory.
- Observation: one bounded Codex app-server initialize was sent; exit 1, stdout has no RPC response. No skills/list was sent or observed. Error is Operation not permitted; the exact failing file/path is unknown.
- Disposition: confirmed. Clean per-package/collection bytes and CLI list are valid installation evidence, but cannot satisfy this condition.
- Owner of unblock: environment/Host provider and user-authorized future test setup.
- Smallest next action: provide an environment in which native initialize and skills/list can return actual responses for the already-identified clean install paths. No permission/configuration expansion was authorized or performed in this task.
- State: unresolved. Final project-review must retain this gap; no catalog synchronization/admission based on the current record.
