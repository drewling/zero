---
name: zero landing
description: A one-bit Macintosh desktop landing page for a Mac menu-bar utility that keeps Gmail conversations needing action visible and archives the rest reversibly.
colors:
  paper: "#ffffff"
  ink: "#000000"
  soft-ink: "#1a1a1a"
  dither: "#000000"
  panel: "#ffffff"
  inverse: "#000000"
typography:
  display:
    fontFamily: "Pixelify Sans, monospace"
    fontSize: "clamp(40px, 6vw, 88px)"
    fontWeight: 600
    lineHeight: .94
    letterSpacing: "-0.03em"
  body:
    fontFamily: "Geist, system-ui, sans-serif"
    fontSize: "17px"
    lineHeight: 1.5
  mono:
    fontFamily: "Geist Mono, monospace"
    fontSize: "15px"
    lineHeight: 1.5
rounded:
  window: "0"
  button: "0"
spacing:
  page-padding: "clamp(20px, 6vw, 88px)"
  section: "clamp(72px, 10vw, 144px)"
components:
  window:
    backgroundColor: "{colors.panel}"
    border: "2px solid {colors.ink}"
    shadow: "6px 6px 0 {colors.ink}"
  dither-surface:
    background: "50% black-and-white halftone"
  title-bar:
    backgroundColor: "{colors.panel}"
    borderBottom: "2px solid {colors.ink}"
  terminal:
    backgroundColor: "{colors.inverse}"
    textColor: "{colors.paper}"
---

## Overview

**Creative North Star: “One-bit Macintosh desktop.”**

The page is a small desktop assembled from windows, folders, a dated archive label, and an empty Trash. It makes zero's mechanism legible at a glance: the visitor sees a message that needs attention, learns which kinds stay in Inbox, sees that archived mail remains recoverable, then gets the real requirements and install command. The visual world is a replacement, not a polish pass over the old departure-board system.

The surface is strict black and white with a 50% dither texture behind solid windows. Striped title bars, pixel display type, Finder-style rules, and Terminal-style install instructions establish the Macintosh reference without pretending the page is an actual operating system. The real app screenshot is the only color image.

## Product evidence and claims

- `assets/zero-panel.png` remains the source product screenshot, and `assets/panel-cut.png` is the approved portrait crop used in the hero. The caption states that names and subjects are made up.
- The rules window is an illustration of zero's default rules, not a live inbox or a guarantee.
- Archive remains reversible. Nothing is deleted. Gmail All Mail and the dated recovery label stay explicit.
- The Jev data path, optional draft provider, Apple Silicon and macOS 26 requirements, unverified Google app warning, ad-hoc signing, and provider billing remain visible.
- No testimonials, logos, adoption claims, unsupported privacy promises, or fictional product features are added.

## Typography and assets

Pixelify Sans is self-hosted for the display voice. The implementation keeps the official Pixelify files and SIL Open Font License notice in `assets/pixelify-400.woff2`, `assets/pixelify-600.woff2`, and `assets/OFL-pixelify.txt`. The files were sourced from the approved comp font inventory at `missions/website-redesign-2/slices/01-research-direction/proof/comps/fonts/`.

Geist and Geist Mono remain self-hosted for body copy, code, and labels, with their existing OFL notice. Archivo and its license file are removed because the approved world no longer uses them. There are no Google Fonts requests. The source product image remains byte-identical; the portrait crop is the approved crop-only derivative used by the B comp.

## Layout and responsive rules

- The first viewport is a dithered desktop with a large white hero window, the real app window, dated archive folders, and an empty Trash cue.
- The current dated folder has one authored 900ms stepped drop on load, matching the approved B moment. Reduced-motion users see the settled folder with no animation.
- Hero copy remains the factual product explanation and the requirements line remains visible near the primary action.
- The rules section uses a native table inside a Finder-style window. The note is outside the table so the accessibility tree has a clear caption, header row, and body rows.
- The recovery section uses the factual dated-label chip and a short list explaining undo, Gmail search, and changing rules.
- Before-install facts remain a readable paper-colored section. Install instructions use a black Terminal panel with the exact command and clipboard fallback.
- The FAQ uses native `details` disclosures. The footer retains Source, Privacy, and Terms.
- At 760px and below, windows become a single readable flow. The dither remains decorative behind panels, the command can wrap or scroll inside its code block, and no content is clipped.

## Interaction and accessibility

The page is complete in HTML without JavaScript. The only script behavior is optional clipboard support for the install command. The Copy button exposes an aria-disabled pending state with a JS guard so keyboard focus remains on the control, plus manual-copy recovery. Native headings, table semantics, caption, `thead`, `tbody`, links, `details`, and visible copy provide the primary accessibility path.

Focus rings remain visible at 3px against both black and white surfaces. Decorative check, folder, and trash symbols are hidden from assistive technology when their adjacent labels already provide the meaning. There is no Canvas, requestAnimationFrame, IntersectionObserver, layout observer, or motion-specific fallback to maintain.

## Build and deployment constraints

The page remains static HTML, CSS, JavaScript, nginx, and Docker. `landing/build.sh` validates the homepage, legal routes, install redirects, CSS, JS, Pixelify and Geist assets, the source product image and approved portrait crop, 404 behavior, and the returned installer script. `node --test landing/test-site.mjs` covers clipboard behavior, structure, product truth, install-step count, compact hero requirements, and absence of the replaced motion implementation.

Deployment is outside this slice. Dokploy currently serves a raw Compose service pinned to an image, so `autoDeploy=true` is not evidence of Git commit deployment. Do not deploy from the landing build slice. If the local Docker daemon is unavailable, record that build and `/install` smoke evidence is blocked and leave release preflight to the lead.
