---
id: OPR.99.0.3.2c
slice: 02c-content-rebuild
mission: website-redesign-2
status: gated
depends_on: [OPR.99.0.3.2b]
intent: "Integrate the owner-approved story into the clean one-bit B landing and hand an exact candidate to independent QA"
---

# Slice 02c: rebuild the approved story

## Intent

After owner approval of slice 02b's outline and copy, the builder reorders and edits the clean B page to match it. Preserve the real app, the restrained folder-drop with reduced-motion settled state, semantic content, install/clipboard/legal routes and the removal of old departure-board code.

## Mini-requirements

- Implement the **approved** outline and wording rather than carrying the first B candidate's old order forward. The one-bit visual system should support the visitor decision path, not add clutter.
- Resolve the Copy button keyboard-focus defect: Enter on focused Copy must not strand focus on BODY on success or denied clipboard writes. Preserve pending guard and status announcement, and cover both paths.
- Update tests for actual headings, order, essential disclosures and absence of retired sections/hooks. Verify narrow and desktop public-page behavior. No release from this slice.

## Proof contract

Map approved outline/copy and safety facts to the committed HTML; show before/after word count, browser screenshots, keyboard Copy success/denial, true 1440/390/320 geometry, reduced motion, static fallback, source diff and test output. If Docker is unavailable locally, leave nginx install redirects as a clearly named release preflight, not as passed. Hand exact SHA to independent QA.
