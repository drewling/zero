---
id: OPR.99.0.3.3
slice: 03-independent-qa
mission: website-redesign-2
status: gated
depends_on: [OPR.99.0.3.2]
---
# Slice 03: independent visual and functional QA

Reviewer checks real browser rendering against approved comps at desktop and narrow mobile, visitor/install/legal journeys, no-JS/Canvas, reduced motion, keyboard and screen reader semantics, performance and source-of-truth claims. Inspect the shipped source/asset inventory and dependency graph for obsolete departure-board CSS/JS/Canvas, unused images, duplicate visual systems and dead selectors; validate that needed routes and app functionality survived the replacement. Report defects or PASS with direct evidence before release.

**Held after the owner's content/structure rejection.** Do not issue final PASS on the initial visual-only B candidate. After slice 02b's outline and draft receive owner approval and slice 02c lands an exact committed candidate, compare the content against the approved visitor decision path and factual disclosures as well as the B visuals. Recheck the Copy button's keyboard focus on both clipboard success and denial; the first candidate blurred focus to BODY when it disabled the focused button.
