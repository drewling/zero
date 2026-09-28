# PROOF — OPR.99.0.2.3 Motion, accessibility and performance QA

> **WHO/WHEN:** the impl/QA pair that worked the slice, at slice-close — a slice is NOT done until this file exists and every `SPEC.md` proof-contract item has evidence (mapped 1:1, artifacts under `proof/`). See the `mission-slice-sop` skill + the conventions SSOT (`docs/reference/sdlc-conventions.md` in the repo, `$OPENRIG_HOME/reference/sdlc-conventions.md` on an installed package).
>
> **HOW (the drop verb, not hand-placement):** put media files under `proof/`, then ATTACH them with `rig proof add OPR.99.0.2.3 --artifact-type qa --verdict PASS --candidate-sha <tip> --money-evidence "<one line>" --evidences "1" --media "screenshot-01.png"` — the drop writes the C1 header the Living Notes DELIVERED pairing joins on. Hand-placing files without a drop leaves the deliverable unpaired and `unverified`.

Closed by: review-qa@zero   Date: 2026-09-28   Verdict: **pass-with-residue**

## What this proves

Independently verified the "board sorts" motion/Canvas layer (candidate `0505816f`) against `MOTION-BRIEF.md`'s storyboard and my own slice SPEC: real-viewport visual states at 1440/390/320 with zero overflow, both brief-flagged "unproven" gates (true mobile viewport visuals and rAF performance under throttling) closed with passing measurements, full reduced-motion/no-JS/no-Canvas fallback correctness including live accessibility-tree verification, no verdict-word scramble regression across an exhaustive 50ms-interval sweep, keyboard/touch/interrupt/hidden-tab behavior all correct, zero cross-browser (Chromium+WebKit) console errors, and zero scope/copy/route regressions vs the prior QA'd baseline. See `proof/VERDICT.md` for the full requirement-by-requirement breakdown.

## Artifacts (media in proof/)

Dropped via `rig proof add … --evidences … --media …` (one drop per verdict; media attached, never only hand-listed):

- proof/VERDICT.md — full requirement-by-requirement verdict, methodology, and every measurement with numbers
- proof/command-output.txt — raw log of every check run (node tests, grep, diff-stat, contrast math, perf numbers, a11y tree queries)
- proof/d1440-sort-0.png, d1440-sort-700.png, d1440-sort-1300.png, d1440-sort-settled.png — desktop sort-track motion states vs storyboard `d-sort-*.jpg`
- proof/d1440-rail-0.png, d1440-rail-450.png, d1440-rail-900.png — desktop rail/undo motion states vs storyboard `d-rail-*.jpg`
- proof/m390-sort-mid.png, m390-sort-settled.png, m320-sort-mid.png — TRUE narrow-viewport sort states (closes the brief's named mobile-unproven gate; storyboard's own mobile frames were an iframe-in-desktop-Chrome approximation, not a real viewport)
- proof/m390-install-boarding.png — true-viewport install-steps boarding reveal (never captured at all in the storyboard; prototype tooling timed out on this state)
- proof/m390-reduced-sort.png, m390-reduced-install.png, m320-reduced-sort.png — true-viewport reduced-motion states (also never captured in the storyboard)
- proof/nocanvas-sort-scrolled.png, nocanvas-undo-scrolled.png — no-Canvas-context fallback, matches storyboard `d-nocanvas-*.jpg` intent
- proof/resize-700-settled.png — live resize across the 760px breakpoint, canvas redraws correctly, no overflow

## Residue / caveats (if any)

- **Docker build/smoke: blocked, not waived.** Docker daemon unavailable in this environment (same constraint as slice 02's own PROOF.md, and flagged by main-lead's QA-gate reminder message). Compensated with source syntax checks, static-route checks on a local fallback server, and a byte-identical diff of `nginx.conf`/`Dockerfile` against the already-QA'd baseline (confirms infra untouched). The one thing not verifiable locally is the live nginx `/install.sh` rewrite route and a true containerized boot — recommend an isolated Docker smoke preflight before deploy, per main-lead's guidance.
- Firefox was not installed locally and not exercised in the cross-browser error sweep (Chromium + WebKit only). Not a target platform for this macOS-only product, so treated as a minor non-blocking gap rather than residue against the SPEC.
