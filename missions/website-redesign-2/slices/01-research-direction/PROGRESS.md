# Progress: slice 01

- 2026-09-29 02:47Z: Claimed `qitem-20260929024721-d48cab59` (design-lead@zero).
- Captured and reviewed 12 live references and kept 10 (`proof/references.md`).
- Derived three concept-seed directions (`proof/evidence/concept-derivation.md`).
- 03:05Z: Owner rule received: replace the old code and do not overlay it. Wrote `proof/replacement-inventory.md`.
- Built comps A, B and C plus a phones harness. Did two Aside capture passes, and fixes after the first covered light-band strength, wrapping the install code on mobile and icon rendering in B.
- Wrote `proof/DESIGN-BRIEF.md` (critique, the directions, the recommendation and the owner decision).
- Status: **awaiting owner choice** (A, B or C). Slice 02 (rebuild) must not start until the owner approves a direction.
- 03:25Z: Accuracy pass after the handoff. The critique now rests on source-checked claims (flap board, sr-only h1, warning box), and the 390 iframe and static shots were all viewed. A sentence diff restored two abridged install steps in the comps (the shots predate this). New comp lines are listed in DESIGN-BRIEF §3.
- 03:28Z: At main-lead's request, recaptured the 3 install shots and 4 phone shots from a fresh clone of 54b51a9 (Aside). They now show the corrected install steps. Also checked the owner viewing path (all comp assets return 200 from the clone, and the production routes resolve) and recorded interpretations in DESIGN-BRIEF §6.
- 03:43Z: main-lead flagged A's time-rail label as clipped at 390. Cause: a `nowrap` label at `left:50%`, hidden by `body{overflow-x:hidden}`, which `scrollWidth` cannot detect. Fixed only in the mobile media query: the label anchors right, wraps and sits under the tick row. `phones.html` now counts `past right edge` (2 before the fix, 0 after, in all comps). Recaptured phone shots and added `shots/a-rail-390.jpg`.
