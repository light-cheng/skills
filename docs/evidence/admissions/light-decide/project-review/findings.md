# Findings registry

| ID | Sev | Source | Summary | Disposition | Status |
|---|---|---|---|---|---|
| F-001 | high | Critic r1 | Destination rule covers only network addresses; a local stdio MCP would classify third-party and fail VS-1 under the default limit | confirmed | fixed (Critic recheck at repair1) |
| F-002 | medium | Critic r1 | "Active feature" undefined | confirmed | fixed (Critic recheck at repair1) |
| F-003 | medium | Critic r1 | One-legal-option result shape and logging undefined | confirmed | fixed (Critic recheck at repair1) |
| F-004 | medium | Critic r1 | `applied` undefined; `none` cases ambiguous | confirmed | fixed (Critic recheck at repair1) |
| F-005 | medium | Critic r1 | Score `answer` and `confidence` undefined | confirmed | fixed (Critic recheck at repair1) |
| F-006 | medium | Critic r1 | Policy key depends on call path | confirmed | fixed (Critic recheck at repair1) |
| F-007 | low | Critic r1 | Calibration section mixes frozen labels with labeling logged rows | confirmed | fixed (Critic recheck at repair1) |
| F-008 | low | Critic r1 | Unrecognized `Decision data:` value undefined | confirmed | fixed (Critic recheck at repair1) |
| F-009 | low | Critic r1 | Availability assumes a status tool | confirmed | fixed (Critic recheck at repair1) |
| F-010 | low | Critic r1 | Tests hard-code vocabulary, test the example's state and the stdlib; confidence rule untested | confirmed | fixed (Critic recheck at repair1) |
| F-011 | low | Critic r1 | Missing question id / meaning of `<caller>` undefined | confirmed | fixed (Critic recheck at repair1) |
| F-012 | low | Producer O-1 | Log time source unspecified; VS-1 wrote an approximate time | confirmed | fixed (Critic recheck at repair1) |

| F-013 | medium | Critic recheck | Repair-1 manifest missing (setup command blocked) | confirmed | fixed (candidate-manifest-repair1.txt written) |
| F-014 | low | Critic recheck | Score answer/options/confidence vs general rules | confirmed | fixed (Critic recheck at repair2) |
| F-015 | low | Critic recheck | User-named source outside limit or unavailable skipped silently | confirmed | fixed (Critic recheck at repair2) |
| E-001 | low | Evaluator | Error reply had no fallback_reason | confirmed | fixed (repair3, Evaluator recheck) |
| E-002 | low | Evaluator | Calibrated policy path unobserved; Host blocked reading user-level policy file | confirmed | recorded limitation (no package change) |
| E-003 | low | Evaluator | Temp VS projects not cleaned up | confirmed | fixed (deleted after recheck) |
| E-004 | low | Evaluator | Score bin boundary ownership unspecified | confirmed | fixed (repair3, Evaluator recheck) |

O-2 (heredoc friction) rejected: Host behavior, not a package defect.
