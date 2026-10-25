# Round 1 — light-code-review, Spec axis

Reviewer: fresh general-purpose subagent, no shared context, read-only. Spec: `charter.md` AC-1..AC-9 and the port list. Diff `ee05c3c...39732d6`.

- C-001 medium: with to-do off and overview on, `#route` maps to the disabled to-do chapter and falls back to itinerary; the overview map and the pocket/day-map links to it become unreachable (AC-2).
- C-002 medium: the tab-less `overview` chapter holds only `#map-examples`; demo map examples become unreachable, and with itinerary/bookings off the fallback shows a blank overview chapter (AC-2, VS-3).
- C-003 low: `display-and-navigation.md` still says "Stays appear between flights and the route" (AC-8).
- C-004 low: `.todo-card` hard-codes a Japanese font stack (AC-5, AC-7).
- C-005 low: pocket `summary()` shows the card text for a to-do whose instruction line has no `。；：:` before the blank line (AC-6).
- C-006 low: cash-budget amount header falls back to 金额 instead of the trip currency named in the port list (AC-5).
- C-007 low: `geographicFocusViewport` adds a zoom crop for every `geographic-inset` map, not requested; regions without the sketch setting change (AC-1).

Checked with no finding: tab numbering and materials placement with/without ledger; `#route` with overview off; weekday on undated trips; card rule as written; tonight logic (`checkIn <= today < checkOut`, trip time zone); resubmit guard paths; CHANGELOG pair; handbook-design.md.

Summary: 7 findings (2 medium, 5 low).
