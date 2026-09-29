---
id: OPR.99.0.2.4
slice: 04-release
mission: website-motion
status: completed
stage: wip
verified: 2026-09-28 against existing Dokploy raw Compose release proof
created: 2026-09-28
intent: "Deploy the QA-approved motion candidate through the verified raw Compose route and confirm live behavior with rollback ready"
depends_on: [OPR.99.0.2.3]
---

# Slice 04: release and live motion verification

## Intent

Publish only the independently QA-approved motion candidate to zero.headless.com after a fresh production preflight. A local animation demo is not a live outcome.

## Mini-requirements

1. Re-confirm live Dokploy Compose `u2SP2b5035tm1yaHVNcH8`, its one service, current image, healthy baseline and stored/generated Compose before modifying anything. Back up both Compose and prior image. Do not assume Git auto-deploy; it is `sourceType=raw` as of the prior release.
2. Build the reviewed landing bytes on amd64 `production-server`, smoke the candidate in isolation and use the authenticated native Dokploy Compose API to update and deploy only zero-landing. Observe deployment status and retain an exact rollback procedure and image.
3. Verify public homepage and assets actually serve the reviewed candidate. In a real browser, exercise the Canvas focal sequence, representative below-fold beats and reduced-motion/static path on desktop and mobile if tooling permits; otherwise state the visual verification constraint and do not imply live animation was witnessed. Verify `/install`, `/install.sh`, legal routes and installer shell syntax without executing the installer.
4. Record production image ID, source SHA, health, routes, visual evidence and rollback. Roll back if the live user path fails materially.

## Proof contract

- [ ] Fresh Compose/configuration and rollback evidence, deployment result and production container health.
- [ ] Live HTML/CSS/JS/assets tied to candidate plus browser-observed motion and reduced-motion behavior, or an explicit blocked verification path.
- [ ] Installer/legal route and syntax results, residual risks and rollback instructions.

## Status

Released 2026-09-29 02:35Z after independent QA PASS and explicit owner authorization, with exact candidate, isolated Docker/nginx smoke, healthy Dokploy deployment, retained rollback and live browser checks documented in [PROOF.md](PROOF.md). **Technical release passed, but the owner rejected the visual design at 02:43Z.** Replacement visual mission OPR.99.0.3 is active and has not been authorized for build or deployment.
