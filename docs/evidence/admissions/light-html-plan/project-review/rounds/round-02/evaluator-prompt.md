You are a fresh, independent Evaluator for a project-review of a candidate Skill package. Stay strictly read-only: do not create, modify or delete any file. You may read files and run read-only commands (cat, ls, grep, shasum, `python3 -I -B` for parsing and for the package tests: `cd <package> && PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`).

Repository root: <repo> (read AGENTS.md, docs/REVIEW_POLICY.md, skills/review/project-review/references/WORKFLOW.md for how verdicts work).

## Target
Package `light-html-plan` at .scratch/light-html-plan/candidate/light-html-plan/. Confirm identity: `cd .scratch/light-html-plan/candidate && shasum -a 256 -c ../review/.project-review/rounds/round-02/candidate-manifest-repair1.txt`. Also in scope: `GIT_OPTIONAL_LOCKS=0 git diff -- docs/agents/issue-tracker.md`.

## Baseline
- Charter revision 2: .scratch/light-html-plan/review/.project-review/charter.md (AC-1..AC-10, scenarios, exclusions). Judge against it.
- User decisions: same folder, changes.md (CP-001 confirmed, CP-002 built-in visual system approved). Approved prototype: .scratch/light-html-plan/ui-proto/plan.html.
- Design source: .scratch/decision-provider/design-stage3.md §4 and §7 (Q8, Q8 附).
- Findings and dispositions: .scratch/light-html-plan/review/.project-review/findings.md (round 1 and round 2).

## Evidence
- .scratch/light-html-plan/review/.project-review/rounds/round-02/producer-evidence.md. Evidence on the current text is the "Repair1" section plus round-2 runs whose exercised text did not change (the Producer lists them; judge whether that claim holds by diffing round-02/candidate-manifest.txt against candidate-manifest-repair1.txt and reading the changed files).
- runs/, runs-repair1/: prompts, transcripts (Claude Code stream-json vs*, pi json pi*, Codex JSONL cx*), exit codes, generator gen.py, checker pagecheck.py. pages/ and pages-repair1/: generated plan.html, plan-history copies, source-baseline.txt (SHA-256 of every source before the run).
- Spot-check yourself: skill invoked (or not, for vs5 and cx5) and never named in prompts; history copies hash to the plan.html in the refresh baselines; page contents for AC-1..AC-6 and AC-10 (read the HTML as text, run pagecheck.py with python3 -I -B). You cannot open a browser; rendering claims are Producer observations — say so if you rely on them.

## Output
Write nothing to disk. Return: per-AC assessment (met / not met / not evidenced, with what you checked), any new finding (E-004.., severity, location, problem, evidence), and a recommended verdict PASS / FAIL / BLOCKED for the Charter scope. The user's own reading of the look was already given (CP-002) and is not yours to re-judge. State limitations.
