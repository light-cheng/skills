---
name: light-decide
description: Answer a bounded judgment inside a workflow (pick one of several legal options, answer yes or no, or rate a level on an ordered scale) through a typed decision source when one is allowed and available, otherwise by your own judgment, and log it. Use when a skill reaches such a judgment. Not for user decisions, approvals, verdicts or permissions.
---

# Light Decide

A **bounded judgment** is a question with a fixed set of legal answers that a
workflow can act on: one of several options (`choice`), yes or no (`yes_no`),
or a level on an ordered scale (`score`). `light-decide` answers it, says how
sure the answer is, and logs it. The caller decides what to do next.

## What it judges

Judge only what the caller could judge itself. Leave these to the user or to
evidence: user-owned decisions, approval of a SPEC, ticket graph or change
proposal, finding dispositions, `PASS`/`FAIL`/`BLOCKED`, and any permission.
When only one option is legal, return it without asking any source.

## Steps

1. **Frame.** Take from the caller the legal options, the feature name when it
   has one, and a stable question id `<caller>/<slug>`, where `<caller>` is the
   calling skill's name. Without an id, form one from a short kebab-case slug
   of the question; a new id stays uncalibrated until the user calibrates it.
   Write the question in plain words a non-engineer can read. Ordered levels use `score`, two-way questions `yes_no`, the rest
   `choice`. Build a minimal state: the request excerpt and the facts the
   question needs. Leave out source code, diffs, credentials and personal data.
   Done when the question, kind, options and state exist.
2. **Find the data limit.** Read `Decision data:` in the project's
   `docs/agents/light-project.md`. No line means `on-device`. `off`, or a value
   you do not recognize, means self-judgment with reason `off`; nothing the user says in this run lifts
   `off` or widens the limit. The user may narrow it or name a source within it.
3. **Pick a source** with [selection](references/selection.md). Done when you
   have named one source that is verified available on this Host and within the
   limit, or chosen self-judgment. When no source is found and one would clearly
   help, finish this judgment by self-judgment, then offer setup once with
   [setup](references/setup.md). Never start setup without the user's yes.
4. **Ask** through the script or MCP path in [selection](references/selection.md).
   A timeout, error or malformed reply becomes a fallback, never a retry loop.
5. **Normalize and apply policy** with [formats](references/formats.md). Apply
   the source's answer only when the source is calibrated for this question id
   and its confidence meets the threshold. Otherwise make your own judgment the
   final answer and keep the source's answer on record.
6. **Log** one row to `.scratch/<feature>/decisions.md` as described in
   [formats](references/formats.md). When the feature is unclear, return the
   row to the caller instead.
7. **Return** the normalized result to the caller and stop.

## Contract with callers

- **Optional.** When this capability is missing, unavailable or declined, the
  caller continues with its original behavior. Nobody reports `BLOCKED` or asks
  for an installation because of it.
- **Caller records first.** The caller writes the event into its own record
  before calling. `light-decide` logs only the judgment.
- **Returns, never takes over.** It hands the result back. It never starts a
  user-invoked skill.
- **Grants nothing.** Its answer never changes the caller's permissions,
  approval state or verdict.
