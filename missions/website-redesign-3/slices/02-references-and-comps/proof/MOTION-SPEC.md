# MOTION-SPEC: zero redesign 3 (DRAFT, early publish)

Status: **draft for development-motion@zero**. Nothing here is approved for `landing/`. Implementation waits for main-lead's authorization after owner gate B. Any prototype belongs in slice 04 `proof/sandbox/`.

**Update 2026-09-29 22:50Z: the owner picked hero B.** Build from §3.0 below. §3 (hero A) and the old B row in §3b are kept only as history. The rest of the page (sections) is **not** approved and is being rethought, so §4 is on hold.

Reference prototype: `comps/kit/motion.js` (the `Zm` runner) plus `comps/hero-b/index.html`. To serve it, run `python3 -m http.server` from `proof/comps`. The page supports `?frame=N` for a still of frame N and `?static` for the end state.

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

## 3.0 Hero storyboard: comp B, "zero drags it" (the owner's pick, 6 frames, ~4.6 s measured)

The owner's constraint is that **zero is the actor**. The hero must never suggest that the visitor drags mail by hand. So:

- **There is no arrow pointer in any frame.** The only cursor is zero's **watch**. It appears *on* the `Working…` button, does the selecting and dragging, and is gone when the button reads `Run zero now` again. Its lifetime equals the `Working…` state. That coupling is what makes it zero's hand and not the visitor's.
- Opening the popover is zoom rects stepping out from the tray icon, with no click shown. (It's a still-frame story, and zero's menu-bar window being open is enough.)
- On touch or below 760px there is no cursor at all (the §1 rule). The same frames play, and the `Working…` label plus the rows inverting carry the "zero is doing it" meaning.

Stills: `storyboard/hero-b-frame-0..5.jpg`, strip `storyboard/hero-b-strip.jpg`. Final shots: `comps/hero-b/hero-b-1440.jpg`, `-390.jpg`.

| # | Frame | What moves | Timing |
|---|---|---|---|
| 0 | **Cluttered.** Inbox window, 12 rows (4 readable, 8 greeked). The folder `Auto-Archived 2026-09-29` is empty and Trash is on the desktop. zero's popover is closed. No cursor. | nothing | hold 600 ms |
| 1 | **zero opens.** Zoom rects step from the tray icon to the popover box, and the popover appears: zero mark plus `Run zero now`. | zoom 5 steps | 240 ms, hold 450 |
| 2 | **zero starts.** The button swaps to `Working…` (paper on ink with an outline). zero's watch appears on the button. | swap (1 step), watch placed (no travel) | hold 420 |
| 3 | **zero selects.** The watch steps from the button to the first routine row. The 8 routine rows invert one at a time. | watch 6 steps, 8 inverts | 320 ms + 8 × 70 ms, hold 250 |
| 4 | **zero drags.** Dashed outlines, one per selected row, step together from the rows into the folder in 7 steps as they shrink to icon size. The watch travels with them. The folder inverts as the drop target, the rows go, and the folder fills. Outlines pass *behind* the headline sheet (z-index below it), never over its text. | watch 7 steps, outlines 7 × 80 ms | ~560 ms, hold 260 |
| 5 | **Done (the HTML default).** The watch is gone. The button reads `Run zero now` again. Inbox holds the 4 rows (`Alex Rivera · Can you approve the quote? · 11h`, `Priya Sharma · Which date works for you? · 13h`, `Daniel Kim · Your payment failed · 1d`, `Sarah Mitchell · Contract changes to review · 1d`). The folder is full and selected. Trash is empty. | none | — |

Layout:
- At ≥1240px the popover hangs from the tray (the notch points at it), with the Inbox on the right and the headline plate on the left.
- Below 1240px the stack is headline, then popover, then folder and Trash, then Inbox, then caption. That keeps the button and the drop target together near the top.
- The stacked Inbox list is `height:auto`, so the final window is 4 rows and not a mostly blank window. That resize happens once, at the end, and only moves the caption below it.

**Reserved geometry (agreed with development-motion, their sandbox `cbd261f`, `slices/04-motion-and-polish/proof/sandbox/hero-b/`).** The page comps still use the comp's behavior: the 12-to-4 collapse measures about 0.002 CLS at 390 and 0.015 at 1440, and the drag outlines measure 0.02 more (`acceptance/pages-chromium.log`, INFO lines). Slice 04 replaces this by reserving the scene's outer height, so the caption and everything below it never move:

| Layout | Reserved geometry |
|---|---|
| ≥1240 | hero 940px, Inbox slot 468px, list 432px, caption top 700 |
| stacked 640–1239 | Inbox slot 468px |
| stacked <640 | Inbox slot 548px (list 512 at first, 224 at the end) |

Inside the slot the window may still shrink to its 4 rows. The slot keeps its height, so only the empty desktop under the window changes.

Honesty rules for B:
- No arrow pointer.
- The watch only exists during `Working…`.
- Nothing enters Trash.
- The final 4 rows are the COPY v3 strings exactly.
- The only strings are the ones the copywriter counted: zero mark, `Run zero now`, `Working…`, `Inbox`, the rows and ages, the folder, `Trash` and the caption. Provisional count is 532/550.

Measured (Playwright Chromium, live playback to `data-mode=done`): 1440, about 4.6 s. 390, about 3.7 s, with no cursor. There are 0 console errors. Sampled live states are `Run zero now` with no cursor, then `Working…` with the watch, then `Run zero now` with no cursor. No arrow cursor ever appears.

Kit change: `motion.js` now *places* a cursor at its first target when the previous frame had none, instead of sliding it in from 0,0. This affects any story whose first frame has no cursor. A, C and the sections all start with a cursor, so they're unchanged.

## 3. Hero storyboard (comp A, "the menu-bar roll", 5 frames, ~5 s). Superseded by 3.0; kept for history

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

History. The B column below is the **pre-rework** B. The reworked B is §3.0, and its stills now occupy `hero-b-frame-0..5.jpg`. C stills are `hero-c-frame-0..3.jpg`.

| # | B, "the Finder select" | C, "the poster and two windows" |
|---|---|---|
| 0 | Inbox window with 12 rows (4 readable, 8 greeked). Folder and Trash on the desktop. | Poster headline plate over an Inbox window (12 rows) and an inactive, empty `Auto-Archived 2026-09-29` window. |
| 1 | The watch cursor appears. The 8 routine rows invert one at a time (70 ms apart). | Zoom rects step open from Inbox to the archive window. |
| 2 | Dashed drag outlines step from the 8 rows into the folder in 7 steps. The folder highlights as the drop target. | The 8 rows step across as solid blocks, one at a time, and fill the archive slots. |
| 3 | Final: 4 rows remain, the folder is full and Trash is empty. | Final: Inbox holds 4 rows, the archive holds 8. |

Why A was recommended at first: the pre-rework B read as "you drag mail yourself" (a manual Finder action zero doesn't ask for), and it had no count. C is calm and clear, but it drops the menu-bar tray, which is where zero actually lives, and it pushes both windows below the headline plate at 1440×900. The owner chose B. §3.0 removes the manual-drag reading by making zero's popover and watch the only actor. B still has no count, and the Inbox window going from 12 rows to 4 is the proof.

## 4. Section motion (one beat each, played on first view)

### 4.0 Whole-page comps A and B (00:30Z, built in `comps/page-a/`, `comps/page-b/`; `kit/sections.js`)

These replace §4.1 for the rethink. The Stays/Archived demo is cut in both outlines, so no section replays hero B's sort. There is one beat per section object, each on the Zm runner and data-driven (a frame list per object in `kit/sections.js`), with no new strings. **Proposal, not approved.** It goes to readers and review-qa with the pages.

| Section | Object | Beat (frames) | Steps and timing | Stills |
|---|---|---|---|---|
| Recovery (A "See what went into the archive." / B "Restore archived mail.") | zero's Undo tab, 5 of 8 rows | 0 batch collapsed (disclosure points right) · 1 expanded, the 5 rows step in one at a time · 2 the balloon `Put this email back in the inbox` appears on row 5's put-back button, which inverts (final) | 5 × 80 ms, hold 380 | `page-{a,b}/shots/beat-undo-f0..2.jpg` |
| Rules (B only, "Choose what needs to stay.") | zero's Settings window, Rules pane | 0 `Open loops` tab selected, pane empty · 1 the selection hops tab to tab to `Settings` · 2 the 14 policy lines step in two at a time (final) | 3 × 170 ms, then 7 × 45 ms | `page-b/shots/beat-rules-f0..2.jpg` |
| Before you install (both) | a Get Info window opened from the zero app icon | 0 icon only, window closed · 1 zoom rects step from the icon to the window's box · 2 the window is there and its 5 rows fill in one at a time (final) | zoom 6 steps / 300 ms, 5 × 110 ms | `page-{a,b}/shots/beat-ledger-f0..2.jpg` |
| Install (both) | Terminal on ink | 0 empty prompt · 1 the command types in, 2 characters a step, then the block cursor blinks 3 times and rests (final) | ~26 steps × 28 ms, blink `steps(1)` × 3 | `page-{a,b}/shots/beat-install-f0..1.jpg` |

Rules the runner now enforces (`kit/motion.js` `when()`):

- **Armed, then played.** A section story is put on frame 0 while it's still below the fold (30% root margin), and it plays when 35% of it, or 35% of the viewport, is visible. The visitor never sees the final frame snap back to frame 0.
- **Arrival stays final.** If a section is already on screen at first sight (reload mid-page, a fling), or it's reached through an in-page link within 1.2 s (the hero's `Install zero for Mac` goes to `#install`, and the menu bar), it is settled on its final frame and never plays. People who jump to the ledger came to read it.
- **No layout shift.** Every hidden part uses `visibility`, never `display`. The collapsed Undo keeps its expanded height, and untyped command text is present but invisible. Measured section CLS: 0.0000 at 390 and 1440 on both pages.
- **No stray DOM.** Stories without a cursor frame get no cursor element. The zoom rects sit under the ledger heading and lede plates (z 35 < 36), never across text.
- Reduced motion and no JS: the final frame, nothing plays. Measured equal to `?static` in both engines (`acceptance/pages.mjs`).
- Byte cost: `sections.js` is 3.6 KB unminified. The runner additions are about 1 KB.

### 4.2 Selected page B (owner choice 00:58Z): the beats to prototype

Tayo chose page B (risk-first). This section replaces 4.0 for sandbox work. Page A's beats are archived with page A. **Proposal, not approved.** Sections and copy aren't final until Tayo approves the tightened B, and the build stays held. Source: `comps/page-b/index.html`, generated by `comps/kit/build-pages.py` and driven by `comps/kit/sections.js` on `comps/kit/motion.js`.

B has four sections, in page order, with one beat each:

| # | Section (B order) | Object | Frames | Steps and timing |
|---|---|---|---|---|
| 1 | Before you install (straight after hero B) | Get Info window from the zero app icon | 0 icon only · 1 zoom rects step from the icon to the window's box · 2 the rows fill in one at a time (final) | zoom 6 steps / 300 ms, then N × 110 ms, where N is the row count (5 today). **The beat doesn't depend on row order or wording.** The trust fix may reorder or relabel rows, and the beat stays the same. |
| 2 | Choose what needs to stay. | zero's Settings window, Rules pane | 0 `Open loops` selected, pane empty · 1 the selection hops tab to tab to `Settings` · 2 the policy lines step in two at a time (final) | 3 × 170 ms, then ⌈13 / 2⌉ = 7 × 45 ms. There are now 13 lines: since `39aa729` the source's hard-wrapped rule is one line with a hanging indent, with the same words. |
| 3 | Restore archived mail. | zero's Undo tab | 0 batch collapsed · 1 expanded, the 5 rows step in, then the cut 6th row (no text, `aria-hidden`) · 2 the balloon appears on row 5's put-back button, which inverts (final) | 6 × 80 ms, hold 380 |
| 4 | Ready to install? | Terminal on ink | 0 empty prompt · 1 the command types in 2 characters a step, then the block cursor blinks 3 times and rests (final) | ~26 × 28 ms, blink `steps(1)` × 3 |

Runner rules are unchanged from 4.0: armed before view, arrival stays final, visibility never display (0 section CLS), no stray cursor DOM, and reduced motion or no JS show the final frame.

Two behaviours added in `39aa729` that the sandbox must keep:

- **Copy command** ships `hidden` and appears only when `navigator.clipboard.writeText` exists in a secure context. On success, `Copied` goes in the visible `role=status aria-live=polite` region. On denial the page shows `Copy manually: press Command-C.` and selects the command text, and focus stays on the button. With no API, or no JS, there's no button and the command stays selectable. The copywriter approved these strings. `acceptance/pages.mjs` §7 tests this with a stubbed clipboard.
- The **proof label** now sits in flow after the footer and isn't fixed. It's proof-only, so it doesn't port.

### 4.1 Earlier proposal for comps/sections (superseded by 4.0)

> **On hold (22:50Z).** The owner has not approved the sections. They are being rethought with the copywriter, so do not prototype these beats. Note that the section 1 beat below (rows hopping from Stays to Archived) would replay the new hero B. Whatever replaces section 1 must not repeat the sort.

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
