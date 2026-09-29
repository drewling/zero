# Slice 02 implementation proof

Candidate: focused repair, source and proof committed together; SHA recorded in the QA handoff
Mission: `OPR.99.0.3.2` / `website-redesign-2`

## Delivered

- Replaced the departure-board landing markup and styles with the approved one-bit Macintosh desktop world.
- Preserved the real product screenshot, factual copy, disclosure sections, FAQ, clipboard install command, legal links, nginx routes, and Docker image structure.
- Added self-hosted Pixelify 400/600 assets and license notice from the approved comp inventory.
- Removed Archivo assets and the unused `og.png` asset and Docker copy instruction.
- Replaced the motion and Canvas script with the existing clipboard behavior only. The page remains complete without JavaScript.
- Reworked the rules presentation to a native table with caption, `thead`, `tbody`, scope attributes, and the explanatory note outside the table.
- Documented the replacement system in `landing/DESIGN.md`.
- Added the approved portrait crop of the real product window so the B hero gives the app its intended prominence on desktop and mobile.
- Collapsed the hero facts into the single compact requirements line shown in the approved B comp.
- Restored the Terminal command and safety warning as the first item in the four-step install list, with a regression assertion for the count.

## Requirement traceability

| Requirement | Evidence | Result |
| --- | --- | --- |
| Approved B one-bit desktop world | `landing/index.html`, `landing/site.css`, `landing/DESIGN.md` | Present. Hero window, dither surface, Finder rules, Terminal install, dated folders, and empty Trash cue are implemented. The hero now uses the approved compact requirements line and portrait app crop. |
| Product truth and copy | Static tests and direct source inspection | Pass. Product image, archive reversibility, Jev data path, requirements, costs, disclosures, FAQ, privacy, and terms remain present. |
| No legacy departure-board/motion implementation | `node --test landing/test-site.mjs`; scoped `rg` absence check | Pass. No Canvas, rAF, observers, old board selectors, Archivo references, or old motion controls in shipped source. |
| No-JS and reduced-motion safety | HTML-only structure and CSS media query inspection | Pass by construction. No required content depends on JavaScript, and the only CSS motion policy is reduced-motion-safe scrolling/transition handling. |
| Install clipboard behavior | Four Node tests | Pass. Exact command copy, denial fallback, pending disabled state, and unavailable clipboard behavior all pass. |
| Install flow semantics | `landing/test-site.mjs`, served homepage extraction | Pass. The visible “Four steps” intro now corresponds to four actual list items, with the Terminal command and warning retained inside step one. |
| Font licensing/source | `landing/assets/pixelify-*.woff2`, `OFL-pixelify.txt`, `landing/DESIGN.md` | Present. Geist and Geist Mono remain self-hosted. |
| Public static files | Local HTTP smoke on port 8877 | Pass for `/`, legal pages, CSS, JS, Pixelify, Geist, Geist Mono, `panel-cut.png`, and `zero-panel.png`. |
| nginx install redirects and packaged Docker image | `landing/build.sh` attempted | Blocked locally. Docker daemon is unavailable. Do not treat `/install` 404 from Python static server as an nginx result. |
| Strict 1440/390/320 layout acceptance | Aside content smoke; independent QA | Pending independent QA recheck of the repaired candidate. The previous true-viewport QA finding required the compact hero line and portrait crop because the app was too low on mobile and too short on desktop. |

## Checks

- `node --test landing/test-site.mjs` -> 6 passed.
- `node --check landing/site.js` -> passed.
- `bash -n landing/build.sh landing/deploy.sh macapp/install-zero.sh` -> passed.
- `git diff --check -- landing` -> passed.
- Scoped absence check across shipped source -> no banned legacy references.
- Local static files -> expected 200 responses for page, legal pages, CSS, JS, all four self-hosted fonts, and app image.
- Impeccable detector -> no errors, with advisory warnings for intentional one-bit title-bar repeating stripes, approved retained Geist body/mono fonts, and a few undocumented tonal/radius values. These are recorded as advisories, not acceptance claims.
- The focused source assertion now checks four install `<li>` elements, the first Terminal step, the compact `.hero-req` line, and the approved `panel-cut.png` reference.

## Browser evidence and limitations

Aside opened the real local page and confirmed the one-bit hero, native rules table, install command, FAQ, legal links, and no mutation. Its available browser object did not expose viewport resizing, so 1440/390/320 scroll-width and clipping evidence is intentionally delegated to independent QA. No browser console or page error was reported in the content smoke.

The follow-up real-page interaction smoke exercised the first FAQ disclosure and the install Copy button. The FAQ exposed the required statement that Google sign-in tokens are stored on the Mac. Copy changed the button to `Copy again` and announced `Copied. Paste it into Terminal when you’re ready.` The browser accessibility snapshot exposed the native table with caption and eight rows, the FAQ disclosure, the install command, legal links, and the expected keyboard-focusable controls. No form was submitted. Aside could not provide a console error stream or true viewport resizing, so those claims remain outside this proof.

The repaired-candidate real-page acceptance smoke then observed the approved compact requirements line, `/assets/panel-cut.png` at its natural 700 × 1057 ratio rendered as 372 × 560, four install list items in order, an opening FAQ disclosure, and a working Copy button that changed to `Copy again` with its live status. This closes the direct browser checks for the repaired public output while strict 1440/390/320 geometry remains with independent QA.

The explicit source/integration matrix also observed: the source app image SHA-256 stayed `cfc92f3926d69b134cab2c092b8c70b9df7b205e7b44158ddffa3ec717eb2686`; the approved portrait crop is tracked separately and referenced by the hero; one stylesheet, one script, and one script event listener remain; all six shipped binary assets are referenced by page, stylesheet, or smoke packaging checks; both font license files are present; key page content is delivered in the HTML source without JavaScript; and the local public server returned 200 for the homepage, legal pages, CSS, JS, all four fonts, and both app images, with `/nope` returning 404.

`bash landing/build.sh` parsed the installer, then stopped at the Docker daemon connection:

```text
ERROR: Cannot connect to the Docker daemon at unix:///Users/light/.docker/run/docker.sock. Is the docker daemon running?
```

Release preflight must run the Docker image and verify `/install` and `/install.sh` return 302 before deployment. No deployment was attempted.
