# Tightened B: fresh matched reader results

**Test object:** designer-declared `50bf1213e06975ba8897400ef57ac8f1c2e07cfb`, frozen at01:46Z, tested01:47–01:48Z on30Sep2026. This is diagnostic model-reader evidence, not human usability testing, conversion data, owner approval or a statistical winner.

## Inputs and isolation

The unchanged [whole-page prompt](reader-prompt.md) and the same requested model `claude-sonnet-5` were used in three new one-turn sessions. Each ran from a neutral scratch directory with no tools, MCP, browser, project settings or persisted session. Raw outputs and exact input/session/model metadata are retained:

| Reader | Answer | Provenance |
|---|---|---|
| 1 | [Verbatim answer](readers/after-b-tightened/matched-1.answer.md) | [Metadata](readers/after-b-tightened/matched-1.metadata.json), [raw JSONL](readers/after-b-tightened/matched-1.jsonl) |
| 2 | [Verbatim answer](readers/after-b-tightened/matched-2.answer.md) | [Metadata](readers/after-b-tightened/matched-2.metadata.json), [raw JSONL](readers/after-b-tightened/matched-2.jsonl) |
| 3 | [Verbatim answer](readers/after-b-tightened/matched-3.answer.md) | [Metadata](readers/after-b-tightened/matched-3.metadata.json), [raw JSONL](readers/after-b-tightened/matched-3.jsonl) |

[Immutable source/capture hashes and runtime count](after-b-tightened/freeze.json), [reader image provenance](after-b-tightened/image-provenance.json), [complete authored words](after-b-tightened/PAGE-TEXT.txt), [desktop](after-b-tightened/shots/full-1440.jpg), [mobile](after-b-tightened/shots/full-390.jpg). Every served HTML/shared kit asset was checked against Git. The authored549 words include both observed clipboard statuses, complete Rules text, hidden mobile subjects and all hero states. No reader saw a later copy revision.

## Matched observations, not an improvement claim

Scores are job clarity / story / visuals / finding safety-data-requirements-cost / readiness. Comparators retain the original baseline and original B from [earlier findings](after-findings.md).

| Condition | Reader 1 | Reader 2 | Reader 3 |
|---|---|---|---|
| Rejected baseline | 4 / 3 / 2 / 4 / 2 | 4 / 3 / 2 / 3 / 2 | 4 / 3 / 2 / 4 / 3 |
| Original B (`cdfee91`) | 4 / 3 / 3 / 3 / 2 | 4 / 3 / 3 / 3 / 2 | 4 / 3 / 3 / 3 / 3 |
| Tightened B (`50bf121`) | 4 / 3 / 3 / 3 / 2 | 4 / 3 / 3 / 4 / 2 | 4 / 3 / 3 / 3 / 3 |

Different new reader sessions are matched in procedure, not the same people measured twice. The single higher findability rating is a narrow diagnostic signal, not proof of a general gain. **Readiness did not improve.** Compared with the rejected baseline, visuals remain one point higher for each model reader. Other score categories do not show a consistent further improvement.

## Requirement-level findings

- **Product and actor:** all three identify a Mac/Gmail app and the app sorting after the user invokes **Run zero now**, not a user dragging mail. They infer manual-only operation from the pictured example. That inference is not the source truth that scheduling is impossible: the conditional launch-agent option stays owner-visible, outside approved visitor copy.
- **Recovery:** all three explain individual restore and a day's **Restore all**, Gmail **All Mail** and a dated recovery label. Reader1 still asks whether restoring all days is supported. We do not add that capability.
- **Outbound recipients:** all three identify TypeSafe/Jev receiving sender, subject, <=160-character preview, reply-history signals and rules/preferences, plus the separate coding-tool provider receiving draft context. The recipients and field lists are now found. Nevertheless readers1/2 still flag the nearby **“No zero server receives your email”** reassurance as potentially read as nothing leaving the Mac. Reader3 explicitly distinguishes zero's own servers from the third-party recipients. The privacy-reading gap is **not fully closed**.
- **Price:** all three locate the dated unit rate and distinguish metered sorting from the free app. All still ask what typical usage costs. Readers1/3 flag the juxtaposition of free app and paid inference. We do not invent monthly/inbox estimates or billing caps from these requests.
- **Installer:** all three notice non-notarization, Terminal installation and conditional developer-tool additions. Each questions how optional drafts fit Claude Code being added by the installer. This is a material product/choice question, not permission to remove the disclosure or pretend a notarized DMG exists.
- **Visual story:** readers1/3 flag the approved hero's archived folder beside Trash. No hero change is made after this test. All find repetitions or dense Rules prose; the real110-word policy excerpt was deliberately retained for fidelity. Reader2 calls the disclosure block “genuinely dense, well-organized” but still rates readiness2.

## Interpreting reader errors fairly

These raw critiques are not authoritative product facts. Reader2 briefly describes previews as metadata-only and suggests an unimplemented preview-before-archive flow. The source and page disclose an email-content preview and no pre-run approval guarantee. Several readers treat repeated screenshots of the same hero across full/cropped/desktop/mobile inputs as duplicate page objects. The actual B has one hero inbox, not a second inbox chapter. These artifacts can affect visual comments, so we retain those comments without manufacturing a duplicate live section or removing inconvenient scores.

All three ask retention, training, first-run scope or vendor-identity questions beyond the existing claims. Such missing evidence remains unknown. A request to identify a model's underlying vendor is not evidence that it is Claude or GPT. See [truth trace](truth-trace.md) and [dated price/schedule evidence](schedule-and-price-evidence.md).

## Owner-visible conclusion and next gate

The targeted structure made both external recipients and the unit price recoverable in all three answers, but it **did not establish improved decision readiness or resolve every trust reading**. Hand back B as the owner's chosen direction with those limitations plainly visible, not as a reader-selected winner or fully closed trust fix.

Independent B-only skeptical-stranger/design-critic [QA atdf6632d](../../../05-independent-qa/proof/proposal-review.md) has reported on this exact SHA. It confirms the browser results, independently finds the hero Trash contradiction and reprobes canonical installer successfully after the transient429. Following QA, design lead authorized the recipient-explicit privacy plate in Draft5dcaabd6, authored550 with unchanged hero. These scores and answers remain about Draft4, not a comprehension pass for the new wording. A new rendered freeze and applicable fair-fix check are pending; hero Trash removal needs owner approval. Build/deployment remain held.
