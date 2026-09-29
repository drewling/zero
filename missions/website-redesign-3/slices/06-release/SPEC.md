---
id: OPR.99.0.4.6
slice: 06-release
mission: website-redesign-3
status: blocked
stage: wip
verified: 2026-09-29 against mission SPEC
created: 2026-09-29
intent: "Release the QA-passed SHA to zero.headless.com after an explicit owner go, verify live, keep rollback ready"
depends_on: [OPR.99.0.4.5]
owner_seat: main-lead@zero
---

# Slice 06: release

## Mini-requirements

1. Show the owner the QA-passed candidate (screenshots and a local URL) and get an explicit "ship it". Do not deploy without it.
2. Record the current production image or SHA as the rollback target, following the path used in `missions/website-redesign-2/slices/05-panel-redraw/RELEASE.md` (Dokploy).
3. Deploy the exact SHA. Then verify live: the homepage hash matches the build, `/install` and legal routes work, and 1440 and 390 screenshots of the live page are compared with the QA shots.
4. Push the zero repo commits to origin, record the release in the mission PROGRESS, and tell the owner in plain words with the live link.

## Proof contract

- [ ] `RELEASE.md`: the owner go (quote plus time), the rollback target, the deploy id, the live hashes and the live screenshots.
