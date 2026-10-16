# Choosing and asking a source

## Sources

A source has two properties. Record both on every judgment.

- **Method**: `typed-decision` (a decision model or interface that returns
  probabilities over the given options) or `self-judgment` (you decide).
- **Data destination**: the farthest machine the state reaches. `on-device`
  (this machine), `private-network` (a machine on the user's own network), or
  `third-party` (someone else's service). Self-judgment records `in-session`.

Name the backend with the name the user gave it in the policy file (see
[formats](formats.md)). Without a policy entry, use the name the Host reports:
the MCP server name, or the model id the endpoint returns. Never write a URL,
key or local model name into a skill or a repository.

Decide the destination from where the model runs, using evidence from this run:

- A model served on a loopback address, or by a process on this machine that
  runs the model itself, is `on-device`. A locally launched MCP server counts
  only when its status or configuration shows where its model runs.
- A private address the user named is `private-network`.
- A local process that forwards to another machine takes that machine's
  destination.
- Anything else, and anything unknown, is `third-party`.

## Data limit

`Decision data: on-device | private-network | third-party | off` in
`docs/agents/light-project.md` names the farthest destination allowed. Each
level includes the nearer ones. No line means `on-device`. `off` is a hard
limit: self-judgment only. A value outside this list also means `off`; tell
the caller the line is unrecognized.

## Availability

A source is available only with evidence from this run:

- an MCP decision tool appears in this session and a read-only call (its status
  tool when it has one) succeeds, or the first decision call returns a
  well-formed result; or
- the decision endpoint's readiness check (`/ready`) returns true, or the
  caller's script reports the client ready.

A configuration file alone is not evidence. A status field such as `loaded:
false` does not mean unavailable: some services load the model on first use.

## Selection order

Pick the first that fits, within the data limit:

1. The source the user named for this run, when it is within the limit and
   available. Otherwise skip it and tell the caller why.
2. A source calibrated for this question id (see the policy file in
   [formats](formats.md)).
3. An available uncalibrated source. Ask it, record its answer, and use your
   own judgment as the final answer (reason `uncalibrated`).
4. Self-judgment.

When several sources tie on a step, pick the nearest destination:
`on-device`, then `private-network`, then `third-party`.

Ask exactly one source per judgment. Comparing sources is calibration work, and
it runs on a labeled evaluation set, never on live judgments.

## Two call paths

| Path | Who calls | Use when |
|---|---|---|
| Script → SDK | The caller's own script | The caller has a script with a decision client. Swapping backends changes only the client's base URL. |
| Agent → MCP | You | The caller has no script, or its script cannot reach a source. Use the result directly, or pass the normalized result to the caller's script. |

Batch independent questions into one request. Asking the same question again is
not progress.

## Timing

The first call to a lazily loaded local model can take about two seconds longer
than later calls. Allow at least ten seconds. A timeout falls back with reason
`timeout`.

## Calibration

Calibration runs only when the user asks for it, in two separate parts:

1. **Collect cases.** Rows in `decisions.md` files, including other projects',
   are candidate cases. Rows where the source's answer and the final answer
   differ are a useful start, not the whole set. The user labels each case
   before any source answers it again.
2. **Measure.** Run each source on the labeled set, keep calibration cases
   separate from held-out cases, and record thresholds in the policy file.

Logged answers are never scored as calibration results, and a past row is never
back-filled as right or wrong.
