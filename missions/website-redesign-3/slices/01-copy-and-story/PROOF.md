# PROOF: OPR.99.0.4.1 plain copy and visitor-first story

Prepared by: design-copywriter@zero. Date: 2026-09-29. **Verdict: authoring ready for gate A, owner approval pending.** Design reviewer: design-lead@zero. This is copy proof, not independent built-page QA.

## What this proves

The proposed page states the task as **“Clean up your Gmail inbox on your Mac.”** It follows the visitor's decision path, stays within a measured 549-word authored inventory and preserves shipped recovery, requirements, permissions, provider-data and cost disclosures. Three isolated fresh model sessions identify a Mac app managing a Gmail inbox from the hero/subhead/first demonstration alone.

## Proof contract map

| SPEC proof item | Artifact | Observed result |
|---|---|---|
| 1. Recommended hero, two alternates, full copy, word count | `proof/COPY.md`, `proof/verify-copy.mjs`, `proof/banned-phrase-lint.txt` | V3 contains all three heroes and all six sections. 425 primary + 124 panel/demo/chrome/nav/footer/brand words = 549. Both repeated hero/demo row occurrences count. |
| 2. Before/after outline | `proof/OUTLINE.md` | V2 maps every old section to the new visitor-first location, cut or rewrite, with a reason. |
| 3. Six comparable tools | `proof/comparables.md`, six `proof/comparables/*-first-viewport.png` images | Dated URL/headline/subhead/CTA and clarity lesson for SaneBox, Superhuman, Shortwave, HEY, Spark and Clean Email. Quotes visually inspected. |
| 4. Disclosure truth trace | `proof/truth-trace.md`, `proof/shipped-app-check.txt` | Every mission-boundary disclosure mapped to wording and source lines. Seven relevant code/policy files are byte-identical to installed app 1.7.0 payload. No assumed install-time schedule. |
| 5. Cold-reader test | `proof/cold-reader.md`, both prompt files, nine reader JSONs | Every prompt, model/session id and reply retained verbatim. Early rounds invalidated for context contamination. Accepted isolated round 3: 3/3 name Mac app, Gmail and inbox sorting. |
| 6. Banned-phrase lint output | `proof/banned-phrase-lint.txt` | Real case-insensitive fixed-string grep for all banned phrases plus curly-quote variants: 0 hits in COPY.md. |
| 7. Design lead review | `proof/design-review.md`, commit `bc9f296` | Fits the one-bit section plan. V3 incorporates requested hero installer link, owned demo rows, plain titles and caption. Final 549-word constraint sent to designer. |
| 8. Main lead presents gate A with gate B | Durable handback to main-lead@zero | **Pending downstream. Not claimed complete.** No owner decision or implementation authorization received by this seat. |

## Checks and limits

Reproduce from the slice directory:

```sh
node proof/verify-copy.mjs
node proof/verify-copy.mjs --cold-reader
```

Fresh check: word budget PASS, every grep 0 hits, exact tested excerpt retained, 3 distinct successful one-turn reader sessions, six PNG captures and required proof files exist. `git diff --check` is clean. No `landing/` diff against the pre-proof baseline.

The 549 words are an authored inventory, not an assertion about a page that has not yet been built. Keep demo destination labels grouped, do not repeat captions/paragraphs and recount all extra visual chrome. The designer/builder have one word of spare budget. Both hero and demo captions, Trash, the repeated folder title and transient Working state are counted, while the clock is omitted. AI readers are not humans and do not prove a literal five-second comprehension time. Later independent QA repeats comprehension on the built page and checks its actual text, responsive presentation, keyboard/no-JS/reduced-motion paths and packaging. No production change, provider pricing quote or inbox mutation was made.

The formal C1 proof drop is `proof/authoring-clear.md`, attached after committing the copy candidate. Its CLEAR verdict covers authoring checks only, not owner gate A or production acceptance.
