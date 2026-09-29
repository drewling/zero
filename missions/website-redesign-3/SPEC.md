---
id: OPR.99.0.4
mission: website-redesign-3
stage: wip
verified: 2026-09-29 against owner feedback relayed by advisor-lead@kernel and live capture of zero.headless.com
created: 2026-09-29
intent: "Make zero.headless.com read as a simple inbox tool and look finished: plain copy, a stronger hero, rethought sections, and motion and polish in the one-bit style"
depends_on: ["OPR.99.0.3"]
---

# Mission: website redesign 3, clear copy and a finished-looking page

## Why (owner feedback, 2026-09-29 ~20:24Z, verbatim points)

The owner looked at the live site (redesign 2, Direction B "one-bit desktop", slice 05 panel redraw) and said:

1. **Hero:** "just doesn't have a good layout to it and it could do with more animations and stuff." Text such as the "zero" window title sits **on top of the stripe lines**. "I like the style but I feel like the slug could be executed even better with a bit more detail and a bit more polish."
2. **Copy is confusing:** "It asks who's waiting, not who's writing" reads like a riddle. "A lot of the way the text is written and what's on the page text-wise is just confusing."
3. **Sections are poorly planned.** "Two questions" is again text on top of black lines. It needs white behind it to block the lines.
4. **Everything below the hero** could use `/impeccable` design. "Find more references in this style for more ideas on how we can style it."
5. **The three sections under the hero** are "just text on the left and something on the right", "a mess" and "confusing".
6. **The core point:** "At the end of the day zero is just an inbox management tool and we've way overcomplicated the way we're talking about it in so many different ways throughout the page." Read it from a user's perspective, the way the owner reads other sites that do similar things.

**Keep:** the one-bit Macintosh style (the owner likes it). **Change:** the words, the order, the hero layout, the section designs, and the level of detail, motion and polish.

## Advisor's audit of the live page (evidence for the seats, not a design)

Captures: `slices/01-copy-and-story/proof/before/` (1440 and 390, fold and full page, plus extracted copy).

- **Bug, window titles over stripes.** `landing/site.css` `.window-bar` paints the stripes, and its title `<span>` has no background, so "zero", "Two questions" and "Terminal" render struck through. A classic Mac title bar puts the title in a white box that breaks the stripes.
- **Jargon a visitor has to decode:** "open loops", "Jev", "TypeSafe's Jev model", "agent CLI", "the ball is in their court", "who's waiting, not who's writing", "Check it with your coffee. Then close it", "Two questions", "Set something aside and zero can learn to handle mail like it next time".
- **The hero never says "inbox".** "Only the mail that still needs you" plus a 40-word paragraph. A visitor has to work out that this cleans up their Gmail inbox.
- **The hero panel shows "416 things still need you"**, which undercuts a promise of a short, calm inbox.
- **The three content sections** use the same text-left, thin-object-right grid. "Check it with your coffee" has nothing on the right. "Two questions" is a small box in a large empty area. None of them *shows* the product doing its job, for example a messy inbox becoming a short one.
- **Word count:** about 1,290 words in `index.html` including markup text. The story still reads as a feature list with clever headlines.

## Outcome

A visitor understands in five seconds: **zero is a Mac app that cleans up your Gmail inbox. It keeps the emails you need to deal with, archives the rest, and you can undo anything.** Then the page shows it happening, answers "is it safe / what does it need / what does it cost", and gets them to install. It keeps the one-bit style, with a hero and sections that look deliberately composed, carry real detail, and move.

## Boundaries

- **Truth over wording.** Every claim, disclosure, requirement and route stays true: reversible archive via dated label and All Mail, starred mail untouched, uncertain threads kept, Apple Silicon + macOS 26, Gmail only, the unverified Google app warning, not notarized, installer dependencies, the data sent to Jev, optional reply drafts via the agent CLI, costs, AGPL, the Privacy and Terms links, the exact install command. The words, order, grouping and length are all open to rewriting. Do **not** carry copy over verbatim (see `~/.openrig/workspace/knowledge/zero-redesign-method.md`).
- Product names such as Jev and TypeSafe may appear where a visitor needs them (the key, cost and data flow), not as the explanation of how it works.
- Keep the one-bit Mac world (black, white, dither, pixel display type, windows). It is now a style to execute *better*, not to replace. Motion must fit it: stepped, snappy, 1-bit (think classic Mac window zoom rects, marching ants, a cursor dragging mail into a folder), and never smooth SaaS gradients.
- Preserve: semantic HTML, the page working without JS, reduced motion, keyboard access, visible focus, no horizontal overflow at 320px, static nginx/Docker packaging, `landing/build.sh` and `node --test landing/test-site.mjs` green (update the tests to match the new truth, do not delete coverage).
- Replace, do not layer. Remove obsolete markup, CSS and tests that the new build no longer uses.
- **No production deploy without an explicit owner go at slice 06.** Production stays as it is until then.

## Seats

| Seat | Role in this mission | Model |
|---|---|---|
| `main.lead` | Owns the mission, dispatch, gates, owner updates | claude-opus-5-5 |
| `design.lead` | Owns visual direction: references, hero and section comps, motion direction, final design sign-off | claude-opus-5-5 |
| `design.copywriter` (new) | Owns the words: plain positioning, outline, all page copy, the comprehension test | gpt-6.1-sol |
| `development.implementer` | Builds the structure and static design from approved comps and copy | gpt-6.1-sol |
| `development.motion` (new) | Builds the motion and interaction layer in parallel, then integrates | gpt-6.1-sol |
| `review.qa` | Independent QA of visuals, copy, a11y, responsive, packaging | gpt-6.1-sol |

## Sequence and gates

1. [01 Copy and story](slices/01-copy-and-story/SPEC.md), copywriter, with the design lead reviewing. Plain positioning, new outline, full copy draft, cold-reader comprehension test. **Owner gate A:** the owner approves the outline and copy.
2. [02 References and comps](slices/02-references-and-comps/SPEC.md), design lead. It runs in parallel with 01 and uses the 01 draft as soon as it exists. At least 8 new references in this style, a hero composition with a detail and motion storyboard, and a design for each section. Comps carry the 01 copy, not the old copy. **Owner gate B:** the owner picks a hero and approves the section designs. Gates A and B can be shown to the owner together.
3. [03 Build structure](slices/03-build-structure/SPEC.md), implementer. The approved copy and comps, rebuilt cleanly in `landing/`, including the title-bar fix.
4. [04 Motion and polish](slices/04-motion-and-polish/SPEC.md), motion engineer. It prototypes from gate B in a sandbox while 03 builds, then integrates on top of the 03 SHA. The design lead does a polish pass and signs off.
5. [05 Independent QA](slices/05-independent-qa/SPEC.md), QA. Checks the exact SHA against gates A and B, runs the functional, a11y and responsive checks, and repeats the cold-reader test on the built page.
6. [06 Release](slices/06-release/SPEC.md), main lead. Only after QA PASS and an explicit owner go. Live verification and a rollback path.

## Done means

The owner reads the live page and agrees it says "inbox tool" plainly, that the hero and sections look composed and finished, and that nothing is confusing. There is QA PASS evidence on the released SHA, and the live site matches it.
