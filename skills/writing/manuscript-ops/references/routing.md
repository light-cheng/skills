# Writing routes

## Current policy: needs-v2

Classify the current deliverable, source relationships, output purpose and real
management requirements. Workspace size, a delay caused by earlier blocked work,
one writer delegation, independent content review and a QA-only PDF do not
create a manuscript lifecycle requirement.

| Route | Use when | Finish |
| --- | --- | --- |
| Quick | A bounded low-risk text edit with clear meaning | Edit, run relevant checks, deliver and return |
| Structured | A bounded rewrite/report needing source, content, image or format review | Keep a compact brief, write the whole document, review and render as required, deliver and return |
| Project | Explicitly requested, or actual long/batched resumable work, locked derivatives or reproducible interdependent editions | Use the approved Project lifecycle and its gates |

Safety/privacy/legal and other high-stakes facts require corresponding content
review and factual evidence. They alone do not require Project. Shortness cannot
waive needed content review. Material unknowns require the corresponding source
or user decision; unrelated uncertainty never becomes an initialization gate.

The six dimensions remain explanatory evidence, scored `0`, `1`, `2` or unknown.
They do not force Project by their total. Do not derive manuscript scale from
repository file count. True lifecycle triggers select Project; risk and reviewer
count select checks. Derive triggers from the original task, not overhead the
Skill itself introduced. Explicit task facts outrank a model preference.

## Assessor input and output

Use `assets/templates/routing-input.json`. `task.scope` is `bounded`, `long-form`
or `unknown`; `task.lifecycle_required` records a real management requirement.
Dimensions carry their task-grounded evidence. Deliverables distinguish
`purpose: deliverable` from `purpose: qa`. Risk axes use the canonical manuscript
axis IDs; several formats or sources can still be a bounded Structured task.

The read-only assessor returns route, required review axes, initialization need,
unknowns, reasons and the next action. It may inspect an existing directory but
never creates it; a new authorized output directory is not a missing project.
It never starts another Skill or decides the content is accepted.

## Existing state: score-v1

Unversioned snapshots retain the original scoring and hard-trigger semantics
when replaying their approved Profile and gates. Explicit `routing_policy:
score-v1` is available for diagnosis. New tasks use `needs-v2`. Do not rewrite an
existing Project snapshot, receipt or hash because the new task default differs.
A scope change produces a traceable successor under its applicable authority.

## Examples

| Task | Route and checks |
| --- | --- |
| Correct spelling in one supplied paragraph | Quick; content check |
| Rewrite a short high-voltage training memo from confirmed material into DOCX | Structured; source/safety, image and real render checks |
| Write a sourced departmental report | Structured; source, content and selected format checks |
| Resume a long manual with accepted batches and review gates | Project; preserve existing state |
| Produce locked translations and interdependent editions | Project; source lock and derivative gates |
