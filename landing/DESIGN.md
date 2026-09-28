---
name: zero landing
description: A departure-board landing page for a Mac menu-bar utility that keeps Gmail conversations needing action visible and archives the rest reversibly.
colors:
  signal-yellow: "#FFC72C"
  enamel-navy: "#0A1F44"
  ink-soft: "#2B3F66"
  board-black: "#161514"
  flap-face: "#23211F"
  glyph: "#F4EFE2"
  glyph-dim: "#9C958A"
  ticket-stock: "#F6F1E4"
typography:
  display:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(40px, 5.2vw, 76px)"
    fontWeight: 800
    fontStretch: "78%"
    lineHeight: .98
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 450
    lineHeight: 1.5
  mono:
    fontFamily: "Geist Mono, monospace"
    fontSize: "15px"
    lineHeight: 1.7
  board:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontStretch: "72%"
    fontWeight: 800
rounded:
  board: "12px"
  tile: "clamp(3px, .35vw, 5px)"
  button: "8px"
  command: "10px"
spacing:
  page-padding: "clamp(20px, 5vw, 72px)"
  section: "clamp(72px, 9vw, 128px)"
  content-gap: "clamp(28px, 5vw, 80px)"
components:
  departure-board:
    backgroundColor: "{colors.board-black}"
    tileColor: "{colors.flap-face}"
    glyphColor: "{colors.glyph}"
    desktopColumns: 15
    mobileColumns: 10
  primary-button:
    backgroundColor: "{colors.enamel-navy}"
    textColor: "{colors.signal-yellow}"
    rounded: "{rounded.button}"
  install-command:
    backgroundColor: "{colors.board-black}"
    fontFamily: "{typography.mono.fontFamily}"
  ticket-section:
    backgroundColor: "{colors.ticket-stock}"
---

## Overview

**Creative North Star: “Departure board.”**

The page behaves like a station departure board. A visitor glances at the headline, sees what still needs them, then follows the route through the real app, default sorting rules, reversibility, requirements, costs, and install steps. The page is a replacement visual world, not an extension of the discarded charcoal and coral system.

The visual language is signal yellow ground, enamel navy rules and type, black split-flap tiles, warm glyphs, and a navy install band. The approved refinement adds ticket-stock off-white to the **Before you install** and **Questions** sections so the long mobile read does not become an uninterrupted yellow field.

## Product evidence and claims

- The real `assets/zero-panel.png` is the only product image. Its caption says names and subjects are made up.
- The board is an illustration of default rules, not a live inbox or a guarantee.
- Archive is described as reversible. Nothing is deleted. Gmail All Mail and the dated recovery label remain explicit.
- The Jev data path, optional draft provider, Apple Silicon and macOS 26 requirements, unverified Google app warning, ad-hoc signing, and provider billing remain visible.
- No testimonials, logos, metrics, adoption claims, or unsupported privacy promises are used.

## Typography and assets

Archivo is self-hosted as the Latin-subset variable `assets/archivo-latin.woff2`, with width axis 62–125 and weight axis 100–900. Its source is the Archivo project at commit `b5d63988ce19d044d3e10362de730af00526b672`; the matching `assets/ARCHIVO-OFL.txt` records the SIL Open Font License and provenance. Geist Mono remains self-hosted for the install command and recovery label.

The mockup used Google Fonts only as an authoring convenience. Production has no Google Fonts request. The Docker image copies the complete `assets/` directory.

## Layout and responsive rules

- The desktop headline board is two rows by 15 columns: `KEEP THE MAIL` and `THAT NEEDS YOU.`
- The mobile board is three rows by 10 columns: `KEEP THE`, `MAIL THAT`, and `NEEDS YOU.` It switches at 760px.
- The hero uses a 5:6 text-to-product split before collapsing to a single column.
- Sorting rules use a dark timetable board. `Stays` gets signal yellow. `Archived` gets a dim outline mark.
- Before-install facts use a three-column label, fact, caveat table on wide screens and a single readable flow on narrow screens.
- The install band is navy. Questions return to ticket stock.
- The page was authored against the approved 1440px, 390px, and 320px captures with no horizontal overflow as an acceptance requirement.

## Interaction, accessibility, and motion

The headline tiles are server-rendered and visible without JavaScript. JavaScript only cycles and settles them once when reduced motion is not requested. `prefers-reduced-motion: reduce` disables the animation and transitions. The visual board is `aria-hidden` and the semantic headline is the screen-reader-only `h1`.

The sorting board retains row and cell semantics. The FAQ uses native `details` disclosures. Focus rings are three pixels and switch to signal yellow on navy and board surfaces. The install command keeps the `install-command`, `copy-command`, and `copy-status` IDs, including clipboard fallback text and pending-button state.

## Build and deployment constraints

The page remains static HTML, CSS, JavaScript, nginx, and Docker. `landing/build.sh` must validate the homepage, legal routes, install redirects, CSS, JS, Archivo, Geist Mono, product image, 404 behavior, and the returned installer script. `node --test landing/test-site.mjs` covers clipboard behavior and critical page structure.

Deployment is intentionally outside this surface. Dokploy currently serves a raw Compose service pinned to an image, so `autoDeploy=true` is not evidence of Git commit deployment. Do not deploy from the landing build slice.
