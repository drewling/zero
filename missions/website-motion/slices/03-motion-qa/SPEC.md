---
id: OPR.99.0.2.3
slice: 03-motion-qa
mission: website-motion
status: blocked
stage: wip
verified: 2026-09-28 against motion mission contract and prior independent QA criteria
created: 2026-09-28
intent: "Independently verify the motion and Canvas behavior across desktop/mobile, input and preference states, failure paths and performance"
depends_on: [OPR.99.0.2.2]
---

# Slice 03: independent motion QA

## Intent

Judge the running candidate against the approved storyboard and the existing page's visitor path, not just static screenshots or animation code.

## Mini-requirements

1. Compare first-run, mid-journey, install and settled motion states at 1440, 390 and 320 widths against the storyboard. Confirm Canvas is visible and purposeful without hiding text, product proof, cost/safety disclosures or install actions. Verify no horizontal overflow and no motion-induced layout shift that loses reading position.
2. Exercise keyboard, touch/pointer where available, FAQ, anchor navigation, Copy and error fallback, rapid scroll/re-entry, tab hide/show, resize and repeated visits. Confirm animations can be interrupted and cleaned up, without timers/frames running indefinitely offscreen or while hidden.
3. Exercise `prefers-reduced-motion`, JavaScript disabled and Canvas context unavailable. The fallback must keep the full story readable, functional and visually composed, with no blank content. Check focus, contrast, screen-reader semantics and nonessential canvas `aria-hidden`/pointer behavior.
4. Measure candidate against the baseline on representative mobile and desktop viewports with capture/trace evidence: animation smoothness, main-thread tasks, memory/canvas dimensions, and JS/asset weight. Diagnose any material slowdown and rerun after repairs. Re-run node tests, Docker build/smoke, installer parse, links and legal routes. State limitations honestly if real-device measurement is unavailable.

## Proof contract

- [ ] Independent visual motion comparison and interaction evidence, with before/after frames or recording and a requirement-by-requirement verdict.
- [ ] Reduced-motion, no-JS, Canvas-unavailable, hidden/offscreen/re-entry, keyboard and copy behavior results plus baseline/candidate performance measurements.
- [ ] No regression in build, first-party routes and installer path; repaired defects rechecked on the final candidate SHA. PASS or blocking residue clearly stated before release.

## Status

Blocked on a builder candidate. Reviewer owns the verdict and does not edit `landing/` concurrently with builder repair.
