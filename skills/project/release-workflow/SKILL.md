---
name: release-workflow
description: Prepare, verify and attest a first-party Skills release, or audit an existing tag and its installation evidence. Use for a new release, fresh-install verification or release-evidence closeout; execute only the requested stages and authorized targets.
---

# Skills Collection Release Workflow

Run the requested release stages with immutable source identity and observed
verification facts. A local candidate, remote CI, installed source, publication
and final attestation are distinct results.

## Scope and authority

Resolve the repository, target version, requested stages and current baseline.
For an existing tag audit use historical mode; a new release uses current mode.
A fresh-install-only request does not authorize creating a tag or publishing.

Prepare and review the local candidate before asking for any missing publication
authority. Before the first remote write, name the exact candidate, tag, package
count and actions. Reuse already explicit authority within that scope; changed
targets need a new decision. Never push, tag, publish, install globally or change
Host configuration outside the authorized task.

## Artifacts and document state

- Manifest freezes preparation-time scope, source identity and local evidence.
- Notes and public snapshot pages describe this version's content without
  freezing claims that another version is currently stable or this one unpublished.
- Receipt is first created on main after publication and records observed facts.
  Do not prefill it or place it in the candidate/tag.

Read [DOCUMENT-STATE.md](references/DOCUMENT-STATE.md) for current-stable authority,
bilingual surfaces, snapshot/Release-body semantics, observation inputs and
historical compatibility. File existence and matching link text do not establish
correct version or publication state.

## Execute the selected stages

```text
PREPARED → CI_VERIFIED → TAGGED → INSTALL_VERIFIED → PUBLISHED → ATTESTED
```

Read [RELEASE-STAGES.md](references/RELEASE-STAGES.md) for stage procedures and
[VERIFICATION.md](references/VERIFICATION.md) for actual released-source installs.
Run the common integrity gate on each relevant fixed tree and stage. Recorded CI
must identify the exact commit, be completed and successful. Tag protection,
annotated object/peel identity and complete install manifests remain required.

Prepare the Release body with the semantic-aware renderer, then check the actual
published body and navigation. Only observed installation/publication evidence
permits success claims. Local external-fact substitutes require explicit
`--simulate` and remain `SIMULATED_PASS`, never production PASS.

## Closeout

Follow [CLOSEOUT.md](references/CLOSEOUT.md): complete one coherent repair per
stage, verify the final staged Git tree and its clean export, and require exact
candidate/final-main CI for an authorized publication. Candidate and receipt
remain separate commits. Preserve failed attempts and immutable history.

The final main CI observation stays outside its own receipt; do not create a
self-reference commit loop. Report the candidate and final identities, actual
checks, installation/publication results and unresolved gates. A published
Release or successful push alone does not complete the task.
