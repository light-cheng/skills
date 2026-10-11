# Modes and approval transition

## Workflow mode (`$ask-light workflow`)

Model-led: inspect the current context, read the helper's recipe catalog
(`--mode workflow` publishes every canonical recipe with step availability,
handoff contracts, `entryCondition`, `stoppingBoundary`, `finalAuthority`,
and per-step `missing dependency` fields), select the relevant workflow
semantically, anchor the entry point at the user's actual current state, and
explain the relevant remaining flow from there. A project with an accepted
SPEC must not be shown the full chain from `project-init`; show the remaining
flow from the current state and preserve each Skill's stopping boundary.

## Navigation mode (`$ask-light <category>`)

Collection browsing, family listings, and exact named comparisons (for
example `clarify vs project-clarify`) may resolve deterministically from the
map taxonomy; the explanation is model-generated. No need to make
deterministic list operations probabilistic.

## Approval transition

After explicit approval:

1. **Revalidate before transition.** Re-run `--mode validate` for the
   accepted Skill and recheck material hard project state (fresh evidence for
   current-project recommendations). If the recommendation became stale, do
   not execute stale advice: recompute or explain the changed state.
2. **Transition per the host's actual capability:**
   - a **model-invoked** accepted Skill may begin in the current conversation
     where the host supports that;
   - a **user-invoked** accepted Skill begins itself only where the host
     verifiably permits an explicit approved transition — the user's explicit
     approval may constitute the required authorization there. Otherwise
     render the exact invocation (`$<skill>` on Codex, `/<skill>` on Claude
     Code) and ask the user to start it.
   - Do not fake execution, do not assume every host supports recursive Skill
     invocation, and do not claim a transition is impossible merely because
     the target normally requires explicit user invocation — check the
     actual host capability and document the tested behavior. Repository
     policy forbids a user-invoked Skill from auto-invoking another
     user-invoked Skill without that verified capability.

## Safety and stop

Before approval the recommendation phase is read-only: nothing is invoked,
installed, or orchestrated (`recommendation phase was read-only`). After
approval: for a model-invoked accepted Skill, begin it where the host
supports that; for a user-invoked accepted Skill without a verified
approved-transition capability, render the exact invocation and do not fake
execution. Follow the accepted Skill's stop condition once it actually
starts. Do not auto-chain past the accepted Skill; that Skill decides its own
handoff.

