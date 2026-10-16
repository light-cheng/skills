# Trigger-rate evaluation (v0.2.8)

[中文记录](README.zh-CN.md)

Checks that each changed `description` loads its Skill when it should and stays quiet when it should not: the 7 Ports whose descriptions gained the "install one or the other" note, the rewritten `eli5`, and a regression of the 15 stage-3 cases for `light-redirect`, `light-html-plan` and `light-decide`.

- Hosts: Claude Code 2.1.296 (2 runs per case) and pi 1.2.0 (1 run per case, 4 for the cases it missed). Codex is not installed on this machine, so it was not run.
- Setup: each run gets its own copy of a small tool-lending project with the whole collection installed in the project only. Claude Code ran with the user's synced mattpocock plugin turned off and pi with `--no-skills` plus the project's Skills, so only the Light versions compete.
- Signal: Claude Code calls the Skill tool for the package; pi reads the package's `SKILL.md`.
- Cases: [cases.tsv](cases.tsv). Scores: [all cases](w1-score.txt), [eli5 after the description fix](w2-eli5-score.txt). 41 Claude Code runs cut short by a usage limit were rerun and only the reruns are counted.

## Results

| Cases | Claude Code | pi |
| --- | --- | --- |
| 7 Ports, should trigger (`light-tdd`, `light-diagnosing-bugs`, `light-prototype`, `light-merge-conflicts`, `light-wizard`, `light-research`, `light-writing-for-agents`) | 14/14 | 7/7 |
| Port near-misses, should not trigger (`light-wizard` W2, `light-research` S2) | 4/4 | 2/2 |
| `eli5` should trigger (E1, E2) | 4/4 | 6/6 after the fix |
| `eli5` should not trigger: rewrite a section for non-technical readers (E3) | 2/2 | 1/4 before, 0/3 after |
| `eli5` should not trigger: plain explanation with no audience (E4) | 2/2 | 2/3 after |
| `light-redirect`, `light-html-plan` (R1–R6, H1–H5) | 22/22 | 10/11 (R5 1/4 on reruns) |
| `light-decide` should trigger in conversation (D2) and in a large implementation (D1b) | 0/4 | 2/2 |
| `light-decide` should not trigger (D3) | 2/2 | 0/4 |

## What changed because of it

`eli5`'s description now says "asks for a non-technical explanation. Not for rewriting a document for its readers." instead of "asks for a non-technical version". Claude Code was already right on E3; pi's model still reaches for `eli5` on any "simplify this" request.

## Limits

- pi reads `SKILL.md` files liberally while it decides; a read is counted as a trigger even when pi then does not follow the Skill. Its R5, D3 and E3 misses wrote no proposal or decision row. In some runs pi also browsed outside its project into the harness directory.
- `light-decide` is not chosen by Claude Code from conversation or from a large `light-implement` run (known since stage 3; recorded in the joint integration limits).
- Small samples, one fixture domain, Chinese prompts only.
