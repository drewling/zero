---
id: OPR.99.0.4.1
slice: 01-copy-and-story
mission: website-redesign-3
status: ready
stage: wip
verified: 2026-09-29 against owner feedback and live capture (proof/before/)
created: 2026-09-29
intent: "Rewrite zero's page so a first-time visitor instantly gets 'a Mac app that cleans up your Gmail inbox', in plain words and a visitor-first order"
depends_on: []
owner_seat: design-copywriter@zero
reviewer_seat: design-lead@zero
---

# Slice 01: plain copy and a visitor-first story

## Intent

The owner: "zero is just an inbox management tool and we've way overcomplicated the way we're talking about it." This slice owns every word on the page. It is proof-only until the owner approves (gate A). Do not edit `landing/`.

## Mini-requirements

1. **One-line positioning in plain words.** Write 3 candidate hero headlines plus subheads that say *inbox*, *Gmail* and *Mac* plainly, and state the job: it keeps what needs you and archives the rest, reversibly. No riddles, wordplay that needs decoding, or internal terms. Recommend one.
2. **Study how comparable products say it.** Look at the first-viewport copy of at least 6 real inbox and email tools (for example SaneBox, Superhuman, Shortwave, Hey, Spark, Clean Email, Mailstrom, Inbox When Ready). Capture each headline and subhead with URL and date. Note what makes each one instantly understood. This is for clarity patterns, not their claims.
3. **Visitor-first outline.** Answer the visitor's questions in order: What is it? → Show me it working → How does it know what to keep? → Is it safe (can I undo)? → What does it need, send and cost? → Install. Each section gets one plain heading that a skimmer can understand on its own. Target 350–550 words of visible copy (current: well over 900).
4. **Ban list, enforced.** Do not use the following as explanations: "open loops", "who's waiting / who's writing", "ball is in their court", "Check it with your coffee", "Two questions", "set something aside", "agent CLI" (say "Claude Code, or another AI coding tool you already use" where needed), or "Jev model reads each thread" (say "an AI model reads each email thread" and name Jev/TypeSafe only where the key, cost and data flow are explained). Run a lint: `grep` the draft for every banned phrase and record 0 hits.
5. **Truth trace.** Every claim and disclosure listed in the mission SPEC Boundaries maps to its new line. Check against `PRODUCT.md`, `macapp/Sources/`, `install.sh` and the shipped app, not the old page. Mark anything not shipped (for example, an automatic morning run) and do not advertise it.
6. **Hero panel content.** Say what the redrawn app panel should show so it tells the story, for example a believable small count (such as "4 things need you") rather than "416". It must remain honest ("illustration, made-up names").
7. **Cold-reader test.** Give the headline, subhead and first section, with nothing else, to 3 fresh model sessions (different models are fine) that have no zero context. Ask: "What does this product do, who is it for, and what would worry you?" Record the answers verbatim. Pass means all 3 say it is an app that cleans or manages a Gmail inbox on a Mac. Iterate until it passes, and record every round.

## Proof contract

- [ ] `proof/COPY.md`: recommended headline, 2 alternates, the full page copy by section, and the word count.
- [ ] `proof/OUTLINE.md`: before/after outline table (old section → new section, what moved, what was cut, why).
- [ ] `proof/comparables.md`: 6+ products with URL, date, their headline and subhead, and the lesson.
- [ ] `proof/truth-trace.md`: disclosure → new location → source file:line.
- [ ] `proof/cold-reader.md`: prompts, model ids, verbatim answers, pass or fail for each round.
- [ ] Banned-phrase lint output showing 0 hits.
- [ ] Design lead review note: the copy fits the one-bit world and the section plan in slice 02.
- [ ] Main lead presents gate A to the owner together with gate B.

## Source material

- `missions/website-redesign-3/SPEC.md` (owner points and audit), `proof/before/`
- `PRODUCT.md`, `keep-policy.md`, `macapp/Sources/PanelView.swift`, `install.sh`, `landing/index.html` (current)
- `missions/website-redesign-2/slices/02b-content-structure/proof/` (the previous attempt, and what not to repeat)
- `~/.openrig/workspace/knowledge/zero-redesign-method.md`

## Intent visual

N/A (copy slice). Slice 02 carries this copy into comps.
