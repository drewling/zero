# Design brief: replacing zero's landing world

Owner-facing. design-lead@zero, 2026-09-29. Proof only: nothing in `landing/` changed.

## 1. What is wrong with the live page (critique)

The evidence is the owner's rejection ("trash") plus the live captures at `~/.jcode/scratch/zero-live-sort-mid.png` and `zero-live-rail-mid.png` (2880×1800, 2026-09-28). The rules-section and recovery-rail frames are reproduced at half size as `evidence/live-sort.jpg` and `evidence/live-rail.jpg`.

1. **A costume, not a world.** Signal yellow, enamel navy, split-flap letters and ticket stock say "airport", but zero is a quiet menu-bar utility. None of the references that feel premium (atlas items 1, 7 and 8) dress a product as a different object.
2. **Everything shouts.** The heavy condensed caps sit at the same weight on every section ("WHAT STAYS. WHAT GETS ARCHIVED.", "NOTHING IS DELETED.", "BEFORE YOU INSTALL"), so there is no hierarchy between the promise and the small print. The yellow field under navy caps reads as a warning sign.
3. **The product is small and dark on a loud field.** The real app is the best asset the page has, yet it competes with a black board panel of the same darkness in the next section. Linear and Things make the real UI the largest element on screen.
4. **Two dark slabs on yellow.** The rules board and the app image are both near-black rectangles with drop shadows, so the page reads as heavy blocks and not as a sequence.
5. **The motion is a mechanism, not a meaning.** Canvas sort tracks, a rail diagram with seven navy pills and "illustration · same 7 · none deleted", a replay button and a boarding reveal all need explaining. The rail frame (`live-rail.jpg`) is a big empty yellow area with a tiny diagram and a caption that reads as debug text.
6. **Type costumes.** Mono is used as texture ("illustration · same 7") rather than for data, and the tracked "K E E P · T H E · M A I L" letter grid is `aria-hidden` duplication.
7. **The install warning looks like an alarm.** The non-notarized disclosure is true and must stay, but it deserves the calm, first-class treatment of Raycast and Tailscale, not a hazard band.

## 2. Three directions (all use the real copy, the real app image and the real install command)

Each opens at `proof/comps/<file>` over a local server from `proof/comps/`. Add `?static` to see the reduced-motion and static state. Mobile views come from `phones.html?<file>`.

### A · First light (recommended)

- **Comp:** `comps/a-first-light.html`
- **Desktop shots:** `shots/a-top.jpg`, `a-sort.jpg`, `a-install.jpg`
- **Motion start and settled:** `a-t0.jpg`, then `a-top.jpg`
- **Static:** `a-static.jpg`
- **Mobile:** `a-phones.jpg`, `a-phones-static.jpg`

**The world.** A cool, shaded morning room (`#e6eaee`) and one warm band of window light (two panes split by a mullion) falling across the real app. The light is the only accent on the page, and it means "needs you":

- Rows that stay sit in the light.
- Rows that are archived stay in shade at 4.8:1, still readable and above WCAG AA. Stayed-row text on the light is 4.9:1 (`#8a5a00` on `#fbe7b3`) and ink is 13.3:1, computed with the WCAG formula.
- A tabular time rail says "07:30 · your daily run, at a time you set".

**Type.** Hanken Grotesk 300 with a 600 emphasis on the promise ("Keep the mail that **needs you.**") takes Stripe's two-tone lesson without the gradient. Geist Mono is used only for times, dates and the command.

**Motion.** One authored moment: the band slides into place and the rail marker ticks to 07:30 on load (2.4 s, exponential ease-out, from an already visible state). No scroll-driven effects. Reduced motion shows the settled frame.

**Why it wins.** It is the moment the product is for (open the laptop, only what needs you is lit). It is calm where the old page shouted. It lets the real app be the brightest, largest object on screen. It also looks like nothing else in the category: the nearest precedent, Mercury, uses a painted landscape and not light as a state.

**Risks.** Light that is too faint reads as a gradient glitch. The comp's band is `#fbe7b3` with a 9 px edge blur, and it should be tuned on real displays. Hanken is a new font dependency (OFL, 3 weights, about 45 KB).

### B · One-bit desktop (bold alternative)

- **Comp:** `comps/b-one-bit.html`
- **Shots:** `shots/b-top.jpg`, `b-sort.jpg`, `b-install.jpg`, `b-static.jpg`, `b-phones.jpg`

**The world.** The 1984 Macintosh desktop in one-bit black and white: a 50% dither pattern, striped title bars and Pixelify Sans headings. zero's real window is **the only colour on screen**. Archived mail appears as dated folders on the desktop, named with the real label format. The Trash sits in the corner, labelled "empty". The rules are a Finder list, and the install is a Terminal window.

**Motion.** The day's folder drops onto the desktop in six steps, the way classic Mac windows zoomed.

**Why.** Mac users know it by heart. It tells "nothing is deleted" by showing where the mail goes (a dated folder, not the Trash). The single colour window makes the real app unmissable.

**Risks:**
- It is a period costume, so the owner may find it cute rather than premium.
- The dither is heavy at full width, and the build would need a lighter pattern field or a smaller desktop area.
- The hard 4 px drop shadow is legitimate only because this world owns it.
- A pixel display face costs some readability at small sizes, so body text stays in Geist.

### C · Native macOS utility (safe alternative)

- **Comp:** `comps/c-native.html`
- **Shots:** `shots/c-top.jpg`, `c-sort.jpg`, `c-install.jpg`, `c-static.jpg`, `c-phones.jpg`

**The world.** The page is macOS itself:

- Apple's light grey (`#f5f5f7`), with Geist in place of SF, which can't be self-hosted.
- A centred headline.
- A real menu bar strip with zero's tick icon, and the real popover dropping down from it.
- Rules and recovery set as Settings-style grouped lists with Stays and Archived badges.
- The install shown as a grouped card with an amber "Read this first" callout.

**Motion.** The popover drops from the menu-bar icon once (520 ms).

**Why.** It shows exactly what zero is and where it lives, with the lowest risk and the fastest build.

**Risks.** It is the most familiar option and sits close to Things, Raycast and CleanShot pages. It is clean, but not memorable, and the owner asked for "unmistakably zero".

### Not offered: a dark Linear-style page

It is the category default, and the owner already rejected a dark-board look. It stays available only as a standing exit.

## 3. What stays true in every direction

- The copy is carried verbatim from `landing/index.html`: hero, lede, requirements, default rules and their disclaimer, "It gets things wrong sometimes", Nothing is deleted, the label format `🗄️ Auto-Archived YYYY-MM-DD`, Undo and Restore all, Settings → Rules, the not-notarized warning, SHA-256, the Jev key and TypeSafe link, and the AGPL footer. **Before you install** and the FAQ are not comped, but they carry over unchanged (see `replacement-inventory.md`).
- The app image is the real `zero-panel.png`, cropped to the popover with rounded corners by crop and alpha only (`comps/panel-cut.png`). It is not retouched, and the caption "Names and subjects are made up" stays.
- Illustrative values are labelled:
  - The 07:30 in A is labelled "at a time you set". In C, "Tue 29 Sep 07:30" is only the scene's menu-bar clock.
  - The dated folders in B use the real label format with example dates.
  - "Trash · empty" states zero's behaviour, since zero archives and never trashes. It is not a live reading.
- Routes: `/install.sh`, `#install`, GitHub, Releases, the TypeSafe keys page, `/privacy.html` and `/terms.html` all keep their current targets.

## 4. The decision needed from the owner

Choose **A, B or C** (or "A with B's folders", since the dated-folder idea can move into A's recovery section). Also say whether any headline copy may change, because all three comps keep the current words. Once a direction is approved, slice 02 rebuilds `landing/` from scratch per `replacement-inventory.md`. There will be no overlay on the departure-board code.

## 5. Method limits, stated honestly

- The comps are code-rendered HTML, not generated images, and were captured by Aside at a 1440×900 CSS viewport.
- **Mobile is a 390 px-wide same-origin iframe** (`comps/phones.html`), not device emulation: there is no mobile user agent, touch or DPR change. Aside cannot set a true viewport. All three comps measured `scrollWidth 390` at 390, so there is no horizontal overflow.
- The first viewport, the rules section and install are comped. Before you install, the FAQ, privacy and terms are not.
- A's sunbeam intensity is judged on one display only.
