# Selected hero B motion sandbox

Sandbox-only prototype against design-lead's `MOTION-SPEC.md` §3.0 at `d0a5685`. Main-lead authorized hero B only on 2026-09-29 at 22:36Z, reaffirmed the boundary at 23:02Z, and was notified when the updated B spec unblocked work. No section motion, `landing/` changes, integration or queue claim is included. The supplied comp kit and text are fixture inputs, not approval of the rest of the page.

## Run and inspect

Serve the repository over loopback HTTP and open:

`missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/hero-b/index.html`

- Default: one six-frame autoplay. The HTML default is frame 5.
- `?frame=0` through `?frame=5`: frozen storyboard frames. Reduced motion still takes precedence.
- `?static`: final HTML state with no overlays or playback.
- The real, named button replays the illustration with Enter or Space. It does not install or run the Mac app. It is disabled during playback, reduced motion and capture hooks.
- `?fault=drop` and `?deadline=100`: fixture-only recovery checks.

```sh
node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/hero-b/test-hero-b.mjs
CAPTURE=1 node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/hero-b/test-hero-b.mjs
ENGINE=webkit WEBKIT_EXECUTABLE="$HOME/Library/Caches/ms-playwright/webkit-2336/pw_run.sh" node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/hero-b/test-hero-b.mjs
```

The tests own their ephemeral HTTP server and headless browser. They use the existing Playwright installation, with `PLAYWRIGHT_PACKAGE` available as an override. No application dependency was added. `BASELINE=1` tests the designer's actual B reference page over the same server, not substituted source.

## Six beats

0. Four readable emails and eight greeked routine rows. Empty folder and Trash, closed popover, no cursor.
1. Five stepped zoom rectangles open zero's tray popover.
2. The button shows Working…. A fine-pointer watch appears directly on it, never traveling from the page origin.
3. The watch steps to the first routine row. Eight routine rows invert one by one.
4. Eight dashed outlines move and shrink together into the dated folder. The watch travels with them. Outlines sit below the paper-backed headline. The folder inverts and fills. Trash receives nothing.
5. Four exact hero emails and ages remain, the archive folder stays selected and full, the watch is gone, and the button returns to Run zero now.

At widths below 760 px and on coarse pointers, the same storyboard plays without a cursor. All movement is discrete and bounded. No fades, easing, blur or indefinite loops are introduced.

## Fixed scene reserves

Design-lead explicitly allowed a twelve-row reserve on 2026-09-29 at 23:04Z. The caption and everything below must not move, and the played end must occupy the same position as the no-JS/reduced end. These fixture sizes are not runtime constants:

| Layout | Reserved geometry |
|---|---|
| ≥1240 px | Hero height 940 px. Inbox outer slot 468 px. List stays 432 px, including after archiving. Caption top 700 px relative to the hero. |
| 640–1239 px, stacked | Inbox outer slot 468 px. Initial list 432 px; final list shrinks to four 36 px rows inside the unchanged outer slot. |
| <640 px, stacked | Inbox outer slot 548 px. Initial list 512 px: four readable 56 px rows plus eight routine 36 px rows. Final list shrinks to four 56 px rows inside the unchanged outer slot. |

Four readable rows use fixed normal-flow slots. During clutter, discrete transforms place them between routine rows, which have absolute slots. Clearing the transforms restores their final positions without layout-shift entries. Outline translations also use rounded transforms. Their discrete dimensions remain whole CSS pixels, without scale transforms or softened borders. The button has a fixed 160×36 px footprint. Only one folder sprite is displayed at a time.

The shared `../motion.js` measures live source/destination geometry. B-specific choices live in `story.js`; fixture fonts, widths and row placement live in `sandbox.css`. The font/container variation check is a compatibility probe, not permission to change the approved typography or composition.

## Evidence and limits

See `evidence/VERIFICATION.md`, engine logs and full-resolution six-column strips. These are **synthetic fixture checks in real browser engines**, not integrated landing acceptance or Safari 26 certification. Visibility cancellation uses a synthetic hidden-document event. WebKit lacks independent Layout Instability measurements. Sections, real browser tab throttling, full-page accessibility/performance, actual build/hosting/CSP and the exact slice 03 integration SHA remain outside this prototype. Main-lead must authorize those later boundaries.
