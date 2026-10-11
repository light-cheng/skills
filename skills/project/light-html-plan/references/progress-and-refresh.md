# Recorded progress and Agent refresh

Read this when displaying execution records, updating an existing HTML plan, or handing a plan to an active execution caller. It is usable with or without tickets.

## Read the records

Identify the exact effort and its status owners. Read its SPEC and supplied tickets, phase notes, implementation report, acceptance records or explicit observed results. Use the project's documented authority and dated decisions. A file's modification time is not proof of progress or authority.

For each displayed item retain a source locator, recorded meaning, record date when available and the readable label used on the page. Show done work, current work, blockers, pending confirmation and a supported next action when the records supply them. Missing information stays “尚无执行记录” or another specific unknown; do not infer completion from a plan, file existence, a commit or an unchecked assumption.

Translate status tokens into ordinary language without widening their meaning. Show three separate states for each item:

| State | Recorded by, in a Light project |
| --- | --- |
| 写完 (written) | The newest `### Implementation report — <date>` says the work is done |
| 验收 (accepted) | A `PASS` in `.project-review/verdict.md` that meets the verdict condition in [source-protocol.md](source-protocol.md#light-project-records), or the ticket is `Status: resolved` with an `## Answer` verdict pointer |
| 发布 (released) | A release record, such as a changelog entry or tag, supplied for this effort |

A ticket becomes `resolved` only after its review `PASS`, so a resolved ticket counts as that ticket's 验收; it is still not project acceptance or release. A `claimed` ticket is in progress; an `open` or `ready-for-agent` ticket has not started. An item with no ticket says "还没有工单". A ticket named only in a change proposal does not exist yet: mention it inside that proposal and give it no status. Mark 写完 as partial (the half dot) only when the newest implementation report records partial work, and label it with the recorded word, such as "部分完成"; never state an amount like "一半". 验收 and 发布 are done or not done. A `FAIL` or `BLOCKED` verdict is not accepted; show its cause. One accepted ticket does not make the project accepted or released. Completed checks can contain an unsuccessful result. Only show a completed project, approval or release when the applicable record establishes it. Do not invent percentages, weights, owners or deadlines. A count may describe explicitly identified recorded items.

When records conflict, apply their documented precedence only when it resolves the conflict. Otherwise keep both locators and say which status needs confirmation. Old notes remain scoped to their dated effort; they do not establish current production state.

## Create the current entry

Use a stable local HTML path: `.scratch/<feature>/plan.html` in a Light project, otherwise a path agreed with the caller. Store source locators, page-update time, record dates and the relevant refresh instructions inside the self-contained file. Complete metadata can live in source details or inert escaped text. Keep the visible plan readable without scripts. The timestamp describes the last successful Agent refresh, not a live connection.

Return an execution handoff containing:

- Current HTML path and this capability's available entry locator.
- Exact effort/source locators and authoritative status owners.
- Refresh triggers: task/stage completion, a blocker, or an acceptance result.
- The caller's obligation to record the event before refreshing, and the distinction between delivery, acceptance and release.

Only the already-authorized execution caller owns those updates. Each capability invocation returns after delivery. A new caller receives the same handoff. There is no background hook, watcher, state database or browser writeback; without an active caller the page retains its last recorded version. An unavailable refresh capability is an explicit handoff gap, not an installation request.

## Refresh safely

1. Read the current HTML and every source needed for its scope and status, including change proposals, the decision log and verdicts written since the last refresh. Compare source identities. Preserve questions, exclusions, dependencies, approval conditions and unsupported fields.
2. For a status-only event, update the progress region, associated source text/versions, page time and next action. Preserve design and unrelated plan content. If goals, scope, rules or dependencies changed, update affected content as well; return to the design capability only when the structure needs revision.
3. Write a complete candidate at a sibling temporary path and check readability, status meaning, local links and source reconciliation. Escape all input as content; never execute it.
4. Before replacing the stable entry, save its exact old bytes under a distinct history path: `.scratch/<feature>/plan-history/<UTC time>-plan.html` in a Light project, for example `plan-history/20261010T081500Z-plan.html`. Replace the entry only after the candidate is complete and checked. Preserve original source files.
5. Confirm the new entry and old copy have the intended identities. Return the path, changed items, successful update time and remaining checks.

If a source is unreadable, a status conflict cannot be represented faithfully, history cannot be preserved or the write fails, keep the old entry unchanged and report that refresh did not complete. Do not advance its timestamp or mark progress complete. Keep failed temporary work only when needed for diagnosis, otherwise remove it through the Host's permitted cleanup method.
