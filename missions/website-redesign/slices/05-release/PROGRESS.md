# Progress — Dokploy release and live verification

## Acceptance

- [x] Implementation complete: confirmed raw one-service Dokploy Compose, built QA-approved `57deff2` image on amd64 production host, updated stored Compose through native API, and completed `/api/compose.deploy` with status `done`.
- [x] Tests passing: isolated image smoke passed; live homepage exactly matches candidate source; `/`, legal pages, styles/scripts, app and OG images, crawler files returned 200; installer redirects returned 302 and public `/install` parses with `bash -n`. Production container is healthy.
- [x] Review approved: independent QA slice 04 verdict PASS against `57deff2`; release proof registered as [proof/release-pass.md](proof/release-pass.md), covering all three SPEC proof items and rollback target `14e9e2b`.
