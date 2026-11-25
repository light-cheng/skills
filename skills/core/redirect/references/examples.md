# Redirect Examples

## 1. Local `.scratch/` tracker: broken external assumption

During `/implement` on `.scratch/payment-reminders/issues/02-send-sms.md`, integration tests reveal the SMS carrier blocks outbound messages between 21:00 and 08:00 local time. The approved spec requires sending reminders "exactly 24 hours before due time", which fails for every evening bill.

The implementer records the blocked finding under `## Comments` in `issues/02-send-sms.md`, halts code edits, and invokes `redirect`.

`docs/agents/issue-tracker.md` points to `.scratch/`. `redirect` scans `spec.md`, all files in `issues/`, and `.scratch/payment-reminders/map.md`, then writes `.scratch/payment-reminders/changes/01-send-reminders-in-daytime-hours.md`:

```markdown
# 01: Send SMS reminders during daytime hours instead of exactly 24 hours ahead

**Status:** proposed
**Raised by:** implement (2026-10-10)
**Trigger:** .scratch/payment-reminders/issues/02-send-sms.md#comments

## Why
Carrier quiet-hours rules reject SMS delivery between 21:00 and 08:00 (verified in `issues/02-send-sms.md` under `## Comments`). `spec.md` (`## Solution`, bullet 2, and User Story 4) requires exact 24-hour lead time, which cannot hold for bills due between 21:00 and 08:00.

## Change
- Spec: `spec.md` (`## Solution` and User Story 4) -> send at the latest daytime window (08:00 to 21:00) that is at least 24 hours before the due timestamp.
- Tickets: change acceptance `.scratch/payment-reminders/issues/02-send-sms.md` -> verify daytime clamping for due times inside 21:00 to 08:00 alongside daytime due times.
- ADR: none
- Acceptance charter: none
- Re-verify: none

## Open decisions
- For bills due between 00:00 and 08:00, should the reminder send the previous evening before 21:00 (27 to 35 hours ahead) or the previous morning at 08:00 (16 to 24 hours ahead)? Recommended: previous evening before 21:00, preserving at least 24 hours of notice.

## Not changed
Email reminder timing, SMS copy, and opt-out handling (`issues/03-opt-out-webhook.md`).

## Comments
```

`redirect` appends `- Change proposed, waiting on user: [01: Send SMS reminders during daytime hours instead of exactly 24 hours ahead](changes/01-send-reminders-in-daytime-hours.md)` under `## Not yet specified` in `map.md` and asks the user to approve the change and settle the open decision.

When the user replies `"Approved, use previous evening before 21:00"`, `redirect`:

1. Updates `- Spec:` and `- Tickets:` if needed, sets `**Status:** approved`, and appends `- 2026-10-10 approved: "Approved, use previous evening before 21:00"` under `## Comments`.
2. Moves the `map.md` pointer to `## Decisions so far`:
   `- [01: Send SMS reminders during daytime hours instead of exactly 24 hours ahead](changes/01-send-reminders-in-daytime-hours.md): Change approved 2026-10-10 (clamp quiet-hour SMS reminders to pre-21:00 previous evening)`.
3. Recommends `/to-spec .scratch/payment-reminders/changes/01-send-reminders-in-daytime-hours.md` followed by `/to-tickets .scratch/payment-reminders/changes/01-send-reminders-in-daytime-hours.md` (or applies the exact approved edits directly if `/to-spec` and `/to-tickets` are not installed or the user requests direct application).

## 2. Remote GitHub tracker (`gh`): Charter-scale `acceptance` fails on direction

Charter-scale `acceptance` evaluates milestone `#40` ("Offline sync queue") against `.scratch/offline-sync/acceptance/charter.md` and returns `FAIL` with `Cause: direction`: two tickets (`#42` and `#44`) implemented last-write-wins, which matches `ADR-0004` (`docs/adr/0004-client-timestamp-lww.md`) but loses edits on shared checklists required by criterion `AC-3`.

`acceptance` invokes `redirect`. Reading `docs/agents/issue-tracker.md` shows GitHub Issues (`gh`). `redirect` verifies the repo with `gh repo view --json nameWithOwner`, posts Change proposal `01` as a comment on `#40` via `gh issue comment 40 --body ...` (mirroring `.scratch/offline-sync/changes/01-per-item-checklist-merge.md` because `.scratch/offline-sync/acceptance/` is active), swaps `#44` from `ready-for-agent` to `needs-info`, and highlights both `- ADR: docs/adr/0004-client-timestamp-lww.md` and `- Acceptance charter: .scratch/offline-sync/acceptance/charter.md (AC-3)`. Nothing in `#40`, `#42`, `#44`, `ADR-0004`, or `charter.md` is modified until the user approves the proposal.

## 3. Local fix: not a redirect

Inline `acceptance` reviews ticket `01-invoice-email.md` and reports a finding: invoice emails omit the three-letter currency code next to the total. Checking `spec.md` shows currency codes are already required, and `01-invoice-email.md` already includes them in its acceptance criteria.

If `redirect` is consulted (or evaluates `redirect/is-direction-change` via `decide`, returning `no`), it classifies this as a **local fix**: the plan still holds and only the implementation is incomplete. `redirect` writes no Change proposal and returns the finding to the caller for ordinary code repair.
