# PROOF — OPR.99.0.2.2 Motion and Canvas implementation

> **WHO/WHEN:** the impl/QA pair that worked the slice, at slice-close. A slice is not done until this file exists and every `SPEC.md` proof-contract item has evidence mapped 1:1, with artifacts under `proof/`.
>
> **DROP NOTE:** media artifacts should be attached with the rig proof workflow when independent QA supplies them. This implementation handoff records text evidence only because the available browser workflow did not produce a media artifact.

Closed by: development-implementer@zero  Date: 2026-09-28  Verdict: pass-with-residue pending independent QA

## What this proves

The approved “The board sorts” direction is implemented as a progressive enhancement of the existing landing page. The static semantic page remains the source of truth while optional Canvas tracks, a recovery rail, replay controls, install boarding, copy feedback, and FAQ feedback activate only when supported. No deployment was attempted.

## Requirement mapping

1. **Approved Canvas focal and supporting beats**
   - `landing/index.html` adds the hidden sort and recovery Canvas surfaces plus replay controls.
   - `landing/site.js` implements the 7-row sort timeline, visible DOM verdict words, stays bloom, archived drop, recovery rail, boarding reveal, copy flap, and FAQ feedback.
   - Aside at 1440x900 observed the native table, replay control, restore control, FAQ expansion, and no console errors. Exact recovery control text changed from `Show a restore` to `Show the archive again` after activation.

2. **Progressive enhancement and lifecycle**
   - Static HTML keeps the semantic table, readable verdict words, install command, native FAQ details, legal links, and no-JS content.
   - Canvas elements are `aria-hidden` and hidden until a working 2D context is available. Reduced motion exits spatial motion setup and applies settled behavior for the rail.
   - `IntersectionObserver` gates first play and pauses after exit. `document.hidden` pauses and resumes active timelines. `ResizeObserver` remeasures. DPR is capped at 2. Replay restarts deterministically. No prototype query hooks are present.

3. **Existing contracts and checks**
   - `node --test landing/test-site.mjs`: 5 passed, 0 failed.
   - `node --check landing/site.js`: passed.
   - `bash -n landing/build.sh landing/deploy.sh macapp/install-zero.sh`: passed.
   - `git diff --check -- landing`: passed.
   - Installer parse passed as the first stage of `bash landing/build.sh`.

4. **Real rendering and finish detector**
   - Aside real-browser smoke at the available 1440x900 viewport is recorded in `proof/command-output.txt`.
   - The final Impeccable detector was run against `landing/index.html`, `landing/site.css`, and `landing/site.js`. It reported existing design-system/advisory findings and pre-existing slop warnings; no new detector-specific repair was required for this scoped motion handoff.

## Artifacts

- `proof/command-output.txt` — exact source checks, real-browser observations, and validation limitations.

## Residue / caveats

- Docker smoke is **blocked**, not passed: `bash landing/build.sh zero-motion-candidate-1` reached installer parsing, then failed because the local Docker daemon was unavailable at `unix:///Users/light/.docker/run/docker.sock`. Release preflight or QA must rerun the Docker route smoke in an available runtime.
- Aside did not expose viewport emulation or `prefers-reduced-motion` controls. Strict 390/320 mobile, reduced-motion, and performance/frame-budget verification remain independent QA gates and are not waived.
- This candidate is not deployed. Independent QA must review the candidate SHA and may report repairs before release.
