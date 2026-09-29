---
id: OPR.99.0.3.2c
slice: 02c-content-rebuild
mission: website-redesign-2
status: assigned
depends_on: [OPR.99.0.3.2b]
intent: "Integrate the provisionally approved story into the clean one-bit B landing and hand an exact candidate to independent QA"
---

# Slice 02c: rebuild the approved story

## Intent

After provisional owner choices were relayed by `advisor-lead@kernel` at 2026-09-29 05:13Z, the builder may integrate slice 02b's six-section, 608-word draft into B. The owner can veto in the morning. This authorization is strictly for build and independent QA, not a production release. See `../../PROGRESS.md` for Q1(a), Q2 and Q3 and the no-release gate. Preserve the real app, the restrained folder-drop with reduced-motion settled state, semantic content, install/clipboard/legal routes and the removal of old departure-board code.

## Mini-requirements

- Implement the **provisionally approved** outline and wording rather than carrying the first B candidate's old order forward. The one-bit visual system should support the visitor decision path, not add clutter.
- Resolve the Copy button keyboard-focus defect: Enter on focused Copy must not strand focus on BODY on success or denied clipboard writes. Preserve pending guard and status announcement, and cover both paths.
- Update tests for actual headings, order, essential disclosures and absence of retired sections/hooks. Verify narrow and desktop public-page behavior. No release from this slice.

## Proof contract

Map approved outline/copy and safety facts to the committed HTML; show before/after word count, browser screenshots, keyboard Copy success/denial, true 1440/390/320 geometry, reduced motion, static fallback, source diff and test output. If Docker is unavailable locally, leave nginx install redirects as a clearly named release preflight, not as passed. Hand exact SHA to independent QA.
