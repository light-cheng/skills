<!-- skill tree: see commits up to 8317357; prompts are in the scenario list in review/evaluator-verdict.md -->
## ask-light turn 1 (before fix)
Your instinct is right: the idea isn't ready for a spec yet, and clarifying it should come next. I can't hand you off to that step, though, because the validator returned **BLOCKED**.

```text
Mode: next
Status: BLOCKED

Observed:
- The project is set up. docs/agents/light-project.md records the goal (a CLI that turns CSV expense exports into a monthly summary), the output (Python package `expsum` with tests) and the constraint (standard library only).
- There's no spec, no tickets, no review, and no research or clarification notes.
- Nothing shows that your own decisions about the product are settled (CSV columns, how expenses are grouped, how the summary is printed, currencies, CLI flags, edge cases), and you said you weren't sure the idea was clear enough.

Assessment: The goal, output and constraint are written down, but your own product decisions aren't. That's the gap between a recorded goal and a spec.

Skill: project-clarify (logical recommendation, not cleared to start)
Scope: current-workflow
Reason: project-clarify settles your open decisions from what's already in the project and produces the handoff that project-spec needs. Running project-spec now would be premature: it expects clarified material and doesn't interview you.
Alternative: decision-map, which is for large decisions spread across several sessions. It's too heavy for a small CLI that uses only the standard library.
Source: none (validation failed)
Invocation: none

Next: revalidation-blocked
Reads: metadata=115; bodies=0; references=0
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

**Why it's blocked:** two first-party copies of `project-clarify` are installed, and nothing shows which one the host should prefer. ask-light won't pick another Skill in its place.

Two other things look off:
- The evidence packet reports the host as `codex`, but this session runs in Claude Code.
- `project-clarify` isn't in this session's list of usable skills, so it probably couldn't start here even once validation passes.

**To unblock it:** remove the duplicate `project-clarify` install, or say which copy should take precedence. Make sure the one you keep is visible to Claude Code. Then run `/ask-light` again.

## ask-light turn 1 (after fix)
The idea isn't ready for a spec yet. Run **`project-clarify`** next. The project has its basic frame, but none of the product decisions are written down.

```text
Mode: next
Status: RECOMMEND

Observed:
- Project initialized: docs/agents/light-project.md records the goal (CSV expense exports → monthly summary CLI),
  the output (Python package `expsum` with tests), the constraint (stdlib only) and the review profile (software)
- No SPEC, no tickets, no review, no research or clarification artifacts
- Repo contains only the project contract; no code yet

Assessment: The frame is set. The decisions a SPEC would need are still open: which CSV
formats and columns to accept, how to group by month and category, how to handle currency
and negative or refund rows, what the output looks like (table, CSV, JSON?), the CLI
shape, and how to handle errors. You're right that it's not clear enough for a spec.

Skill: project-clarify
Scope: current-workflow
Reason: The project is initialized, but the decisions you own haven't been settled.
  project-clarify works through them using the project's real facts and returns a
  handoff that project-spec can use directly.
Alternative: project-spec. Not yet: it only works from already-clarified material and
  won't reopen open questions, so starting there now would mean guessing at those decisions.
Source: first-party: .claude/skills/project-clarify
Invocation: /project-clarify

Next: awaiting-approval
Reads: metadata=115; bodies=1; references=3
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

`project-clarify` is user-invoked, so I can't start it for you. Once you approve, type `/project-clarify`.

The skill list showed every Light Skill twice, so it looks like the collection is installed in two places. The check still confirmed one usable first-party copy of `project-clarify`, so this doesn't block anything, but you may want to remove the duplicate install.

## s2a-t2
TOOL Bash {"command": "cd <tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2a/.claude/skills/ask-light && cat references/modes-
I couldn't start `project-clarify` from here, so you'll need to launch it yourself.

The recheck still passes: the project state hasn't changed and `project-clarify` is still the right next step. But the skill can only be started by you, and it isn't in the list of skills I'm able to launch in this session. Running it by just reading its instructions myself would only imitate the skill, so I haven't done that.

To start it, type:

```
/project-clarify
```

It will go through the open product decisions with you (CSV formats and columns, how months and categories are grouped, refunds and currency, output format, the CLI shape, error handling). It ends with a handoff that `/project-spec` can work from directly.

## s2b-t1
TOOL Skill {"skill": "agent-config", "args": "Plan execution of ticket 01 in .scratch/expsum/issues/ \u2014 model tier, effort, single vs multi-agent. User has not stated difficulty."}
TOOL Bash {"command": "ls .scratch/expsum/issues/ .claude/skills/agent-config .claude/skills/agent-config/scripts .claude/skills/agent-config/references; cat .scratch/expsum/issues/01*", "description": "List ti
TOOL Bash {"command": "cd .claude/skills/agent-config; sed -n '/Script entry/,/^## [^S]/p' references/host-evidence-schema.md | head -80; echo ----; cat references/task-<redacted>.md | head -80; echo ----; pyth
TOOL Bash {"command": "cd <tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b; ls -a; ls docs/agents 2>/dev/null; ls ~/.agent-c
TOOL Bash {"command": "cat docs/agents/light-project.md; ls .scratch/expsum; ls tests expsum 2>&1", "description": "Read project decision config and check repo layout"}
I couldn't produce a ready execution config. agent-config needs a confirmed Profile and Host evidence, and this session has neither: the companion and the Profile are both missing, so the script returns `NEED_INPUT` in plan-only mode. Its rules don't let me pick a model tier or effort without them, so I didn't guess one.

My read of ticket 01 on its own, without a profile:

- **Shape: single-pass.** It's one bounded job: write `expsum/__main__.py` to read a CSV and print totals per category per month, plus `tests/test_sum.py`. It's standard library only and has no blockers. Neither `expsum/` nor `tests/` exists yet, so this starts from scratch.
- **Difficulty: routine to moderate.** The work is mechanical, can be undone easily and is simple to test. The main open questions are the CSV columns, date format and output format, which `.scratch/expsum/spec.md` should answer.
- **Topology: one agent in the main session.** Splitting it across several agents or tickets wouldn't help.
- **Tier and effort: not decided.** You said nothing about difficulty, and the project file (`docs/agents/light-project.md`) has no `Decision data:` line, so the optional automatic difficulty check isn't allowed. With a profile, this ticket would go to your `routine` tier, or `standard` if the spec turns out to be unclear, at low to medium effort.

To get a ready config:
1. Run `agent-config setup` to confirm your models and tiers, then run this again; or
2. Tell me which model and effort to use for this session only, and I'll fill in the plan without saving it.

After that, the next step would be `light-implement` on ticket 01. I won't start it without your approval.

## light-decide with available, uncalibrated OpenDecider (MCP)
TOOL Skill {"skill": "light-decide", "args": "question id ask-light/next-action; feature expsum; options: project-clarify, decision-map"}
TOOL Bash {"command": "cd <tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2a; cat .claude/skills/light-decide/references/selec
TOOL ToolSearch {"query": "select:mcp__opendecider__status,mcp__opendecider__choose", "max_results": 2}
TOOL Bash {"command": "cat ~/.config/light/decision-policy.json 2>&1; ls -a <tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2a
TOOL mcp__opendecider__status {}
TOOL mcp__opendecider__choose {"state": {"project_goal": "A small CLI that converts CSV expense exports into a monthly summary.", "outputs": "Python package expsum with tests", "constraints": "standard library only", "feature_work
TOOL Bash {"command": "cd <tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2a/.scratch/expsum; t=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TOOL Bash {"command": "date -u +%Y-%m-%dT%H:%M:%SZ", "description": "Get current UTC time"}
TOOL Write {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2a/.scratch/expsum/decisions.md", "content": "| time 
The next action is **project-clarify**. I haven't started either skill.

- **Decider's pick:** the `opendecider` tool chose project-clarify with 0.84 confidence. It runs on this machine (`localhost:8001`), which is within the project's limit that decision data stays on-device.
- **Why I made the final call:** no thresholds have been set for `ask-light/next-action` (`~/.config/light/decision-policy.json` doesn't exist), so the tool's answer was recorded but not applied. My own judgment also picked project-clarify, because nothing has been written for `expsum` yet: there are no clarification notes, spec, tickets or earlier decisions.
- **Log:** I added one row to `.scratch/expsum/decisions.md`, which I created with its header because it didn't exist yet.

```yaml
question_id: ask-light/next-action
kind: choice
options: [project-clarify, decision-map]
answer: project-clarify
probabilities: {project-clarify: 0.8439, decision-map: 0.1561}
confidence: 0.84
method: typed-decision
data: on-device
backend: opendecider
calibrated: false
applied: false
fallback_reason: uncalibrated
final: project-clarify
```
| time | question_id | question | kind | answer | confidence | method | data | backend | applied | reason | final |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-15T16:52:21Z | ask-light/next-action | Which step should the workflow take next for this project? | choice | project-clarify | 0.84 | typed-decision | on-device | opendecider | false | uncalibrated | project-clarify |
