# Producer Evidence - Round 1

This is Producer evidence, not final acceptance.

## Scope
- Charter revision: 1
- Profile: agent-skill
- In-scope work: candidate package `.scratch/light-decide/candidate/light-decide/` at manifest `candidate-manifest.txt`
- Out-of-scope check: no caller Skill, script, catalog or README was changed for this package

## Evidence

### E-001 - Package tests
- Evidence label: structural
- Run or observation: `uv run --no-project --python 3.11 python -m unittest discover -s .scratch/light-decide/candidate/light-decide/tests -p 'test_*.py'`
- Expected: all tests pass; tests include a negative control that fails on a drifted log row and an unparseable policy
- Observed: `Ran 6 tests ... OK`
- Outcome: PASS
- Validates: AC-5, AC-6, AC-7 (format consistency), AC-9
- Environment and limitations: Python 3.11; tests read only package files. They check format consistency, not agent behavior.
- Artifact: console output

### E-002 - Clean copy runs its own tests
- Evidence label: installation
- Run or observation: copy the package into a fresh temp dir and run the same unittest discovery there
- Expected: passes without repository files
- Observed: `OK`
- Outcome: PASS
- Validates: AC-9
- Environment and limitations: proves self-containment of tests only
- Artifact: console output

### E-003 - No URL, key or local model name
- Evidence label: structural
- Run or observation: `grep -rnE "https?://|localhost|127\.0\.0\.1|api[_-]?key|mlx" <package>`
- Expected: no match
- Observed: no match. The examples name the backend `opendecider` (an MCP server name, used as the "name the Host reports").
- Outcome: PASS
- Validates: AC-4
- Environment and limitations: pattern search
- Artifact: console output

### E-004 - Fresh install and discovery in Claude Code
- Evidence label: installation
- Run or observation: package copied to `<tmp>/<case>/.claude/skills/light-decide/` in six fresh projects; `claude -p ... --output-format stream-json` (Claude Code 2.1.296). Runner: `runs/run.sh`.
- Expected: the Host lists `light-decide` in every session
- Observed: the `init` event lists `light-decide` in all six sessions (`runs/*.jsonl`)
- Outcome: PASS
- Validates: AC-9
- Environment and limitations: one Host (Claude Code) on macOS; other Hosts not observed
- Artifact: `runs/*.jsonl`

### E-005 - Positive trigger (VS-1 prompt, skill not named)
- Evidence label: invocation
- Run or observation: `runs/vs1.jsonl`. Prompt describes a bounded yes/no judgment before implementing a ticket; it does not name the skill.
- Expected: the agent invokes `light-decide` on its own
- Observed: first tool call is `Skill(light-decide)`
- Outcome: PASS
- Validates: AC-9 (invocation), AC-1
- Environment and limitations: one prompt; phrasing included "bounded judgment" and a question id, as a caller pointer line would
- Artifact: `runs/vs1.jsonl`

### E-006 - Non-trigger
- Evidence label: invocation
- Run or observation: `runs/nontrig.jsonl`, prompt "Summarize README.md in one sentence."
- Expected: no `light-decide` invocation
- Observed: only `Read(README.md)`; no Skill call
- Outcome: PASS
- Validates: AC-9 (invocation)
- Environment and limitations: one prompt
- Artifact: `runs/nontrig.jsonl`

### E-007 - VS-1 success, default limit, uncalibrated local source
- Evidence label: behavioral
- Run or observation: `runs/vs1.jsonl`, `runs/vs1-decisions.md`
- Expected: no `Decision data:` line → on-device; local decision MCP verified with a status call; one source asked; no policy → uncalibrated; own judgment final; one row logged
- Observed: `mcp__opendecider__status` then one `yes_no` call; result `method: typed-decision`, `data: on-device`, `calibrated: false`, `applied: false`, `fallback_reason: uncalibrated`, `final: no`; one row in `decisions.md`. The policy file read was blocked by the Host sandbox; the agent treated it as unreadable → uncalibrated, as `formats.md` says.
- Outcome: PASS
- Validates: AC-2, AC-3, AC-5, AC-6, AC-7
- Environment and limitations: the row's `time` is `2026-10-10T12:00:00Z`, which the agent itself called approximate; it did not read the clock (see observation O-1)
- Artifact: `runs/vs1.jsonl`, `runs/vs1-decisions.md`

### E-008 - VS-2 `off` holds against an explicit user request
- Evidence label: behavioral
- Run or observation: `runs/vs2.jsonl`; project has `- Decision data: off`; prompt asks to use the opendecider MCP
- Expected: no decision tool call; self-judgment with reason `off`
- Observed: no `mcp__opendecider__*` call; row `self-judgment | in-session | agent | true | off`; reply explains how to change the line
- Outcome: PASS
- Validates: AC-2, AC-3
- Environment and limitations: one run
- Artifact: `runs/vs2.jsonl`, `runs/vs2-decisions.md`

### E-009 - VS-3 verdict request declined
- Evidence label: behavioral
- Run or observation: `runs/vs3.jsonl`; prompt asks light-decide to decide PASS/FAIL and resolve the ticket
- Expected: declines, asks no source, changes no ticket
- Observed: no decision call, no `decisions.md`, ticket still `**Status:** open`; reply hands the verdict back to the user or evidence
- Outcome: PASS
- Validates: AC-1, AC-8
- Environment and limitations: one run
- Artifact: `runs/vs3.jsonl`

### E-010 - VS-4 no source available
- Evidence label: behavioral
- Run or observation: `runs/vs4.jsonl`, run with `--strict-mcp-config --mcp-config '{"mcpServers":{}}'`
- Expected: self-judgment, reason `unavailable`, no BLOCKED, no install request
- Observed: row `self-judgment | in-session | agent | true | unavailable`; no BLOCKED or install request in the reply
- Outcome: PASS
- Validates: AC-3, AC-8
- Environment and limitations: the local decision endpoint was still running but unreachable with the allowed tools, so "unavailable" means "no evidence in this run"
- Artifact: `runs/vs4.jsonl`, `runs/vs4-decisions.md`

### E-011 - VS-5 one legal option
- Evidence label: behavioral
- Run or observation: `runs/vs5.jsonl`; only `light-implement` is legal
- Expected: returned without asking a source
- Observed: no decision tool call; result `self-judgment`, `fallback_reason: none`, `final: light-implement`; did not start light-implement
- Outcome: PASS
- Validates: AC-1, AC-8
- Environment and limitations: one run
- Artifact: `runs/vs5.jsonl`, `runs/vs5-decisions.md`

### E-012 - Executable axis
- Evidence label: structural
- Run or observation: package tree inspection
- Expected: no scripts
- Observed: only Markdown, YAML and a unittest file that reads package files; axis 6 not applicable
- Outcome: PASS
- Validates: AC-9
- Artifact: `candidate-manifest.txt`

## Producer observations (candidates for the Core)
- O-1: In VS-1 the agent wrote an approximate `time` instead of reading the clock. `formats.md` says "UTC in ISO 8601" but not where the value comes from. VS-2, VS-4 and VS-5 ran `date -u`.
- O-2: Every run first tried a heredoc to append the row; the Host rejected it and the agent fell back to Write. Host-specific friction, not a package defect.
