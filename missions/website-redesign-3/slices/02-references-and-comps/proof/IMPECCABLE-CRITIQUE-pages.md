⚠️ DEGRADED: single-context (no sub-agent tool in this jcode seat, and the rig's policy forbids spawning helpers). Assessment A (design review of the real captures) was written before any detector output was read.

# /impeccable critique: page-a and page-b at cdfee91 (frozen)

Targets: `comps/page-a/index.html` and `comps/page-b/index.html`, served at `127.0.0.1:8941`. Mode: **Persuade** (landing page). Context: repo `PRODUCT.md` (the one job, reversible by construction, ambient, the model decides) and `landing/DESIGN.md` (one-bit Mac, Geist body). The comps are frozen while the copywriter's six readers run. **This is a record only, with no edits.** Fixes go into the single post-reader and review-qa batch.

## A. Design review (1440 and 390 full captures, beat stills)

**Design specificity: specific.** Every section object is zero's own UI (the menu-bar popover, the Undo tab, the Settings Rules pane, Get Info on the app icon, Terminal) in one System 7 grammar. An unrelated product couldn't reuse it unchanged. The old risk was that the pixel type made the page hard to read. T3 fixes that without losing the Mac voice, which now lives in the windows, labels and icons.

| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of system status | 3 | Beats show zero doing the work. The hero's final Inbox is 4 rows in a mostly empty window at 1440 (hero territory, slice 04's reserved slot) |
| 2 | Match with the real world | 4 | Real app labels throughout: `Restore all`, `Settings → Rules`, `All Mail` |
| 3 | User control and freedom | 3 | Recovery is concrete in both outlines. The illustrated controls look pressable but aren't, which is correct for an illustration, but a sceptic may try to click them |
| 4 | Consistency and standards | 3 | One window chrome everywhere. Page B alternates split-r and split-l, while page A has one split band, then a full ledger, then ink |
| 5 | Error prevention | 3 | The ledger comes before the command on both pages, and B leads with it |
| 6 | Recognition over recall | 3 | Section h2s say the point. The Rules text is dense monospace |
| 7 | Flexibility | n/a | Landing page |
| 8 | Aesthetic and minimalist | 3 | See issues 1 to 3 |
| 9 | Error recovery | n/a | No forms, apart from Copy command, which falls back to a selectable command |
| 10 | Help and documentation | 3 | Privacy, TypeSafe pricing and Releases links sit where the question comes up |

**Cognitive load.** No decision point shows more than 4 options. The hero offers 2 CTAs. The ledger is the heaviest block at 5 rows and about 150 words, which is accepted because it's the must-read.

**Emotional journey.** The peak is the Undo balloon `Put this email back in the inbox`, the relief moment. The end is the ink Terminal, a calm and concrete finish. The valley is the ledger on B, straight after the hero: risk before the reader has seen any payoff. That's by design for the risk-first outline, and the readers decide whether it costs trust or earns it.

**Strengths**
1. The objects prove rather than decorate: the Undo rows and the balloon *are* the reversibility claim.
2. Headings read at a glance at every width (OCR 0.93 at 320 and 390, against 0.30 to 0.35 for Pixelify).
3. The ink install band gives the page a clear end and a single action.

**Priority issues (for the fix batch)**
1. **Empty halves in B's split bands at ≥1100.** Rules has 4 lines of text against a 490px window, so the left column is about 55% empty. Undo is the same, with 3 lines against a 450px window. SPEC §4 says "no empty halves". Fix: centre `.txt` vertically on the field (`align-self:center`) in split bands. It's CSS only, with no new words.
2. **The ledger's odd row leaves a hole.** Five rows in 2 columns (`grid-auto-flow:column`, 3 rows) leaves an empty cell under `Installer`, and the column rule stops short, so it reads as unfinished. Fix: let `Sorting cost` span both columns, or flow the rows as 3 + 2 with the rule running to the bottom.
3. **The prose measure is 85 characters at 768 and 2560** (LAYOUT-GRID open finding). Fix: `--measure:32em` and a real-line check.
4. **The Rules editor wraps mid-clause.** The source's hard break ("…uses a real / human name…") plus soft wrapping in a narrow editor gives 3 ragged lines. The words are verbatim and have to stay. Option: widen the editor within the field, or reduce the editor font a step at ≥1100. Ask the copywriter before touching the source line break.
5. **Page A's Undo band carries 3 paragraphs**, the most prose on either page, beside the densest object. Copy is the copywriter's call. Design-side, it makes page A's split visually heavier than B's. Record it for the readers and review-qa to weigh.

**Persona red flags.** A *sceptical Gmail user* may try clicking `Restore all` in the illustration. The `Illustration. Made-up mail.` label is present but small. A *mobile visitor* at 390 scrolls about 5,100px on B, with the ledger in the first scroll after the hero.

**Minor.** The `→` in `Settings → Rules` is Geist inside ChicagoFLF labels (by design, no glyph). The fixed draft flag overlays content at the bottom left in captures (proof-only, excluded from counts).

**Provocative questions.** Does B need the Undo band at all, when the ledger and Rules already name the recovery label? Could A's Undo band lose its second paragraph to the Rules link?

## B. Detector evidence (read after A was written)

**CLI** (`impeccable detect --json`, exit 2), 16 findings across both files:

| Rule | Count | Verdict |
|---|---|---|
| overused-font (Geist, Geist Mono) | 4 | **False positive by brief.** They're the incumbent body faces in `landing/DESIGN.md`, and the Mac voice is carried by ChicagoFLF and the one-bit objects |
| repeating-stripes-gradient | 2 | **False positive by brief.** These are System 7 title-bar stripes, the pinned idiom |
| cramped-padding (`li`, `.field`, `.band`, `.bar`) | 10 | **Mostly false positive.** The Undo rows are 52px minimum with 6/14px insets and a bottom rule by design. `.field` and `.band` are full-bleed containers whose children are windows, not text. `.bar` is the title bar. Checked in the captures: no text touches a border |
| tight-leading (1.29×) | 2 | **Unlocated.** The CLI doesn't name the element (line 0). Headings are set at 1.02 on purpose, and body prose is 1.58, so it's likely one small label or caption. Find it in the fix batch before judging |

**Browser** (the impeccable live-server `detect.js` injected into Chromium at 1440 for A and B, and at 390 for B). It found overused-font and repeating-stripes, as above, plus `text-occlusion` of `p.draft-flag`. **False positive:** the flag is `position:fixed; z-index:99; pointer-events:none`, so `elementFromPoint` passes through it, and it's visibly on top in every capture. The live server (PIDs 86197 and 92628) was stopped after each run.

**Where they agree.** Neither flags type legibility, contrast or overflow. The detector missed all five priority issues. They're compositional (empty halves, the ledger hole, measure, wrap, prose weight), which is the kind of thing only the visual review catches.

## Run notes

- Target slug: not persisted, because this is a proof run and the snapshot lives here.
- There is no `.impeccable/critique/ignore.md`.
- Independence was sequential, with A before B (degraded).
- Aside wasn't used: this critique needs a detector injection into a local page, and Playwright is the allowed engine for that.

Questions skipped: this is a proof-only run inside the rig, and the owner gate goes through main-lead. The findings go into the single post-reader fix batch and to review-qa.
