# v0.2.10 — Skill Calls for Every Host and Sturdier Project Flow

<!-- release-state: {"view": "notes", "version": "v0.2.10", "verification": "Verification", "install_commands": "template"} -->

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md)

This release snapshot v0.2.10 keeps the same 39 Skills. Skill calls now work on every Host, not only Codex, and the project flow no longer lets a review, a plan change or a clarification claim more than really happened. The [release manifest](RELEASE_MANIFEST.md) records the preparation-time scope and local evidence; observed CI, installation and publication facts are recorded in the release receipt on `main`.

## Changes you will notice

- **Skill calls for any Host.** Packages, descriptions and docs name Skills without the Codex `$` prefix, and the Agent writes the call in the current Host's form (`/name` in Claude Code, `$name` in Codex). Before, an Agent on Claude Code could tell the user to type `$project-tickets`, which does not work there. `manuscript-ops` handoff examples are now logical calls. Codex's own `agents/openai.yaml` and the frozen `recap` keep `$`.
- **Review evidence.** `review-loop` reports a clean result only with the reviewer's name, the rounds run and where each round's report is. `light-implement`'s report adds `Reviewer:` and `Evidence:` lines; without a reviewer report the review is `not run`, never `converged`.
- **Ticket order.** `light-implement` stops with `BLOCKED` when the ticket is already `claimed` or a ticket it depends on is not `resolved`.
- **Plan changes.** `light-redirect` searches the whole SPEC and every open ticket for passages a change would contradict. After approval it gives the exact `project-spec` or `project-tickets` call for the current Host instead of saying they are not installed, and it refreshes `plan.html`.
- **Clarification.** `clarify` and `project-clarify` list only what the user chose as decided; a default the Agent would pick stays an open question.
- **Smaller fixes.** `project-retro` has a trigger sentence and cites the record behind any "pending elsewhere" claim. `light-html-plan` runs its visual check on every refresh or says it did not. `release-workflow` reads a hidden `release-state` field block instead of fixed release wording, and its stage guide covers the final CI observation, worktrees and zsh-safe push commands.

No package is added, removed or renamed, so no migration is needed. Update a global install (for example under `~/.agents/skills`) as well as project installs: a Host may read an older global copy first.

## Installation

Select the fixed tag for a reproducible install:

```bash
npx skills add light-cheng/skills#v0.2.10
npx skills add light-cheng/skills#v0.2.10 --skill light-implement
```

## Verification

Local evidence at preparation, including the stage 7 rehearsal and its retest on Codex and pi, is listed in the [release manifest](RELEASE_MANIFEST.md). Pull-request CI, the tag, fresh installation and publication are observed after preparation and recorded in the release receipt on `main`. The full [changelog](https://github.com/light-cheng/skills/blob/main/CHANGELOG.md) lists every change.
