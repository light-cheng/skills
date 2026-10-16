# Live probe against local OpenDecider (2026-10-11)

Run: `TYPESAFE_BASE_URL=http://127.0.0.1:8001 ~/.hermes/environments/opendecider/bin/python -I <script> <repo>` (outside the sandbox).

- SDK answer shapes (probe.py): Score → `score`, `confidence`, `legend {0..n-1: label}`, `probabilities {0..n-1: p}` (int keys); Noul → `noul`; Choice → `choice`, `confidence`, `probabilities {name: p}`.
- Fix from this: `_bin_confidence` now reads `probabilities[level]` by int key and requires keys == range(levels) (was value order).
- e2e.py (agent-config, task "Redesign the consensus layer", baseline routine):
  - calibrated (0.5): complexity score 2.447 → high bin, bin confidence 0.39 → not applied (low-confidence); reasoning → high applied.
  - uncalibrated: both not applied (uncalibrated), deterministic profile kept.
- e2e.py (ask-light, two legal actions, calibrated 0.55): next-action → agent-config, conf 0.91, data on-device, backend `local` (matched by `names: ["127.0.0.1:8001"]`), applied; reasoning-escalation → no (0.64), applied.
