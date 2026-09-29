# Proof: slice 01, research and direction

Start with `proof/DESIGN-BRIEF.md`. It is the owner-facing summary and the decision request.

| Acceptance item | Evidence | How it was checked |
|---|---|---|
| Ten inspected URLs with dated evidence and distinct lessons | `proof/references.md`; `proof/refs/<key>-1.jpg` and `-2.jpg` (20 images) | Aside sessions `154401a085` (Linear, Stripe, Superhuman, HEY, Granola) and `3516485kda` (Raycast, Things, Teenage Engineering, Vercel, Arc, Tailscale, Mercury), 2026-09-29 UTC, at a 1440×900 CSS viewport. I viewed every capture. Vercel and Arc were dropped, and the atlas says why. |
| Live page audit grounded in screenshots and feedback | `proof/DESIGN-BRIEF.md` §1; `proof/evidence/live-sort.jpg` and `live-rail.jpg` | Two live zero.headless.com frames captured by Aside (02:42 UTC on 2026-09-29), viewed again for this brief. The hero and warning claims were checked against the `landing/index.html` and `site.css` source (`.flap-board`, `sr-only` h1, `.warning` in `.install-band`). There is no committed hero frame. Plus the owner's "trash" rejection. |
| Distinct replacement comps at desktop and mobile, with a static state | `proof/comps/a-first-light.html`, `b-one-bit.html`, `c-native.html` (add `?static`) and `phones.html?<comp>`; captures in `proof/shots/` (17 jpgs) | Aside task `745854eqrl` captured the top, sort and install sections of each comp at 1440, plus `?static`, A at t=0 and three 390 px iframes per comp. `scrollWidth` was 390 in every iframe. I reviewed every shot visually (montaged at 03:19Z and 03:23Z), and an earlier pass (`4188159rpo`) drove the fixes. A later sentence diff against `landing/index.html` restored two abridged install-step phrases in the HTML, so the install shots predate that text-only fix. |
| Copy fidelity | DESIGN-BRIEF §3 | A sentence-level diff of the comp text against the landing text lists every new or reworded line |
| Concept derivation (impeccable concept-seed) | `proof/evidence/concept-derivation.md` | Product truth was checked against `landing/index.html`. The Jev line was corrected to the landing wording. |
| Keep/replace/remove inventory | `proof/replacement-inventory.md` | Built from `landing/` at `69f15d2` (file sizes, the `site.js` function list, asset references, nginx routes and tests). It sets exit checks for slice 02. |
| Owner-facing recommendation and choice via durable queue | DESIGN-BRIEF §2 and §4; queue handoff to main-lead@zero | Recommends A and asks the owner to choose A, B or C plus a copy latitude answer. |
| Scope | `git show --stat` on the commit | Only this slice directory changed. `landing/` was not touched, and there was no build, QA or deploy. |

## Contrast (comp A, WCAG formula)

| Text on background | Ratio |
|---|---|
| ink `#18212d` on shade `#e6eaee` | 13.4 |
| ink-2 `#465264` on shade | 6.6 |
| archived `#5a6679` on shade | 4.8 |
| sun `#8a5a00` on light `#fbe7b3` | 4.9 |

All four pass AA for body text. B is black on white, where the only risk is the dither behind text: every text block sits on a solid white panel. C uses Apple-style greys, which slice 02 must check when building.

## Limits

- Mobile evidence comes from a 390 px iframe, not device emulation, because Aside cannot set a viewport. There was no touch or DPR test.
- The metadata JSON for batch A was lost. The screenshots survive and are the evidence.
- Comps are prototypes for choosing a direction and are not production code. Fonts in `proof/comps/fonts/` are OFL and ship with their licences. `proof/comps/assets` is a symlink to `landing/assets` so the comps use the real panel and Geist files.
- Before you install, the FAQ, privacy and terms were not comped. The inventory keeps their content.
