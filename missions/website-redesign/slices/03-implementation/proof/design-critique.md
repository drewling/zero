# Design critique: repaired candidate

- Reviewer: design.lead (design-lead@zero)
- Candidate: `e7b5809`. The `landing/` bytes are identical to `5b6da43`, which contains the repair. Pre-fix candidate was `5c84ac2`.
- Date: 2026-09-28 05:39Z
- Mode: read-only. The snapshot was served from `~/.jcode/scratch/cand-5b6da43/landing` on 127.0.0.1:8732, outside the repo.

## Verdict

From a design standpoint, no material visual differences remain against the approved Departure board direction. The repaired mobile rendering is **not** visually proven on real device emulation. That remains QA's call.

## Findings

| # | Issue (pre-fix, 320px) | Status at e7b5809 | Evidence |
|---|---|---|---|
| 1 | Rule table: the "A deadline with a consequence" label touched the status dot (0px gap) | Fixed | All 7 rows have a 10px gap at 320 and 390. Labels wrap inside a 166px box at 320. |
| 2 | Install command was clipped to "curl -fsSL https://z" behind a hidden horizontal scroll | Fixed | `white-space: normal`. scrollWidth == clientWidth (176 at 320, 246 at 390). The full command is visible. |
| 3 | Horizontal page overflow | None | `documentElement.scrollWidth` == innerWidth (318 and 388) |
| 4 | Install step grid is narrow at 320 (about 70px for number and gap, 207px body column) | Minor, not blocking | `gridTemplateColumns` 54.4px / 207.6px |
| 5 | Desktop at 1440 | Unchanged by the repair | Pre-fix captures match the approved mockup in hierarchy, type and board treatment |

## Method and limitations

- Browser: Aside only, per global routing. Aside could not emulate a device viewport and could not save outside its session directory.
- The narrow widths were measured by loading the page in same-origin iframes, 320px and 390px wide, inside an Aside tab. Media queries respond to the iframe width, so this shows the layout, but it is **not** device emulation: there is no touch, DPR or mobile UA.
- The desktop comparison uses the pre-fix captures in `~/.jcode/scratch/crit/` (the repair diff touches only mobile-scoped rules, plus `white-space: nowrap` on the status cell), and the source diff `5c84ac2..5b6da43`.
- The pre-fix captures in `~/.jcode/scratch/crit/` were taken with direct Playwright, before the Aside-only instruction. They support the pre-fix findings only. No repaired-candidate claim rests on them.
- No polish loop was requested or run.

## Evidence

- Aside background task `858361uqh1` (iframe measurements and screenshots), with output at `~/.jcode/scratch/jcode-bg-tasks/858361uqh1.output`
- Screenshots: `~/.jcode/scratch/crit2/sort.png` and `~/.jcode/scratch/crit2/install.png` (320 and 390 side by side)
- Pre-fix captures: `~/.jcode/scratch/crit/`
- Approved mockups: `slices/01-discovery-direction/proof/mockup-*.png`
