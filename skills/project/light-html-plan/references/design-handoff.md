# Optional design capability

Read this only when the user asks for a design other than the built-in visual system and a separate design capability, such as `huashu-design`, is available. Without that request, build from `assets/`.

## Division of work

`light-html-plan` owns the text, source fidelity and delivery. A design capability owns layout, colour, type and exhibit drawing. It receives settled text and does not rewrite, shorten or replace sentences. If a returned page changed a sentence, dropped a commitment or turned a sentence into labels, restore the text.

## Resolve it

1. Find the capability in the current session's Skill inventory or the Host's installation. Read its actual `SKILL.md` and only the relevant supporting file. Do not hardcode a maintainer's home path.
2. Confirm the Host can run it. A model-invoked capability may be composed. A user-invoked one needs the user's explicit approval for that exact target.
3. If it is missing or incompatible, build the page directly using [design-and-verification.md](design-and-verification.md) and say which capability was unavailable. Do not install anything.

## What to pass

| Input | Content |
| --- | --- |
| Purpose | Reader, the questions they must answer, current user design choices |
| Settled text | Title, status line, level-1/2/3 sentences, decisions — marked as final wording |
| Exhibits | For each sentence that has one: what it must prove and the source data it may use |
| Sources | Paths, record dates, SHA-256 |
| Delivery | Absolute output path; one offline HTML file; 1440px and 390px; light and dark; keyboard-usable |
| Limits | No approvals, feedback export, state writeback, external requests or invented data |

## After it returns

Diff the page text against the settled text. Then run the checks in [design-and-verification.md](design-and-verification.md#check). A refresh keeps the existing design and does not call the design capability.
