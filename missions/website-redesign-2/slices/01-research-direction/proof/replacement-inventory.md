# Replacement inventory: keep, replace, remove

**Status:** proof only. Nothing in `landing/` was edited. The inventory was read from the tree at `69f15d2` on 2026-09-29.

**Owner rule (main-lead, 03:05Z):** the redesign **replaces** the old landing code. It does not overlay or accumulate on it. Slice 02 rebuilds HTML, CSS and JS around the chosen direction and deletes the departure-board system. It must then prove that no legacy hooks or duplicate systems remain in the shipped `landing/` tree.

## Keep unchanged: infrastructure and truth

| Item | Why it survives | Slice 02 check |
|---|---|---|
| `nginx.conf` with `/install` 302 to raw `macapp/install-zero.sh` and `/install.sh` 302 to the GitHub view | The headline install path. The redirect keeps the installer single-sourced. | `build.sh` already asserts 302 on both, and that `curl -fsSL /install` returns a bash script that parses. |
| `Dockerfile` (nginx:alpine, `HEALTHCHECK` on `/` and the `/install` 302) | Deploy contract | Edit only the `COPY` lines if file names change, for example after deleting `archivo-latin.woff2` or renaming the bundles. |
| `build.sh`, `deploy.sh` | Smoke test and deploy path | Update the font check (Archivo → the chosen face). Keep every route check. |
| `privacy.html`, `terms.html` | Legal routes linked from the footer | They carry their own inline `<style>` and don't use `site.css`. Keep the content. Restyle them to the new system in slice 02, then check that they stay 200. |
| `robots.txt`, `sitemap.xml`, `llms.txt` | Discovery | No change needed. `llms.txt` copy is truthful. |
| `assets/zero-panel.png` (1349×1166) | The only real app image. It is also `og:image`. | It must stay byte-identical. The comps use a rounded-corner crop (`proof/comps/panel-cut.png`, derived by crop and alpha mask only). Slice 02 may ship such a crop as a new file, but must keep the original for OG. |
| `assets/geist.woff2`, `assets/geist-mono.woff2`, `assets/OFL.txt` | Used by B and C as body and mono, and by A for mono only | Keep whatever the chosen direction references. Delete the rest. |
| All product copy and disclosures in `index.html`: hero line and lede, requirements line, default-rules table and disclaimer, the "Nothing is deleted" block with the label format `🗄️ Auto-Archived YYYY-MM-DD`, Undo, Settings → Rules, the whole **Before you install** table (Mac, Gmail and unverified-app warning, Jev key and billing, where mail goes, replies, ad-hoc signing and tools added), the install four steps and SHA-256 line, the FAQ, and the footer licence | Product truth and safety | Carry the words over verbatim unless the owner edits them. The comps show the hero, rules, recovery and install. **Before you install** and the FAQ are not comped, but they must survive in the build. |
| Links: `/install.sh`, `https://github.com/drewling/zero`, `/releases`, `https://console.typesafe.ai/keys`, `/privacy.html`, `/terms.html`, canonical, OG and Twitter meta | Routes | Keep the link check in tests. |
| **Copy-to-clipboard behaviour** (`site.js` lines 1–21: reveal only if `navigator.clipboard` exists, disabled while pending, "Copied." and "copy it manually" status, "Copy again") and its four unit tests in `test-site.mjs` | Accessible, tested install affordance | Keep the behaviour and tests. Move it into the new single bundle. Rename the IDs only if the tests move with them. |

## Replace: rebuild from scratch in the chosen system

| Item | Today | Replacement |
|---|---|---|
| `index.html` markup | Departure-board structure (`.hero` split-flap title with `aria-hidden` letter grid, `.sorting-board` with desktop and mobile board variants, `.rail-wrap`, `.ticket-section` ×2, `.install-band`) | New semantic document: `header`/`nav`, hero, rules, recovery, before-you-install, install, FAQ (`details`), footer. Same copy. Real `<table>` for rules, with no `aria-hidden` duplicate headline. |
| `site.css` (1,104 lines, Archivo, signal yellow and navy, flap faces, ticket stock, board black) | Departure-board tokens and components | New stylesheet written only from the chosen direction's tokens. Target well under 400 lines. |
| `site.js` (430 lines) | Copy (keep) plus an IIFE motion system (see Remove) | Copy handler plus **at most one** motion moment per the chosen direction (A: CSS sunbeam and rail tick; B: stepped folder drop; C: popover drop). All are CSS-only in the comps, so no Canvas and no rAF timeline are needed. |
| `test-site.mjs` structural test (lines 73–93) | Asserts legacy hooks: `class="sort-track" hidden`, `class="rail-wrap" hidden`, "Run the sort again", `IntersectionObserver`, `ResizeObserver`, `document.hidden`, `archivo-latin.woff2` | Rewrite it to assert the new structure plus the **absence** of every legacy selector listed below. Keep the privacy/terms link and no-Google-Fonts assertions. |
| `DESIGN.md` (departure-board spec: signal-yellow, enamel-navy, flap-face tokens) | Rejected world | Rewrite it after owner approval from the chosen comp's tokens. |
| Favicon (inline SVG, navy and yellow tick) | Old palette | Redraw the tick in the chosen palette. |
| `og.png` (1200×630, unreferenced; `og:image` points at `zero-panel.png`) | Copied by the Dockerfile but not used by any meta tag | Either regenerate it in the new world and point `og:image` at it, or delete it and its `COPY` line. Don't leave it orphaned. |

## Remove: must not exist in the shipped tree

- **Canvas and motion system in `site.js`:**
  - `getContext`, `sizeCanvas`, `timeline`, `playOnceOnView` and `roundRect`
  - `setupSortTrack` (sort-track canvas, flap words, replay)
  - `setupRail` (rail-diagram canvas, "Show the archive again")
  - `setupBoarding`, `setupCopyFlap` and `setupFaq` (`faq-ready`)
  - the `COLORS` table, the `timelines` array, the `document.fonts.ready` reseek, and `.motion-reduced` toggling
- **Markup hooks:**
  - the `canvas.sort-track` and `canvas.rail-diagram` elements
  - the `.sort-replay` and "Run the sort again" button, and "Show the archive again"
  - the split-flap `aria-hidden` hero letter grids (desktop and mobile)
  - the `.flap-board`, `.flap-row`, `.desktop-board` and `.mobile-board` variants
- **CSS selectors** (all in `site.css`): `.sorting-board`, `.has-track`, `.sort-track`, `.status` flap styles, `.rail-wrap`, `.rail-diagram`, `.boarding`, `.will-board`, `.install-band`, `.ticket-section`, `.flap-*`, `.board-foot`, `.tile`, `.faq-ready`, `.motion-reduced`, `.demo-button`, `.label-demo`, `.undo-list`. Also every token named signal-yellow, enamel-navy, board-black, flap-face, glyph or ticket-stock.
- **Assets:** `assets/archivo-latin.woff2` (187 KB) and `assets/ARCHIVO-OFL.txt`, unless the owner picks a direction that uses Archivo. None of the three comps does.
- **Tests:** the assertions that require the hooks above.

## Proof that slice 02 must show

1. A before and after `git diff --stat landing/` and a file list.
2. `grep -rE "sort-track|rail-diagram|sorting-board|flap|ticket-section|install-band|boarding|motion-reduced|archivo|getContext|requestAnimationFrame" landing/` returns nothing. The exception is `requestAnimationFrame`, which is allowed only if the chosen motion needs it, and none of the comps do.
3. Every selector in the new `site.css` is used by `index.html`, `privacy.html` or `terms.html`, and every asset in `landing/assets` is referenced. Both can be checked with a short script over the tree.
4. `build.sh` passes with all existing route checks.
