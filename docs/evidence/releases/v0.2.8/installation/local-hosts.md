# Local fresh installs and Host discovery

Date: 2026-10-16. Machine: the maintainer's macOS computer. Skills CLI `1.7.2`. Each install ran in a new, empty Git project under `<tmp>`; no project contained the repository checkout. The source is the repository's new name `light-cheng/skills`; `skills-lock.json` records it. The same matrix was first run from the old name `LightDevCoder/skills` (which GitHub redirects) with identical results.

| Case | Command | Result |
| --- | --- | --- |
| Pinned whole | `npx --yes skills add light-cheng/skills#v0.2.8 --skill '*' --agent claude-code pi --copy --yes` | exit 0; `.claude/skills` and `.agents/skills` each hold 39 packages and 406 files, every file byte-identical to `refs/tags/v0.2.8` |
| Default whole | `npx --yes skills add light-cheng/skills --skill '*' --agent claude-code pi --copy --yes` | exit 0; both destinations 39 packages / 406 files, byte-identical to `origin/main` (`c522857`) |
| Renamed single | `npx --yes skills add light-cheng/skills#v0.2.8 --skill light-merge-conflicts --agent claude-code pi --copy --yes` | exit 0; exactly one package (3 files) in each destination, byte-identical to the tag |
| CLI listing | `npx --yes skills list` in the pinned project | 39 project Skills listed |
| Repeat install | the pinned command again | exit 0; reports `overwrites: Claude Code, Pi`, a no-op overwrite; bytes unchanged |

The byte comparison hashed every file under `skills/<category>/<name>/` in the Git tree and every installed file. `skills/docs/assets/` is a shared asset directory, not a package, and is correctly not installed.

## Host discovery

Both Hosts were asked, without tools, which of six named Skills they could see. Four of the six (`light-merge-conflicts`, `light-decide`, `light-redirect`, `light-html-plan`) exist only in v0.2.8 and in no global install on this machine, so seeing them proves project discovery.

| Host | Command | Answer |
| --- | --- | --- |
| Claude Code 2.1.296 | `claude -p "<prompt>" --output-format json` in the pinned project | `6:light-merge-conflicts,light-decide,light-redirect,light-html-plan,eli5,project-review` |
| pi 1.3.0 | `pi --approve -p "<prompt>"` in the pinned project | all six; `light-decide` loaded from `<tmp>/pinned/.agents/skills/light-decide/SKILL.md` |

Without `--approve`, pi print mode found only `eli5` and `project-review`, both from the user's global `~/.agents/skills`. pi loads project `.agents/skills` only after project trust, and print mode cannot ask for it. Interactive pi asks once per project, or the user saves a decision with `/trust`.

## Limits

- Codex is not installed on this machine, so no local Codex discovery was run. The hosted run covers Codex installation targets (project and native global), not Codex runtime.
- The checks prove installation and discovery, not behavior of each Skill.
