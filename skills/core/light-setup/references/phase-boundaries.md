# Phase Boundaries and Context Hygiene

Host-neutral rules for deciding how context moves across workflow phases in Claude Code, Codex, GitHub Copilot, and any Agent Skills harness.

## Decide at boundaries, not mid-phase

A **phase** is one unit of work with an explicit completion criterion: sharpening a spec, slicing tickets, implementing one ticket, running an acceptance pass, or diagnosing a bug.

Make context transitions **at** the boundary between two phases. Mid-phase, stay in the current window or delegate bounded legwork to a subagent started with a **fresh context window** rather than compressing half-settled work.

## Primary vs secondary sources

Every transition trades context tokens against source fidelity:

- **Primary sources** live in the repository or tracker and retain exact fidelity across sessions: source files, failing and passing tests, git commits and diffs, `GLOSSARY.md`, ADRs under `docs/adr/`, `.scratch/<feature>/spec.md`, numbered ticket files, Change proposals, and Acceptance charters.
- **Secondary sources** are lossy reconstructions: compaction summaries, handoff notes, and subagent prose reports. Each summarization pass drops edge cases, rejected designs, exact failure modes, and subtle user constraints.

Two rules follow directly from this trade-off:

1. **Before primary sources exist on disk, stay unbroken.** Keep tightly coupled planning phases (`/grill-with-docs` -> `/to-spec` -> `/to-tickets`) in one context window while inside the Smart Zone so ticket boundaries reflect every nuance surfaced during interview.
2. **Once primary sources exist on disk, discard the chat.** After `/to-tickets` writes self-contained tickets or `/implement` commits a verified slice, the files and git history *are* the ground truth. Starting fresh from primary files beats carrying forward or summarizing stale dialogue.

## The ~150k Smart Zone discipline

Frontier models reason most reliably inside the **Smart Zone**: roughly the first **~150k tokens** of active context, and earlier when verbose tool outputs, stack traces, or broad file dumps accumulate. Past ~150k tokens, multi-constraint tracking, glossary discipline, and completion-criterion rigor degrade well before the hard context-window ceiling.

Keep sessions inside the Smart Zone proactively:

- Offload broad codebase reading, external docs lookups, and multi-axis diff checks to subagents started with a **fresh context window** so raw exploration logs stay out of the parent thread.
- Check context headroom before starting a new phase. If the next phase would push the window past ~150k tokens, stop at the current boundary and clear, hand off, or compact first.

## Ordered 5-way boundary decision tree

At each phase boundary, walk these five options **in order** and pick the first branch that fits:

### 1. `Continue` (keep the current context window)

- **Use when:** The next phase relies directly on live, unpersisted reasoning from the phase that just finished, **and** total context remains comfortably inside the ~150k Smart Zone (for example: `/grill-with-docs` -> `/to-spec` -> `/to-tickets`, or fixing a defect -> `/retro` on the same session).
- **Why first:** Zero serialization loss and zero transition cost. Rule out `Continue` only when prior turns are disposable noise, context approaches ~150k tokens, work crosses a directory/harness/team boundary, or the next step requires independent evaluation.

### 2. Clear context (open a clean session)

- **Use when:** Everything the next phase needs is already recorded in durable primary sources on disk or in the issue tracker, and prior conversation history adds only noise (for example: moving from `/to-tickets` into `/implement`, advancing from ticket `01` to ticket `02`, or switching to an unrelated task).
- **Host action:** Run `/clear` (Claude Code), start a new thread (Codex), or open a fresh chat session in your IDE/harness, then point the new session at the ticket or spec path.
- **Why second:** Clean primary artifacts outperform summaries of old turns and reset the full ~150k Smart Zone budget.

### 3. `handoff` (write a portable transfer note)

- **Use when:** Work must cross a boundary where bare repo files are not enough: switching agent harnesses, moving into a separate directory or branch (such as spinning out a `/prototype` detour and bringing findings back), passing work to a colleague, or pausing an unfinished mid-phase investigation.
- **Host action and Graceful fallback:** When `handoff` is installed, invoke `/handoff` or `$handoff` to write a redacted note in the OS temp directory (`$TMPDIR` or `/tmp`, `%TEMP%` on Windows) that links specs, issues, ADRs, and commits by path or URL without duplicating their contents. When `handoff` is not installed, write the same concise pointer-only transfer note manually to `$TMPDIR/handoff-<slug>.md` recording the goal, current state, primary-file links, redacted secrets, and suggested next skills.

### 4. Fresh-context `Subagent` (bounded delegation)

- **Use when:** The current session owns orchestration or synthesis, while a well-scoped child task needs isolated legwork or unbiased review: primary-source `/research`, parallel ready-frontier workers in `/implement-spec` or `agent-config` `controller-workers` runs, or independent diff/criteria checks in `/code-review` and `acceptance`.
- **Hard invariant:** Always launch every subagent with a **fresh context window**, never a fork of the current conversation. Pass explicit file paths, commit ranges, and checkable completion criteria in the prompt, and return a concise cited report to the parent. Fresh context preserves the parent's ~150k Smart Zone and prevents self-confirmation bias during review and acceptance.

### 5. Compact context (compress session history)

- **Use when:** Options 1 through 4 are ruled out: you are still inside one effort and workspace, essential context has not yet landed in durable `.scratch/` or repo files, and active tokens are approaching the ~150k Smart Zone limit.
- **Host action:** Run `/compact` (Claude Code) or your host's context-compaction command; if the host has no built-in compaction command, write settled decisions to `.scratch/` or a temp `handoff` note and open a clean session from it.
- **Why last:** Compaction converts primary dialogue into a secondary summary. Before compacting, flush settled domain terms to `GLOSSARY.md` and settled design choices to `docs/adr/` or `.scratch/<feature>/` so primary truth survives intact.

## Common workflow boundaries at a glance

| Transition | Boundary choice | Reason |
| --- | --- | --- |
| `/grill-with-docs` -> `/to-spec` -> `/to-tickets` | `Continue` (within ~150k) | Spec and ticket slicing need live interview nuance until tickets are written. |
| Planning session nearing ~150k before `/to-tickets` | Flush `GLOSSARY.md` / ADRs, then compact context | Avoids degraded reasoning while preserving settled domain terms on disk. |
| Runnable design question during planning (`/prototype`) | `handoff` out -> `/prototype` -> `handoff` back | Crosses into a separate prototype branch or directory and returns only the answer. |
| External doc or codebase investigation (`/research`) | `Subagent` with a **fresh context window** | Keeps raw reading logs out of the planning thread and returns cited findings. |
| `/to-tickets` -> `/implement` (and ticket `N` -> `N+1`) | Clear context | Each ticket is a self-contained primary source; prior implementation turns are noise. |
| Multi-ticket ready frontier (`/implement-spec`) | Orchestrator + `Subagent` workers (**fresh context window** each) | Isolates per-ticket implementation and protects integration-branch context. |
| Broken assumption during build -> `redirect` | Stay in current session, halt edits, write Change proposal | Captures exact invalidating evidence while fresh, then stops for human approval. |
| Ticket or milestone verification (`code-review`, `acceptance`) | Reviewer / Evaluator `Subagent` (**fresh context window**) | Independent eyes prevent self-assertion and fake convergence. |
| Post-build environment improvement (`/retro`) | `Continue` before clearing (or pass session log after clearing) | Needs visibility into where the build stalled or needed manual correction. |
