# Changes and interpretations

## CP-001 — ticket `resolved` counts as ticket-level 验收 (2026-10-10, Producer interpretation, not a user decision)
Design §4 item 3 maps "ticket resolved" to 交付. Since commit 57a148e (stage 0+2), TICKET-CONTRACT says `project-review` sets `Status: resolved` only after a `PASS`, so a resolved ticket has passed review. The candidate therefore shows it as that ticket's 验收, and keeps "not project acceptance or release" explicit. 写完 comes from the implementation report. Raised by Critic F-006. Flag to the user in the step report.

**User decision (2026-10-10):** CP-001 confirmed. User's words, answering the two open questions (visual direction and CP-001): "都确认了，非常好，我很满意".

## CP-002 — built-in visual system (2026-10-10, user decision)
User feedback on generated pages: "UI还是有点简陋，这种内容块感觉像是在看几年前的模型写出来的…怎么能帮他表的简约高级一点". Prototype v1 (vertical) followed; user: "我虽然说了之前的内容框很丑，是因为框的UI丑，并不是完全否决了用内容框把内容横向显示…变成了瀑布流…考虑一下哪些内容需要用到X轴横向展示". Prototype v2 (`.scratch/light-html-plan/ui-proto/plan.html`) approved: "都确认了，非常好，我很满意".
Decision: the package ships its own visual system (`assets/plan.css` + `assets/skeleton.html`) derived from prototype v2, and pages must use it. huashu-design stays optional for bespoke design. This reopens the round: Charter revision 2 adds AC-10 (page uses the shipped visual system and its horizontal layouts); scenarios rerun on Claude Code and pi; pi acts as an independent reviewer.

## CP-003 — AC-3 "expands to" becomes "shows" (2026-10-10, follows CP-002)
The user-approved prototype (CP-002) shows each item's four facts directly on its progress card, with no disclosure. Codex Evaluator E-005 noted the Charter still said "expands to". Charter revision 3 aligns AC-3 with the approved layout. No other acceptance criterion changes. Flag to the user in the step report.

## CP-004-L — Codex is a test host, not a reviewer (2026-10-11, user decision)
User: "我说实话我从来没想让codex做审查，只让他用来当你的测试工具而已，因为这个html-plan就是因为codex写的太烂，才导致我想重写这个技能，甚至审查整个技能合集找出他埋的一堆测试的一堆防御性编程的雷。" The four Codex Evaluator reports in round 2 are not acceptance evidence. Their findings (E-004..E-010) are reclassified with the user before the next freeze. Reviewers are fresh Claude subagents; pi and Codex are test hosts.

## CP-005 — reclassify Codex-driven repairs (2026-10-11, user decision)
User confirmed the handoff §4.1 recommendations ("待确认项已确认，继续执行"). Repair6 (`candidate-manifest-repair6.txt`):
- Kept: E-004 (source dates only from the source itself; now one sentence, skeleton comment removed), E-009 (proposal-only ticket has no status), E-010 (checks outside the project; now one sentence), CP-003.
- E-008: kept only "an item with no ticket says 还没有工单" (progress-and-refresh + skeleton tally); reverted the repair3 "尚无执行记录, never 没开始" rule and the repair4/5 writing.md rule "missing record = unknown". Reason: defensive wording rules make the page less plain; "还没发布" is fine for the reader.

## CP-006 — sparse part 2 shows gap cards, not "目前没有" (2026-10-11, Core interpretation)
Evaluator E-011: Charter VS-2 says parts 2–5 say "none so far". With CP-005 and AC-10, a component with no ticket gets a "还没有工单" gap card in its column, so the sparse page's part 2 shows four gap cards and a tally; parts 3–5 say "目前没有". Core reads VS-2's "none so far" for part 2 as "no recorded progress", which the gap cards state. Flag to the user in the step report.

## User acceptance of step 3 (2026-10-11)
User read the repair6 pages (Claude Code, pi, Codex, sparse) and accepted: "基本都很好，只有pi这里没给跳转链接，不过这不是什么大问题，可以验收". This covers CP-003, CP-006 and the look and readability. Observation recorded as E-013.
