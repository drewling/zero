# LAYOUT-GRID: zero redesign 3 whole-page comps (DRAFT, proposal)

Source: `comps/kit/page.css` (header comment and `.band` rules), as built at `cdfee91`. It applies to `comps/page-a/` and `comps/page-b/`. Hero B keeps its own approved layout and isn't part of this grid. **Proposal, not approved.**

## Model

- **Full bleed.** Every section is a `.band` that runs edge to edge, with a 2px ink rule between bands. There are no centered cards on a grey page.
- **12 columns between gutters.** `grid-template-columns: [full] var(--pad) [content] repeat(12, 1fr) [content] var(--pad) [full]`, with `--pad: clamp(16px, 5vw, 72px)`.
- **Text and field.** A band holds `.txt` (h2 and prose) and `.field`, the dithered desktop the object's window sits on. The field always bleeds to the viewport edge on its own side. Windows keep a natural maximum and sit on the desktop. They're never stretched to fill it.
- **Measure.** Prose is capped at `--measure: 60ch`. Headings are capped at `16ch`.
- **Ledger exception.** The Get Info window runs the full content width, and its 5 rows are in 2 columns from 1100px. The heading and lede sit on a paper plate (z 36) above the zoom rects (z 35).
- **Ink band.** Install is ink on paper inverted: text on the left, Terminal on the right from 1100px.

## Breakpoints

| Width | Columns | Text | Field | Root |
|---|---|---|---|---|
| < 400 | 1 | full content width | full bleed, under the text | 16px, tabs and window padding tightened (fixes a 56px overflow at 320) |
| 400–1099 | 1 | full content width | full bleed, under the text | 16px |
| 1100–1919 | split 5 \| 7 | 5 columns | 7 columns plus the gutter to the edge | 16px |
| ≥ 1920 | split 4 \| 8 | 4 columns | 8 columns plus the gutter to the edge | 18px |

`split-r` puts the text on the left and the field on the right. `split-l` mirrors it. Page B alternates, with Rules as split-r and Undo as split-l. Page A has one split band (Undo, split-r).

## Measured (Playwright Chromium, page-b `?static`, `#how-band`)

| Viewport | Gutter | Text box | Field | Body / h2 | Prose chars per line, median (max), A and B |
|---|---|---|---|---|---|
| 320 | 16 | 288 | 0–320 | 17 / 32 | 34–35 (39) |
| 390 | 20 | 351 | 0–390 | 17 / 32 | 43 (47) |
| 768 | 38 | 691 | 0–768 | 17 / 32 | **84–85 (88)** |
| 1440 | 72 | 540 | 720–1440 | 17 / 47.5 | 60–64 (67) |
| 1920 | 72 | 592 | 812–1920 | 19 / 60 | 60–63 (78) |
| 2560 | 72 | 805 | 1079–2560 | 19 / 60 | **84–85 (88)** |

Horizontal scroll width equals the viewport at every width. `acceptance/pages.mjs` reports 0 overflow, escape or clip in Chromium and WebKit at all 6 widths.

Chars per line are counted from real line boxes (character ranges grouped by line top, last line of each paragraph dropped), not estimated.

## Open finding (fix after the reader round, bundled with review-qa fixes)

- **The measure is too long at 768 and 2560: a median of 85 characters, 88 at most.** `60ch` is a Geist `0`-width unit, and Geist's lowercase text is narrower than its zero, so 60ch sets about 85 characters. The acceptance check (`<= 40em`) passed because 60ch is about 36em, which shows the check was too loose. The target is 60–75 characters. Planned fix: `--measure: 32em`. From the measured 7.95px per character at 17px, that's 544px, or about 68 characters. Also tighten the check to a real chars-per-line limit of 75 or fewer. It isn't applied now because the comps are frozen at `cdfee91` while the copywriter's readers run.
- 1440 and 1920 are in range because the split column, not the measure, limits the width there.

## Not verified

Real Safari 26 and real devices. The WebKit numbers come from Playwright's WebKit build.
