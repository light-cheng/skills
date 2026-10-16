# Light Skills v0.2.8 migration

[简体中文](MIGRATION-v0.2.8.zh-CN.md)

**Status:** v0.2.8 is published. Exact-candidate CI, the protected tag and fresh installs from the released source passed; see the [release receipt](evidence/releases/v0.2.8/RELEASE_RECEIPT.md).

## Renamed package

| Previous Light name | New name | Category | Invocation |
| --- | --- | --- | --- |
| `resolving-merge-conflicts` | `light-merge-conflicts` | engineering | model-invoked |

The old name was the same as the mattpocock/skills original, so installing both collections let one package replace the other. Behaviour, responsibilities and invocation are unchanged. There is no installable alias or wrapper for the old name. The installed path becomes `<skills-root>/light-merge-conflicts/`; the source path is `skills/engineering/light-merge-conflicts/`.

## Decision sources no longer call Jev

`ask-light` and `agent-config` no longer call TypeSafe Jev. A project that has no `Decision data:` line in `docs/agents/light-project.md` gets on-device judgments only. To use a typed decision source, set `Decision data:` and configure the source through `light-decide` (see its `references/setup.md`).

## SPEC approval line

A SPEC now records its approval in an `Approval:` line under the title, and `project-tickets` adds a `Tickets approved` line under the SPEC's `## Comments`. A SPEC written before 0.2.8 has no `Approval:` line: `project-tickets` asks whether it is approved and adds the line on yes. A SPEC that says `Approval: pending` goes back to `project-spec` for approval. A handoff saved at `.scratch/<feature>/clarify-handoff.md` marks a new feature for `ask-light`. When another feature folder still holds an active SPEC, `ask-light` keeps routing to that one: set `Current effort:` in `docs/agents/light-project.md`, or mark the finished SPEC superseded. Rerun `project-init` to add the new tracker lines (`clarify-handoff.md`, approvals) to an existing project.

## light-travelpage AI connection

The optional AI assistant now connects to any service that speaks the OpenAI or the Anthropic API format, and the CPA-specific setup is gone. Existing pages keep working without changes: `ai-config.json` with `provider: openai` reads as `on`, and the server still reads `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` and `OPENAI_API_STYLE`. A generated page carries its own runtime, so a page made before v0.2.8 keeps reading only `OPENAI_*`; do not run the new setup on it (the script refuses). To use the new settings or Anthropic for that trip, generate a new project with `create.mjs --ai on`, apply the existing trip with `update.mjs`, deploy it to the same Pages project and D1 database, and have the owner run `node <skill>/scripts/ai-setup.mjs <project> --base-url <url>` in their own terminal: it detects the format, lets the owner pick the model, checks one real tool call and writes `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL` and `AI_API_FORMAT`. New pages use `--ai on` instead of `--ai openai` (the old spelling still works). A gateway on the owner's computer or behind a Tunnel belongs to the separate optional `light-travelpage-gw` package.

## Before upgrading

Record the target Host and its Skill root. For an installed `resolving-merge-conflicts`, check where it came from before touching it: open its `SKILL.md` and `ATTRIBUTION.md`, or the symlink target. A Light copy names `light-cheng/skills` or its old name `LightDevCoder/skills`; Matt's original does not. Leave a package from another source in place.

Search project prompts, `AGENTS.md`, availability declarations, scripts, automations and installer `--skill` arguments for `resolving-merge-conflicts` when it refers to the Light package.

## Upgrade steps

1. Install the fixed tag into the Host scope you use.
2. Remove the old Light `resolving-merge-conflicts` directory only after confirming it is the Light copy and saving its contents or link target.
3. Change Light references from `resolving-merge-conflicts` to `light-merge-conflicts`, for example `$resolving-merge-conflicts` becomes `$light-merge-conflicts`.
4. Refresh discovery and check that the Host lists `light-merge-conflicts` from the Light source.

```bash
npx skills add light-cheng/skills#v0.2.8
npx skills add light-cheng/skills#v0.2.8 --skill light-merge-conflicts
```

## Recovery

If the upgrade fails, stop using the new entry, restore the saved copy or link target, and reinstall `#v0.2.7` if needed. Before restoring the old directory, confirm it will not replace Matt's package of the same name.
