---
id: OPR.99.0.4.4
slice: 04-motion-and-polish
mission: website-redesign-3
status: blocked
stage: wip
verified: 2026-09-29 against mission SPEC
created: 2026-09-29
intent: "Add the approved 1-bit motion (hero story, section reveals, micro-interactions) and a detail polish pass, without hurting access or speed"
depends_on: [OPR.99.0.4.2, OPR.99.0.4.3]
owner_seat: development-motion@zero
reviewer_seat: design-lead@zero
---

# Slice 04: motion and polish

## Intent

The owner wants "more animations and stuff" and "a bit more detail and a bit more polish". Once gate B is approved, prototype `MOTION-SPEC.md` in a sandbox (`proof/sandbox/`) while slice 03 builds. Then integrate on top of the 03 SHA.

## Mini-requirements

1. Build the hero motion story from the storyboard exactly, for example the pixel cursor dragging mail into the dated folder and the count settling. Stepped, 1-bit and snappy. It plays once, then rests, and has a replay affordance only if the spec asks for one.
2. Section motion and micro-interactions from the spec, for example window "zoom rect" opens on scroll-in, button press states, and a copy-command flash. Nothing loops forever, and nothing blocks reading.
3. Honour `prefers-reduced-motion` (show the settled end state) and no-JS (the complete static page from 03). Nothing that is only visible while animating.
4. Performance: animate transform and opacity only, or stepped sprite frames. No layout thrash. Total added JS should be small (target under 8 KB gzipped, and justify anything larger). No new third-party libraries without the main lead's OK. Lighthouse performance and accessibility on the built page must not drop from the 03 SHA, and you record both.
5. Design lead polish pass: spacing, alignment, text-on-line collisions, icon consistency, and focus states. They record a sign-off with before and after screenshots.
6. Keep `build.sh` and the tests green, and add tests for the reduced-motion and no-JS end states.

## Proof contract

- [ ] Commit SHA, plus a screen recording or frame strip of the hero story (desktop and mobile) and the reduced-motion capture.
- [ ] Lighthouse numbers for 03 and 04, and the JS size.
- [ ] The design lead's polish sign-off note.
- [ ] Exact SHA handed to QA for slice 05.
