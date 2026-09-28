---
id: OPR.99.0.1
mission: website-redesign
stage: wip
verified: 2026-09-28 against scaffold (rig scope create)
created: 2026-09-28
intent: "Ship a distinctive, truthful, conversion-oriented redesign of zero.headless.com with verified live deployment"
depends_on: []
---

# Mission: zero website redesign

## Intent

Replace the messy landing page with a singular, high-craft product experience that earns a confident install without burying the risks or imitating Linear. The complete brief, sources, funnel, team and acceptance are in [the plan](../../docs/website-redesign-plan.md).

## Slices

1. [Discovery and direction](slices/01-discovery-direction/SPEC.md): research, selected world and desktop/mobile mockups. Design lead.
2. [Message and install journey](slices/02-message-journey/SPEC.md): truthful conversion path and human copy. Design lead with mission-owner claims check. Depends on 1.
3. [Responsive implementation](slices/03-implementation/SPEC.md): approved page in `landing/`. Builder. Depends on 1 and 2.
4. [Independent QA](slices/04-independent-qa/SPEC.md): visual and functional compare, repairs. Reviewer and builder. Depends on 3.
5. [Release](slices/05-release/SPEC.md): Dokploy or verified auto-deploy, live checks and rollback. Mission lead. Depends on 4.

## Status

Planning complete. Seats requested from `operator-agent@kernel` as a design/strategy pod with Claude Opus 5.5, development pod, and independent review pod. No production changes until the implementation passes independent QA. Preserve unrelated untracked OpenRig files and existing production behavior.

## Decision boundaries

Use updated `/impeccable` for replacement-world direction and mockups, `/funnels` for the install path, `/slopmonster` for final copy. Current README, installer, implementation and privacy disclosures prevail over aspirational language in PRODUCT.md. The design lead may propose a direction; mission owner selects and signs off before builder starts. Avoid simultaneous edits to landing files. If requested model cannot be verified, report rather than substitute silently.
