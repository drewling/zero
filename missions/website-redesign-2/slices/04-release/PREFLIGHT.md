# Local isolated Docker/nginx preflight, not a release

**Checked 2026-09-29 05:59–06:02Z against exact QA source candidate** `3f8f1a4e19b2d0eb9cb773d5cacd8c28acfd232e`. This was run entirely in local Docker Desktop. No production Compose/API, deployment, push, installer execution, or release action occurred.

## Source and image

- Archived only `landing/` and `macapp/install-zero.sh` from the exact commit into the Jcode scratch area. Archived `landing/index.html` SHA-256 matched `git show 3f8f1a4:landing/index.html`: `9a55f555c49ac99bea6a26fc8eb2faaf227eae019b7373907e01e8454d0b5f07`.
- Ran `DOCKER_DEFAULT_PLATFORM=linux/amd64 bash landing/build.sh zero-landing:preflight-3f8f1a4` against that archived copy. Installer shell syntax passed. The image built successfully as `sha256:b09f3caab34836edf15546a28bc325e326e783d3a3f0883e47916da6a45f97f6`, `linux/amd64`, on the local aarch64 host through Docker Desktop emulation.
- The build script's temporary container passed homepage 200, `/install` 302, `/install.sh` 302, privacy/terms/CSS/JS/four fonts/two app images 200, unknown path 404, and the redirected `/install` returned a bash script that passed `bash -n`. It did **not** run the installer.

## Separate container-level confirmation

After waiting for nginx readiness on a new local amd64 container:

| Check | Observed |
| --- | --- |
| `/install` | 302 to `https://raw.githubusercontent.com/drewling/zero/master/macapp/install-zero.sh` |
| `/install.sh` | 302 to `https://github.com/drewling/zero/blob/master/macapp/install-zero.sh` |
| Served homepage | SHA-256 `9a55f555c49ac99bea6a26fc8eb2faaf227eae019b7373907e01e8454d0b5f07`, byte-identical to archived exact candidate |
| Robots, sitemap, llms, portrait app image | All 200 |
| Image health check | `healthy` after 35 seconds |
| Residual test containers | None; both temporary containers stopped by traps |

An immediate curl on the first verification container got an empty reply before nginx was ready. The readiness-gated retry reached 200 after two 0.5-second attempts and all checks above passed. This was a startup race in the extra test command, not a site defect. The production deployment and its host-specific network, proxy and cache path remain untested and require a separate owner-authorized release with backup, rollback and live browser verification.

Local full build log: `$JCODE_SCRATCH_DIR/zero-preflight-3f8f1a4-20260929T055941Z/build-output.txt` (SHA-256 `502dc00134b2163042e9cc97103b555435f5eecf7fd3430e090e36f0a689a02a`). Local route/health log: `route-output.txt` in the same directory (SHA-256 `23a510ce88d02adbdc691aac0cbb0311538a489d791c4d12e0b70a4b99e26214`). These logs are local artifacts, not committed deployment credentials.
