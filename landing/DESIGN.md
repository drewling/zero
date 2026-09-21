---
name: zero landing
description: A restrained, plainspoken landing page for a Mac menu-bar utility that keeps Gmail's open loops visible.
colors:
  charcoal: "#151313"
  warm-surface: "#1e1a19"
  warm-white: "#f5f1ee"
  muted-stone: "#bfb6b1"
  hairline: "#403836"
  coral: "#ffaaa0"
  coral-hover: "#ffcbc3"
  dark-ink: "#261513"
  command-black: "#110f0f"
  control-brown: "#302825"
typography:
  display:
    fontFamily: "Geist, Arial, sans-serif"
    fontSize: "clamp(46px, 5.35vw, 76px)"
    fontWeight: 560
    lineHeight: 1.04
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Geist, Arial, sans-serif"
    fontSize: "clamp(32px, 3.5vw, 46px)"
    fontWeight: 530
    lineHeight: 1.13
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Geist, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Geist, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 550
    lineHeight: 1.4
  mono:
    fontFamily: "Geist Mono, monospace"
    fontSize: "13px"
    lineHeight: 1.7
rounded:
  control: "9px"
  panel: "16px"
  command: "10px"
  small: "6px"
spacing:
  page-gutter: "48px"
  section: "100px"
  content-gap: "32px"
components:
  primary-button:
    backgroundColor: "#ffb1a6"
    textColor: "{colors.dark-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "15px 21px"
  product-shot:
    rounded: "{rounded.panel}"
  command-block:
    backgroundColor: "{colors.command-black}"
    rounded: "{rounded.command}"
    padding: "16px"
---

## Overview

**Creative North Star: "A useful Mac utility, shown plainly."**

The landing page is a restrained product showcase: warm charcoal, warm-white Geist, a quiet coral action color, and one large bounded view of the real app. It explains the promise before the mechanics, then makes setup, privacy, reversibility, and limitations easy to find. The result should feel crafted and calm in the spirit of Raycast, without imitating Raycast's identity or inventing an interactive inbox.

**Key Characteristics:**
- Plainspoken product clarity over spectacle.
- Warm dark surfaces with one soft coral action voice.
- Real product evidence, fictional demo content clearly captioned.
- Generous two-column breathing room that collapses cleanly on small screens.
- Trust information is part of the interface, not buried in decoration.

**The Plain Utility Rule.** Show one useful Mac utility, one clear installation path, and the real product image. Do not make the page compete with the app.

## Colors

The page uses charcoal as its continuous canvas, a slightly lifted warm surface for setup, warm-white for primary reading, muted stone for supporting copy, and coral for actions, links, focus, and hover. The blue checkmark icon is a fixed brand mark, not a general palette role.

**The Single Accent Rule.** Coral carries action and attention; do not introduce a second promotional accent.

## Typography

Self-hosted Geist is the only family. Large headings are medium-weight, tightly tracked, and balanced rather than ornamental. Body copy is readable and conversational. Geist Mono is reserved for the install command. Keep the hierarchy compact: display promise, section headline, explanatory body, then small operational labels.

**The Useful Scale Rule.** Typography should make the next decision obvious: understand, inspect, install, or review.

## Layout

The shared content frame is capped at 1200px with a 48px desktop gutter. The first viewport places left-aligned promise, explanation, action, requirements, and cost note beside one large product image. Workflow and FAQ use two-column editorial layouts; setup uses a text-and-steps split inside the lifted surface. Sections are separated by hairlines and generous vertical rhythm, not cards everywhere.

On narrower screens, columns become a single readable flow at 760px, while the 1100px breakpoint reduces gutters and inter-column gaps. At 1500px and above, the hero gets more vertical room. The navigation remains a compact horizontal pair; it does not become a stacked menu.

**The Evidence-Adjacent Action Rule.** Keep requirements and cost directly below the install action so the decision is informed before the click.

## Elevation & Depth

Depth is tonal, not glossy. The page is mostly flat charcoal with one warm-surface installation band, near-black command block, thin hairlines, and the product screenshot's own visual detail. There are no decorative shadows or gradients in the landing system. On desktop widths of at least 1000px, the product image arrives over 0.8s with a restrained clip-path reveal and 12px upward translation, using `cubic-bezier(.16,1,.3,1)`; reduced-motion users receive no animation.

## Shapes

Use gently rounded controls and panels: 9px for the primary action, 10px for the command block, 16px for the product image, and 6px for compact controls. FAQ rows are line-led rather than enclosed cards. Focus uses a 3px coral outline with a 6px offset and must remain visible.

**The Quiet Container Rule.** Round containers only when they group a meaningful object or action; do not turn every text block into a card.

## Components

- **Brand and navigation:** Small blue checkmark plus `zero`, with sparse text links and no heavy navigation chrome.
- **Primary install button:** Coral, dark ink text, download icon, and a clear product-specific label. Hover lightens the coral; focus is explicit.
- **Product shot:** The supplied `zero-panel.png`, displayed large with a 16px radius and a centered note that names and subjects are fictional.
- **Workflow list:** Three plain text blocks with strong short headings and muted explanations. No icon grid or fabricated metrics.
- **Setup steps:** Ordered steps use outlined numbered circles, a monospace install command, copy affordance, and an expandable caveat for security and prerequisite details.
- **FAQ details:** Native disclosure rows with hairlines, plus/minus affordance, and concise answers.
- **Footer:** Minimal brand, source, privacy, and terms links.

## Do's and Don'ts

### Do:
- **Do** use self-hosted Geist and Geist Mono from `landing/assets`.
- **Do** preserve the warm charcoal, warm red-coral, and warm-white relationship.
- **Do** show the actual product image and label fictional demo content.
- **Do** state macOS 26+, Apple Silicon, Gmail, Jev key, provider billing, privacy, and reversibility plainly.
- **Do** keep interactions native, sparse, keyboard-visible, and understandable.

### Don't:
- **Don't** clone Raycast, add neon gradients, or turn the page into a generic SaaS dashboard.
- **Don't** invent inbox interactions, testimonials, metrics, or product capabilities.
- **Don't** use `Persuade` as a universal visual rule; it belongs to a surface brief when explicitly requested.
- **Don't** hide risk: zero can be wrong, sends thread text to configured services, and is ad-hoc signed.
- **Don't** replace the simple install path with competing offers or distracting secondary CTAs.
