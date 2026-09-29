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

Design-lead judged the original `62f413e` mobile strip on 2026-09-29 at 22:12Z: the counter-launch reads as archiving, so keep it. This refreshed strip addresses the two requested corrections: mobile envelopes launch from the top of the count digits into empty list space, never splitting the label, and both lists use the exact COPY v3 hero sender/subject strings. Row slots are fixed at a height that accommodates full wrapped copy. No account initials, badges, or ages were added. On 2026-09-29 at 22:28Z, design-lead independently checked `af81274`'s mobile strip and confirmed the envelope stays clear of the label and the hero rows are the exact v3 strings, unclipped. Both sandbox review defects are resolved, with no further sandbox design changes requested. This is not gate B approval or integrated-page polish sign-off.

The two new regression tests were run against `62f413e` before changing the fixture. Both failed as expected: abbreviated hero copy and a frame-3 label collision at 320 px. After the corrections, both pass in Chromium and WebKit. The live path test observes all five visible positions of each of eight hops. The sixth position is the folder arrival, removed synchronously before paint, and the separate eight-arrival/count test verifies completion.

## Mechanical design detector

The required one-time Impeccable detector ran on the fixture HTML/CSS and exited 2 with four inherited-kit warnings: a flush window primitive, Geist, Geist Mono, and repeating title-bar stripes. These are not a clean-detector claim. The draft explicitly pins the classic Mac title stripes and the supplied comp kit. Window text uses the kit's white title plates and inset list/panel rows. No font or visual-world substitution was made merely to clear the detector. Actual design polish remains at the later authorized slice boundary.

## Limits

No production or `landing/` edits, no deploy, no queued assignment claim, no slice-close proof drop. Full section motion, finite ants, Safari 26 jitter verification, genuine OS tab-switch verification, Lighthouse comparison against slice 03, and the exact approved integration candidate remain later work. Integration still requires gate B, the real queue row, and the slice 03 SHA.

## Acceptance boundary and observed improvement

These results are **synthetic fixture evidence**, even though they were collected in real browser engines. The fixture borrows the comp kit and runs the sandbox scripts. It is not the complete landing page, a production integration, or the end-user acceptance path required by slice 04. The full suite passing does not close slice 04.

There is concrete before/after evidence, rather than just source inspection:

- Before the corrections, the two new checks both failed. The 320 px frame-3 envelope rectangle occupied x=123..155, y=358..380, overlapping the label rectangle x=82.109375..237.890625, y=355..381.34375. The copy check observed the four abbreviated strings instead of COPY v3's authored subjects.
- After the corrections, the exact-copy and text-fitting check passes at 320/390/1440 px, and the frame-3/live mobile rectangle-intersection check reports no collisions at 320/390 px. Both checks pass in Chromium and installed Playwright WebKit. Each live eight-hop story observes at least 40 visible envelope placements, and the independent arrival test still observes every decrement from 12 through 4.
- Design-lead's 22:12Z observation on the original strip was that the counter-launch reads as archiving. The corrected `af81274` strip was independently checked at 22:28Z, and design-lead confirmed both requested defects resolved: label-clear envelopes and exact, unclipped COPY v3 rows. This closes those sandbox review requirements by observed visual judgment, not by inferring approval from automated geometry checks. It does not close the full-page polish or owner gates.

The real acceptance route comes from `slices/04-motion-and-polish/SPEC.md` mini-requirements 1 through 6. Its status is still `blocked`. At the 22:25Z dependency check, `slices/03-build-structure/PROGRESS.md` did not record implementation, passing tests or review approval, and the last live destination queue check at 22:22Z returned zero rows. These are scoped observations of the checked surfaces, not a claim that nobody has done work elsewhere.

| Real slice requirement | What this sandbox established | What has not been exercised or accepted |
|---|---|---|
| Approved hero storyboard | Draft five-frame story, eight arrivals, settled count and stepped sprites | Owner-selected gate B hero integrated on the exact slice 03 SHA |
| Section motion and micro-interactions | Keyboard replay in the fixture | Full-page section reveals, Terminal/Undo choices, copy-command feedback and reading flow |
| Reduced motion and no JS | Fixture final HTML, static and reduced PNG byte parity | Complete slice 03 page parity after integration |
| Performance and accessibility | 4,682 gzip runtime bytes; Chromium fixture CLS 0; bounded fixture timings | Lighthouse performance/accessibility comparison of the built 03 and 04 candidates |
| Design-lead polish sign-off | Original counter-launch comprehension judgment and explicit approval of both corrected sandbox defects at 22:28Z | Before/after polish sign-off on the approved integrated page |
| Build, tests and QA candidate | Sandbox regression suite green | Actual project `build.sh` and project tests on the integrated SHA, then exact QA handoff |

The integrated acceptance workflow was **not attempted**, because the prerequisite approved candidate and assignment have not been supplied and main-lead explicitly disallows landing edits/integration before gate B and the slice 03 SHA. It is not marked acceptance-aligned or described as an attempted project test that failed. Read-only checks of an older landing page would not substitute for that missing integrated candidate. Once authorized, the new assignment must exercise the actual build, full-page browser behavior, Lighthouse baseline comparison and authored review/QA boundaries.

## Changed-output and failure-mode trace

The numbered checks below refer to the actual `ok N` observations in `chromium-green.txt` and `webkit-green.txt`, not merely the aggregate pass count. Checks 1 through 14 passed in both engines. Checks 15 and 16 ran in Chromium only and were explicitly skipped in WebKit.

| Sandbox output or requirement | Concrete check | Observed result and scope |
|---|---|---|
| `index.html` final-frame fallback | Check 1: static/reduced/no-JS screenshot comparison | At the tested 1440 px viewport, both script-enabled modes have PNG bytes equal to disabled-JS HTML. This is fixture parity, not full landing parity. |
| Desktop-only pixel cursor | Check 2: coarse-pointer context at desktop width; check 8: 320/390 px live playback | No visible cursor under emulated coarse pointer and no cursor at mobile widths. Physical-device pointer behavior is not inferred. |
| Reduced motion wins over QA rewind | Check 3: reduced preference with `?frame=0` | Final count remains 4 and rewind classes are absent. |
| Safe bad QA input | Check 4: `?frame=oops` | Valid final state, no page exception. |
| Preference change cancels playback | Check 5: real browser reduced-motion media change while playing | Mode becomes cancelled, final count 4, no overlays, and no subsequent mutation in the observation window. |
| Missing target error recovery | Check 6: `?fault=target` | Mode becomes error, complete final count and no residual overlays. This does not test failed network assets. |
| Replay and concurrent activation | Check 7: keyboard Enter replay and concurrent `Zm.play` call | A second call returns the current pending promise. Playback settles again with count 4 and no overlays or page exceptions. |
| Fixed row slots and mobile layout | Check 8: complete 320/390 px playback; check 14: complete 1440/390 px playback | No mobile horizontal overflow. Chromium reports fixture CLS 0 including startup. WebKit's missing Layout Instability API cannot establish CLS. |
| Full COPY v3 rows in `index.html` and wrapping slots in `sandbox.css` | Check 9: exact strings in both lists and text-range bounds at 320/390/1440 px | Strings equal the authored sender/subject pairs and text fits every visible tested row. Design-lead independently confirmed exact unclipped rows at 22:28Z. |
| Mobile source point and path in `story.js` | Check 10: frame-3 and live envelope/label rectangle intersections at 320/390 px | Zero intersections, with at least 40 visible placements per eight-hop playback. Design-lead independently confirmed label clearance at 22:28Z. |
| Discrete zoom geometry | Check 11: QA frame-1 rectangle inline geometry | Left/top/width/height are whole CSS pixels. Despite the broader test title, the assertion directly covers zoom rectangles, not all transforms at every frame. Transform rounding is additionally source inspection, not a separate measured assertion. |
| Hidden-document cleanup and replay return | Check 12: synthetic hidden/visible property and event | Final state has no late mutations and replay re-enables on return. An actual OS/browser tab switch remains untested. |
| Viewport geometry invalidation | Check 13: real browser viewport resize to 390 px during playback | Playback cancels and overlays are absent rather than continuing with old coordinates. |
| Exactly eight archives and bounded normal story | Check 14: actual live count mutations at 1440/390 px | Sequence is 12 through 4 with each decrement present, mode is done rather than error, and measured durations are within six seconds. The timeout-deadline cancellation branch itself was not forced. |
| Timing comparison with designer comp | Check 15: active reference renderer | Reference final count is 4 and duration is 4,488 ms. The previously reported nine seconds is not reproduced and no cause is asserted. |
| Frame and reduced-state evidence files | Check 16: captures at 1440/390 px; rebuilt strips | Fresh individual frame/reduced PNGs and timestamped capture metadata were produced. Corrected mobile strip received explicit designer approval. |
| Script syntax and leaf loading boundary | `node --check` on changed scripts and test module; all browser checks load the committed fixture over loopback HTTP | Syntax checks passed and scripts/fonts/CSS loaded sufficiently for the observed workflows. This is not project bundling, `build.sh`, production CSP, hosting or deployment verification. |
| Added-JS budget | Node `zlib.gzipSync` on each served runtime script | 3,508 bytes for runner plus 1,174 bytes for story data, total 4,682 bytes. Fixture-only instrumentation is excluded and no production bundle size is claimed. |
| Authorized edit territory | Scoped commit file lists and git status | All new/changed tracked files are under slice 04 `proof/sandbox/`. Pre-existing owner untracked files remain untouched. |

Likely failures outside these observations remain explicitly open: `dispose()` cleanup and IntersectionObserver-driven starts are not separately exercised, real hidden-tab throttling and deadline cancellation are not forced, Safari 26 ants and complete section motion do not exist in this fixture, and no integrated packaging/hosting/build/Lighthouse/QA path has been validated. Adding more synthetic checks would not remove the missing approved integration candidate. These are boundaries of the evidence, not silently passed requirements.
