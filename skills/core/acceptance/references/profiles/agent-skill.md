# Agent-Skill Profile (`Profile: agent-skill`)

Select `agent-skill` when accepting an installable Agent Skill package: a directory containing `SKILL.md`, `agents/openai.yaml`, and optional `references/`, `scripts/`, `assets/`, or `tests/`.

## Review axes

Audit every applicable axis independently and tag each `F-###` finding with its axis:

1. **Package structure and discoverability:** valid strict YAML frontmatter in `SKILL.md` (`name` matching directory basename, crisp `description`), synchronized `agents/openai.yaml` (`policy.allow_implicit_invocation` matching `disable-model-invocation`), progressive disclosure that keeps `SKILL.md` focused, and zero broken relative links.
2. **Clean installation and discovery:** installing or linking only the declared skill directory (and plugin manifest when applicable) succeeds cleanly without relying on undeclared parent files or stale `.scratch/` runtime state.
3. **Invocation contract and authority boundaries:** user-invoked (`disable-model-invocation: true`) vs model-invoked behavior matches design; trigger branches are distinct; the skill recommends user-invoked peer skills rather than silently executing them; subagent dispatches require a **fresh context window**.
4. **Method fidelity and Graceful fallback:** positive, boundary/no-op, and failure/missing-dependency scenarios exercise the skill's repeatable method; every cross-collection reference (`code-review`, `research`, `writing-for-agents`, `wizard`) or optional companion MCP (`light-decision-mcp`, `agent-config`) includes a self-contained **Graceful fallback**.
5. **Target-repository hygiene and prose invariants:** runtime artifacts written into user repos stay under `.scratch/`; upstream attribution files (`ATTRIBUTION.md` / `LICENSE`) remain intact where required; newly authored English prose contains zero em-dashes.
6. **Executable artifact quality:** when the skill ships executable scripts (`scripts/`), focused assertion-bearing positive and negative tests pass, and `code-review` (or the built-in two-axis diff fallback in [reviewer-protocol.md](../reviewer-protocol.md)) audits `Standards` and `Spec` on the script changes. Packages with zero executable scripts record `Not applicable - pure markdown skill` in `producer-evidence.md`.

## Evidence requirements and failure stops

Required labeled evidence ([charter-and-evidence.md](../charter-and-evidence.md)):
- `source`: frozen target package path, git revision, and originating spec/ticket.
- `structural`: strict frontmatter/YAML/link validator output (for example `check-frontmatter.mjs`) and prose/attribution checks.
- `installation`: clean link, copy, or `claude plugin validate` observation.
- `invocation` and `behavioral`: observed positive trigger, non-trigger boundary, and missing-dependency Graceful fallback trace; for packages with `scripts/`, executed `pytest` / test runner output with non-zero assertions.
- `review`: fresh-context Critic report (plus `code-review` / fallback report when executables exist) and separate fresh-context Evaluator report.

Severity follows Core impact tiers (`Critical`: unsafe execution, secret leak, or destructive host mutation; `High`: broken install/validation, invocation policy desync, missing Graceful fallback, or untested scripts; `Medium`: vague completion criteria, sprawl/duplication, or broken edge case; `Low`: minor wording note). Return `FAIL` (`Cause: direction` -> `redirect`) if fixing the package requires changing its approved invocation model, plugin bucket, or dependency contract.
