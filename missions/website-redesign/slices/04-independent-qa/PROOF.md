# PROOF — OPR.99.0.1.4 Independent visual and functional QA

> **WHO/WHEN:** the impl/QA pair that worked the slice, at slice-close — a slice is NOT done until this file exists and every `SPEC.md` proof-contract item has evidence (mapped 1:1, artifacts under `proof/`). See the `mission-slice-sop` skill + the conventions SSOT (`docs/reference/sdlc-conventions.md` in the repo, `$OPENRIG_HOME/reference/sdlc-conventions.md` on an installed package).
>
> **HOW (the drop verb, not hand-placement):** put media files under `proof/`, then ATTACH them with `rig proof add OPR.99.0.1.4 --artifact-type qa --verdict PASS --candidate-sha <tip> --money-evidence "<one line>" --evidences "1" --media "screenshot-01.png"` — the drop writes the C1 header the Living Notes DELIVERED pairing joins on. Hand-placing files without a drop leaves the deliverable unpaired and `unverified`.

Closed by: review-qa@zero (claude-sonnet-5)   Date: 2026-09-28   Verdict: **PASS**

## What this proves

Independent QA compared the built landing candidate against the approved slice-01 mockups, the slice-02
claims ledger, and this slice's own SPEC requirements. Two material defects were found (an invisible
keyboard focus ring on both `.button` instances, and a FAQ token-storage wording overclaim vs
`privacy.html`); both were repaired by builder/design-lead and independently re-verified fixed against the
corrected committed SHA before this pass verdict was issued. Full detail, evidence, and per-requirement
pass/fail is in `proof/PROOF.md` (the qa artifact registered below).

## Artifacts (media in proof/)

Dropped via `rig proof add` at commit `e0bfb42` (artifact-type `qa`, verdict `PASS`,
candidate_sha `57deff2a49eb56791c5634afe795a933c11ddc2a`):

- `proof/PROOF.md` — full per-SPEC-requirement pass/fail narrative: visual/responsive compare vs slice-01
  mockups, keyboard/focus/contrast/motion/alt-text a11y checks, full 28-row claims-ledger cross-check
  against repo source, `build.sh`/`node --test` smoke results, and the two defect-found-and-repaired
  writeups (focus ring, FAQ row 26).
- `proof/screenshots/built-desktop-1440.png` — clean 1440 desktop render of the corrected candidate.
- `proof/screenshots/built-mobile-320-full.png` — full-page 320 mobile render of the corrected candidate.
- `proof/screenshots/focus-ring-nav-fixed-chromium.png` — nav "Install" button showing the repaired
  visible navy focus ring.
- `proof/screenshots/focus-ring-hero-fixed-chromium.png` — hero "Install zero for Mac" button showing the
  repaired visible navy focus ring.

## Residue / caveats (if any)

- True native device-metrics emulation (Aside CLI) was blocked in this environment (hung with no
  actionable output); Playwright cross-engine (chromium + webkit) real-browser automation was used as the
  documented substitute. This is real browser-engine rendering, not a stub, but is explicitly not claimed
  equivalent to true device emulation. See `proof/PROOF.md` Requirement 1 for the full framing.
- Two non-blocking hygiene nits: an unreferenced `geist.woff2` asset, and a cosmetic mid-word break in the
  install URL at narrow widths (command still fully wraps, no clipping, Copy button copies the correct
  unbroken string).
