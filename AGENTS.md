# Light Skills — maintainer guide

> Local workspace tracker: inspect `.scratch/` for the active feature directory — see `docs/agents/issue-tracker.md`. This note is local-only.

This file tells an Agent how to maintain this repository. The detailed rules live in the linked documents; do not copy them into Skill packages.

## What belongs here

The repository holds only:

- Skills the collection owner wrote; and
- Skills substantially transformed into an owned capability, with attribution and any required license notice.

Do not import an unmodified upstream Skill for convenience. If upstream already does the job, recommend installing it directly. If it needs local changes, compatibility work or a pinned variant, evaluate it for the separate `skills-3rdParty` repository.

The approved Matt Pocock Ports (SPEC §14/§16) are the exception: `light-research`, `light-prototype`, `light-tdd`, `light-handoff`, `light-diagnosing-bugs`, `light-wizard`, `light-teach`, `light-wait-what`, `light-to-questionnaire`, `light-writing-for-agents`, `light-merge-conflicts`, `project-retro`. Each is self-contained, carries `ATTRIBUTION.md`, and has no upstream runtime dependency.

`project-workflow` is retired. Do not add a shim, dependency or package with that name unless a separately approved change shows a real external need.

## Where things live

- Packages: `skills/<category>/<skill-name>/`. Each owns its `SKILL.md` and only the resources, scripts, templates or assets it needs. No empty directories or placeholders.
- Provenance for a transformed Port: `ATTRIBUTION.md` in the package (source, path, pinned revision, license, Light changes). Never claim authorship of unmodified material.
- `CATALOG.md`: human-readable inventory, derived from package metadata. `CHANGELOG.md`: unreleased and released changes.
- Workflow documents are examples and test assets, not admission gates.

Governance documents:

- [Admission and evidence](docs/SKILL_ADMISSION.md)
- [Maintenance, catalog, release and closeout](docs/MAINTENANCE.md)
- [Installation and fresh-install verification](docs/INSTALLATION.md)
- [Review weight, profiles and verdicts](docs/REVIEW_POLICY.md) · [Reviewer contract](docs/REVIEWER_CONTRACT.md)

## Rules for every change

1. Use **Matt Pocock Skills** as the main reference for writing Skills: a short entry file, details in supporting files, composition over copying.
2. Treat `agent-config`'s own `SKILL.md` and references as its design contract. (Sol Advisor was its original design reference and is now out of date; do not consult it.) In short, `agent-config`:
   - keeps setup (companion, bootstrap, Profile preparation or repair) separate from normal execution planning, and never enters setup silently;
   - changes Host configuration only after explicit approval, and leaves unrelated Host settings untouched;
   - treats single-model and multi-model as equal modes and uses only user-confirmed Profiles;
   - relies on real Host evidence: it never infers a model's ability from its name, treats unknown capability as unconfirmed, and maps abstract reasoning levels to values the Host actually supports;
   - uses the optional companion MCP for persistence and Host changes across 10 native adapters (Codex, Claude Code, Antigravity, DeepSeek Harness, OpenCode, ZCode, Cursor, Grok Build, Hermes, Pi with its MCP extension) plus one generic fallback, which is non-native and plan-only; it never claims universal Harness support;
   - stops at planning: ticket decomposition, implementation, review convergence and final acceptance belong to other Skills.
3. Read the upstream or reference Skill before changing a Skill derived from it.
4. Leave the mature Light Skills alone (`manuscript-ops`, `kb-init`, `learn-anything`, `language-learning`, `kanban-worker`, `recap`, `eli5`, `release-workflow`) unless their responsibility must change. Several are hash-frozen by tests.
5. Do not redesign the Ports listed above. Port them, then make only the small changes Light handoff needs.
6. Keep `SKILL.md` short: when to use it, what it does, how, where to read more, and when to stop or hand off.
7. Put long workflows, examples, formats and checklists in `references/`, `templates/` or `scripts/`.
8. Let each package choose its own structure.
9. Compose instead of copying instructions (`clarify → socratic`, `light-implement → review-loop`).
10. Do not copy repository architecture into Skill packages.
11. Update only the documents a change actually affects.
12. Tests protect behavior and composition, not wording. Do not add words to a `SKILL.md` just to satisfy a test; fix or delete the test instead.
13. Keep required upstream attribution in `ATTRIBUTION.md`.
14. Do not guess what an Agent Host can do. Inspect Host evidence first (`agent-config`).

## Writing style

Write instructions as short, direct sentences. Name who does what. Say what to do before what to avoid, and give an example when a rule is easy to misread. Agents imitate the prose they read, so this applies to `SKILL.md` files, references and these governance documents alike.

## Invocation direction

Every package declares and tests one invocation type:

- **User-invoked**: the user selects it. It never silently chains into another user-invoked Skill. It may recommend one, and with explicit user approval and verified Host support it may hand over to that exact Skill and stop there. It may call model-invoked capabilities.
- **Model-invoked**: a reusable capability the model or another Skill may call.

## Changing a package

For a create, update, rename, deprecation, removal, Port or adaptation:

1. Check reuse before invention ([admission](docs/SKILL_ADMISSION.md)).
2. Keep the package boundary, invocation direction and attribution.
3. Pick the review weight in [review policy](docs/REVIEW_POLICY.md#how-much-review-a-change-needs) and collect only the evidence it asks for. Structure alone never proves behavior.
4. Update the affected documents and catalog entries ([maintenance](docs/MAINTENANCE.md)).

Never rename, remove or deprecate silently. Keep a migration path, update discovery and installation docs, and record the change in the changelog and release notes.

## Review weight

- **Everyday change** to an admitted package (same invocation type, dependencies, attribution and install surface; no script change): run the package tests and the full suite locally, and the owner tries it in real use.
- **Documentation only**: run `python scripts/check_public_docs.py` and the full suite.
- **New admission**: an eligible low-risk prompt-only Skill uses the fast track — structural, install, contract and invocation evidence plus one fresh independent Evaluator, with no separate Critic or `light-code-review`. Everything else uses the full path.
- **Full path**: `review-loop` with the matching Profile (`agent-skill`, `generic`, `software`, `manuscript`, `specification`) drives convergence; `project-review` owns the frozen baseline and the final `PASS`/`FAIL`/`BLOCKED`. Executable scripts also need focused and negative tests, adversarial fixtures where useful, and `light-code-review` findings. A zero-assertion or no-op test is not a pass. Specialist reviewers (`generic-review`, `light-code-review`, domain) return findings only ([reviewer contract](docs/REVIEWER_CONTRACT.md)).

## Installation and release

Do not publish an installation command as verified until it has worked against the released repository in a fresh environment. Keep a manual fallback and record Host discovery ([installation](docs/INSTALLATION.md)).

Before a stable release, bring the README, catalog, installation guide, governance links, workflow examples, discovery tests, changelog and attribution records into line. The release record separates first-party, approved Port, direct upstream, modified third-party and retired sources, and lists the real release identifiers, verified commands, evidence, limits and migration state. Follow [maintenance](docs/MAINTENANCE.md).
