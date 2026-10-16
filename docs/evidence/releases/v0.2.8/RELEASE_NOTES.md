# v0.2.8 — Plan Changes, Decisions and Plan Pages

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md)

This release snapshot v0.2.8 grows the collection from 36 to 39 Skills and tightens how the project workflow hands work between stages. The [release manifest](RELEASE_MANIFEST.md) records the preparation-time scope and local evidence; observed CI, installation and publication facts are recorded in the release receipt on `main`.

## New Skills

- `light-decide` (thinking): answers a bounded judgment inside a workflow — pick one of several legal options, yes or no, or a level — through an allowed decision source or the Agent's own judgment, and logs it to `.scratch/<feature>/decisions.md`. It never decides approvals, verdicts or permissions.
- `light-redirect` (project): when the approved plan no longer holds, writes a change proposal to `.scratch/<feature>/changes/` that only the user approves; `project-spec` and `project-tickets` apply it.
- `light-html-plan` (project): shows where a plan stands as one offline HTML page at `.scratch/<feature>/plan.html`, with a built-in visual system.

All three are optional: callers keep their old behaviour when they are missing.

## Changes you will notice

- **Decision sources without Jev.** `ask-light` and `agent-config` no longer call TypeSafe Jev. A project without a `Decision data:` line only uses a model on this machine. Thresholds move to `~/.config/light/decision-policy.json`. `project-init` no longer sets up Jev.
- **Project flow records.** The ticket lifecycle is explicit: `light-implement` claims a ticket and appends an implementation report (with `Plan gap:`); `project-review` resolves it after `PASS` and records `Cause:` on a `FAIL`. A SPEC now carries an `Approval:` line, the ticket-graph approval is recorded in the SPEC, and a clarification handoff can be saved at `.scratch/<feature>/clarify-handoff.md` for a later session.
- **light-travelpage AI.** The optional assistant connects to any OpenAI- or Anthropic-format API. The page owner runs `scripts/ai-setup.mjs` at deployment to detect the format, pick the model and check one real tool call; travelers cannot change the model. The CPA-specific setup is removed; pages generated before v0.2.8 keep working with their `OPENAI_*` settings.
- **Rename.** `resolving-merge-conflicts` becomes `light-merge-conflicts` so it no longer shares a name with the mattpocock/skills original. The seven Ports whose names follow mattpocock/skills now say "install one or the other, not both" in their descriptions.
- **eli5** is rewritten from scratch as the owner's own Skill.

## Upgrade notes

Read the [v0.2.8 migration guide](https://github.com/light-cheng/skills/blob/main/docs/MIGRATION-v0.2.8.md) before upgrading: update `resolving-merge-conflicts` references, add `Decision data: third-party` if a project relied on the hosted Jev service, and rerun `project-init` to add the new tracker lines.

## Installation

Installation from the actual v0.2.8 source passed in fresh environments. Select the fixed tag for a reproducible install:

```bash
npx skills add light-cheng/skills#v0.2.8
npx skills add light-cheng/skills#v0.2.8 --skill light-decide
```

## Verification

Local evidence at preparation is listed in the [release manifest](RELEASE_MANIFEST.md). Exact-candidate CI and the protected annotated tag are verified. On a fresh hosted Linux user, pinned and default whole installs for Codex and Claude Code projects, native Codex global scope and three single Skills each matched their source bytes (39 packages, 406 files). Local Claude Code and pi installs matched too, and both Hosts discovered the new Skills from a fresh project; pi needs project trust for that. Codex is not installed on the maintainer's machine. The post-release receipt on main has the details. The full [changelog](https://github.com/light-cheng/skills/blob/main/CHANGELOG.md) lists every change.
