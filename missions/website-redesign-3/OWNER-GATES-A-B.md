# zero website redesign 3: your decisions (gates A and B)

Nothing is live. Production is unchanged. This is a proposal to look at, and nothing gets built until you answer.

## What you said, and what changed

| You said | What the proposal does |
|---|---|
| Copy is confusing, zero is just an inbox tool | The headline now says it: **"Clean up your Gmail inbox on your Mac."** Subhead: zero keeps the emails you need to deal with and archives the rest. Undo any archive. Keep using Gmail or Apple Mail. |
| Hero layout is weak, needs animation | New hero (below) shows the app doing its job in a short stepped 1-bit animation |
| Title text sits on the stripe lines | Every window title now sits on a white plate that breaks the stripes, like real System 7. An automated check found no text on a stripe or dither at 320, 390 and 1440 px. |
| The 3 sections are text-left, object-right | Each section now has its own purpose-built object and layout |
| Find more references | 14 live one-bit references, 5 animated. `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/refs/references.md` |
| Too many riddles ("who's waiting...") | Removed. The visible page is about 544 words, down from over 900. Three isolated fresh AI readers, given only the headline and first section, each understood it as a Mac app that cleans up a Gmail inbox (3 of 3 in the final round). |

## Gate A: the words

Six sections, in the order a visitor asks questions:

1. Clean up your Gmail inbox on your Mac. (what is it)
2. See what stays. See what gets archived. (watch it work)
3. Keep mail that needs your reply or action. (how it decides, and that it can be wrong)
4. Undo an archive. Nothing is deleted. (safety)
5. Know what you connect, share and pay for. (Gmail access, data sent, cost)
6. Install zero on your Mac. (the command)

All the honest disclosures are kept (unverified Google app warning, not notarized, what data goes to the AI model, own key cost), each said once. Two alternate headlines are in the copy file.

Full words: `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/01-copy-and-story/proof/COPY.md`. Before and after outline: `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/01-copy-and-story/proof/OUTLINE.md`.

## Gate B: pick a hero

**Recommended: A, "menu-bar roll".** The tray icon opens zero's popover, you click Run zero now, 8 emails hop into the dated Auto-Archived folder, and the count settles at "4 things still need you". Trash stays empty.

![Hero A](file:///Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/hero-a/hero-a-1440.jpg)

**Alternate: C, "poster + two windows".** Quieter and centred, with an Inbox window beside the Auto-Archived window.

![Hero C](file:///Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/hero-c/hero-c-1440.jpg)

B (Finder drag) is not recommended, since it implies you drag mail yourself. Shot: `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/hero-b/hero-b-1440.jpg`. Mobile shots for each: `hero-*-390.jpg` beside them.

Motion frames: `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/storyboard/hero-a-strip.png`. Live runnable comps: open `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/hero-a/index.html` in a browser (add `?static` for the end state).

## Gate B: the sections

Demo (two windows: what stays, what's archived):
![Demo](file:///Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/sections/shots/demo-1440.jpg)

Rules window:
![Rules](file:///Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/sections/shots/decisions-1440.jpg)

Undo window:
![Undo](file:///Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/sections/shots/undo-1440.jpg)

Also: a "zero Info" window for access, data and cost (`before-1440.jpg`), and a Terminal on a black ground for install (`install-1440.jpg`) in the same folder `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/comps/sections/shots/`.

## What we need from you

1. **Gate A:** approve the copy and order, or tell us the exact changes.
2. **Gate B:** pick hero A (recommended) or C, and approve or change the sections.
3. Nothing releases to zero.headless.com until you later say go, after independent QA.

## Honest caveats

- Comps are mock-ups in a browser frame, not a real device. Real Safari behaviour is checked in QA.
- If you pick C or B, the copywriter recounts words (ceiling 550, A is at 544).
- The live site has a font bug where "Read the installer first" shows as "Arst". The new build fixes it.
- One label truncates at 320 px ("Product announcement"), to be fixed in the build.
- Mission files: `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/SPEC.md`. Design brief with all reasons: `/Users/light/Documents/GitHub/zero/missions/website-redesign-3/slices/02-references-and-comps/proof/DESIGN-BRIEF.md`.
