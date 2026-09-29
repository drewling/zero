---
id: OPR.99.0.3.2
slice: 02-implementation
mission: website-redesign-2
status: gated
depends_on: [OPR.99.0.3.1]
---
# Slice 02: implement the owner-approved direction

Builder owns `landing/` only after visual approval. **Replace the old page implementation, do not append a second system to it:** rewrite HTML/CSS/JS around the approved design, delete dead departure-board components, motion/Canvas hooks, unused assets and obsolete tests, and replace the rejected DESIGN.md. Keep the functioning nginx/Docker packaging, install/legal routes, real app image and product truth. Produce a before/after inventory showing every retained asset and removed legacy module, verify no duplicate stylesheet/interaction paths or dead selectors, and prove rendered desktop/mobile correspondence to approved comps. No release from this slice. Do not touch the Mac app, installer source or Git history.
