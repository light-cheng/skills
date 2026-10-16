# First-Party Maintenance and Documentation Synchronization

<!-- release-state: {"view": "current", "stable": "v0.2.9"} -->

[中文维护说明](MAINTENANCE.zh-CN.md)

This document governs the lifecycle of admitted first-party Skills and the documentation that makes them maintainable and installable. It does not duplicate the ownership contract ([AGENTS.md](../AGENTS.md)) or the architecture.

## Authoritative records

Keep each fact in one authoritative location and link elsewhere:

| Fact | Authoritative location |
| --- | --- |
| Package behavior, triggers, invocation, inputs, outputs, resources | `skills/<category>/<skill-name>/SKILL.md` (and its supporting files) |
| Provenance for a Port/transformed package | `skills/<category>/<skill-name>/ATTRIBUTION.md` |
| Human-readable inventory | [CATALOG.md](../CATALOG.md), synchronized from package metadata |
| Installation procedure and proof requirements | [docs/INSTALLATION.md](INSTALLATION.md) |
| Review triggers, reviewer vs engine vs acceptance | [docs/REVIEW_POLICY.md](REVIEW_POLICY.md) · [docs/REVIEWER_CONTRACT.md](REVIEWER_CONTRACT.md) |
| Repository change history | [CHANGELOG.md](../CHANGELOG.md) and the actual release record |
| Composition validation assets | [docs/workflows/](workflows) and linked evidence |

## Current synchronization baseline

The admitted collection contains **39 first-party Skills** under `skills/` (see [CATALOG.md](../CATALOG.md)). The current stable release is [v0.2.9](https://github.com/light-cheng/skills/releases/tag/v0.2.9) (39 packages; repository links move to `light-cheng`). Its [release manifest](evidence/releases/v0.2.9/RELEASE_MANIFEST.md) records the preparation-time scope and its [release receipt](evidence/releases/v0.2.9/RELEASE_RECEIPT.md) the observed publication and installation facts.

The previous release is [v0.2.8](https://github.com/light-cheng/skills/releases/tag/v0.2.8) ([release receipt](evidence/releases/v0.2.8/RELEASE_RECEIPT.md)).

History markers: `v0.1.1` (five), `v0.1.2` (seven), `v0.1.3` toolchain migration, `v0.1.4` (`kanban-worker` as `light-kanban-worker`), `v0.1.5` scheduling + identity hardening, `v0.1.6` (`kb-init`). Structural/discovery checks live in [tests/test_collection_discovery.py](../tests/test_collection_discovery.py) and [tests/test_composition.py](../tests/test_composition.py); they are structural evidence, not fresh-install proof.

v0.2.8 renames one package ([v0.2.8 migration guide](MIGRATION-v0.2.8.md)). The earlier v0.2.7 changes to 12 names are in the [v0.2.7 migration guide](MIGRATION-v0.2.7.md) and the previous [v0.2.7 release receipt](evidence/releases/v0.2.7/RELEASE_RECEIPT.md); evidence for the v0.2.6 attempt remains historical.

## Change workflow

For every **add / update / rename / deprecation / removal / port / adapt**:

1. Re-check ownership and reuse-before-invention in [Skill admission](SKILL_ADMISSION.md) — approved Matt PORTs (SPEC §14) are architecture-authorized when they carry `ATTRIBUTION.md` and no runtime dependency.
2. Preserve package boundary, invocation direction, and required attribution.
3. Pick the review weight in [review policy](REVIEW_POLICY.md#how-much-review-a-change-needs): everyday change, documentation only, full review, or a release. Collect only the evidence that weight requires. For full review, `review-loop` is the engine and `project-review` owns final acceptance.
4. For a new admission, classify it as the prompt-only fast track or the full path in [Skill admission](SKILL_ADMISSION.md).
5. Update only the surfaces the change affects: README, catalog, installation guide, governance links, composition examples, discovery/composition tests, attribution records, and changelog.
6. Prepare an unreleased changelog entry. Do not claim a version, tag, or verified release command until the release gate passes.

## Synchronization matrix

| Change | Documentation and validation that must be reviewed |
| --- | --- |
| **Add** | README, catalog, installation guide, governance references, affected composition examples (`docs/workflows/`), discovery + composition tests, changelog, applicable `ATTRIBUTION.md`, fresh-install evidence, and the selected fast-track or full-path verdict. |
| **Update** | Package contract and behavior evidence; affected catalog, installation, attribution, examples, discovery/composition tests, compatibility evidence, and changelog. |
| **Rename** | Old-to-new migration guidance; all links, catalog records, installer examples, discovery/composition tests, examples, attribution references, and changelog. |
| **Deprecate** | Catalog status, README guidance, replacement/migration path, installation warning, examples, discovery/composition tests, changelog, and release notes. |
| **Remove** | Confirm no supported consumer needs a shim; remove stale references, preserve migration guidance, update catalog/installation, and record the removal. |
| **Port** | Upstream source read, `ATTRIBUTION.md` (source/path/revision/license/Light changes), Light handoff adaptation, no upstream runtime dependency, plus Add-matrix docs/tests. |
| **Adapt** | Reference upstream pattern, describe Light-specific integration need, preserve `ATTRIBUTION.md` where applicable, plus Update-matrix docs/tests. |

## Catalog and installation maintenance

Catalog entries must name purpose, when to use (where useful), invocation type, package path, status, installation scope, and evidence. Package metadata (`SKILL.md` frontmatter + `agents/openai.yaml`) remains the source of truth; do not create a second static routing table.

Every release installation example must name an actual released source and match the current catalog. Verify whole-repository and per-Skill installation against a fresh environment, then preserve exact command, released revision, host, and observed discovery result in the release evidence. Until that exists, keep commands marked as templates.

## Upstream attribution and compatibility

Approved Matt PORTs are self-contained first-party packages with `ATTRIBUTION.md` (source repo, original path, revision/tag, license/notice, Light-specific changes) and **no** required runtime install of `mattpocock/skills`. Other upstream sources may be recommended for direct use without being copied. A package that remains principally a third-party modification belongs in `skills-3rdParty`.

Before release, review attribution, licenses/notices, dependency availability, supported hosts, installation behavior, and known behavioral differences. Light main workflow must not require `mattpocock/skills` or `sol-advisor` at runtime.

## Composition examples

Documents in `docs/workflows/` are validation assets. They explain Skill composition and handoff (`entry → handoff → stop → optional`), not internal Skill workflows. They cannot become hidden admission prerequisites or an automatic workflow.

## Deprecation, rollback, and release

Deprecation is explicit: mark catalog and installation guidance, name a replacement or state none, retain migration info for the released support period, and record in the changelog.

If a release candidate fails verification, stop promotion and repair through the applicable review process. Do not rewrite published history or erase evidence. A stable release requires only admitted packages, synchronized docs, verified installation commands, required review evidence, and a real version/tag.

## Closeout record

At closeout, record final repository location, released versions/tags, verified commands, first-party catalog (current package count), approved Ports vs direct upstream vs modified third-party distinctions, evidence, limitations, and migration/archive guidance. Do not label structural or simulated evidence as runtime proof. Historical evidence (`docs/evidence/`) stays immutable.

Evidence added after v0.2.7 names no one's machine. Before you commit an evidence file, run `python3 scripts/check_evidence_paths.py --apply <file>...`: it turns the repository root into `<repo>`, temporary directories into `<tmp>`, the home directory into `~`, and key-shaped values into `<redacted>`. `python3 scripts/check_evidence_paths.py --check` fails while any evidence added since v0.2.7 still holds a personal path or a key-shaped value; run it before a release. Older evidence is not rewritten.


## Validation entry points after categorization

From the repository root, run `python3 -m pytest -q`. For standalone frozen package test scripts, use `PYTHONPATH=tests python3 <test-path>`; CI sets the same `PYTHONPATH=tests`. This preserves frozen file bytes while resolving the shared helpers after adding a category level.

## Release document views

A frozen version snapshot describes its own content. Current main identifies the stable version from confirmed bilingual Receipts. A Manifest records preparation-time history. Use the common [document-state contract](../skills/project/release-workflow/references/DOCUMENT-STATE.md) and fixed-tree stage gates; historical audits preserve their original scope. Installation/publication facts and final-main CI remain distinct from local simulation.
