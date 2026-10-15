---
name: light-redirect
description: Use when the approved plan no longer holds - work finds a requirement missing or wrong, a review fails on direction rather than code, the user brings a new idea or changes their mind after approval, or tickets contradict each other or the SPEC - and when the user answers an open change proposal. Writes a change proposal the user approves before any SPEC, ticket or acceptance item changes.
---

# Light Redirect

A **change proposal** says that the approved plan should change, why, and
exactly what would change. `light-redirect` writes it and records the user's
answer. Only the user approves it. `project-spec` and `project-tickets` apply
it, unless the user insists on a hand edit.

## Direction or local fix

A **direction change** needs a different SPEC, ticket graph (add, drop, split
or reorder tickets, change `Blocked by`) or acceptance item. A **local fix**
leaves the approved plan true: only the code or a document is wrong. Hand a
local fix back to the caller; it is not a redirect.

When the call is unclear, see [Optional capabilities](#optional-capabilities).
Every change to the SPEC, tickets or acceptance items goes
through a proposal, however small.

## Steps

1. **Gather.** Read the trigger (implementation report, review verdict, the
   user's words, or the conflicting tickets) and the approved SPEC and tickets
   it touches. Done when every claim you will make has a file locator or a
   quote.
2. **Decide** direction or local fix, as above. A local fix ends here.
3. **Write** the proposal to `.scratch/<feature>/changes/<NN>-<slug>.md` with
   [the proposal format](references/PROPOSAL.md). Done when the proposal names
   every affected SPEC section, ticket action, Charter item and resolved ticket
   that needs acceptance again, every decision the user still has to make, and
   what stays unchanged.
4. **Point** to it from `.scratch/<feature>/map.md` when that file exists
   ([map pointer](references/PROPOSAL.md#map-pointer)).
5. **Ask** the user to approve or reject it, in plain words, together with any
   open decisions. Record the answer as the format describes; partial
   approvals, edits, silence and "just edit it" are covered in
   [handling the answer](references/PROPOSAL.md#handling-the-answer).
6. **Hand off** and stop:
   - Approved → recommend `$project-spec` for SPEC changes and
     `$project-tickets` for ticket changes, passing the proposal path. When its
     `Charter` line names a Charter item, recommend `project-review`'s Change
     Proposal first and cite the recorded approval as its decision evidence.
   - An open decision needs more than a short answer (research or a longer
     interview) → recommend `$project-clarify` and leave the proposal
     `proposed`.
   - Rejected → return to the caller with the reason.

The applying skills make the edits; `light-redirect` never does. A hand edit
the user insists on after approval follows
[hand edit](references/PROPOSAL.md#hand-edit).

See [examples](references/EXAMPLES.md) for a direction change and a local fix.

## Optional capabilities

- **Direction or local fix is unclear** → call `light-decide` with question id
  `light-redirect/is-direction-change` (yes or no). Unavailable → judge it
  yourself.

## Contract with callers

- **Optional.** When this capability is missing, unavailable or declined, the
  caller keeps its original behavior (for example, `light-implement` reports
  the gap and stops). Nobody reports `BLOCKED` or asks for an installation
  because of it.
- **Caller records first.** The caller writes the event into its own record
  (for example the ticket's implementation report) before calling. Its ticket
  stays as the caller left it.
- **Returns, never takes over.** It returns the proposal path and status. It
  recommends user-invoked skills and never starts them.
- **Grants nothing.** It never edits the SPEC, tickets, code or a Charter, and
  its proposal changes nothing until the user approves and the change is
  applied.
