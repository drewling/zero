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

## Follow-up candidate evidence

The follow-up candidate restores the approved page metadata contract, including `theme-color`, `color-scheme`, canonical, Open Graph/Twitter tags, an inline favicon, and a real 1200x630 `assets/og-image.png` generated from the rendered hero. The final local file hash is `778a627d5ced1173ff450f02cd484d4f027722811687c11a27d0f027cf8a73bd`.

The hero remains one compact `.req` line and one dated folder target. The disallowed `.folder-current` / `folder-drop` animation and all related overrides were removed per design direction. The terminal typing overlay now reserves the real command's layout, hides the full command while glyph sprites are active, positions glyphs and caret absolutely, preserves the Copy slot, and retains the no-JS fallback.

Concrete checks on the current working tree:

- `node --test landing/test-site.mjs`: 7/7 pass.
- `node --test landing/test-terminal.mjs`: Chromium and WebKit pass at 1440px and 390px, including 150/500/850/1600ms playback samples, no simultaneous full-command/overlay visibility, absolute overlay placement, Copy-slot stability, and final settled command.
- Fresh real Playwright matrix: `proof/shots/playwright-matrix.json`, 13 rows covering Chromium/WebKit at 1440/390/320, JS on/off, plus reduced motion. The rerun reported no rows where `scrollWidth`, `bodyScrollWidth`, and `clientWidth` differed. Title and OG image URL matched on JS and no-JS rows.
- Fresh terminal frame captures are in `proof/shots/terminal-{chromium,webkit}-{1440,390}-{150,500,850,1600}.png`.
- `bash landing/build.sh`: pass. Docker built `zero-landing`, nginx served homepage/legal/assets, `/install` and `/install.sh` returned 302, and the fetched installer parsed as bash. Manual served hashes and redirect locations are recorded in `command-output.txt`.

The earlier sections retain the original pre-Docker-block observations for history. This section supersedes their pending mobile and Docker status for this follow-up candidate. No deploy or push was performed. VoiceOver/axe and formal performance auditing remain outside this implementation check and independent QA may rerun them.

## Status

Scoped follow-up implementation checks pass locally and through the Docker/nginx public interface. Exact-SHA review approval remains with independent QA and the main lead.
