# Progress — Website redesign 3: clear copy, better hero, polished sections

> Durable acceptance state for this mission. In-process steps belong in the
> working agent's todo tool. See the `mission-slice-sop` skill and the
> conventions SSOT (`docs/reference/sdlc-conventions.md` in the repo,
> `$OPENRIG_HOME/reference/sdlc-conventions.md` when installed).

## Acceptance

- [ ] Scope complete (all slices shaped)
- [ ] Implementation in progress
- [ ] QA / review pass
- [ ] Merge / ship

## 2026-09-29 20:55Z: slices 01 and 02 dispatched

Owner request relayed by advisor-lead (qitem-20260929203933-11379476). Slice 01 went to design-copywriter@zero (qitem-20260929205447-1a417f3a) and slice 02 to design-lead@zero (qitem-20260929205448-0fbfa1ce), in parallel. development-motion@zero was told to read its slice and wait for MOTION-SPEC. Next: gates A and B shown to the owner together once both slices hand back. No deploy without an owner go at slice 06.

## 2026-09-29 21:35Z: slice 01 handed back

Copy v3 ready for owner gate A: hero "Clean up your Gmail inbox on your Mac.", 549 visible words (ceiling 550, so the designer must recount actual chrome), 3/3 isolated fresh readers pass, banned-phrase lint 0 hits, six comparables, truth trace, design-lead fit review incorporated. See slices/01-copy-and-story/proof/COPY.md and HANDOFF.md. Slice 02 comps still in progress. Gates A and B go to the owner together.

## 2026-09-29 22:08Z: slice 02 handed back, gates A and B with the owner

Slice 02 done: 14 references (5 animated), three hero comps, one design per section, MOTION-SPEC, title-plate fix (script and visual check), 544 rendered words vs the 549 inventory (ceiling 550). Recommendation: hero A "menu-bar roll", C as the quieter fallback, B not recommended. Brief for the owner: OWNER-GATES-A-B.md, relayed by advisor-lead (Tayo has the live comps) and filed as human@kernel qitem-20260929220710-92821b38. **Build held until the owner answers.** development-motion continues sandbox-only. No deploy.

## 2026-09-29 22:38Z: owner answer, hero B approved, rest of page not approved

Tayo (via advisor-lead): hero B approved (zero as the visible actor, not the user dragging). Copy and sections are NOT approved and need much more consideration. Wants a stronger proposal with concrete before/after, not tweaks. Not urgent. Build stays held. design-lead and design-copywriter asked to rethink story order, each section object and every line, with two genuinely different outlines, extra comparables, and isolated fresh-reader tests of current versus proposed page. Slice 03 is not released.

## 2026-09-29 23:03Z: more owner feedback folded into the rethink

Tayo (via advisor-lead): still confusing and hard to read, not enough animation, heading font too hard to read, wants a holistic pass and a full-width layout. Suggests adversarial review, funnel thinking and /impeccable. Dispatched to design-lead and design-copywriter: 2 or 3 heading font options against the current one, full-width edge-to-edge layout tested from 320 to 2560, per-section stepped animation, /funnels and /impeccable passes recorded, isolated reader test of proposal vs baseline. review-qa is queued as the adversarial reviewer (sceptical stranger, then design critic) once the proposal exists. Build held. Slice 03 not released.

## 2026-09-30 01:00Z: owner chose page B (risk-first)

Tayo (via advisor-lead): page B over page A, hero B stays. Page A stays archived in the comps folder. design-lead, copywriter and motion tighten B only (impeccable critique items, heading font, full-width layout, per-section motion, the pending fix batch including the data and cost findability gap). review-qa runs the adversarial passes on the frozen B SHA. Truth rule: no promise of automatic daily runs. Build held, slice 03 not released, no deploy. Handback to advisor-lead: one runnable page B and a 3 line plain summary.

## 2026-09-30 02:30Z: tightened page B handed to the owner

Page B tightened and frozen (50bf121, follow-up 65463b8), review-qa pass 1 (df6632d, one Medium: hero Trash) and pass 2 (72f3424, no new findings), Chromium 148/0 and WebKit 144/0 (Playwright). Proposal: slices/02-references-and-comps/proof/comps/proposal/index.html, runnable page: comps/page-b/index.html, served at 127.0.0.1:8941 via acceptance/serve.py. Sent to advisor-lead for Tayo with a 3 line summary. Open owner decisions: drop the hero Trash, keep tightened B, typical monthly cost (product answer, nothing invented), installer and Claude Code presentation, scheduling line (recommend unsaid). Limits: real Safari 26 and devices unverified, clipboard stubbed, readers are AI models with mixed results, three fresh reads of the final privacy wording still running. Build, slice 03 and deploy held.
