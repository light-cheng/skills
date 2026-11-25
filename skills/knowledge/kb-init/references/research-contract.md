# KB Init Research Contract

External research resolves verifiable facts (platform capabilities, official APIs/connectors, attachment/search/export limits, domain standards) that bear on an open knowledge-base decision. Keep research tightly bounded so it never turns into a parallel architecture process or silently decides on the user's behalf.

## 1. Frame the decision before dispatch

Before starting research, define internally:

- **Paused decision**: the exact unresolved choice (base selection, connection feasibility, attachment handling, search/scale limits, backup/export fidelity).
- **Research question**: one narrow, verifiable question answerable from primary sources.
- **Comparison level**: like-for-like options occupying the same decision role (if cross-layer comparison is unavoidable, normalize around one user decision and state each option's role).
- **Must verify & out of scope**: only the facts that could change the paused decision, explicitly excluding downstream consumer design or unrelated setup tutorials.
- **Return condition**: the evidence required to resume the paused decision.

## 2. Dispatch via `research` with graceful fallback

1. **Primary path (`research` installed)**: Invoke the Base workflow `research` skill against primary sources (official documentation, specifications, official repositories, first-party APIs), never bypassing an available `research` skill with ad-hoc secondary summaries.
2. **Graceful fallback (`research` not installed)**: Dispatch a **fresh-context** primary-source research subagent (launch it with a fresh context window, never a fork of the current conversation) instructed to verify every claim against primary sources, record `YYYY-MM-DD` retrieval dates or `repo@commit` anchors, and write cited findings to a single Markdown report. If the current harness cannot spawn subagents, run bounded primary-source verification inline under the same citation and artifact-isolation rules, or keep the decision `unresolved` if primary sources are unreachable.

Before dispatching, tell the user briefly which decision is paused, what fact is being checked, and why it matters. Never ask the user for public documentation URLs you can find yourself; ask only when a target system is private or internal.

## 3. Dispatch verification and pre-approval artifact isolation

- **Verified dispatch state**: Mark a decision `researching` and tell the user research is underway **only after** the harness confirms the `research` call or subagent task actually started (for example via a task/conversation ID or running state). An intention to research is not an active run; if dispatch fails, report that it did not start and keep the decision `unresolved`.
- **Pre-approval `.scratch/` isolation**: Research notes created before SPEC approval are design evidence, not final knowledge-base deliverables. Write them outside the intended KB destination (prefer `.scratch/kb-init/research/` or session/OS scratch). If harness rules force project-local output, keep it inside `.scratch/` (clearly separated from the KB target), exclude it from final KB deliverables unless the user asks to retain it, and state that scratch research-note exception accurately at the SPEC approval gate.

## 4. Completion verification and conflict handling

Treat a research run as usable only when all five checks hold:

1. the `research` skill or fresh-context subagent finished cleanly (never summarize partial or aborted runs as findings);
2. the expected report artifact exists;
3. you have opened and read the report yourself;
4. it answers the framed question;
5. material claims cite primary sources with explicit `YYYY-MM-DD` or `repo@commit` anchors.

If a run aborts, fails, or produces no usable artifact, tell the user it did not complete, keep the decision `researching` or `unresolved`, and offer to retry, narrow the question, or defer.

When resuming the interview, present in order: (1) verified facts and anchors, (2) limits or uncertainty, (3) impact on the paused decision, (4) an optional recommendation with tradeoffs, and (5) a prompt for the user's choice. If verified facts conflict with an earlier settled user decision, state the conflict explicitly, reopen only the affected decision(s), and let the user keep or revise their choice rather than overwriting it silently.
