# Section copy for two whole-page proposals

DRAFT 3, 2026-09-29. Joint selection: make both A and B, then recommend from reader evidence. Hero B is approved and remains unchanged. These are section words for proof comps, not approved implementation copy. The hero's frozen authored inventory is 104 words, including one navigation bar, illustration rows/ages, both popover states and its extra zero mark.

The marked blocks below are visitor copy. Markdown headings, bold/link labels and command text render, but authoring markers and notes do not. Use one shared footer. Count all repeated app labels and readable window text separately when rendered. Do not add a second header.

## A: recovery-first, four blocks including hero

<!-- COPY-A-START -->

### See what went into the archive.

Start a run from zero's menu bar. The app sorts the Gmail accounts you connect. Keep reading your connected Gmail account in Gmail or Apple Mail.

An AI model uses your rules to keep replies you owe, direct requests, payment problems, legal matters and consequential deadlines. Receipts, newsletters and cold sales may be archived. Change the rules in **Settings → Rules**. Sorting leaves starred mail alone and keeps threads it can't decide about.

Check your first few runs. The model can make mistakes. In zero's **Undo** tab, restore one email or choose **Restore all** for a day's archives. Nothing is deleted: archived mail stays searchable in Gmail's **All Mail** under a dated recovery label.

### Before you install.

**Google sign-in.** Connect Gmail through Google in your browser. zero never sees your password. You may see an unverified-app warning because zero hasn't completed Google's app review.

**Sorting data.** TypeSafe's Jev model receives sender, subject, a preview of up to 160 characters, whether you sent the latest message and whether you've replied to that sender before, your rules and learned preferences. No zero server receives your email. [Privacy policy](/privacy.html).

**Sorting cost.** Bring your own Jev key, billed by TypeSafe. See [TypeSafe pricing](https://docs.typesafe.ai/models). The app is free and open source under AGPL-3.0.

**Optional drafts.** Claude Code, or another AI coding tool you already use, can draft replies using its account and billing. Its provider receives thread previews, sent-mail samples, writing preferences and saved profile context. Review before **Send reply**. Drafts never send automatically.

**Installer.** zero is not notarized by Apple. The installer may add Homebrew, Python, Node and the Google Workspace CLI. It adds Claude Code if no supported coding tool is installed.

### Install when you're ready.

```sh
curl -fsSL https://zero.headless.com/install | bash
```

**Copy command**

Open zero, connect Gmail and save your [Jev key](https://console.typesafe.ai/keys) in **Settings → Sorting engine**. Or download from [GitHub Releases](https://github.com/drewling/zero/releases).

<!-- COPY-A-END -->

## B: risk-first, five blocks including hero

<!-- COPY-B-START -->

### Before you install.

Read your connected Gmail in Gmail or Apple Mail.

**Google sign-in.** Connect Gmail through Google in your browser. zero never sees your password. You may see an unverified-app warning because zero hasn't completed Google's app review.

**Sorting data.** TypeSafe's Jev model receives sender, subject, a preview of up to 160 characters, whether you sent the latest message and whether you've replied to that sender before, your rules and learned preferences. No zero server receives your email. [Privacy policy](/privacy.html).

**Sorting cost.** Bring your own Jev key, billed by TypeSafe. See [TypeSafe pricing](https://docs.typesafe.ai/models). The app is free and open source under AGPL-3.0.

**Optional drafts.** Claude Code, or another AI coding tool you already use, can draft replies using its account and billing. Its provider receives thread previews, sent-mail samples, writing preferences and saved profile context. Review before **Send reply**. Drafts never send automatically.

**Installer.** zero is not notarized by Apple. The installer may add Homebrew, Python, Node and the Google Workspace CLI. It adds Claude Code if no supported coding tool is installed.

### Choose what needs to stay.

Run zero from its menu bar to sort connected Gmail accounts. AI applies your rules. Starred mail stays untouched. Uncertain threads stay in your inbox. Check your first runs: the model can make mistakes.

### Restore archived mail.

In zero's **Undo** tab, restore one email or a day's archives with **Restore all**. Nothing is deleted. Find archived mail in Gmail's **All Mail** under a dated recovery label.

### Ready to install?

```sh
curl -fsSL https://zero.headless.com/install | bash
```

**Copy command**

Open zero, connect Gmail, then add your [Jev key](https://console.typesafe.ai/keys) in **Settings → Sorting engine**. Or download from [GitHub Releases](https://github.com/drewling/zero/releases).

<!-- COPY-B-END -->

## Shared object text and routing

<!-- OBJECT-COPY-START -->

Undo
Open loops
Accounts
Undo
Settings
Tue 29 Sep
8 set aside · alex@example.com
Restore all
Weekly newsletter
Fieldnotes · 2d
Coffee receipt
Northwind · 2d
Sales introduction
SalesCo · 3d
Shipping confirmation
Parcel · 3d
Webinar invitation
Workshop · 4d
Put this email back in the inbox
Illustration. Made-up mail.
zero
Before you install
Terminal
zero
AGPL-3.0
Source
Privacy
Terms

<!-- OBJECT-COPY-END -->

The first Undo above is the editorial window title, the second is the actual tab. These are five visible rows from an eight-item fictional batch, not repeated kept hero rows. A visible System 7 scrollbar makes the window's partial view clear, with no extra copy. Eight matches the hero's archived-message count. Ages and fictional address count. The additional zero before the ledger title is the new app icon label, distinct from the footer's zero. Tooltip is the real shipped individual-control wording; **Restore all** is the real batch control. The caption identifies an editorial facsimile, not a screenshot of someone's mail. If designer replaces the Get Info title with a shorter title, use exactly the rendered title in the final inventory. No live inbox screenshot, no new explanation badge, no Finder/Gmail Restore.

## B Rules object: exact source-contiguous excerpt

<!-- RULES-B-COPY-START -->

Settings
Open loops
Accounts
Undo
Settings
Rules
Save

## Keep a thread only if it genuinely needs me to act

- A real person is awaiting my reply or my decision.
- There is an unanswered direct question or request addressed to me.
- A payment has actually failed or is a live problem (not a routine receipt).
- It is a legal, contractual, or dispute matter.
- There is an explicit deadline with a real consequence.

## Archive everything else (reversibly)

- Cold outreach, sales, prospecting, pitches, even when the sender uses a real
  human name and I have never replied to them.
- Receipts, invoices, statements, order and delivery confirmations.
- Notifications, alerts, digests, newsletters, social, marketing, surveys.

<!-- RULES-B-COPY-END -->

This is a faithful contiguous excerpt of `keep-policy.md:8–21`, including the Cold outreach bullet that lies between the archive heading and Receipts. Do not silently remove a middle bullet from a supposedly real editor. Settings is selected, the pane is Rules, and Save is the real control. A's policy sentence is omitted from B because this excerpt explains it once. The complete policy continues beyond the frame. The real editor scroll affordance may show that without inventing additional words. All authored excerpt text counts, even if a scroll viewport clips its last lines. Final rendered inventory still requires designer's stable source; no per-email reason badge or new policy mode.

`#install` begins the decision ledger plus installation area, so the approved hero CTA does not skip warnings/cost/data. `#before` can point to the same ledger. `#command` points to the Terminal. `#undo` identifies readable recovery, `#how` identifies operation/rules (A can share the recovery area). Preserve `/install.sh` as the approved hero's Read the installer first route, `/privacy.html`, `/terms.html`, source/release links and the exact command. TypeSafe pricing is a verified new public documentation route, not an unverified /pricing guess.

## Intent and no-duplication rule

The high-level hero promises and material explanation are different jobs: hero says the task, recovery explains the route back. No second stays/archived lesson. Rules only in one explanation or B's editor. Requirements only in approved hero. Access/data/cost/draft/footprint facts only in the decision ledger. The optional draft paragraph's automatic-send statement is scoped to replies. Footer labels are links, not repeated paragraphs.

## Draft3 authored count

`node count-section-drafts.mjs`: A = hero104 + primary314 + shared objects56 = **474**. B = hero104 + primary274 + shared objects56 + Rules110 = **544**, including the complete proposed Rules excerpt and its eight label words. Prose ban hits: **0** for each. Shared objects include every planned Undo tab/date/count/address/tooltip/row/age, the extra zero app-icon label, one ledger title, Terminal and footer. The policy itself is 102 words and the UI labels are 8, kept separate by a newline when counting. This leaves B six words below the ceiling before any further comp strings. This is not the final rendered comp inventory. Added labels or other comp chrome must be counted or kept outside visitor content. Typeface specimens are proof material, not visitor page content.

Draft3 changes are limited to the extra app icon, consistent eight-item batch, faithful contiguous B policy excerpt, and 22-word net trim of B's operation/recovery/setup text and headings. Both five-row facsimiles remain fictional. The common decision ledger and all material access/data/billing/install facts are unchanged. A's prose and approved hero words are unchanged.
