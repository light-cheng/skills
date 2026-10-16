# When a published release is broken

Release tags are protected: nobody can move or delete them, and people may
already have installed `#vX.Y.Z`. So you never repair a release in place. You
mark the broken one, publish a fixed patch release, and record both.

Example: `v0.3.0` installs a Skill whose script crashes. You publish `v0.3.1`
with the fix, and `v0.3.0` stays available but clearly marked.

## 1. Confirm and write down the defect

Reproduce it from the released tag, not from main. Record what breaks, who is
affected (pinned installs, latest installs, which Skills), how you found it, and
the evidence. Show this to the owner before any remote change; each step below
that writes to GitHub needs their approval.

## 2. Mark the broken release

Keep the tag and the GitHub Release. Do not mark it as a draft or pre-release:
that changes the published facts its receipt recorded.

1. Add a short notice at the top of the Release body and keep the rest:
   ```bash
   REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
   NOTES="$(mktemp -d)/release-body-vX.Y.Z.md"
   gh release view vX.Y.Z --repo "$REPO" --json body --jq .body > "$NOTES.old"
   { printf '> **Known defect:** <one sentence>. Use vX.Y.Z+1 instead.\n\n'; cat "$NOTES.old"; } > "$NOTES"
   gh release edit vX.Y.Z --repo "$REPO" --notes-file "$NOTES"
   ```
2. In INSTALLATION (both languages), put the same warning next to the pinned
   `#vX.Y.Z` command. Remove the warning only if the defect turns out not to
   exist.

## 3. Publish the fix as a new patch version

Fix the defect on main through the normal review weight, then run the full
workflow for `vX.Y.Z+1`, from PREPARED to ATTESTED. Its Notes name the defect,
the affected version and the migration (usually: reinstall with the new tag).
`gh release create` marks the higher version as Latest.

If the fix is not ready soon and the defect is serious, tell the owner. They
decide whether to point README and INSTALLATION back to the previous good
release in the meantime.

## 4. Record it in the receipts

On main, add a `Known defect` section to both languages of the broken release's
`RELEASE_RECEIPT`:

| Field | Example |
| --- | --- |
| Defect | `light-x` script crashes on empty input |
| Found | 2026-10-20, by the owner, reproduced from `#v0.3.0` |
| Affected | pinned `#v0.3.0` installs of `light-x` |
| Replaced by | `v0.3.1` (link to its receipt) |

Keep `Status: VERIFIED`. The receipt still records what was really published
and installed; the new section records what was learned later. The new
release's receipt says which release it replaces.

Then rerun the attested check for the broken tag in historical mode, so the
edited body and receipt still pass:

```bash
python3 scripts/verify_release_integrity.py --tag vX.Y.Z --stage attested --mode historical --check-remote
```

If it rejects the notice wording, change the notice; do not weaken the check.

## Never

- delete, move or re-point a release tag;
- republish a different commit under an existing version;
- edit the Manifest or Notes frozen inside the tag;
- erase the failed evidence.
