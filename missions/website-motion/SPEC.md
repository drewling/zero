---
id: OPR.99.0.2
mission: website-motion
stage: wip
verified: 2026-09-28 against live landing source, DESIGN.md, prior QA and release proof
created: 2026-09-28
intent: "Add a cohesive, expressive motion system and a purposeful HTML Canvas effect to the existing zero.headless.com landing page without weakening its clarity, accessibility, performance, or install path"
depends_on: []
---

# Mission: zero website motion and Canvas

## Intent

Give the live [Departure board](../../landing/DESIGN.md) landing page an authored sense of movement from first glance through install, including a genuinely integrated HTML Canvas effect. This **enhances** the approved visual world; it does not replace its palette, typography, copy, real product image, factual disclosures or conversion path. Motion should express the page's keep / set-aside / reversible-archive story, not become a generic particle background or make an exhausted inbox user wait for information.

## Outcome and boundaries

- The visitor sees a memorable, product-specific focal sequence and a small number of distinct supporting motion beats distributed across the page. The Canvas effect has a legible role within that sequence, not a perpetual layer over the copy or controls. The design slice chooses its exact appearance and asks the mission owner to approve the storyboard before coding.
- The headline and all essential content are immediately legible and actionable with JavaScript disabled, Canvas unavailable, a failed script, or `prefers-reduced-motion: reduce`. Reduced-motion mode should preserve meaningful state feedback without the spatial choreography. Motion must stop offscreen and when the tab is hidden; no autoplay sound, scroll-jacking, fake inbox activity, or animation that obscures safety, cost, or install information.
- Preserve semantic HTML and native FAQ/keyboard behavior, focus visibility, copy-command fallback, legal/install routes, real product image and source links. No new runtime/framework dependency unless the design and measured benefit warrant it. Retain static nginx/Docker packaging and a bounded mobile/desktop CPU, memory and paint budget, measured against the current page before selecting an implementation.

## Slices

1. [Motion direction and storyboard](slices/01-motion-direction/SPEC.md), design lead. Inventory current motion and create desktop/mobile/reduced-motion storyboards or prototypes showing the focal Canvas moment and supporting choreography. Mission owner approves or corrects direction.
2. [Motion and Canvas implementation](slices/02-motion-implementation/SPEC.md), builder, after direction approval. Progressive enhancement in `landing/`, with tests and integration smoke.
3. [Independent motion QA](slices/03-motion-qa/SPEC.md), reviewer. Compare implementation to storyboard and exercise responsive, keyboard, reduced-motion, failure and performance paths; builder repairs issues.
4. [Release and live verification](slices/04-release/SPEC.md), mission lead, after QA PASS. Deploy to the verified single-service raw Dokploy Compose, check live experience and rollback.

## Current state and decisions

Planning and scaffold only. No `landing/` changes or production deployment under this new mission yet. The existing hero tile animation settles once under 1 second and is suppressed by reduced-motion preference. Design may refine it but must not create competing headline loops. The user's phrase “animations throughout this page, and html canvas effects too” is interpreted as **page-wide authored choreography with at least one Canvas effect**, not animation on every element. The intensity, focal Canvas metaphor and whether to include optional pointer interaction remain open for the design storyboard and owner sign-off.

Source of truth: [landing/DESIGN.md](../../landing/DESIGN.md), [current page](../../landing/index.html), [approved direction](../website-redesign/slices/01-discovery-direction/proof/DESIGN-BRIEF.md), [prior independent QA](../website-redesign/slices/04-independent-qa/proof/PROOF.md), and [release proof](../website-redesign/slices/05-release/proof/release-pass.md). Existing production image `zero-landing:57deff2` is the starting baseline and rollback candidate, subject to re-check immediately before any release.
