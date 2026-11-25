---
name: redirect
description: "Halt active work and write a Change proposal when an approved spec, ticket graph, or Acceptance charter stops holding: implementation hits a broken assumption or missing requirement, acceptance or review fails on direction rather than code, tickets contradict each other or an ADR, the user shifts scope after approval, or the user answers an open Change proposal."
---

# Redirect

A **Change proposal** records that an approved spec, ticket graph, or **Acceptance charter** no longer holds, explains why with primary locators, and specifies the exact blast radius of revising it. `redirect` halts active work, publishes the Change proposal through the project's issue tracker, and waits for explicit human approval before any downstream artifact changes.

## Direction change vs local fix

- **Direction change**: requires altering an approved spec, ticket graph (adding, dropping, splitting, or reordering tickets, changing `Blocked by` edges, or changing ticket acceptance criteria), an accepted ADR (`docs/adr/`), or a frozen **Acceptance charter**. Every change to those artifacts goes through a Change proposal, however small.
- **Local fix**: leaves the approved spec, ticket graph, ADRs, and Acceptance charter intact; only code, tests, or draft prose are wrong. Hand a local fix back to the caller for repair without writing a Change proposal.

When the boundary between a direction change and a local fix is genuinely unclear, evaluate [Bounded judgment](#bounded-judgment) first.

## Steps

1. **Halt and gather.** Stop active implementation immediately without editing code, specs, tickets, or charters. Read `docs/agents/issue-tracker.md` (when absent, default silently to local markdown under `.scratch/<feature>/`), `docs/agents/triage-labels.md` (when present), `GLOSSARY.md`, relevant `docs/adr/` files, the trigger (implementation block, `acceptance` verdict with `Cause: direction`, conflicting tickets, or user request), and the approved artifacts it touches. If scanning a large spec or multi-ticket graph would crowd the current context, dispatch a read-only exploration subagent started with a **fresh context window** (never a fork of the current conversation) and pass sparse context pointers. Done when the tracker mode is known and every claim you plan to make has an exact file locator, issue reference, or quote.
2. **Classify.** Decide whether the trigger is a direction change or a local fix. On a local fix, return the finding to the caller and stop. Done when the classification is settled.
3. **Publish the Change proposal.** Search the entire spec, every open and resolved ticket, relevant ADRs, and any frozen Acceptance charter under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/`) for every requirement, user story, blocking edge, or criterion the change touches. Publish the proposal following [tracker targets and template rules](references/proposal.md): write `.scratch/<feature>/changes/<NN>-<slug>.md` for local `.scratch/` trackers, or post a structured comment on the active ticket or parent spec issue via `gh` / `glab` (or the configured tracker workflow) for remote trackers. Done when the published proposal names every contradicted spec passage, ticket action, ADR conflict, Acceptance charter criterion, resolved ticket needing re-verification, open user decision (with a recommendation), and unchanged boundary.
4. **Update tracker pointers.** When `.scratch/<feature>/map.md` or a `wayfinder:map` issue exists for the effort, append a pending pointer under `## Not yet specified` per [map pointer rules](references/proposal.md#map-pointer). On remote trackers where the blocked ticket carries `ready-for-agent`, update its triage label to `needs-info` (mapped via `docs/agents/triage-labels.md` when present). Done when tracker state reflects that the slice is waiting on human approval, or no map/label applies.
5. **Ask the user and record the decision.** Present the Change proposal in plain language alongside any open decisions, then wait for explicit human approval or rejection. When the user replies (in this turn or a later session), validate every open decision, record the status transition (`approved`, `rejected`, or `proposed` if questions remain), and move any map pointer per [handling the answer](references/proposal.md#handling-the-answer). Done when the user's explicit answer is recorded on the proposal, or the proposal rests at `proposed` awaiting their reply.
6. **Route approved revisions and stop.**
   - **Approved**: Route follow-up updates to the **Base workflow** with **Graceful fallback** ([routing details](references/proposal.md#routing-and-graceful-fallback)):
     - Spec revisions: recommend `/to-spec <proposal-ref>` (or `$to-spec` in Codex); if `/to-spec` is not installed or the user asks to apply the approved proposal directly, edit `.scratch/<feature>/spec.md` or the remote spec issue (`gh issue edit` / `glab issue update`) to match the approved proposal and log `Spec applied`.
     - Ticket revisions: recommend `/to-tickets <proposal-ref>`; if `/to-tickets` is not installed or the user asks for direct tracker updates, update `.scratch/<feature>/issues/` or remote tracker issues (`gh` / `glab`) to match the approved proposal and log `Tickets applied`.
     - Frozen Acceptance charter revisions: route charter updates through `acceptance` (Charter scale), citing the recorded approval on the Change proposal as authorization (if `acceptance` is not installed, update the charter file under `.scratch/` only with explicit user confirmation).
   - **Open decision needs deeper exploration**: Recommend `/grill-with-docs` or `/wayfinder` (Graceful fallback: run a focused clarifying interview inline) and leave the proposal `proposed`.
   - **Rejected**: Return to the caller with the recorded rejection reason.
   Done when the proposal locator, status, and next command (or completed fallback update) are reported.

See [examples](references/examples.md) for local `.scratch/` and remote GitHub direction changes as well as a local fix.

## Bounded judgment

When classifying between a direction change and a local fix is borderline:

- Invoke `decide` with question ID `redirect/is-direction-change` (`yes_no`: `yes` = direction change, `no` = local fix), the feature slug when known, and minimal plain-language facts (omit raw source code, diffs, credentials, and personal data). `decide` enforces `Decision data` from `docs/agents/light-project.md` and logs to `.scratch/<feature>/decisions.md`.
- **Graceful fallback**: When `decide` or `light-decision-mcp` is unavailable, `off`, or uncalibrated for `redirect/is-direction-change`, classify directly using your own self-judgment and continue without warning or blocking.

## Caller contract

- **Caller records first.** Calling workflows (`/implement`, `/implement-spec`, `acceptance`) record their own trigger state (such as a blocked ticket note or a `FAIL` verdict with `Cause: direction`) before invoking `redirect`.
- **Zero unapproved mutation.** `redirect` never modifies specs, tickets, code, ADRs, or Acceptance charters before explicit human approval.
- **Fresh context windows.** Whenever `redirect` dispatches a helper subagent for blast-radius reading, launch it with a **fresh context window**, never a conversation fork.
- **Standalone-safe.** Works across local `.scratch/` and remote trackers whether or not `mattpocock/skills`, `decide`, or `acceptance` is installed.
