# OUTLINE: from feature list to visitor decision

Status: **DRAFT v2, 2026-09-29.** Aligned with COPY v3 and reviewed for design fit. Copy slice only. The design lead owns the one-bit composition, section designs and motion storyboard. Owner gate A approves words and order alongside gate B, not this proof commit.

## Visitor and outcome

A person with too much Gmail, using a supported Mac, needs to know what zero does before deciding whether to let it archive mail. In the first five seconds: **Mac app, Gmail inbox, keep what needs action, archive the rest, undo any archive.** No new mail client, promised schedule, inbox-size guarantee or performance claim.

The owner has already selected the one-bit Mac world. This plan uses its windows and folder/recovery affordances to explain the job, not to introduce clever period-themed language. No style interview or new aesthetic direction is needed for this copy-only assignment.

## New visitor-first sequence

| Order | Visitor question | Standalone heading | What the words must prove | Suggested content role, not a comp |
|---|---|---|---|---|
| 1 | What is it? | Clean up your Gmail inbox on your Mac. | The task in the headline, Mac and reversible archive in the subhead, supported hardware beside the CTA | Hero with the four-row illustrative app panel |
| 2 | Show me it working | See what stays. See what gets archived. | Familiar concrete messages end up in one of two places | Labeled keep/archive transformation, readable without animation |
| 3 | How does it know? | Keep mail that needs your reply or action. | A model uses your rules, identifies consequences, and can be wrong | A compact decision example, not a jargon window |
| 4 | Can I undo it? | Undo an archive. Nothing is deleted. | All Mail plus dated recovery label, restore one or a day, starred and uncertain mail protected | Recovery label/folder moment, a genuine Undo action |
| 5 | What does it need, send and cost? | Know what you connect, share and pay for. | Google access and warning, sorting and draft data flow, own-key billing, free AGPL app | Short, openly readable disclosure block |
| 6 | How do I get it? | Install zero on your Mac. | Notarization/dependency warning before command, connect account, add key, run and check | One legible Terminal command and brief next steps |

Primary CTA: **Install zero for Mac**, links to `#install`. Secondary due-diligence route: **Read the installer**, not a competing signup. Privacy, Terms, Source, GitHub Releases and the TypeSafe key route remain reachable.

## Before → after, preserving truth rather than wording

Source for old outline: committed `landing/index.html` and mission audit. The old page is evidence of the failed structure, not the product source of truth.

| Old section/content | New location | Moved, cut or rewritten | Why |
|---|---|---|---|
| Hero: “Only the mail that still needs you” and long category paragraph | 1, direct inbox headline and short Mac subhead | Rewritten. Headline finally says Gmail and inbox. Undo moves into the immediate promise | Visitor learns the familiar task before the visual theme |
| Hero panel: 416-item list, nine sample rows, terminology tabs | 1, four relevant fictional rows; 2, keep/archive illustration | Replace count and trim repeated row content. Label the illustration honestly. No invented interface | A huge kept count contradicts the story. Four examples teach the job without promising four actual results |
| “It asks who's waiting, not who's writing” | 3, plain explanation of what is kept | Replace wordplay with replies, requests and consequences | The reader should not solve a riddle to understand a mail tool |
| “Two questions” signal window, sender-history explanation | 3, decision example; 5, data-flow disclosure | Remove abstract title and sports metaphor. Keep reply-history signals where data transmission is explained | Mechanism supports the user outcome instead of becoming the headline |
| “Check it with your coffee. Then close it” | 2, menu-bar run and Gmail link; 6, setup step | Cut the ritual headline. Do not imply installation schedules automatic runs | Shows the shipped manual action rather than aspirational morning behavior |
| Learning sentence: “Set something aside…” | 3, editable rules; 5, learned-preference disclosure | Cut vague benefit claim. Preserve the fact of learned data where it matters for privacy | No unexplained promise that the model learns from every archive |
| “Nothing is deleted” with recovery list | 4, actionable Undo heading and concise recovery paragraph | Rewrite and consolidate. Retain All Mail, dated label, restore one/day, star protection and uncertainty | Safety answers “what if it is wrong?”, not just “what happens to labels?” |
| “What it needs, sends and costs”, five long fact cards | Hardware in 1; access/data/drafts/cost in 5; installer dependencies in 6 | Redistribute each fact once to its decision point. Add the actual reply-history data fields | Requirements screen unsuitable visitors early. Disclosure stays honest and readable |
| Long Terminal four-step install list | 6, warning, exact command, compact next-step paragraph | Rewrite. Keep the exact command, script/release links and real app action names | Fewer steps on the page, without disguising required setup |
| App-license footer and legal/source links | Footer and relevant inline links | Preserve destinations and AGPL license, not all old words | Legal and source access are not optional simplifications |

## Content budgets and design handoff

- Keep all six sections in the visitor order. Do not invent a testimonials/logo wall, feature grid, AI manifesto or FAQ that repeats these facts.
- First viewport must carry the recommended headline/subhead and direct CTA, not only a stylized app drawing. Its category is not supplied by a decorative window title.
- The demo and recovery moments should be distinct. Motion may show the transformation, but the static state needs both destination labels.
- H2s remain meaningful in isolation. Pixel/window craft must not force duplicate short, cryptic titles over striped bars.
- The disclosure block is not hidden behind an accordion to make the word count look low. Small print must remain readable.
- Visible word budget is measured in COPY.md. Alternate heroes and planning notes are excluded, rendered panel/controls and navigation are included.
- COPY v3's claims now map to shipped source in `truth-trace.md`. Cold-reader round 3 is 3/3 on the exact hero/subhead/demo excerpt, and grep finds zero banned phrases. No edit to `landing/`, no deploy and no push from this slice. The 549-word authored inventory includes both hero and demo rows, captions, window chrome, navigation and footer. Recount any added/duplicated strings in the actual comps/build.
