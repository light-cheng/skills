# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

## Ticket status

A ticket's `Status:` line moves through these values:

| Status | Set by | Meaning |
| --- | --- | --- |
| `ready-for-agent` | `project-tickets` | Published and unclaimed; the same as `open` for the frontier |
| `open` | `decision-map` | Open wayfinding question, unclaimed |
| `claimed` | `light-implement` or `decision-map` | Someone is working on it |
| `resolved` | `project-review` (implementation tickets) or `decision-map` (questions) | Done and accepted |
