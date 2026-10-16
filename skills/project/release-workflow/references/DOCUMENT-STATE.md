# What release documents may say

The same version appears in three places. Each may claim only what is true at
the moment it is frozen or published.

| Place | Describes | Must not say |
| --- | --- | --- |
| Candidate and tag (Notes, Manifest, public pages at that commit) | This version's content | That it is the current stable release, that it is unpublished, or any install or publication success. Those facts are only known later. |
| Current main | The latest confirmed stable version, and the difference between latest and pinned installs | A stable version that no VERIFIED receipt confirms. |
| GitHub Release body | This release's content, migration, and verification you actually observed | An unpublished status, a wrong version, broken links, or a success nobody observed. |

Check README, CATALOG, INSTALLATION and MAINTENANCE in both languages, plus both
languages of the Notes and Manifest. A Manifest states that it was written at
preparation time. Old failures, earlier versions and recovery commands keep
their meaning: never search-and-replace version numbers across the docs.

Main learns the current stable version only from a release's bilingual receipts
with `Status: VERIFIED`, a matching version and a passing publication row.
Writing VERIFIED into some unrelated receipt does not make a version stable.

## The checking scripts

`scripts/verify_release_integrity.py --tag <version> --release-commit <commit>
--stage <stage> --mode current` checks one stage: `prepared`, `ci_verified`,
`tagged`, `install_verified`, `published` or `attested`. For prepared and
tagged it exports the committed Git tree and checks that, not your working
directory.

`scripts/check_public_docs.py --tag <version> --stage prepared` checks the
snapshot pages. Without `--tag` (as in CI) it picks the view itself: if the
newest Manifest has no confirmed receipt yet, it checks the snapshot rules;
once that receipt is confirmed, it checks the current-main rules.

### Observations

From CI_VERIFIED on, pass what you observed with `--observations <json>`. The
file has `kind: observed`, the exact `tag`, `candidate` set to the commit you
pass as `--release-commit` (from TAGGED on, `RELEASE_SHA`, the commit the tag
points at), and the real tool results:

- `ci`: the GitHub run's `databaseId`, `headSha`, `status` and `conclusion`;
- `installation`: the `result.json` from the `release-installation` workflow,
  with pinned and latest source commits, source manifests and the installed
  manifests; every path and hash must match;
- `release`: from `gh release view --json`, the `tagName`, the draft and
  pre-release flags (both false), `url`, `publishedAt` and the `body`.

The `url` must be this tag's release page on the current repository (found as in
[RELEASE-STAGES.md](RELEASE-STAGES.md); `--repo owner/name` overrides it). Receipts
and other documents written before a rename keep the old name and still pass.

For ATTESTED, pass the final main CI run separately with `--final-ci <json>`.
Its `headSha` must be the current main commit. Do not write that commit or run
into its own receipt.

For a local rehearsal, use `kind: test-double` with `--simulate`. The result is
`SIMULATED_PASS`. Missing or mismatched observations never count as facts.

## The Release body

`scripts/prepare_release_body.py` reads the Notes from the tag (or `--revision`)
and checks the version, the statements and the links. It turns relative links
into full URLs on the current repository, pinned to the tag; receipt links
point to main because receipts are written after the tag. It allows an
installation-success claim only with matching observations or an existing
valid receipt.

## Re-auditing an old tag

Use `--mode historical` only to re-audit an existing tag; it cannot prepare or
promote a candidate. Tags up to v0.2.7 were frozen before these rules existed;
they keep their original wording and report a historical-snapshot result. New
candidates follow the current rules. Never move current main back to an older
audited tag.
