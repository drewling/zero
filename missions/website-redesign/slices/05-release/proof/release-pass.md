---
slice: OPR.99.0.1.5
candidate_sha: 57deff2a49eb56791c5634afe795a933c11ddc2a
artifact_type: qa
verdict: PASS
money_evidence: QA-approved landing page is live at zero.headless.com,
  byte-identical to 57deff2, with healthy container and verified install path
evidences:
  - "1"
  - "2"
  - "3"
self_check: I independently read the Dokploy stored and generated Compose,
  inspected the healthy container and retained rollback image, fetched the live
  homepage and compared its bytes to candidate source, checked every listed live
  route, and parsed the redirected installer with bash -n.
---

# Release evidence, 2026-09-28

## 1. Deployment configuration, not assumption

- Dokploy project `zero`, production environment, Compose `zero-landing` (`composeId u2SP2b5035tm1yaHVNcH8`, generated app `zero-zerolanding-m7cxtx`), domain `zero.headless.com`. Authenticated `GET /api/compose.one` confirmed `sourceType=raw`, not a Git branch deployment; its `autoDeploy=true` flag is not Git wiring. The generated Compose has exactly one service, `zero-landing`, and pre-release image `zero-landing:14e9e2b`. The pre-release container was healthy.
- Previous stored Compose saved at `$JCODE_SCRATCH_DIR/zero-release-20260928T0603Z/stored-compose-before.yml`. Server generated Compose was backed up under `/root/zero-landing-backup-20260928T0604Z/docker-compose.yml` before the swap. Previous amd64 image remains on the server: `zero-landing:14e9e2b`, image ID `sha256:55c9a37e0c646213be87f4441d7e50e79188128432952f223c657291fc5b962a`.
- Source and routing cross-check: `docs/MAINTENANCE.md#deploying-the-site`, `landing/nginx.conf`, GCP `production-server` in `drewl-366215/us-central1-a`, Dokploy Compose API documentation at <https://docs.dokploy.com/docs/api/compose>. No host restart or unrelated service modification.

## 2. Deployment result and real user path

- Candidate is the independently QA-approved landing-byte SHA `57deff2a49eb56791c5634afe795a933c11ddc2a`; later commits only changed proof/docs, `git diff 57deff2 HEAD -- landing` was empty at build. Source archive SHA-256 `84f7770e67d35825cdafe97510d80512ad583b818ae4cfecc99e792383bdff05` was transferred over GCP IAP. Image built on amd64 `production-server`, not the arm64 laptop: `zero-landing:57deff2` / `sha256:fa98f6ddc47c7f65cf04ba5657318bc03adcc746ae3d220f17257c43bdf3287c`.
- Prior to release, an isolated candidate container passed homepage marker, privacy, terms, CSS, JS, app screenshot and OG asset 200 checks, plus both installer redirects. Authenticated Dokploy `/api/compose.update` changed only `composeFile` to the new image tag. `/api/compose.deploy` returned `success=true, Deployment queued` for this composeId. `/api/compose.one` subsequently reported `composeStatus=done`; generated Compose and stored record both point at `zero-landing:57deff2`. Container `01a9de477770` was `Up (healthy)` on that image at 06:34Z.
- Live HTTPS requests to `https://zero.headless.com` at 06:33Z: `/`, `/privacy.html`, `/terms.html`, `/site.css`, `/site.js`, `/assets/zero-panel.png`, `/og.png`, `/robots.txt`, `/sitemap.xml`, `/llms.txt` all returned **200**. Live homepage bytes compared exactly (`cmp`) with local `landing/index.html` from the QA candidate: SHA-256 `efefae2f0a16b74b43641737e3fea75ec6fcb84510fae4c21479ea409af2c41d`; contains distinct new hero `Keep the mail that needs you.`. `/install` returned **302** to the raw `macapp/install-zero.sh` on `master`, and `/install.sh` returned **302** to its GitHub-readable blob. Following the public `/install` redirect into `bash -n` passed. The installer was parsed, not executed.

## 3. Rollback and residue

Rollback target is the retained image `zero-landing:14e9e2b`. To revert, update **stored** Dokploy Compose via authenticated `POST https://deploy.drewl.com/api/compose.update` with `{ "composeId": "u2SP2b5035tm1yaHVNcH8", "composeFile": "services: {zero-landing: {image: 'zero-landing:14e9e2b', restart: unless-stopped, environment: {HOST: '0.0.0.0', PORT: '80'}}}" }`, then `POST /api/compose.deploy` with the same `composeId`. Verify `composeStatus=done`, generated Compose tag, healthy container, and live routes. The pre-change Compose backup above is the exact restore payload. Use `x-api-key` from authenticated Dokploy environment, not a token pasted into the runbook. If Dokploy API fails, restore the server-side generated Compose backup and `docker compose up -d --no-deps zero-landing` in `/etc/dokploy/compose/zero-zerolanding-m7cxtx/code`, then repair stored Compose so future redeploys do not revert it.

Known residue: QA tested chromium and webkit at 320/390/1440 but could not run native-device/Aside emulation in this environment. The installer redirects to `master` and remains a separate mutable source of truth. The Docker build on the crowded host was unusually slow, though it completed and the final container is healthy. No Git push was necessary or performed for this raw Compose site deployment.
