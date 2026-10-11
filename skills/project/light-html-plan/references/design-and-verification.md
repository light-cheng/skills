# Build and check the page

Read this after the text is settled with [writing.md](writing.md). The page
helps a person see where a plan stands and what they must do. A reader should
get the state from the exhibits alone, and read prose only to learn why.

## Build from the skeleton

Start from [skeleton.html](../assets/skeleton.html) and inline
[plan.css](../assets/plan.css) whole in its `<style>`. The user approved this
visual system; use its classes and layouts as they are. Write its fixed labels and `lang` in
the reader's language. Change colour tokens only to match a theme the user
supplied.

Each part has a fixed layout. Wide screens use the horizontal axis; below
760px every row becomes one column.

| Part | Layout | Shows |
| --- | --- | --- |
| Top | Status on the left; on the right, a card with the most urgent thing waiting on the user | Snapshot date, title, status line |
| 这个项目是什么 | One card per component in a row (`--n` = component count) | Change size, name, what changes, acceptance; struck-through out-of-scope items |
| 做到哪一步 | One progress card per item in a row; when tickets map one-to-one to components, same order and `--n`, so each sits under its component | Track 写完 → 验收 → 发布, then 在做什么 / 已完成 / 没完成 / 证据 |
| 等你决定的事 | One card per decision: question and why on the left, options and what it blocks on the right | The record and options on record |
| 跟当初相比哪里变了 | Change cards two per row, each with 原计划 → 现在 side by side | Status, approver, reason, path |
| 系统替你做了哪些判断 | Judgment cards two per row, each with a confidence bar | Answer, what the work followed, who judged, raw log row in `details` |

A component with no ticket gets a dashed gap card in its column. Counts sit in
one row of their own, never in columns above cards they do not label. A part
with nothing in it keeps its heading and says "目前没有".

**Change size** in the framework diagram has four values: 重点改动, 小改,
新能力, 不改. Each block shows its value as a text label and a colour; colour
never carries it alone. A block whose size the records do not give says
"改动大小未记录" in a neutral style. A legend next to the diagram lists every
value the diagram uses.

**Short lines, not paragraphs.** Card text is a phrase or one sentence. Use
native `details`/`summary` only for raw records and long evidence.

Inside part 1, give a claim its own exhibit only when the exhibit lets the
reader check something prose makes hard: a before/after, a boundary, a flow,
two versions side by side, or a chart of supplied measurements. Use real
records and screens when supplied. Label a sketch or invented example once, in
its caption. One exhibit per claim; a second exhibit means a second claim.

Put each question for the user both in 等你决定的事 and beside the claim it
changes; beside the claim, make it a link to its card there. A preview selection is a reading state, never a decision.

The five parts, their order and their layouts are fixed. The number of cards
follows the records.

Before building, check: every part has its exhibit or "目前没有", every open
question has a location, every commitment and record has a home.

## Layout

The first screen shows the part bar, the status line and the card of what
waits on the user. Keep the source reference next to its claim. The source
area at the end lists each input's path, record date and SHA-256, plus one
sentence on scope and limits. It does not embed the full source text.

Show quantitative charts only from supplied observations or explicit targets,
and label the two differently. A confidence bar's width is the logged
confidence; draw no thresholds the records do not give. Counts describe
recorded items, never a made-up completion percentage.

A separate design capability is optional and only for a page the user asks to
design differently. Follow [design-handoff.md](design-handoff.md): it receives
the settled text and returns layout, colour and type. If it changes a
sentence, restore the sentence.

## Single file

Keep prose and exhibits in semantic HTML. Inline the stylesheet and the
skeleton's theme script. Scripts may reveal a claim or preview
an unapproved alternative, with keyboard-operable controls and local effects
only. The page does not export feedback, record approvals, start work or keep
a backend.

The page needs no remote fonts, CDN, account or service. Use system fonts.
Keep readable line lengths, visible focus, and text labels beside status
colours. Support `prefers-color-scheme` unless the user supplied a theme; a
theme control must win over the system in both directions. Respect reduced
motion.

Long identifiers wrap; the body fits the viewport. Escape all source text as
content. Essential claims stay readable without scripts.

## Check

1. Read the status line and each part's main claim alone. They must tell what
   the project is, how far it got, what the reader must decide, what changed
   and what the system judged.
2. Read the whole page, including closed sections. No fragment without a
   subject or verb in the reading flow, and no paragraph doing an exhibit's
   job.
3. Reconcile the page with the commitment map: exclusions, order, owners,
   dependencies, acceptance, proposals and judgments all reachable.
4. Open the local file in a browser at 1440px and 390px, light and dark. Check
   for horizontal overflow, external requests and console errors. Use the
   keyboard on controls and disclosures. Check that every class on the page is
   defined in plan.css and that no other stylesheet was added.
5. Record the browser used and any check you could not run. Agent observation
   is not user acceptance; the user judges the writing and the look.

Run checks outside the user's project, so it ends with only the page and its history copy. Deliver the local file without installing services or publishing it.
