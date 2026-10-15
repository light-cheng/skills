# Findings — round 1 (Critic: generic-review, agent a2e78c1cc71ed091a)

| ID | Severity | Summary | Disposition | Repair |
|---|---|---|---|---|
| F-001 | medium | `.project-review/` location; stale or other-feature PASS shown as accepted | accepted | source-protocol: root location; count verdict only when state.md agrees and Target is this feature, else "验收结论待核对" |
| F-002 | medium | writing example gives unused answer the value of `final` | accepted | example states decider answer (not used) and final |
| F-003 | low | proposed proposals excluded from part 4 in table | accepted | table: 4 for every proposal, 3 also for proposed |
| F-004 | low | "改动大小未记录" missing from design reference | accepted | design: neutral style, legend lists used values |
| F-005 | low | low-confidence ordering had no field | accepted | order by logged `reason` ≠ `none` |
| F-006 | low | resolved → 验收 differs from design §4 | accepted with interpretation CP-001 | progress-and-refresh states why |
| F-007 | low | 验收 row did not point to the verdict condition | accepted | row links to source-protocol verdict condition (repair3) |
| E-001 | low | "blocked tickets" ambiguous (only `Blocked by:` edges exist) | deferred to step 4 (define when wiring callers; add a scenario) | — |
| E-002 | low | only root `.project-review/` read | accepted as limitation (safe direction); revisit in step 4 | — |
| E-003 | low | pi labels a new component 重点改动 | accepted as residual limitation on pi's default model | — |

## Round 2 (Charter revision 2). Critics: Claude generic-review subagent; pi (Gemini) generic-review
| ID | Severity | Summary | Disposition | Repair (repair1) |
|---|---|---|---|---|
| F-008 | low | half-dot "part" state undefined; "写了一半" invents an amount | accepted | progress-and-refresh + skeleton: partial only on 写完, recorded word, never an amount |
| F-009 | low | "opens to" vs always-shown facts; order differs | accepted | "shows"; one order 在做什么/已完成/没完成/证据 |
| F-010 | low | fixed Chinese labels and `lang` with no rule for other readers | accepted | labels and `lang` follow reader's language |
| F-011 | low | "delivery evidence" undefined → Codex wrote and overwrote `plan-evidence.md` | accepted | map in reply or page source area; no other project file |
| pi F-008 | low | same as F-011 | duplicate of F-011 | — |

Note from Claude Critic: Codex run cx1 read `~/.codex/memories` entries about earlier light-html-plan work, so Codex evidence is less independent.
| E-004 | medium | pi pages borrow dates for undated sources (Codex Evaluator) | accepted | source-protocol: each source's own date, else "无日期"; never borrow (repair2) |
| E-005 | medium | Charter AC-3 "expands to" vs approved always-shown facts | accepted | Charter revision 3 (CP-003) |
| E-006 | medium | no current browser evidence for repair pages | accepted | browser + keyboard checks on repair2 pages |
| E-007 | low | VS-6 not rerun after repair1 | accepted | full rerun on repair2 |
| E-004 (recheck) | medium | still reproduced on pi (1/2) | rule repeated at point of use in skeleton (repair3); rerun pi ×3 | — |
| E-008 | medium | sparse page inferred "没开始" for items with no records | accepted | skeleton tally + progress-and-refresh: 没开始 only for open/ready tickets; else 尚无执行记录 (repair3) |
| E-004 (recheck 2) | medium | fixed: pi 3/3 "无日期" (Codex Evaluator round 3) | closed | — |
| E-008 (recheck) | medium | body text still asserted "没有一项写完/验收/发布" without records | accepted | writing.md rule: missing record = unknown, with example (repair4) |
| E-009 | medium | pi1b gave proposed-only ticket 04 a status | accepted | progress-and-refresh: proposal-only ticket has no status (repair4) |
| E-006 (recheck) | medium | repair3 pages not re-measured in browser | accepted | browser measurement of repair4 pages |
| (evidence) | — | pi2 read sibling project folders | accepted | repair4 runs use one isolated parent folder per project |
| E-006 (recheck 2) | medium | fixed (Codex Evaluator round 4) | closed | — |
| E-009 (recheck) | medium | fixed (Codex Evaluator round 4) | closed | — |
| E-008 (recheck 2) | medium | still: sparse pages "未发布/没有发布"; pi1b "尚未开始" for ticketless R4 | accepted | writing.md: rule covers every state, with 发布 and 无工单 examples (repair5, **not yet rerun**) |
| E-010 | low | vs2 ran package tests in the project, leaving `.pytest_cache/` | accepted | design-and-verification: run checks outside the project, never the package tests there (repair5, **not yet rerun**) |
| E-008 (CP-005) | medium | reclassified by user: only the no-ticket case is a real error | partly reverted | keep "还没有工单" for ticketless items; drop repair3–5 wording rules (repair6) |
| E-004, E-009, E-010 (CP-005) | — | kept; E-004 and E-010 condensed to one sentence | — | repair6 |
| E-011 | low | VS-2 wording "parts 2–5 none so far" vs gap cards in part 2 | accepted as interpretation | CP-006; no package change |
| E-012 | low | vs1/vs3 inline-style grid wrapper; pi1/pi3 stray `theme{}` CSS rule; pagecheck misses both | recorded | harmless; tighter style-block check left for step 4 |
| E-013 | low | user: pi1 part-1 R3 card says "短信提醒改动提案待你决定" as plain text with no link to part 3 | recorded | not blocking (user); consider a link pattern in skeleton at step 4 |
