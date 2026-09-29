# DESIGN-BRIEF: zero redesign 3, slice 02 (DRAFT for owner gate B)

Status: **proof only, not approved.** Nothing in `landing/` has changed. Every comp carries COPY v3 (slice 01) and a `DRAFT comp · copy v3 · not approved` flag. Gate A (copy) and gate B (hero pick and section approval) go to the owner together.

## Recommendation

> **Owner decision, 22:33Z and 22:36Z: hero B is approved. The rest of the page is not.** The recommendation below (A) is kept as the record of what was proposed. What follows is the B rework the owner's pick required. The whole-page rethink (outline, section objects, copy) is a separate proposal in progress with design-copywriter. Its before evidence is frozen in `baseline-v3/` (commit a196c47).
>
> **The risk with B, and the fix.** The original B showed an arrow pointer selecting rows and dragging them into a folder. A visitor would reasonably read that as "I drag my mail into folders", which is manual work zero exists to remove. In the rework, **zero is the only actor on screen:**
>
> 1. zero's menu-bar popover opens from its tray icon with `Run zero now`.
> 2. The button turns to `Working…`, and **zero's watch** appears on that button. It is the only cursor on the page, and it exists only while zero is working.
> 3. The watch selects the 8 routine rows and drags them into `Auto-Archived 2026-09-29`.
> 4. The watch disappears and the button reads `Run zero now` again.
>
> There is no arrow pointer in any frame, so there's no "you" in the scene. On phones, where no cursor is drawn, `Working…` plus the rows inverting by themselves carries the same meaning. The end state is honest in every mode (live, reduced motion, no JS): 4 kept, 8 in the dated folder, Trash empty.
>
> - **Strings.** The only strings added are the zero mark, `Run zero now` and `Working…`, all from COPY v3. The copywriter's provisional count is 532/550.
> - **Motion.** See `MOTION-SPEC.md` §3.0 (6 frames, about 4.6 s measured at 1440 in Chromium).
> - **Evidence.** Stills are in `storyboard/hero-b-frame-0..5.jpg` and `hero-b-strip.jpg`. Final shots are `comps/hero-b/hero-b-1440.jpg` and `-390.jpg`.
>
> **How B changes the sections.** The hero now shows the whole sort, inbox to folder. The old section 1 (`Stays` / `Archived` windows with the same rows hopping across) repeats it almost frame for frame, so it can't stay as it is. The rethink tests replacing it with something the hero doesn't show, such as opening the dated folder next to zero's Undo, and at least one genuinely shorter outline. It doesn't default to trimming section 1.

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
- Audit: a script checked every visible text element in all 4 comps at 320, 390 and 1440 by walking up its ancestors to the first painted background. **None resolves to a texture.** The only hits were the visually hidden `.sr-only` descriptions, which aren't painted. This is an ancestor check, not a pixel check. Text that overlaps a texture by absolute positioning would slip past it, so the screenshots were also reviewed by eye.

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
| Clipped text | none at 320, 360 or 390 (sender, subject, heading, button and title elements). The first pass truncated `Product announcement`, then `Sarah Mitchell`, at 320. A ≤350 px demo-row grid fixed both. |
| Text on stripes or dither | none painted (see above) |
| Hero A live playback | ends in the done state with count 4. Development-motion's sandbox measured 5.055 s desktop and 4.112 s mobile in Playwright WebKit (**not** real Safari 26). |
| Demo section live playback (Aside Chrome) | on scroll-in the rows start mixed. Ten seconds later Stays holds the 4 named rows in order, Archived holds 8, and no flying envelopes are left in the DOM. |
| Reduced motion, `?static` | the final frame renders with no added DOM |
| impeccable detector | **ran degraded** (parser modules missing, regex fallback, URL mode blocked by a missing Puppeteer Chrome). 2 findings, both `overused-font` for Geist and Geist Mono. Kept on purpose: they're the incumbent body faces in `landing/DESIGN.md`, and the one-bit voice comes from Pixelify plus the icons. The findings are an undercount, not a clean bill of health. |
| Word count | 544 rendered, 549 inventory, 550 ceiling |

### Real-engine acceptance pass (2026-09-29 23:00Z, Playwright 1.61.1). Script and raw results: `acceptance/`

Each comp was loaded directly, with no iframe harness, in **Chromium** and **Playwright WebKit build 2336** on macOS. This is WebKit, **not Safari 26**. Device profiles:

- desktop 1440×900 @2x
- iPhone 390×844 @3x, mobile with touch
- SE 320×568, mobile with touch

Pages: hero A, reworked hero B, hero C and sections. Per engine that's 3 profiles × 4 pages × 12 checks, plus keyboard, copy and control checks.

| Check | Chromium | WebKit |
|---|---|---|
| Live playback reaches `done` (the story's own state flag), 0 leftover motion DOM, 0 console or page errors | 12/12 | 12/12 |
| No horizontal overflow, no clipped text, no text on texture | 12/12 | 12/12 |
| Title plates break the stripes (white plate, text box not narrower than its text) | 12/12 | 12/12 |
| `fi` ligatures off on Pixelify | 12/12 | 12/12 |
| Tap targets ≥24px (WCAG 2.2 2.5.8, with links inside sentences exempt per the inline exception) | 12/12 | 12/12 |
| Images and SVGs named or hidden | 12/12 | 12/12 |
| Reduced motion shows the final frame with no motion DOM | 12/12 | 12/12 |
| No-JS HTML text equals the played final frame | 12/12 | 12/12 |
| Keyboard: every link and button reachable, visible focus ring | 4/4 (Tab) | 4/4 (Option+Tab) |
| COPY v3: all 57 primary sentences render verbatim (hero A + sections) | pass | not run, since it's engine-independent |
| Control: the audit, pointed at the live site, **does** catch the `fi` ligature bug and the title on the stripes | both caught | not run |

Final: Chromium 155/155. WebKit 146/146 page checks, plus 4/4 keyboard in a separate WebKit pass.

**Fixed because of this pass:**

- `Read the installer first` was 21px tall and the footer links were 15px. Standalone text links now have a `min-height: 24px`.

**Audit false positives corrected, not hidden:**

- The stripe check flagged 5 plates that were narrower than `scrollWidth` by less than 1px. That's subpixel rounding: the plates are white and the text isn't clipped.
- WebKit reached 0 controls with a plain Tab. macOS WebKit only tabs to links with Option+Tab (Safari's default). With Option+Tab, every control is reachable.

**Harness faults:**

- The first full run died when a WebKit context closed underneath it.
- A second run hung on WebKit's second `newPage` in a reused context. The keyboard step now uses a fresh context per page.

Neither fault was a page defect.

**Not verified:** real Safari 26 (Playwright WebKit is a stand-in, not the shipping browser), the marching-ants animation in Safari (a `background-position` fallback is specified), real touch devices, and screen-reader passes.

## Files

- `refs/references.md` + `refs/*.jpg`: 14 live references, 5 animated
- `comps/hero-{a,b,c}/index.html` + `hero-*-1440.jpg`, `hero-*-390.jpg`: `?frame=N` shows a still, `?static` shows the end state
- `comps/sections/index.html` + `shots/`
- `storyboard/`: A (5 frames), B and C (4 each), the demo strip
- `MOTION-SPEC.md`: grammar, the storyboards, per-section beats, slice 04 constraints and decisions
- `comps/kit/`: the shared CSS, icon sprite, stepped-motion runner and capture harness

After gate B, link the chosen hero's 1440 shot as `./intent.png`, as the slice SPEC asks.
