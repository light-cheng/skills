---
name: ask-light
description: Act as the Light workflow advisor, navigator, and router. Understand what the user is trying to do, inspect the actual project/host evidence and Skill catalog, reason about the best next Light Skill, explain why, wait for user approval, then honor the accepted Skill's invocation policy with host-aware transition. Also answer collection-navigation and standalone routing requests. Use only when the user explicitly invokes $ask-light; never execute before consent.
disable-model-invocation: true
---

# Ask Light

`ask-light` is the **Light workflow advisor, navigator, and router** — a
user-invoked entry that understands what the user is trying to do, inspects
the actual project state, knows the Light Skills and their contracts, reasons
about the best next action, explains why, waits for approval, and transitions
into the accepted Skill where the host permits.

## Architecture

Five stages, with an explicit ownership boundary:

1. **Request interpretation** — MODEL: what is the user asking, and at what
   scope (current workflow, independent task, new effort, standalone)?
2. **Project/host evidence collection** — CODE (`ask_light.py`): repository
   facts, effort resolution, SPEC/ticket/review state, Skill catalog.
3. **Candidate Skill understanding** — MODEL + catalog metadata.
4. **Final workflow judgment** — MODEL: choose one primary Skill, justify it.
5. **Selection validation / transition** — CODE + host capability.

Python is the evidence/validation authority, **not** the semantic
recommendation authority. It never names a recommended Skill; the evidence
packet returns facts plus scoped hard constraints. Regex patterns,
`taskKindRoutes`, and pattern scores in
[light-skill-map.json](references/light-skill-map.json) are candidate hints
only — they are never the final selector, and no language needs its own
routing rules: the model handles multilingual understanding. Full discovery,
evidence, and approval protocol:
[discovery-contract.md](references/discovery-contract.md).

## Session flow

1. **Interpret the request.** Determine internally (this is not a new public
   command) which situation this is, because it decides what evidence binds:
   - *current workflow* — “what should I do next?” / “这个项目下一步做什么？”;
     project state constrains the answer.
   - *explicit task or named Skill* — an independent request (review this
     diff, ELI5 this diagram); current-effort state must not hijack it.
   - *new effort inside an existing project* — new work, routed by its own
     maturity, even when the current effort is accepted.
   - *standalone task* — no project workflow involvement required.
   - *workflow overview* — `$ask-light workflow`.
   - *collection navigation* — `$ask-light <category>` or a comparison query.
2. **Collect evidence.** Run
   `python3 scripts/ask_light.py --mode next --context-json '{"projectRoot": "..."}'`
   (use `--roots-json` when the collection root is known). Read the evidence
   packet: stage, project contract, current effort, SPEC, ticket frontier,
   durable review state, artifact signals, hard constraints, and the compact
   Skill catalog. Never read every SKILL.md file to route — shortlist from
   the catalog first.
3. **Understand candidates.** Identify 2–4 plausible Skills from catalog
   metadata. When neighboring Skills are materially close, read their
   `SKILL.md` contracts before selecting. Read only relevant references when
   needed.
4. **Judge.** Compare candidate preconditions against the evidence and the
   current conversation. Pick **one** primary Skill; keep at most one
   meaningful alternative. Hard evidence overrides imagination: never invent
   state contrary to the packet (no SPEC claimed when `spec.exists` is false,
   no acceptance claimed when review freshness is stale or unknown, no
   execution claimed for an unavailable Skill).
5. **Validate the selection.** Run
   `python3 scripts/ask_light.py --mode validate --skill <name> --scope <scope>`
   with the same project root. Scope: `current-workflow` for current-workflow
   recommendations (hard constraints bind), `independent` for explicit
   independent tasks and new efforts, `standalone` for standalone requests.
   On `BLOCKED`, report the logical recommendation with the validator's
   reason and stop — never substitute another Skill. Only after validation
   passes does the user-visible result become `Status: RECOMMEND`, and a
   `RECOMMEND` result always carries a real Skill unless the project is
   legitimately terminal.
6. **Explain like an advisor.** For current-project questions answer: what
   does this project appear to be doing; where is the current effort; what
   is already finished; what is actually unresolved; why does the recommended
   Skill fit **now**; why is the most obvious neighboring Skill premature or
   unnecessary. Cite the actual observed facts. Never present generic
   “Light Skill Map matched pattern …” as the user-facing reason.
7. **Wait for approval.** Do not execute before the user explicitly agrees
   (`yes`, `可以`, `go ahead`, `do it`, `用这个`).
8. **Honor the host invocation policy after approval.** Revalidate first
   (below), then transition per the accepted Skill's invocation type and the
   host's actual capability.

## Decision principles and evidence

Before choosing, read [references/routing-judgment.md](references/routing-judgment.md). It holds the situation → Skill guide, the boundary cases that matter most (clarify vs spec, ticket frontier, active review, `light-implement` vs `agent-config`), and how to read hard constraints, conversation evidence, clarification handoffs, research artifacts and review state.

## Modes

- `$ask-light next` — one next-Skill recommendation with workflow reasoning.
- `$ask-light workflow` — one bounded workflow recipe anchored at current state.
- `$ask-light <category>` — browse the collection (e.g. `project Skills`, `review Skills`, `learning Skills`) and explain roles and neighbors.
- Plain standalone requests (`Explain this like I'm five`, `Investigate this bug`) route without deep project inspection.

## Approval transition and safety

Before approval, the recommendation phase is read-only: nothing is invoked,
installed or orchestrated. After the
user approves, revalidate, then start the accepted Skill only as its
invocation type and the Host's verified capability allow. Otherwise render the
exact invocation and stop. Do not chain past the accepted Skill. Details,
including workflow and navigation modes:
[modes-and-transition.md](references/modes-and-transition.md).

## Result contract

Return the record in [result-contract.md](references/result-contract.md).

## Optional capabilities

- **Several legal Skills remain, or ambiguity or escalation is in question**
  → the semantic mode (`--mode semantic`) asks through the light-decide script
  path; when you judge without the script, call `light-decide` with question
  ids `ask-light/next-action`, `ask-light/material-ambiguity` or
  `ask-light/reasoning-escalation`. It asks only within the project's
  `Decision data:` limit and applies an answer only when the user's policy file
  calibrates that question. Log the returned `decisions` with light-decide's
  log format. Unavailable or uncalibrated → keep the deterministic baseline. A
  judgment never grants transition authority; only the user's approval does.
