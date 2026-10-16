# Writing the page

Read this before writing any page text. The text is written and settled before design starts.

## The one test

For every heading and every sentence in the main reading flow, ask: could the reviewer point at it and say "wrong — the records do not say that"? If not, it is a topic word or a slogan. Rewrite it as a claim.

## Before and after

All examples come from a real review page for a resume-website SPEC. Every "after" uses only facts already in the SPEC or its implementation report.

| Before | After |
| --- | --- |
| 图片与加载 | 首页首次打开从约 1.03 MiB 降到 92–106 KiB。 |
| 中英文页面 | 切换语言后，访客停在同一页的同一位置。 |
| 公开 / 申请版分开 | 公开版简历不含电话和私人邮箱；完整联系方式只留在私下投递的版本里。 |
| 单点配置，可替换 | 公开邮箱只在一处配置，以后换别名只改这一处。 |
| 缺别名 → 原位置省略 | 你还没给公开邮箱时，联系区不显示邮箱，其他模块位置不变。 |
| 不回退成有效详情 | 地址不存在时显示对应语言的 404 页面，不会跳到某个真实的详情页。 |
| 灰色小字不够清晰：未通过，配色尚未改动 | 原有灰色小字对比度只有 4.45:1 和 4.16:1，低于 4.5:1 的要求。配色属于锁定的框架，改不改由你决定。 |
| 标签对应文字位置，不按实站尺寸或卡片数量绘制。 | (Delete it. Write "示意" once in the figure caption.) |
| 新内容的条件与文字放不下的处理 | 文字放不下时，先删重复，再挪进原详情区；还放不下，就留在候选稿里，不改版面。 |

What changed in each pair: a subject appeared, a verb appeared, and the reader learned something they can check.

## Rules

- **Headings inside a part are claims** with a subject and a verb. Only the five part names, navigation and the source area may use nouns.
- **One sentence, one thing.** Put the condition first: "如果……，就……" / "When…, …".
- **Name the actor.** Use "你" when the reader must act. Otherwise name who actually does it: the visitor, the build, the page.
- **A figure needs a sentence above it** saying what the figure proves. Labels inside the figure may be short.
- **Say each limit once**, where it changes a judgement. Merge page-wide disclaimers into one sentence in the source area.
- **Numbers carry units.** Mark which numbers are budgets or limits and which are measurements. Never invent a percentage, score or date.
- **Replace empty words with real verbs.** Cut words like 对应、相关、处理、情况、层面、维度、机制、能力、闭环、确保、进行 (or "handle", "ensure", "leverage", "mechanism") and say what actually happens.
- **Quote the source; do not reword quotes.** Technical names stay as written.
- **Prefer the reader's words.** "本地改动已完成，等你确认", not an internal lifecycle token such as `ready-for-human`. Keep the token in level 3 if it matters.

## Writing each part

- **这个项目是什么.** Write what the reader can now do or see when the plan is done, one claim per change. Read aloud, these claims tell the whole change. Under each, one rule, boundary or number supports it, and below that its source. The framework diagram labels each block with the component's name and a few words on what changes: "light-implement：收尾时写实现报告", not "light-implement：优化". Take each block's change size from the records: a component the plan adds is 新能力, one it names as out of scope is 不改. When the records do not say how much an existing component changes, the block says "改动大小未记录" rather than a guess.
- **做到哪一步.** Name each item by what it delivers, not by its ticket id. Its four facts answer in short lines: 在做什么, 已完成, 没完成, 证据. Write 写完, 验收 and 发布 as separate facts: "代码已写完，还没验收" rather than "已完成".
- **等你决定的事.** Each item says what you decide and what waits on it: "你选一个公开邮箱，联系区才会显示邮箱。" Lead with the choice, not the record type. List only what the records put on the user: a ticket whose `BLOCKED` or `FAIL` comment names a decision for you, a `proposed` change and its open decisions, a `FAIL` with `Cause: direction`, a report's `Plan gap:` that no change proposal answers yet, or an open question in the SPEC or map. A `FAIL` with `Cause: implementation` is the implementer's to repair: show it in 做到哪一步. A ticket that waits for another ticket (`Blocked by:` lists one that is not `resolved`) waits on work, not on you: say so in 做到哪一步. Unfinished work in an implementation report is the implementer's next step; it belongs in 做到哪一步.
- **跟当初相比哪里变了.** Each change says what was planned, what it is now, and who approved it: "原计划只做中文页；你在 10 月 9 日批准加英文页。" A `proposed` change says it is waiting on you and sits in 等你决定的事 too.
- **系统替你做了哪些判断.** Start each row with the question in plain words, then the answer and how sure: "这次改动要不要先换更强的模型？本机判断器说要（把握 0.83），但它还没校准，所以没采用；实际按 Agent 自己的判断：不用。" A question id such as `light-implement/offer-agent-config` appears only in the source line.
- **An empty part** says "目前没有" and, when useful, why: "目前没有：还没有记录过判断。"

## The status line

One sentence: date, state, next step. The date is the newest record's date; the page is a snapshot of the records on that date, so call it a snapshot, never live or real-time. Then, if needed, one short list of what the reader must do and what each item blocks.

> 本地改动已在 9 月 10 日交付。现在等你确认中英文页面和公开版简历。

## Read-aloud check

Before design, write only the status line and the main claim of each part in a plain text file. Read them aloud in order. They must explain what the project is, how far it got, what the reader must decide, what changed and what the system judged. If one needs its supporting line to make sense, rewrite it.

## After rendering

Read the whole page in the browser, including closed sections, captions, buttons and the footer. A fragment without a subject or verb in the reading flow is a defect. Fix it in the text. Do not hide it with styling.

Writing quality and appearance are for the user to judge by reading. Do not add a separate "remove AI phrasing" pass: removing words without adding a claim makes the page worse.
