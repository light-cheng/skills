# Format adapters

Use [format-registry.json](../assets/format-registry.json) as the canonical machine registry. Copy the registry into `.manuscript-ops/format-registry.json` for `Project` state and pair it with observed capability evidence from `scripts/probe_capabilities.py`. Supplement process probes with [platform-capabilities.json](../assets/templates/platform-capabilities.json) translated through [platform-capability-map.json](../assets/platform-capability-map.json).

The packaged registry is an immutable floor: a project copy may add custom adapters, but it cannot delete a canonical adapter, claim a canonical file extension on another adapter, or weaken any canonical operation, dependency, validation step, `blocking_qa_gaps` flag, or degradation rule.

## Tier 1

Tier 1 formats carry an explicit end-to-end contract:

- TXT and Markdown;
- DOCX and PDF;
- HTML and EPUB;
- PPTX.

For each selected Tier 1 format, record reading, editing, generation, structural validation, representative rendering, visual QA, round-trip expectations, dependencies, metadata/privacy checks, and degradation behavior. When an environment lacks a required capability, report the exact gap and stop at `DEGRADED` or `BLOCKED` rather than weakening the contract.

## Tier 2

Enable ODT, RTF, LaTeX, ODP, XLSX, ODS, CSV, Google Workspace, Microsoft 365, and Apple iWork only when the host environment exposes the required operations. Cloud-native documents additionally require stable document identity, revision or export snapshot, permission boundary, and deterministic export where supported.

## Document sources

`source-register.tsv` accepts registered local document format IDs (`pdf`, `markdown`, `docx`, `txt`, `rtf`, and other file-backed adapters) alongside the six source-layer adapters. Keep canonical adapter IDs, matching file extensions, SHA-256 hashes, authority class, `permitted_use`, and `exclusions`. Capture remote document URLs as hash-bound local files before registration.

- `legacy-doc` records original OLE `.doc` intake bytes (verified by header bytes) and declares conversion/extraction derivatives with hashes and `parent_source_ids`. It is never a DOCX generation adapter.
- `json-text-extract` is valid only when another registered source declares the same path and SHA-256 as a `page_text_extract` or `extracted_text` derivative.
- Derivatives (converted documents, text/Markdown extracts, JSON page extracts) inherit every parent's authority ceiling, permitted uses, and exclusions; conversion never promotes `reference-only` or `incoming-draft` material to `authoritative`.

## Source-layer formats

Web captures (`web`), emails (`email`), images/scans (`image-scan`), audio (`audio`), video (`video`), and transcripts (`transcript`) are registered sources with provenance, retrieval timestamps, privacy classes, local hashes, and derivative lineage:

- OCR derivatives (`ocr_text`) link to their `image-scan` parent and record `engine_or_author` and `language`.
- `transcript` rows reference a distinct registered `audio` or `video` `parent_source_id` in `metadata_json` and record `engine_or_author`, `language`, and `created_at`.
- Every `derived_artifacts_json` item records `kind`, project-relative `path`, `sha256`, `parent_source_ids` (containing the declaring source ID), and `created_at`.

## QA contract

1. **Structural QA**: parseability, package parts, links, metadata, styles, dimensions, fields, and internal relationships (`validator_log` evidence).
2. **Render QA**: rendering through a real target application or representative engine (`rendered_output` evidence).
3. **Visual QA**: page-by-page or slide-by-slide inspection, or risk-based sampling only when authorized by the Brief (`inspection_record` evidence).
4. **Semantic QA**: comparing headings, steps, tables, figures, numbers, and cross-references against a distinct hash-bound locked source (`comparison_report` evidence plus `invariants`).
5. **Round-trip QA**: saving through the target application and comparing semantic and layout invariants against a distinct output artifact (`comparison_report` evidence plus `invariants`).

Every check records `coverage` (`mode`, `unit`, `total`, `inspected`, `items`, and `sampling_authority`). `full` PASS inspects every item (`inspected == total`). `sampled` PASS hash-binds the approved Brief and requires that deliverable's Brief row to specify `Visual QA: sampled`. `partial` is valid only on `FAIL`.

Every `READY` format-QA record also binds `generation` (`reproducible` or `manual` mode, tool name/version/evidence, ordered command array, hashed configuration or `not_applicable_reason`, hashed inputs, and exact output hash). Deliverables marked `Reproducible: required` in the Brief must use `reproducible` mode. QA is keyed by exact Brief deliverable path, so multiple editions sharing one format each require their own QA record.

## Degradation and capability verification

- `READY`: all required generation and QA operations succeeded with hash-bound evidence.
- `DEGRADED`: a non-blocking QA or automation capability is absent and the approved Brief policy permits a bounded claim; never accepted at final gates when `blocking_qa_gaps` is `true` or final deliverables require `READY`.
- `BLOCKED`: required generation, rendering, visual inspection, or comparison cannot be performed safely.

`validate_state.py` reparses `platform-capabilities.json`, verifies its SHA-256 and the canonical `platform-capability-map.json` SHA-256, checks platform snapshot freshness against `snapshot_max_age_hours`, reproduces `process_probe` entries against live probes, and enforces closed `derived_alias` rules (`rtf_capable_editor` only from `microsoft_word` or `libreoffice`; `spreadsheet_application` only from `microsoft_excel` or `libreoffice`).
