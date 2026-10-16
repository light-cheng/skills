# light-travelpage AI connection review (v0.2.8)

[中文记录](README.zh-CN.md)

The optional assistant moved from a CPA-specific setup to any OpenAI- or Anthropic-format API, with the model chosen by the page owner at deployment (`scripts/ai-setup.mjs`).

- Review: software Profile. Critic (7 findings) and `light-code-review` (8 findings) — all fixed, among them a key echo in the hidden prompt, setup on pages older than v0.2.8, and mixed `AI_*`/`OPENAI_*` settings. A fresh Evaluator found the eight acceptance criteria met. Verdict: **PASS** (implementation commit `4c99626`).
- Tests: template suite 88/88, setup and generator tests 15/15, repository suite 586, local Wrangler Functions + D1 against a synthetic upstream — all on Node 26.7.0.
- Real service (with the owner's approval, through the owner's own OpenAI- and Anthropic-format gateway): the setup script got a real tool call back in `openai-chat`, `openai-responses` and `anthropic-messages`. In local Wrangler Functions + D1, each format saved one real tool-created task; an identical retry and the switched-off page made no further model call.
- Model selection against the same gateway: automatic detection from the model list completed a real round trip. With the model list made unavailable, the setup asked for `--model`, and a typed model ID completed a real round trip in each of the three formats. A typed model the service does not have failed at the round trip and left the earlier settings unchanged. The interactive terminal picker was not run against the real service (the package's tests cover it).

Limits: the gateway listed its models in the OpenAI shape although it also serves the Anthropic format, so the owner passes `--format anthropic-messages`. One `openai-chat` run took 34 seconds for its first reply and once exceeded the 55-second plan budget; that request failed safely with nothing saved, and the rerun passed. CI's Node 22 was not run locally. Keys, the gateway address and model names are left out of this record.
