---
name: light-html-plan
description: Show where a plan stands as one readable offline HTML page - what the project is, how far it got, what waits on the user, what changed since approval, and what the system judged for them - built from SPECs, tickets, change proposals, decision logs and review verdicts. Refresh `.scratch/<feature>/plan.html` when it exists and a stage finished, work got blocked, or an acceptance result arrived. Use when HTML is requested or plan relationships need a visual overview; plain plan wording alone is not a trigger.
---

# Light HTML Plan

`light-html-plan` turns plan records into one offline page that a person can
read and check. The records keep their authority; the page is a dated
snapshot. In a Light project the page is `.scratch/<feature>/plan.html` and
earlier versions go to `.scratch/<feature>/plan-history/`. Elsewhere, agree a
path with the caller.

## The page has five parts, in this order

1. **这个项目是什么** (what this project is): what the plan changes, with a
   framework diagram. Each block shows the component's name (in a skill
   collection, the Skill's name) and what changes in it, marked 重点改动,
   小改, 新能力 or 不改 by colour and by text.
2. **做到哪一步** (how far it got): each work item shows 在做什么, 已完成,
   没完成 and 证据. 写完, 验收 and 发布 (written, accepted, released) are three
   separate states.
3. **等你决定的事** (what waits on you): tickets stopped on a user decision,
   `proposed` change proposals, open questions, a report's `Plan gap:` no
   proposal answers yet, and a `FAIL` caused by the plan itself, each with what
   it blocks.
4. **跟当初相比哪里变了** (what changed since approval): each change proposal
   with what it changes, its status, and who approved it.
5. **系统替你做了哪些判断** (what the system judged for you): each logged
   judgment, starting with the question in plain words, then the answer, how
   sure, and who judged. Rows whose logged `reason` is not `none` come first. Ids
   appear only as the source.

A part with nothing in it says "目前没有" ("none so far"). Write part names in
the reader's language. Above part 1, a status line gives the record date,
where the work stands, and the next step.

Every heading and main sentence inside a part is a **claim**: the reader can
point at it and say "wrong". Show relationships, progress and numbers as
diagrams, strips, tables or charts; prose says what each exhibit proves.

## Steps

1. Decide creation or refresh. Read the materials, output path, and existing
   HTML when refreshing. Resolve unreadable inputs before claiming a complete
   result.
2. Read [source-protocol.md](references/source-protocol.md) and map every
   commitment and record to a source and a part. For recorded progress or a
   refresh, read [progress-and-refresh.md](references/progress-and-refresh.md).
3. Read [writing.md](references/writing.md). Write the status line and each
   part's claims as plain text first. Read them aloud and fix them until they
   tell the whole state.
4. Build the page from [skeleton.html](assets/skeleton.html) with
   [plan.css](assets/plan.css) inlined, following
   [design-and-verification.md](references/design-and-verification.md).
   Design starts only after the text is settled. A refresh keeps the page's
   existing design.
5. Read the whole rendered page, including closed sections. Fix wording in the
   text, not in CSS. Reconcile it with the commitment map. Check 1440px and
   390px widths, light and dark themes, overflow, and that the file makes no
   external requests. Do this on every refresh too. When you cannot open a
   browser, return `Visual check: not run` and the reason.

## Return and stop

Return the HTML path, source locators with SHA-256, what changed, and the
checks done and not done. For an active execution, include the refresh
handoff from the progress reference.

The page lists sources by path, date and SHA-256; it does not embed their full
text. The user judges whether the page reads plainly and looks good by reading
it; report the checks you ran and leave that verdict to them.

This capability does not approve a plan, split tickets, change task or
proposal state, publish, or install anything. Source questions go back to
their owner; it does not invoke another user-invoked Skill.
[ATTRIBUTION.md](ATTRIBUTION.md) records the upstream reference and Light
changes.

## Contract with callers

- **Optional.** When this capability is missing or declined, the caller keeps
  its original behaviour and the page keeps its last version. Nobody reports
  `BLOCKED` or asks for an installation because of it.
- **Caller records first.** The caller writes the event (implementation
  report, verdict, proposal) before asking for a refresh. The page reads
  records; it never fills them in.
- **Returns, never takes over.** It returns after delivery.
- **Grants nothing.** The page shows state; it never approves, accepts or
  releases anything.
