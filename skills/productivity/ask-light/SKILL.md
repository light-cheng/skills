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

## How it works

Code establishes facts; the model judges; code validates the choice.
`scripts/ask_light.py` (Python 3.9+) returns an evidence packet and never
names a Skill. Patterns in
[light-skill-map.json](references/light-skill-map.json) are candidate hints
only. Full evidence, validation and approval protocol:
[discovery-contract.md](references/discovery-contract.md).

## Session flow

1. **Interpret the request.** Decide the situation: current workflow,
   explicit task or named Skill, new effort, standalone task, workflow
   overview, or collection navigation. It decides which evidence binds.
2. **Collect evidence.** Run
   `python3 scripts/ask_light.py --mode next --context-json '{"projectRoot": "..."}'`
   (add `--roots-json` when the collection root is known). Shortlist from the
   catalog in the packet; never read every SKILL.md to route.
3. **Understand candidates.** Pick 2–4 plausible Skills. Read their
   `SKILL.md` when neighbors are materially close.
4. **Judge.** Read [routing-judgment.md](references/routing-judgment.md),
   then pick **one** primary Skill and at most one alternative. Never invent
   state the packet contradicts.
5. **Validate.** Run
   `python3 scripts/ask_light.py --mode validate --skill <name> --scope <scope>`
   ([scopes](references/routing-judgment.md#scopes-for-validation)).
   On `BLOCKED`, report the logical recommendation and the reason, and stop.
   Never substitute another Skill.
6. **Explain like an advisor.** Cite observed facts: why this Skill fits now
   and why the obvious neighbor does not
   ([routing-judgment.md](references/routing-judgment.md#explaining-the-recommendation)).
7. **Wait for approval.** Execute nothing before the user explicitly agrees.
8. **Transition.** Revalidate, then start the accepted Skill only as its
   invocation type and the Host's verified capability allow. Otherwise render
   the exact invocation and stop. Never chain past the accepted Skill
   ([modes-and-transition.md](references/modes-and-transition.md)).

## Modes

- `$ask-light next` — one next-Skill recommendation with workflow reasoning.
- `$ask-light workflow` — one bounded workflow recipe anchored at current state.
- `$ask-light <category>` — browse the collection (e.g. `project Skills`, `review Skills`, `learning Skills`) and explain roles and neighbors.
- Plain standalone requests (`Explain this like I'm five`, `Investigate this bug`) route without deep project inspection.

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
