---
id: OPR.99.0.3.5
slice: 05-panel-redraw
mission: website-redesign-2
status: in-progress
owner: design-lead@zero
requested_by: advisor-lead@kernel (owner Tayo, 2026-09-29 15:35Z)
intent: "Re-create the hero app screenshot as real HTML/CSS in the site's one-bit language, faithful to the real panel"
---

# Slice 05: redraw the hero panel

## Intent

Tayo, 15:35Z: "on the zero site we should re-create this in the style of the rest of the site". "This" is the hero screenshot `landing/assets/panel-cut.png`. It is a dark macOS raster with a blue count and red and blue pills, and it clashes with the one-bit B world.

## Mini-requirements

- **Faithful to the real app structure** (`macapp/Sources/PanelView.swift`, `KeeperModel.swift`, `Style.swift`):
  - Header: the wordmark, account badges with inbox counts, and the More menu.
  - Tabs: Open loops, Accounts, Undo, Settings.
  - The count, the "things still need you" subline, and "Across N accounts. Tap any to open it in Gmail."
  - The "Waiting on you" rows: avatar, sender, subject, category tag (Needs reply, Action required), preview chevron and age.
  - Row actions: Reply, AI archive and Archive.
  - The footer: "Tidies every inbox to only what needs you." and **Run zero now**.
- No invented features. Names and subjects stay fictional.
- The caption must be honest: "zero's real layout, redrawn. Names and subjects are made up."
- It must work at 1440, 390 and 320 with no clipping or horizontal overflow.
- It is decorative but meaningful. Use `aria-hidden` plus `inert`, with an sr-only text summary, and nothing focusable in the tab order.
- Honour reduced motion. Keep it static HTML, CSS and JS, and it must work without JS.
- Update `landing/build.sh`, `landing/test-site.mjs` and `landing/DESIGN.md` wherever they reference `panel-cut.png`. Keep `zero-panel.png` as source evidence and as the og:image.
- Process:
  1. Make 1 or 2 directions as screenshots and pick one.
  2. Build it.
  3. review-qa checks Chromium at 1440, 390 and 320, reduced motion and no JS, and compares faithfulness against `zero-panel.png`.
  4. Send advisor-lead the before and after shots and the candidate SHA.
- **No push or deploy.** advisor-lead releases after QA.

## Proof contract

`PROOF.md` maps each item above to evidence:
- a faithfulness table (element, real source, redraw)
- the direction shots and the pick rationale
- before and after at 1440, 390 and 320
- the overflow counters
- the a11y tree and tab-order checks
- `node --test` and `build.sh` results
- the review-qa verdict
