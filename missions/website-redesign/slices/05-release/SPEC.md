---
id: OPR.99.0.1.5
slice: 05-release
mission: website-redesign
status: blocked
stage: wip
verified: 2026-09-28 against scaffold (rig scope create)
created: 2026-09-28
intent: "Confirm actual deployment wiring, release the checked site, verify live homepage and installer, and document rollback"
depends_on: [OPR.99.0.1.4]
---

# Slice 05: Dokploy release and live verification

## Intent

Ship the QA-approved redesign to zero.headless.com and prove the actual user path works.

## Mini-requirements

1. Determine which Dokploy project/application/domain serves this site and whether Git integration auto-deploys from a branch. Cross-check against repository `landing/deploy.sh` (legacy GCP/SSH path) and DNS/live headers. Do not guess or overwrite unrelated deployment.
2. Release only QA-approved commit with known rollback target. If auto-deploy exists, observe its status rather than trigger a duplicate release; otherwise use the authenticated native route.
3. Verify `https://zero.headless.com/`, `/install`, `/install.sh`, privacy, terms and key assets after deployment. Confirm the served page includes a unique redesign marker and installer returns parseable shell script.
4. Record deployment ID/commit, live response and rollback command or control. If access is blocked, leave production unchanged and document exact blocker.

## Proof contract

- [ ] Dokploy application and deployment configuration evidence, not assumption.
- [ ] Deployment result, served commit/marker, live route checks and installer syntax.
- [ ] Rollback target and outstanding risk recorded; no live claim if verification failed.
