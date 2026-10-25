# Round 2 — Producer evidence (repairs for E-001..E-003)

| Label | Command or action | Observed | Finding |
|---|---|---|---|
| behavioral | New tests: `layered-text.test.mjs` "a to-do cannot be resubmitted while the previous save is pending or busy", "the to-do input clears only after the save is confirmed, including a recovered retry"; `handbook.test.mjs` "during the trip the pocket puts tonight's stay first and marks it" | template `npm test` 101 pass, 0 fail | E-001 |
| behavioral | Mutations in a scratch copy: guard disabled; input cleared right after `applyChange` instead of after confirmation; tonight-first ordering removed | the three new tests fail (98 pass, 3 fail); restored copy 101/101 | E-001 |
| structural | Review records committed with the round-2 repair commit | in git | E-002 |
| runtime | Chromium 1366×900 and 390×844, template source served with its own (unconfigured demo) `trip-data.json`, `/api/*` stubbed empty | no console or page errors; loading error hidden; no tabs shown because the demo data enables no modules; no horizontal scroll | E-003 |
