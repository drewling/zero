# Reader protocol and baseline provenance

Status: three matched baseline reads complete, 2026-09-29. After reads are waiting for the designer's stable A/B commit, final type and full-bleed layout. This is a proof-only redesign proposal. Hero B is owner-approved; sections and copy are not. No install, inbox access, deployment or landing edit is part of this test.

## Before sources

- Rejected comp: designer's frozen `../../../02-references-and-comps/proof/baseline-v3/`, commit `a196c47`, recorded source `2d6d725`. Its full-page images stack hero B and the standalone section comp, not a single implemented page. Both repeated navigation bars and draft labels are visible in the pictures. Do not mistake these capture artifacts for intended production content.
- Local snapshot: `before/hero-b/index.html`, `before/sections/index.html` and their assets. `before/inventory.json` records both source hashes and all authored visible text nodes. `before/PAGE-TEXT.txt` uses one navigation/header, excludes author-only draft labels and screen-reader-only descriptions, and includes illustration rows. It counts 527 words before the run-popover rework. It is a full visible-copy inventory, not extracted rendered innerText.
- Desktop long page: `before/page-full-1440.jpg`, exact copy of designer's 1440×4322 JPEG.
- Mobile long page: `before/page-full-390.jpg`, designer's 390-CSS-pixel viewport capture (585×8802 JPEG), resized to a 7000-pixel maximum dimension to fit image-input constraints. The unresized original remains in the designer's baseline. Detail crops accompany both widths, so long-page scaling does not remove access to the words.
- Live site, second documentary before: `../before/live-1440-{fold,full}.png`, `../before/live-390-{fold,full}.png`, `../before/copy.txt`. These are the advisor's captured production baseline. No claim that this is the current live HTML after capture. The rejected v3 comp, not the older live design, is the matched reader-test comparator.

## Isolation and test conditions

`reader-prompt.md` is fixed for the before/after test: eight questions on category, confusing words/objects, skipped/repeated material, missing information, install/leave reasons, actor, recovery/data and five clarity ratings. No suggestion that a newer proposal ought to win.

`run-isolated-reader.mjs` passes the complete copy and images inline as one user message. Each run has a new UUID, neutral scratch cwd, replacement plain system prompt, no project settings, no slash skills, no auto-memory, no MCP servers, no browser, no tools and no persisted session. Model requested explicitly: `claude-sonnet-5`. The wrapper CLI gets `</dev/null`; the child gets only the one generated stream-json message, then stdin closes. Inline images require that technical input stream, not an interactive chat. Raw JSONL, stderr, answer and metadata are retained. Metadata records exact prompt, source-image hashes, model usage, session IDs and turn count. Reject errors, substitutions, reused session IDs, tool calls or more than one turn.

`run-matched-reader.mjs before 1|2|3` uses identical ordered inputs: two long-page screenshots, six desktop crops, six mobile crops, and the full authored copy. Fresh after readers use `run-matched-reader.mjs after-a 1|2|3` and `after-b 1|2|3`. Each frozen `after-{a,b}/` contains `PAGE-TEXT.txt` and `reader-images.json`, an ordered list of relative image paths within that snapshot. Use two long views first (1440 then 390), then desktop crops in page order, then mobile crops in page order. Detail crops must make every section readable. The same fixed prompt, model and isolation conditions apply. A changed section count need not force duplicated after screenshots to preserve an artificial crop count. Report that input difference explicitly.

Do not run on moving designer sources. Record the stable commit and hashes of both source pages, copied assets, full copy and images before launching. Preserve the original screenshots alongside any API-size derivatives. The wrapper rejects an invalid phase/reader, absolute or parent-traversing manifest paths, missing inputs and output prefixes with existing evidence. A repeat uses a new explicit output prefix and retains the previous attempt, not an overwritten run.

## Selection and complete-workflow checks

Evaluate each outline independently before comparing it. Three fresh sessions per outline do not imply that a given session has seen both pages or directly preferred one. The recommendation is the team's qualitative comparison of independently observed category, actor, recovery, tradeoff comprehension and section usefulness, not a fictional paired preference or a significance claim. Document contradictory observations and all product-based reasons to decline. If the evidence is tied, report the tie and select on the declared shorter-story requirement without claiming a reader winner.

Baseline self-reports are job 4/4/4, story 3/3/3, visuals 2/2/2, tradeoff finding 4/3/4, decision 2/2/3. Targets declared before after reads are in `frameworks-and-section-jobs.md`. Retain raw answers and explain changes with specific responses, not only average ratings. Improvements caused solely by removing repeated comp chrome or proof watermarks are input-condition changes, not proof that the new story works better.

Before handback, check the full chosen page through public comp routes, all six viewport widths, final authored text including alternate actor states, correct install-warning anchors, exact command and copy fallback, no-JS and reduced-motion completeness, source-faithful Rules/Undo controls, disclosure coverage, and proof-only packaging. Record each check and its observable result in `acceptance-checklist.md`. Still screenshots test content/layout, not animation quality or classification accuracy. Independent QA receives exact frozen proposal and comp paths, and its findings and fix/recheck responses are retained.

The earlier `readers/before/reader-1.*` is a retained pilot with crops but without the complete stitched page images. It does not count as one of the three matched baseline readers. Two launch attempts failed before calling the model because a hero-crop path contained an extra `shots/`; corrected in the repeatable wrapper, with no model result discarded.

## Limits

Three isolated model reads are diagnostic qualitative evidence, not human usability participants, install conversion data, security certification or proof of classification accuracy. Numeric ratings are self-reports from three samples, not statistically significant measures. Preserve product reasons to decline even when presentation improves. Do not copy factual mistakes from readers, including conflating non-notarized with unsigned, or asserting that all email body data is excluded from every provider path.
