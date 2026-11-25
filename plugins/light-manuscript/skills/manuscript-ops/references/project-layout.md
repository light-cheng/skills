# Project layout and path mapping

## New Project route

Create only the smallest directory set needed for the approved Brief:

```text
<root>/
|-- CLAUDE.md or AGENTS.md          (optional workflow bridge from /light-setup)
|-- docs/
|   |-- manuscript-brief.md
|   |-- outline.md
|   |-- source-map.md
|   `-- glossary.md
|-- sources/
|   |-- authoritative/
|   `-- reference-only/
|-- manuscript/
|-- assets/
|-- deliverables/
|-- archive/
|-- .scratch/
|   `-- <feature>/
|       |-- acceptance/             (Acceptance charter and milestone verdicts)
|       |-- changes/                (redirect Change proposals when scope shifts)
|       `-- decisions.md            (optional decide audit log)
`-- .manuscript-ops/
    |-- state.json
    |-- routing-snapshot.json
    |-- project-profile.json
    |-- batch-manifest.json
    |-- format-registry.json
    |-- platform-capabilities.json
    |-- capability-snapshot.json
    |-- format-qa/
    |-- sources/
    |   `-- source-register.tsv
    |-- reviews/
    |-- snapshots/
    `-- gates/
```

Keep temporary page renders and scratch inspection caches in an ignored QA directory rather than alongside user-facing deliverables.

## Existing project

Preserve every existing file and directory path. Never move or rename user files just to match the default tree; map logical roles to existing project-relative paths in `project-profile.json`:

```json
{
  "paths": {
    "brief": {
      "value": "planning/approved-scope.md",
      "origin": "资料发现",
      "evidence": "existing approved planning record"
    },
    "deliverables": {
      "value": "output/final",
      "origin": "用户决定",
      "evidence": "user-designated delivery directory"
    }
  }
}
```

## Separation rules

- `docs/` holds human-readable intent, outline, source map, and glossary.
- `.manuscript-ops/` holds deterministic machine state, snapshots, batch manifest, format QA records, and gate receipts.
- `.scratch/<feature>/` holds companion skill artifacts (`acceptance/`, `changes/`, `decisions.md`) so the repository root stays clean.
- `sources/authoritative/` backs factual claims.
- `sources/reference-only/` informs tone, structure, or presentation without granting factual authority unless reclassified with user approval and evidence.
- `manuscript/` holds editable source drafts and the locked source manuscript.
- `deliverables/` holds user-facing generated outputs only.
- `archive/` retains superseded immutable milestones under approved retention rules.

## Source intake

Register every source in `source-register.tsv` before batch consumption: stable `source_id`, authority `class`, `adapter_id`, `path_or_url`, `publisher_or_owner`, `retrieved_at`, local file `sha256`, `privacy_class`, `permitted_use`, `exclusions`, `metadata_json`, and `derived_artifacts_json`.

`permitted_use` is a comma-separated subset of `factual`, `context`, `style`, and `incoming`. `exclusions` is `none` or a disjoint subset of the same tokens. Batch dependencies must match an allowed use: `factual` requires `authoritative` class, and `incoming` requires `incoming-draft` class. OCR outputs, transcripts, and text extractions remain linked derivatives and never silently replace or promote their parent source.
