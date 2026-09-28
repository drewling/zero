---
mission: OPR.99.0.1
name: zero website redesign
created: 2026-09-28
---

# Notes — zero website redesign

Context and observations that help the mission but do not change its
`SPEC.md` contract or `PROGRESS.md` acceptance checklist belong here.

## Notes

- 2026-09-28: Plan and five slices committed as `d49b160`. `/impeccable` updated globally via skills CLI at 04:30Z; its lock hash is `01fe78e7bc253016bfc30a3d12036bbf90f1c1bc`.
- Seats seen via `rig ps --nodes --rig zero`: design.lead (`claude-opus-5-5`), development.implementer (`gpt-5.6-luna`), review.qa (`claude-sonnet-5`), and main.lead. Model values are OpenRig declarations until each seat confirms active runtime. Discovery queue `qitem-20260928043532-bd4d2920` is assigned to design.lead. Builder waits on direction and copy.
- Dokploy native CLI token verified. Its `zero` project production environment contains **Compose**, not an application: `zero-landing` composeId `u2SP2b5035tm1yaHVNcH8`, domain `zero.headless.com`. Read-only `/api/compose.one` returned `sourceType=raw`, no repository/branch/GitHub ID, `autoDeploy=true`, `triggerType=push`, and compose image `zero-landing:14e9e2b`. Thus the autoDeploy flag does **not** prove Git auto-deploy. Current live `/` returned 200 and `/install` 302 to the raw GitHub installer on 2026-09-28. Release slice needs an explicit image-build/transport plan and rollback, not `dokploy app deploy` (wrong service type). [Dokploy Compose API](https://docs.dokploy.com/docs/api/compose) documents the Compose endpoint.
- Legacy `landing/deploy.sh` describes GCP SSH/docker route. Do not run until the actual image tag/build/registry path is verified against Dokploy production. Do not output auth tokens or environment content.

