# Result contract

Return a compact, complete record:

```text
Mode: next | workflow | navigate | standalone

Status: RECOMMEND | NEED-INPUT | BLOCKED

Observed:
- <fact lines from the evidence packet and conversation>

Assessment: <what the project appears to be doing, what is finished,
what is unresolved, and why the recommendation fits now>

Skill: <one name, or none only when legitimately terminal / needs-input>
Scope: current-workflow | independent | standalone
Reason: <context-specific workflow reasoning, not a generic description>
Alternative: <at most one, with why it is not primary>
Source: first-party: <validated package path>
Invocation: <host-specific command>

Next: awaiting-approval | host-transition-required | beginning-<skill> | revalidation-blocked | no-execution
Reads: metadata=<count>; bodies=<count>; references=<count>
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

For `NEED-INPUT`/`BLOCKED` results keep the same shape, name no executable
Skill, and explain the gap. Never expose an empty `Skill:` inside a
`RECOMMEND` result. For a legitimately terminal current effort, return the
clean terminal record: `Skill: none`, `Completed` includes `acceptance
passed`, `Next: no-execution`.

