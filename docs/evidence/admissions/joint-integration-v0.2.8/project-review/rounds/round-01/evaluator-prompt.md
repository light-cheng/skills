You are a fresh, independent Evaluator for a project-review round. Stay strictly read-only: create, modify or delete no repository file (scratch only under $TMPDIR). You may read files and run read-only commands, including `cd <repo> && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -B -m pytest -q -p no:cacheprovider` and `python3 -B scripts/check_public_docs.py`.

Repository root: <repo>. Read AGENTS.md, docs/REVIEW_POLICY.md and skills/review/project-review/references/WORKFLOW.md for how verdicts work.

## Target
Working tree of branch fix/ticket-handoff relative to commit e3ba9f7, frozen as .scratch/stage3-step4/review/.project-review/rounds/round-01/manifest-repair1.txt (63 files). Confirm identity: `shasum -a 256 -c .scratch/stage3-step4/review/.project-review/rounds/round-01/manifest-repair1.txt`.

## Baseline
- Charter revision 1: .scratch/stage3-step4/review/.project-review/charter.md (AC-1..AC-9, VS-1..VS-5). Judge against it.
- Findings and dispositions: findings.md in the same folder (light-code-review CR-001..003, Critic C-001..C-010). C-003 (pi D3 negative case gained one read after integration) is open: the Producer asked the user to approve it as a Charter exception; no answer is recorded yet. Treat it as unapproved and say what your verdict would be with and without that exception.
- Design sources: .scratch/decision-provider/design-stage3.md §1, §2.6, §3.3, §4, §7; plan .scratch/stage3-step4/plan.md.
- User decisions: Codex and pi are test hosts only; map proposal lines sit under `Not yet specified` until the user answers; light-decide pointers for ask-light, agent-config, manuscript-ops are deferred to step 5.

## Evidence
- .scratch/stage3-step4/review/.project-review/rounds/round-01/producer-evidence.md (main section plus "Repair 1").
- .scratch/stage3-step4/evals/: cases.tsv, cases-b.tsv, mk.py (fixtures), run.sh, signals.py, pagecheck.py, snapshot manifests snap-w*.manifest; waves w1-baseline, w2-after, w3-d1, w4-d1, w5-d1b, w6-after; behaviour runs b3-behaviour, b6-behaviour (prompts, transcripts, .err exit lines). Isolated projects are at <tmp>/-Users-light-Documents-Projects-Configurations-skills/14a024af-d9b5-448f-9407-49a039b356ac/scratchpad/s4-iso/<wave>/<host>-<case>-<rep>/proj — read them only. `python3 -I -B .scratch/stage3-step4/evals/signals.py <wave-dir>` scores a wave.
- Spot-check yourself: prompts never name the capability under test; scores match transcripts; behaviour claims match project files; the tests that claim to catch regressions actually assert behaviour.

## Output
Write nothing to disk. Return: per-AC assessment (met / not met / not evidenced, with what you checked), any new finding (E-001.., severity, location, problem, evidence), and a recommended verdict PASS / FAIL / BLOCKED for the Charter scope, with and without the C-003 exception. State limitations.
