# Implement workflow

Supporting detail for `light-implement`. `SKILL.md` is the entry;
this file holds the full step description.

## Entry condition

- User explicitly invokes `light-implement` with a bounded work item: a path to
  `.scratch/<feature>/issues/NN-<slug>.md`, a path to
  `.scratch/<feature>/spec.md` (or a narrow section of it), or a small
  explicit conversation slice.
- Do not synthesize a scope from a vague thread without a Spec or ticket.
  That case belongs to `project-clarify` / `project-spec` first.
- One run covers **one** work item inside **one** fresh context window. Do not
  batch many tickets in one run and do not pre-load several tickets to execute
  in sequence.

## Inputs and ticket consumption

`project-tickets` produces one file per ticket under the tracker convention
used by the active repository (`.scratch/<feature>/issues/`). Wayfinding
operations:

```text
.scratch/<feature>/issues/NN-<slug>.md    # from 01 in dependency order
```

Each file carries near the top:

```text
**Blocked by:** 01, 03
**Status:** ready-for-agent | claimed | resolved
```

and a body starting `**What to build:**` with acceptance criteria.

When `light-implement` is passed a ticket path:

1. Read the file body and its header lines. Record the title, `Blocked by` set,
   `Status`, and parent Spec pointer (the ticket body normally cites the Spec
   path). If the caller used `#NN` rather than a full path, confirm the title
   back against the file on disk before proceeding (mirrors the Matt upstream
   guidance on ticket-number resolution).
2. Verify the ticket is `ready-for-agent` (treat `open` as its alias when the
   caller scanned an unblocked frontier) and that every blocker listed in
   `Blocked by` is `resolved`. If not ready or blocked, report `BLOCKED` and
   stop — do not jump to a different ticket. A `claimed` ticket is in progress
   in another run: report `BLOCKED` unless the user confirms that this run
   resumes that claim (for example after a `project-review` `FAIL`).
3. Treat the ticket body as the bounded Spec for this run. Do not re-slice it,
   merge other tickets, or broaden its acceptance.
4. Claim the ticket before changing any other file: set `**Status:** claimed`
   and save. It tells concurrent sessions to skip the ticket and tells a plan
   view that the work is in progress. `project-review` resolves the ticket
   after a `PASS`. The claim and the implementation report (step 7) are the
   only tracker writes this Skill makes.
5. The run works in a single independent context and produces one bounded diff
   (or one non-code artifact) attributable to that ticket only.

For a small Spec slice or conversation slice, record the scope string and
limit the diff to that slice. Any gap that makes the scope ambiguous is a
handoff gap — report it rather than inventing a broader scope.

## Steps

### 1. Pin the work item and the fixed point

- Resolve the exact item path and read its full body plus comments. For a
  ticket, load its parent Spec at `.scratch/<feature>/spec.md` for provenance;
  the ticket body remains the bounded authority.
- For code work, note the fixed point for later `light-code-review`: the branch
  point or the reference the user passed (default to the fork-point of the
  current branch). Do not start changing files if the fixed point cannot be
  resolved.

### 2. Inspect relevant context

- Skim the domain glossary (`CONTEXT.md` / `CONTEXT-MAP.md`), ADRs, and only
  the source or templates the item touches. Locate the seams (public
  boundaries) that the work will be verified at; prefer existing seams.
- Record each usable fact with a bounded locator (file + heading/symbol/line).
  A seam or contract that the item assumes but the inspection cannot find is
  an evidence gap — note the `BLOCKED` location rather than assuming it.
- Keep this inspection bounded; it exists to avoid proposing a seam the repo
  cannot host.

### 3. Offer execution routing when materially useful (optional opt-in)

`agent-config` is an optional planning enhancement, not an automatic call.
`light-implement` never invokes `agent-config` automatically unless the user explicitly
requested routing.

#### A. Evaluate whether routing would materially help

Assess whether the task would benefit from:

- profile-driven execution topology (evaluating single-pass vs decomposed task shape on the current Host);
- ticket graph coordination (frontier scheduling across ready dependency items without embedding runtime config into tickets);
- effort resolution (mapping abstract task uncertainty to host-supported reasoning effort);
- model tier routing (matching routine vs demanding slices to user-confirmed profile tiers);
- delegated execution with fresh worker contexts or concurrency;
- stronger independent review context.

Do not invoke `agent-config` for legacy fixed roles (Controller, Explorer, Merger) or mandatory waves; execution topology adapts dynamically to current host capabilities and user-confirmed profiles.

For clearly bounded solo work (e.g., modifying one function, fixing a typo,
updating a configuration file, adding an isolated test, or updating documentation),
skip the offer and proceed directly with single-agent execution.

#### B. User choice contract

When routing could materially help:

1. Present the choice explicitly to the user:
   - Option A: Use `agent-config` to configure profile-driven model tier, reasoning effort, and execution topology (`Scope: current-item`).
   - Option B: Continue directly with single-agent execution using the current model.
2. If the user accepts: invoke `agent-config` (model-invoked, `Scope: current-item`), present the plan,
   and execute according to the resulting plan.
3. If the user declines: continue implementation directly without blocking.

#### C. Explicit user intent overrides

- If the user's invocation already expressed explicit intent to route (e.g.,
  "use agent-config", "use routing", "plan agents first"): invoke `agent-config`
  directly without asking again.
- If the user's invocation explicitly skipped routing (e.g., "don't use
  agent-config", "skip routing", "just implement it"): do not offer or invoke
  `agent-config` during that run.

#### D. Non-blocking fallback

`light-implement` remains fully functional without `agent-config`. A missing model
selector, unavailable `agent-config`, or user decline must never convert into a
`BLOCKED` implementation by default. Unless the task itself carries a hard,
unresolvable constraint, continue safely under serial execution with the current
model. A fallback requires evidence that the problem affects only optional
routing, that the current session is capable and authorized for this item,
and that the user has not required the failed route. State the reason and
continue without another setup question. Never bypass model restrictions,
configuration-preview approval, required independent review, or a user-required
execution method. If the rejection scope is unclear, stop and report it.

#### E. AgentConfigResult consumption rules

When `agent-config` is invoked, `light-implement` inspects the canonical `AgentConfigResult` envelope:

- **`readiness === "READY"`**: Consume `execution_config` (model, resolved reasoning effort, worker context, review context) and proceed to execute the bounded slice.
- **`readiness === "NEED_INPUT"`**: Profile is missing or setup is required (`setup_state.profile === "missing"`). If section D's fallback conditions are met, continue the item directly; do not wait for the user to decline setup. Otherwise report the needed setup and obtain its explicit authorization before starting it. A declined setup does not override a required route or task constraint.
- **`readiness === "NEED_PROJECT_TICKETS"`**: Task is classified as decomposed without formal tickets (`handoff: "project-tickets"`). Halt implementation immediately, recommend explicit `project-tickets`, and stop. Never batch-execute un-ticketed tasks inside a single light-implement run.
- **`readiness === "BLOCKED"` or `"UNSUPPORTED"`**: Stop the rejected configuration and inspect the diagnostic. Continue directly only when section D's fallback conditions are evidenced. Otherwise halt implementation and report the diagnostic to the caller; a missing or ambiguous diagnostic is not permission to fall back.

### 4. Execute the bounded slice

Branch by artifact type. One item produces one slice through every relevant
layer (tracer-bullet), sized for the single context window.

**Code artifact** (default branch when the item touches `src/`, tests, or a
software Profile):

1. Read the Spec/slice and existing test approval. Follow `light-tdd`'s seam
   confirmation rule, reusing approval for the same seam and confirming new
   or materially changed boundaries before writing tests.
2. Drive `light-tdd` (model-invoked) at those seams. One red→green cycle at a time:
   a named seam, a failing test in the correct harness location, then the
   minimal implementation that makes that test pass. Do not write tests bulk
   ahead of implementation. Follow `light-tdd`'s seams, anti-patterns, and loop
   rules — do not duplicate them here.
3. The run's editorial position is **tracer-bullet vertical**: each cycle is a
   narrow but complete path through the relevant layers, demoable on its own.

**Document / configuration / research artifact / Skill / generic task**
(branch when the item's deliverable is not executable code):

1. Resolve the artifact's template or contract (e.g., `SKILL.md` shape,
   proposal template, configuration schema, research Markdown). Prefer the
   template the Spec names; when none is named, use the item body's stated
   structure.
2. Produce the artifact once. Keep it bounded to the item — do not pull in
   sibling tickets or the broader Spec.
3. The item's body is the contract; do not broaden it to "finish the whole
   feature".

### 5. Verify locally

**Code:** typecheck often and run single test files often during the loop;
run the full relevant test suite once at the end, including focused boundary
and failure cases relevant to the changed behavior. Report any environment or
dependency gap as a limitation. Code that cannot be exercised by focused tests
adds a representative runtime or integration observation.

**Non-code:** run the verification the item's contract implies: render the
document in its target format and spot-check a real output, validate the
configuration or schema, or perform the domain check the Spec names. Record
the observation path rather than asserting correctness abstractly.

A verify step that surfaces a missing requirement (new ticket, Spec revision,
ADR) is a stop — report the gap rather than repairing by broadening scope.

### 6. Hand to `review-loop` when appropriate

Package the evidence for `review-loop`:

- frozen item path and acceptance source with revision,
- fixed-point identity and bounded diff or artifact observation,
- verification outputs (test commands and results, render/schema observation),
- limitations (unavailable dependencies, environments, generated outputs, or
  untestable paths).

Select the reviewer implied by the artifact and call it through `review-loop`:

- **Code** → `light-code-review` (Standards + Spec) as the specialist reviewer. It
  returns candidate findings; `review-loop` drives convergence and
  `project-review` owns any final verdict.
- **Non-code** → `generic-review` (or an available domain reviewer). Do not
  call `light-code-review` on a non-code diff.

Do not copy the reviewer's rubric or the acceptance/state machine into this
file; call those Skills via their public protocols.

### 7. Write the implementation report

For a tracker ticket, append one report under the ticket's `## Comments` when
the run ends, whether it handed off to review or stopped `BLOCKED` after the
claim. Earlier reports stay; the newest one is current. `project-review` and a
plan view read this report, so a fresh session can continue from the file
alone.

```markdown
### Implementation report — <YYYY-MM-DD>
- Outcome: handed to review | BLOCKED: <gap and smallest unblock>
- Fixed point: <full commit SHA the change is reviewed against>
- Candidate: <full commit SHA of the committed change, or artifact path>
- Implementation scope: <repository-relative literal paths this run changed>
- Verification:
  - `<exact command or observation>` → <observed result>
- Review: review-loop <rounds run>/<limit>, <converged | limit reached | not run: reason>
- Remaining findings:
  - <F-###> · <severity> · <location> · <problem> · <reason>
- Limitations: <unavailable dependencies, environments, untestable paths, or none>
- Plan gap: <none, or one sentence on what in the approved SPEC, ticket or acceptance items no longer holds>
```

Write `none` for an empty list; leave no field out. `Plan gap:` names a
problem with the plan itself (a missing or wrong requirement, tickets that
contradict each other or the SPEC), not with the work; the run stops
`BLOCKED` with it, leaves the plan as approved, and hands it to `light-redirect`
([Optional capabilities](../SKILL.md#optional-capabilities)). Copy each remaining
finding from the last `review-loop` report with its original ID and fields,
so the next review can recheck it. A non-code item records its artifact
path in `Candidate:`, its render or schema observation under
`Verification:`, and `Fixed point: none` when it has no commit base.

For a Spec slice or conversation slice there is no ticket file. Return the
same fields to the caller in the handoff.

## Boundaries

- One item per run. A new ticket needs a fresh `light-implement` invocation in a
  fresh context. Do not merge sibling tickets to "save a round trip".
- Inspect only what the item names; do not run a whole-repo redesign inside an
  item.
- `agent-config`, `light-tdd`, `review-loop`, `light-code-review`, and `generic-review`
  are composition targets, not text to duplicate. Call them per their
  instructions.
- This Skill commits its bounded change to the current branch (mirroring the
  Matt baseline) but does not push or publish. It claims the ticket and
  reports on it; `project-review` resolves it.

## Handoff options

- On a verified diff/artifact, invoke `review-loop`, write the implementation
  report, and return this item's status, evidence, and outstanding findings to
  the caller. The caller owns
  any remaining authorized work; this handoff does not complete the larger
  request. A new ticket still requires a fresh `light-implement` invocation in a
  fresh context, and review limits and approval gates still apply.
- On a `BLOCKED` gap (missing Spec/ticket/authority/Spec-fidelity decision),
  report the gap with the smallest unblock and stop without branching into
  clarification or reticketing.
- If a focused question is needed for a human decision, recommend
  `ask-light` or `clarify` and stop; the recommendation is not an automatic
  invocation.

