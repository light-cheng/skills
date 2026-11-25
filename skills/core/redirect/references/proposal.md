# Change Proposal Format and Tracker Operations

## Tracker targets

Read `docs/agents/issue-tracker.md` first to match how the repository stores specs, tickets, and wayfinding maps:

1. **Local markdown** (configured in `docs/agents/issue-tracker.md`, or used silently by default when `docs/agents/issue-tracker.md` is absent):
   - Write the Change proposal to `.scratch/<feature>/changes/<NN>-<slug>.md`, where `<NN>` is the next unused two-digit number starting at `01`. Create `changes/` if missing.
   - Infer `<feature>` from the trigger path (`.scratch/<feature>/...`). If `.scratch/` holds multiple features and the trigger gives no path, ask the user which feature applies.
   - Link affected artifacts relative to `.scratch/<feature>/`: `spec.md`, `issues/<NN>-<slug>.md`, `map.md`, and `acceptance/` (or `.scratch/acceptance/<slug>/`).
2. **GitHub Issues (`gh`)**:
   - In forked repositories, run `gh repo view --json nameWithOwner` before writing so comments or label edits target the user's repository rather than an upstream parent.
   - Fetch the relevant issue(s) with `gh issue view <number> --json number,title,body,labels,comments` (or `gh pr view <number>` when PRs act as the request surface).
   - Publish the Change proposal using the template below as a comment on the active ticket (or on the parent spec issue when no child ticket is active) via `gh issue comment <number> --body "..."` with a heredoc. When `.scratch/<feature>/` is also active locally (for example holding `acceptance/` charters or `decisions.md`), mirror the file at `.scratch/<feature>/changes/<NN>-<slug>.md` referencing the issue comment URL.
   - If the blocked ticket carries the `ready-for-agent` label, replace it with `needs-info` (`gh issue edit <number> --remove-label "ready-for-agent" --add-label "needs-info"`, mapped through `docs/agents/triage-labels.md` when present).
3. **GitLab Issues (`glab`)**:
   - Fetch the relevant issue(s) with `glab issue view <number> --comments` (or `glab mr view <number> --comments`).
   - Publish the Change proposal note via `glab issue note <number> --message "..."` with a heredoc (and mirror to `.scratch/<feature>/changes/<NN>-<slug>.md` when a local `.scratch/<feature>/` directory is active).
   - Replace `ready-for-agent` with `needs-info` via `glab issue update <number> --unlabel "ready-for-agent" --label "needs-info"` (mapped through `docs/agents/triage-labels.md` when present).
4. **Custom issue tracker**:
   - Follow the read, comment, and status rules written in `docs/agents/issue-tracker.md`. Keep any local files inside `.scratch/<feature>/changes/` so the repository root stays clean.

## Template

```markdown
# <NN>: <one plain sentence stating what should change>

**Status:** proposed
**Raised by:** <calling skill or "user"> (<YYYY-MM-DD>)
**Trigger:** <file#section, #issue comment URL, or quoted user request>

## Why
<What broke or changed in plain words, with an exact file locator, ADR reference, or issue link for every claim.>

## Change
- Spec: <spec.md section or #issue section -> exact revision, or none>
- Tickets: <add | drop | split | reorder | change Blocked by | change acceptance> <ticket path or #issue -> exact revision, or none>
- ADR: <docs/adr/ path contradicted or superseded -> proposed update, or none>
- Acceptance charter: <charter path under .scratch/ + criterion ID -> exact revision, or none>
- Re-verify: <resolved ticket paths or #issues whose acceptance reopens, or none>

## Open decisions
<Questions the user must answer before revisions apply, each with a recommended option and trade-off, or none.>

## Not changed
<Approved requirements, boundaries, and tickets that stay as planned.>

## Comments
```

Template rules:

- Write `none` for any line or section that does not apply; keep all headings and `Change` keys intact.
- On remote trackers without local `changes/` files, assign `<NN>` sequentially across Change proposals on that spec or effort starting at `01`.
- Check `docs/adr/` (and context-scoped ADRs per `docs/agents/domain.md` when present). Surface any ADR contradiction explicitly under `- ADR:` rather than overriding an accepted decision silently.
- Check `.scratch/<feature>/acceptance/` and `.scratch/acceptance/` for frozen Acceptance charters whose source spec or tickets overlap the change. When only one branch of an open decision alters a charter criterion, note that impact on that option and update `- Acceptance charter:` once the user chooses.
- Write for the human reader: use the project's `GLOSSARY.md` terms and refer to issues by title alongside their path or `#number`.

## Status lifecycle

| Status | Who sets it | When |
| --- | --- | --- |
| `proposed` | `redirect` | On initial publication, and whenever `Change`, `Not changed`, or `Open decisions` is edited beyond settling offered options |
| `approved` | `redirect`, after explicit human approval | Every open decision has the user's answer and the user approves the proposal |
| `rejected` | `redirect`, after explicit human rejection | The user rejects the proposed change |
| `applied` | `/to-spec`, `/to-tickets`, `acceptance`, or the agent executing an approved fallback update | Every non-`none` `Spec:`, `Tickets:`, `ADR:`, and `Acceptance charter:` item has been applied |

Record each transition under `## Comments` in local files, or as a follow-up tracker comment on `gh` / `glab` issues:

- `- <YYYY-MM-DD> approved: "<the user's words>"`
- `- <YYYY-MM-DD> rejected: "<the user's words>"`
- `- <YYYY-MM-DD> Spec applied (/to-spec)` or `- <YYYY-MM-DD> Tickets applied (/to-tickets)` when applied in stages
- `- <YYYY-MM-DD> applied (direct fallback): "<summary of updated files or #issues>"`

Never infer approval from silence, model confidence, or an earlier approval of a different item.

## Handling the answer

- **Approval with unanswered open decisions**: Keep `**Status:** proposed` and ask the remaining open decision(s). `"Go with your recommendations"` counts as an explicit answer for all recommended options; update `Change` and `Acceptance charter` lines to reflect the chosen options before setting `approved`.
- **Answer modifies scope or approach**: Update the proposal to reflect the user's counter-proposal, re-check blast radius across the spec and tickets, and confirm approval if new impacts appear.
- **No answer yet**: Leave the proposal `proposed` and stop cleanly. When the user answers in a later turn or fresh session, resume at Step 5 on that existing proposal rather than creating a duplicate.
- **"Skip the proposal and edit it directly"**: Still write the Change proposal so the blast-radius check and audit log exist. Treat the user's instruction as `approved` only when the full blast radius matches exactly what they asked to change; if scanning uncovered hidden contradictions in other tickets, ADRs, or an Acceptance charter, surface those extra items and confirm before editing.

## Routing and Graceful fallback

Base workflow authoring skills (`/to-spec`, `/to-tickets`, `/grill-with-docs`, `/wayfinder`) are user-invoked (`disable-model-invocation: true`), so host harnesses may hide them from the model's own tool list even when installed.

When a Change proposal reaches `approved`:

1. **With Base workflow handoff**: Give the user the exact invocation for their host (such as `/to-spec <proposal-ref>` and `/to-tickets <proposal-ref>` in Claude Code, or `$to-spec <proposal-ref>` and `$to-tickets <proposal-ref>` in Codex), listing `/to-spec` before `/to-tickets` when both apply.
2. **Graceful fallback (standalone or explicit direct update)**: When `mattpocock/skills` is not installed, or when the user asks you to apply the approved revision directly now:
   - Update `.scratch/<feature>/spec.md` or the remote spec issue (`gh issue edit <n> --body "..."` / `glab issue update <n> --description "..."`) with the exact approved `Spec:` changes.
   - Update `.scratch/<feature>/issues/<NN>-<slug>.md` (one file per ticket, keeping `Blocked by:` edges accurate) or remote tracker tickets (`gh issue create`, `gh issue edit`, `gh issue close`, or `glab issue create`, `glab issue update`, `glab issue note`, `glab issue close`), restoring `ready-for-agent` on tickets that are now unblocked and ready.
   - Update `**Status:** applied` and log the fallback application entry under `## Comments` (or post the closing status comment on the tracker issue).
3. **Frozen Acceptance charters**: Route charter updates through `acceptance` (Charter scale), citing the approved Change proposal locator as authorization. Only when `acceptance` is unavailable and the user explicitly confirms editing the charter directly should you update `.scratch/<feature>/acceptance/` (recording the approval locator inside the charter).

## Map pointer

When `.scratch/<feature>/map.md` exists locally, or an open `wayfinder:map` issue exists on GitHub/GitLab, treat an unanswered Change proposal as open fog:

- On writing a `proposed` Change proposal, append one line under `## Not yet specified`:

```markdown
- Change proposed, waiting on user: [<NN>: <title>](changes/<NN>-<slug>.md)
```

  (On GitHub/GitLab maps, link the issue or comment URL in place of `changes/<NN>-<slug>.md`.)

- On recording `approved` or `rejected`, remove that line from `## Not yet specified` and append one line under `## Decisions so far`:

```markdown
- [<NN>: <title>](changes/<NN>-<slug>.md): Change approved <YYYY-MM-DD> (<one-line gist>)
- [<NN>: <title>](changes/<NN>-<slug>.md): Change rejected <YYYY-MM-DD> (<one-line reason>)
```

`applied` requires no further map edit. If the map lacks `## Not yet specified` or `## Decisions so far`, skip the map edit and note that in your report.
