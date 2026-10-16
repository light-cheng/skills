# Setting up a decision source

Read this only when all three hold: no source within the data limit showed
evidence of availability, this judgment or the work ahead would clearly
benefit from one, and the user has not declined setup (see
[Remember a refusal](#remember-a-refusal)). Otherwise answer by
self-judgment and continue.

Setup is a side trip. Finish or pause the current judgment first: answer it
by self-judgment, log it, and return it to the caller. Then offer setup.

## 1. Look before asking

Collect evidence from this run. Do not ask the user for what you can see.

- MCP tools in this session whose names or descriptions offer typed
  decisions (choice, yes/no, score). Call a read-only status tool when one
  exists.
- The caller's script client: whether its library imports, and what
  `TYPESAFE_BASE_URL` points at. Check `/ready` when the endpoint is local.
- The user's policy file `~/.config/light/decision-policy.json`, when the Host
  lets you read it. A file is a hint, not evidence of availability.

When you find a working source, apply the data limit and the selection order
in [selection](selection.md). Setup ends there.

## 2. Ask the user

Say in one or two plain sentences what you checked and found nothing. Ask
whether they already run a decision model on this machine, on their own
network, or as a cloud service. Ask once. If they name one, go back to step 1
for that source only.

## 3. Recommend, only when asked or accepted

When the user has none and wants one, recommend by data limit:

- **Cloud API** (`third-party`): least work. It needs a key, and the
  project's `Decision data:` must allow `third-party`. Say plainly that the
  question state leaves the machine.
- **Local model** (`on-device`): recommend it only after you check this
  machine's memory, processor or GPU, and free disk with commands, and the
  model the user would run fits. Report what you measured. Never judge a
  machine by its name.

Name categories and the trade-off. Do not install anything.

## 4. Steps only a person can do

Getting a key, signing in to a dashboard, or approving a large download are
the user's steps. Offer `light-wizard` for them, by name. Call it only after
the user says yes. When it is unavailable or declined, give the steps as a
short numbered list.

## 5. Record the result

After the user approves, and only then:

- add or update the backend entry in the policy file (`names`, `data`; no
  `questions` until calibration), or give the user the JSON to paste when the
  Host cannot write there;
- tell the user which `Decision data:` line the project needs, and change
  `docs/agents/light-project.md` only with their approval.

Never write a key, URL or local model name into a skill or a repository.

## Remember a refusal

When the user declines setup, ask where to remember it: this project
(`Decision data: off` in `docs/agents/light-project.md`) or this machine
(`"setup": "declined"` at the top level of the policy file). Write it with
their approval. Do not offer setup again while that record stands.
