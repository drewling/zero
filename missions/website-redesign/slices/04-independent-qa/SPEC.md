---
id: OPR.99.0.1.4
slice: 04-independent-qa
mission: website-redesign
status: blocked
stage: wip
verified: 2026-09-28 against scaffold (rig scope create)
created: 2026-09-28
intent: "Compare delivery to mockups and verify desktop/mobile, accessibility, copy claims, and install routes"
depends_on: [OPR.99.0.1.3]
---

# Slice 04: Independent visual and functional QA

## Intent

Catch defects and truth gaps before exposing the redesign to visitors.

## Mini-requirements

1. Independent reviewer compares desktop/mobile screenshots to approved mockups, checks hierarchy, typography, image fidelity, spacing and responsive edge cases. Have builder repair material differences and re-check once.
2. Check keyboard-only navigation, focus order/visibility, contrast, reduced motion, alt text, copy button, disclosures and narrow/wide viewport behavior.
3. Audit all product, privacy, setup and pricing claims against repository source. Test primary links and local `build.sh` smoke, including installer route and legal pages. Mark external blockers explicitly.
4. State pass/fail per requirement with evidence and remaining risks. No claim that automated tests equal visual acceptance.

## Proof contract

- [ ] QA verdict per requirement with captures and reproduction steps for defects.
- [ ] Tests and repairs re-run with observed results; independent compare verdict attached.
- [ ] Release recommendation identifies any blockers or accepted caveats.
