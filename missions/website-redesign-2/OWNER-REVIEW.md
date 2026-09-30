# Zero Direction B: owner review

**Candidate:** `3f8f1a4e19b2d0eb9cb773d5cacd8c28acfd232e` · **Independent QA:** scoped PASS at `f8a5e35` · **Production:** unchanged. This is a provisionally approved build and QA result, not an owner-approved release.

The new page cuts visible copy from **901 to 608 words** and follows a visitor's decision: the one job across Gmail accounts, why model judgment beats named-sender filters, what daily use feels like, how archiving is reversed, what it needs/sends/costs, then installation. It drops the repeated FAQ and the old generic rules table. The one-bit B system replaces the rejected departure-board/Canvas source rather than layering over it.

## Desktop, Chromium 1440×900

![Full-page desktop screenshot](slices/03-independent-qa/proof/shots/chromium-1440.png)

## Mobile, Chromium 390×844

![Full-page mobile screenshot](slices/03-independent-qa/proof/shots/chromium-390.png)

## Narrow mobile, Chromium 320×700

![Full-page narrow mobile screenshot](slices/03-independent-qa/proof/shots/chromium-320.png)

The independent [QA proof](slices/03-independent-qa/proof/PROOF.md) includes matching WebKit captures at all three true viewports and the requirement-by-requirement browser checks. No horizontal overflow or geometry offenders were found. Reduced-motion, no-JS, keyboard Copy focus on success and denial, four install steps, and asset routes passed within the stated scope.

**Local Docker/nginx preflight now passed:** After QA, Docker Desktop came up. An isolated archive of the exact candidate built a `linux/amd64` image locally; the container was healthy, served homepage bytes identical to the reviewed source, returned `/install` and `/install.sh` 302 to the intended installer targets, served static/legal assets, and returned a parsable shell script when following `/install`. Preflight evidence. No production action occurred.

**Remaining limits:** The local result is not a production deploy or a check of the live host/proxy. QA used an instrumented clipboard adapter for success and denial, with a separate real browser success path in builder proof. VoiceOver/axe and formal performance scores were not measured. No claim of those checks passing is made.

**Your decision:** Keep or veto the provisional choices: (1) manual **Run zero now**, no automatic schedule promise until the app truly installs one; (2) “Only the mail that still needs you.”; (3) “Check it with your coffee. Then close it.” Then explicitly authorize or decline a production release. The isolated Docker/nginx preflight is done; a release would still require a fresh host check, backup and rollback readiness, and a live browser check. **Nothing has been deployed from this redesign.**

[Full content proposal](slices/02b-content-structure/proof/CONTENT-PROPOSAL.md) · [Mission progress](PROGRESS.md)
