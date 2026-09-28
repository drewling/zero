# Motion brief: "The board sorts"

Slice OPR.99.0.2.1 · design-lead@zero · 2026-09-28 · **planning material, awaiting owner decision**

Scope: this is direction only. Nothing in `landing/` was edited and nothing was deployed. Per the 14:41Z scope correction (`1c55bd1`), no build, QA or release is dispatched without a separate go-ahead from the owner. The runnable prototype lives at `proof/prototype/`. It copies the live page and adds `motion.js` (about 5.8 KB gzip, including prototype-only instruments) and `motion.css` (about 1.6 KB gzip).

## 1. Thesis

The page already says "Keep the mail that needs you." Motion should **show the sort happening** instead of decorating the page. A departure board is a machine that decides where things go. So the motion is the board working, once and legibly, at the points where the product makes a claim:

1. **It decides.** The rules table routes each kind of mail to Stays or Archived.
2. **Nothing is lost.** Archived mail moves to a dated label and can come back.
3. **You can start.** The install steps "board" like departures.

Everything else stays still. No particles, no ambient loops, no scroll-jacking, and no fade-up on every section.

## 2. Focal Canvas: the sort track (the rules table)

| | |
|---|---|
| Job | Turn the static "Examples from zero's default rules" table into a witnessed decision: each rule is routed, and you see which ones stay. |
| Trigger | Plays **once** when the board is 45% visible (IntersectionObserver). "Run the sort again" replays it. Hover does nothing (pointer effects rejected, §8). |
| Choreography | Per row, staggered 170 ms: a ticket travels the row divider (520 ms, ease-out) to the verdict dot. The verdict word scrambles through 4 split-flap ticks (40 ms each), then lands. **Stays** rows keep a lit yellow track and a short bloom. **Archived** tickets drop 14 px and fade over 620 ms, and their labels dim. Total 2.16 s, then the board settles and the canvas stops drawing. |
| Truth | The real verdict text never leaves the DOM. The scramble is a `data-scramble` overlay on `.status-word`, so screen readers and copy/paste get "Stays" or "Archived". The canvas is `aria-hidden`. The existing footnote ("This isn't a live inbox… The AI can sort a message wrongly") stays unchanged directly under the effect. |
| Why Canvas and not CSS | The ticket has to travel between two measured DOM points (row start to verdict dot) on seven rows whose geometry changes with wrapping at every width. It carries a gradient trail and ends in either a bloom or a drop. In CSS that means seven extra positioned elements per row state, keyframes recomputed from JS on resize, and radial-gradient layers that repaint the table. One canvas behind the table draws all of it in 0.07 ms per frame (measured, §6), leaves the table DOM untouched, and can be seeked deterministically for review. |

Frames (desktop 1440, Aside capture): `storyboard/d-sort-0.jpg` (unsorted: dots dim, verdicts pending) → `d-sort-700.jpg` (row 1 decided, row 2 scrambling "NYVRK", rows 3 to 5 tickets in flight) → `d-sort-1300.jpg` (Stays lit, archived tickets dropping, newsletter scrambling) → `d-sort-settled.jpg`.

## 3. Second Canvas: the recovery rails ("Nothing is deleted")

| | |
|---|---|
| Job | Make the reversibility claim concrete: the same 7 conversations are always present. Archiving moves 4 of them from the Inbox rail to All Mail with a dated recovery label, and a restore moves them back. The header reads "illustration · same 7 · none deleted". |
| Source truth | Matches `keeper_server._run_undo`: restore re-applies INBOX to the threads under the dated label. Nothing is deleted. |
| Trigger | Plays once at 60% visible. The "Show a restore" button reverses it and becomes "Show the archive again". It is a real `<button>`, so it is keyboard- and screen-reader-operable. |
| Timing | 900 ms total, 80 ms stagger, eased arc. The label tag fades in at the halfway point of each move. |
| Why Canvas | It is a small diagram whose only state is time and direction. The canvas is 150 px tall, draws in 0.02 ms, and redraws on resize and after fonts load. As DOM it would be 7 animated nodes plus rails. It is acceptable either way. See the §9 question on whether to keep it. |

Frames: `d-rail-0.jpg` (all 7 in Inbox) → `d-rail-450.jpg` (archiving, tags arriving) → `d-rail-900.jpg` (4 in All Mail with tags) → `d-restore-450.jpg` (restoring) → `d-restore-live.jpg` (after a real click: all back in Inbox, button reads "Show the archive again").

## 4. Supporting beats (DOM and CSS, no Canvas)

| Beat | Trigger | What moves | Why |
|---|---|---|---|
| Hero flap settle (existing) | Load | Unchanged from production. The tiles cycle and settle in under 1 s, once. | It is already the signature. No competing headline loop. `d-hero-flap-mid.jpg`, `d-hero.jpg` |
| Install steps board | Install steps 25% visible, once | Step number tiles flip down (rotateX 80°→0, 420 ms) and step text wipes in (clip-path, 600 ms), staggered 120 ms. | The install path reads as a sequence of departures. **`:focus-within` shows everything instantly** so a keyboard user tabbing to Copy never waits. `d-install-boarding.jpg` (mid), `d-install-settled.jpg` |
| Copy acknowledgement | Click Copy | The button label flaps once (existing text change, observed via MutationObserver). | It confirms the one action that matters on the page. |
| FAQ sign | Open or close a `<details>` | The chevron flaps (200 ms, two steps) and the answer eases in (280 ms, 4 px). Gated by `.faq-ready`, so nothing animates on load. | Feedback for a click, not decoration. |

Explicitly **not** animated: the headings, the body copy, the app screenshot, the "Before you install" facts, the footer and the nav.

## 5. Reduced motion and static fallback

- **`prefers-reduced-motion: reduce`** (simulate with `?rm=1`): no sort track, so the table renders exactly as production with its final verdicts (`d-rm-sort.jpg`). There's no boarding either, so install steps are visible immediately. The hero is already static in production. The rails show the settled archive state, and the button still works but swaps the state instantly with a 220 ms opacity settle, keeping the explanation without the travel (`d-rm-undo.jpg`).
- **No Canvas or no JS** (simulate with `?nocanvas=1`): the canvases and rail block stay `hidden`, and the page is byte-for-byte the production reading order (`d-nocanvas-sort.jpg`, `d-nocanvas-undo.jpg`). The "Run the sort again" button is also `hidden` until the track initialises, so there are no dead controls.
- All content is present in HTML before any script runs. Motion only adds on top.

## 6. Baseline, budget and measurements

Baseline: production https://zero.headless.com/, measured with Aside at 1440×900, DPR 2 (task `266717zdrp`).

| Metric | Production today |
|---|---|
| DOMContentLoaded / load | 647 ms / 2,018 ms |
| Transfer: HTML / CSS+fonts (3 links) / JS / image | 16.6 KB / 236 KB / 2.1 KB / 1,294 KB |
| CLS | 0 |
| Long tasks | 0 |
| rAF after reload (1.5 s) | 80 frames, mean 19.0 ms, max 33.8 ms |
| LCP | not reported by Aside's buffered observer (null) |
| Running `document.getAnimations()` after load | 0 |

Prototype cost (Aside, local server, same Chrome, task `117558q29o`):

| Metric | Measured | Budget for the build |
|---|---|---|
| Added bytes | +5.8 KB gzip JS (including prototype-only instruments), +1.6 KB gzip CSS; no new images, fonts or libraries | ≤ 10 KB gzip total |
| Sort draw, synchronous bench (200 seeked frames) | **0.067 ms/frame** | ≤ 2 ms/frame |
| Rail draw, same bench | **0.019 ms/frame** | ≤ 2 ms/frame |
| Live playback, script time per rAF callback | mean 2.1 ms, max 19.9 ms (first frame, includes fonts and measure) | mean ≤ 4 ms |
| Frames drawn when idle or settled | 0 (rAF only while playing) | 0 |
| CLS from motion | not measured on the prototype. The sort canvas is absolutely positioned inside the existing board, so it can't shift layout. The rail block and the replay button are unhidden by the deferred script, below the fold. The build should reserve their space in CSS so a slow script can't shift content | 0 |

Caveat, stated plainly: Aside's Chrome was delivering only about 30 fps even with **nothing animating** (idle rAF on the prototype: mean 33 ms). A same-session idle sample on production returned no frames at all, so that session was throttled. Live frame pacing captured through Aside therefore reflects the automation browser, not the animation. The synchronous per-draw bench is the reliable number. The build slice should re-measure pacing on a real, unthrottled browser and a mid-tier Mac before release.

## 7. Lifecycle rules (the builder must keep these)

1. rAF runs **only while a timeline is playing**. Settled means no loop.
2. A hidden tab pauses the timeline (`visibilitychange`), and it resumes where it left off.
3. Offscreen before first view: the timeline rests at t = 0 (unsorted), and plays once when seen. After that it never auto-replays on scroll.
4. ResizeObserver re-measures row geometry and redraws the current frame. The canvas DPR is capped at 2.
5. After `document.fonts.ready`, settled frames redraw so canvas text uses Archivo and Geist Mono.
6. Every frame is a pure function of time, so `?seek=` and `zeroMotion.seek()` reproduce any frame for QA.
7. Interruption: pressing replay mid-run restarts from 0, and flipping the rail mid-move restarts in the new direction. Neither queues or stacks.
8. Prototype-only hooks (`?seek`, `?rm`, `?nocanvas`, `?slow`, `?at`, `stats()`, `bench()`, `mobile.html`) are **not** for production. The builder strips them or gates them behind a dev flag.

## 8. Alternative considered (materially different)

**"Split-flap everywhere": a DOM-only departure board.** Every section heading would re-flap on entry, and the rules table would become flap tiles cycling to its verdicts, with no Canvas.
- For: it is the most on-brand and needs zero Canvas.
- Against: it repeats the hero's effect six times, which weakens the signature. It animates headings that carry no state change (the "every section reveals" pattern we are avoiding). Flap tiles for full row verdicts roughly triple the DOM in the table, and it doesn't satisfy the requested Canvas effect.
- Rejected, but it is the fallback if the owner decides Canvas isn't wanted.

Also rejected: a pointer-reactive "departure board" background (ambient and distracting on a trust-heavy install page), and scroll-scrubbed sorting (it scroll-jacks and fails on trackpad inertia).

## 9. What needs owner approval before any build

1. **Direction:** approve "The board sorts" (focal sort track, recovery rails, install boarding, micro-feedback), or choose the DOM-only alternative.
2. **Second Canvas:** keep the recovery rails (my recommendation, because it proves the "nothing is deleted" claim) or drop it to keep a single Canvas moment.
3. **Replay controls:** keep the visible "Run the sort again" and "Show a restore" buttons (recommended, they are honest demos) or make both effects play-once with no controls.
4. **Pointer interaction:** none is proposed. Confirm that none is wanted.
5. **Scope of the build slice:** DOM, CSS and JS only in `landing/`. No new assets or dependencies, with the §6 budget and §7 lifecycle as acceptance criteria.

## 10. Method and limitations

- All captures and measurements were made by design-lead through **Aside** against the prototype on `127.0.0.1:8741` and against production. No Playwright.
- **Mobile is iframe width, not device emulation.** The 390 px frames come from a 390×844 iframe inside desktop Chrome (the `mobile.html` harness), with no mobile UA, touch or device DPR. The harness reported `scrollWidth 390 = clientWidth 390` (no horizontal overflow) for the sort, rail, install and reduced-motion states. Captured mobile frames: `m-hero.jpg`, `m-sort-700.jpg` (mid-sort: tickets in flight, "NYVRK" scramble, the verdict column wraps its header but not its rows), `m-sort-settled.jpg` and `m-rail-450.jpg` (mid-archive, with the rightmost tag inside the frame). Aside's screenshot command timed out repeatedly on the mobile install and reduced-motion states, so those two are **not** proven visually, only width-checked. The build slice's QA owns that proof on a real narrow viewport. The prototype's `?at=` jump had also run before the rail was unhidden. It was fixed before `m-rail-450.jpg` was recaptured. At the 760 px breakpoint the geometry is re-measured per row, and the same code path runs.
- Frames were seeked (`?seek=`), not screen-recorded, except `d-restore-live.jpg` (a real click) and `d-hero-flap-mid.jpg` / `d-install-boarding.jpg` (captured during live playback).
- Fixed during review: the first capture pass scrolled with smooth-scroll, so the frames showed the hero (discarded). The resize redraw also turned t = 0 into "settled". Both were fixed before the frames listed here were recaptured. The row verdict DOM writes now happen only on state change, not every frame.
