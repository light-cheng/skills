# Public state model

All machine state uses UTF-8 JSON (except Markdown Briefs and TSV Source Registers) with `schema_version: "1"`, RFC 3339 UTC timestamps, and `YYYY.MM.DD` date versions (with `-02`, `-03` suffixes for same-day collisions).

## Modular validator architecture

`scripts/validate_state.py` is the read-only CLI and public Python entrypoint, backed by four focused internal modules under `scripts/`:

- `schema.py`: `Report`, provenance wrappers, `ProjectProfile`, `ManuscriptBrief`, `RoutingSnapshot` (`needs-v2`), `FormatRegistry`, and `LifecycleState`.
- `lineage.py`: `source-register.tsv` intake, magic-byte container identity, `legacy-doc` and `json-text-extract` parent lineage, derivative authority inheritance, and `BatchManifest` DAG/source bindings.
- `qa.py`: `capability-snapshot.json`, host `platform-capabilities.json` and live `process_probe` verification, `format-qa-record.json` coverage/sampling, semantic/round-trip comparisons, and reproducible generation lineage.
- `gates.py`: `ReviewMatrix`, `acceptance` JSON report integration, the six `GateReceipt` contracts, publication target bindings, and Jujutsu (`jj`) gate verification.

Exit codes: `0` (`READY`), `1` (`DEGRADED`, warnings only), `2` (`BLOCKED`, one or more errors).

## RoutingSnapshot

Required fields: `schema_version`, `routing_policy` (strictly `"needs-v2"`), `task`, `semantic_result`, `semantic_policy`, `semantic_judgment`, `captured_at`, `root`, `dimensions` (six objects with `score`, `effective_score`, `unknown`, `evidence`), `hard_triggers`, `repository_evidence`, `unknowns`, `total`, `route`, `required_review_axes`, `needs_initialization`, `reasons`, `next_action`, and `next_invocation` (set when `route == "Project"`). Snapshots expire once older than `ProjectProfile.snapshot_max_age_hours`.

## ManuscriptBrief

Markdown contract ([manuscript-brief.md](../assets/templates/manuscript-brief.md)) recording goal, audience and optional `Target-reader prerequisites`, scope, source authority, framework, deliverables table (`Deliverable | Language | Format | Reproducible | Visual QA | Stable path`), review and gates, acceptance criteria, risks/assumptions/open questions, and approval metadata (`Approver`, `Exact confirmation`, `Confirmed at`). Deliverable language and format sets must match `ProjectProfile` exactly, and each deliverable uses a unique project-relative path whose suffix matches its selected adapter.

## ProjectProfile

Executable configuration ([project-profile.json](../assets/templates/project-profile.json)) where every configurable leaf is wrapped with provenance:

```json
{
  "value": "docs/manuscript-brief.md",
  "origin": "规则推导",
  "evidence": "standard logical layout",
  "confirmed_at": "2026-11-25T00:00:00Z"
}
```

`origin` must be `资料发现`, `用户决定`, or `规则推导`.

## LifecycleState

`.manuscript-ops/state.json` indexes `phase` (`brief-approved`, `initialized`, `framework-approved`, `working`, `candidate`, `source-locked`, `deriving`, `final-approved`, `published`, `archived`), `date_version`, `required_gates`, `active_receipts`, `active_batch`, `source_register`, `review_matrix`, `latest_review_report`, `capability_snapshot`, `format_qa_records`, and `updated_at`.

## BatchManifest

`.manuscript-ops/batch-manifest.json` lists batches with unique `id`, `kind`, `scope`, typed `source_dependencies` (`{source_id, use, purpose}`), acyclic `depends_on`, `risk`, `review_axes`, `reviewable_volume`, `review_cadence`, `cumulative_regression`, `regression_surface`, frozen `input_snapshot` (required once active/review/accepted/blocked), hash-capable `outputs`, `status`, `user_gate`, hash-bound `review_report`, and post-review `user_confirmation`.

## Manuscript ReviewMatrix and `acceptance` result

`ReviewMatrix` ([review-matrix.json](../assets/templates/review-matrix.json)) freezes `profile: "manuscript"`, `milestone` (`outline`, `batch`, `candidate`, `source-lock`, `final`), `artifact_snapshot`, and all nine manuscript review axes.

`acceptance` consumes that profile and emits a JSON result (stored under `.scratch/<feature>/acceptance/` or `.manuscript-ops/reviews/`) containing:

- `schema_version: "1"`, `provider: "acceptance"`, `profile: "manuscript"`, `milestone`;
- optional `charter`: `{path, sha256}` binding the frozen Acceptance charter (for example `.scratch/<feature>/acceptance/charter.md`);
- `artifact_snapshot`: matching `captured_at` and hashed `files`;
- `verdict`: `"PASS" | "FAIL" | "BLOCKED"` or `{"result": "PASS" | "FAIL" | "BLOCKED", "cause": "implementation" | "direction"}` (`cause` allowed on `FAIL`);
- `completed_at`: RFC 3339 UTC timestamp;
- `manuscript_evidence`: one entry per applicable axis with non-empty hashed `evidence` artifacts (`{kind, path, sha256}`).

## GateReceipt

Each receipt under `.manuscript-ops/gates/<gate>-<date_version>.json` ([gate-receipt.json](../assets/templates/gate-receipt.json)) binds `gate`, `date_version`, `created_at`, `bookmark`, `current_alias`, `jujutsu` (`version`, `change_id`, `commit_id`, `remote_count`), closed `files` hashes, `baseline_profile` (on `baseline`), `locked_source` (on `source-locked`), `capability_snapshot` and `format_qa` (mandatory and `READY` on `final-approved` and `publish-approved`), `publication` (structured target plus path/hash-bound active `final-approved` receipt on `publish-approved`), `review` (mandatory `PASS` on `framework-approved`, `source-locked`, and `final-approved`), and post-evidence `user_confirmation`.
