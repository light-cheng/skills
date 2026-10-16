# Producer evidence — round 2 (Charter revision 2, `candidate-manifest.txt`)

Hosts: Claude Code 2.1.296 (`claude -p`), pi 1.1.0 (default model, Gemini family), Codex CLI 0.162.0-alpha.17.2 (`codex exec -m gpt-6.1-sol -c model_reasoning_effort="high"`). Runner `runs/run.sh`; generator `runs/gen.py` (host arg chooses `.claude/skills` or `.agents/skills`); page checker `runs/pagecheck.py`. Pages, history copies and source baselines: `pages/<run>/`.
Candidate unchanged during all runs (manifest re-verified after the runs: 0 mismatches).

## Scenarios (skill never named)
| Run | Host | Result | Sources unchanged |
|---|---|---|---|
| vs1, vs1b | Claude Code | invoked; page built on skeleton | yes |
| vs2 (spec only) | Claude Code | invoked; parts 3–5 "目前没有"; hero card plain (no accent) "目前没有等你决定的事"; 4 gap cards | yes |
| vs5 (summarise) | Claude Code | not invoked, no file | yes |
| vs6 (other-feature PASS) | Claude Code | invoked; acceptance shown as pending check | yes |
| pi1 | pi | read SKILL.md; page built on skeleton | yes |
| cx1 | Codex | read SKILL.md and plan.css (native discovery from `.agents/skills`); page built on skeleton; **also wrote `.scratch/tool-lending/plan-evidence.md`** (commitment map) | yes |
| cx5 (summarise) | Codex | not invoked, no file | yes |
| vs3, vs3b | Claude Code | refresh: history byte-equal; style identical; 30/434, 30/426 lines changed | yes |
| vs4 (decisions.md unreadable) | Claude Code | no refresh, nothing written, asked the user | yes |
| pi3 | pi | refresh: history byte-equal; style identical; 22/437 lines; ran headless Chrome at 1440/390 itself | yes |
| cx3 | Codex | refresh: history byte-equal; style identical; also updated its `plan-evidence.md` | yes (project records) |

## AC-10 page checks (`pagecheck.py`, every created page: vs1, vs1b, vs2, vs6, pi1, cx1)
Stylesheet inlined in one `<style>`; zero classes outside plan.css; sections in order what/progress/decide/changed/judged/sources; no external src/href/url(); full-record pages: 4 component cards, 3 progress cards + 1 gap card (R4), 1 decision card, 2 change cards, 2 judgment cards.

## Rendering (built-in browser, served over 127.0.0.1)
1440×900 light: cx1 and pi1 hero, parts 01 and 02 inspected; same layout as the approved prototype. 390×844 dark: all six created pages scrollWidth = clientWidth, no element beyond the viewport (nav excluded: it scrolls by design), dark background applied.

## Observation for review
O-1: Codex writes a commitment-map file next to the page. The package allows "The map may live in the page or delivery evidence", so it is not a breach, but it leaves an unrequested file in the project.

## Repair1 (`candidate-manifest-repair1.txt`, fixes F-008..F-011) — `runs-repair1/`, `pages-repair1/`
Codex runs now pass `--disable memories` (per-run flag; config untouched) so earlier Codex memories cannot shape the run (Critic note). Candidate re-verified unchanged after the runs.

| Run | Host | Result | Sources unchanged |
|---|---|---|---|
| vs1 / vs3 | Claude Code | create; refresh with history byte-equal, style identical (30/425) | yes |
| pi1 / pi3 | pi | create; refresh with history byte-equal, style identical (22/433) | yes |
| cx1 / cx3 | Codex | create; refresh with history byte-equal, style identical (18/230); **no extra file**; no memory reads | yes |

pagecheck on all six: inlined CSS, zero undefined classes, sections in order, no external requests, 4 comp / 3 prog + 1 gap / 1 ask / 2 chg / 2 jg. Partial state labelled "部分完成" on every host; "一半" absent (F-008). Facts order 在做什么/已完成/没完成/证据 (F-009). Only `plan.html` and `plan-history/` written (F-011).
Not rerun on repair1 (text they exercise unchanged): vs2, vs5, vs6, vs4, cx5 — round-2 runs above.

## Repair2 (`candidate-manifest-repair2.txt`, fixes E-004; Charter revision 3 per CP-003) — `runs-repair2/`, `pages-repair2/`
Full scenario set rerun on the current text, all three hosts, Codex with `--disable memories`. Candidate re-verified unchanged after the runs (0 mismatches).

| Run | Host | Invoked | Result | Sources unchanged |
|---|---|---|---|---|
| vs1, vs1b | Claude Code | yes | page on skeleton; undated sources "无日期"; partial "部分完成" | yes |
| vs2 | Claude Code | yes | spec only; parts 3–5 "目前没有"; 4 gap cards | yes |
| vs5 | Claude Code | no | chat only | yes |
| vs6 | Claude Code | yes | other-feature PASS "待核对" | yes |
| pi1, pi1b | pi | yes | page on skeleton; pi1b dates correct; **pi1 still dates `state.md` 2026-10-06** (borrowed) | yes |
| cx1 | Codex | yes (native) | page on skeleton; dates correct; no extra file; no memory reads | yes |
| cx5 | Codex | no | chat only | yes |
| vs3, vs3b | Claude Code | yes | refresh; history byte-equal; style identical (30/428, 28/426) | yes |
| vs4 | Claude Code | yes | decisions.md unreadable → no write, asked user | yes |
| pi3 | pi | yes | refresh; history byte-equal; style identical (24/456); inherits pi1's borrowed date | yes |
| cx3 | Codex | yes | refresh; history byte-equal; style identical (6/239) | yes |

pagecheck: every created/refreshed page ok (inlined CSS, 0 undefined classes, section order, no external requests; 4/3+1/1/2/2 cards on full records). "一半" appears only inside the user's quoted words ("half the members").

Rendering (built-in browser over 127.0.0.1, `pages-repair2/`): all 10 pages measured in 1440px and 390px frames with every disclosure open: no overflow, 0 elements past the edge (nav excluded), `.cols` 4 columns at 1440 and 1 at 390, `.two` 2 and 1. Real viewport: vs1 1440×900 light screenshot; pi1 and cx1 390×844 dark screenshots. Keyboard on vs1: theme button focused, Enter switched light → dark; raw-record `summary` focused, Enter opened it.

Residual (pi only): E-004 date borrowing reproduced in 1 of 2 pi creates (pi1, inherited by pi3). Claude Code 5/5 and Codex 2/2 comply.

## Repair3 (`candidate-manifest-repair3.txt`, fixes E-008, reinforces E-004 at the skeleton) — `runs-repair3/`, `pages-repair3/`
Full set rerun, all hosts, Codex with `--disable memories`. A session restart interrupted pi1, pi1b, pi1c, pi2 and cx2 in the first pass (transcripts kept in `runs-repair3/interrupted/`, not counted); their projects were rebuilt and rerun (`resume.sh`). Candidate re-verified unchanged after the runs (0 mismatches).

| Run | Host | Invoked | Key result | Sources unchanged |
|---|---|---|---|---|
| vs1, vs1b | Claude Code | yes | undated sources "无日期"; tally 1/1/1/1(尚无执行记录)/0 | yes |
| vs2 | Claude Code | yes | tally 0 没开始, 4 尚无执行记录 (E-008) | yes |
| vs5 | Claude Code | no | chat only | yes |
| vs6 | Claude Code | yes | other-feature PASS "待核对" | yes |
| pi1, pi1b, pi1c | pi | yes | **all three** date `state.md` and ticket 03 "无日期" (E-004: 3/3) | yes |
| pi2 | pi | yes | sparse: 0 没开始, 4 尚无执行记录 | yes |
| cx1 | Codex | yes | dates correct; no extra file; no memory reads | yes |
| cx2 | Codex | yes | sparse: "4 项功能尚无执行记录"; gap-styled cards with the four facts | yes |
| cx5 | Codex | no | chat only | yes |
| vs3, vs3b | Claude Code | yes | refresh; history byte-equal; style identical (32/425, 30/426) | yes |
| vs4 | Claude Code | yes | unreadable source → no write | yes |
| pi3 | pi | yes | refresh; history byte-equal; style identical (24/435) | yes |
| cx3 | Codex | yes | refresh; history byte-equal; style identical (4/191) | yes |

pagecheck: all 14 pages ok (inlined CSS, 0 undefined classes, section order, no external requests). Rendering of the repair3 pages was not re-measured in the browser; the stylesheet and skeleton layout are unchanged from repair2 except two comments, one tally item and one date placeholder (diff the manifests: only skeleton.html and progress-and-refresh.md changed), and repair2 rendering is recorded above.

## Repair4 (`candidate-manifest-repair4.txt`, fixes E-008 body text and E-009) — `runs-repair4/`, `pages-repair4/`
Full set rerun on all hosts. **Isolation:** each project at `lhp-iso/<run>/proj`, alone in its parent; baselines in `lhp-iso/_base/`. Codex `--disable memories`. Candidate re-verified unchanged after the runs (0 mismatches). Only `writing.md` and `progress-and-refresh.md` changed from repair3.

| Run | Host | Invoked | Key result | Sources unchanged |
|---|---|---|---|---|
| vs1, vs1b, vs6 | Claude Code | yes | dates "无日期"; "还没开始" only for ticket 03 (`Status: open`); no status for proposal-only ticket 04 | yes |
| vs2 | Claude Code | yes | sparse: no "没开始" claim in text; tally 0 没开始 / 4 尚无执行记录. **O-2:** ran the package's own tests with pytest, leaving `.pytest_cache/` in the project | yes |
| vs5 | Claude Code | no | chat only | yes |
| pi1, pi1b, pi1c | pi | yes | dates "无日期" 3/3; no proposal-only ticket status | yes |
| pi2, pi2b | pi | yes | sparse: "状态均无法确认"-style text; pi2 read `../../_base/` hash lists (not pages); pi2b fully isolated | yes |
| cx1, cx2 | Codex | yes | correct; cx1 used a status sentence as `<h1>` instead of the project name | yes |
| cx5 | Codex | no | chat only | yes |
| vs3, vs3b, pi3, cx3 | refresh | yes | history byte-equal; style identical (28/426, 28/427, 22/439, 2/192) | yes |
| vs4 | Claude Code | yes | unreadable source → no write | yes |

pagecheck: all 15 pages ok. Rendering (built-in browser over 127.0.0.1, `pages-repair4/`): all 15 pages measured in 1440px and 390px frames with disclosures open — no overflow, 0 elements past the edge (nav excluded), `.cols` 4 → 1. Real viewport: vs1 and pi1 at 1440×900 light; cx1 and pi2b at 390×844 dark. Keyboard on vs1: theme button Enter → dark; first `summary` Enter → open.

## Repair6 (`candidate-manifest-repair6.txt`, CP-005: user reclassified the Codex-driven repairs) — `runs-repair6/`, `pages-repair6/`
Changed from repair5: `writing.md` back to repair2 bytes (`ba7e75c7…`; "missing record = unknown" rule removed); `progress-and-refresh.md` keeps only "an item with no ticket says 还没有工单" and the E-009 sentence; skeleton tally `尚无执行记录` → `还没有工单`, both skeleton comments removed; E-004 and E-010 condensed to one sentence each. Package tests 7/7.
Full set rerun on all three hosts in one wave (`wave.sh`), each project alone at `lhp-iso6/<run>/proj`, baselines in `lhp-iso6/_base/`. Codex `gpt-6.1-sol`, effort high, `--disable memories`. All 18 runs exit 0, none interrupted. Candidate re-verified unchanged after the runs (`shasum -c` clean). Codex and pi are test hosts only.

| Run | Host | Invoked | Key result | Sources unchanged | New files |
|---|---|---|---|---|---|
| vs1, vs1b | Claude Code | yes (Skill tool) | R4 "还没有工单"; "没开始" only for open ticket 03; ticket 03 / state.md "无日期"; proposal-only ticket 04 has no status | yes | none |
| vs2 | Claude Code | yes | sparse: 4 还没有工单; no project files touched (E-010) | yes | none |
| vs5 | Claude Code | no | chat summary only | yes | none |
| vs6 | Claude Code | yes | other-feature PASS → "验收结论待核对" | yes | none |
| pi1, pi1b, pi1c | pi | yes (reads SKILL.md) | R4 "还没有工单"; "无日期" 3/3; ticket 04 only inside proposal | yes | none |
| pi2, pi2b | pi | yes | sparse: 4 还没有工单 | yes | none |
| cx1, cx2 | Codex | yes | cx1 says "工单 04 目前还不存在"; cx2 4 还没有工单 | yes | none |
| cx5 | Codex | no | chat only | yes | none |
| vs3, vs3b, pi3, cx3 | refresh | yes | history byte-equal to pre-refresh page; style identical (30/443, 28/426, 26/436, 20/248 lines changed) | only plan.html changed | none |
| vs4 | Claude Code | yes | unreadable decisions.md → page unchanged, no history, reports refresh incomplete | yes | none |

pagecheck: 16 pages ok (inlined CSS, 1 style block, 0 undefined classes, fixed section order, 0 external requests).
Wording observation (not a defect under CP-005): pages say "尚未发布" / "还没发布" without a release record; pi2b says "尚未开始编码" for ticketless items. vs6 replied to a Chinese prompt in English (page itself is Chinese).
Rendering (built-in browser, 127.0.0.1:8766): all 16 pages in 1440px and 390px iframes with disclosures open — no horizontal overflow, 0 elements past the edge (nav excluded), `.cols` 4 → 1. Real viewport: vs1 and pi1 at 1440×900 light; cx1 and pi2b at 390×844 dark. Keyboard on vs1: theme button Enter → dark; first `summary` Enter → open. No console errors. Server stopped afterwards; no launch.json created.
