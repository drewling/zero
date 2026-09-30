# Matched after-reader findings and selection

Observed 2026-09-30 00:37–00:38Z. Both outline inputs are frozen from designer commit `cdfee91`, copy `496d985`. Three fresh independent one-turn sessions per outline used the same prompt/model/isolation as the baseline. All six answers, raw JSONL and input/session metadata remain under `readers/after-a/` and `readers/after-b/`. Original images and readable derivatives remain under `after-a/` and `after-b/`.

**Selection update01:12Z:** owner chose risk-first B at00:58Z. The original A recommendation below is retained as the historical pre-decision judgment, not a current build instruction. A is archived. Tightened B copy at `SELECTED-B-COPY.md` needs a new freeze and three fresh reads, which cannot inherit these original results.

## Scores: mixed results, not an overall win

| Input | Reader | Job | Story | Visuals | Finding safety/data/requirements/cost | Decide |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 1 | 4 | 3 | 2 | 4 | 2 |
| Baseline | 2 | 4 | 3 | 2 | 3 | 2 |
| Baseline | 3 | 4 | 3 | 2 | 4 | 3 |
| A | 1 | 4 | 4 | 3 | 3 | 2 |
| A | 2 | 4 | 3 | 3 | 4 | 3 |
| A | 3 | 4 | 3 | 2 | 3 | 2 |
| B | 1 | 4 | 3 | 3 | 3 | 2 |
| B | 2 | 4 | 3 | 3 | 3 | 2 |
| B | 3 | 4 | 3 | 3 | 3 | 3 |

Job clarity and readiness to decide are unchanged. Visual usefulness improves descriptively: A scores 3/3/2 and B 3/3/3 against baseline 2/2/2. Only one A reader rates story higher. Finding tradeoffs does not improve: baseline 4/3/4, A3/4/3 and B3/3/3. No statistical inference, direct paired preference, human-conversion result or general success claim follows from these small independent model reads.

## What changed in comprehension

- **The app is the actor after a manual trigger:** all six explicitly identify an AI/app run begun from the menu bar, not the visitor dragging mail. A1 cites “Start a run from zero's menu bar” and the Run/Working states; B1 explicitly says “It is not manual dragging.” All six infer or question manual-only operation. Source contradicts that inference: `lib/keeper_server.py:1890–1897` updates an already-installed launch agent, while `bin/zero:169–229` installs/loads it. Settings → Daily routine edits its time and days (`PanelView.swift:1394–1428`). This is conditional scheduling, not an automatic install-default promise. Baseline already inferred a manual trigger, so trigger comprehension is firmer evidence, not a new category breakthrough.
- **Recovery is readable:** all six name zero's Undo tab, individual put-back and Restore all for a day's batch. A1 cites the dated batch and icon; B2 names the exact put-back tooltip. Baseline prose already communicated recovery, but its greeked object did not. B2 still reads 8 items/5 visible rows as a mismatch: the existing scrollbar is too easy to miss for that reader.
- **Rules earns a little more than filler in B:** B3 calls Rules and Undo “concrete and helpful,” unlike the rejected decorative Rules text card. The extra editor does not improve story or decision scores enough to justify preferring a longer outline on this evidence.
- **The ledger is still hard work:** all six ask for actual pricing. All six flag the distinction between no zero server and TypeSafe receiving email content/metadata as potentially evasive or easy to conflate. B3 calls Before you install the strongest section while still wanting clearer vendor boundaries. The factual data fields are recognized, but grouping and wording do not yet close comprehension.

## Recommendation before independent QA

**Choose A's recovery-first four-block story as the working recommendation, not a reader-voted winner.** It removes the separate Stays/Archived demonstration and separate Rules chapter, is 70 words shorter (474 vs 544), and has no demonstrated story/decision disadvantage against B. B's slightly stronger visual scores are real counterevidence and are retained. Keep B as the tested risk-first rival, with its source-faithful Settings view visible in the proposal.

A needs one coordinated post-reader/QA batch before an owner-ready recommendation:
1. Make the outbound third-party data recipient unmistakable without removing any disclosure.
2. Consider a concrete, dated provider unit price, with no invented per-inbox/month estimate. TypeSafe docs were re-fetched at 00:39Z: Jev 1.13 is $0.042 per million input tokens, outputs free, and `jev-latest` points to it. Product code `lib/jev.py:34` uses `jev-latest`. This is a versioned current rate, not a fixed lifetime price. Source: https://docs.typesafe.ai/models.
3. Clarify connected-Gmail viewing and conditional scheduled runs. The launch agent must be installed and loaded, with working connected accounts and inference configuration; changing time/days alone does not install it. Record this as an owner-visible story correction, not an approved new hero promise. [Exact source conditions and line audit](schedule-and-price-evidence.md).
4. Fix the known actual prose measure, the ledger hole and illustration partial-view cue in the designer's single batch. Preserve the entire source policy; its hard line break may become wrapping whitespace without changing words.
5. Verify command copy feedback, denial/unavailable recovery and semantic/status behavior. The current handler has a silent catch, not proven accessible recovery.

## Product reasons to decline, not copy defects

All six retain meaningful objections: third-party email data, separate usage billing, non-notarized app, Google unverified-app warning, development-tool installer footprint, optional drafting's additional data recipient. These remain candid. Requests for accuracy rates, zero retention, free tier, uninstall guarantees, unlimited restore history or tiny footprint are not permission to invent those claims.

## Reader errors and input confounds

- Three readers (A2 and B2/B3) complain about visible draft flags. B1 objects to disclosures/agency, not watermark. Flags were retained for parity with the before comp, are excluded from authored visitor counts, and are not intended production content. Their overlap nevertheless contaminated visual confidence. Do not credit later flag removal as a story win.
- A1 says two identical Terminal commands appear; the authored page has one. Full-page images plus crops show the same section more than once. A3 similarly treats repeated views of the hero as repeated page content. Do not remove a nonexistent duplicate.
- Several readers infer that no zero server receives email means the full body cannot reach any provider. That inference is not justified by that sentence. Preserve the distinct complete sorting and optional-draft data lists, and clarify recipient boundaries.
- Several readers call dependency additions “silent” or all mandatory. The page says “may add,” with Claude conditional on no supported tool. Verify the installer source before adopting stronger wording.
- A3 interprets “check your first few runs” as an Undo retention limit; it is a model-review caution, not a stated recovery cutoff.
- B2 misses a real scrollbar. This is evidence about salience, not evidence that the window has no scrollbar.
- The model inputs contain stills and copy, not live playback. They cannot validate motion agency or temporal proof quality. A has 10 ordered images, B12, baseline14 because section counts differ. Desktop/mobile long views precede all section crops; complete copy accompanies each. All use the same proof-label condition.

The six reads establish narrower improvements and continuing weaknesses. They do **not** close the whole-page feedback loop. Independent QA, fair fixes and observed rechecks are still required.
