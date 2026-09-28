# Progress: Motion direction and storyboard

> Durable acceptance state for this slice. In-process steps belong in the
> working agent's todo tool. See the `mission-slice-sop` skill and the
> conventions SSOT (`docs/reference/sdlc-conventions.md` in the repo,
> `$OPENRIG_HOME/reference/sdlc-conventions.md` when installed).

## Acceptance

- [x] Implementation complete: direction, runnable prototype and storyboard under `proof/` (no `landing/` edits)
- [x] Tests passing: `node --check` on the prototype, Aside captures and measurements recorded in `proof/MOTION-BRIEF.md` §6 and §10
- [ ] Review approved: **owner decision pending** on `proof/MOTION-BRIEF.md` §9

## Log

- 2026-09-28 design-lead@zero: measured the production baseline, built the prototype, captured the desktop, reduced-motion and no-Canvas storyboard and a partial mobile set (Aside), and wrote the brief. Awaiting owner approval. No downstream dispatch, per `1c55bd1`.
- 2026-09-28 design-lead@zero: responded to main-lead's review (`be48c02`). Verdicts are now always the real, legible word (dimmed, then a single flap), and the reduced-motion rail swap is now instant. Recaptured 5 desktop frames and removed the stale `m-sort-700`. Ran functional checks T1 to T8 and re-benched through Aside. The results are in brief §6 and §11. Owner decision is still pending.
