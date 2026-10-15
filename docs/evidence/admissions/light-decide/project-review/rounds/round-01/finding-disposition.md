# Findings registry

| ID | Sev | Source | Summary | Disposition | Status |
|---|---|---|---|---|---|
| F-001 | high | Critic r1 | Destination rule covers only network addresses; a local stdio MCP would classify third-party and fail VS-1 under the default limit | confirmed | pending |
| F-002 | medium | Critic r1 | "Active feature" undefined | confirmed | pending |
| F-003 | medium | Critic r1 | One-legal-option result shape and logging undefined | confirmed | pending |
| F-004 | medium | Critic r1 | `applied` undefined; `none` cases ambiguous | confirmed | pending |
| F-005 | medium | Critic r1 | Score `answer` and `confidence` undefined | confirmed | pending |
| F-006 | medium | Critic r1 | Policy key depends on call path | confirmed | pending |
| F-007 | low | Critic r1 | Calibration section mixes frozen labels with labeling logged rows | confirmed | pending |
| F-008 | low | Critic r1 | Unrecognized `Decision data:` value undefined | confirmed | pending |
| F-009 | low | Critic r1 | Availability assumes a status tool | confirmed | pending |
| F-010 | low | Critic r1 | Tests hard-code vocabulary, test the example's state and the stdlib; confidence rule untested | confirmed | pending |
| F-011 | low | Critic r1 | Missing question id / meaning of `<caller>` undefined | confirmed | pending |
| F-012 | low | Producer O-1 | Log time source unspecified; VS-1 wrote an approximate time | confirmed | pending |

O-2 (heredoc friction) rejected: Host behavior, not a package defect.
