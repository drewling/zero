# References: one-bit and retro-Mac on the live web (redesign 3, slice 02)

Captured 2026-09-29 in a real Chrome session (Aside), 1440×900 CSS px at DPR 2, downscaled to 1200 px wide for this folder. For each site, `-a` is the first view and `-s` is scrolled. "Motion" frames were taken 700 ms to 1.2 s apart, and the % figure is the share of pixels that changed between them (a threshold of 24/255). These are live sites, so they may change after today.

**Criteria.** Each reference had to teach one concrete move that zero's site can use or must avoid. Pretty but irrelevant sites were cut (teenage.engineering, panic.com, pce-js and macos9.app were captured but add nothing the list below doesn't already cover).

## The 14

| # | Site | Files | Animated? | What it teaches zero |
|---|---|---|---|---|
| 1 | **System.css** · sakofchit.github.io/system.css | `systemcss-a/s.jpg` | no | The canonical System 6 window: 6 fine horizontal stripes across the title bar, **with the title sitting on a white plate that interrupts the stripes**. This is exactly Tayo's "title text off the stripe lines" note, done right. Also shows the invert-on-press button and the rounded default ring. Our kit's `.bar .t` copies this construction. |
| 2 | **HyperCard Simulator** · hypercardsimulator.com | `hypercard-a/s.jpg`, `hc-*` in scratch | idle (the video is paused) | The best proof that one-bit works at landing-page scale. One big card-window, 1-bit Susan-Kare-grade icons in a grid with labels under them, and a single chunky title. The icons carry the page, and there's no dither wallpaper behind the content. |
| 3 | **Infinite Mac** · infinitemac.org | `infinitemac-a/s.jpg`, `sys7-1/2/3-motion.jpg` | **yes** (the System 7.0 boot, frames 9 s, 18 s and 30 s after load) | A timeline of beige machines, each with a real screen and a real `Run` button. The move for zero: **the product runs inside the device frame, and the chrome around it stays quiet**. The boot is the authentic stepped-motion reference, and it's small: a gray screen, then the arrow cursor appears, then extension icons pop in one at a time along the bottom-left. Each change is a whole jump, with no easing. We captured it only up to the extension parade, not the Finder desktop. |
| 4 | **Poolsuite** · poolsuite.net | `poolsuite-a/s.jpg`, `poolsuite-1/2-motion.jpg` | **yes** (2.28% per 700 ms) | A retro-OS window as the entire hero, with a Dock of labeled icons under it. The motion is content (the video) inside a still frame, and the chrome never moves. It shows how far a single strong window can carry a hero. The warning: it's colorful and nostalgic-kitsch, and zero is one-bit and calm. |
| 5 | **ryOS** · os.ryo.lu | `ryos-a.jpg`, `ryos-1/2-motion.jpg` | **yes** (1.21% per 700 ms) | A full desktop metaphor in the browser: a real menu bar with a clock, desktop icons down the right, an assistant bubble and a dock. It proves the "whole page is a desktop" layout and **the menu bar as navigation**. It also shows the cost: busy, and the story gets lost. Zero should take the menu bar and drop the rest. |
| 6 | **Playdate** · play.date | `playdate-a/s.jpg`, `playdate-1/2-motion.jpg` | **yes** (2.22% per 700 ms) | A modern product page for a 1-bit device. The screen content is honest 1-bit, and everything around it is clean modern marketing. Big, plain-spoken headings ("The System.", "The Design.") and one idea per section. **This is the section rhythm Tayo is asking for.** |
| 7 | **PostHog** · posthog.com | `posthog-a/s.jpg`, `posthog-motion-0/1.jpg` | **yes** (5.45% per 1.2 s; the site runs 23 animations) | A current SaaS site dressed as an OS: draggable windows, desktop icons, tabs that switch the demo window. The lesson is in the negative: **so much chrome that the product pitch is a paragraph in a window among windows**. Use one window at a time. |
| 8 | **Return of the Obra Dinn** · obradinn.com | `obradinn-a/s.jpg` | no | Two-color (ink on paper tint) with the dither used **as illustration, never behind text**. The period document plates carry the copy on flat paper. This rule protects legibility: the dither frames content and never sits under it. |
| 9 | **Susan Kare** · kare.com | `kare-a/s.jpg` | no | The source of the icon language. Relevant for zero's sprite (envelope, folder, trash, watch): 1-bit icons have to be drawn on the pixel grid at their true size, then scaled by integer multiples only. |
| 10 | **Hundred Rabbits** · 100r.co | `hundredrabbits-a/s.jpg` | no | Black page, 1-bit dithered illustration, an icon row for navigation, and plain long-form text underneath. It shows that one-bit can read as warm and handmade, not only as nostalgia. |
| 11 | **Low-tech Magazine (solar)** · solar.lowtechmagazine.com | `lowtech-a/s.jpg` | no | Dithered photos as a *performance* choice, not only a style. The site shows its page weight and battery level. The move: **say why the thing looks this way**. Zero's equivalent is being honest that the panel is an illustration with made-up names. |
| 12 | **Ditherpunk (Surma)** · surma.dev/things/ditherpunk | `ditherpunk-a/s.jpg` | no | The technical reference for dithering. Ordered (Bayer) dithers read as "Mac"; error diffusion reads as "photo". Zero's 2×2 checker `--dither` and 25% pattern are ordered, which is correct. |
| 13 | **Folklore.org** · folklore.org | `folklore-a/s.jpg` | no | The original Macintosh team's stories, and a period-correct but dated page. A tonal reference for plain, first-person, specific copy. Visually it shows what to avoid: a table-layout clutter of links. |
| 14 | **Gingerbeardman** · gingerbeardman.com | `gingerbeardman-a/s.jpg` | no | A developer of Mac menu-bar utilities presenting them as a dense spec table: name plus one line each. It's proof that a **menu-bar app can be explained in one line** if the line is concrete. |

Animated count: **5** (Infinite Mac, Poolsuite, ryOS, Playdate, PostHog). The spec's minimum was 2.

## What we take (and what it became in the comps)

1. **The title plate** (System.css). Stripes stop 8 px before the title. The title sits on paper with 8 px of padding. Inactive windows lose their stripes entirely. → `kit.css .bar .t`, used on every window in every comp.
2. **One window at a time carries the story** (Infinite Mac, Poolsuite, against PostHog). → Hero A has one active window (zero's popover). The Inbox is drawn inactive, stripe-free and quieter.
3. **The menu bar is navigation** (ryOS). → Every comp's top bar is a Mac menu bar: brand, nav, Install, and zero's real `tray.full` status item.
4. **Dither frames content and never sits under text** (Obra Dinn, HyperCard). → Every text block sits on a white `.plate`. This is audited in slice 02's verification.
5. **Stepped motion, System 7 style** (the Infinite Mac boot: icons appear one at a time, whole jumps, no tween). → MOTION-SPEC grammar: steps only, no easing, and the final frame is the HTML.
6. **One idea per section, said plainly** (Playdate). → Each section comp is a single purpose-built scene (see `comps/sections/`).
7. **Say what's illustrated** (Low-tech Magazine). → The caption "Illustration. Names are made up." stays next to every mock.

## What we avoid

- A desktop full of windows and draggable toys (PostHog, ryOS). They're fun for 10 seconds and then bury the pitch.
- Color nostalgia (Poolsuite's pink, Playdate's yellow). Zero stays strictly ink and paper.
- Dither behind body text (the current live site's hero sheet edge and stripe titles, which is Tayo's complaint).
- Faux-CRT, scanlines, glitch or VHS effects. None of these references needs them.

## Also captured (not in the 14)

teenage.engineering, panic.com, macintoshgarden.org, pce-js and macos9.app are in the Aside session folders but were not copied into this folder. They add nothing beyond the 14.
