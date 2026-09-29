---
id: OPR.99.0.3
mission: website-redesign-2
stage: wip
created: 2026-09-29
intent: "Replace the rejected zero landing-page visual world with a premium, truthful, responsive site informed by ten inspected references"
depends_on: []
---

# Mission: replace the rejected website design

## Why

The owner saw the deployed page and said, "you can tell this entire design is trash." This is explicit aesthetic rejection, notwithstanding functional and accessibility QA passing. The live yellow/navy departure-board system, oversized all-caps headings, black sorting table, and broad empty color fields are an **anti-reference**, not a palette or composition to preserve. The owner requested `/impeccable`, Claude Opus 5.5 in the design seat, and ten references from sites of Linear.app-level craft. Do not simply add polish, imitate Linear, or retain the rejected system by default.

## Outcome and boundaries

- Design lead `design-lead@zero` (verify model `claude-opus-5-5`) researches ten real, inspectable high-quality websites, records URLs and dated visual evidence, and produces replacement visual direction with viewable desktop/mobile comps and a specific product narrative. Use `/impeccable` replacement-world method and make an owner-facing visual decision before production code.
- Product truth comes from `PRODUCT.md`, the actual application, installer and `landing/` implementation. Keep honest claims about inbox sorting, errors, archive/recovery, permissions, requirements and pricing, plus accessible, discoverable install and legal paths. The copy and layout may change to serve the new world. The actual zero app image is a real asset, not license to fabricate functionality.
- Existing `landing/DESIGN.md` describes the now-rejected direction. Replace it after the owner selects a new visual world, not before. Current production remains as is while designing. Do not roll back or deploy without an explicit decision at the relevant gate.
- Preserve required functionality, semantic HTML, responsive layout, reduced motion and no-JS states. Motion and Canvas should serve the new art direction, not dictate it. Avoid large empty theatrical sections, filler animations, fake inbox activity and stock SaaS icon grids.
- **Replace, do not layer.** The owner explicitly wants the redesign to replace all old landing-page code rather than pile a new visual layer over it. After direction approval, rebuild the page's HTML, CSS and JS around the chosen system, remove obsolete departure-board components, animation/Canvas logic, selectors, styles, tests and unused image assets, and rewrite the design document. Retain only code/assets that the new implementation actually uses. Keep the necessary nginx/Docker routes, install/legal behavior, app source and history intact. Show a before/after source inventory and prove there are no dead legacy hooks or duplicate systems in the shipped `landing/` tree.

## Sequence and gates

1. [Research and design direction](slices/01-research-direction/SPEC.md): Opus 5.5 design lead. Ten verified references, critique of existing live page, multiple distinct replacement directions, compelling desktop/mobile visual comps. Owner selects before build.
2. [Implementation](slices/02-implementation/SPEC.md): builder, after owner direction approval. Only then modify `landing/` and durable `DESIGN.md`.
3. [Independent QA](slices/03-independent-qa/SPEC.md): compare rendered candidate to chosen comps, test desktop/mobile, fallback, install/legal, keyboard, performance and content truth.
4. [Release](slices/04-release/SPEC.md): owner-authorized scoped production release after QA PASS and live browser check, with rollback available.

## Owner decision, 2026-09-29 03:49Z

The owner chose **B, One-bit desktop**, after viewing Opus 5.5's desktop/mobile comps and the ten-reference atlas: "I think i like B, let's not overcomplicate the pages copy though, or overall clutter it too much, but yeah whatever you done here me likey". This authorizes the *build* of B, not a production release. Keep the existing plainspoken headline and factual copy by default; make only small edits needed for clarity and do not add another elaborate copy deck. Treat the one-bit Mac desktop as a disciplined visual system, not permission to fill the page with Finder chrome, repeated folders, dither everywhere or decorative UI. The real app remains the only colour and primary proof. One dated-folder recovery moment and a restrained empty-Trash cue are enough. Cut anything that competes with the promise, the app or install.

The user also asked that kernel know about this reference-led design process; the mission lead will relay the proof and practical lessons to the kernel seats. **No deployment of this replacement is authorized yet.** Current production remains the prior motion site until a separately checked release.
