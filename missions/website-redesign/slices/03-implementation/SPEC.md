---
id: OPR.99.0.1.3
slice: 03-implementation
mission: website-redesign
status: blocked
stage: wip
verified: 2026-09-28 against scaffold (rig scope create)
created: 2026-09-28
intent: "Build the approved responsive design while preserving install, safety, legal, and source routes"
depends_on: [OPR.99.0.1.1, OPR.99.0.1.2]
---

# Slice 03: Responsive implementation

## Intent

Implement the approved direction and copy as a production-ready homepage without breaking the install workflow.

## Mini-requirements

1. Follow direction mockups, updated `/impeccable` craft floor and copy deck; replace visual system in `landing/DESIGN.md` and page styles. Use real product imagery and transparent labels for fictional demo content.
2. Semantic responsive HTML/CSS/JS with usable mobile navigation, keyboard focus, reduced-motion behavior, image dimensions and sensible loading. Avoid new framework unless there is a demonstrated need.
3. Preserve working `/install`, `/install.sh`, privacy, terms, source and release links; copy-to-clipboard and its fallback; explicit macOS 26+, Apple Silicon, Gmail and Jev-key requirements.
4. Extend tests where interactions or routes change. Run local test and build/smoke commands.

## Proof contract

- [ ] Implementation compared with desktop/mobile mockups, with deviations noted.
- [ ] `node --test landing/test-site.mjs`, installer syntax and Docker smoke if available, with command output.
- [ ] Real page desktop/mobile captures and interaction checks; no invented testimonials or numbers.
