# Frozen page B sandbox refresh verification

2026-09-30. Sandbox-only refresh requested by design-lead at 01:45Z. Contract remains MOTION-SPEC §4.2 `e58ff8f`. Selected source is frozen comp B `50bf121`, DRAFT4 / COPY-B `85dfe6f`. No comp or landing file was edited, no shared branch rebase was performed, and no application dependency was added.

## What changed and what actually improved

The prior `39aa729` snapshot was stale. `refresh-source-red.txt` shows S13 failing exact frozen reader markup for `#install`, `#how-band`, `#undo` and `#command`. After refresh, those sections plus the hero, navigation and footer match the frozen source's DOM exactly. `kit.css` and `page.css` match the frozen CSS byte-for-byte. The ledger now presents the two recipient disclosures first, followed by sorting cost, Google sign-in and installer information. Copy facts and the dated price are mirrored from the selected copy source, not independently researched or endorsed by this motion seat.

The expanded final run then found a real desktop reader race: `refresh-chromium-final.txt` records S3 receiving `seen` instead of playback at 1440px. The first pre-observer callback arrived after the reader had scrolled, but treated that arrival as initial sight. S16 reproduces `seen !== armed` deterministically with controlled observer delivery in `refresh-observer-red.txt`. The same regression fails with the exact `50bf121` comp runner, in `refresh-comp-observer-red.txt`. This comparison uses the frozen runner in the sandbox, not a test of the live comp page or permission to edit it.

The minimal shared sandbox runner repair captures initial scroll position and only uses the asynchronous initial-sight shortcut if the scroll position is unchanged. The existing synchronous initial-box, native hash and in-page link rules remain intact. S16 and S2 then pass in `refresh-observer-green.txt`; the full repaired real reader S3 and authored-server S14 also pass. The comp owner received the exact reproduction and minimal diff to port in their own lane. `reference/pre-observer-refresh.js` preserves the exact before-state runner.

## Final whole-result run

All mapped checks were rerun on the repaired runtime, not just S16:

- `refresh-chromium-repaired.txt`: **16 pass, 0 fail, 0 skip**. Full S1-S16 mapping and mobile/desktop captures.
- `refresh-webkit-repaired.txt`: **14 pass, 0 fail, 2 skip**. Optional S7 captures and Chromium-only native Clipboard API S10 are the skips.
- `refresh-hero-b-chromium.txt` and `refresh-hero-b-webkit.txt`: **10 pass, 0 fail, 1 skip each**. Optional storyboard generation skipped. Selected hero behavior and strict PNG parity rerun after the generic runner change.
- `refresh-hero-a.txt`: **14 pass, 0 fail, 2 skip**. Historical consumer only, not selected design. Reference timing and optional captures skipped.
- `git diff --check` passed for the sandbox territory.

Compatible WebKit 2336 is an installed alternate, not the package-pinned revision and not Safari. Its Layout Instability API is unavailable. Zero values printed by the historical hero accumulator are not a WebKit CLS measurement.

## Requirement-to-observation map

| Requirement or changed reader output | Checks rerun | Observed result |
| --- | --- | --- |
| Frozen DRAFT4 text, recipient hierarchy, reordered five-row ledger, changed Rules/Undo/install explanation | S13 | Exact DOM comparison for seven public reader regions passes. Two recipient plates, row order, dated price string and unchanged hero/nav/footer match frozen source. |
| Frozen trust styles and hidden-control fix | S13, S5 | Both CSS files are byte-identical to frozen input. Clipboard-unavailable button is absent, not exposed by `.btn` display. |
| Complete default HTML with no JS, static and reduced end states | S1 | Exact full-page PNG equality at 320, 390, 760, 1440 and 2560px, including reduced plus QA frame 0. Clipboard is unavailable consistently for this parity comparison. |
| 13 Rules lines, five complete Undo rows and empty cut sixth, five ledger entries, full command | S1, S11, S13 | All contents/counts preserved. Cut row has no text and is aria-hidden. |
| Native first-sight hash and real Install anchor arrival never rewind | S2 | All four native target hashes and the clicked hero Install link remain complete `seen` final states. |
| Purposeful stepped Get Info, Rules, Undo and Terminal beats | S3 | Actual reader scrolling observes pre-arming, playback, intermediate row/line counts, four tab states, zoom rectangles and partial command glyphs; every beat reaches complete final once. |
| No horizontal overflow or downstream motion layout shift | S3, S14 | No observed overflow. Chromium reader-motion CLS exactly 0 at all five widths after fonts are ready. WebKit supplies no CLS metric. |
| Stepped geometry, cursor-free section stories and finite Terminal blink | S3, S11 | Integer zoom coordinates, aria-hidden pointer-inert overlays, no cursor DOM. Terminal blink is three `steps(1)` iterations. |
| Reduce Motion interruption of playing and armed stories | S4, S15 | Playing stories settle fully with no later mutations; offscreen armed ledger settles before reveal and does not replay when scrolled into view. |
| Missing observer or failed target keeps complete final | S6 | Missing observer leaves final content. Removed app icon produces an honest error outcome with no stranded rows/overlays. |
| Visibility interruption has no late writes | S8 | Controlled hidden-document property/event settles every scene. This is synthetic visibility, not an OS tab-switch test. |
| Copy success, rejection, unavailable API, pending repeat and rejection during typing | S5, S9, S10 | Exact full command copied using a real isolated Chromium Clipboard API and Enter. Stubbed denied/pending paths retain focus and select full command with polite manual-copy status; concurrent writes ignored. No installer command executed. |
| Keyboard order, visible focus and readable policy | S11 | Actual browser key traversal matches visible controls; Copy has a 3px outline and Rules stays readable. No screen-reader product tested. |
| Layout/copy independence | S12 | Changed six-row ledger and resize interruption preserve every row with complete final state. Beats query DOM, not fixed strings. |
| Delayed first observer callback following reader scroll | S16, S3, S14 | Controlled prior sandbox and frozen kit fail `seen !== armed`; repaired sandbox arms then plays. Whole real reader suite and authored-server route pass after repair. |
| Authored static-server packaging and public reader path | S14 | Exact authored `acceptance/serve.py` serves the sandbox, CSS/fonts/JS, keyboard Copy and complete normal reader playback without recorded HTTP or page errors; context and owned server close afterward. |
| Changed visible ledger output | S7, bounded 390/1440 inspection | Recipient plates lead clearly, paper-backed disclosures remain legible against dither, all five rows and the price/date are visible and unclipped. Mobile wraps the second recipient into two readable lines. This is implementing-seat observation, not independent design acceptance. |
| Existing selected hero B | Complete B suites in both engines | Six frames, correct subjects/ages, eight simultaneous dragged outlines, single Working-owned watch, empty Trash, replay exclusion, preference/resize/visibility/error fallbacks and strict played/static/no-JS/reduced parity remain passing. |
| Historical hero A | Complete A suite | Its previous playback, labels, keyboard replay, final parity and cancellation/error checks remain passing. |
| Runtime package budget | Byte/hash/gzip measurement below | Combined runtime JS 7412 gzip bytes, below 8192. No added dependency. |
| Approved landing integration and final owner/QA acceptance | External gate | Not entered, not represented as passing. Build remains held and this is a copied prototype. |

## Final Chromium reader timing

Controller milliseconds, excluding Terminal's subsequent three-second decorative blink:

| Width | Get Info | Rules | Undo | Terminal | Reader CLS |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 320 | 1301 | 1367 | 1243 | 1027 | 0 |
| 390 | 1308 | 1369 | 1239 | 1031 | 0 |
| 760 | 1310 | 1384 | 1242 | 1034 | 0 |
| 1440 | 1311 | 1382 | 1234 | 1028 | 0 |
| 2560 | 1302 | 1376 | 1243 | 1029 | 0 |

Selected B Chromium timing is 3396/3397/3718/3718ms at 320/390/760/1440, with observed CLS 0. Compatible WebKit timings are 3419/3409/3758/3746ms, without a CLS API.

## Frozen snapshot identity

Files under `reference/50bf121/` were compared directly against `git show 50bf121:<source-path>`:

| Snapshot file | Git blob |
| --- | --- |
| `index.html` | `04b58710f0e36b57cc8932bb8b21997204682c93` |
| `motion.js` | `6a528f0763ebfa49a354b381ca315450ec765a35` |
| `sections.js` | `8edaa4081274652790c127c33fde8f8cc0d3bffe` |
| `kit.css` | `68e86e11b60fbe491f288a1bb06b530fe8219cc3` |
| `page.css` | `cda2e63d74492b20636c1d1926dc1234021da408` |

## Final runtime identity

| File from sandbox root | Source bytes | Gzip bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `motion.js` | 13935 | 4518 | `c828e9e46be3ccc47e1787e5672d4c209bbd62fac93ed1c353c63b714b8fa734` |
| `hero-b/story.js` | 2343 | 952 | `ce228783ba678d4f2bf4d4d6b4a62f7dc700ade47adaccfb3af2771b2f9051e2` |
| `sections/sections.js` | 5248 | 1942 | `ed670d6d6358ace2cb70681af20d388efadb0871c46d20a0ee2a815a870ff818` |
| Combined | 21526 | **7412** | Limit **8192** |

## Reproduce the selected sandbox

From repository root:

```sh
python3 missions/website-redesign-3/slices/02-references-and-comps/proof/acceptance/serve.py 8174 .
# Open http://127.0.0.1:8174/missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/sections/index.html
CAPTURE=1 node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/sections/test-sections.mjs
ENGINE=webkit WEBKIT_EXECUTABLE="$HOME/Library/Caches/ms-playwright/webkit-2336/pw_run.sh" node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/sections/test-sections.mjs
# Expected RED comparison of frozen comp observer, not a production test:
REFERENCE_RUNNER=50bf121 node --test --test-name-pattern='S16:' missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/sections/test-sections.mjs
```

## Acceptance limitation and stop condition

This is the authorized sandbox refresh, not the landing build. The hero in the section fixture is static context, with its animated implementation verified separately. Combined final-page layout/observers, the slice-03/04 Lighthouse comparison, final owner approval and independent design/QA acceptance await the live integration gate and exact approved slice-03 SHA. The prior live gate check is documented in `VERIFICATION.md`: slice 04 blocked, QA row blocked on selected design, owner explicitly holds build and prohibits landing edits/release/push/deploy. The latest designer instruction likewise keeps comps under their review and limits this seat to sandbox refresh.

All authorized prototype checks are now satisfied. Continuing into production to manufacture a closed acceptance loop would violate that boundary. No Safari, actual OS tab-switch, screen-reader, owner browser clipboard permission UI or deployment acceptance is claimed. Old report `VERIFICATION.md` and its logs describe the `f1d36e0`/`39aa729` candidate; old PNG bytes remain recoverable at that commit, while current capture paths now show DRAFT4.
