# Source records and review snapshots

Read this before composing the page. It is the Light-specific method for preserving authority while changing presentation.

## Read and identify

Record each input's type, readable locator, and generation-time version. For files, use a content fingerprint or a recognizable revision that identifies the actual working content; a Git commit alone misses uncommitted edits. For conversation inputs, retain an identifiable decision summary and date, without invented file paths or message IDs.

The page is a derived snapshot. Show the material locators, generation time, and generation-time versions within the file. A fingerprint identifies the read version; it is not an authenticity certificate. Offline snapshots show that version and do not claim live synchronization.

Give each source the date it states itself, or "无日期" when it states none; never borrow another record's date or a file's modification time. Keep the page-update time distinct from the dates of execution records. Scope progress to the supplied effort: an old SPEC's implementation report does not establish today's whole-project or production state. Explain a material age or scope limit in plain words near progress; complete locators and fingerprints belong in source details.

Give each main claim a nearby, descriptive source disclosure. Full paths and fingerprints can live in evidence details rather than the main reading flow. Keep source sections and all key commitments reachable. Verify code paths/line numbers against readable files; missing implementation stays unknown or explicitly a sketch.

## Light project records

In a Light project, read every record below that exists. All of them sit
under `.scratch/<feature>/` except `.project-review/`, which sits at the
project root. A missing record leaves its part saying "目前没有"; it is
not an error.

| Record | What to take | Part |
| --- | --- | --- |
| `spec.md` | Goal, scope, exclusions, decisions, acceptance | 1, and the baseline for 4 |
| `issues/NN-<slug>.md` | `Status:`, `Blocked by:`, acceptance items; under `## Comments` the newest `### Implementation report — <date>` (outcome, scope, verification, remaining findings, `Plan gap:`); `## Answer` with the verdict pointer | 2, 3 |
| `changes/NN-<slug>.md` (change proposals from `light-redirect`) | `Status:` (`proposed`, `approved`, `rejected`, `applied`), Why, Change, Open decisions, the recorded approval | 4 for every proposal; 3 also for `proposed` ones and open decisions |
| `decisions.md` (judgment log from `light-decide`) | Each row: question, answer, confidence, method, data, backend, applied, reason, final. A row whose `reason` is not `none` is a fallback or low-confidence row | 5 |
| `.project-review/verdict.md`, `state.md` and `findings.md` at the project root | `PASS`, `FAIL` or `BLOCKED`, its date, its Target, the cause of a `FAIL` (its `Cause:` and unmet criterion), open findings | 2 for acceptance and a `Cause: implementation` `FAIL`; 3 for a `Cause: direction` `FAIL` |
| `map.md` | Decisions so far, open fog | 1 and 3 |

Count a verdict only when `state.md` shows the same terminal status and the
verdict's Target is this feature's SPEC or one of its tickets. Otherwise show
it as "验收结论待核对" with both locators. Show a proposal's status and a
verdict exactly as recorded. A `proposed`
change is not yet a decision, and an `approved` one is not yet applied. A
judgment row whose `applied` is `false` was recorded but not used: show its
`final` value as what the work followed.

## Map commitments

Before authoring, make a compact record for each relevant goal, scope item, exclusion, constraint, accepted decision, sequence, owner, dependency, and acceptance condition:

| Field | Meaning |
| --- | --- |
| Source locator | File/section, ticket ID, or conversation decision |
| Commitment | The source's meaning, including any uncertainty |
| Page locator | One or more section IDs or anchors |
| Check | Preserved, explicitly unresolved, or a named gap |

After rendering, reconcile the record against the visible page. Rearranging and folding content are allowed; silently dropping a commitment is not. Readers must be able to trace important content to a source section or decision. Keep the map in your reply or in the page's source area. Write no project file other than `plan.html` and its `plan-history/` copy. The source/version inventory lives in the page.

Distinguish accepted decisions, unaccepted suggestions, assumptions, and open questions using explicit text labels. Preserve approval or completion states only when the input supplies evidence. Missing fields stay unknown or absent; do not fill layout slots with plausible values.

Keep open questions beside the behaviour or guarantee they affect. A concrete invented example must say it is explanatory, and a proposed variant must say it is unapproved. Local preview changes carry no feedback, decision or approval meaning. For a synthetic input, its stated decisions describe that fixture; they are not real project approvals.

## Preserve the authority owner

For clarification material, expose decisions and unanswered questions. For a formal SPEC, retain the contract. For tickets, show actual IDs, dependencies, and recorded states. For implementation evidence, quote the observed results and locators. Each remains authoritative in its own source; the HTML neither replaces nor modifies it.

For independent drafts, show the known input summary and label newly proposed structure or content as suggestions. Material conflicts retain both locators and the unresolved point. When a key source cannot be read or a conflict prevents faithful presentation, report the precise gap; do not manufacture a complete plan. A later refresh rereads sources and compares versions using [progress-and-refresh.md](progress-and-refresh.md). Preserve historical pages while updating the agreed current entry.

Return feedback with its source locator to the caller. Recommend the appropriate owner (`project-clarify`, `project-spec`, `project-tickets`, `light-redirect` when the feedback says the approved plan should change, or the implementation/acceptance caller) only when those capabilities are available; standalone use needs none of them. Stop without modifying records or invoking those user-invoked entry points.
