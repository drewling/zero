# Sandbox verification, 2026-09-29

Scope: slice 04 draft runner prototype only. Candidate source and artifacts are the files in this directory's parent sandbox. This is not slice 04 acceptance or QA approval of the landing page.

## Observed results

| Check | Result | Evidence |
|---|---|---|
| Chromium full suite | 16 passed, 0 failed | `chromium-green.txt` |
| Installed Playwright WebKit full suite | 14 passed, 0 failed, 2 optional capture/reference checks skipped | `webkit-green.txt` |
| Regression RED against designer runner | 3 expected failures out of 5 selected checks | `reference-red.txt` |
| Static and reduced-motion render | PNG bytes equal to no-JS final HTML in both engines | parity tests in green logs |
| Keyboard replay and overlapping activation | Second activation returns current promise, settled result remains truthful | replay test in green logs |
| Live reduce/resize cancellation and missing target | Immediately settles, no residual overlays, ordinary playback cannot pass on an error fallback | green logs |
| Hidden-document cancellation | Synthetic property/event, no late mutations, replay available after return | explicitly named synthetic test |
| 320/390 px playback | No horizontal overflow or cursor, four final kept rows | green logs |
| Whole CSS pixels | Rounded zoom sprite geometry checked in real browser | geometry test |
| Eight real arrivals | Numeric transition sequence `12, 11, 10, 9, 8, 7, 6, 5, 4` in both engines | timing log and `timing-chromium.json` |
| Measured Chromium CLS | Exactly 0 at tested desktop/mobile widths, including startup | Chromium log |
| WebKit CLS | Not independently measured: the Layout Instability API is absent | do not interpret its zero accumulator as proof |
| Active Chromium duration | Desktop 4,987 ms; mobile 4,044 ms | `timing-chromium.json` |
| Active WebKit duration | Desktop 5,065 ms; mobile 4,088 ms | `webkit-green.txt` |
| Designer reference active Chromium duration | 4,488 ms at 1440 px, final count 4 | `reference-timing.json` |
| Runner size | 10,480 source bytes, 3,508 gzip bytes | measured with Node `zlib.gzipSync` |
| Story data size | 2,735 source bytes, 1,174 gzip bytes | measured with Node `zlib.gzipSync` |
| Separately served runtime gzip total | 4,682 bytes, below 8 KB target | sum of the two runtime scripts, excludes fixture-only metrics instrumentation |
| COPY v3 hero rows | Exact sender/subject strings in both lists, all text fits at 320/390/1440 px | owned COPY.md and full-string browser geometry test |
| Mobile envelope/label separation | No rectangle intersections in frame 3 or live playback at 320/390 px | new geometry regression test in both green logs |

The reported nine-second Aside playback was not reproduced in the active local renderer. No cause is asserted. The hardened runner cancels to the complete final state on hidden-document events and has a six-second default deadline.

The current designer reference measured above is the live comp as of `9d9d1db`. That update adds alternative hero/section beats, removes the demo counter, and makes Terminal and Undo options explicit. The sandbox remains the originally authorized five-frame hero draft. It does not claim to implement those newer section options.

## Visual artifacts

- `mobile-strip.png`: full-resolution five-frame counter-launch strip, left to right 0 through 4.
- `desktop-strip.png`: full-resolution five-frame desktop strip, left to right 0 through 4.
- `390-frame-0.png` through `390-frame-4.png`, plus the corresponding 1440 px frames.
- `390-reduced.png` and `1440-reduced.png`: settled end states.
- `capture.json`: capture timestamp, widths, and Chromium version.

Design-lead judged the original `62f413e` mobile strip on 2026-09-29 at 22:12Z: the counter-launch reads as archiving, so keep it. This refreshed strip addresses the two requested corrections: mobile envelopes launch from the top of the count digits into empty list space, never splitting the label, and both lists use the exact COPY v3 hero sender/subject strings. Row slots are fixed at a height that accommodates full wrapped copy. No account initials, badges, or ages were added. Visual acceptance of this corrected strip remains design-lead's judgment.

The two new regression tests were run against `62f413e` before changing the fixture. Both failed as expected: abbreviated hero copy and a frame-3 label collision at 320 px. After the corrections, both pass in Chromium and WebKit. The live path test observes all five visible positions of each of eight hops. The sixth position is the folder arrival, removed synchronously before paint, and the separate eight-arrival/count test verifies completion.

## Mechanical design detector

The required one-time Impeccable detector ran on the fixture HTML/CSS and exited 2 with four inherited-kit warnings: a flush window primitive, Geist, Geist Mono, and repeating title-bar stripes. These are not a clean-detector claim. The draft explicitly pins the classic Mac title stripes and the supplied comp kit. Window text uses the kit's white title plates and inset list/panel rows. No font or visual-world substitution was made merely to clear the detector. Actual design polish remains at the later authorized slice boundary.

## Limits

No production or `landing/` edits, no deploy, no queued assignment claim, no slice-close proof drop. Full section motion, finite ants, Safari 26 jitter verification, genuine OS tab-switch verification, Lighthouse comparison against slice 03, and the exact approved integration candidate remain later work. Integration still requires gate B, the real queue row, and the slice 03 SHA.
