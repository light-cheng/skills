# Producer evidence — round 1

Host: Claude Code 2.1.296 (`claude -p`, stream-json) on macOS; pi 1.1.0 (default model, `-p --mode json --approve --no-session`) for cross-host discovery.
Runs dir: `runs/` (prompts `*.prompt.txt`, transcripts `*.jsonl`, exit codes `*.err`; fixture generator `gen.py`; summariser `summ.py`).
Temp projects: session scratchpad `lhp/<scenario>`; each had a SHA-256 baseline of every non-skill file before the run.
Fixture domain: tool-lending library (unlike the resume and payment-reminder examples).

## Text version under test
- Runs vs1, vs1b, vs2, vs5, vs3, vs3b, vs4, pi1: `candidate-manifest.txt`.
- `candidate-manifest-repair1.txt`: writing.md tightened after pi1 (change size from records; part 3 lists only what records put on the user; snapshot, never "live"). Scenarios must be rerun on the final text before the Evaluator.

## Structural
- Package tests: 6 passed (`tests/test_light_html_plan_contract.py`), including drift controls.
- Repo: `check_public_docs.py` PASS; full suite 610 passed (after the `docs/agents/issue-tracker.md` edit).

## Scenarios
| Run | Prompt (skill not named) | Invoked | Result | Sources unchanged |
|---|---|---|---|---|
| vs1 | 帮我做一个网页…进展到哪了 | yes | plan.html; five parts in order; 9 sources with correct SHA-256; unused typed judgment shown as not used, final followed; proposed SMS change in part 3, applied 7-day change in part 4 with approver; 写完/验收/发布 separate; flagged R4 has no ticket | yes |
| vs1b | same | yes | same shape; 8 sources correct SHA-256; 13 details | yes |
| vs2 | same, spec only | yes | five parts; parts 3–5 "目前没有"; progress "尚无记录"; R4 gap noted as an observation, labelled not a record | yes |
| vs5 | summarise spec in 5 bullets | no | chat answer, no file | yes |
| vs3 | 工单 02 刚写完…把计划页面更新一下 | yes | history `plan-history/20261010T065551Z-plan.html` byte-equal to old page; ticket 02 → 写完 ✓, 验收 not (still claimed, verdict only for 01); `<style>` identical; 32/488 lines changed | yes (only plan.html changed) |
| vs3b | same | yes | history byte-equal; style identical; 38/420 lines changed | yes |
| vs4 | same, decisions.md chmod 000 | yes | refused to refresh; plan.html unchanged, no plan-history; reported the unreadable file and the planned change; did not chmod | yes |
| pi1 | as vs1, on pi | yes (listed and loaded) | five parts; no external requests; **defects**: invented change sizes (重点改动/小改) for all-new features; invented a user decision ("confirm the refusal text") from an unfinished implementation item; called the page "实时" | yes |

## Rendering (built-in browser, served over 127.0.0.1)
- vs1 at 1440×900 light and 390×844 dark: no horizontal overflow (scrollWidth = clientWidth), all details opened; theme buttons override system both ways; summaries keyboard-focusable; no console errors.
- vs1b, vs2 at 390: no overflow. vs1/vs1b/vs2/pi1: no external src/href/@import/url().
- Agent subjects cannot open a browser inside `claude -p`; each said so and left look/readability to the user.

## Not done
- Codex native discovery (old A13).
- User reading of the page (the user judges look and plainness).

## Final runs on `candidate-manifest-repair3.txt` (`runs-final/`)
Installed copy in every project verified equal to repair3. Fixture now includes `.project-review/state.md`; new VS-6 uses a PASS verdict whose Target is another feature (`.scratch/shed-signage/spec.md`). Pages, history copies and source baselines are kept in `runs-final/pages/`.

| Run | Invoked | Result | Sources unchanged |
|---|---|---|---|
| vs1 | yes | five parts; unused judgment shown as not used, work followed `no`; R4 gap flagged; 9 sources | yes |
| vs1b | yes | first attempt hit 429 usage limit (kept as `vs1b-p1.limit.*`, not counted); rerun after reset: same shape, three states separate | yes |
| vs2 | yes | spec only; parts 3–5 "目前没有" (3×); no invented progress | yes |
| vs5 | no | chat summary only | yes |
| vs6 | yes | other-feature PASS shown as "验收结论待核对", not counted as accepted; both locators named | yes |
| vs3 | yes | history byte-equal; `<style>` identical; 38/434 lines changed; ticket 02 写完, not 验收 | yes (only plan.html) |
| vs3b | yes | history byte-equal; `<style>` identical; 26/327 lines changed | yes (only plan.html) |
| vs4 | yes | unreadable decisions.md → no refresh, no history, page unchanged, did not chmod | yes |
| pi1 | yes (listed, SKILL.md read) | five parts; part 3 now only records-based items (no invented user decision); part 5 separates decider answer and final; "实时" only in "非实时同步". **Residual:** labels R2 重点改动 although every component is new; legend lists 小改 unused | yes |

Rendering (built-in browser over 127.0.0.1): vs1, vs2, vs6, pi1 no external src/href/url/@import; five h2 parts in order. vs1 1440 light and 390 dark: scrollWidth = clientWidth, all details opened, summaries focusable; theme toggle overrides system both ways (system dark → light, system light → dark). vs6 at 390: no overflow. No console errors.

Critic (generic-review, same agent across rechecks): round-1 F-001..F-006 → repair2; recheck: all fixed, new F-007 → repair3; recheck: fixed, no findings.
