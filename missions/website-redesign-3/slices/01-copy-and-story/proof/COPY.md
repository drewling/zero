# COPY: zero, plain inbox-tool story

Status: **DRAFT v1, 2026-09-29.** For slice 02 comps, not approved for implementation. Gate A remains with the owner. Truth trace, comparable study and cold-reader evidence are in progress.

## Hero candidates

### Recommended: A, say the job first

**Clean up your Gmail inbox.**

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

### Clean up your Gmail inbox.

zero is a Mac app that keeps the emails you need to deal with and archives the rest. Undo any archive. Keep using Gmail or Apple Mail.

**Install zero for Mac**

Apple Silicon. macOS 26 or later. Gmail only.

### See what stays. See what gets archived.

A question from a colleague stays. A newsletter gets archived. A payment problem stays. A routine receipt gets archived.

Run zero from your menu bar to sort the Gmail accounts you connect. Open a kept email in Gmail when you're ready to deal with it.

*Illustration. Made-up names and email subjects, not a result promised for your inbox.*

### Keep mail that needs your reply or action.

An AI model reads each email thread against your rules. It looks for a reply you owe, a direct request, a payment problem, a legal matter or a deadline with consequences. Receipts, newsletters and cold sales emails can be archived.

Change what counts in **Settings → Rules**. The model can make mistakes. Check your first few runs.

### Undo an archive. Nothing is deleted.

Archived mail stays searchable in Gmail's **All Mail**, with a dated recovery label. In zero's **Undo** tab, restore one email or choose **Restore all** for a day's archives.

Sorting leaves starred mail alone. If the model can't decide, the email stays in your inbox.

### Know what you connect, share and pay for.

**Gmail access.** Sign in with Google in your browser. zero never sees your password. Google may show an unverified-app warning because zero hasn't completed its review.

**Email data.** zero runs on your Mac. Sorting sends TypeSafe's Jev model the sender, subject, a short preview, reply-history signals, your rules and learned preferences. The zero project has no server receiving your email. Read the **Privacy policy**.

**Optional reply drafts.** Claude Code, or another AI coding tool you already use, can draft a reply. That provider receives the thread. Review it first. No reply is sent until you click **Send reply**.

**Cost.** zero is free and open source under AGPL-3.0. Bring your own TypeSafe Jev key for sorting, billed by TypeSafe. Reply drafts use your coding tool's account and billing.

### Install zero on your Mac.

zero is not notarized by Apple. The installer may add Homebrew, Python, Node, the Google Workspace CLI and Claude Code. **Read the installer** before running it.

```sh
curl -fsSL https://zero.headless.com/install | bash
```

Then open zero, connect Gmail and save your Jev key in **Settings → Sorting engine**. Choose **Run zero now** and review the results. Prefer a download? **GitHub Releases** has the app.

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

## Navigation, footer and routes

Visible navigation: **How it works · Undo · Before you install · Source · Install**.

Visible footer: **zero · AGPL-3.0 · Source · Privacy · Terms**.

Destination map, implementation must preserve:

- Install CTAs → `#install`.
- How it works → demonstration/decision section; Undo → recovery section; Before you install → data/requirements section.
- Read the installer → `/install.sh`.
- Privacy policy and Privacy → `/privacy.html`; Terms → `/terms.html`.
- Source → `https://github.com/drewling/zero`.
- GitHub Releases → `https://github.com/drewling/zero/releases`.
- “Jev key” in the setup paragraph → `https://console.typesafe.ai/keys`.
- Exact executable command is unchanged. Do not replace it with the aspirational setup command in PRODUCT.md.

## Word count

V1 mechanical count: **425** primary-copy words (including install command), **60** panel/navigation/footer words, **485 visible words total**. Counter uses Unicode letter/number tokens, retaining internal apostrophes, dots and hyphens. Decorative separators, arrows and Markdown syntax do not count. Target: 350–550. No automatic-run promise, invented speed metric, testimonials or customer results.
