# Proposal format

## File

`.scratch/<feature>/changes/<NN>-<slug>.md`. `<NN>` is the next unused two-digit
number in that directory, starting at `01`. Create `changes/` when it is
missing. Take `<feature>` from the trigger's path; when the trigger has no
path and `.scratch/` holds more than one feature, ask the user which one.

## Template

```markdown
# <NN> — <one plain sentence: what should change>

**Status:** proposed
**Raised by:** <calling skill or "user"> · <YYYY-MM-DD>
**Trigger:** <path#section of the report or verdict, or the user's words in quotes>

## Why
<What was found, in plain words, with a locator for each claim.>

## Change
- SPEC: <section> → <what changes>
- Tickets: <add | drop | split | reorder | change Blocked by | change acceptance> <ticket path> → <what changes>
- Charter: <Charter path + item this change affects, or none>
- Accept again: <resolved ticket paths whose acceptance this change reopens, or none>

## Open decisions
<Questions the user must answer before this can be applied, each with a recommendation, or none.>

## Not changed
<What stays as approved, so the reader sees the edge of the change.>

## Comments
```

- Write `none` for an empty line or section. Keep every heading and line.
- `Charter`: look for an acceptance Charter (`.project-review/charter.md` at
  the project root) whose `Source` is the SPEC or a ticket this change touches.
  Name only the items that the proposal as written changes. When only one
  option of an open decision would change a Charter item, say so in that
  option.
- When the user picks an offered option, update the `Change` and `Charter`
  lines to match it as part of recording the choice.
- Write for the user: plain words, no internal IDs without a short explanation.

## Status

| Status | Who sets it | When |
|---|---|---|
| `proposed` | `light-redirect` | On writing, and again after an edit to `Change`, `Not changed`, or an open decision beyond the options it offered |
| `approved` | `light-redirect`, on the user's explicit approval | The user approves this proposal, or asks for exactly its change to be made directly |
| `rejected` | `light-redirect`, on the user's explicit rejection | The user rejects this proposal |
| `applied` | `project-spec` or `project-tickets`; or the agent that made a hand edit the user insisted on | After every `SPEC:` and `Tickets:` line that is not `none` is applied; a hand edit is recorded as one |

Record each status change as one line under `## Comments`:
`- <YYYY-MM-DD> <status> — "<the user's words>"` (or the applying skill's name).
An applying skill that applies one line while the other is still pending
records `- <YYYY-MM-DD> SPEC applied — project-spec` or
`- <YYYY-MM-DD> Tickets applied — project-tickets` and leaves the status.
Recording the user's choice among offered options (including updating the
lines it settles), or a `Comments` line, is not an edit that resets the
status. An approval covers the proposal as the user
saw it, and every open decision needs the user's own answer. Never infer approval from
silence, from a model's judgment, or from an earlier approval of something
else.

## Map pointer

When `.scratch/<feature>/map.md` exists, a proposal is open fog until the
user answers it. On writing the proposal, append one line under the map's
`Not yet specified`:

```markdown
- Change proposed, waiting on the user: `<NN> — <title> → changes/<NN>-<slug>.md`
```

When you record `approved` or `rejected`, move that line to `Decisions so far`
and rewrite it with the answer:

```markdown
- Change approved <YYYY-MM-DD>: `<NN> — <title> → changes/<NN>-<slug>.md`
- Change rejected <YYYY-MM-DD>: `<NN> — <title> → changes/<NN>-<slug>.md`
```

`applied` needs no map edit. When the map lacks the section you need, skip
the line and tell the caller.
