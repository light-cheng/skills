# Examples

## Direction change: a requirement turns out wrong

`light-implement` is working on `.scratch/payment-reminders/issues/02-send-sms.md`.
Its tests show the SMS provider blocks messages between 21:00 and 08:00, so
"send the reminder exactly 24 hours before the due time" cannot hold for
bills due in the evening. It appends an implementation report with
`Outcome: BLOCKED`, then calls `light-redirect`.

The approved SPEC promised exact timing, so this is a direction change.
`light-redirect` writes `.scratch/payment-reminders/changes/01-send-reminders-in-daytime-hours.md`:

```markdown
# 01 — Send reminders in daytime hours instead of exactly 24 hours ahead

**Status:** proposed
**Raised by:** light-implement · 2026-10-10
**Trigger:** issues/02-send-sms.md#implementation-report--2026-10-10

## Why
The SMS provider rejects messages sent between 21:00 and 08:00
(implementation report, Verification). The SPEC's "exactly 24 hours before"
(spec.md, Requirements, R1) fails for every bill due between 21:00 and 08:00.

## Change
- SPEC: R1 → send at the latest daytime moment that is still at least 24 hours before the due time.
- Tickets: change acceptance issues/02-send-sms.md → test an evening due time as well as a daytime one.
- Charter: none
- Accept again: none

## Open decisions
- Should reminders for bills due before 08:00 go out the previous morning or the previous evening before 21:00? Recommended: previous evening, closer to 24 hours.

## Not changed
Email reminders, message wording and the opt-out link.

## Comments
```

It asks: "Approve this change? Reminders would arrive in daytime hours, a
little earlier than 24 hours for evening bills. One question: for bills due
before 08:00, previous evening (recommended) or previous morning?" The user
says "yes, previous evening". It records the choice in the proposal, sets
`**Status:** approved`, adds
`- 2026-10-10 approved — "yes, previous evening"`, and recommends
`$project-spec` and then `$project-tickets` with the proposal path.

## Local fix: not a redirect

Review fails ticket 01 because reminder emails show the amount without its
currency. The SPEC already requires the currency, so the plan is still right
and only the code is wrong. `light-redirect` writes nothing and hands the
finding back for repair.
