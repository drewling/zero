# Implementation evidence

Slice: OPR.99.0.1.3
Seat: development-implementer@zero
Date: 2026-09-28

## Proof contract mapping

1. **Approved direction and copy**
   - `landing/index.html` implements the approved Departure board direction and slice 02 copy, including the approved board word `Archived`.
   - `landing/DESIGN.md` records the design system, responsive behavior, accessibility decisions, and self-hosted font provenance.

2. **Build and behavior checks**
   - `node --test landing/test-site.mjs` passed: 5 tests.
   - `bash -n landing/build.sh landing/deploy.sh macapp/install-zero.sh` passed.
   - `git diff --check -- landing` passed.
   - Docker nginx smoke passed: homepage, `/install` and `/install.sh` redirects, privacy, terms, CSS, JS, Archivo, Geist Mono, panel image, unknown-path 404, installer download, and installer syntax.

3. **Responsive and accessibility checks**
   - Final Aside inspection confirmed the page had `scrollWidth/clientWidth = 1440/1440`, loaded Archivo and the panel image, exposed a native sorting table, and exposed the install command.
   - Responsive proof media is in this directory for desktop, 390px mobile, and 320px mobile layouts.
   - The sorting board uses a native `<table>` with caption, `thead`, `tbody`, and scoped headers. The animated flap board is decorative and the semantic heading remains available to assistive technology.
   - `site.js` bounds the visible tile sequence to under one second, skips the hidden breakpoint board, preserves reduced-motion behavior, and leaves content available without JavaScript.

4. **Preserved seams**
   - Clipboard IDs and status behavior remain intact.
   - Installer command, legal routes, source route, SEO metadata, and real `/assets/zero-panel.png` remain wired for the nginx deployment.

## Residue

The strict visual capture workflow is owned by the independent QA seat. The attached screenshots were produced during local browser verification before the final desktop table-width correction; the final Aside inspection independently confirmed the corrected 1440px overflow result. QA should recapture strict policy-compliant visual evidence before approval. No deployment or push was performed.
