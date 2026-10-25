# Round 1 — light-code-review, Standards axis

Reviewer: fresh general-purpose subagent, no shared context, read-only. Diff `ee05c3c...39732d6`. Report quoted in full below (lightly reformatted).

- S-001 medium (hard): index.html — i18n.js, overview-map.js and sync-ui.js changed but their `?v=` was not bumped (sync-ui.js has none); breaks the rule this change writes into handbook-design.md; returning visitors can mix new app.js with old i18n/overview-map.
- S-002 medium (hard, i18n gap): sketch-map.js header/label strings ("圆圈数字是当天第几步，箭头是方向", "今晚住 …", "（未订）", "住 N 晚", "圆圈数字是第几天 · 实心点是住宿", "旅行路线") and travel-cards.js "取消和付款", "位置和入住" have no i18n entries.
- S-003 low: "当天地点" translated twice (i18n.js "Places today", handbook.js "Daily places").
- S-004 low (possible Duplicated Code): schedule detail markup in app.js `scheduleTextMarkup` and the route-ui.js popover, with different conditions.
- S-005 low (possible Duplicated Code): to-do label regex copied three times (app.js ×2, handbook.js).
- S-006 low (possible Repeated Switches): `source.sketch && typeof sketchMapArtwork === "function"` in four places; `.replace(/sketch-/g, …)` id prefixing also rewrites `data-sketch-version` and any "sketch-" in label text.
- S-007 low: `splitTodoCard` and `ticketGuidanceLines` computed twice per item.
- S-008 low: sketch-map.js `fill="${color}"` from `routes[].color` not escaped (build-generated; same pattern as existing `--route-color`).

Escaping of trip and to-do data otherwise verified across app.js, handbook.js, travel-cards.js, route-ui.js, sketch-map.js, sketch-layout.mjs. Tests check behaviour, not wording.

Summary: 8 findings (2 medium, 6 low).
