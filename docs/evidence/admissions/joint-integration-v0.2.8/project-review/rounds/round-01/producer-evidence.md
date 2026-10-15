# Producer evidence — round 1

Reviewed tree: `manifest.txt` (61 changed or new files since `e3ba9f7`; list in `changed-files.txt`). Evals: `.scratch/stage3-step4/evals/` (`cases.tsv`, `cases-b.tsv`, `mk.py`, `run.sh`, `wave.sh`, `signals.py`, `pagecheck.py`). Isolated projects: `<tmp>/-Users-light-Documents-Projects-Configurations-skills/14a024af-d9b5-448f-9407-49a039b356ac/scratchpad/s4-iso/<wave>/<host>-<case>-<rep>/proj` (one per run, alone in its folder). Fixtures are built from frozen snapshots `snap-w1` (before integration: 36 admitted + 3 candidates), `snap-w2`, `snap-w3`, `snap-w4`, `snap-w5` (after; manifests beside them). Hosts: Claude Code 2.1.296 (`claude -p`), pi 1.1.0, Codex 0.162.0-alpha.17.2 (`gpt-6.1-sol`, effort high, `--disable memories`). Codex and pi are test hosts only.

## Suite and checks (observed)
- `PYTHONPATH=tests python3 -m pytest -q -p no:cacheprovider` → 635 passed (after the CR-001/CR-002 repairs).
- `python3 scripts/check_public_docs.py` → PASS.
- Mutation checks (observed red → restored green):
  - remove `REDIRECT_LINE` from the pointer → `test_rerun_adds_the_redirect_line_to_an_older_pointer_once` fails;
  - remove the fallback sentence from project-spec's optional line → `test_optional_calls_are_declared_with_a_fallback` fails;
  - count the manifest against the working tree / drop the tag-as-revision line → `test_published_manifest_is_counted_against_its_own_tag` fails.

## AC-2 Trigger waves (VS-1)
Scores from `signals.py` (`loaded` = Claude Code `Skill` call / pi read of `<cap>/SKILL.md` / Codex command printing it; `left` = project effects). Claude Code ×2, pi ×1, Codex ×1 per case unless noted. Interrupted runs (Claude session limit) are in `w1-baseline/interrupted/` and were rerun from the same snapshot. Superseded D1 runs (flawed fixtures) are in `*/superseded-D1*`.

| Case | Expect | Before (w1) claude / pi / codex | After claude / pi / codex | Note |
|---|---|---|---|---|
| R1 new idea mid-work | redirect | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | after: pi read the skill but wrote no proposal |
| R2 FAIL on direction | redirect | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | |
| R3 user changes mind | redirect | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | |
| R4 ticket contradicts SPEC | redirect | **0/2** · 1/1 · 1/1 | **2/2** · 1/1 · 1/1 | before: Claude Code edited ticket 04 directly ("当成工单笔误直接改了") |
| R5 local bug | none | 2/2 · **0/1** · 1/1 | 2/2 · 1/1 · 1/1 | before: pi read light-redirect, no proposal |
| R6 question about R2 | none | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | |
| H1 page request | plan | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | page created everywhere |
| H2 report written, page exists | plan | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | plan-history written everywhere |
| H3 verdict PASS, page exists | plan | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | |
| H4 "plan next week" | none | 2/2 · **0/1** · 1/1 | 2/2 · **0/1** · 1/1 | pi reads the skill both times; no page written |
| H5 summarize SPEC in chat | none | 2/2 · 1/1 · 1/1 | 2/2 · 1/1 · 1/1 | |
| D1 `$light-implement` on a bounded static page | informational | 0 · 0 · 0 loads | (w4) 0 · 1 · 1 loads, pi and Codex log a `decisions.md` row | Claude Code applies WORKFLOW §3A (bounded solo work skips routing) and never reaches the judgment; step 3 now says so explicitly |
| D1b `$light-implement` on a multi-part ticket | decide | 0/2 · 1/1 · 0/1 | (w5) 0/2 · 1/1 · 0/1 | after: every Host stopped on real plan problems in the fixture (no code base, missing `Blocked by`, R6 unapproved) and wrote a light-redirect proposal before routing |
| D2 wording: direction or fix? | decide | 0/2 · 1/1 · 0/1 | 0/2 · 1/1 · 0/1 | Claude Code and Codex answer "local fix" confidently and correctly; nothing unclear to ask |
| D3 user asks Agent to pick a library | none | 2/2 · 3/3 · 1/1 | 2/2 · **2/3** · 1/1 | after: one of three pi runs read light-decide, logged nothing |

Waves used snapshot w2 for R/H/D2/D3; light-implement step 3 changed after w2 (A6 wording), which does not touch R/H/D2/D3 prompts.

**Plan gap chain (AC-4), observed:** in the superseded w2 D1 runs, Claude Code wrote `Plan gap:` in the implementation report (ticket 04 had no SPEC requirement), then called `light-redirect` with the ticket path and wrote proposal 03.

## Behaviour scenarios (`b3-behaviour/`, snapshot w3)
- **VS-2 map seam (AC-7).** Claude Code turn 1 added `- Change proposed, waiting on the user: …` under `Not yet specified`; resumed turn 2 ("批准这个提案…") removed it and added `- Change approved 2026-10-11: …` under `Decisions so far`, status `approved`. pi and Codex (one turn): proposal `proposed`, line under `Not yet specified`.
- **VS-3 apply (AC-6).** `/project-spec` with a SPEC-only approved proposal → SPEC `Out of scope` gains "Photos of tools.", proposal `applied` with a Comments line, ticket untouched. With a SPEC+Tickets proposal → SPEC R3 changed, ticket 03 unchanged, proposal stays `approved` with "Status stays approved until the ticket 03 change is applied."
- **VS-4 plan gap (AC-4).** Ticket 05 asks for late fees the SPEC rules out. pi and Codex: claim, report `Outcome: BLOCKED` with a non-`none` `Plan gap:`, proposal 03 `proposed`. Claude Code: saw the conflict before claiming, wrote proposal 03, left the ticket `ready-for-agent` with no report, citing the project's standing line.
- **VS-5 page (AC-8).** Ticket 03 carries a `BLOCKED` comment naming the user's SMS decision. On all three Hosts part 3 lists exactly that one decision (ticket 02's remaining work is not listed), part 2 says ticket 03 also waits on ticket 02, the in-card flag links to an existing `ask-*` card id, the one style block equals `plan.css` (`pagecheck.py` `css_exact: True`), 0 undefined classes.

## light-code-review (script scope)
Findings CR-001..CR-003 in `findings.md`; CR-001 and CR-002 repaired and re-tested, CR-003 recorded as a limit.

## Limits
- light-decide from light-implement is not demonstrated on Claude Code (D1 is bounded work; D1b fixture surfaced plan gaps first). pi and Codex do call it and log rows.
- pi reads skills it does not use (H4 both waves; D3 one of three after); no effect files.
- One fixture domain; Producer, Claude Code subjects and reviewers share a model family.
- No fresh-install verification of the 39-package collection; no release.

## Repair 1 (`manifest-repair1.txt`, 63 files; Critic C-001, C-002, C-004..C-010) — snapshot `snap-w6` (equals `skills/` at freeze)
- Suite: 636 passed; `check_public_docs.py` PASS. Mutation checks: wrong category count → `test_collection_guides_state_the_real_category_counts` fails; removed fallback → `test_optional_calls_match_declarations_and_each_has_a_fallback` fails; removed edge → same test fails.
- **R1–R6 rerun (`w6-after/`, narrowed standing line):** R1–R4 claude 2/2, pi 1/1, codex 1/1, each writing a proposal; R5, R6 no trigger on any Host.
- **VS-4 rerun (`b6-behaviour/*-BGAP-1`):** all three Hosts claim ticket 05, write `Outcome: BLOCKED` with a non-`none` `Plan gap:`, and write proposal 03 (`proposed`).
- **VS-3b (`*-BTIX-1`, new):** proposal with `SPEC applied — project-spec` already recorded → `/project-tickets` (Claude Code) and `$project-tickets` (Codex) change ticket 03 acceptance and set `applied`.
- **VS-5b (`*-BFAIL-1`, new):** verdict `FAIL`, `Cause: implementation` on ticket 02 → on all three Hosts part 3 keeps one card (the SMS decision); the FAIL is shown in part 2; `css_exact: True`, 0 undefined classes, ask links resolve.
- **C-003 (pi, D3):** open; not repairable in package text. Before 0/3 reads, after 1/3 read (no decision row, no file). Raised with the user as an approved-exception request.
- D1/D1b/D2/H/D3 waves were not rerun: the repair touched light-implement step 6 and the plan-gap bullet (exercised by VS-4), light-html-plan part-3 scope (VS-5b), light-redirect wording (R1–R6, VS-2 unchanged path), project-spec/tickets apply lines (VS-3b), docs and tests.
- **VS-2/VS-3 rerun on final text (`b6-behaviour/`):** Claude Code BMAP: turn 2 recorded `approved` and the line sits under `Decisions so far`, none left under `Not yet specified`; Codex BMAP (one turn): `proposed`, line under `Not yet specified`. BSPEC (SPEC-only) → `applied`. BBOTH (SPEC+Tickets) → stays `approved` with `- 2026-10-11 SPEC applied — project-spec`.
