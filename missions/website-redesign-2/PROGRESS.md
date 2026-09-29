# Website redesign 2 progress

## 2026-09-29 05:13Z: provisional content choices, build and QA only

Advisor `advisor-lead@kernel` relayed that the owner is away overnight and asked that the team complete unblocked work. The advisor independently reviewed [the 608-word content and structure proposal](slices/02b-content-structure/proof/CONTENT-PROPOSAL.md) against `PRODUCT.md` and code, and gave a **provisional go-ahead for the rebuild and independent QA**, subject to owner veto in the morning. This is not direct final owner acceptance of the copy.

- **Q1:** Use option (a). Describe manual **Run zero now** and do not promise an automatic morning run. The shipped v1.7.0 app does not create its LaunchAgent from Settings. No app change in this website slice.
- **Q2:** Use the proposed headline, **“Only the mail that still needs you.”**
- **Q3:** Use **“Check it with your coffee. Then close it.”** The owner may change its register after reviewing the candidate.
- **Outline and copy:** Build the six-section, 608-word draft in visual Direction B, not the rejected 901-word feature inventory. Preserve the verified safety, data-flow, install and pricing disclosures, and the clean replacement of old landing code.

Builder may fold the proof comp into `landing/` under slice 02c, then hand an exact committed SHA to independent QA. QA must compare both content and visuals with the provisional proposal, exercise true desktop/mobile viewports, functionality and accessible fallback, and leave desktop/mobile shots for morning owner review. **Stop at a QA-passed build. No deployment, production release or push is authorized by this provisional go-ahead.** Release still requires a separate direct owner decision after seeing the candidate.

Source: advisor message to `main-lead@zero` at 05:13Z, handoff `qitem-20260929045726-da037ac8`, content proof commit `43fb9c7`. The earlier 390px phone proof used an iframe; final QA owns true viewport proof. The local Docker daemon remains unavailable and nginx redirect/image packaging claims must not be marked passed without an isolated runtime test.

## 2026-09-29 05:54Z: candidate built and scoped independent QA passed

- **Exact candidate:** `3f8f1a4e19b2d0eb9cb773d5cacd8c28acfd232e` (content source `1f8e641`; builder proof at `3f8f1a4`). This changes `landing/` in the repo only, not production. The original B design is retained, with the 608-word visitor-first story, two-question differentiator, single-home safety and cost facts, and FAQ removed.
- **Independent QA:** [requirement-mapped verdict](slices/03-independent-qa/proof/PROOF.md), commit `f8a5e35`, is PASS for the authorized visual, copy, responsive-browser and functional scope on that exact SHA. Chromium and WebKit true 1440/390/320 captures had no horizontal overflow or geometry offenders. Reduced-motion and no-JS fallbacks, folder settlement, four install steps, exact command, keyboard Copy success/denial focus paths, and static assets were checked. No landing source was changed by QA.
- **Review the rendered page:** [Chromium desktop 1440](slices/03-independent-qa/proof/shots/chromium-1440.png), [mobile 390](slices/03-independent-qa/proof/shots/chromium-390.png), [narrow mobile 320](slices/03-independent-qa/proof/shots/chromium-320.png). Matching WebKit captures and machine-readable browser evidence sit beside them in `slices/03-independent-qa/proof/`.
- **Honest boundaries:** Docker image and nginx `/install` and `/install.sh` redirects could not be smoke-tested locally because the daemon is unavailable. Clipboard success and denial used an instrumented adapter in QA; the builder separately checked the real Aside success path. No VoiceOver/axe or formal performance audit was run. These are not claimed as passed.

**Next owner decision:** review the copy and visual captures, keep or veto the provisional Q1–Q3 wording, then explicitly decide whether to authorize a production release. Until then this stops at a QA-passed source candidate. No deployment, push or production change under the overnight build-and-QA permission.

## 2026-09-29 06:02Z: local packaging and redirect gate closed

Docker Desktop became available after independent QA. The exact `3f8f1a4` source was archived into an isolated local build, matched by homepage SHA-256, built and smoke-tested as `linux/amd64`. The container was healthy, served byte-identical homepage, static/legal assets, `/install` 302 to the raw shell script and `/install.sh` 302 to the source view, and followed `/install` to a parsable shell script. Details and source/route hashes: [local preflight](slices/04-release/PREFLIGHT.md). No installer execution, push, production host action, Compose update, deploy or release. The earlier QA limitation was accurate at the time and is now closed **locally**, not on production.
