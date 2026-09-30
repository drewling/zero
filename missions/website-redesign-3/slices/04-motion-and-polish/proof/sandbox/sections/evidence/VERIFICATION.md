# Selected B section-motion verification

Historical report for candidate `f1d36e0` against `39aa729`. Current source and captures have been refreshed to DRAFT4 `50bf121`, documented in [REFRESH-VERIFICATION.md](REFRESH-VERIFICATION.md). Historical capture bytes are recoverable at `f1d36e0`. The original logs below are retained without rewriting their observed results.

2026-09-30. Contract `e58ff8f` §4.2, selected source `39aa729`. This report describes the scoped sandbox, not the production landing page. All paths below are relative to this `evidence/` directory unless noted.

## Acceptance boundary

The authorized deliverable is a prototype at `sandbox/sections/index.html`, with preserved selected hero B coverage. The page is a **copied, frozen fixture** and its hero is static context. Real browser scrolling, keys, rendered pixels and isolated Clipboard API operations exercise that fixture, but they do not substitute for the eventual approved landing integration. No `landing/` edits, production build, deployment, Lighthouse comparison or Safari acceptance occurred. Gate B, the real assignment and the exact slice-03 SHA remain required. Copy remains provisional.

## Complete final mapped run

- `chromium-final.txt`: S1 through S12, **12 pass, 0 fail, 0 skip**, including full captures and actual partial typing capture. This reran the whole mapping on the final runtime, not just the corrected tests.
- `webkit-correct-revision.txt`: **10 pass, 0 fail, 2 skip**. S7 optional screenshots and S10 Chromium-only native clipboard are the explicit skips. Runtime and section CSS are identical to the final Chromium run. The later test-only S7 addition captures live partial typing, not a runtime change.
- `hero-b-chromium-final.txt` and `hero-b-webkit-final.txt`: **10 pass, 0 fail, 1 skip each**. The skipped item is optional six-frame screenshot generation. These run all behavioral and pixel assertions on the selected hero consumer after the actor-layer correction.
- `hero-a-consumer.txt`: historical runner consumer, **14 pass, 0 fail, 2 skip**. Reference timing and optional evidence generation are skipped. A is not the selected hero.
- `git diff --check` passed for the complete sandbox territory. No new application dependency was introduced.

WebKit 2336 is a compatible installed alternate, not Playwright's pinned 2311 revision. The first attempted 2248 revision failed at protocol setup (`Console.enable` unavailable), recorded in `webkit.txt`; it supplied no page-level evidence. Playwright WebKit is not Safari. Its zero-valued historical hero accumulator must not be read as a CLS measurement because Layout Instability entries are unavailable there.

## Requirement to observation mapping

| Requirement or changed public output | Check | Observed result |
| --- | --- | --- |
| Selected B final content, 13 Rules lines, five complete Undo rows plus a cut empty sixth row, five ledger entries, exact installer command | S1, S11 | Counts and full command match the frozen input. Peek has no text and is aria-hidden. |
| Default HTML, no JS, static and reduced end states remain complete, including reduced plus QA frame 0 | S1 | Rendered PNG bytes match at 320, 390, 760, 1440 and 2560px with Clipboard API unavailable consistently. Copy is a progressive enhancement and is deliberately absent in no-JS mode. |
| First-sight and same-page arrivals never rewind | S2 | Native initial hash arrivals for each of four targets settle as `seen`, with target content complete and no stepping/overlays. Actual hero Install anchor reaches a complete ledger. Unrelated offscreen scenes may still pre-arm. |
| Four purposeful beats, pre-arming and one-shot reader playback | S3 | Actual 100px reader scrolling observes `armed` then `play`/`done` for every scene, intermediate rows/lines, all four Rules tabs, zoom rectangles and partial Terminal glyphs. Returning to the page top leaves complete final content. |
| Stepped 1-bit geometry, no animation cursor for these stories | S3, S11 | Zoom coordinates are whole pixels, overlays are aria-hidden and pointer-inert, no cursor DOM appears. Finite cursor blink is exactly three iterations with `steps(1)`. |
| Caption and downstream layout remain still, no overflow | S3 | Layout Instability total during reader motion is exactly 0 in Chromium at all five widths, after fonts are ready. No observed horizontal overflow. WebKit has no independent CLS result. |
| Changing to reduced motion interrupts safely | S4 | Every story settles to the complete final state, all overlays/stepping removed; the final DOM remains unchanged after 900ms. |
| Successful Copy uses keyboard focus and accessible status | S5, S10 | Stubbed success and actual isolated Chromium Clipboard API both copy the exact full command. Enter activation preserves `#copy` focus and visible polite `role=status` announces `Copied`. The command is never executed. |
| Clipboard rejection and unavailable API remain usable | S5, S9 | No API hides the button. Rejection announces the exact manual-copy text and selects the entire command. Rejection during typing cancels before selection; selection and button focus survive another second. |
| Repeated Copy does not race | S9 | Two activations while a write is pending produce one API call, then the rejection fallback remains intact. |
| Missing observer and failed story target fall back truthfully | S6 | Without IntersectionObserver all scenes stay final. Removing the app icon target produces an `error` outcome with complete content and no overlays, not a false normal-playback pass. |
| Visibility cancellation has no late writes | S8 | A **synthetic** hidden-document property/event interrupts each story, restores complete content and produces no later DOM mutations. This is not an actual OS tab-switch test. |
| Actual keyboard traversal, policy readability and focus treatment | S11 | Browser keyboard order matches all visible links/buttons, Copy has a 3px focus outline, Rules is not aria-hidden, and the cut row remains nonverbal. No screen-reader product was tested. |
| Font/container independence and pending copy changes | S12, hero B geometry check | A six-row ledger with changed words cancels cleanly on resize and preserves all six rows. Hero B still works under altered fonts/container widths. Counts and positions are queried, not derived from fixed copy strings. |
| Mobile/desktop visible section output | S7 plus two bounded visual rounds | 390/1440px captures show readable Rules policy, five real Undo rows with the cut sixth and row-five balloon, all ledger paragraphs, and actual partial Terminal typing. Terminal's last QA frame correctly shows the full command; `*-term-live-partial.png` supplies the intermediate paint evidence. |
| Existing selected hero B behavior | Full B suite | Exact subjects/ages, six frames, eight selections and simultaneous outlines genuinely reaching the dated archive folder, Working-owned watch only, empty Trash, actual Enter replay, repeated activation exclusion, resize/reduced/synthetic visibility interruption, missing-target/deadline fallback and coarse-pointer exclusion all pass. Played/static/no-JS/reduced pixels are byte-identical. |
| Existing historical consumer | Full A suite | Its replay, eight-hop playback, no-JS/reduced parity, copy strings, label noncollision, cancellation and error paths remain passing. |
| Payload and packaging | Source hashes and gzip below, HTTP response/error checks in S1/S3 | Combined generic runner, hero B story and section stories are 7331 gzip bytes, below 8192. Local CSS/font assets load without recorded HTTP/page errors. No dependency added. |
| Production integration or owner/design acceptance | External boundary | Not performed or claimed. Await exact approved page/copy and integration authorization. |

## Concrete reader timing

Final Chromium run, measured controller durations in milliseconds. Terminal duration excludes its subsequent finite three-second decorative blink.

| Width | Get Info | Rules | Undo | Terminal | Reader-motion CLS |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 320 | 1296 | 1381 | 1244 | 1019 | 0 |
| 390 | 1293 | 1369 | 1244 | 1015 | 0 |
| 760 | 1296 | 1375 | 1245 | 1020 | 0 |
| 1440 | 1297 | 1377 | 1244 | 1017 | 0 |
| 2560 | 1297 | 1367 | 1235 | 1013 | 0 |

Final selected hero B Chromium playback is 3378/3377/3700/3699ms at 320/390/760/1440px, with observed CLS 0. Compatible WebKit timings are 3406/3404/3734/3741ms, without a CLS API.

## Before/after evidence, not just a final-state assertion

1. `reference-final-red.txt`: the frozen designer runner/stories fail all three mapped reference checks S4/S5/S9. Mid-reveal reduced motion leaves ledger rows hidden, author `.btn` display exposes the nominally hidden fallback button, and repeat pending Copy activates twice.
2. `pre-final-red.txt`: the prior hardened runner fails S2, rewinding a native hash arrival into `play` rather than preserving `seen`.
3. Terminal flow text rewrites initially produced measured nonzero CLS, including a whitespace text-fragment source at 390px. The final implementation never rewrites the full command's line boxes. It paints measured, absolute glyph sprites and restores the original code, giving exact zero observed motion CLS in S3.
4. An existing hero B exact-PNG check failed at 1440px. Decoding both PNGs found precisely two differing popover-corner pixels at `(1406,169)` and `(1407,169)`. `hero-b-parity-late.txt` shows the mismatch persists after 300ms. `hero-b-prior-runner.txt` reproduces it with the exact pre-section runner, so the new observer changes are not its cause. A stable compositor layer on `.pop` in `hero-b/sandbox.css` makes the same strict played/static/no-JS/reduced PNG assertions pass in Chromium and compatible WebKit. No pixel tolerance was added. `hero-b-stable-layer.txt` and both full B logs record the correction. Diagnostic PNGs remain in `../../hero-b/evidence/parity-1440-*.png`.

The full section runtime was rerun after the complete requirement mapping, and both selected hero consumer suites ran after the layer correction. The initial full B run generated a large Buffer diff that looked stalled; bounded PNG diagnostics replaced that output, without weakening the assertion. The final section task also issued a watchdog warning because its output was redirected until completion; its complete log ends with 12 passes and zero failures.

## Runtime identity and budget

Gzip sizes are independently compressed files, summed conservatively. Test fixtures, reference copies, CSS, fonts and PNG evidence are not counted as runtime JavaScript.

| File | Source bytes | Gzip bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `../motion.js` from section directory | 13774 | 4446 | `d169c95b56cd0a9f8f49bc3d08734085243041909d11de0f84139cb666d6770b` |
| `../hero-b/story.js` from section directory | 2343 | 952 | `ce228783ba678d4f2bf4d4d6b4a62f7dc700ade47adaccfb3af2771b2f9051e2` |
| `sections.js` | 5237 | 1933 | `2d89c1264e06ef1d9458302fa79f18de0c522573d14bfeefe46774d3099f5b1e` |
| Combined | 21354 | **7331** | Limit **8192** |

## Live acceptance-gate check, 01:41Z

Entry to the real acceptance workflow was checked against the authored slice and current queue, rather than assuming fixture passes release the build. `slices/04-motion-and-polish/SPEC.md` is still `status: blocked`, depends on slices 02 and 03, and explicitly requires the 03/04 built-page Lighthouse comparison, design sign-off and exact QA handoff SHA. Live QA obligation `qitem-20260930005834-0ce76331` is **blocked** on designer obligation `qitem-20260930005832-91c2fccb`, which is in progress. Its owner instruction explicitly says: build held, no `landing/` edits, no slice-03 release, no push/deploy, and development-motion sandbox only. The QA query returned one row at limit 10000, so it was not truncated.

That gate prevents entering the integrated build/end-user acceptance path. No landing test was bypassed or represented as passing. Sandbox observations and complete post-mapping rerun remain valid, but they are **not closure of integrated acceptance**. Continue only when the live owner gate permits integration and supplies the approved slice-03 SHA.

## Remaining limits

- The copied page hero and animated hero are verified separately. The final complete landing page, their combined observer/layout interaction, final copy and production font policy require checks after actual integration.
- Final owner acceptance and independent design/QA judgment are not inferred from these tests. Visual observations here are the implementing seat's bounded checks.
- Denial/pending clipboard and document-hidden tests are controlled fixtures. A real isolated Chromium clipboard success was exercised, not an authenticated owner's browser. Actual Safari, OS tab switching, assistive technology and clipboard-permission UI remain outside this proof.
- Historical hero styles still consume the designer's shared kit. The section page itself freezes the approved input snapshot and does not silently follow uncommitted designer changes.
