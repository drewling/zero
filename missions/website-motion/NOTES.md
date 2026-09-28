---
mission: OPR.99.0.2
name: zero website motion and canvas
created: 2026-09-28
---

# Notes — zero website motion and Canvas

## Top of mind

- 2026-09-28 13:38Z: User requested a **new mission** for animations throughout the existing zero.headless.com page plus HTML Canvas effects. Mission `OPR.99.0.2` scopes direction → implementation → independent QA → release. No production/code changes yet.
- Direction boundary: retain the approved Departure board visual world and product truth. Existing hero tiles already cycle/settle once and are static under reduced motion. The new focal Canvas effect must have a product-specific job and several supporting page beats without becoming animation on every node.
- Open design decision: exact Canvas metaphor, intensity and optional pointer interaction. Design lead will storyboard desktop, mobile and reduced-motion states for mission-owner approval before builder starts.
- Existing `zero-landing:57deff2` was healthy and live at prior release on 2026-09-28 morning; treat it as a historical baseline, re-check production before any later deployment. Raw Dokploy Compose service `u2SP2b5035tm1yaHVNcH8`, no Git auto-deploy. Prior proof: `missions/website-redesign/slices/05-release/proof/release-pass.md`.
- Preserve unrelated untracked OpenRig files. Design lead owns prototype artifacts under this mission; builder alone owns `landing/` during implementation; reviewer independently accepts the final candidate.
