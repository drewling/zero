---
name: zero landing
description: A one-bit Macintosh desktop landing page for a Mac menu-bar utility that keeps Gmail conversations needing action visible and archives the rest reversibly.
colors:
  paper: "#ffffff"
  ink: "#000000"
  dither: "#000000"
  panel: "#ffffff"
typography:
  display:
    fontFamily: "Geist, system-ui, sans-serif"
    fontSize: "clamp(40px, 6vw, 88px)"
    fontWeight: 700
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
  ui:
    fontFamily: "ChicagoFLF, Geist, system-ui, sans-serif"
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
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
---

## Overview

**Creative North Star: “One-bit Macintosh desktop.”**

The page is a small desktop assembled from windows, folders, a dated archive label, and an empty Trash. It makes zero's mechanism legible at a glance: the visitor sees a message that needs attention, learns which kinds stay in Inbox, sees that archived mail remains recoverable, then gets the real requirements and install command. The visual world is a replacement, not a polish pass over the previous departure-board system.

The surface is strict black and white with a dither texture behind solid windows. Striped title bars, Chicago UI labels, Geist headings, Finder-style rules, and Terminal-style install instructions establish the Macintosh reference without pretending the page is an actual operating system. The hero product window is an HTML/CSS redraw of zero's real Open loops panel, so the page carries no product screenshot dependency.

## Product evidence and claims

- The hero redraw shows the product's Open loops state, account badges, tabs, count, waiting-on-you rows, action labels, recovery affordance, and Run zero now control. It adds no product features. Names and subjects are explicitly made up.
- Archive remains reversible. Nothing is deleted. Gmail All Mail and the dated recovery label stay explicit, with a six-step CSS-only folder drop for the newly dated archive folder.
- The Jev data path, optional draft provider, Apple Silicon and macOS 26 requirements, unverified Google app warning, ad-hoc signing, and provider billing remain visible.
- No testimonials, logos, adoption claims, unsupported privacy promises, or fictional product features are added.

## Typography and assets

Geist is self-hosted for headings and body copy. Geist Mono is self-hosted for the terminal command and code labels. ChicagoFLF is self-hosted for short UI labels, window titles, tabs, buttons, and the footer. The Chicago font file is retained with the existing `OFL.txt` notice. There are no Google Fonts requests and no product screenshot asset in the production page. Pixelify and its license file were removed because the approved B direction does not use them.

The production bundle is self-contained under `landing/`. CSS, JavaScript, fonts, and markup do not reference mission proof paths or parent directories.

## Layout and responsive rules

- The first viewport is a dithered desktop with a large white hero window, the real app window, dated archive folders, and an empty Trash cue.
- The current dated folder uses one authored `900ms steps(6, end) 700ms both` drop on load. `?static` and reduced-motion users see the settled folder with no animation.
- The visitor order is hero, judgment, ambient use, reversibility, requirements/data/cost, and install. The page supports the visitor decision path instead of repeating a feature inventory.
- The hero keeps one compact requirements line near the primary action. The app panel is a one-bit popover with a notch, and its rows are drawn as the app's rounded cards.
- The panel is decorative and inert. Its visible content is accompanied by an accessible summary. No drawn controls can be focused.
- Before-install facts remain a readable paper-colored section. Install instructions use a black Terminal panel with the exact command and clipboard fallback.
- At 760px and below, windows become a single readable flow. The command can wrap or scroll inside its code block, and the page reserves no fixed-width content that can create horizontal overflow.

## Interaction and accessibility

The page is complete in HTML without JavaScript. Optional scripts provide the folder-drop animation and clipboard support only. The Copy button uses an `aria-disabled` pending state plus a JavaScript guard instead of native `disabled`, so keyboard focus remains on the control on both clipboard success and denial. Manual-copy recovery is always visible.

Focus rings remain visible at 3px against both black and white surfaces. Decorative symbols are hidden from assistive technology when adjacent labels provide the meaning. There is no Canvas, layout observer, scroll-jacking, audio, or pointer-reactive effect.

## Build and deployment constraints

`node --test landing/test-site.mjs` covers the page B metadata and section order, approved disclosure and recovery copy, exact install command, four semantic install steps, compact hero requirements, folder-drop timing and reduced/static fallbacks, pending clipboard focus behavior, motion safety, accessibility structure, and self-contained assets. `landing/build.sh` validates the homepage, legal routes, install redirects, CSS, JS, ChicagoFLF and Geist assets, 404 behavior, and the returned installer script.

Docker and nginx smoke are release-gate checks because `/install` and `/install.sh` are redirects in the container. Deployment is outside this slice. Dokploy currently serves a raw Compose service pinned to an image, so `autoDeploy=true` is not evidence of Git commit deployment. If the local Docker daemon is unavailable, record the build and redirect smoke as blocked and leave release preflight to the lead.
