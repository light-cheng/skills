# Fresh-install verification

Install from the **published tag** into a fresh, empty directory that does not
contain the source checkout. There are three checks:

| Check | Required? | Proves |
| --- | --- | --- |
| `release-installation` workflow | **Required** for INSTALL_VERIFIED | On a fresh hosted Linux runner, the pinned and latest sources install every package file exactly, for the Codex and Claude Code targets, globally and per project, plus three single Skills. Its `result.json` is the `installation` observation the integrity gate reads. |
| Manual command matrix (below) | Optional | The published commands work on the owner's own machine and the `skills` CLI lists the packages. |
| Real-Host smoke (below) | Optional, recommended | A real Agent Host started in the fresh install discovers the Skills and runs one of them. |

The workflow and the matrix check that files arrive. Only the Host smoke shows
that a Host actually loads them. Record each result you ran; never report one
you skipped.

## Running the required workflow

```bash
REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
gh workflow run release-installation.yml --repo "$REPO" --ref main -f tag=vX.Y.Z -f expected_commit="$RELEASE_SHA"
```

Dispatch it from main. The tag freezes its own copy of the verifier, so a bug
in that copy would block the release; running from main lets a fix on main
apply without moving the tag. (v0.2.7 hit this: its tagged verifier expected
`~/.codex/skills`, while the installer writes `~/.agents/skills`.)

If the workflow cannot run, INSTALL_VERIFIED stays blocked. Report that; the
manual matrix does not replace it.

## Manual command matrix

Record `npx --yes skills --version` first. Use a new empty directory per row.

| Form | Whole collection | One Skill |
| --- | --- | --- |
| Latest | `npx --yes skills add "$REPO" --yes --copy --agent '*'` | `npx --yes skills add "$REPO" --skill <name> --yes --copy --agent '*'` |
| Pinned | `npx --yes skills add "$REPO#vX.Y.Z" --yes --copy --agent '*'` | `npx --yes skills add "$REPO#vX.Y.Z" --skill <name> --yes --copy --agent '*'` |

Latest follows the repository's default branch; `#vX.Y.Z` pins the tag.

For each row:

1. Record the exact command and its exit code.
2. Count the packages under `.agents/skills/`: the whole admitted set, or
   exactly one.
3. Run `npx --yes skills list` in the directory and confirm the packages are
   listed. Strip ANSI colour codes before searching the output.
4. Run the same install again. `overwrites:` means a harmless reinstall.

## Real-Host smoke

Run this in the pinned whole-collection directory after the matrix, with a Host
the owner already has installed and signed in. Use one run: it asks the Host to
list what it sees and to use one model-invoked Skill. `eli5` is a good choice
because any explanation request triggers it and it needs no tools.

Claude Code example (install with `--agent claude-code` or `--agent '*'`):

```bash
cd "$FRESH_DIR"
claude -p "List the Skills you can use in this project. Then explain what a git tag is, like I'm five." \
  --output-format stream-json --verbose > host-smoke.jsonl
# Discovery: every installed package is in the session's Skill list. Prints nothing on success.
jq -r 'select(.type=="system" and .subtype=="init") | .skills[]' host-smoke.jsonl | sort > host-skills.txt
ls .claude/skills | sort | comm -23 - host-skills.txt
# Invocation: the Host called the Skill. Prints "eli5".
jq -r 'select(.type=="assistant") | .message.content[] | select(.type=="tool_use" and .name=="Skill") | .input.skill' host-smoke.jsonl
```

Pass when the first check prints nothing and the second prints `eli5`. (Checked
on 2026-10-16 with Claude Code 2.1.296 against `#v0.2.7`: all 36 packages were
listed and `eli5` was called.) For pi or another Host, first check its own help
for a one-shot (print) mode and how it reports Skill use; do not guess flags.

Before you trust the result, check whether the Host also loads a user-level copy
of this collection (for Claude Code, `~/.claude/skills`). If it does, say so in
the evidence: the smoke then shows that the Host works, not which copy it used.
Do not delete or move the owner's user-level Skills to make the test cleaner.

## What to record

- the exact commands, CLI version and Host version;
- repository, released tag and commit;
- Host, install scope and destination type (never absolute private paths,
  tokens or usernames — run `python3 scripts/check_evidence_paths.py --apply`);
- that discovery ran without the source checkout;
- each smoke result, including skipped ones and why;
- any manual fallback and known limits.

## Known pitfalls

- ANSI colour codes can make a `skills list` search look empty.
- GitHub TLS handshakes sometimes fail. Retry; record the successful run.
- The collection-discovery test is a structure check on the source tree. It is
  not installation evidence.
