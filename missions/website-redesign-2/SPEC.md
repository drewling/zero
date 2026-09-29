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

## Sequence and gates

1. [Research and design direction](slices/01-research-direction/SPEC.md): Opus 5.5 design lead. Ten verified references, critique of existing live page, multiple distinct replacement directions, compelling desktop/mobile visual comps. Owner selects before build.
2. [Implementation](slices/02-implementation/SPEC.md): builder, after owner direction approval. Only then modify `landing/` and durable `DESIGN.md`.
3. [Independent QA](slices/03-independent-qa/SPEC.md): compare rendered candidate to chosen comps, test desktop/mobile, fallback, install/legal, keyboard, performance and content truth.
4. [Release](slices/04-release/SPEC.md): owner-authorized scoped production release after QA PASS and live browser check, with rollback available.

## Status

Direction request being dispatched. **No approval to build or deploy this replacement yet.** Prior motion release remains live; prior passing QA does not constitute visual approval.
