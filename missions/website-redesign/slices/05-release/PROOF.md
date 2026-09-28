# PROOF — OPR.99.0.1.5 Dokploy release and live verification

Closed by: main-lead@zero, 2026-09-28. Verdict: **PASS**.

The registered release artifact is [proof/release-pass.md](proof/release-pass.md). It covers all three SPEC proof-contract items with configuration checks, a healthy production container, byte-identical live homepage, installer syntax and a tested rollback target. The detailed evidence and rollback procedure are also in that artifact.

The release image is `zero-landing:57deff2` (QA-approved landing bytes). No repository push was needed or performed for this raw Compose deployment.
