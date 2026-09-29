# COPY: zero, plain inbox-tool story

Status: **DRAFT v3, 2026-09-29.** Reviewed for one-bit design fit, not approved for implementation. Gate A remains with the owner. V1 was 2/3 on strict comprehension, and V2 was 3/3, but both early rounds used a CLI configuration later shown to carry unrelated account context. Round 3 repeated V2's headline, subhead and first section with explicit isolation and passed 3/3. V3 keeps that tested excerpt unchanged, shortens later sections and owns the extra demo strings requested by design review.

## Hero candidates

### Recommended: A, say the job first

**Clean up your Gmail inbox on your Mac.**

zero is a Mac app that keeps the emails you need to deal with and archives the rest. Undo any archive. Keep using Gmail or Apple Mail.

### Alternate B, say what remains

**A Gmail inbox with less to sort.**

zero runs on your Mac. It keeps mail that needs your reply or action and archives the rest, without deleting it. You can undo any archive.

### Alternate C, say what happens

**Keep the emails that need you. Archive the rest.**

zero cleans up your Gmail inbox from your Mac's menu bar. Every archive is reversible, and your usual mail app stays the same.

A puts the familiar task in the headline. Its subhead names the platform, decision and recovery, without asking the reader to decode a metaphor. B is gentler but less active. C names the mechanism but needs its subhead to establish the category.

## Full page copy

Only the text between the following markers is the recommended visible copy. Section numbers and Markdown formatting are authoring metadata, not page text. Count the primary copy, panel labels, navigation, footer and command separately, then report a conservative total. The two alternate heroes are not rendered.

<!-- PAGE-COPY-START -->

### Clean up your Gmail inbox on your Mac.

zero is a Mac app that keeps the emails you need to deal with and archives the rest. Undo any archive. Keep using Gmail or Apple Mail.

**Install zero for Mac**

**Read the installer first**

Apple Silicon. macOS 26 or later. Gmail only.

*Illustration. Names are made up.*

### See what stays. See what gets archived.

A question from a colleague stays. A newsletter gets archived. A payment problem stays. A routine receipt gets archived.

Click **Run zero now** on your Mac to sort the Gmail accounts you connect. Open a kept email in Gmail when you're ready to deal with it.

*Illustration. Made-up names and email subjects, not a result promised for your inbox.*

### Keep mail that needs your reply or action.

An AI model checks each thread against your rules. It keeps replies you owe, direct requests, payment problems, legal matters and deadlines with consequences. Receipts, newsletters and cold sales emails may be archived.

Change what counts in **Settings → Rules**. The model can make mistakes. Check your first few runs.

### Undo an archive. Nothing is deleted.

Archived mail stays searchable in Gmail's **All Mail**, with a dated recovery label. In zero's **Undo** tab, restore one email or choose **Restore all** for a day's archives.

Sorting leaves starred mail alone. If the model can't decide, the email stays in your inbox.

### Know what you connect, share and pay for.

**Gmail access.** Sign in with Google in your browser. zero never sees your password. Google may show an unverified-app warning because zero hasn't completed its review.

**Email data.** zero runs on your Mac. Sorting sends TypeSafe's Jev model the sender, subject, a short preview, reply-history signals, your rules and learned preferences. No zero server receives your email. Read the **Privacy policy**.

**Optional reply drafts.** Claude Code, or another AI coding tool you already use, can draft replies. Its provider receives thread previews, sent-mail samples, writing preferences and saved profile context. Review before clicking **Send reply**. Nothing sends automatically.

**Cost.** zero is free and open source under AGPL-3.0. Sorting needs your own Jev key, billed by TypeSafe. Reply drafts use your coding tool's account and billing.

### Install zero on your Mac.

zero is not notarized by Apple. The installer may add Homebrew, Python, Node, the Google Workspace CLI and Claude Code. **Read the installer** before running it.

```sh
curl -fsSL https://zero.headless.com/install | bash
```

Open zero, connect Gmail and save your Jev key in **Settings → Sorting engine**. Choose **Run zero now** and review the results. Or download from **GitHub Releases**.

<!-- PAGE-COPY-END -->

## Hero panel content and illustration boundary

Show a shortened, illustrative version of the app's existing kept-mail list, not new product controls:

- Count: **4 things still need you**.
- Supporting line: **Across 2 accounts. Tap any to open it in Gmail.**
- List label: **Waiting on you**.
- Four fictional rows: **Alex Rivera / Can you approve the quote?**; **Priya Sharma / Which date works for you?**; **Daniel Kim / Your payment failed**; **Sarah Mitchell / Contract changes to review**.
- Action label, if the existing run button appears: **Run zero now**.
- Use the illustration caption in the primary copy adjacent to the panel. This count is illustrative, not a measured customer outcome, a target, a guaranteed inbox size or a shipped screenshot.
- The before/after example is editorial illustration, not an extra app mode. Do not add an invented “Clean inbox” control, a timer or a claimed speed-up.

## Demo and window strings, owned after design review

These are editorial illustrations, not new app screens. Count both occurrences if a row is shown in hero and demo. Keep the four hero rows above intact. Use the shorter demo rows below to avoid reading the same long subjects twice.

| Destination | Fictional sender | Fictional demo subject |
|---|---|---|
| Stays | Alex Rivera | Approve quote? |
| Stays | Priya Sharma | Which date? |
| Stays | Daniel Kim | Payment failed |
| Stays | Sarah Mitchell | Contract changes |
| Archived | Fieldnotes | Weekly newsletter |
| Archived | Northwind | Coffee receipt |
| Archived | SalesCo | Sales introduction |
| Archived | Parcel | Shipping confirmation |
| Archived | Workshop | Webinar invitation |
| Archived | Market | Product announcement |
| Archived | Bank | Monthly statement |
| Archived | Priya | Lunch confirmed |

The last row has an editorial annotation **Last reply: you**. Do not depict a new app reason badge. Do not archive a sign-in/security alert just because it is automated, since it could need urgent action. The “Stays” and “Archived” words label destinations, not an invented new product mode.

Plain window titles: **Inbox · Auto-Archived 2026-09-29 · Rules · Undo · zero Info · Terminal**. These are illustration titles. zero's menu-bar popover does not need an invented title bar. Break decorative stripes behind title text with white, as specified in slice 02.

Count the hero's short illustration label in primary copy. Extra hero/motion chrome is **Trash · Auto-Archived 2026-09-29 · Working…**. The folder string is a second occurrence, so count it again. Drop the menu-bar clock. Count Working conservatively alongside the idle button even though the same button swaps between them. The hero's pre-sort archived rows are greeked bars with no readable words. The section 2 caption remains visible and counts separately.

Keep extra demonstration chrome within this budget: **Stays · Archived · All Mail · Restore all · Copy command**. Do not add counters, duplicate paragraphs or other visible strings without recounting against the 550-word ceiling. Decision-card text reuses the existing decision copy, not an extra repeated explanation.

## Navigation, footer and routes

Visible navigation: **How it works · Undo · Before you install · Source · Install**.

Visible footer: **zero · AGPL-3.0 · Source · Privacy · Terms**.

Destination map, implementation must preserve:

- Install CTAs → `#install`.
- How it works → demonstration/decision section; Undo → recovery section; Before you install → data/requirements section.
- Read the installer / Read the installer first → `/install.sh`.
- Privacy policy and Privacy → `/privacy.html`; Terms → `/terms.html`.
- Source → `https://github.com/drewling/zero`.
- GitHub Releases → `https://github.com/drewling/zero/releases`.
- “Jev key” in the setup paragraph → `https://console.typesafe.ai/keys`.
- Exact executable command is unchanged. Do not replace it with the aspirational setup command in PRODUCT.md.

## Word count

V3 mechanical count: **425** primary-copy words (including install command, both hero routes and the short hero caption), **124** additional visible words, **549 visible words total**. Extra text includes the hero panel (46), all 12 demo sender/subject pairs (40), the last-reply annotation (3), window titles (8), extra chrome (8), additional hero/motion chrome (4), navigation (9), footer (5) and site brand (1). The demo's destination labels are counted once as group labels, not a repeated badge on every row. If the comp repeats any title, caption, button or row elsewhere, count that occurrence too.

Reproduce with `node proof/verify-copy.mjs` from the slice directory. Counter uses Unicode letter/number tokens, retaining internal apostrophes, dots and hyphens. Decorative separators, arrows and Markdown syntax do not count. Target: 350–550. This is an authored-copy inventory, not a claim that the unbuilt page has already been checked. There is one spare word for incidental chrome. The builder and QA must count the actual rendered page. No automatic-run promise, invented speed metric, testimonials or customer results.
