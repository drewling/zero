# PROOF: OPR.99.0.2.1 Motion direction and storyboard

Closed by: design-lead@zero   Date: 2026-09-28   Verdict: **direction delivered, owner decision pending** (pass-with-residue on mobile visual proof)

## What this proves

A concrete, runnable motion and Canvas direction ("The board sorts") for the live Departure board page. It covers a focal Canvas sort track on the rules table, a second Canvas recovery-rail diagram for "Nothing is deleted", DOM beats on install, copy and FAQ, and reduced-motion and no-Canvas fallbacks. It was measured against a production baseline. No `landing/` file was edited and nothing was deployed.

## Proof contract mapping

1. **Storyboard / runnable prototype showing the Canvas focal moment and multiple beats.**
   - Runnable prototype: `proof/prototype/`. Serve that directory statically, for example `python3 -m http.server` from inside it. `assets` is a relative symlink to `landing/assets` so the prototype uses the real fonts and app image without duplicating 1.5 MB.
   - Desktop frames (Aside, 1440×900): `storyboard/d-sort-0/700/1300/settled.jpg`, `d-rail-0/450/900.jpg`, `d-restore-450.jpg`, `d-restore-live.jpg`, `d-hero-flap-mid.jpg`, `d-hero.jpg`, `d-install-boarding.jpg`, `d-install-settled.jpg`.
   - Reduced motion / no Canvas: `d-rm-sort.jpg`, `d-rm-undo.jpg`, `d-nocanvas-sort.jpg`, `d-nocanvas-undo.jpg`.
   - Mobile (390 px iframe, not device emulation): `m-hero.jpg`, `m-sort-settled.jpg`, `m-rail-450.jpg`. (`m-sort-700.jpg` was removed after review because it showed the retired scramble. The recapture hung in Aside.)
2. **Written motion brief** covering purpose, triggers, timing, reduced-motion and static states, failure fallbacks and the measured baseline: `proof/MOTION-BRIEF.md` §§1 to 7. Owner approval: **pending**, with the questions listed in §9.

## Residue / caveats

- The mobile install and reduced-motion frames are not visually proven because Aside's screenshots timed out on the iframe harness. Only the no-overflow width check (`scrollWidth = clientWidth = 390`) is recorded for those states. The build slice's QA owns that proof on a real narrow viewport.
- Live frame pacing through Aside is throttled (about 30 fps even when idle). The synchronous draw bench (0.07 ms and 0.02 ms per frame) is the reliable cost figure. Pacing must be re-measured before release.
- Prototype-only hooks (`?seek`, `?rm`, `?nocanvas`, `?slow`, `?at`, `zeroMotion.stats/bench`, `mobile.html`) must not ship.
- Per the `1c55bd1` scope correction, no build, QA or release is dispatched from this slice.
