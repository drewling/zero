---
mission: OPR.99.0.2
name: zero website motion and canvas
created: 2026-09-28
---

# Notes — zero website motion and Canvas

## Top of mind

- 2026-09-28 15:19Z direction handoff reviewed: `1490316` delivered `slices/01-motion-direction/proof/MOTION-BRIEF.md`, a runnable prototype and 21 storyboard frames. The proposed “board sorts” focal Canvas, recovery-rail Canvas and small install/copy/FAQ beats are coherent with the page, and the inspected desktop sort and 390px rail frames are legible. Recommend the two Canvas moments and replay controls, with no pointer effect. **This is a planning recommendation, not authorization to build or release.** Before implementation, keep actual verdict words legible even before and during the sort rather than replacing them with dots/scrambled letters, and make the reduced-motion rail swap truly instantaneous rather than a 220ms opacity transition. Real-device mobile/reduced-motion visual checks and unthrottled pacing remain unproven and belong in the future implementation/QA gate. Await the user's go-ahead and design preference before dispatching any downstream slice.

- 2026-09-28 14:41Z scope correction: this turn requested **mission creation**, not end-to-end shipping. Direction seat can finish its planning prototype, but do not dispatch build/QA/release or modify production without a separate go-ahead. A message to the design seat failed because the OpenRig daemon was slow/unresponsive; this committed contract is the durable boundary.
- 2026-09-28 13:38Z: User requested a **new mission** for animations throughout the existing zero.headless.com page plus HTML Canvas effects. Mission `OPR.99.0.2` scopes direction → implementation → independent QA → release. No production/code changes yet.
- Direction boundary: retain the approved Departure board visual world and product truth. Existing hero tiles already cycle/settle once and are static under reduced motion. The new focal Canvas effect must have a product-specific job and several supporting page beats without becoming animation on every node.
- Open design decision: exact Canvas metaphor, intensity and optional pointer interaction. Design lead will storyboard desktop, mobile and reduced-motion states for mission-owner approval before builder starts.
- Existing `zero-landing:57deff2` was healthy and live at prior release on 2026-09-28 morning; treat it as a historical baseline, re-check production before any later deployment. Raw Dokploy Compose service `u2SP2b5035tm1yaHVNcH8`, no Git auto-deploy. Prior proof: `missions/website-redesign/slices/05-release/proof/release-pass.md`.
- Preserve unrelated untracked OpenRig files. Design lead owns prototype artifacts under this mission; builder alone owns `landing/` during implementation; reviewer independently accepts the final candidate.
