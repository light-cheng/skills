# Round 1 — Producer evidence

Reviewed head: `39732d6` (branch `claude/project-thread-ml55ij`), fixed point `ee05c3c`. Environment: Linux container, Node 22.22.0, Python 3, Chromium via Playwright. Date: 2026-10-25.

| # | Label | Command or action | Observed | Criteria |
|---|---|---|---|---|
| E-1 | behavioral | `npm test` in `assets/template` | 96 tests, 96 pass, 0 fail (includes `tests/layered-text.test.mjs`, 6 tests; updated navigation tests; #15 schedule-derivation and nearby-stays tests) | AC-1–AC-6 |
| E-2 | behavioral | `python3 -m pytest -q` in a clean `git worktree` of `39732d6` | 631 passed, 2 skipped, 10 failed. The same 10 tests fail on a clean worktree of `fa1b9c3` (#15 head); `diff` of the two FAILED lists is empty. They are release-integrity and evidence tests that need tags and network (shallow clone, offline). | AC-9 |
| E-3 | structural | `python3 scripts/check_public_docs.py` | `RESULT: PASS` | AC-8 |
| E-4 | review | GitHub Actions `quality` on PR #16 head `39732d6` | success (run 40172910892) | AC-8, AC-9 |
| E-5 | installation | `node scripts/create.mjs /tmp/claude-0/vs/fresh`, then `npm test` | project created with AI off; 96/96 pass | AC-9 |
| E-6 | behavioral | `npm run build` in the fresh project with the unfilled template data | refuses: "Trip ID must be configured / Uninitialized template cannot be deployed"; same message on a fresh project from `ee05c3c` (by design) | AC-9 |
| E-7 | runtime | Fresh project + the owner's Kyushu `trip-data.json` and map assets (local fixture, not committed), `npm run build` | builds; region `九州=schematic-sketch`; lists 21 places without coordinates that the sketch map skips | AC-1 |
| E-8 | runtime | Chromium, built `dist/` served locally with `/api/*` stubbed to empty shared state, 1366×900 and 390×844 (script `serve-shot.cjs`, kept outside the repo) | both viewports: no console or page errors; visible tabs `01 行程 · 02 预订 · 03 to-do · 04 材料 · 05 账本`; weekdays `周四 周五 周六`; 8 daily sketch maps; 42 structured schedule entries; on `#prep` the overview map is visible with 0 day-tab bars; 2 to-do cards; cash table 11 rows; `#route` opens chapter `todo`; materials visible; no horizontal scroll | AC-2–AC-5 |
| E-9 | runtime | Chromium 390×844 with clipboard permission: click the first to-do card's 复制 | button shows 已复制; clipboard holds the card text with line breaks, without the instruction line | AC-5 |
| E-10 | structural | `git diff ee05c3c...HEAD` of template code (tests excluded) scanned for 九州, kyushu, JPY, `lang="ja"`, 日本, 博多, 小仓, suica, 由布院, 阿苏 | no match | AC-7 |
| E-11 | structural | `git diff ee05c3c...HEAD --name-only` | `ai-config.js`, `scripts/validate.mjs`, `server/ai.js`, `server/ai-client.js`, `SKILL.md`, `agents/`, `ATTRIBUTION.md`, `package.json` not changed | AC-7, AC-9 |

Screenshots for E-8/E-9 contain the owner's real booking data, so they are kept in the owner's private project files, not in this repository.

## Producer observations

- P-1: In the 390px itinerary, the daily sketch map drawn with `labelScale: 2` cuts off its own title line at the right edge ("11/12 Hong Kong → Fukuoka → 小仓 | 落地…"). The same code runs on the live Kyushu page.
- P-2: Kyushu data has no `cashBudget.currency`, so its amount column reads 金额. Expected; an existing trip adopting this template should add `currency`.

## Limits

- No real Host invocation trial; SKILL.md and invocation type are unchanged.
- No WebKit run; no hosted deployment or cross-session sync check (not in scope).
