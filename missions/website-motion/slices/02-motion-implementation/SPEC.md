---
id: OPR.99.0.2.2
slice: 02-motion-implementation
mission: website-motion
status: ready
stage: wip
verified: 2026-09-28 against current landing source and motion mission contract
created: 2026-09-28
intent: "Build the approved animation system and Canvas effect as a resilient progressive enhancement of the static landing page"
depends_on: [OPR.99.0.2.1]
---

# Slice 02: motion and Canvas implementation

## Intent

Translate the approved storyboard into the existing static HTML/CSS/JS landing page. Build only after the mission owner selects the motion direction.

## Mini-requirements

1. Integrate the approved Canvas focal effect and supporting motion beats through the visitor journey, with deterministic start/settle and clear state feedback. Do not change factual copy, install destination, screenshot or visual identity. Preserve the existing headline board's semantic `h1` and avoid contradictory motion.
2. Make Canvas and all nonessential motion optional: no-JS and no-Canvas paths remain readable and complete; reduced-motion avoids spatial movement but retains essential feedback; pause/stop and release work offscreen, on hidden tab and after exit/interruption. Bound DPR, canvas dimensions, redraw frequency and any event listeners to the measured budget. Do not intercept scrolling, clicks or focus.
3. Preserve performance and existing contracts: static nginx/Docker, self-hosted assets, semantic table/FAQ, focus rings, install-command copy fallback, `node --test landing/test-site.mjs`, `bash landing/build.sh` and public legal/install routes. Add focused tests for lifecycle, fallback and preference behavior where practical without testing implementation trivia.
4. Run the page in real rendering engines at desktop and narrow mobile widths; compare key frames and settled states to the approved storyboard, then run the Impeccable detector once on changed UI targets at finish.

## Proof contract

- [ ] Working source and tests showing Canvas effect plus multiple intentional motion beats, with screenshots or recording compared to the approved storyboard.
- [ ] Evidence for no-JS/no-Canvas/reduced-motion/hidden-tab/offscreen behavior and measured baseline-versus-candidate runtime cost on representative desktop/mobile hardware or browser throttling, with limitations stated.
- [ ] Existing landing build, route and installer smoke pass without changing user-facing factual claims.

## Source material

[Mission spec](../../SPEC.md), [approved motion brief](../01-motion-direction/SPEC.md) and its `proof/` artifacts once complete, `landing/index.html`, `site.css`, `site.js`, `test-site.mjs`, `build.sh` and `DESIGN.md`.

## Status

Approved 2026-09-28 20:26Z by the user. Builder owns `landing/`; design and QA should not concurrently edit those files. Use `../01-motion-direction/proof/MOTION-BRIEF.md` and prototype revision `3f06044` as the direction, with legible verdicts, instant reduced-motion rail swap, both Canvas moments, replay controls and no pointer effect. Follow the brief's lifecycle/budget; do not ship prototype query hooks. Hand off a source SHA and evidence for independent QA before release.
