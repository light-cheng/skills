# Round 1 — Finding disposition (Core)

| ID | Source | Severity | Disposition | Reason / repair |
|---|---|---|---|---|
| P-1 | Producer | medium | confirmed | Daily sketch map title cut off at 390px. Repair: `dayTitle: false` for the itinerary embed (the page already shows the title). |
| P-2 | Producer | low | rejected | Expected behaviour; documented `currency` field. |
| S-001 | Standards | medium | confirmed | Bump `?v=` of every changed asset to `20261025-1`; give `sync-ui.js` a version. |
| S-002 | Standards | medium | confirmed (partial repair) | Added English for the static strings (取消和付款, 位置和入住, 旅行路线, both sketch legends). Dynamic sketch captions ("今晚住 X", "住 N 晚") keep the existing i18n limitation of runtime-composed text; recorded as a limit. |
| S-003 | Standards | low | confirmed | Removed the dead `i18n.js` entry; `handbook.js` keeps "Daily places". |
| S-004 | Standards | low | rejected | The popover uses compact `<p>/<ul>` markup and needs a lead to stay short; reuse would add a mode flag for little gain. |
| S-005 | Standards | low | duplicate of C-005 | Pocket now reads only the instruction line; the label regex stays local to each file because `handbook.js` loads without `app.js` in its tests. |
| S-006 | Standards | low | rejected | The id-prefix rewrite only touches ids and one data attribute inside generated SVG; label text with "sketch-" is not produced by the template. Not worth a helper now. |
| S-007 | Standards | low | rejected | Repeated pure calls on short strings; no measurable cost. |
| S-008 | Standards | low | confirmed | `esc(color)` in the step marker. |
| C-001 | Spec | medium | confirmed | `site-navigation.js`: overview home is to-do when enabled, else a tab-less `overview` chapter that `#route` opens. New test. |
| C-002 | Spec | medium | confirmed | `#map-examples` travels with `#route`; `overview` is never the fallback while to-do is on. New test. |
| C-003 | Spec | low | confirmed | Sentence rewritten. |
| C-004 | Spec | low | confirmed | Neutral default font; Japanese and Korean stacks via `:lang()`. |
| C-005 | Spec | low | confirmed | Pocket summary uses the first line only. New test. |
| C-006 | Spec | low | rejected | The data contract has no trip-level currency field; the port list wording was loose. `data-contract.md` documents `currency` as the header. |
| C-007 | Spec | low | confirmed | Removed `geographicFocusViewport` and its dialog crop; the dialog matches #15 again. |
