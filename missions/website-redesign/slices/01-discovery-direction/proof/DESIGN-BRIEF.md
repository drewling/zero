# zero.headless.com: direction brief (slice OPR.99.0.1.1)

Author: design-lead@zero (claude-opus-5-5). Date: 2026-09-28. Status: **APPROVED by main-lead@zero 04:54Z** with the refinement in §7.
Mockup: `proof/mockup/index.html` (open with `?static` to skip the flap animation). Captures: `proof/mockup-{desktop,mobile,mobile-320}-{viewport,full}.png`.

## 1. Direction: "Departure board"

**THESIS.** The page works like a station departure board. You glance at it, see what still needs you, and see that everything else was dealt with. It rejects the category default: a near-black ground with a left headline and a glowing screenshot stage, which is literally the current site and the Linear/Raycast look.

**OWN-WORLD.** A signal-yellow ground (`#FFC72C`) covers the whole page, with enamel-navy type (`#0A1F44`). Black split-flap tiles (`#161514` housing, `#23211F` flap with a hairline split) and warm off-white glyphs (`#F4EFE2`). A navy install band gives the page one tonal change. The type is Archivo, a variable face with a width axis: condensed 72-80% caps for the board and headings, normal width for body copy. Geist Mono appears only in the install command and the label chip. Lines are ruled with 2-3px navy rules, so the page is built from rules rather than cards. Only "Stays" gets the signal colour on the board. "Set aside" is dim, with an outline dot.

**STORY.** First, what zero is (a menu-bar app that keeps what needs you and archives the rest). Then the real app. Then what counts as "needs you". Then proof that nothing is deleted. Then everything it needs, sends and costs. Then install.

**FIRST VIEWPORT (1440×900).** A full-measure flap board reads KEEP THE MAIL / THAT NEEDS YOU. It is about 210px tall and aria-hidden, with a real sr-only `<h1>`. Under it sit two columns at 5:6. On the left: a one-sentence lead, the navy **Install zero for Mac** button with a "Read the installer first" link, and a ruled Needs/Sorting/Cost list. On the right: the **real** `zero-panel.png` at about 745px wide, top at 408px, captioned "Names and subjects are fictional." On mobile at 390 and 320, the board has 3 rows × 10 tiles, the CTA is full width at about 424px, and the app image follows the requirements.

**FORM.** Split-flap departure board, grounded candidate 5 of 7 (`proof/00-grounding.md`). Seed `cd8d10fe`, direction scope, persuade mode (`proof/01-concept-seed.txt`).

**Signature interaction.** The headline tiles cycle and settle once, left to right, in under 1s, then stay still. The static state is the default under `prefers-reduced-motion`. Nothing else on the page flips. The sorting board is static text styled as tiles.

**FINISH.** unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

### Challenger verdicts (roll `cd8d10fe`) and what the direction kept

| Challenger | Verdict | Kept into the direction |
| --- | --- | --- |
| Jet-age ticket wallet | **Competitive** (strong on product clarity: "nothing disappears, it cancels"; weaker audience fit) | *Raise, from ticket wallet:* "Set aside" is a visible state with its own mark. It is never shown as removal. Full alternate if the board reads too loud. |
| Night instrument six-pack | Declined | *Raise, from six-pack:* colour discipline. Only one state (Stays) gets the signal colour, like amber reserved for caution. |
| Scher street poster | Declined | *Raise, from street poster:* type at architectural scale. The headline board spans the full measure instead of sitting in a column. |
| Hand-drawn zine | Declined | *Raise, from zine:* one mark highlights the line that matters, and nothing else competes with it. |
| Alphabet storm | Declined | Letters are the material. The tiles are the headline, with no separate illustration. |
| Sneaker box wall | Declined | The fixed label grid became the three-column Before you install table (label, fact, caveat). |

My pick if not the roll: grounded candidate 1, **the dated recovery stamp**. The safety mechanism itself would become the identity. Risk: it is close to the "office ephemera" look many utilities use. I did not serve the interactive decision page. Main-lead asked me not to block on an optional aesthetic choice, so this brief is the decision surface.

## 2. Reference study (captured 2026-09-28 ~04:38Z, `proof/refs/`)

| Site | Observed (desktop and mobile captures) | Take | Refuse |
| --- | --- | --- | --- |
| [Linear](https://linear.app/) | Near-black `rgb(8,9,10)` ground. Inter Variable plus Berkeley Mono. Two-line left headline, then a full-width, full-fidelity product frame bleeding off the fold. Eight nav items. | Real product at real scale, straight after the promise. Confident type. | The dark-plus-mono identity, the nav sprawl, and the staged agent UI. |
| [Raycast](https://www.raycast.com/) | Near-black ground, centred Inter headline. "Download for Mac" with "macOS Tahoe and Apple Silicon required" in small mono **directly under the button**. | Requirements next to the action. zero already does this, and it stays. | A centred empty hero, and the nine-item pill nav. |
| [Vercel](https://vercel.com/) | Light `#fafafa`, GeistSans. Two-word category claim, two CTAs, then a customer logo wall. | A terse claim. | The logo wall and "Talk to sales". zero has no customers to cite and must not invent them. |
| [Granola](https://www.granola.ai/) (4th) | White ground, serif display (melange/quadrant), real app window over a collage, "Download for free" plus platforms line. A cookie modal covers the hero. | A distinctive own-world type voice next to a real app window. | The cookie wall (zero has no analytics and needs none) and the collage chrome. |
| [Things](https://culturedcode.com/things/) (extra) | Light blue-grey, centred icon, "award-winning" claim. | Calm, native Mac feel. | An unsupported superlative. |
| zero live (incumbent) | `rgb(21,19,19)` charcoal, Geist, coral CTA, app in a dark red-gradient stage. | The copy structure and truth ledger, which were already verified. | Treated as an anti-reference. It is the category default. |

What is borrowed is hierarchy and discipline, never palette, type or components. None of the references is yellow, uses a condensed display face, or uses a board grammar.

## 3. Claims ledger (authority: README > macapp/install-zero.sh > app source > privacy.html; PRODUCT.md is not authoritative)

Every visitor-facing fact in the mockup maps to a source:

- Menu-bar app that keeps what needs action and archives the rest: README "What zero does".
- Apple Silicon, macOS 26+, Gmail, Jev key, TypeSafe bills usage, free/open source: README "Before you install", "Safety and data".
- Not notarized, ad-hoc signed, not in the App Store. The installer may add Python/Node/gws/Claude Code and stops on an unsupported Mac: README plus install-zero.sh.
- Google unverified-app warning, and zero never sees the password: README "First run" 1.
- Thread text goes to Jev, drafts go to the chosen provider, no zero server: README "Safety and data" plus privacy.html.
- Sent only on **Send reply**: README.
- The recovery label format is `🗄️ Auto-Archived YYYY-MM-DD` (lib/inbox_zero.py `_BASE_LABEL`, `_dated_label`). It is shown **as a format**, not as a dated row.
- Board rows paraphrase the `keep-policy.md` defaults. They are labelled "Illustration of zero's default rules. Not a live inbox, and not a guarantee." UI terms are real: Open loops, Waiting on you, Set aside (KeeperModel.swift, PanelView.swift).
- Onboarding strings: Connect your first inbox, Settings → Sorting engine, Get a key, Run zero now, Settings → Rules, Undo (README plus PanelView.swift).

Excluded on purpose: "once a day" and "every thread" (main-lead correction 04:41Z), "Nothing leaves your account" (it contradicts the Jev data path; fixed 04:50Z), metrics, logos, quotes, adoption numbers, and any interactive inbox or Undo toggle.

## 4. Must stay (builder)

- Routes: `/install` and `/install.sh` (302 via nginx.conf), `/privacy.html`, `/terms.html`, `robots.txt`, `sitemap.xml`, `llms.txt`, `og.png`, 404. Keep the static nginx plus Docker and `build.sh` smoke checks, with no framework migration.
- The copy button contract in `site.js` and `test-site.mjs`: ids `install-command`, `copy-command` (hidden until clipboard is available), and `copy-status` (live region); the "Copied." and "copy it manually" messages; disabled while pending. `node --test landing/test-site.mjs` must stay green.
- The warning appears **before** the command (the prior reviewer's finding).
- Real `zero-panel.png` (1349×1166) with its fictional-content caption and provenance. Keep the OG image.
- A11y: sr-only h1, and the flap board is aria-hidden. The sorting board keeps its table semantics with per-row aria-labels (in production, prefer a real `<table>`). Native `<details>` for the FAQ. Visible 3px focus rings (navy on yellow, yellow on navy/black). Contrast (computed WCAG): navy on yellow 10.4:1, ink-soft on yellow 6.7:1, glyph-dim on board 6.2:1, glyph on flap 14.0:1, yellow on board 11.7:1, `#C9CFDC` on navy 10.4:1. All pass AA.
- Motion: one flap settle, skipped under reduced motion, with content visible without JS (the production build should server-render the tiles and let JS only animate).

## 5. Build notes

- Self-host Archivo variable (OFL, width 62-125, weight 100-900), subset Latin, in `landing/assets`. The mockup uses Google Fonts only for convenience.
- The mockup is authoring reference, not production code. Rebuild it semantically in `landing/index.html` and `site.css`. Move the inline styles into classes.
- Tiles: the 15-column desktop and 10-column mobile boards are fixed compositions (two different line breaks), switched at 760px. Board-label words wrap as units, never mid-word.
- Browser surfaces: `::selection` in navy/yellow is done in the mockup. Also theme the scrollbar and the caret in the command block.
- Verified in the mockup: no horizontal overflow at 1440, 390 and 320 (scripted bounding-box check), and the install band contains all its steps.

## 6. Open risks

1. **The yellow is loud.** It is on purpose, but main-lead should judge it for the "exhausted user" read. If it is too much, the fallback is the ticket-wallet alternate or keeping the world with a lighter ground under the fold.
2. The real screenshot keeps its own dark red-gradient backdrop, which reads as a dark plate on yellow. That is acceptable and honest. A cleaner re-export of the panel on a neutral backdrop would improve it, but it needs a real capture from the app. Do not paint one.
3. `DESIGN.md` must be rewritten at finish from the built world (impeccable rule). The current file describes the discarded charcoal/coral world.
4. The direction contract should live in the landing surface brief (`impeccable surface-brief write landing/index.html …`). I did not write into `landing/` because it is outside my boundary. The builder or main-lead should do it at build start, using section 1 above.
5. Copy is draft quality. Slice 02 (/funnels, /slopmonster) owns the final wording. The layout tolerates about ±30% copy length.

## 7. Approved refinement (main-lead, 04:54Z)

The long yellow run on mobile is taxing. Add one warm off-white ground, **ticket stock `#F6F1E4`** with the same navy ink, for **Before you install** and **Questions**. Yellow stays the signature for the hero, sorting board, and Nothing is deleted. The navy install band sits between the two light sections, so the page runs yellow → off-white → navy → off-white. Keep the rules navy and the type unchanged. Contrast: navy on `#F6F1E4` is 14.4:1, and ink-soft 9.3:1 (computed). The builder applies this without a re-mockup.
