# PROOF: OPR.99.0.4.3

## Candidate

This proof accompanies the scoped page B rebuild from the owner-approved frozen source `1ad99b34198d01c59e7d9fe52112b0526fd557b8`. The exact committed candidate SHA is reported in the handoff and is the commit containing this proof.

## Requirement-to-check map

| Requirement | Concrete evidence |
|---|---|
| Production page is self-contained under `landing/` | `node --test landing/test-site.mjs` test 6, asset listing in `command-output.txt`, no mission or parent-directory refs |
| Exact approved page B copy, disclosures, cost, privacy boundary, and no schedule promise | tests 1 and 2, plus rendered Aside text from the real local page |
| Compact hero requirements and one dated archive target | test 3 and CSS assertion for `900ms steps(6,end) 700ms both` |
| Complete static state, `?static`, reduced-motion hooks, no prohibited rendering APIs | test 5; `?static` real-page check confirmed zero animated elements in the observed state. Reduced-motion emulation remains QA-owned because the local Aside session exposed no preference control. |
| Clipboard success/denial focus contract | test 4 checks the `aria-disabled` pending guard and absence of native `disabled`; browser success/denial verification remains an independent QA boundary |
| Legal pages, robots, sitemap, llms, 404 | local HTTP checks returned 200 for `/`, legal pages, robots, sitemap, llms, and 404 for `/nope` |
| `/install` and `/install.sh` redirects | `landing/build.sh` contains explicit 302 and fetched-script assertions. Docker execution is blocked by the unavailable local daemon, so this gate is not claimed passed. |
| 320px no overflow and responsive screenshots | not claimed from this seat's Aside session because it could not set a true mobile viewport. Independent QA must provide 1440, 390, and 320 JS-on/off captures. |
| Replacement inventory and banned-phrase lint | obsolete Pixelify and panel assets removed; all banned explanatory phrases are absent, with two `open loops` hits limited to literal product-tab UI labels |

## Before / after inventory

- Replaced the old landing document, styles, story script, and stale test assumptions with the approved B structure and copy.
- Added self-contained `kit.css`, `page.css`, `chicagoflf.woff2`, `motion.js`, and `sections.js` under `landing/assets`.
- Removed tracked Pixelify font files, Pixelify license, and `zero-panel.png` because the approved page is an HTML/CSS one-bit redraw.
- Retained legal pages, nginx/Docker packaging, installer route configuration, robots, sitemap, and llms files.
- Updated `DESIGN.md` and `build.sh` to describe and check the production bundle.

## Evidence

- `proof/command-output.txt` contains exact test, route, Aside, and Docker observations.
- No screenshots are fabricated. Desktop evidence is real at 1440x900. Mobile geometry and reduced-motion captures remain explicitly pending independent QA because the approved Aside session could not resize or emulate preferences.

## Status

Implementation checks pass. Docker/nginx release smoke is blocked by the local Docker daemon. No deploy or push was performed. Review approval remains with the independent QA and main lead.
