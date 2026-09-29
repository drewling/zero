---
id: OPR.99.0.4.3
slice: 03-build-structure
mission: website-redesign-3
status: blocked
stage: wip
verified: 2026-09-29 against mission SPEC
created: 2026-09-29
intent: "Rebuild landing/ around the owner-approved copy (gate A) and comps (gate B): structure, static design, title-bar fix, clean replacement"
depends_on: [OPR.99.0.4.1, OPR.99.0.4.2]
owner_seat: development-implementer@zero
---

# Slice 03: build the structure and static design

## Intent

Build the approved page. Start only after the owner approves gate A (copy) and gate B (hero pick and sections). The main lead dispatches this slice with the exact approved artifact paths.

## Mini-requirements

1. Rebuild `landing/index.html`, `site.css` and `site.js` to the approved comps and **exact approved copy**. Do not reword it. If a line does not fit, raise it with the copywriter through the main lead.
2. Title-bar fix everywhere: text sits on a white plate, and no text renders over stripes, dither or rules at any viewport.
3. Leave motion hooks for slice 04 (stable classes and data-attributes named in `MOTION-SPEC.md`), but build and ship a complete static page. It must look finished with JS off.
4. Replace, do not layer. Remove obsolete sections, selectors, assets and tests, and give a before/after inventory.
5. Update `landing/DESIGN.md` to describe the new build, and update `test-site.mjs` for the new truth, keeping coverage for install, legal, clipboard, requirements and disclosures.
6. Keep `landing/build.sh` and `node --test landing/test-site.mjs` green. Keep the 320px layout with no overflow, semantic headings, and visible focus.
7. Hand an exact committed SHA to the main lead, who passes it to the motion seat for slice 04.

## Proof contract

- [ ] Commit SHA plus the output of build.sh and the tests.
- [ ] Screenshots at 1440, 390 and 320 (JS on and JS off), placed next to the gate B comps.
- [ ] Replacement inventory, and a grep showing that no banned phrase from slice 01 remains in `landing/`.

## Dependencies

Gates A and B (owner). Slice 04 builds on this SHA.
