# Charter Scale Workflow (`init` | `run` | `resume`)

Complete lifecycle, durable `.scratch/` state layout, stopping rules, closeout ordering, `redirect` handoff, and issue-tracker synchronization for **Charter scale** acceptance.

## Entry modes

- `init`: inspect the approved source, select the domain Profile, freeze `charter.md`, and initialize `state.md` (`Status: READY`).
- `run` (also accepts `review` as a compatibility alias from external callers): execute up to 3 bounded evidence, Critic review, validation, Producer repair, and fresh Evaluator rounds to reach a terminal verdict (`PASS`, `FAIL`, or `BLOCKED`).
- `resume`: read existing durable records, verify coherence across `charter.md`, `state.md`, and `findings.md`, refresh only stale or missing evidence, and continue from the recorded next action without rewriting prior round files.

When invoked at Charter scale without an explicit mode, infer `resume` if an active non-terminal `state.md` already exists for the target, `init` + `run` when an approved source exists and no Charter has been frozen yet, or ask the user if multiple targets compete.

## Durable `.scratch/` state tree

Store all Charter-scale records inside `.scratch/` so target repository roots stay clean:

- Feature-scoped work (matching `.scratch/<feature>/spec.md` or `.scratch/<feature>/issues/`): `.scratch/<feature>/acceptance/`
- Standalone milestone, package, or manuscript run without a feature folder: `.scratch/acceptance/<slug>/` (or an explicit `.scratch/...` path configured in `docs/agents/light-project.md`)

Keep every durable file inside that `.scratch/` acceptance directory so the target repository root stays untouched. Preserve every approved Charter revision, retired finding record, and completed round file by appending new revisions or rounds rather than overwriting history.

```text
.scratch/<feature>/acceptance/
|-- charter.md
|-- state.md
|-- findings.md
|-- verdict.md
|-- changes.md
`-- rounds/
    `-- round-01/
        |-- producer-evidence.md
        |-- critic-findings.md
        |-- finding-disposition.md
        |-- repair-plan.md
        |-- repair-evidence.md
        `-- evaluator-verdict.md
```

### Transaction coherence invariants

`charter.md`, `state.md`, and `verdict.md` form one atomic acceptance transaction:

1. `charter.md` defines the frozen baseline (`Charter revision`, `Source`, `Source revision or identity`, `Profile`, plus `Fixed point` and `Implementation scope` for `software`).
2. `state.md` is authoritative for live lifecycle state (`Status: INIT | READY | CRITIC | REPAIR | EVALUATE | PASS | FAIL | BLOCKED`, `Charter revision`, `Profile`, `Round` >= 1, `Independence`, and `Next action`). While `Status` is non-terminal (`INIT`, `READY`, `CRITIC`, `REPAIR`, `EVALUATE`), any earlier `verdict.md` is stale and non-authoritative.
3. `verdict.md` is authoritative only when `state.md` is terminal (`PASS`, `FAIL`, `BLOCKED`) and both files match `charter.md` on `Charter revision`, `Profile`, and `Round`.
4. Every canonical identity field (`Charter revision:`, `Profile:`, `Round:`, `Status:` in `state.md`; `Verdict:`, `Charter revision:`, `Profile:`, `Round:` in `verdict.md`, plus `Reviewed implementation revision:` for `software` and `Cause:` on `FAIL`) is a strict singleton. Missing, duplicate, or aliased verdict fields (`Result:`, `Outcome:`, `State:`) fail closed (`BLOCKED`).

## `init` steps

1. **Locate and verify the acceptance source.** Read the approved `spec.md`, ticket files, `ManuscriptBrief`, or package contract, plus `docs/agents/light-project.md` when present. Never synthesize a Charter from Producer claims or passing test logs alone. If the source is missing or unapproved (`Approval: pending`), record `Status: BLOCKED` in `state.md` with the smallest unblock action and stop.
2. **Select the Profile.** Honor an explicit caller or `docs/agents/light-project.md` profile when valid; otherwise choose the narrowest matching profile:
   - [software.md](profiles/software.md): executable code, scripts, or repository diffs.
   - [manuscript.md](profiles/manuscript.md): books, multi-format documents, outlines, semantic batches, or translations (`manuscript-ops` gates).
   - [agent-skill.md](profiles/agent-skill.md): installable Agent Skill packages (`SKILL.md` + metadata/references/scripts).
   - [specification.md](profiles/specification.md): specs, briefs, ticket graphs, or formal contracts audited against upstream authority.
   - [generic.md](profiles/generic.md): bounded deliverables where no narrower profile applies.
3. **Freeze `charter.md`.** Populate every section in [charter-and-evidence.md](charter-and-evidence.md). Map every spec user story into at least one `AC-<n>` or `Out of scope` (flag unmapped stories before starting `run`). For `software`, freeze `- Fixed point: <full 40-char Git SHA>` and `- Implementation scope: <repo-relative POSIX literal paths separated by ';'>` (never inferred from changed diff files; return `BLOCKED` if component scope is ambiguous). Do not freeze the final implementation commit SHA in `charter.md`, because bounded repairs advance it before `verdict.md` records `Reviewed implementation revision`.
4. **Initialize `state.md` and `findings.md`.** Set `Status: READY`, `Round: 1`, `Max rounds: 3` (unless configured otherwise), `Independence: required`, and `Next action: collect round-01 producer evidence`.

## `run` steps

Confirm `state.md` is `READY` (or resuming into a permitted round <= `Max rounds`) with an approved `charter.md`.

1. **Collect Producer evidence (`rounds/round-NN/producer-evidence.md`).** Execute verification checks and label every item accurately per [charter-and-evidence.md](charter-and-evidence.md).
   - **Ticket implementation report intake (round 1):** When reviewing claimed tracker tickets that carry an implementation report under `## Comments`, verify its `Fixed point` and scope match `charter.md` (`BLOCKED` on conflict), re-run every listed verification command in the current session rather than trusting reported passes, import any open findings into `findings.md` as `pending`, and check any reported plan gap against `charter.md`. If a ticket reports `Outcome: BLOCKED`, return `BLOCKED` immediately.
2. **Run Critic review (`Status: CRITIC`).** Dispatch the **fresh-context** read-only reviewer(s) per [reviewer-protocol.md](reviewer-protocol.md), passing `findings.md` active entries as `Previous findings`. Save candidate output in `rounds/round-NN/critic-findings.md`.
3. **Validate dispositions (`rounds/round-NN/finding-disposition.md`).** Assign or reuse stable `F-###` IDs in `findings.md` and classify each candidate as `confirmed`, `rejected`, `duplicate`, or `out-of-scope`.
4. **Apply bounded Producer repair when needed (`Status: REPAIR`).**
   - Enter `REPAIR` only when at least one `confirmed` blocking finding has a bounded repair inside the Charter's frozen scope. When zero `confirmed` blocking findings exist, skip `REPAIR` and proceed directly to step 5 (`EVALUATE`).
   - If resolving a `confirmed` finding requires changing requirements, adding/splitting tickets, altering architecture, or editing `charter.md`, **do not repair it**: proceed to closeout as `FAIL` (`Cause: direction`) when the frozen baseline cannot hold, or `BLOCKED` when external authority/access is missing.
   - Otherwise, record `repair-plan.md`, apply the minimal in-scope Producer fix (for `software`, commit the repaired candidate in scope before re-evaluation), re-run verification checks into `repair-evidence.md`, and re-run the **fresh-context** Critic reviewer (`Previous findings` supplied) across remaining rounds (up to `Max rounds`, default 3) until `confirmed` Critic findings clear or the round/progress bound stops convergence.
5. **Dispatch independent fresh-context Evaluator (`Status: EVALUATE`).**
   - Launch a **separate fresh-context** read-only Evaluator subagent (distinct from all Critic subagents) with the Evaluator packet in [reviewer-protocol.md](reviewer-protocol.md). If independent subagent context is unavailable, transition to `BLOCKED` (`independence: unavailable`).
   - Record criterion-by-criterion audit results in `rounds/round-NN/evaluator-verdict.md`.
   - If the Evaluator uncovers an unmet `AC-<n>` that has a permitted bounded in-scope repair AND `Round < Max rounds` with material progress, record the new/reopened `F-###` as `confirmed` in `findings.md` and open `round-(NN+1)` at `CRITIC`. Otherwise proceed to terminal closeout.

## State machine and stopping rules

```text
INIT -> READY -> CRITIC -> REPAIR -> EVALUATE -> PASS
                    |                   |
                    +-------------------+------> FAIL (Cause: implementation | direction)
                                        |
                    bounded repair path +------> CRITIC (next round, up to Max rounds)
any state -------------------------------------> BLOCKED
```

- **`PASS`:** Every frozen `AC-<n>` and applicable Profile axis has verified, accurately labeled evidence; zero `confirmed` blocking findings remain; `charter.md` was not silently altered; for `software`, `Implementation scope` has zero uncommitted tracked, untracked, or ignored files; and the fresh Evaluator accepts the baseline.
- **`FAIL`:** A frozen `AC-<n>` or mandatory Profile condition is demonstrably unmet and no permitted bounded repair remains (either in-scope repair failed to satisfy a valid baseline -> `Cause: implementation`, or the frozen spec/ticket/charter itself is flawed or contradictory -> `Cause: direction`).
- **`BLOCKED`:** Required baseline source, user approval, credentials/environment, required renderer/runtime, or fresh independent subagent context is unavailable; durable records conflict; two consecutive rounds make zero material progress; or `Max rounds` (default 3) expires while repairable gaps remain unsettled. Every `BLOCKED` record names the exact blocker, attempted check, owner of the unblock, and smallest next action.

## Safe closeout ordering

Write terminal artifacts in strict fail-closed order so consumers never read a stale or partial verdict:

1. **Write `verdict.md`** for the evaluated `Round` with all singleton fields (`Charter revision`, `Profile`, `Round`, `Verdict: PASS | FAIL | BLOCKED`, `Independence`, plus `Reviewed implementation revision` for `software` and `Cause: implementation | direction` for `FAIL`).
2. **Verify singleton coherence** across `charter.md` and `verdict.md`.
3. **Transition `state.md` to terminal** (`Status: PASS | FAIL | BLOCKED` with matching `Charter revision`, `Profile`, and `Round`).

## Tracker ticket closeout and `redirect` handoff

1. **Tracker closeout (when reviewing tracked issues):** Consult `docs/agents/issue-tracker.md` (defaulting to `.scratch/<feature>/issues/<NN>-<slug>.md` local markdown conventions when absent):
   - **`PASS`:** On local markdown tickets, append an `## Answer` section citing `verdict.md`, `Charter revision`, and `Round`, update the ticket's `Status:` line to `resolved`, and when `.scratch/<feature>/map.md` exists, append a one-line gist + verdict link under `Decisions so far` (unblocking downstream tickets). On remote GitHub/GitLab trackers (`gh` / `glab`), post the acceptance summary comment and close/resolve per repo convention.
   - **`FAIL` or `BLOCKED`:** Keep the ticket claimed/open and append one entry under `## Comments` (or a remote tracker comment) linking `verdict.md` and naming the unmet criterion or blocker (including `Cause: implementation | direction` on `FAIL`).
   Leave ticket problem statements and unrelated tickets untouched.
2. **Direction failure -> `redirect`:** When `verdict.md` records `Verdict: FAIL` with `Cause: direction`, invoke `redirect` after tracker closeout, passing the `verdict.md` path so `redirect` drafts a **Change proposal** under `.scratch/<feature>/changes/` (or on the active tracker issue) for human approval before `/to-spec`, `/to-tickets`, or a new Charter revision in `changes.md` is applied. **Graceful fallback:** When `redirect` is absent or declined, leave `verdict.md` and the ticket's `FAIL (Cause: direction)` comment as the authoritative handoff and ask the user whether to revise the spec/charter.

## `resume` rules

1. Read `state.md`, `charter.md`, `findings.md`, and the latest `rounds/round-NN/` directory before acting.
2. Verify `Charter revision` and `Profile` match across records; any contradiction sets `Status: BLOCKED` without overwriting prior files.
3. Refresh only stale or missing checks (for example, if working-tree commits moved since an interrupted `REPAIR`), then resume from `state.md`'s recorded step, appending new round artifacts rather than editing completed ones.
