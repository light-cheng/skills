# Attribution and ownership boundary

This package's Light instructions and source/authority protocol were independently written for the collection. It is a first-party package admitted on 2026-10-11; it is not an approved Port.

- Primary reference: [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community), fixed revision `f60f0454df3045f724c43c6346ec80bdcc3472b2` (read on 2026-10-08).
- Primary paths: [`html-plan/skills/html-plan/SKILL.md`](https://github.com/anthropics/claude-plugins-community/blob/f60f0454df3045f724c43c6346ec80bdcc3472b2/html-plan/skills/html-plan/SKILL.md), [`references/blocks.md`](https://github.com/anthropics/claude-plugins-community/blob/f60f0454df3045f724c43c6346ec80bdcc3472b2/html-plan/skills/html-plan/references/blocks.md), [`examples/scheduled-send.html`](https://github.com/anthropics/claude-plugins-community/blob/f60f0454df3045f724c43c6346ec80bdcc3472b2/html-plan/skills/html-plan/examples/scheduled-send.html). The example was actually rendered and inspected. Runtime claim-tree/CSS excerpts informed the comparison; no runtime is reused.
- Primary licenses at the pinned revision (checked 2026-10-11): the repository root `LICENSE` is Apache-2.0; the `html-plan` plugin manifest (`html-plan/.claude-plugin/plugin.json`) declares `MIT`, author Thariq Shihipar. The pinned tree contains no `NOTICE` file, so no NOTICE text applies. This package copies no upstream runtime, component markup, CSS or executable code. Apache/MIT here and the auxiliary MIT reference below are distinct sources.
- Preserved primary ideas: level-1/level-2 claims are true-or-false sentences and the closed tree is the summary; one exhibit per claim; review questions → observable behaviour/testable guarantee → concrete exhibit → mechanism/source drill-down → question beside the claim it changes. The independently written Light guidance avoids copying fixed English word/count limits, component APIs, feedback/Respond export or execution chaining.
- Auxiliary reference repository: [plannotator/effective-html](https://github.com/plannotator/effective-html). It is a separate implementation, not a substitute for the primary reference above.
- Fixed reference revision: `2ac1dfecb0f2474e75260cb6d3c9b9d6d9b5062e` (read again on 2026-10-07).
- Reference paths: [`skills/html-plan/SKILL.md`](https://github.com/plannotator/effective-html/blob/2ac1dfecb0f2474e75260cb6d3c9b9d6d9b5062e/skills/html-plan/SKILL.md) and [`skills/design-artifact/SKILL.md`](https://github.com/plannotator/effective-html/blob/2ac1dfecb0f2474e75260cb6d3c9b9d6d9b5062e/skills/design-artifact/SKILL.md).
- Auxiliary license: MIT, `Copyright (c) 2026 plannotator`; its notice is retained below.
- Preserved principles: read before design; organize real work; preserve commitments; avoid invented metrics; choose tables/flows for real relationships; separate decisions and uncertainty; deliver accessible single-file HTML; inspect real outputs.
- Independent Light behavior: generation-time source identity, a pre/post commitment map, source-versus-snapshot authority, project-owner handback, standalone operation, intent-bounded model invocation, recorded progress from ticket or non-ticket inputs, caller-triggered refresh of a stable entry with exact-byte history, and honest verification limitations.
- No upstream instructions, HTML/CSS, assets, or code were copied into this package. Reference principles were expressed in new instructions. No `html`, `html-plan`, or `design-artifact` runtime install is required. Admission evidence, including reference snapshots and hashes, is recorded with the collection's admission evidence, not inside this package.
- Upstream direct-invocation restrictions and publication/`tot` workflow were not adopted. Light's model-invoked choice is explicit and its output stops at local review delivery.

## External design capability

The user approved composition with the separately available `huashu-design` Skill on 2026-10-08. On 2026-10-10 it became optional: the page text is written and settled first, and a design capability may only choose layout, colour, type and exhibit drawing; it does not rewrite sentences. It is not a first-party package or an approved Port in this collection. No huashu-design instructions, assets or implementation are vendored here, and the capability is neither installed nor modified by this package.

## Writing-rule correction (2026-10-10)

An earlier draft told authors to name sections by topic ("经历说明"), which contradicted the primary reference's rule that level-1 and level-2 claims are sentences that can be true or false and that the level-1 claims read aloud tell the whole change. The package now follows that rule and adds `references/writing.md` with before/after examples drawn from a real resume-website review page.

## Fixed page parts and project records (2026-10-10)

At the collection owner's decision, the page now has five fixed parts in a fixed order (what the project is, how far it got, what waits on the user, what changed since approval, what the system judged). The primary reference has no fixed section template; its claim rule now applies inside each part. The package also reads Light change proposals (`changes/`), the judgment log (`decisions.md`), implementation reports and review verdicts, and uses `.scratch/<feature>/plan.html` with `plan-history/` in a Light project. These are Light changes, not upstream behaviour.

## Built-in visual system (2026-10-10)

`assets/plan.css` and `assets/skeleton.html` were written for this collection and approved by the collection owner after reviewing prototypes. They copy no upstream CSS, markup or runtime. A separate design capability is now optional and used only when the user asks for a different design.

## Retained auxiliary reference notice

MIT License

Copyright (c) 2026 plannotator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
