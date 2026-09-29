---
id: OPR.99.0.3.2
slice: 02-implementation
mission: website-redesign-2
status: ready
depends_on: [OPR.99.0.3.1]
---
# Slice 02: implement the owner-approved direction

Builder owns `landing/` only after visual approval. **Replace the old page implementation, do not append a second system to it:** rewrite HTML/CSS/JS around the approved design, delete dead departure-board components, motion/Canvas hooks, unused assets and obsolete tests, and replace the rejected DESIGN.md. Keep the functioning nginx/Docker packaging, install/legal routes, real app image and product truth. Produce a before/after inventory showing every retained asset and removed legacy module, verify no duplicate stylesheet/interaction paths or dead selectors, and prove rendered desktop/mobile correspondence to approved comps. No release from this slice. Do not touch the Mac app, installer source or Git history.

## Approved direction and restraint

Implement **B, One-bit desktop**, from [Opus's design brief](../01-research-direction/proof/DESIGN-BRIEF.md) and the `b-top.jpg`, `b-sort.jpg`, `b-install.jpg`, `b-phones.jpg` and `b-static.jpg` comps in `../01-research-direction/proof/shots/`. The owner likes the world but specifically says not to overcomplicate copy or clutter the page. Preserve the current headline and factual language unless a small edit is necessary; no new elaborate copy deck. Use the one-bit grid/retro window language with discipline, not across every surface. Let the real app be the only colour and the visual proof. A dated-folder recovery cue and an empty-Trash cue suffice; avoid repeated icons, faux file-system interactions and nostalgic decoration that compete with actual product and install.

The comps are direction prototypes, not complete page code: the actual **Before you install**, FAQ and legal content must remain, the prototype Copy button is visual only, and `#before` has no target in the comp. Wire real paths, real clipboard behavior and all disclosures in the rebuilt page. Test in true browser viewports, not only the comp's 390px iframe. The design brief documents the TypeSafe link curl 403 caveat. Handoff to independent QA, do not deploy.

## Superseding content direction (2026-09-29)

This first implementation faithfully preserved old copy and order but the owner rejected that content/structure outcome. The preserve-nearly-verbatim sentence above is superseded for the next build. Slice 02b owns a new product-grounded story and owner approval; slice 02c integrates that approved story. Do not treat the visual B approval as approval to reuse the old feature-inventory order or repeated wording.
