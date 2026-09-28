---
id: OPR.99.0.2.1
slice: 01-motion-direction
mission: website-motion
status: ready
stage: wip
verified: 2026-09-28 against current landing source and design brief
created: 2026-09-28
intent: "Select an authored departure-board motion thesis, page-wide choreography and Canvas role with desktop/mobile/reduced-motion storyboards"
depends_on: []
---

# Slice 01: motion direction and storyboard

## Intent

Show what movement adds to the existing Departure board page before anyone codes it into production. The design lead owns the motion thesis; the mission owner approves a concrete direction and scope.

## Mini-requirements

1. Inventory the actual live page sequence and existing hero flap animation, interactions and responsive layouts. Establish a baseline for mobile and desktop rendering and runtime cost. Keep the approved palette, type, copy and real app image.
2. Propose one distinctive focal sequence that integrates an **HTML Canvas** effect with the keep / archive / reversible journey, plus purposeful supporting beats in more than the hero. Specify which moments respond to scroll, hover, click, focus or visibility and why, rather than animating every section on entry.
3. Produce viewable desktop and mobile storyboards or a small interactive prototype (first, middle, install, settled states) and a reduced-motion/no-Canvas static alternative. State timing, interruption, replay, offscreen/hidden-tab behavior, fallback and practical performance budget. Explain why the Canvas is preferable to simpler CSS for its particular job.
4. Present a concise owner decision: selected direction, one credible alternative if materially different, risks and what specifically needs approval before implementation. No production `landing/` edits in this slice.

## Proof contract

- [ ] Desktop/mobile motion storyboard or runnable prototype showing the Canvas focal moment and multiple page beats, with captured frames or a short recording under `proof/`.
- [ ] Written motion brief documenting purpose, triggers, timing, reduced-motion/static state, failure fallbacks and measured baseline, plus owner approval or required correction.

## Source material

[Mission spec](../../SPEC.md), [landing/DESIGN.md](../../../../landing/DESIGN.md), [landing/index.html](../../../../landing/index.html), [site.js](../../../../landing/site.js), [site.css](../../../../landing/site.css), [prior direction brief](../../../website-redesign/slices/01-discovery-direction/proof/DESIGN-BRIEF.md), `/impeccable animate` guidance.

## Status

Ready for design-lead@zero. The exact Canvas metaphor and intensity are intentionally not preselected by this scaffold.
