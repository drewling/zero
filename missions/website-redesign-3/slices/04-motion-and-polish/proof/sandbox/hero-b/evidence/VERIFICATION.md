# Hero B sandbox verification, 2026-09-29

Candidate: this directory's parent `hero-b/`, using shared `../motion.js`. Storyboard input: `d0a5685`, `MOTION-SPEC.md` §3.0. Scope is the authorized **hero-only sandbox**, not the landing page, gate B, slice 04 completion or an independent QA decision.

## Observed results

- Chromium 149.0.7827.55: **11 passed, 0 failed**, including capture, in `chromium.txt`.
- Installed Playwright WebKit: **10 passed, 0 failed**, one optional capture check skipped, in `webkit.txt`. This is not certification of Safari 26.
- Historical A consumer against the final shared runner: **14 passed, 0 failed**, two optional reference/capture checks skipped, in `a-regression.txt`.
- Reference B RED: all three selected checks failed as expected in `reference-red.txt`. The actual designer reference was served, not replaced with copied source. The observed defects were reduced-motion QA rewinding to frame 3, hidden mobile subjects and a forced coarse-pointer watch. All three pass with the hardened sandbox.
- `node --check` passed for the shared runner, B story and B test module. Scoped `git diff --check` passed. These are not production build checks.

| Width | Chromium active duration | Chromium CLS | WebKit active duration |
|---|---:|---:|---:|
| 320 | 3,374 ms | 0 | 3,405 ms |
| 390 | 3,382 ms | 0 | 3,406 ms |
| 760 | 3,707 ms | 0 | 3,742 ms |
| 1440 | 3,703 ms | 0 | 3,739 ms |

`timing.json` records the Chromium observations. WebKit's Layout Instability API is absent: its zero accumulator is **not independent CLS evidence**. Both engines completed in normal `done` mode; an error/cancelled fallback cannot pass the active test.

## Requirement and changed-output trace

Check numbers refer to named `ok N` results in both engine logs. Check 11 runs in Chromium only.

| Requirement or changed output | Concrete browser check | Observed result |
|---|---|---|
| Default HTML is final frame, reduced preference wins over QA hooks | 1: reduced `?frame=3`; 4: no-JS/static/reduced PNG equality | Frame 5, full selected folder, no cursor, zero routine rows/overlays. PNG bytes equal at 320/390/760/1440. |
| Exact hero sender/subject/age strings remain readable | 2: complete strings and text-range bounds | All four pairs and ages match at 320/390/760/1440; every text range fits and is visible. No horizontal overflow. |
| Real accessible replay, no duplicate runs | 3: type=button, named control, keyboard Enter and concurrent `Zm.play` | Playback replays and settles; repeat call returns the current promise. Button remains disabled during playback. This is not a complete accessibility audit. |
| Six frames, zero-owned watch only during Working, no arrow | 5: six QA frames at 320/390/760/1240/1440; 6: live mutation observations | Visible watch exists only in desktop frames 2–4. No arrow or cursor at smaller widths. During live playback every visible cursor is `#watch` and the label is Working…. Its first observed location is the button, not the origin. |
| Four readable rows plus eight greeked routines in clutter; archive exactly eight | 5: selected count in frames 3/4; 6: every live selection count and actual drag arrivals | All selection counts 1 through 8 observed. Eight simultaneous dashed outlines are present, and all eight actually reach bounds inside the visible folder before removal. Final has exactly four retained rows. |
| Stepped 1-bit geometry and meaningful folder destination | 6: every observed outline/zoom dimension, cursor/outline DOMMatrix, layer and Trash bounds | Left/top/dimensions and translations use whole CSS pixels. Outlines are below the headline plate. No drag outline intersects Trash. Overlay nodes are aria-hidden and pointer-inert. Selection invert and truthful full-folder state are shown in captures. |
| Caption and everything below never move, including collapse | 5: exact caption bounds compared across all six frames at five widths; 6: live CLS and played-end PNG equality | Caption rectangles are identical across frames. Chromium live CLS is exactly 0 at four widths, including startup. Played final screenshot bytes equal static final screenshots at those widths. Together with check 4, played/no-JS/reduced end states occupy identical rendered positions. |
| Cancellation cannot leave partial state or late mutations | 7: live reduce, viewport resize and synthetic hidden event during eight-outline drag | Final frame settles immediately with zero overlays; full state is unchanged after 700 ms. Hidden event is synthetic, not an OS tab-switch test. |
| Missing target and deadline recover to complete fallback | 8: `?fault=drop` and forced 100 ms deadline | Missing target ends in `error`, deadline ends in `cancelled`; both have truthful final rows/folder/button and no overlays. |
| Fine pointer plus ≥760 is mandatory even for QA | 9: emulated coarse-pointer 1440 px frame 4; 5: narrow frames | No visible watch under coarse pointer or at mobile widths. This is media/device emulation, not physical-device certification. |
| Runner independent of fixture fonts/container width | 10: altered heading/list fonts and Inbox width before autoplay | Normal `done` completion and no controller error after live geometry changes. This does not prove arbitrary font changes fit approved copy or preserve layout. |
| Evidence captures reflect final source | 11: all six still frames and reduced mode at 390/1440 | Fourteen PNGs and dated `capture.json`; six-column full-resolution strips assembled from those frames. `desktop-review.png` is a reduced-size viewing aid, not a replacement for full-resolution artifacts. |
| Existing A story still consumes shared runner | `a-regression.txt` | Fourteen behavioral checks pass against the final helper implementation. Historical A source/captures were not rewritten to claim selected B acceptance. |
| Runtime budget | Node `zlib.gzipSync` measured separately served scripts | Runner 12,052 source / 3,966 gzip bytes. B story 2,343 source / 952 gzip bytes. Total 4,918 gzip bytes, below 8 KB. Fixture metrics, HTML/CSS/fonts and historical A story are excluded. No production bundle size claim. |

Runtime SHA-256:

- Shared `motion.js`: `90f3db551684f54ccf7ef82c14eef75477a70c4cba2a8029e8f5ade054fb6244`
- B `story.js`: `ce228783ba678d4f2bf4d4d6b4a62f7dc700ade47adaccfb3af2771b2f9051e2`

## Concrete improvement and layout reserve

The first B implementation was not accepted on partial green checks. Actual Chromium evidence found a 61 px caption jump: `svg.px` outranked a single-class hidden sprite rule, so the final folder rendered both SVGs. A more specific selector removed the duplicate. Subsequent shift-source observations found moving absolute `.drop` nodes, collapsing readable `LI` rows and the changing button footprint. At 320 px these contributed CLS 0.098641740625 even after the caption itself was stable.

The correction moves outline sprites with rounded transforms, keeps readable row layout slots fixed while earlier positions use discrete transforms, and fixes the button footprint. Measured CLS is now 0, while all eight real arrivals and exact final pixel parity remain true. A visual pass of desktop/mobile strips found mobile zoom outlines crossing headline text. Zoom and drag outlines now sit below the paper-backed headline; the final live observer verifies that layer relationship in both engines.

Per design-lead's explicit 23:04Z reserve permission:

- ≥1240: hero 940 px, outer Inbox slot 468 px, list 432 px including final, caption top 700 px relative to hero.
- 640–1239 stacked: outer Inbox slot 468 px; initial list 432 px, final four 36 px rows.
- <640 stacked: outer Inbox slot 548 px; initial list 512 px (four 56 px readable rows plus eight 36 px routines), final four 56 px rows.

Blank space inside the scene after collapse is deliberate. No-JS and reduced final states use these same reserves. They are fixture CSS sizes, not assumptions embedded in the generic runner.

## Review and acceptance boundary

B strips and reserve notes will be handed to design-lead on this exact sandbox candidate. No B design verdict is implied by the tests, by the historical A verdict, or by owner selection of B's concept. The fixture reuses the existing comp fonts while typography/full-width decisions are still being authored elsewhere.

The complete landing acceptance workflow has **not been attempted**: main-lead explicitly disallows integration and `landing/` edits before gate B, the real queued assignment and the slice 03 SHA. Destination queue check at 23:03Z returned no pending/in-progress/blocked rows. A sandbox pass is synthetic evidence, not acceptance-aligned project validation. Full-page section motion is still undefined for this seat.

Remaining boundaries: actual project build/tests, production packaging/CSP/hosting and failed-network behavior, full-page no-JS/reduced parity, Lighthouse comparison with slice 03, authored section beats/finite ants, Safari 26-specific rendering and real background-tab throttling, physical pointers, independent QA and owner/page polish approval. `dispose()` and IntersectionObserver-driven starts were not separately tested in this on-load hero fixture. These are explicit limits, not silently passed checks.
