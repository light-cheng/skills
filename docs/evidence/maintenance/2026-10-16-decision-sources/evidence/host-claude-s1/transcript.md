<!-- skill tree: see commits up to 8317357; prompts are in the scenario list in review/evaluator-verdict.md -->
## turn 1  session 9b97785d-e356-40d7-a6dc-bffb5ff4ec20  model ['claude-opus-5-5']
**Answer: `html`.** The readers are non-engineers reading in an email client, and email clients render HTML but show Markdown as raw text, with the `#`, `*` and `[]()` symbols visible.

This was my own judgment, not a decision model's. A local endpoint is configured at `127.0.0.1:8001`, but its `/ready` check returned an empty reply, so it didn't count as available. There's also no `~/.config/light/decision-policy.json`, so no source is calibrated for this question yet.

```yaml
question_id: weekly-note/format
question: Should this week's status note be written as Markdown or HTML, given readers are non-engineers who open it in email?
kind: choice
options: [markdown, html]
answer: html
score: null
probabilities: {}
confidence: null
provider_confidence: null
method: self-judgment
data: in-session
backend: agent
calibrated: false
applied: true
fallback_reason: unavailable
final: html
```

**Not logged:** the log goes in `.scratch/weekly-note/decisions.md`, but `.scratch/` doesn't exist and the skill isn't allowed to create it. Here's the row to add if you want it kept:

```markdown
| time | question_id | question | kind | answer | confidence | method | data | backend | applied | reason | final |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-15T16:39:40Z | weekly-note/format | Should this week's status note be written as Markdown or HTML, given readers are non-engineers who open it in email? | choice | html | - | self-judgment | in-session | agent | true | unavailable | html |
```
## turn 2  session 9b97785d-e356-40d7-a6dc-bffb5ff4ec20  model ['claude-opus-5-5']
**Answer: `no`.** Non-engineers get more from two or three key numbers written into the text than from a raw metrics table. You could link the full table for anyone who wants it.

This was my own judgment again. The endpoint at `127.0.0.1:8001` refused the connection this time (HTTP 000).

```yaml
question_id: weekly-note/include-metrics
question: Should this week's note include the raw metrics table, given readers are non-engineers?
kind: yes_no
options: [yes, no]
answer: no
score: null
probabilities: {}
confidence: null
provider_confidence: null
method: self-judgment
data: in-session
backend: agent
calibrated: false
applied: true
fallback_reason: unavailable
final: no
```

**Not logged:** `.scratch/weekly-note/` still doesn't exist. Here's the row to add:

```markdown
| 2026-10-15T16:40:28Z | weekly-note/include-metrics | Should this week's note include the raw metrics table, given readers are non-engineers? | yes_no | no | - | self-judgment | in-session | agent | true | unavailable | no |
```

**Setting up a decision source:** you'll hit dozens of these a week, so a working source would help. Here's what I checked:
- No decision tools are available in this session.
- `TYPESAFE_BASE_URL` points to a local endpoint at `127.0.0.1:8001`, but nothing is answering there.
- There's no decision policy file at `~/.config/light/decision-policy.json`.

Do you already run a decision model on this machine, on your own network, or as a cloud service? If you do, I'll check that one. If not, I can recommend options, but nothing gets installed or changed without your OK.

Two other things are worth knowing:
- **Allowed data limit:** your project file has no `Decision data:` line, so only on-device sources count. A cloud service would need that line added.
- **Calibration:** a source that's answering still isn't trusted until it's calibrated for each question. Until then I'd only record its answer next to my own. Calibration means checking its answers against cases you've labeled.

If you'd rather not set this up, say so. I'll record that so I don't ask again.
## turn 3  session 9b97785d-e356-40d7-a6dc-bffb5ff4ec20  model ['claude-opus-5-5']
Got it, no setup. Future judgments like these will be my own, logged the same way.

Where should I record that so I don't offer setup again?

- **This project only:** I'd add `Decision data: off` to `docs/agents/light-project.md`. That also blocks any decision source in this project, even one you set up later, until you remove the line.
- **This whole machine:** I'd add `"setup": "declined"` to `~/.config/light/decision-policy.json`. That stops the setup offer in every project. Decision sources stay allowed wherever a project permits them.

Which one do you want? I won't write either until you choose.
## turn 4  session 9b97785d-e356-40d7-a6dc-bffb5ff4ec20  model ['claude-opus-5-5']
I added `Decision data: off` to `docs/agents/light-project.md`, so I won't offer setup again in this project. I haven't committed the change.

From now on, judgments here will be my own and will be recorded with reason `off`. The setup offer comes back only if you remove that line.

Decision rows will keep coming back to you in the reply, because `.scratch/weekly-note/` doesn't exist and I'm not allowed to create it. If you create that folder, I'll write the rows to `decisions.md` there myself.
## turn 5  session 000dea25-63c1-49a7-95dc-d330f2d4aeab  model ['claude-opus-5-5']
**I chose `formal`.** The note goes to the whole department, so many readers outside the team will see it, including people at different levels. A formal tone keeps it clear and suitable for all of them.

- **How it was decided:** `docs/agents/light-project.md` has `Decision data: off`, so no decision source was asked. This is my own judgment, and the reason is logged as `off`.
- **Not logged to a file:** `.scratch/weekly-note/` doesn't exist, and the skill must not create it. Here is the row so you can record it:

```markdown
| time | question_id | question | kind | answer | confidence | method | data | backend | applied | reason | final |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-15T16:41:38Z | weekly-note/tone | Should the team status note for the whole department be formal or casual? | choice | formal | - | self-judgment | in-session | agent | true | off | formal |
```
