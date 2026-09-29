# DESIGN-BRIEF: zero redesign 3, slice 02 (DRAFT for owner gate B)

Status: **proof only, not approved.** Nothing in `landing/` has changed. Every comp carries COPY v3 (slice 01) and a `DRAFT comp · copy v3 · not approved` flag. Gate A (copy) and gate B (hero pick and section approval) go to the owner together.

## Recommendation

**Pick hero A, "the menu-bar roll", and the section set in `comps/sections/`.**

Hero A is the only option that shows where zero actually lives. The tray icon in the menu bar opens zero's popover. `Run zero now` becomes `Working…`, eight envelopes hop into `Auto-Archived 2026-09-29`, and the count settles at **4 things still need you**. It tells the product story in one pass: *click, sort, the mail that needs you stays, nothing goes to Trash*. The headline plate, the proof (the popover) and the action (the install button) read left to right in that order.

| | A · menu-bar roll | B · Finder select | C · poster + two windows |
|---|---|---|---|
| Shows zero's real surface (tray + popover) | **yes** | no | no |
| Shows the result as a count | **yes (12 → 4)** | no | no |
| Risk of a false impression | low | **"you drag mail yourself"**, a manual act zero doesn't ask for | low |
| Fold at 1440×900 | headline, popover, folder and Trash all visible | all visible | the windows sit partly below the plate |
| Motion frames | 5 (~4.4 s designed, 5.1 s measured in WebKit by development-motion) | 4 | 4 |
| Word cost | inside budget | lower | lower (drops Trash, the folder name moves to a window title) |

C is the fallback if the owner wants a quieter, poster-first page. B isn't recommended.

## Before → after (the owner's five notes)

| Owner note | Live site today (`slices/01-copy-and-story/proof/before/`) | This proposal |
|---|---|---|
| "Hero doesn't have a good layout" | A headline window and a tall, dense panel redraw (416 count, 6 rows with tabs, badges and 4 action icons each) compete at equal weight. Two folder labels float between them, and Trash is cropped at the fold. | A plate-headline on the left, zero's popover under the menu-bar tray on the right, and the desktop (folder and Trash) as the stage. The popover is cut to 4 rows and no per-row controls. The order is headline → proof → action. |
| "More animations" | One effect: the dated folder slides in (`folder-drop`, 900 ms, 6 steps). | A stepped, 1-bit hero story (5 frames) that shows the sort itself, plus one beat on the demo section. The motion is finite, with no easing, and every animation's final frame is the HTML default. See `MOTION-SPEC.md`. |
| "More detail and polish" | The headline window's title "zero" sits **on** the stripes, and "Read the installer first" renders as "Arst". | A striped title bar with a white title plate, a close and zoom box, an inactive window with no stripes, a pixel cursor that turns into the watch, zoom rects, a folder that fills, an empty Trash and finite marching ants. The icons are a hand-drawn 1-bit sprite set (`kit/icons.svg`). |
| "Copy is confusing" | slice 01 | COPY v3, with the headline "Clean up your Gmail inbox on your Mac." 3/3 isolated readers passed it (slice 01). |
| "Sections are a mess, text left + thing right" | The owner's words: "just text on the left and something on the right" | Each section is a different object with its own layout. See below. |

## Sections: one purpose-built design each

The rhythm runs dither desktop → paper → light dither → paper → ink, so the page has pace and no two neighbours look alike. Screenshots are in `comps/sections/shots/{id}-1440.jpg` and `-390.jpg`.

| # | COPY v3 h2 | Design | Layout |
|---|---|---|---|
| 1 | See what stays. See what gets archived. | Two destination windows, `Stays` (4) and `Archived` (8), with the `Last reply: you` annotation. On first view the 8 rows hop out of Stays one at a time. | headline plate above, two windows side by side |
| 2 | Keep mail that needs your reply or action. | A `Rules` window whose body *is* the section copy: the four "keeps" as checked items. A separate note gives `Settings → Rules`, plus a caution icon beside "The model can make mistakes." | window left, notes right, top-aligned |
| 3 | Undo an archive. Nothing is deleted. | An `Undo` window with a `Restore all` button and greeked archived rows. One row wears finite marching ants. | text plate left, window right, centered (the one split row, earned by the object) |
| 4 | Know what you connect, share and pay for. | A `zero Info` (Get Info) window with 4 labelled rows: Gmail access, Email data, Optional reply drafts, Cost. | a full-width table window |
| 5 | Install zero on your Mac. | An ink section with a `Terminal` window holding the one install line and a `Copy command` button. The "what next" line sits under it. | plate left, Terminal right, ink ground |

At 390 every section stacks to a single column with no horizontal overflow (see Verification).

## The title-plate fix (the owner's "text off the stripe lines")

This follows the System 6/7 construction, and System.css is the reference (ref #1 in `refs/references.md`):

- Title-bar stripes are a `::before` layer inset 5 px × 4 px. The title text sits on a **paper plate** (`.bar .t`, 10 px side padding) that interrupts the stripes. The close and zoom boxes get a 3 px paper halo, so no stripe touches a glyph or a box.
- An **inactive** window drops the stripes and boxes entirely, as System 7 draws it (the `Archived`, `Auto-Archived` window).
- Any heading or paragraph on a dither ground sits on a paper plate with a 2 px ink border (`.on-dither .head`, the hero plate, the captions and the folder and Trash labels).
- Audit: a script walked every visible text node in all 4 comps at 320, 390 and 1440, looking for the nearest painted background. **No visible text sits on a texture.** The only hits were the visually hidden `.sr-only` illustration descriptions, which aren't painted.

## Other craft bugs found

- **The "fi" ligature bug is live on the current site.** Pixelify Sans's `liga` turns "fi" into one glyph, so "first" reads as "Arst" (for example "Read the installer first"). Any `font` shorthand resets `font-variant-ligatures`, so the comp kit ends with `*{font-variant-ligatures:none!important}`. Slice 04 must carry this or an equivalent.
- An SVG `<use>` without a `viewBox` renders at 300×150. `kit/inject.py` stamps each symbol's box.
- Sprite swaps (folder empty → full) must target the *visible* sprite. Both development-motion and I hit this independently.

## Word budget

The copywriter's inventory is **549 / 550** (`node slices/01-copy-and-story/proof/verify-copy.mjs`). I counted the rendered comps with the same tokenizer (hero A + the sections page, excluding the DRAFT flag and `.sr-only` text): **544**. The gap is `Working…` (counted by copy, but hidden at rest) and small tokenizer differences on `→`.

To stay inside the budget I **removed** chrome that the first comp pass had but copy never counted: the popover's account initials and badge counts (`TA 3`, `LI 1`) and the row ages (`11h`, `13h`, `1d`). The two accounts now show as a filled and a ring disc with no text. Hero B and C keep ages on their Inbox rows. If the owner picks B or C, send them to the copywriter for a recount first.

**No strings were added beyond COPY v3.** Every window title, label and demo row in the comps is listed in COPY.md's "Demo and window strings" section.

## Verification (what was actually checked)

| Check | Result |
|---|---|
| Horizontal overflow at 320, 390 and 1440, all 4 comps (iframe harness, not device emulation) | `scrollWidth == width` everywhere, with no element past the right edge |
| Clipped text | one at 320: `Product announcement` truncates with an ellipsis in the demo list. 390 is clean. |
| Text on stripes or dither | none painted (see above) |
| Hero A live playback | ends in the done state with count 4. Development-motion's sandbox measured 5.055 s desktop and 4.112 s mobile in Playwright WebKit (**not** real Safari 26). |
| Reduced motion, `?static` | the final frame renders with no added DOM |
| impeccable detector | **ran degraded** (parser modules missing, regex fallback, URL mode blocked by a missing Puppeteer Chrome). 2 findings, both `overused-font` for Geist and Geist Mono. Kept on purpose: they're the incumbent body faces in `landing/DESIGN.md`, and the one-bit voice comes from Pixelify plus the icons. The findings are an undercount, not a clean bill of health. |
| Word count | 544 rendered, 549 inventory, 550 ceiling |

**Not verified:** real Safari 26, the marching-ants animation in Safari (a `background-position` fallback is specified), real touch devices, and screen-reader passes.

## Files

- `refs/references.md` + `refs/*.jpg`: 14 live references, 5 animated
- `comps/hero-{a,b,c}/index.html` + `hero-*-1440.jpg`, `hero-*-390.jpg`: `?frame=N` shows a still, `?static` shows the end state
- `comps/sections/index.html` + `shots/`
- `storyboard/`: A (5 frames), B and C (4 each), the demo strip
- `MOTION-SPEC.md`: grammar, the storyboards, per-section beats, slice 04 constraints and decisions
- `comps/kit/`: the shared CSS, icon sprite, stepped-motion runner and capture harness

After gate B, link the chosen hero's 1440 shot as `./intent.png`, as the slice SPEC asks.
