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
| **Plays once, nothing loops forever.** Hero on load (700 ms delay), sections on first intersection (`IntersectionObserver`, threshold ~0.4). Even the ants are finite (6 cycles, 2.4 s, then a still dashed outline). | Looping motion competes with reading. |
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
| **Marching ants** | 2px dashed outline cycling offset, for the "you are here" selection (e.g., the one row being undone). Only one ants element on screen at a time. | CSS `.ants` (`steps(2)`, 400 ms, **6 iterations**) | 2.4 s then still. Stopped under reduced motion |

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

### 3b. Alternative hero storyboards (comps B and C, 4 frames each)

These are kept for comparison. The brief recommends A. Stills are `storyboard/hero-b-frame-0..3.jpg`, `hero-c-frame-0..3.jpg` and each `*-strip.jpg`.

| # | B, "the Finder select" | C, "the poster and two windows" |
|---|---|---|
| 0 | Inbox window with 12 rows (4 readable, 8 greeked). Folder and Trash on the desktop. | Poster headline plate over an Inbox window (12 rows) and an inactive, empty `Auto-Archived 2026-09-29` window. |
| 1 | The watch cursor appears. The 8 routine rows invert one at a time (70 ms apart). | Zoom rects step open from Inbox to the archive window. |
| 2 | Dashed drag outlines step from the 8 rows into the folder in 7 steps. The folder highlights as the drop target. | The 8 rows step across as solid blocks, one at a time, and fill the archive slots. |
| 3 | Final: 4 rows remain, the folder is full and Trash is empty. | Final: Inbox holds 4 rows, the archive holds 8. |

Why A wins: B reads as "you drag mail yourself" (a manual Finder action zero doesn't ask for), and it has no count. C is calm and clear, but it drops the menu-bar tray, which is where zero actually lives, and it pushes both windows below the headline plate at 1440×900.

## 4. Section motion (one beat each, played on first view)

These are proposals. Only the demo beat is built as motion in `comps/sections/`. The Undo ants are static CSS there, and the other beats are spec only. Each plays once, and its final frame is the HTML default.

| Section (COPY v3 h2) | Beat | Idiom | In the comp |
|---|---|---|---|
| See what stays. See what gets archived. | All 12 rows start mixed in `Stays`. The 8 archived rows hop one at a time into `Archived`, and 4 stay. There is no counter, because COPY v3 bans extra counters. Stills: `storyboard/demo-strip.jpg` (frames 0, 2 and 3). | envelope hop | built (`?frame=0..3`) |
| Keep mail that needs your reply or action. | No motion. It's a reading section, and motion here would compete with the rules. | none | static |
| Undo an archive. Nothing is deleted. | Marching ants go around one archived row in the Undo window (finite, ~2.4 s). `Restore all` is shown as the way back but isn't wired. A reverse hop on click is a slice 04 option that needs an Inbox target on screen. | ants | ants only |
| Know what you connect, share and pay for. | No motion. The Get Info window just sits there. | none | static |
| Install zero on your Mac. | Optional: the Terminal reveals the one install line in 3 chunks. No result line, because that would be a new string. Default off if it slows reading. | stepped reveal (3 steps) | static |

## 5. Implementation constraints for slice 04

- Zero dependencies. The kit is about 4 KB of vanilla JS, and CSS handles the ants.
- Timelines are async functions with no rAF easing math. `setTimeout` pacing is fine because every change is a discrete step.
- `?frame=N` and `?static` stay in the build as QA hooks (they're harmless in production).
- All overlays are `aria-hidden="true"` and `pointer-events:none`. The hero has an sr-only sentence that describes the finished state. Motion never carries meaning that the static state lacks.
- Performance: animate `transform` only on overlays, and never animate the dither background.
- Tests to write: no-JS render equals the final frame (pixel diff). Reduced motion equals `?static`. There's no CLS during playback. At 320 and 390 px the sequence plays without the cursor and nothing overflows.

## 6. Decisions (settled with development-motion, 21:45Z)

1. **Replay.** The only trigger is a real keyboard-accessible `<button>` (the menu-bar tray item, with an accessible name like "Replay the illustration"). Repeat presses are ignored while a story plays. There is no replay under reduced motion. The kit does not have this yet, so slice 04 builds it.
2. **Eight archives at every width.** This keeps the 12 → 4 arithmetic intact. At under 760 px the envelopes launch from the counter. Whether that reads is **a visual question to test in the sandbox, not yet validated**.
3. **Safari ants.** Still unverified. If `outline-offset` stepping jitters in Safari 26, fall back to a stepped `background-position` on a 2px dashed border image.
4. **Finite ants.** 6 cycles, then still. Slice 04's "nothing loops forever" wins.

## 7. Known gaps in the comp runner (for slice 04, found by development-motion's inspection)

| Gap | Status in `kit/motion.js` |
|---|---|
| The static and reduced-motion paths injected a cursor that is absent from the no-JS HTML | **Fixed.** `?static` and reduced motion now add nothing to the DOM. |
| No fine-pointer gate on the cursor | **Fixed.** Live playback draws the cursor only with `(pointer: fine)` and >= 760 px. `?frame=N` forces it on, for captures only. |
| Zoom rects used fractional positions | **Fixed.** Now `Math.round`ed. |
| No error-to-final path | **Fixed.** Any throw mid-story removes the overlays and applies the final frame. |
| No cancellation (e.g., the tab goes hidden or the user replays mid-story) | Open. Slice 04: use an `AbortController` per story, and on `visibilitychange` jump to the final frame. |
| Archived rows use `display:none`, so the Inbox window shrinks as it plays (CLS inside the window) | Open. Slice 04: keep fixed row slots and blank the row in place (`visibility:hidden`), or give the list a fixed height. In the comp the window is absolutely positioned, so the page doesn't shift, but the window itself does. |
