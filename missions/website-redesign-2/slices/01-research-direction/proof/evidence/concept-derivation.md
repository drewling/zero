# Concept derivation (impeccable replacement-world flow)

Date: 2026-09-29. Author: design-lead@zero. Mode: **Persuade** (landing page).

## 1. What is true about zero

- **Unique mechanism, in one sentence:** on the daily schedule you set (Settings → Daily routine), zero sends each Gmail thread's relevant text to Jev, TypeSafe's AI sorting service (wording verified against `landing/index.html`, "Before you install" → Jev key). It keeps the threads where someone is waiting on you. Everything else is archived with a dated recovery label, never deleted.
- **Audience and scene:** Mac users with too much Gmail, often developer-adjacent (the install is a `curl | bash` in Terminal). They open the laptop in the morning and dread the inbox.
- **Cultural home:** macOS itself (menu-bar utilities, Finder, the Mac's own history), inbox-zero and Getting Things Done practice ("open loops" is David Allen's term, and it is the name of zero's main tab), and the morning routine.
- **What the first surface must prove:** that zero keeps only what needs you, that nothing is ever lost, and that installing it is honest and safe.
- **The rut, kept off the list:**
  - The page this category always ships: a dark SaaS hero with a product screenshot on a gradient, the Linear, Superhuman or Stripe template.
  - Its predictable opposite: cream paper, an editorial serif and a terracotta accent.
  - The literal reading of the brief ("sorting mail"): the rejected departure board and the post-office sorting frame.

## 2. Seven grounded candidates, ordered by resonance

| # | Candidate | Family | Why it resonates and can carry the mechanism |
|---|---|---|---|
| 1 | **Native macOS utility.** The page is the Mac itself: the menu bar, the real popover dropping down, Settings-style grouped rows. | Interface language | zero *is* a menu-bar app, so the medium and the message match. This is the most familiar option and the most likely landing spot for every run. |
| 2 | **GTD tickler file.** Forty-three folders, 31 days and 12 months, with things resurfacing on a date. | Stationery ritual | "Open loops" is GTD vocabulary. Dated folders match the dated recovery labels. |
| 3 | **Morning edition front page.** Today's paper: "4 things still need you." | Publication | The once-a-morning cadence. A briefing that you read rather than manage. |
| 4 | **Recovery day book or ledger.** Every run is a dated entry that can be reversed. | Document | Reversible by construction, one entry per day. |
| 5 | **Plain-language rulebook.** The keep-bar typeset as a readable policy with marginal notes. | Documentation standard | The rules are sentences you can edit, not a DSL. |
| 6 | **First light.** The kitchen table at 7:30 with the laptop open in window light. What still needs you sits in the light, and what zero set aside sits in shade. | Place and ritual | Ambient, once a morning, "forget it's running." This is the moment the product is for. |
| 7 | **Pigeonhole sorting frame.** | Physical furniture (the literal reading) | The rut spend. It is too close to the rejected sorting board. |

The candidates span five families: interface, stationery, publication, document and place. No material family covers more than three.

## 3. Roll

`impeccable concept-seed --scope direction --mode persuade` gave seed key **`baf5f3f6`** with **assigned index 6: First light**.

## 4. Challengers, fused with product facts and weighed on two axes: audience identification (AI) and product clarity (PC)

| Challenger | Fused reading for zero | AI | PC | Verdict | Kept line / raise |
|---|---|---|---|---|---|
| Riley moire gallery | Black-and-white wave fields, with tighter lines where mail needs you | Loses | Loses | **Declined** | *Raise, total commitment:* First light uses **one** light band as its only accent, with no decorative gradients and no second highlight colour. |
| Gothic-lolita fashion mook | Annotation ribbons that name every garment | Loses | Loses | **Declined** | *Raise, name every real part:* the real app image carries thin callouts naming its real controls (Open loops, Undo, Run zero now). Nothing is invented. |
| Oscilloscope bench | A trace locks when a thread "triggers" as needs-you | Loses | Holds partly | **Declined** | *Raise, measured grid:* all type and rules sit on one 8 px baseline, and times are set in tabular figures. |
| **One-bit desktop** | The Macintosh desktop of 1984. zero's real window is the only colour on screen. Archived mail goes into a dated **folder**. The Trash is shown empty: "zero never puts mail here." | **Wins** (Mac users know it by heart) | Holds | **Competitive**, full alternate | Comped as Direction B. |
| **Daylight section** | An architectural section of a morning. A sunbeam travels across time stamps: the routine runs, you open the laptop. | Holds partly | Wins (time and state together) | **Competitive**, full alternate | *Raise to A, tabular time stamps:* First light's kicker and recovery rail use tabular times and dates, with the sunbeam as the moving state band. No separate comp; the quality-bar card is shown. |
| Bioluminescent wake | Only active things glow, and everything at rest returns to dark | Loses | Holds partly | **Declined** | *Raise, rest recedes:* archived categories drop to shadow blue and lose contrast; only "stays" rows sit in the light. |

- **Impeccable's pick:** candidate 1, native macOS utility (Direction C). *Honest risk:* it is the most familiar option and sits close to Raycast, CleanShot and Things marketing pages.
- **Standing exit, the category standard:** a Linear-style dark product page. It is offered quietly and never recommended.

## 5. Build path

The comps are **code-rendered HTML**, captured through Aside, not generated images:

- They use the real app PNG, the real copy and the real install command, so they stay honest about the product.
- The only image generator available is the billed OpenAI fallback on the owner's key. I did not spend on it without a go-ahead.
- If the owner wants painted north-star comps as well, that is a separate, cheap step after the choice.
