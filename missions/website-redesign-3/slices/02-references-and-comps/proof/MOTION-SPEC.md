# MOTION-SPEC: zero redesign 3 (DRAFT, early publish)

Status: **draft for development-motion@zero**. Nothing here is approved for `landing/`. Implementation waits for main-lead's authorization after owner gate B. Any prototype belongs in slice 04 `proof/sandbox/`.

Reference prototype: `comps/kit/motion.js` (the `Zm` runner) plus `comps/hero-a/index.html`. To serve it, run `python3 -m http.server` from `proof/comps`. The page supports `?frame=N` for a still of frame N and `?static` for the end state.

## 1. Grammar (applies to every motion on the site)

| Rule | Why |
|---|---|
| **Stepped only.** Every change jumps in whole steps (`steps()` in CSS, or a fixed-count loop in JS). No easing curves, no opacity fades, no blur, no scale-with-smoothing. | A one-bit Mac had no alpha channel and no easing. Tweened motion is the thing that makes retro sites look like modern sites in costume. |
| **Pixel-snapped.** Animated elements land on whole CSS pixels (`Math.round`). | Half-pixel positions blur the 1-bit edges and the dither. |
| **The HTML default is the final frame.** The page ships showing the finished state. JS adds `lt-K` ("before frame K") classes to rewind, then plays forward, removing them. | With no JS, a JS error or reduced motion, the page shows the same finished, truthful state. There's no flash of an unfinished state and no layout shift. |
| **Reduced motion = final frame, no playback.** `prefers-reduced-motion: reduce` renders `?static`. Marching ants stop too. | WCAG 2.3.3. Also, the final frame is a full explanation on its own. |
| **Plays once.** Hero on load (700 ms delay), sections on first intersection (`IntersectionObserver`, threshold ~0.4). No loops except the ants. | Looping motion competes with reading. |
| **No layout movement.** Motion happens on absolutely positioned overlays (cursor, zoom rects, flying envelopes) or on content whose box does not change size (the counter uses `tabular-nums`, rows hide in place inside a fixed-height list). | CLS 0 and nothing jumps under a reader's eyes. |
| **The cursor is desktop-only.** Draw it only at >= 760 px and with a fine pointer (`(pointer: fine)`). On touch, the same frames play without the cursor. | A fake arrow on a phone reads as a bug. |
| **Timing budget.** Each step 30-80 ms, each beat <= 600 ms, a whole sequence <= 6 s. | Retro feel comes from few, visible steps, not from length. |

## 2. Vocabulary (the only effects allowed)

| Idiom | What it is | Kit function | Default steps and timing |
|---|---|---|---|
| **Zoom rect** | The System 7 open/close animation. 1px outline rectangles step from the source (tray icon) to the target window's box, trailing 2 behind the lead, then the window appears solid. | `Zm.zoom(root, from, to, {steps, ms})` | 5 steps / 240 ms |
| **Stepped cursor** | The classic black arrow moves in 5-7 straight jumps to a target and "clicks" by inverting the target for one step. | `Zm` frame `cursor: {sel, fx, fy}`, `cursorSteps`, `cursorMs` | 6 steps / 300 ms |
| **Watch cursor** | While zero works, the arrow becomes the wristwatch. The button label swaps to the real app string `Working…`. | frame `kind: 'watch'` | swap is instant (1 step) |
| **Envelope hop** | A 1-bit envelope icon lifts from a row and hops along a 5-point stepped arc into the dated folder `Auto-Archived 2026-09-29`. The row disappears the moment its envelope leaves. The folder icon switches to `folder-full` on the first arrival. | `Zm.hop(root, from, to, {n, steps, ms, gap, lift, onEach})` | 5 steps / 170 ms per envelope, 120 ms gap |
| **Stepped counter** | The popover count decrements by 1 as each envelope lands (12 → 4). No rolling digits and no tween. | `onEach` in `hop` | 1 step per envelope |
| **Invert flash** | A clicked control shows paper-on-ink for one step (80 ms). | CSS `.pressed` | 1 step |
| **Marching ants** | 2px dashed outline cycling offset, for the "you are here" selection (e.g., the one row being undone). Only one ants element on screen at a time. | CSS `.ants` (`steps(2)`, 400 ms, infinite) | stopped under reduced motion |

Explicitly out: parallax, scroll-jacking, typewriter text, glitch or CRT effects, confetti, springy UI, and motion on body copy or headings. Text never moves.

## 3. Hero storyboard (comp A, "the menu-bar roll", 5 frames, ~5 s)

Each frame can be viewed as a still with `?frame=N`. Screenshots are in `storyboard/`.

| # | Frame | What moves | Timing |
|---|---|---|---|
| 0 | **Cluttered.** The Inbox window shows 12 rows. zero's tray icon sits in the menu bar. The popover is closed. The cursor is about 150 px below-left of the tray. | nothing (the start state holds for 700 ms after load) | hold 700 ms |
| 1 | **Open.** The cursor steps to the tray and clicks. The tray inverts, zoom rects step from the tray to the popover's box, and the popover appears showing `12` and the 4 rows that need you. | cursor 6 steps, invert, zoom 5 steps | 300 + 240 ms, hold 250 |
| 2 | **Run.** The cursor steps to `Run zero now` and clicks. The label becomes `Working…` and the cursor becomes the watch. | cursor 7 steps, invert, swap | 380 ms, hold 350 |
| 3 | **Archive.** Eight envelopes hop one at a time from the Inbox window into `Auto-Archived 2026-09-29`. Each landing removes a row and steps the count down (12, 11 … 4). The folder fills on the first landing. Trash stays empty (nothing is deleted). | 8 hops x 5 steps | ~2.3 s |
| 4 | **Done (the HTML default).** The count reads `4`, the label reads `things still need you`, and 4 rows remain. The button is back to `Run zero now`. The cursor rests below the first row, arrow again. | cursor 5 steps | 220 ms |

Honesty rules for the storyboard:
- The names are fictional, and the caption reads `Illustration. Names are made up.`
- Every string is a real app string or approved COPY v3 copy.
- The number of rows the popover shows (4) matches the final count.
- Frame 3 must never show anything entering Trash.

## 4. Section motion (one beat each, played on first view)

These are proposals and are built in the section comps (`comps/sections/`). Each plays once, and its final frame is the HTML default.

| Section (COPY v3 h2) | Beat | Idiom |
|---|---|---|
| See what stays. See what gets archived. | Twelve compact rows split: 8 hop into the `Archived` column and 4 stay under `Stays`. The count steps. | envelope hop + counter |
| Keep mail that needs your reply or action. | No motion. It's a reading section, and motion here would compete with the rules. | none |
| Undo an archive. Nothing is deleted. | Marching ants go around one archived row in the Undo window. A click on `Restore all` hops the envelopes back to the Inbox, one by one. | ants + reverse hop |
| Know what you connect, share and pay for. | No motion. The Get Info window just sits there. | none |
| Install zero on your Mac. | The Terminal window "types" the single install line in 3 chunks, then shows the result line. It's a text reveal, not a moving caret flourish. **Optional**, and it defaults off if it slows reading. | stepped reveal (3 steps) |

## 5. Implementation constraints for slice 04

- Zero dependencies. The kit is about 4 KB of vanilla JS, and CSS handles the ants.
- Timelines are async functions with no rAF easing math. `setTimeout` pacing is fine because every change is a discrete step.
- `?frame=N` and `?static` stay in the build as QA hooks (they're harmless in production).
- All overlays are `aria-hidden="true"` and `pointer-events:none`. The hero has an sr-only sentence that describes the finished state. Motion never carries meaning that the static state lacks.
- Performance: animate `transform` only on overlays, and never animate the dither background.
- Tests to write: no-JS render equals the final frame (pixel diff). Reduced motion equals `?static`. There's no CLS during playback. At 320 and 390 px the sequence plays without the cursor and nothing overflows.

## 6. Open questions for development-motion

1. Should the hero replay when the user clicks the tray icon? My proposal: yes, as the only replay trigger, with no autoplay loop.
2. Should the envelope count be 8 at every width? At under 760 px the Inbox window is hidden, so the envelopes launch from the counter. Check whether that still reads.
3. Can the ants be done with pure CSS `outline-offset` stepping in Safari 26 without jitter? The kit does this, but it's unverified on Safari.
