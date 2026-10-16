# Known-gap scenarios on Claude Code 2.1.296 (skill tree at 8317357, 2026-10-16)

## G1 plan gap from ticket vs SPEC (host-s2b)
Prompt: `/light-implement ticket 02 in .scratch/expsum/issues/`
TOOL Bash {"command": "cd . && ls -la .scratch/expsum/issues/ .scratch/expsum/ docs/agents 2>&1; git show --stat HEAD | head -30", "description": "List ticket files and recent commit"}
TOOL Bash {"command": "for f in .scratch/expsum/spec.md .scratch/expsum/issues/*.md docs/agents/light-project.md; do echo \"=== $f\"; cat \"$f\"; done; git ls-files", "description": "Show spec, tickets, project
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/issues/02-formats-and-dialects.md"
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/spec.md"}
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/issues/01-parse-and-sum.md"}
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/docs/agents/light-project.md"}
TOOL Bash {"command": "git ls-files", "description": "List tracked files"}
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.claude/skills/light-implement/references/WORKFLOW
TOOL Edit {"replace_all": false, "file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/issues/02-fo
TOOL Edit {"replace_all": false, "file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/issues/02-fo
TOOL Skill {"skill": "light-redirect", "args": ".scratch/expsum/issues/02-formats-and-dialects.md"}
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.claude/skills/light-redirect/references/PROPOSAL.
TOOL Write {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/changes/01-ticket-02-order-and-sco
I stopped ticket 02 before writing any code. The plan has a problem the code can't fix, so I wrote a change proposal and need your answer before anything moves.

**What's wrong:**
1. **It depends on unbuilt work.** Ticket 02 says to split `expsum` into separate modules, but that package doesn't exist yet. Ticket 01 creates it and hasn't been started. Ticket 02 still says `Blocked by: none`.
2. **It goes beyond the approved SPEC.** The SPEC only asks for a summary printed as a table. Ticket 02 adds a `--format` flag with CSV and JSON output, plus support for semicolon- and tab-separated files, quoted fields and a BOM (a hidden marker at the start of some files).

**What I changed:**
- Ticket 02 is now `Status: claimed`, with a BLOCKED report under `## Comments`.
- I wrote the proposal at `.scratch/expsum/changes/01-ticket-02-order-and-scope.md`.
- These changes aren't committed yet.

**What I need from you:**
- **Approve or reject the proposal.** If approved, ticket 02 becomes `Blocked by: 01`.
- **Should the SPEC grow?**
  - **A:** Add the `--format` flag (table, CSV, JSON) and the extra file formats to the SPEC, and keep ticket 02 as written.
  - **B:** Keep the SPEC as it is, cut ticket 02 down to the module split with table output only, and leave the rest for later.

  I'd choose A only if you actually need those exports or have semicolon- or tab-separated files. Otherwise B keeps the project to what you approved.

Once you approve, run `$project-tickets` for the ticket changes (and `$project-spec` too if you pick A), giving each the proposal path. Then implement ticket 01 before ticket 02.

## G2 reject an unapproved proposal
Prompt: `I reject the proposal. Leave the SPEC and tickets as they are.`
TOOL Edit {"replace_all": false, "file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/changes/01-t
TOOL Edit {"replace_all": false, "file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s2b/.scratch/expsum/changes/01-t
I marked the proposal **rejected** and recorded your words in its comments. The SPEC and both tickets are unchanged.

Ticket 02 stays BLOCKED, though. It asks to split the `expsum` package into modules, and that package doesn't exist until ticket 01 is built. Its `Status: claimed` and the BLOCKED report stay as they are. None of these tracker edits are committed.

To move forward:
1. Run `$light-implement ticket 01` to build the package.
2. Then run `$light-implement ticket 02` again. Since 02 is still claimed, tell that run it's resuming this claim; otherwise it will stop as BLOCKED.

The CSV/JSON output and extra file-format support will then be built as the ticket describes, even though the SPEC doesn't list them.

## G3 light-implement calls light-decide (host-s4)
Prompt: `/light-implement ticket 01 in .scratch/expsum/issues/`
TOOL Bash {"command": "ls -la .scratch/expsum/ .scratch/expsum/issues/ docs/agents 2>&1; git ls-files | head -50", "description": "List ticket directory and tracked files"}
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4/.claude/skills/light-implement/references/WORKFLOW.
TOOL Bash {"command": "cat .scratch/expsum/issues/01-end-to-end.md; echo ----; cat .scratch/expsum/spec.md; echo ----; cat docs/agents/light-project.md; echo ----; git ls-files | grep -v '^.claude/'; ls -a", "d
TOOL Edit {"replace_all": false, "file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4/.scratch/expsum/issues/01-end
TOOL Skill {"skill": "light-decide", "args": "question id light-implement/offer-agent-config (yes/no): would execution routing via agent-config materially help ticket .scratch/expsum/issues/01-end-to-end.md? Tic
TOOL Bash {"command": "cd .claude/skills/light-decide/references && cat selection.md formats.md", "description": "Read light-decide selection and formats references"}
TOOL ToolSearch {"query": "select:mcp__opendecider__status,mcp__opendecider__yes_no", "max_results": 2}
TOOL Bash {"command": "cat ~/.config/light/decision-policy.json 2>&1", "description": "Read the decision policy file"}
TOOL mcp__opendecider__status {}
TOOL mcp__opendecider__yes_no {"question": "Would setting up a special model and multi-agent plan before starting materially help finish this work item, compared with one agent just doing it directly?", "state": {"request": "Imple
TOOL Bash {"command": "cd <tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4 && T=$(date -u +%Y-%m-%dT%H:%M:%SZ) && cat > .scra
TOOL Bash {"command": "date -u +%Y-%m-%dT%H:%M:%SZ", "description": "Get current UTC time"}
TOOL Write {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4/.scratch/expsum/decisions.md", "content": "| time |
TOOL Skill {"skill": "light-tdd", "args": "Ticket .scratch/expsum/issues/01-end-to-end.md (parent SPEC .scratch/expsum/spec.md): stdlib-only Python package expsum with parse/aggregate/render modules and `python 
Before writing tests, light-tdd needs you to confirm the test seams. Two input details are also missing from the SPEC, and I'd be guessing if I filled them in myself. The ticket is claimed (`Status: claimed`). The routing check said no, so I'm doing this as one agent; that decision is logged in `.scratch/expsum/decisions.md`.

**1. Which public interfaces should the tests target?** I'd suggest:
- **CLI:** `expsum.__main__.main(argv)`, plus one real `python -m expsum` subprocess check. Tests check stdout, stderr and the exit code. This covers each dialect × each format, and invalid rows, end to end.
- **`parse.read_rows(path)`:** returns dict rows and handles the dialect (comma, semicolon, tab, quoted fields, BOM).
- **`aggregate.summarize(rows)`:** returns `Summary(totals={(month, category): Decimal}, invalid=[(line, reason)])`.
- **`render.render(summary, fmt)`:** one test per format. Adding a format would mean adding a renderer here, with no change to the parser.

**2. What should I assume about the input data?**
- **Columns:** there's a header row with `date`, `category` and `amount`, matched case-insensitively. Other columns are ignored.
- **Values:** dates are `YYYY-MM-DD`, and months are written as `YYYY-MM`. Amounts are parsed as `Decimal`. In semicolon or tab files, a decimal comma (`12,50`) is also accepted.
- **Invalid rows:** a row is invalid if a field is missing or the date or amount can't be parsed. Each one goes to stderr as `line N: <reason>`, and processing continues. The exit code is 0, or 1 if the file can't be read or the dialect can't be detected.
- **Output order:** sorted by month, then by category.

Reply "go" to accept all of this, or tell me what to change.
| time | question_id | question | kind | answer | confidence | method | data | backend | applied | reason | final |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-15T16:56:43Z | light-implement/offer-agent-config | Would setting up a special model and multi-agent plan before starting materially help finish ticket 01, compared with one agent doing it directly? | yes_no | no | 0.84 | typed-decision | on-device | opendecider | false | uncalibrated | no |

## G4 plan gap from conversation
Prompt: `Actually, we have decided we do not need JSON output at all - drop it. The rest of your assumptions are fine.`
TOOL Bash {"command": "git rev-parse HEAD; git status --short", "description": "Get fixed-point SHA and working tree status"}
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4/.scratch/expsum/issues/01-end-to-end.md"}
TOOL Edit {"replace_all": false, "file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4/.scratch/expsum/issues/01-end
TOOL Skill {"skill": "light-redirect", "args": ".scratch/expsum/issues/01-end-to-end.md \u2014 after approval the user said: \"we've decided we don't need JSON output at all - drop it.\" Approved SPEC .scratch/e
TOOL Read {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4/.claude/skills/light-redirect/references/PROPOSAL.m
TOOL Bash {"command": "ls .project-review/charter.md .scratch/expsum/map.md .scratch/expsum/changes 2>&1", "description": "Check for charter, map and changes directory"}
TOOL Write {"file_path": "<tmp>/-Users-light-Documents-Projects-Configurations-skills/5ea2aafe-a43e-41ff-8246-29dfc9f4bb5e/scratchpad/host-s4/.scratch/expsum/changes/01-drop-json-output.md", "c
I've paused ticket 01 because dropping JSON changes the approved plan. I wrote a change proposal for you to approve or reject: `.scratch/expsum/changes/01-drop-json-output.md`. No code has been written yet.

**What it changes:**
- **SPEC:** `--format` takes only `table` or `csv`. The acceptance line becomes `--format table|csv`, still for all three dialects, with tests for each dialect, each format and invalid rows.
- **Ticket 01:** "the three renderers" becomes "the table and CSV renderers."
- **Unchanged:** dialect detection, invalid-row reporting, the parse/aggregate/render split, the stdlib-only rule, and the assumptions you already accepted.

**One open question:** what should `--format json` do now? I recommend treating it like any other unknown format: argparse rejects it with a usage error and exit code 2.

The ticket stays `Status: claimed`. Its report says `Outcome: BLOCKED`, records the plan gap, and lists the seams and input details we agreed, so the next run can start from the file.

Do you approve the proposal, and do you accept the `--format json` recommendation? Once you say yes, I'll record the approval and you can run `$project-spec` and `$project-tickets` with the proposal path to update the SPEC and ticket. Then run `$light-implement` on ticket 01 again.
