# Findings — stage 3 step 4

| ID | Source | Severity | Location | Problem | Disposition | Repair |
|---|---|---|---|---|---|---|
| CR-001 | light-code-review F-001 (Standards) | low | scripts/verify_release_installation.py | `COLLECTION_SIZE` placed between functions, away from the other module constants | confirmed | moved next to `REPOSITORY`/`SOURCE` |
| CR-002 | light-code-review F-002 (Spec) | low–medium | scripts/verify_release_integrity.py `check_release_manifest_consistency` | tagged release: count from the tag but claim from the working-tree manifest | confirmed | a resolvable tag now routes through the `revision` branch (manifest and count both from the tag); test edits the working copy after tagging and still expects 36; reverting the line fails the test |
| CR-003 | light-code-review F-003 (Spec) | low | scripts/verify_release_installation.py | one per-release `COLLECTION_SIZE` for pinned and main clones; re-verifying an older tag fails | out-of-scope | existing per-release design of this verifier; recorded as a limit |
| C-001 | Critic | medium | README(.zh-CN) category list; skills/README(.zh-CN) | old counts (36; project 8, thinking 5) | confirmed | counts fixed; v0.2.7 rename line made historical; new test `test_collection_guides_state_the_real_category_counts` (fails on a wrong count) |
| C-002 | Critic | medium | standing line vs light-implement claim/report; VS-4 Claude | standing line made Claude skip claim and report | confirmed | standing line narrowed to "before changing what any of them requires"; light-implement: a plan gap found at any step → claim, BLOCKED report with `Plan gap:`, then light-redirect; WORKFLOW §7 aligned; VS-4 rerun (b6) |
| C-003 | Critic | medium | AC-2, D3 on pi | negative case gained one read after integration (0/3 → 1/3, no effect) | confirmed, not repairable in package text | raise with the user as an approved-exception request |
| C-004 | Critic | medium | light-html-plan part 3 scope | every FAIL routed to part 3 | confirmed | part 3: `Cause: direction` FAIL only; `Cause: implementation` → part 2 (SKILL, writing.md, source-protocol); new scenario BFAIL (b6) |
| C-005 | Critic | low–medium | partial apply record | no defined line for one half applied | confirmed | PROPOSAL.md defines `SPEC applied — project-spec` / `Tickets applied — project-tickets`; Status table states the both-lines rule; project-spec/tickets use those lines; new scenario BTIX (b6) |
| C-006 | Critic | low–medium | hand edit owner | unclear who records `applied` | confirmed | the Agent leaves light-redirect, edits, then records `applied`; test renamed |
| C-007 | Critic | low | test_composition optional-calls test | one-way, wording-based | confirmed | test now derives declared optional calls from every SKILL and compares both ways; fallback checked by structure (two arrows); both directions mutation-checked |
| C-008 | Critic | low | light-redirect step 4 vs PROPOSAL; MAP-CONTRACT | move moment and line shape | confirmed | step 4 says "once you record approved or rejected"; MAP-CONTRACT shows both line shapes |
| C-009 | Critic | low | light-implement step 6 | report list missed `Plan gap:`; no rule for a local-fix answer | confirmed | step 6 lists `Plan gap:`; local fix → continue, next report supersedes |
| C-010 | Critic | low | light-html-plan openai.yaml | `$` prefix in default prompt | confirmed | removed |
| E-001 | Evaluator r1 | medium | light-html-plan source-protocol issues row; writing.md part 3 | `Plan gap:` not read by the page | confirmed | issues row reads outcome and `Plan gap:`; part 3 lists a `Plan gap:` no proposal answers yet; scenario BPGAP (b7) |
| E-002 | Evaluator r1 | low | skills/README(.zh-CN).md:17 | v0.2.7 rename line in present tense beside 39 | confirmed | past tense, names the 36-package total of that release |
| C-001..C-010 recheck | Critic r2 | — | — | C-001, C-002, C-004..C-010 fixed; C-003 open (user) | — | — |
| C-011 | Critic r2 | low | light-html-plan SKILL part 3 | open plan gap missing from the SKILL summary | confirmed | added |
| C-012 | Critic r2 | low | MAP-CONTRACT example | rejected line shape missing | confirmed | added |
| C-013 | Critic r2 | low | light-implement plan-gap bullet | no rule for a SPEC or conversation slice | confirmed | skip the claim, pass the returned report as the trigger |
| E-101 | Evaluator r2 | low | b7 pi-BPGAP page; source-protocol rule on proposed variants | pi invented two unlabelled options on the plan-gap card | recorded as limit | not blocking; one test Host |
