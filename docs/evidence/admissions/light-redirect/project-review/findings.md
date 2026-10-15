# Findings registry

| ID | Sev | Source | Summary | Disposition | Status |
|---|---|---|---|---|---|
| P-001 | high | Producer VS-5 | On "just edit, skip the proposal" the agent edited the SPEC directly with no record | confirmed; user decision: write the proposal anyway, take the request as approval | fixed at repair1 |
| O-1 | low | Producer / Critic | Example shared the fixture's domain; VS-2 copied it | confirmed | fixed at repair2 (example moved to payment reminders; VS-2 rerun wrote its own analysis) |
| F-001 | medium | Critic r1 | Template lacked Charter impact and open decisions; E-005 overclaimed AC-2 | confirmed | fixed at repair2 (Charter line, Open decisions section, tests); E-005 re-scored below |
| F-002 | medium | Critic r1 | Handoff branches ambiguous (Charter + apply, CP evidence, clarify vs inline, conditional approval, Charter location) | confirmed | fixed at repair2 |
| F-003 | medium | Critic r1 | Approval in a later conversation had no owner | confirmed | fixed at repair2 (description + step 5; VS-2 new-session approval) |
| F-004 | medium | Critic r1 | "Just edit" approval not limited to what the user asked | confirmed | fixed at repair2 (approval only when the proposal changes exactly that) |
| F-005 | medium | Critic r1 | After the skill returns, the agent may still edit by hand | confirmed; user decision 2026-10-10: a repeated, explicit insistence after approval is allowed, limited to the approved change and recorded as `applied` by hand | fixed at repair3 (rule + status table); behavior observed in VS-5/VS-5b insist runs |
| F-006 | low | Critic r1 | Map pointer reads like a decision; missing section unhandled | confirmed | fixed at repair2 (wording "not yet a decision"; skip and tell caller). Seam with decision-map's contract recorded for stage 3 step 4 |
| F-007 | low | Critic r1 | "Caller stops" narrower than the hook rule; caller ticket unspecified | confirmed | fixed at repair2 |
| F-008 | medium | Critic recheck 1 | Bare approval with unanswered open decisions was recorded as approved using the model's recommendations; evidence missed it | confirmed | fixed at repair4 (step 5 + PROPOSAL.md); rerun 2/2 kept `proposed` and asked; "go with your recommendations" then approved once |
| F-009 | low | Critic recheck 1 | Status-reset rule contradicts the example | confirmed | fixed at repair4 |
| F-010 | low | Critic recheck 1 | Hand-edit rule loose ends (apply wording, "insists again", Charter exclusion, test name) | confirmed | fixed at repair4 |
| F-011 | low | Critic recheck 2 | Conditional Charter line led to an unneeded Change Proposal recommendation | confirmed | fixed at repair5 (Charter line names only items the proposal as written changes; conditional effect goes in the option; choosing an option updates the lines it settles without resetting status) |
| E-001 | medium | Evaluator r1 | Charter seam unevidenced at current text | confirmed | evidence collected round 2 (R2-E-001) |
| E-002 | medium | Evaluator r1 | Hand-edit rule unevidenced at its own text | confirmed | evidence collected round 2 (R2-E-002) |
| E-003 | low | Evaluator r1 | Review-FAIL and conflicting-tickets triggers and numbering unexercised | confirmed | partly: review-FAIL trigger and numbering run (R2-E-003); conflicting tickets not run (limitation) |
| E-004 | low | Evaluator r1 | Clarify and rejected handoffs unexercised | confirmed | partly: rejection run (R2-E-004); clarify not run (limitation) |
| O-2 | low | Producer r2 | First "just edit" reply mentions the user may insist on a hand edit | rejected (Evaluator r2: transparent, within CP-001) | closed |
| G-001 | low | Evaluator r2 | User decisions qualifying AC-3/AC-4 recorded only as paraphrase | confirmed | fixed: changes.md CP-001 (approved, exact user answers) |
| G-002 | low | Evaluator r2 | Turn-2 prompts not preserved | confirmed | fixed: listed in round-02 producer evidence |
