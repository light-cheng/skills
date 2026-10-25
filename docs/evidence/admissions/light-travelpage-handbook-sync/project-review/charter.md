# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-10-25

## Acceptance baseline
- Source: PR #15 description (hand-drawn sketch map, 2026-10-17, second commit 2026-10-22); PR #16 description; the port list `模板回写清单.md` given to the owner on 2026-10-25 (sections 一–四); owner decision 2026-10-25 "改成四页（默认）" (the template default drops the separate route chapter).
- Source revision or identity: branch `claude/project-thread-ml55ij` (PR #16), stacked on `light-travelpage/sketch-map` (PR #15, head `fa1b9c3`); first reviewed head `39732d6`.
- Fixed point: ee05c3cf93c984be9f58c889cda1bdc8ebe0e67b
- Implementation scope: skills/productivity/light-travelpage/; CHANGELOG.md; CHANGELOG.zh-CN.md
- Approval state: approved
- Approval evidence: owner in the project thread on 2026-10-25: four-chapter default chosen on the decision card; "可以审查" (run the full review over #15 and #16).

## Review Profile
- Profile: agent-skill
- Selection reason: full-review change to an admitted model-invoked Skill whose template contains executable browser and build code (`scripts/sketch-layout.mjs`, `scripts/build-map.mjs`, `sketch-map.js`, `app.js`, `route-ui.js`, …). Executable code also gets `light-code-review` Standards and Spec findings.

## Original goal
Bring the generic improvements made on the live Kyushu trip page back into the `light-travelpage` template so new trips start from them, without Kyushu-only data.

## User-visible outcome
A page generated from the template has the hand-drawn route map, four chapters (itinerary · bookings · to-do · materials, plus ledger), daily sketch maps and weekdays in the itinerary, layered text instead of long paragraphs, to-do cards with Copy, a cash budget table and a stay list in the pocket page.

## In scope
- Template code, tests and assets under `skills/productivity/light-travelpage/assets/template/`.
- Package references touched by #15/#16 (`data-contract.md`, `display-and-navigation.md`, `handbook-design.md`) and the CHANGELOG pair.

## Out of scope
- The Kyushu trip itself, its data and deployment.
- AI integration, sync server and ledger behaviour (unchanged).
- Release, tag and published-install verification.

## Acceptance criteria
- AC-1 Sketch map (#15). With `map.style: "sketch"` the build derives each day's legs from `days[].schedule`, keeps nearby distinct stays as separate markers, writes a `*-sketch.svg` base, and the overview/handbook maps draw it; regions without the setting render as before.
- AC-2 Four chapters. Visible tabs are itinerary, bookings, to-do, materials, then ledger when enabled, numbered by visible order with no gaps; no route tab; the overview map shows at the top of to-do without day tabs; `#route` opens to-do; materials-only trips keep the direct topbar link; drafts survive chapter switches.
- AC-3 Daily view. Hand-drawn trips show each day's sketch map beside the itinerary; dated trips show weekdays in the day heading and date controls; undated drafts still work.
- AC-4 Layered text. `schedule[].detail`, ticket `guidance` arrays, stay `cancellationPoints`/`navigationPoints`, labelled/bulleted to-dos render as structure; records without these fields render as before.
- AC-5 Cards and budget. Text after a to-do's first blank line renders as a card with a working Copy button and fallback; `metadata.localLanguage` sets its `lang`; `preTrip.cashBudget` renders with `currency` as the amount header and stays hidden without rows; `on-site` tickets are not counted as pending.
- AC-6 Pocket and save. The pocket page lists every stay by date and puts tonight's first during the trip; a to-do cannot be resubmitted while its save is retrying, and the input clears only after a confirmed save.
- AC-7 No regression of newer template work. AI provider `on`/`ai-client.js`, `validate.mjs` credential checks and date-strip dragging stay as on `main`; no Kyushu-specific names, currency or language are hard-coded in template code.
- AC-8 Docs. References describe the new structure and optional fields, including the `?v=` rule; CHANGELOG has matching English and Chinese entries; `check_public_docs.py` passes.
- AC-9 Package integrity. Invocation type, dependencies, attribution and install surface unchanged; `create.mjs` produces a project whose `npm test` and `npm run build` pass; the repository suite shows no new failures against the fixed point.

## Required evidence
- Template `npm test`, repository `pytest`, `check_public_docs.py` (observed).
- Fresh project from `create.mjs`: install, test, build (installation/behavioral).
- Browser observation of a generated page with a real hand-drawn trip at desktop and 390px: four tabs, to-do overview, daily sketch map, weekday, layered text, card copy (runtime).
- Kyushu-string scan of template code (structural).
- `light-code-review` Standards and Spec findings on the diff from the fixed point (review).
- Fresh independent Evaluator report (review).

## Required validation scenarios
- VS-1 Fresh project from `create.mjs`, build and test.
- VS-2 Generated page loaded with the Kyushu trip data (local fixture only, not committed): desktop and 390px screenshots of itinerary, to-do and materials.
- VS-3 Demo template data (no optional fields): page loads with no console errors.

## Constraints, assumptions, and risks
- Producer and reviewers are the same model family; reviewers are fresh subagents with no shared context.
- The Kyushu data used for VS-2 is the owner's real trip; it stays outside the repository.
- No real Host trial of the Skill invocation is run; invocation type and SKILL.md are unchanged by this change.

## Approved exceptions
- none
