---
id: OPR.99.0.4.2
slice: 02-references-and-comps
mission: website-redesign-3
status: ready
stage: wip
verified: 2026-09-29 against owner feedback and live capture
created: 2026-09-29
intent: "Find more one-bit / retro-Mac references and design a composed, detailed hero plus a real design for every section, carrying slice 01's copy"
depends_on: []
owner_seat: design-lead@zero
---

# Slice 02: references, hero and section comps

## Intent

The owner likes the one-bit Mac style but says the hero "just doesn't have a good layout", needs "more animations", "more detail and more polish", and the sections are "a mess" that is "just text on the left and something on the right". He asked: "find more references in this style for more ideas." Use `/impeccable` (Persuade mode; refine within the existing B world, do not replace it). This slice is proof-only until gate B. Do not edit `landing/`.

## Mini-requirements

1. **8+ new references in this style.** Each must be live and inspectable, with URL, date and a screenshot captured through Aside or Playwright. Look for sites and projects that do one-bit, System 6/7, pixel-art, dithered or retro-OS interfaces *well*, and include at least 2 that animate in that style. Starting places: poolsuite.net, the Panic and Playdate sites, 100r.co, Susan Kare's work, Basecamp/HEY retro pages, the "Macintosh"-style portfolios on Awwwards/Godly/siteinspire, the classic Mac window and Finder recreations such as the infinitemac.org UI, Teenage Engineering, and dither-art sites. Do not reuse redesign-2's reference atlas. For each: what is seen, the transferable idea (layout, detail, motion), and what not to copy.
2. **Fix the obvious craft bugs by design.** Title-bar text sits on a white plate that breaks the stripes, as in real System 7 windows. Apply this to every window. Check every place where text meets a line or dither.
3. **Hero, 2–3 compositions.** Each has a clear focal hierarchy (headline → proof → action), deliberate alignment, and real detail (for example menu bar clock/items, an icon grid, a cursor, window depth and stacking, a dated folder, an empty Trash). Include a **motion storyboard** of 4–8 frames showing the story in 1-bit motion, for example cluttered inbox rows being dragged into the dated "Archived" folder by a pixel cursor until only the few that need you remain, then the count settling. Motion stays stepped and snappy, and has a reduced-motion end state.
4. **A real design for each section in slice 01's outline.** Break the text-left / object-right sameness. Each section *shows* its point with a purpose-built one-bit illustration or UI (for example a before/after inbox, a "why this stayed" card, an undo dialog, a requirements "Get Info" window, a Terminal install). Vary the layouts and pace the page. No empty halves.
5. **Comps are runnable HTML** at 1440 and 390, using slice 01's draft copy (or its latest version, marked draft). Do not use the old copy. Capture desktop and mobile screenshots of each option.
6. **Motion spec** for slice 04: every animation, its trigger (load, scroll into view, hover), duration and steps, and its reduced-motion and no-JS end states.

## Proof contract

- [ ] `proof/references.md` with 8+ entries and `proof/refs/*.png`.
- [ ] `proof/comps/hero-{a,b,c}/index.html` and screenshots at 1440 and 390.
- [ ] `proof/comps/sections/` with one design per outline section, plus screenshots.
- [ ] `proof/MOTION-SPEC.md` with the storyboard frames.
- [ ] `proof/DESIGN-BRIEF.md`: the recommendation and the reasons behind it.
- [ ] Main lead shows the owner gate B (the hero pick and the section approval) alongside gate A.

## Source material

- `missions/website-redesign-3/SPEC.md`, `slices/01-copy-and-story/proof/before/`
- `landing/DESIGN.md`, `landing/site.css`, `landing/index.html`, `assets/zero-panel.png`, `macapp/Sources/PanelView.swift`
- `missions/website-redesign-2/slices/01-research-direction/proof/` (the old atlas, not to be reused)

## Intent visual

The comps are the intent visuals. Link the chosen hero screenshot as `./intent.png` after gate B.
