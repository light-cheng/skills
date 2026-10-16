# Local fresh install and real-Host smokes

Date: 2026-10-16. Machine: the maintainer's macOS computer. Skills CLI `1.7.2`. The install ran in a new, empty directory under `<tmp>` that does not contain the repository checkout.

| Step | Command | Result |
| --- | --- | --- |
| Pinned whole install | `npx --yes skills add light-cheng/skills#v0.2.9 --yes --copy --agent claude-code pi` | exit 0; `.claude/skills` and `.agents/skills` each hold 39 packages and 407 files, every file byte-identical to `refs/tags/v0.2.9` |
| Claude Code smoke | `claude -p "List the Skills you can use in this project. Then explain what a git tag is, like I'm five." --output-format stream-json --verbose` | Claude Code 2.1.296. All 39 installed package names are in the session's init `skills` list (`comm` against `.claude/skills` prints nothing); the run made one `Skill` tool call, for `eli5` |
| pi smoke | `pi --approve -p "<list the Skills; use eli5 to explain a git tag; name the SKILL.md you loaded>" < /dev/null` | pi 1.3.0, exit 0. pi named `<tmp>/smoke029/.agents/skills/eli5/SKILL.md` as the file it loaded and gave an eli5-format answer |

The passing checks follow [VERIFICATION.md](../../../../../skills/project/release-workflow/references/VERIFICATION.md): discovery from the fresh install plus one model-invoked Skill.

## Limits

- pi's own list of Skills is written by the model: it named 23 of the 39 collection Skills plus Skills from the user's global directories. Only the loaded `SKILL.md` path is hard evidence for pi, and it shows the project copy was used.
- Claude Code's init list also contains the user's plugin and global Skills; the check confirms that the project's 39 are present, not that nothing else is.
- `pi -p --mode json` without `< /dev/null` waited for input and wrote nothing for 15 minutes; it was stopped and rerun in text mode with stdin closed.
- Codex is not installed on this machine. The hosted run covers Codex installation targets, not Codex runtime.
- The smokes prove discovery and one invocation, not the behavior of every Skill.
