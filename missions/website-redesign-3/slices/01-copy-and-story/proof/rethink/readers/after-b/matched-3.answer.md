# Zero — Critique

## 1. What it does / who it's for
Zero is a Mac menu-bar utility that connects to your Gmail account, uses a third-party AI model to auto-archive email that doesn't need a reply (receipts, newsletters, sales pitches), and leaves actionable threads in your inbox — with a reversible undo — aimed at Gmail users on Apple Silicon Macs who want a cleaner inbox without leaving Gmail or Apple Mail.

## 2. Confusing or contradictory elements
- **"Read your connected Gmail in Gmail or Apple Mail"** (tagline under "Before you install") sits oddly next to the mocked-up "Inbox" window inside the zero app itself (Screenshot 1/3), which looks like its own mail-reading UI. It's unclear whether zero has its own interface for browsing mail or whether you only ever look at mail in Gmail/Apple Mail while zero works invisibly in the background.
- **"zero never sees your password"** vs. **"TypeSafe's Jev model receives sender, subject, a preview... your rules and learned preferences."** The page draws a fine distinction between "no zero server" and a third party (TypeSafe) receiving your data — technically consistent, but easy to misread as "nothing leaves your Mac."
- Visible design-QA artifacts baked into the screenshots: **"DRAFT comp · page B · risk-first · Draft3 · not approved"**. This isn't just a presentation nit — it actively appears as page text and undermines confidence this is a finished, reviewed page.
- Three separate install paths are offered (**"Install zero for Mac"** button, **GitHub Releases**, and a **curl | bash** terminal command) with no explanation of which to use or why they differ.

## 3. What I'd skip / what's repeated
- The hero "Inbox" mockup (Screenshot 1/3) adds little beyond the tagline — it's a static list of 4 emails, not a before/after of sorting in action, and it's explicitly "Illustration. Names are made up."
- "Nothing is deleted / fully reversible" is stated three times (hero copy, the Rules screenshot subtitle "Archive everything else (reversibly)", and the dedicated "Restore archived mail" section). One clear statement plus the Undo screenshot would suffice.
- The "Before you install" tagline restates the hero sentence ("Keep using Gmail or Apple Mail") without adding new information.

## 4. Missing before I could decide
- Actual dollar cost — the page defers entirely to an external "TypeSafe pricing" link.
- Whether zero runs automatically/on a schedule, or *only* when you click "Run zero now."
- How to uninstall zero and the dependencies it installs (Homebrew, Python, Node, Google Workspace CLI).
- Whether restored mail can be re-archived on a later run, or is permanently exempted.
- Any indication of maturity/stability: version number, changelog, how long it's existed.
- Scope of "your email" scanned — all mail, unread only, how far back.
- Exact permissions the installer/app requests beyond Google OAuth.

## 5. What would make me install vs. leave

**Product/security tradeoffs:**
- *For:* Open source (AGPL-3.0), OAuth-only sign-in (no password capture), limited metadata sent for sorting (sender/subject/160-char preview, not full email bodies), drafts never auto-send.
- *Against:* App is **not notarized by Apple**; installer uses a **curl-pipe-bash script** that adds Homebrew, Python, Node, Google Workspace CLI, and possibly a whole coding-tool agent (Claude Code) just to archive email; the "unverified app" Google warning is a real friction/trust signal; optional AI drafts send a broader dataset (thread previews, sent-mail samples, writing preferences, saved profile context) to yet another third party.

**Page-presentation problems (separate from the product):**
- Leftover draft watermarks make the page look unshipped.
- Ambiguity about zero's own UI vs. Gmail/Apple Mail.
- Pricing hidden behind an external link with no ballpark figure.

## 6. Who actually sorts and archives the mail?
**The AI model, triggered manually by you.** Evidence: the "Choose what needs to stay" section states "**Run zero from its menu bar** to sort connected Gmail accounts. **AI applies your rules.**" and the mockup shows a **"Run zero now"** button in the menu-bar dropdown. Nothing on the page describes a background daemon, schedule, or continuous process — it appears to run only when invoked. You don't drag anything yourself except to **restore** items via the Undo tab.

## 7. Undo and data leaving the Mac
**Undo:** In zero's **Undo** tab, click **"Put this email back in the inbox"** for a single message, or **"Restore all"** for a whole day's batch. The page states archived mail is never deleted — it's moved to a dated recovery label inside Gmail's **All Mail**, and restoring reverses that labeling.

**What leaves the Mac:** For sorting — sender, subject, a preview (up to 160 characters), whether you sent the latest message, whether you've replied to that sender before, and your rules/learned preferences, sent to TypeSafe's Jev model. If you enable optional AI drafts, a second third party (your chosen coding tool's provider) additionally receives thread previews, sent-mail samples, writing preferences, and saved profile context.

**Unclear, not invented:** Whether attachments, full thread history, or metadata like CC/recipient lists are included; what exactly "learned preferences" accumulate over time is not specified.

## 8. Ratings

| Dimension | Score | Why |
|---|---|---|
| Job clarity | 4/5 | Hero line is clear and consistently repeated; slight ambiguity from the Inbox-mockup/"read in Gmail" tension. |
| Ease of following the story | 3/5 | Logical section order, but repeated "reversible" messaging and draft watermarks disrupt flow and trust. |
| Usefulness of visuals | 3/5 | Rules and Undo mockups are concrete and helpful; the Inbox mockup is redundant, and no before/after of sorting is shown. |
| Finding safety/data/requirements/cost info | 3/5 | "Before you install" is the strongest section (dedicated boxes for sign-in, data, cost, drafts, installer) — but dollar cost is deferred externally and installer risk isn't flagged as a tradeoff, just stated. |
| Readiness to decide | 3/5 | Good data-flow disclosure, but missing pricing, run-schedule behavior, uninstall process, and maturity signals leave real gaps before installing an unnotarized app on your Mac and Gmail account. |

## Three most important presentation changes, in priority order
1. **Remove the leftover production/draft watermarks** ("DRAFT comp · page B · risk-first · Draft3 · not approved") — as shown, they make the page look unreviewed and undercut trust before any product evaluation even starts.
2. **Clarify where you actually read/interact with mail day to day** — resolve whether zero has its own Inbox UI or whether you only ever use Gmail/Apple Mail while zero works in the background; the current mockup contradicts the stated model.
3. **State actual cost on the page and clarify run behavior** — show a real price/range instead of only linking to TypeSafe pricing, and explicitly say whether zero runs automatically or only when you click "Run zero now."
