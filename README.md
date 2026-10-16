![Light Skills — composable agent workflows](Assets/header.png)

[中文说明](README.zh-CN.md)

# Light Skills — Composable Agent Workflows

`light-cheng/skills` provides 39 first-party Agent Skills designed to work together across project planning, coding, and review, or run individually on demand. Each package lives in `skills/<category>/<name>/` and defines its own behavior in `SKILL.md`.

> **Release:** [v0.2.9](https://github.com/light-cheng/skills/releases/tag/v0.2.9) is the current stable release of all 39 first-party Skills. It moves every live link and install command to `light-cheng/skills` after the GitHub account rename and improves `release-workflow`. Its immutable [release manifest](docs/evidence/releases/v0.2.9/RELEASE_MANIFEST.md) and post-publication [release receipt](docs/evidence/releases/v0.2.9/RELEASE_RECEIPT.md) record the scope and verification. See the [v0.2.9 release notes](docs/evidence/releases/v0.2.9/RELEASE_NOTES.md) and [v0.2.9 migration guide](docs/MIGRATION-v0.2.9.md).

> **Name migration:** v0.2.8 renames `resolving-merge-conflicts` to `light-merge-conflicts`. In [v0.2.7](https://github.com/light-cheng/skills/releases/tag/v0.2.7), twelve Skills took `light-` names; see the [v0.2.7 migration guide](docs/MIGRATION-v0.2.7.md).

## Browse by category

[All categories and collection guides](skills/README.md). The 39 source packages are grouped by purpose; invocation modes are unchanged; candidate names follow the migration guide.

- [project](skills/project/README.md) — 10 skills
- [engineering](skills/engineering/README.md) — 5 skills
- [review](skills/review/README.md) — 4 skills
- [thinking](skills/thinking/README.md) — 6 skills
- [knowledge](skills/knowledge/README.md) — 5 skills
- [writing](skills/writing/README.md) — 3 skills
- [productivity](skills/productivity/README.md) — 6 skills

[Path migration guide](docs/CATEGORY_MIGRATION.md)

## Overview

The repository organizes capabilities into focused areas:

- **Project Workflow:** end-to-end delivery from project bootstrap to release.
- **Clarification & Research:** structured questions and primary-source investigation before building.
- **Execution:** bounded implementation tasks with profile-driven execution configuration.
- **Review:** read-only specialist checks and final project acceptance.
- **Specialized Workflows:** dedicated tooling for manuscripts, knowledge bases, language learning, and kanban boards.
- **Router:** `ask-light` inspects workspace state to suggest next steps.

Skills follow the progressive disclosure patterns of Matt Pocock Skills and the host-evidence inspection approach of Sol Advisor as design references without adding runtime dependencies.

## Installation

### Current main / latest

Install the latest collection from the default branch `main`:

```bash
npx skills add light-cheng/skills
```

Install a single Skill from `main` (for example, the updated `agent-config` Skill):

```bash
npx skills add light-cheng/skills --skill agent-config
npx skills add light-cheng/skills --skill project-review
npx skills add light-cheng/skills --skill light-research
```

> **Note:** An unqualified repository source (`light-cheng/skills`) follows the default branch `main`, delivering the latest admitted features and integrations.

### Stable release snapshot (v0.2.9)

To install the reproducible stable release snapshot, pin the `#v0.2.9` tag:

```bash
npx skills add light-cheng/skills#v0.2.9
npx skills add light-cheng/skills#v0.2.9 --skill light-implement
```

### Previous releases

Pin the `#v0.2.8` tag for a reproducible [v0.2.8](https://github.com/light-cheng/skills/releases/tag/v0.2.8) install:

```bash
npx skills add light-cheng/skills#v0.2.8
npx skills add light-cheng/skills#v0.2.8 --skill light-implement
```

Pin the `#v0.2.7` tag for a reproducible v0.2.7 install:

```bash
npx skills add light-cheng/skills#v0.2.7
npx skills add light-cheng/skills#v0.2.7 --skill light-implement
```

Earlier tags (such as `#v0.2.4`, `#v0.2.2`, `#v0.2.1`, and `#v0.2.0`) remain available for reproducible installs:

```bash
npx skills add light-cheng/skills#v0.2.4
npx skills add light-cheng/skills#v0.2.2
npx skills add light-cheng/skills#v0.2.1
npx skills add light-cheng/skills#v0.2.0
```

> **Note:** The `#v0.2.0` tag remains an immutable, reproducible snapshot of the v0.2.0 release line and is not modified by subsequent work on `main`.

### Target a specific Agent directly (command template)

```bash
npx skills add light-cheng/skills --agent claude-code
```

### Companion MCP runtime

The `agent-config` Skill uses an optional companion MCP server for host inspection and profile persistence, maintained in [light-cheng/agent-config](https://github.com/light-cheng/agent-config):

```bash
git clone https://github.com/light-cheng/agent-config.git
cd agent-config && npm ci && npm run build && npm install -g .
agent-config setup --check
```

### Optional decision sources

`ask-light` and `agent-config` can hand bounded judgments (choose among legal options, yes/no, a level on a scale) to a typed decision model through `light-decide`. Each project sets how far that question state may travel with a `Decision data:` line in `docs/agents/light-project.md` (`on-device`, `private-network`, `third-party` or `off`). Without the line, only a model on this machine is asked. An answer is used only when your policy file `~/.config/light/decision-policy.json` calibrates that question; otherwise the deterministic baseline stands. When no source is found, `light-decide` can offer setup and waits for your yes.

See [Installation](docs/INSTALLATION.md) for advanced options (explicit agent targets, copy mode, non-interactive CI flags), manual file copying, and verification notes.

## Quick Start

Type each Skill name with your Host's prefix, for example `/ask-light next` in Claude Code or `$ask-light next` in Codex.

```text
ask-light next        # Suggest the next appropriate Skill from current context
project-init          # Bootstrap project workspace and task tracker settings
clarify               # Clarify requirements through targeted questions
project-clarify       # Clarify project decisions using repository context
light-implement       # Execute a ready ticket with verification
project-review        # Run final acceptance checks: PASS / FAIL / BLOCKED
```

## Main Workflow

A typical project progresses through these stages, though you can start directly at any stage:

```text
project-init
      ↓
project-clarify
      ↓
project-spec
      ↓
project-tickets
      ↓
light-implement
      ↓
project-review
      ↓
release-workflow
      ↓
project-retro (agent evaluates friction)
```

- `project-init`: sets up project layout and task tracker settings.
- `project-clarify → project-spec → project-tickets`: clarifies requirements, writes the specification, and splits work into executable tickets.
- `light-implement`: implements one ticket at a time with automated checks.
- `project-review`: verifies quality against acceptance criteria; `review-loop` handles iterative fixes.
- `release-workflow`: runs release validation, tagging, and publication.
- `project-retro`: evaluates session friction (navigation, automated checks, instruction clarity, tool usage) and proposes concrete improvements at the conclusion of the workflow.

Direct paths for common tasks:

```text
clarify                                  # Standalone brainstorming and clarification
light-implement                          # Implement a well-defined ticket directly
light-diagnosing-bugs → light-implement  # Diagnose an issue, then apply the fix
release-workflow                         # Publish an approved release
ask-light                                # Route unclear tasks to the right Skill
```

See [docs/workflows/](docs/workflows) for full workflow guides.

## Finding the Right Skill

```text
ask-light next
ask-light workflow
```

`ask-light` is the Light workflow advisor, navigator, and router. It inspects project and workflow evidence, reasons about the best next Skill, explains why, and waits for approval before a validated host-aware transition (model-invoked targets may begin where supported; user-invoked targets fall back to rendering the exact invocation when direct Host transition is unavailable).

See [ask-light](skills/productivity/ask-light/SKILL.md) and [docs/workflows/](docs/workflows).

## Skills Overview

| Group | Skills | Details |
| --- | --- | --- |
| **Project** | `project-init`, `project-clarify`, `project-spec`, `project-tickets`, `light-implement`, `project-review`, `release-workflow` | [CATALOG.md](CATALOG.md) |
| **Clarification & Research** | `socratic` (engine), `clarify`, `project-clarify`, `decision-map`, `light-research`, `light-prototype`, `light-to-questionnaire` | [clarification-system](docs/workflows/clarification-system.md) |
| **Execution** | `light-implement`, `agent-config` (primary harnesses: 10 native adapters + fallback), `light-tdd`, `light-diagnosing-bugs`, `light-merge-conflicts` | [execution](docs/workflows/execution.md) |
| **Review** | `review-loop` (engine), `generic-review`, `light-code-review`, `project-review` (acceptance) | [review-system](docs/workflows/review-system.md) |
| **Specialized** | `manuscript-ops`, `kb-init`, `learn-anything`, `language-learning`, `kanban-worker`, `eli5`, `recap` | [specialized-workflows](docs/workflows/specialized-workflows.md) |
| **Productivity** | `light-handoff`, `humanizer`, `light-wizard`, `light-wait-what`, `light-writing-for-agents`, `light-travelpage` | [CATALOG.md](CATALOG.md) |

See [CATALOG.md](CATALOG.md) for full descriptions, invocation modes, and package paths.

## Provenance and Attribution

| Origin | Policy | Repository Treatment |
| --- | --- | --- |
| First-party | Collection owner authored | Maintained in `skills/<category>/<name>/`. |
| Approved Port (Matt Pocock) | Upstream behavior preserved with `ATTRIBUTION.md` | Self-contained in `skills/<category>/<name>/` without upstream runtime dependencies. |
| Third-party unmodified | External upstream | Recommended for direct installation; not duplicated here. |
| Modified third-party | Managed in private `light-cheng/skills-3rdParty` | Retains full patches, licenses, and sync locks. |
| Retired standalone | Consolidated into collection | Documented with migration history in release records. |

Approved Matt Ports (12 packages): `light-research`, `light-prototype`, `light-tdd`, `light-handoff`, `light-diagnosing-bugs`, `light-wizard`, `light-teach`, `light-wait-what`, `light-to-questionnaire`, `light-writing-for-agents`, `light-merge-conflicts`, `project-retro`. Each package contains `ATTRIBUTION.md` and runs without external runtime dependencies.

Adapted origin (2 packages): `humanizer` is a substantially transformed first-party capability based on blader/humanizer (2.11.2) with a thin Chinese adaptation layer informed by op7418/Humanizer-zh; both MIT licenses are preserved in its [ATTRIBUTION.md](skills/writing/humanizer/ATTRIBUTION.md).

`light-travelpage` substantially transforms do-tongxue/Travel-Plan-Page with protected D1 collaboration, validation, recovery and generation/update tooling; its MIT provenance is in [ATTRIBUTION.md](skills/productivity/light-travelpage/ATTRIBUTION.md).

## Documentation

- [Maintenance Contract](AGENTS.md)
- [Skill Admission Policy](docs/SKILL_ADMISSION.md)
- [Maintenance and Synchronization](docs/MAINTENANCE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Review Policy](docs/REVIEW_POLICY.md) · [Reviewer Contract](docs/REVIEWER_CONTRACT.md)
- [Catalog](CATALOG.md) · [Changelog](CHANGELOG.md)
- [Workflow Guides](docs/workflows)
- [Release Receipt](docs/evidence/releases/v0.2.9/RELEASE_RECEIPT.md) · [v0.2.8 Release Receipt](docs/evidence/releases/v0.2.8/RELEASE_RECEIPT.md) (previous release)
- [Collection Discovery Tests](tests/test_collection_discovery.py) · [Composition Tests](tests/test_composition.py)
