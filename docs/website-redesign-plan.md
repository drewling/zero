# zero website redesign plan

Date: 2026-09-28. Owner: `main-lead@zero`. Scope: `landing/` and the public `zero.headless.com` homepage, with privacy, terms, and the installer route preserved. This is a replacement visual world, not a reskin.

## Outcome

A visitor understands in one viewport that zero is a Mac menu-bar app that keeps Gmail conversations needing action and archives the rest, sees a real product view, and can confidently install. A visitor who is not ready can inspect the requirements, data path, reversibility, source, and installer. The site must look considered and singular rather than borrowing Linear's branding.

## Product and offer truth

The repository [README](../README.md) and [product description](../PRODUCT.md) are the claims ledger. zero runs on Apple Silicon with macOS 26+, needs Gmail and a TypeSafe Jev key, is free and open source, and the provider bills for usage. It sends thread text to Jev for sorting. Optional drafts go to the chosen provider and are sent only by a user click. Archive is reversible. The installer is not notarized and Google can show an unverified-app warning. Do not hide any of these costs or caveats to improve clicks. Do not invent adoption numbers, logos, endorsements, privacy promises, or customer quotes.

## Reference study, checked September 28, 2026

- [Linear](https://linear.app/): precise product-first framing and full-fidelity workflow demonstrations. Borrow the conviction and visual hierarchy, not the purple-black identity, product complexity, or fabricated interaction.
- [Raycast](https://www.raycast.com/): a Mac utility explained with a simple promise, product-as-proof, and a direct free download. Borrow the short path to action, not the feature sprawl or social proof that zero cannot substantiate.
- [Vercel](https://vercel.com/): terse category claim and focused entry actions. Its enterprise navigation and customer metrics do not fit this small utility.

These are live first-party sites, not an unverified listicle or a claim that any design style is proven to convert. Visual research and desktop/mobile captures are part of the first slice. The current page's source and [DESIGN.md](../landing/DESIGN.md) are anti-reference, while the real product image and documented behavior remain source material.

## Funnel decision

This is a product-install funnel, not an email-capture or upsell funnel. The audience hypothesis is a Mac Gmail user with accumulated actionable mail who wants a reversible sorting assistant. The path is problem recognition → mechanism and real app proof → trust/cost/requirements → install → first sweep. The homepage's Hook–Story–Offer must remain factual. Until analytics are available, diagnose clarity and usability rather than claim a conversion lift. No lead magnet, fake urgency, or extra commercial rung.

## Delivery sequence

1. **Discovery and direction**: inventory live and source truth, inspect references visually, use updated `/impeccable` replacement-world process, and produce a chosen art direction plus desktop/mobile mockups. Output a durable design brief and evidence. Design lead: Claude Opus 5.5 if available and verified.
2. **Message and journey**: apply `/funnels` to sharpen who, hook, proof and install path, then `/slopmonster` to remove generic prose without changing claims. Produce copy and evidence ledger for approval by mission lead before implementation.
3. **Build**: implement semantic responsive page, real imagery and restrained motion, preserve `/install`, `/install.sh`, privacy, terms, source links and all safety disclosures. Avoid unnecessary framework migration.
4. **Independent QA**: test desktop/mobile visuals, keyboard and reduced motion, copy/claims, links, responsiveness, build and installer routes. Repair defects and record screenshots and proof.
5. **Release**: determine the actual Dokploy application and branch/autodeploy configuration. Deploy only after verified checks, or observe the automatic deployment after integration. Check the live homepage and installer route, and document rollback. Never infer production from a local build.

## Team and boundaries

Keep `main.lead` as mission owner and integrator. Request a design/strategy seat on **Claude Opus 5.5** (the user's preference, not a blanket capability assertion), a development implementation seat, and an independent review/QA seat. Three additional seats across design, development, and review pods are proportionate for this production redesign. The design lead owns direction and mockups, the builder owns landing code, the reviewer owns acceptance compare. The mission owner owns final claim and production decision. Work in the shared repo with explicit file ownership and short handoffs; no competing edits to `landing/index.html`.

## Acceptance

A complete responsive homepage with verified factual copy and real app proof; no invented proof; clear install and caveats; visual compare to approved mockups on desktop/mobile; passing `node --test landing/test-site.mjs`, installer syntax, Docker smoke if available; no broken internal/external primary links; live deployment verified at `/` and `/install`. If Dokploy access or model availability is blocked, record the precise blocker instead of silently substituting or reporting deployment.
