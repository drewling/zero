# Website redesign 2 progress

## 2026-09-29 05:13Z: provisional content choices, build and QA only

Advisor `advisor-lead@kernel` relayed that the owner is away overnight and asked that the team complete unblocked work. The advisor independently reviewed [the 608-word content and structure proposal](slices/02b-content-structure/proof/CONTENT-PROPOSAL.md) against `PRODUCT.md` and code, and gave a **provisional go-ahead for the rebuild and independent QA**, subject to owner veto in the morning. This is not direct final owner acceptance of the copy.

- **Q1:** Use option (a). Describe manual **Run zero now** and do not promise an automatic morning run. The shipped v1.7.0 app does not create its LaunchAgent from Settings. No app change in this website slice.
- **Q2:** Use the proposed headline, **“Only the mail that still needs you.”**
- **Q3:** Use **“Check it with your coffee. Then close it.”** The owner may change its register after reviewing the candidate.
- **Outline and copy:** Build the six-section, 608-word draft in visual Direction B, not the rejected 901-word feature inventory. Preserve the verified safety, data-flow, install and pricing disclosures, and the clean replacement of old landing code.

Builder may fold the proof comp into `landing/` under slice 02c, then hand an exact committed SHA to independent QA. QA must compare both content and visuals with the provisional proposal, exercise true desktop/mobile viewports, functionality and accessible fallback, and leave desktop/mobile shots for morning owner review. **Stop at a QA-passed build. No deployment, production release or push is authorized by this provisional go-ahead.** Release still requires a separate direct owner decision after seeing the candidate.

Source: advisor message to `main-lead@zero` at 05:13Z, handoff `qitem-20260929045726-da037ac8`, content proof commit `43fb9c7`. The earlier 390px phone proof used an iframe; final QA owns true viewport proof. The local Docker daemon remains unavailable and nginx redirect/image packaging claims must not be marked passed without an isolated runtime test.
