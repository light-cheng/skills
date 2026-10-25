# Round 1 — Repair evidence

Repair commit: `db0f5d3` on top of `39732d6`.

| Label | Command or action | Observed |
|---|---|---|
| behavioral | Template copy at `db0f5d3` with dependencies, `npm test` | 98 pass, 0 fail (2 new tests: tab-less overview chapter and fallback; pocket stay order and instruction-only to-do) |
| behavioral | Mutation: same tests against `site-navigation.js` and `handbook.js` from `39732d6` | both new tests fail (18 pass, 2 fail) |
| structural | `python3 scripts/check_public_docs.py` | PASS |
| runtime | Rebuilt the Kyushu fixture project with the repaired files; Chromium 1366 and 390 | no console errors; tabs 01–05 unchanged; overview on to-do; 8 daily maps; no horizontal scroll; Copy still copies the card text |
| runtime | 390px daily sketch map screenshot | title line no longer drawn; legend line fits |
| structural | `index.html` | every changed asset at `?v=20261025-1`, `sync-ui.js` versioned |

Remaining limit seen while checking: in English mode the runtime "(Chinese only)" marker lengthens some sketch labels and can clip at the map edge (pre-existing behaviour of authored-text markers).
