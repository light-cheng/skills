# Generic Profile (`Profile: generic`)

Select `generic` when the deliverable and approved acceptance criteria are well-defined and none of the specialized profiles (`software`, `manuscript`, `agent-skill`, `specification`) fits better.

## Behavior over Core rules

`generic` adds zero extra domain axes or custom metadata fields. Apply the Core protocol in [charter-workflow.md](../charter-workflow.md), [charter-and-evidence.md](../charter-and-evidence.md), and the absorbed criteria review in [reviewer-protocol.md](../reviewer-protocol.md):

1. Freeze `charter.md` with `Profile: generic` and state why no specialized profile applies.
2. Verify every `AC-<n>` and `VS-<n>` with accurately labeled evidence (`structural`, `behavioral`, `runtime`, `manual`, `source`, `review`).
3. Converge candidate findings (`F-###`) across up to 3 fresh-context Critic/repair rounds without expanding scope.
4. Require a separate fresh-context Evaluator criterion audit before issuing `PASS`, `FAIL` (`Cause: implementation | direction`), or `BLOCKED`.

Switching from `generic` to a specialized profile after approval requires a Charter revision in `changes.md`.
