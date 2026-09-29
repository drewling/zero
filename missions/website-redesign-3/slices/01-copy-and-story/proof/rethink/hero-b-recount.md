# Hero B final actor recount

2026-09-29 22:54Z, read-only source inventory. The revised hero source hash is `038f774c974127352b4103fcbd5c4d3d054f5b4b9b48db2bdcae0591282b8e09`.

- Frozen pre-actor B: 99 hero words + 428 rejected-section words = **527**.
- Revised B: 104 hero words + 428 rejected-section words = **532**, **18 below the 550 ceiling**.
- Delta: extra popover `zero` mark (1), `Run zero now` (3), `Working…` (1). Idle and busy labels count together even though they alternate.
- Count four ages, both visible brand marks, Inbox, dated folder, Trash, all fictional sender/subject rows and both captions. One navigation/header only, no clock, no author-only DRAFT flags or screen-reader-only descriptions. Decorative aria-hidden text still counts if visibly readable.
- Earlier **531** was provisional and omitted the added brand mark. It is corrected, not preserved as an accepted final total.

This is a final B-plus-rejected-v3 recount, not the new whole-page recommendation's count. New copy and all new window text require a separate recount against the actual recommended comp.

Reproduce: `python3 ../extract-comp-inventory.py ../../../02-references-and-comps/proof/comps/hero-b/index.html ../../../02-references-and-comps/proof/comps/sections/index.html`, then count joined textNodes with `/[\p{L}\p{N}]+(?:[’'.-][\p{L}\p{N}]+)*/gu`.
