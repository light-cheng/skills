# `manuscript-ops` user guide

[中文指南](../zh-CN/skills/manuscript-ops.md)

The [package contract](../../skills/writing/manuscript-ops/SKILL.md) governs behavior.

## Choose the writing task

Use the Skill for notes, SOPs, reports and manuscript projects. A bounded writing
request can produce a complete document directly; content risk determines the
review needed, while actual lifecycle requirements determine initialization.

| Route | Work | Completion |
| --- | --- | --- |
| Quick | A clear low-risk text edit | Edit, check and deliver |
| Structured | A bounded rewrite/report with sources, images or format needs | Write the whole document, review/render as needed and deliver |
| Project | Explicit manuscript engineering, resumable batches or locked editions | Follow the existing Project gates |

A short safety document normally takes Structured with source and safety review.
One delegation, reference files and a QA-only PDF do not create a Project. Measure
the current manuscript rather than the repository. Preserve material unknowns;
ask only for the decision or source that affects the work.

It is model-invoked and can also be selected explicitly when the Host supports:

Type each Skill name with your Host's prefix, for example `/manuscript-ops` in Claude Code or `$manuscript-ops` in Codex.

```text
manuscript-ops
manuscript-ops resume
```

## Inputs and checks

Supply the purpose, reader, source authority, deliverables, authorized output
location and already-confirmed decisions. Quick/Structured need no project
bootstrap, Profile, Review Charter, Jujutsu or receipts. A delegated writer can
complete the assigned manuscript; reviewers stay read-only and the caller
continues authorized work after a stage returns.

Read the [format/source contracts](../../skills/writing/manuscript-ops/references/formats.md)
for local document IDs, legacy DOC conversions and hash-bound extraction lineage.
DOCX and other layout-sensitive output require real rendering and page inspection.
Missing checks remain not tested; file parseability never proves layout acceptance.

## Optional decision tools

A Host-provided structured MCP can interpret task scope and source relationships.
Its recommendation is bounded by known workflow and review constraints. The
[semantic contract](../../skills/writing/manuscript-ops/references/semantic-routing.md)
describes the optional payload and measured confidence policy. Without a provider
or a reliable result, the current agent uses task evidence; no setup is required.

New assessments use `needs-v2`; unversioned approved Project snapshots replay
`score-v1`. Existing receipts and approvals are preserved. Python 3.11+ is needed
only when using the packaged scripts.

## Project and installation

Only Project reads the [full lifecycle](../../skills/writing/manuscript-ops/references/project-route.md).
It reuses approved state, preserves user-invoked handoff boundaries and consumes
`project-review`'s final acceptance. Unsupported version guarantees are reported
precisely rather than treated as snapshot PASS.

Project consumes the independent `PASS`, `FAIL` or `BLOCKED` verdict. A missing
required dependency returns `BLOCKED` with its precise step and resume condition;
that stage result returns to the caller rather than completing the whole task.

Install through the repository [installation guide](../INSTALLATION.md). Verify
the complete package and an isolated invocation; source scans alone are structural
evidence. The local repair on main is distinct from a released tag or global deployment.
