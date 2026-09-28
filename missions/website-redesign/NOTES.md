---
mission: OPR.99.0.1
name: zero website redesign
created: 2026-09-28
---

# Notes — zero website redesign

Context and observations that help the mission but do not change its
`SPEC.md` contract or `PROGRESS.md` acceptance checklist belong here.

## Notes

- 2026-09-28 05:08Z: Fresh read-only GCP IAP SSH preflight succeeded. Exactly the expected `zero-zerolanding-m7cxtx-zero-landing-1` container is running `zero-landing:14e9e2b`, healthy for six days; the generated Compose file exists. This is a pre-release baseline only. Re-check the container, stored Dokploy Compose and rollback target immediately before any image swap.
- 2026-09-28 04:54Z: Mission owner approved design.lead's **Departure board** direction after reviewing desktop, 390px and full mobile captures in `slices/01-discovery-direction/proof/` and `DESIGN-BRIEF.md`. It is distinctly its own world, shows the real app and immediate install path, and retains disclosures. For copy/build: add a subtle tonal break (warm off-white acceptable) in the long mobile below-fold information run to relieve sustained signal yellow without losing the signature. FAQ copy must distinguish local app operation from sending thread text to Jev. Approval is of visual direction, not final wording or shipping code.
- 2026-09-28: Plan and five slices committed as `d49b160`. `/impeccable` updated globally via skills CLI at 04:30Z; its lock hash is `01fe78e7bc253016bfc30a3d12036bbf90f1c1bc`.
- Seats verified by operator via exact Jcode sockets and `rig ps --nodes --rig zero`: design.lead (`claude-opus-5-5`), development.implementer (`gpt-5.6-luna`), review.qa (`claude-sonnet-5`), and main.lead. No model substitution. Discovery queue `qitem-20260928043532-bd4d2920` is claimed by design.lead. Builder and reviewer wait on approved direction/copy and implementation respectively.
- Dokploy native CLI token verified. Its `zero` project production environment contains **Compose**, not an application: `zero-landing` composeId `u2SP2b5035tm1yaHVNcH8`, domain `zero.headless.com`. Read-only `/api/compose.one` returned `sourceType=raw`, no repository/branch/GitHub ID, `autoDeploy=true`, `triggerType=push`, and compose image `zero-landing:14e9e2b`. Thus the autoDeploy flag does **not** prove Git auto-deploy. Current live `/` returned 200 and `/install` 302 to the raw GitHub installer on 2026-09-28. Release slice needs an explicit image-build/transport plan and rollback, not `dokploy app deploy` (wrong service type). [Dokploy Compose API](https://docs.dokploy.com/docs/api/compose) documents the Compose endpoint.
- [Repository maintenance procedure](../../docs/MAINTENANCE.md#deploying-the-site) independently confirms `production-server` at `34.66.84.21`, raw Compose, no git auto-deploy, server-side image build and scoped service recreate. Historical verified release in [landing-redesign-verification](../../docs/landing-redesign-verification.md). Prefer the native Dokploy Compose API for stored compose and use the documented GCP IAP transport for architecture-correct image build, after QA.
- Baseline on 2026-09-28: `node --test landing/test-site.mjs` passed and `bash landing/build.sh zero-landing-redesign-baseline` passed homepage, legal, CSS/JS, fonts/image, 404, and both install routes; the redirected installer parsed. This is pre-redesign only, not acceptance evidence for the new page. Read-only GCP IAP SSH confirmed the production container `zero-zerolanding-m7cxtx-zero-landing-1` is healthy, on `zero-landing:14e9e2b` (amd64 image `sha256:55c9a37e...`). Keep that tag for rollback; build new image on the amd64 server.

