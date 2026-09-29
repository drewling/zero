# Reader protocol and baseline provenance

Status: baseline evaluation in progress, 2026-09-29. This is a proof-only redesign proposal. Hero B is owner-approved; sections and copy are not. No install, inbox access, deployment or landing edit is part of this test.

## Before sources

- Rejected comp: designer's frozen `../../../02-references-and-comps/proof/baseline-v3/`, commit `a196c47`, recorded source `2d6d725`. Its full-page images stack hero B and the standalone section comp, not a single implemented page. Both repeated navigation bars and draft labels are visible in the pictures. Do not mistake these capture artifacts for intended production content.
- Local snapshot: `before/hero-b/index.html`, `before/sections/index.html` and their assets. `before/inventory.json` records both source hashes and all authored visible text nodes. `before/PAGE-TEXT.txt` uses one navigation/header, excludes author-only draft labels and screen-reader-only descriptions, and includes illustration rows. It counts 527 words before the run-popover rework. It is a full visible-copy inventory, not extracted rendered innerText.
- Desktop long page: `before/page-full-1440.jpg`, exact copy of designer's 1440×4322 JPEG.
- Mobile long page: `before/page-full-390.jpg`, designer's 390-CSS-pixel viewport capture (585×8802 JPEG), resized to a 7000-pixel maximum dimension to fit image-input constraints. The unresized original remains in the designer's baseline. Detail crops accompany both widths, so long-page scaling does not remove access to the words.
- Live site, second documentary before: `../before/live-1440-{fold,full}.png`, `../before/live-390-{fold,full}.png`, `../before/copy.txt`. These are the advisor's captured production baseline. No claim that this is the current live HTML after capture. The rejected v3 comp, not the older live design, is the matched reader-test comparator.

## Isolation and test conditions

`reader-prompt.md` is fixed for the before/after test: eight questions on category, confusing words/objects, skipped/repeated material, missing information, install/leave reasons, actor, recovery/data and five clarity ratings. No suggestion that a newer proposal ought to win.

`run-isolated-reader.mjs` passes the complete copy and images inline as one user message. Each run has a new UUID, neutral scratch cwd, replacement plain system prompt, no project settings, no slash skills, no auto-memory, no MCP servers, no browser, no tools and no persisted session. Model requested explicitly: `claude-sonnet-5`. The wrapper CLI gets `</dev/null`; the child gets only the one generated stream-json message, then stdin closes. Inline images require that technical input stream, not an interactive chat. Raw JSONL, stderr, answer and metadata are retained. Metadata records exact prompt, source-image hashes, model usage, session IDs and turn count. Reject errors, substitutions, reused session IDs, tool calls or more than one turn.

`run-matched-reader.mjs before 1|2|3` uses identical ordered inputs: two long-page screenshots, six desktop crops, six mobile crops, and the full authored copy. Fresh after readers use the same prompt, model/isolation conditions, two long views and ordered detail crops sufficient to read all sections, with the complete new visible copy. A changed section count need not force duplicated after screenshots to preserve an artificial crop count. Report that input difference explicitly.

The earlier `readers/before/reader-1.*` is a retained pilot with crops but without the complete stitched page images. It does not count as one of the three matched baseline readers. Two launch attempts failed before calling the model because a hero-crop path contained an extra `shots/`; corrected in the repeatable wrapper, with no model result discarded.

## Limits

Three isolated model reads are diagnostic qualitative evidence, not human usability participants, install conversion data, security certification or proof of classification accuracy. Numeric ratings are self-reports from three samples, not statistically significant measures. Preserve product reasons to decline even when presentation improves. Do not copy factual mistakes from readers, including conflating non-notarized with unsigned, or asserting that all email body data is excluded from every provider path.
