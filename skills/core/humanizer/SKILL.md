---
name: humanizer
description: |
  Rewrite AI-sounding text so it reads naturally without changing what it says.
  Use when editing or reviewing prose for inflated claims, sales language,
  vague sources, repetitive structure, stock AI words, passive voice, filler,
  or chatbot artifacts, or when tightening technical documentation, specs, SOPs,
  runbooks, and engineering explanations for unambiguous clarity. Works for
  English and Chinese text (去除中英文文本中的 AI 写作痕迹，或按简明技术规范改写技术文档).
---

# Humanizer: remove AI writing patterns and sharpen clarity

Rewrite AI-sounding text so it reads like a capable human writer rather than a chatbot. Keep every factual claim intact and never invent details.

## Language routing

Detect the language of the text before selecting reference rules:

- **English text:** apply the pattern catalog in [references/patterns.md](references/patterns.md).
- **Chinese text:** read [references/zh-adaptation.md](references/zh-adaptation.md) alongside [references/patterns.md](references/patterns.md). It overrides patterns that behave differently in Chinese (§14, §17, §19, §26), maps the remaining patterns to their Chinese manifestations, and supplies Chinese trigger vocabulary.
- **Mixed text:** route each language span to its matching rule set.

The core rewrite rules (keep every claim, never invent facts, match the voice and register) apply in every language.

## Register routing

Select the operating mode from the text's genre before rewriting:

- **General Mode (default):** Use for essays, blog posts, narratives, opinions, correspondence, product or general copy, and creative writing. Apply the AI-pattern catalog while keeping natural rhythm, fitting figurative language, and the writer's voice. Leave [references/technical-clarity.md](references/technical-clarity.md) unloaded so narrative prose is never forced into technical word-count caps or metaphor bans.
- **Technical / Clarity Mode:** Activate **only** when writing or editing technical documentation, specifications, ADRs, API or CLI references, SOPs, runbooks, or engineering explanations. Read and apply [references/technical-clarity.md](references/technical-clarity.md) alongside the AI-pattern catalog: ASD-STE100 principles for English and 简明技术中文 rules for Chinese.
- **Mixed-register documents:** Honor an explicit user mode choice first; otherwise route each distinct section by its register (for example, narrative framing in General Mode and an embedded runbook in Technical / Clarity Mode), defaulting borderline essays and blog posts to General Mode.

## What to do

When given text to humanize:

1. **Find AI patterns (and clarity defects in Technical / Clarity Mode).** Check the text against [references/patterns.md](references/patterns.md), plus [references/zh-adaptation.md](references/zh-adaptation.md) for Chinese and [references/technical-clarity.md](references/technical-clarity.md) when Register routing selects Technical / Clarity Mode.
2. **Keep every claim.** You may shorten dull parts, expand useful parts, and merge or split paragraphs. Preserve every fact, condition, threshold, unit, and logical constraint even when changing sentence structure.
3. **Do not invent facts.** Do not add a fact, name, number, date, quote, citation, command, or parameter unless it comes from the source or the user. If a sentence needs a missing detail, ask for it or write a simpler true statement. You may include an opinion or reaction when a personal voice calls for one, never an invented factual claim. Fiction is exempt because invented details are part of the task.
4. **Match the voice and register.** Fit the tone to the text, such as casual, formal, or strictly technical. Add personality only when the genre and writer call for it.

The input type controls what you return; see [How to return the result](#how-to-return-the-result).

## Match the writer's voice

If the user provides a writing sample (their own previous writing), analyze it before rewriting:

1. Read the sample first. Note its sentence length, word choice, paragraph openings, punctuation, repeated phrases, and transitions.
2. In General Mode, match those habits. Do not replace casual words with formal ones or strip deliberate quirks. If the sample uses dashes, keep them at about the same rate instead of applying §14 in [references/patterns.md](references/patterns.md) as a ban.
3. In Technical / Clarity Mode, terminology consistency and unambiguous structure govern unless the user explicitly asks to preserve specific house-style conventions from the sample.

## Add personality only when it fits

Removing AI patterns is only half the job in General Mode: the result should still sound like a person.

Use personality in blog posts, essays, opinions, and personal writing when it fits the writer, keeping opinions, uncertainty, mixed feelings, humor, asides, and uneven rhythm without inventing facts. Keep reference, technical, specification, legal, and factual text neutral: omit unprompted opinions and first-person commentary where they do not belong.

## Patterns

Read [references/patterns.md](references/patterns.md) before rewriting. It lists 35 numbered patterns across five groups (content, language and grammar, style, chatbot artifacts, and filler and hedging) plus false-positive checks covering what not to flag and which human details to keep. One pattern alone proves nothing; look for several together.

---

## How to return the result

**Pasted text (default).** Return the draft, a short list of remaining AI patterns (and clarity issues when in Technical / Clarity Mode), and the final rewrite.

**File mode.** When the user names a file, run the full rewrite process and write only the final text to the file. Change prose only: keep code blocks, YAML metadata, data literals, and link targets unchanged. Then give the user a short summary.

**Embedded mode.** When another task uses this skill for a pull request, commit message, specification, or document, return only the final text.

## Rewrite process

1. Identify the language and register (`General Mode` vs `Technical / Clarity Mode`), read the matching reference files, and mark each AI pattern or clarity defect in the source.
2. Write a draft and check its cadence, plain verbs such as *is* and *has*, and register fit. When in Technical / Clarity Mode, verify every rule in [references/technical-clarity.md](references/technical-clarity.md).
3. Audit the draft against two completion checks:
   - **"What still sounds AI-generated (or ambiguous, in Technical / Clarity Mode)?"**
   - **"Did the rewrite add, drop, or alter any fact, name, number, date, quote, citation, condition, ranking, or claim?"**
   Treat any unsupported addition or lost claim as an error and repair it.
4. Write the final version. State each point naturally instead of patching one flagged phrase at a time; if a sentence stays awkward, rewrite the paragraph around its main point. Apply the dash rule in §14 (or the paired-dash test in [references/zh-adaptation.md](references/zh-adaptation.md) for Chinese) unless a provided writing sample uses dashes.

Return the result required by [How to return the result](#how-to-return-the-result).

## Source

Pattern catalog adapted from [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup); see [ATTRIBUTION.md](ATTRIBUTION.md) for full upstream lineage and licensing.

Wikipedia's main point: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
