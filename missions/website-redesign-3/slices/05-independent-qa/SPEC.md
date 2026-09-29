---
id: OPR.99.0.4.5
slice: 05-independent-qa
mission: website-redesign-3
status: blocked
stage: wip
verified: 2026-09-29 against mission SPEC
created: 2026-09-29
intent: "Independently verify the exact 04 SHA against approved copy (gate A), approved comps (gate B), function, accessibility, responsive and packaging"
depends_on: [OPR.99.0.4.4]
owner_seat: review-qa@zero
---

# Slice 05: independent QA

## Mini-requirements

1. **Copy:** the built page matches `01/proof/COPY.md` word for word, the banned-phrase grep has 0 hits, and the word count falls within target.
2. **Cold-reader test on the built page:** show a screenshot of the first viewport only to 3 fresh model sessions and ask what the product does. Pass means all 3 say it is a Mac app that cleans up or manages a Gmail inbox.
3. **Visual:** Chromium and WebKit at 1440, 390 and 320, compared side by side with the gate B comps. Find no text over stripes, dither or rules. Record any drift.
4. **Motion:** the hero story plays as storyboarded. Reduced-motion and no-JS show the complete settled page, and nothing loops or blocks reading.
5. **Function:** install command, Copy button (success and denial), install/legal routes, the 404 page, keyboard-only pass, visible focus, and the heading outline. Add an axe scan if available.
6. **Packaging:** the Docker image builds and `/install` and `/install.sh` redirect correctly. Lighthouse performance and accessibility are recorded.
7. QA does not change `landing/`. Findings go back to the main lead with exact repro steps.

## Proof contract

- [ ] `PROOF.md`: a requirement-mapped PASS or FAIL for the exact SHA, with shots in `proof/shots/`.
