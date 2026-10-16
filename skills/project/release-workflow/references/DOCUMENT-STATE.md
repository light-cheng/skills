# Release document state

## One context, three views

The context is a check input, not another release ledger. Target version and fixed
revision identify the snapshot; bilingual VERIFIED Receipts identify current
stable; observation files bind external results to target and candidate.

| View | Meaning | Gate |
| --- | --- | --- |
| Candidate/tag snapshot | This version's content and Manifest, with observed facts in the receipt on main | No frozen current-stable/candidate status, no premature success claims |
| Current main | The latest confirmed stable target and branch/tag install distinction | Target, Receipt and all current fields must agree |
| GitHub Release body | This release's content, migration and actually observed verification | Correct version/links; no unpublished status or unsupported success claims |

Check README, CATALOG, INSTALLATION and MAINTENANCE in both languages, plus both
Notes/Manifest files. A preparation Manifest explicitly names its time context.
Historical failures, previous versions and recovery commands keep their meaning;
never perform an indiscriminate version replacement. Current authority cannot be
established by merely writing VERIFIED in an unrelated newer receipt.

## Common CLI

Run `scripts/verify_release_integrity.py --tag <target> --release-commit <candidate>
--stage <stage> --mode current` for the actual selected phase. Supported stages
are prepared, ci_verified, tagged, install_verified, published and attested.
Prepared/tagged checks export the fixed Git tree rather than the working directory.
Use `scripts/check_public_docs.py --tag <target> --stage prepared` for snapshot
semantics; its ordinary mode selects the branch view from Manifest/Receipt facts.
Without `--tag`, the CI/default entry reads the newest preparation Manifest and
the latest confirmed Receipt. A newer Manifest selects snapshot checks; once its
Receipt is confirmed, current-main checks apply. Keep prior release records.

For CI/install/publication phases supply `--observations <json>`. The record has
`kind: observed`, exact `tag` and `candidate`, then actual tool results:

- `ci`: GitHub run databaseId, headSha, status and conclusion;
- `installation`: the existing released-source verifier result shape, including
  pinned/default source revisions, source manifests and observed destination
  manifests; each source/destination path and hash must match;
- `release`: actual tagName, non-draft/non-prerelease flags, URL, publishedAt and
  the observed body.

Store the final main run separately and pass `--final-ci <json>` to attested.
Its headSha must match the current main commit. Do not put that commit/run back
inside its own Receipt. CI/tag/install/publication checks are separate from
current main's exact final CI, and the report names both.

Local rehearsals use `kind: test-double` plus `--simulate`; the result says
SIMULATED_PASS. Missing or mismatched observations never become a production fact.

## Body renderer and historical audits

`scripts/prepare_release_body.py` validates body identity, statement semantics and
navigation. It reads the requested source/target, expands sibling and parent
relative links, pins immutable content links and uses main for post-release
Receipts. Claims of installation success require bound observations (or a valid
existing Receipt for publication repair), not merely an install_verified flag.

Use `--mode historical` only to re-audit an existing tag. It cannot prepare or
promote a candidate. Already frozen tags through v0.2.7 retain their old prose
with an explicit historical-snapshot result; new candidates must obey the new
semantic rules. Never downgrade current main to an older audited tag.
