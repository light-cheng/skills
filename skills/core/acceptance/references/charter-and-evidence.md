# Charter, Evidence, and Verdict Schemas

Durable file templates, canonical singleton rules, evidence labels, and rubric gates for **Charter scale** acceptance under `.scratch/<feature>/acceptance/` (or `.scratch/acceptance/<slug>/`).

## 1. Acceptance Charter (`charter.md`)

Freeze source identity, scope, criteria, and profile here at `init`. Link to `charter.md` from `state.md`, `rounds/`, and `verdict.md` rather than duplicating criteria across files.

```markdown
# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: <ISO-8601 timestamp>

## Acceptance baseline
- Source: <approved spec, ticket, or brief path/identifier>
- Source revision or identity: <git SHA, version, or timestamp>
- Fixed point: <software Profile only: one full 40-char Git commit SHA; otherwise "Not applicable - non-software profile">
- Implementation scope: <software Profile only: ';'-separated repo-relative POSIX literal paths; otherwise "Not applicable - non-software profile">
- Approval state: approved | pending user confirmation
- Approval evidence: <quoted approval status, user confirmation, or approved brief receipt>

## Review Profile
- Profile: generic | software | manuscript | agent-skill | specification
- Selection reason: <why this Profile governs the target>

## Goal and observable outcome
- Original goal: <concise outcome preserved from source>
- User-visible outcome: <observable state when accepted>

## Scope
- In scope: <bounded deliverables, modules, or milestones>
- Out of scope: <explicit exclusions>

## Acceptance criteria
- AC-1: <checkable condition and required evidence label> (traces: <US-n / ticket NN / brief section>)

## Required validation scenarios
- VS-1: <setup, action, expected observable output, and cleanup>

## Constraints, assumptions, and approved exceptions
- Constraints: <material limits or "None">
- Approved exceptions: <post-review user-accepted Medium/Low risk with actor + timestamp, or "None">
```

### Charter immutability and `changes.md`

Never edit an approved `charter.md` in place to help an implementation pass. When a human-approved **Change proposal** (via `redirect` or explicit user instruction) alters scope, profile, or criteria, preserve prior Charter content, append a `CP-###` entry to `changes.md`, and write the incremented `Charter revision: <n+1>`:

```markdown
## CP-001 - <short title>
- Proposed at: <ISO-8601 timestamp>
- Source proposal: <.scratch/<feature>/changes/NN-slug.md or user directive>
- Reason: <why the prior Charter revision changed>
- Old Charter revision: <n>
- New Charter revision: <n+1>
- Impacted criteria and rounds: <AC IDs and invalidated evidence>
- Decision: pending | approved | rejected
- Decision evidence: <recorded human approval>
```

## 2. Canonical evidence labels

Assign **exactly one** primary label to each recorded evidence item `E-###` (supporting artifacts of other classes may be linked, never relabeled):

- `source`: approved baseline document, commit SHA, or brief receipt.
- `structural`: static file, directory, YAML/JSON schema, frontmatter, or link inspection.
- `behavioral`: executed automated test or command exercising success, boundary, and failure/negative cases.
- `installation`: clean install, symlink, plugin validation, or package discovery observation.
- `invocation`: observed skill trigger, boundary routing, or CLI entrypoint invocation check.
- `runtime`: end-to-end execution or render check in a representative target environment/renderer.
- `manual`: reproducible human inspection where automation is impossible, naming actor and steps.
- `review`: fresh-context Critic, specialist (`code-review`), or independent Evaluator report.

Static grep, fixture syntax checks, or mock-only checks stay `structural` or `behavioral` as observed; never relabel them `runtime` or visual render evidence.

## 3. Round evidence records (`rounds/round-NN/`)

### `producer-evidence.md`

```markdown
# Producer Evidence - Round <NN>

- Note: Producer evidence only, not final acceptance.
- Charter revision: <n>
- Profile: <profile>
- Scope check: <in-scope summary and out-of-scope cleanliness check>

## Evidence items
### E-001 - <short label>
- Evidence label: structural | behavioral | installation | invocation | runtime | manual | review | source
- Command or action: <exact reproducible command or inspection>
- Expected: <AC-backed outcome>
- Observed: <actual exit code, summary, or artifact hash>
- Outcome: PASS | FAIL | BLOCKED
- Validates: <AC-n / VS-n>
- Limitations: <environment constraints or "none">
- Artifact: <path or log excerpt>
```

### `repair-evidence.md`

When `Status: REPAIR` runs in round `NN`, record:
- Confirmed `F-###` IDs addressed;
- Exact modified paths (verified inside Charter `In scope` / `Implementation scope`, and committed when `Profile: software`);
- Refreshed `E-###` verification commands and observed outputs;
- Remaining limitations. Never delete `producer-evidence.md` or `critic-findings.md`.

### `evaluator-verdict.md`

Written from the **separate fresh-context** Evaluator subagent's response:

```markdown
# Independent Evaluator Report - Round <NN>

- Evaluator context: <subagent/session id>
- Independence: full | degraded | unavailable
- Charter revision: <n>
- Profile: <profile>
- Recommendation: PASS | FAIL | BLOCKED

## Criterion audit
- AC-1: satisfied | unmet | blocked (evidence: E-001 [behavioral], E-003 [review])

## Finding audit
- F-001: resolved | confirmed | rejected (verification: <round repair/evidence link>)

## Summary and next action
<concise audit rationale, any newly spotted gap, or unblock action>
```

## 4. Finding registry (`findings.md`)

Single source of truth for `F-###` lifecycle across all rounds:

```markdown
# Finding Registry

## Finding F-001
- First recorded: round-01 | implementation report (<ticket path>, <source ID>)
- Axis: Standards | Spec | generic | <profile-axis>
- Status: pending | confirmed | rejected | duplicate | out-of-scope | resolved
- Severity: Critical | High | Medium | Low
- Related acceptance criterion: AC-<n> | none (<reason>)
- Canonical summary: <one stable statement of the gap>
- Related finding: F-<n> | none
- Current evidence: <round critic/producer link>
- Resolution evidence: <repair + re-review + Evaluator verification, or rejection reason>
```

### Severity and rubric PASS gate

Severity measures impact against the frozen Charter, never repair effort:
- `Critical`: unsafe behavior, data loss/privacy breach, corrupt output, or unusable primary goal.
- `High`: required `AC-<n>`, public seam, or mandatory Profile axis is unmet.
- `Medium`: material in-scope defect, boundary gap, or missing check; blocks `PASS` unless `charter.md` records post-review user risk acceptance (exact statement, actor, timestamp).
- `Low`: minor observation that does not block `PASS` unless `charter.md` elevates it.

**PASS gate:** Both `acceptance` Core and the fresh Evaluator require every `AC-<n>` and applicable Profile axis to carry valid evidence of the required label, every `VS-<n>` scenario executed (or covered by an approved exception), zero unresolved `confirmed` blocking findings (`Critical`, `High`, unaccepted `Medium`), intact Charter identity, and recorded `independence: full` (or explicitly accepted `degraded` where permitted).

## 5. Lifecycle state (`state.md`) and terminal verdict (`verdict.md`)

### `state.md`

```markdown
# Acceptance State

- Status: INIT | READY | CRITIC | REPAIR | EVALUATE | PASS | FAIL | BLOCKED
- Charter revision: <n>
- Profile: generic | software | manuscript | agent-skill | specification
- Round: <integer >= 1>
- Max rounds: 3
- Independence: full | degraded | unavailable | required
- Updated at: <ISO-8601 timestamp>
- Last completed action: <step summary>
- Next action: <exact next step, or "none (terminal)">
- Blocker: <none, or exact blocker + owner + smallest unblock step>
- Links: charter.md, findings.md, rounds/round-<NN>/
```

### `verdict.md`

Every singleton identity field below must appear **once** without aliases (`Verdict:` only; never substitute `Result:`, `Outcome:`, `Status:`, or `State:`):

```markdown
# Acceptance Verdict

- Verdict: PASS | FAIL | BLOCKED
- Charter revision: <n>
- Profile: generic | software | manuscript | agent-skill | specification
- Round: <integer >= 1>
- Independence: full | degraded | unavailable
- Reviewed implementation revision: <full 40-char Git SHA; include for software Profile only>
- Cause: <implementation | direction; include when Verdict is FAIL>
- Issued at: <ISO-8601 timestamp>

## Criterion summary
- AC-1: <outcome + primary evidence IDs and labels>

## Open findings and exceptions
- <none, or F-### list and approved exceptions>

## Risks and reopen rule
- <residual risks; any in-scope drift after Reviewed implementation revision or locked snapshot stales this verdict and requires a fresh run>
```
