# Progress — zero website redesign

> Durable acceptance state for this mission. In-process steps belong in the
> working agent's todo tool. See the `mission-slice-sop` skill and the
> conventions SSOT (`docs/reference/sdlc-conventions.md` in the repo,
> `$OPENRIG_HOME/reference/sdlc-conventions.md` when installed).

## Acceptance

- [x] Scope complete: plan and five ordered slices recorded in `d49b160`; specialist design, development and review seats verified.
- [x] Direction and copy approved: Departure board desktop/mobile proof and slice 02 copy/claims deck approved by main-lead at 05:03Z.
- [x] Implementation and local checks pass: QA-approved landing-byte commit `57deff2`; 5/5 node tests, shell syntax and Docker/nginx smoke passed. Independent QA captured current desktop/mobile rendering and verified the corrections.
- [x] Independent QA / review pass: verdict **PASS** against landing candidate `57deff2` (registered at `e0bfb42`); defects in focus visibility and FAQ wording repaired and re-verified. See slice 04 proof.
- [x] Production Compose deployment and live user-path verification: native Dokploy Compose deployment of `zero-landing:57deff2` completed on 2026-09-28; healthy container and live homepage byte-for-byte match verified, with legal/assets and installer routes green. See slice 05 proof.
