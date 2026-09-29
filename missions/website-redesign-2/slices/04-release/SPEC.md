---
id: OPR.99.0.3.4
slice: 04-release
mission: website-redesign-2
status: gated
depends_on: [OPR.99.0.3.3]
---
# Slice 04: scoped release and live visual check

Mission lead obtains explicit owner authorization, retains rollback image and Compose, builds and smokes candidate, deploys only `zero-landing`, checks health and routes, and browser-verifies live visitor appearance and interactions. Roll back on regression.
