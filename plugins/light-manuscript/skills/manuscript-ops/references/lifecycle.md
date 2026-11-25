# Manuscript lifecycle

This lifecycle and its fixed gates apply only to `Project`. `Quick` and `Structured` tasks finish directly after their task-specific content and format checks.

## Semantic layers

1. **Authoritative sources**: permitted evidence for factual claims.
2. **Reference-only material**: style, layout, or structural inspiration without factual authority.
3. **Incoming draft**: optional user-supplied draft whose factual authority is not assumed.
4. **Outline**: approved chapter/section structure, reader prerequisite map, and content boundaries.
5. **Working draft**: prose under active editing by the assigned writer.
6. **Frozen review draft**: immutable hash-bound snapshot submitted for review.
7. **Candidate**: integrated manuscript after confirmed review findings are repaired.
8. **Locked source**: user-approved master manuscript from which translations and derived editions are built.
9. **Translation or derived edition**: edition generated strictly from the active locked source.
10. **Final**: format-complete deliverable with `READY` format QA and independent `acceptance` `PASS`.
11. **Archive**: gate receipts, snapshots, reproducible generation records, and retained milestones.

Never collapse a human gate by relabeling an earlier layer.

## Fixed human gates

| Gate | Required evidence | Permission granted |
|---|---|---|
| Brief | `brief-approved-*` receipt matching the approved `ManuscriptBrief` | initialize `.manuscript-ops/` state |
| Initialization | `baseline-*` receipt binding an immutable Profile snapshot under `.manuscript-ops/snapshots/` | begin outline work |
| Outline | `framework-approved-*` receipt plus fresh-context `acceptance` `PASS` (`outline` milestone) binding the mapped outline | write body batches |
| Source lock | `source-locked-*` receipt plus fresh-context `acceptance` `PASS` (`source-lock` milestone) binding Source Register and locked manuscript | generate translations and derived editions |
| Final | `final-approved-*` receipt, `READY` format QA for every Brief deliverable, capability snapshot, and fresh-context `acceptance` `PASS` (`final` milestone) | deliver final outputs |
| Publish | `publish-approved-*` receipt binding target metadata and the exact active `final-approved` receipt path and SHA-256 | create remote, push, release, deploy, or distribute |

User confirmation must occur after all referenced review, capability, and format-QA evidence completes, and receipt creation must occur no earlier than confirmation.

## Batches

Partition batches by:

- semantic cohesion;
- prerequisite reading order and **Concept Grounding** dependencies;
- source and terminology dependencies;
- factual, privacy, or safety risk;
- format and layout coupling;
- bounded volume a fresh-context reviewer can audit thoroughly without context dilution.

Each batch declares its `kind` (`outline`, `content`, `candidate`, `source-lock`, `derivative`, `final`), `review_cadence` (`incremental` or `cumulative`), `regression_surface`, `input_snapshot`, hash-capable `outputs`, `status`, `review_report`, and `user_gate`. `outline`, `candidate`, and `final` batches always run `cumulative` review. Keep at most one `active` or `review` batch at a time matching `state.json` `active_batch`, and never advance a dependent batch before all `depends_on` batches reach `accepted`.

## Writer and reviewer boundaries

The assigned writer (main session or a delegated writer subagent started with a **fresh context window**) is the sole prose author for the manuscript. Reviewers and the independent Evaluator inside `acceptance` are strictly read-only, also run in **fresh context windows** against frozen hash-bound snapshots, and return findings or verdicts without editing manuscript files.

## Reproducible generation

Prefer readable source manuscripts plus scripted deterministic generators for binary deliverables. Every `READY` format-QA record captures `generation` mode (`reproducible` or `manual`), tool identity, command array, hash-bound configuration (or `not_applicable_reason`), hash-bound inputs, and output hash. Deliverables marked `Reproducible: required` in the Brief cannot use `manual` mode. Final generation inputs and semantic QA must both bind the active locked manuscript. Never overwrite a prior dated milestone; allocate a new suffix via `scripts/next_version.py`.
