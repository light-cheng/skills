---
name: eli5
description: "Explain a topic, piece of code, concept or error so a named audience can follow it: a child, a grade level, a non-specialist adult, or someone in a given role or relationship. Use when the user says ELI5, \"explain like I'm …\", \"explain this to my …\", \"in plain words for …\", \"dumb it down\", \"simplify this for …\", or otherwise names who the explanation is for or asks for a non-technical explanation. Not for rewriting a document for its readers."
---

# ELI5

Turn something hard into an explanation that one specific listener can follow
and repeat. Accuracy comes first; simplicity is how you deliver it.

## How

1. **Name the listener.** Take the audience from the request ("my mum", "a
   ten-year-old", "our CFO"). A bare "ELI5" means a young child. Any other
   request with no listener named (such as "dumb it down") gets a curious adult
   with no background in the field; say so in one line. Match the profile in
   [audiences.md](references/audiences.md).
2. **Read before you explain.** When the request points at code, a file, a log
   or an error, open it first. Explain what is actually there, not what such
   things usually do. If you cannot see the material, ask for it; do not guess
   its contents.
3. **Find the one idea.** Write, for yourself, the single sentence the listener
   must leave with. Everything else supports that sentence or goes.
4. **Pick one anchor.** Choose one comparison from the listener's own world
   and keep using it. Do not switch analogies halfway.
5. **Build the answer:**
   - the one idea, in a sentence;
   - how it works, in three to five short steps that use the anchor;
   - why it matters to this listener;
   - where the comparison stops being true, in one sentence.
6. **Offer a next level.** End with one line that says what to ask for a
   deeper version. Do not write the deeper version unasked.

## Rules

- Answer in the language the user wrote in.
- Use a technical word only when the listener will meet it again; define it
  once, in plain words, the first time. A listener who works in the same field
  keeps the proper terms; simplifying those would talk down to them.
- Prefer concrete numbers and everyday objects to abstractions.
- Keep the length the profile suggests. A child gets a short answer; an
  executive gets the decision-relevant part first.
- Never trade truth for a cute picture. If the simple version would mislead,
  say what it leaves out.
- Speak to the listener's level, never down to them.

## Stop

Stop after the explanation and the next-level line. Do not rewrite the
user's material, fix the code, or start another task unless asked.
