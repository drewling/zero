# Motion sandbox, redesign 3

**Current selected prototype: [hero B](hero-b/README.md), against `d0a5685` §3.0.** It lives at `hero-b/index.html` and uses the shared runner with a six-frame Finder drag story. The material below documents the historical five-frame A fixture, which remains for regression coverage, not as the selected hero.

Sandbox-only prototype for OPR.99.0.4.4, authorized by main-lead at 21:42Z on 2026-09-29. This is not slice completion, an approved hero, integration, independent QA, or a release candidate. No `landing/` files were edited and no queue row was claimed.

## Source and scope

- Storyboard source: design-lead's draft at `3e1b0ac`, with the resolved replay and cancellation decisions at `5841f04` in `MOTION-SPEC.md` sections 6 and 7.
- `motion.js`: zero-dependency, data-driven stepped runner. It keeps the reference `Zm.play`, `Zm.when`, and helper/frame shape.
- `story.js`: a five-frame hero test story with exactly eight archives at every width. This data file can be replaced after gate B without changing the runner.
- `index.html` and `sandbox.css`: a deliberately plain test fixture, not a new landing design. It reuses the design comp kit's fonts and window primitives. No account initials, badge counts, or ages appear in the fixture.

The default HTML is the final frame: four kept rows and a full dated archive folder. Without JS, with `?static`, or with reduced motion, it remains complete. `?frame=0` through `?frame=4` expose stills. Unlike the reference capture exception, the sandbox never overrides a coarse pointer or reduced-motion preference just to draw a QA cursor.

## Runner contract

- `Zm.when(root, story)` returns a controller with `pending`, `cancel()`, `dispose()`, `error`, and measured `durationMs`. `Zm.play(root, story)` returns the current promise, including when a second activation is ignored.
- Each playback owns an `AbortController`. Every paced wait and overlay helper uses that signal. Hidden-document events, viewport/pointer changes, and a switch to reduced motion stop playback and settle immediately. The story does not resume automatically.
- Replay uses a real named button. It is disabled while playing and under reduced motion, static/frame hooks, or a hidden document. It becomes available after returning to the tab when replay is permitted.
- Exceptions and the default six-second deadline also settle the final state. Overlays are removed, archive rows remain hidden in fixed slots, and the real final strings return.
- `story.finish` is a synchronous final-state restorer for mutable text and row state. When omitted, the last frame's `set` is used. Frame callbacks may use `set`, asynchronous `enter`, and `still`, as in the reference kit.
- Geometry is read before a hop, not during its stepped movement. Translations land on whole CSS pixels. Zoom rectangles are discrete rounded outline sprites, not width/height tweens. Overlays are `aria-hidden` and ignore pointer input.
- The visible folder sprite is resolved for every hop. Selecting the first SVG would target the hidden full-folder sprite before the first arrival.
- Fixed row slots prevent the Inbox window shrinking. Fixed fixture context/caption slots and sandbox-only font loading overrides prevent unrelated font swaps repositioning the test scene. This does not prescribe the production font policy.

## Run locally

From the repository root, serve the files with any static server, for example:

```sh
python3 -m http.server 8174 --bind 127.0.0.1
```

Open `http://127.0.0.1:8174/missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/index.html`.

The tests start and stop their own loopback-only server and headless browser:

```sh
node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/test-motion.mjs
CAPTURE=1 REFERENCE_TIMING=1 node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/test-motion.mjs
```

`PLAYWRIGHT_PACKAGE` can point to an installed Playwright `package.json`. The current default is the installed Node 22.16.0 global package on this machine. No package was installed or added to the application.

For the locally installed WebKit revision:

```sh
ENGINE=webkit WEBKIT_EXECUTABLE="$HOME/Library/Caches/ms-playwright/webkit-2336/pw_run.sh" node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/test-motion.mjs
```

## Verification scope

Tests compare actual rendered PNG bytes for no-JS/static/reduced parity, use real media/viewport emulation, inspect frame geometry, exercise keyboard replay, inject a missing target, and assert the full numeric arrival sequence rather than merely a final count. An `error` or `cancelled` outcome cannot pass as ordinary playback.

The hidden-tab cancellation test **synthesizes** the `document.hidden` property and visibility event. It validates the handler and cancellation behavior, not actual OS tab switching. Playwright WebKit is not an assertion of Safari 26 compatibility. Its lack of the Chromium Layout Instability API also means a zero accumulator there is not an independent CLS measurement.

The initial RED check against the designer runner reproduced invalid-frame exceptions, reduced-motion frame rewinding, and failure to remove the cursor after a live preference change. A later content-check improvement caught an early error fallback that had initially looked like a complete successful playback. It also exposed the hidden folder sprite selection bug. Startup font shifts were then diagnosed from their source rectangles rather than accepting an approximately-zero score.

Verification results and dated artifacts are recorded in `evidence/`. Frame-strip columns are frames 0, 1, 2, 3, 4 from left to right.

## Remaining boundaries

- Design-lead judged the historical A counter-launch as archiving and confirmed its two corrections at 22:28Z. Owner subsequently selected B. B's sandbox strips have their own review boundary.
- This prototype does not implement the full section designs, a finite ants sample, or the optional Terminal reveal. Safari 26 ants jitter and its fallback remain unverified. The settled spec requires six cycles, then still, and no motion under reduced preferences.
- No Lighthouse 03/04 comparison exists yet because slice 03 and integration have not been authorized. Build/test checks on `landing/`, production font policy, and the actual approved hero must be verified on the later exact integration SHA.
- Integration remains blocked on gate B, the real queued assignment, and the slice 03 SHA. This commit must not be deployed or treated as the QA handoff.
