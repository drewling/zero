# 05-panel-redraw progress

The request came from advisor-lead@kernel for owner Tayo at 15:35Z: "re-create this in the style of the rest of the site." "This" is the hero raster `landing/assets/panel-cut.png`, and the brief was resent at 15:40Z. Reviewers are review-qa@zero and advisor-lead. There is no push or deploy. Advisor releases using the 04-release pattern.

## Log

- 15:45Z: I read the panel's structure from source.
  - Tabs come from `KeeperModel.swift` `Tab`.
  - Tags come from `lib/review_open_loops.py` (Needs reply, Action required).
  - Header, count, "Waiting on you", row actions (Reply, AI archive, Archive) and the footer with **Run zero now** come from `PanelView.swift`.
  - SPEC.md written.
- 16:05Z: I built two comps under `proof/comp/`:
  - **A** is a square Finder list with dotted rules.
  - **B** is a rounded popover with a notch and bordered card rows.
  - Shots: `before-1440`, `dirB-1440`, `phones-a`, `phones-b`.
  - The Aside `exec` capture of A at 1440 failed twice (a setViewportSize error, then a hang). A is visible at 390/320 in `phones-a.jpg`.
- **Pick: B.** It keeps the real panel's silhouette: popover notch, rounded row cards, pill tabs, a big count, and a black primary button.
  - It still uses only the site's vocabulary: 2px black line, a 4px hard shadow, Pixelify display, and Geist / Geist Mono.
  - A read as a generic Finder list and lost the "this is the menu-bar popover" recognition that the raster gave.
- 16:12Z: I built B in `landing/`.
  - The `<img>` became markup, and the panel CSS was merged into `site.css`.
  - `panel-cut.png` is `git rm`'d.
  - `zero-panel.png` stays as the og:image and source evidence.
  - `build.sh`, `test-site.mjs` and `DESIGN.md` are updated.
- 16:16Z: Self-check found two real defects.
  1. **Stale CSS.** Aside's Chrome rendered the new HTML with a cached old `site.css`, so the panel appeared unstyled at about 5,000px tall. Prod nginx sends no `Cache-Control`, so returning visitors could hit the same thing.
     - Fix: `site.css?v=05` in `index.html`.
     - A test now asserts a versioned stylesheet href.
  2. **Collision.** At 1280–1440 the caption overlapped the Trash cue by 12px. At 761–1100 the HTML panel grows taller than the raster did, because narrow rows wrap.
     - Fix: tightened the count padding.
     - Fix: rows 5–6 are hidden only at 761–1279px.
     - Fix: Trash `bottom` changed from 34px to 16px.
     - Re-measured from 761 to 1440: no overlaps.
- Aside `exec` began hanging, even on the example.com liveness probe, though the daemon was healthy. I killed my own hung execs by PID and switched to `aside repl`, which drives the same Aside browser without the agent. Every capture after that came from `aside repl` with `page.screenshot` at the default 1440x900 viewport.

## Evidence

| Check | Result |
|---|---|
| `node --test landing/test-site.mjs` | 7/7 pass. The new test covers structure faithfulness, 6 rows each with sender, subject, age and 3 actions in app order, only the two real tags, aria-hidden+inert, no focusables, the sr-only summary, the caption, one-bit CSS (only neutral #3d3d3d), no motion, and the versioned CSS href. |
| Negative controls | The old page fails the new tests (2 fail). Injecting `#e5484d` into `.zp-act` fails the one-bit assertion. |
| `landing/build.sh` (Docker) | exit 0, 17 ok lines, including `zero-panel.png` 200. The `panel-cut.png` check was removed. |
| impeccable detect `--no-advisory` | 4 findings (overused-font: Geist), identical to HEAD. No new findings. |
| measure.html at 1440 / 390 / 320 | scrollWidth equals viewport at all three. 0 panel elements past the right edge. 0 clipped text (ellipsis only, by design). Figure overlaps none. Focusables in panel 0. `inert` and `aria-hidden` both true. |
| Desktop sweep (1440, 1280, 1100, 1024, 800, 761) | Caption and panel clear the Trash cue, the hero window and the folders at every width. |
| No JS (sandboxed iframe, scripts blocked) | The panel renders fully: 372x647, 2px black border, radius 14, 6 rows, Pixelify count. The panel has no JS dependency. |
| Reduced motion | The panel has no animation or transition (test-asserted, and 0 computed animations in the render). The existing folder-drop reduced-motion guard is unchanged. |

Shots in `proof/shots/`: `before-1440.jpg`, `after-1440.jpg`, `after-phones-390-320.jpg`, and the direction shots.

## Not verified by me

- A real `prefers-reduced-motion: reduce` emulated render. I asserted it statically, since the panel has no motion.
- Screen-reader output. The structure is asserted, but no VoiceOver pass was done.
- Safari and Firefox. Only Aside's Chromium was checked.
