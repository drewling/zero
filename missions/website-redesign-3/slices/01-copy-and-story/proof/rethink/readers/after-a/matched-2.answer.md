# Critique of "zero" landing page

## 1. What it does / who it's for
zero is a Mac menu-bar app that uses an AI model to automatically archive low-priority Gmail messages (receipts, newsletters, cold sales) while leaving important threads in the inbox, aimed at Gmail users on Apple Silicon Macs who want inbox triage handled for them but with an undo safety net.

## 2. Confusing or contradictory elements
- **App form factor is unclear.** The hero shows a tiny popover ("zero … Run zero now / Working…") suggesting a lightweight menu-bar utility, but the "Undo" screen has a full four-tab window (Open loops / Accounts / Undo / Settings) that reads like a full desktop app. The page never reconciles these.
- **"No zero server receives your email" vs. the very next sentence** listing what TypeSafe's Jev model *does* receive: "sender, subject, a preview of up to 160 characters, whether you sent the latest message and whether you've replied to that sender before, your rules and learned preferences." Calling this "not your email" is a legalistic distinction that reads as evasive.
- **Undefined term "Open loops"** — this tab label appears in the Undo window but is never explained anywhere in the body copy.
- **Visible production artifact:** the watermark bar "DRAFT comp · page A · recovery-first · Draft3 · not approved" sits directly over the Inbox mock in both desktop and mobile crops (Screenshots 3, 7). This is either a review artifact left in by mistake or, if intentional, deeply confusing.
- **Simplicity claim vs. installer footprint:** the pitch is "Clean up your Gmail inbox on your Mac," yet "Before you install" reveals the installer "may add Homebrew, Python, Node and the Google Workspace CLI" and even adds "Claude Code" — a surprisingly heavy dependency chain for what's framed as a simple utility.

## 3. What I'd skip / what's repeated
- "Keep using Gmail or Apple Mail" is stated almost verbatim in the hero and again in "See what went into the archive" — redundant.
- "Nothing is deleted" / "archived mail stays searchable" is restated in both the how-it-works copy and implied again in the privacy section — could be said once, authoritatively.
- Two illustration disclaimers ("Names are made up," "Made-up mail.") do the same job twice; could be a single page-level note.
- Two separate install paths (GUI "Install zero for Mac" button and a raw `curl | bash` terminal command) are shown without explaining when to use which — one of these could be cut or clearly subordinated.

## 4. Missing information
- Actual price of the "Jev key" — only a link to "TypeSafe pricing," no number on this page.
- Whether TypeSafe retains the sender/subject/preview data it receives, and for how long.
- Whether Apple Mail users get the same labels/undo behavior as Gmail-in-browser users, or if there's lag/sync friction.
- Whether sorting runs happen automatically/on a schedule or only when the user clicks "Run zero now."
- What "Open loops" and multi-account handling ("Accounts" tab) actually do.
- Uninstall process — how to remove the installer's side effects (Homebrew, Node, Claude Code) if the user stops using zero.
- Any encryption/transport detail for data sent to TypeSafe.

## 5. Install vs. leave

**Product/security tradeoffs:**
- *Toward installing:* Nothing is permanently deleted (archives live in Gmail's All Mail under a recovery label); only metadata/short previews leave the Mac for sorting, not full email bodies; open-source (AGPL-3.0) code is auditable; drafting is opt-in and never auto-sends.
- *Toward leaving:* The installer is not notarized by Apple and silently adds a stack of developer tools (Homebrew, Python, Node, Google Workspace CLI, possibly Claude Code) — a large trust footprint for an email-sorting tool; you must bring and pay for your own third-party API key with usage-based billing; the "unverified app" Google warning; the optional drafting path sends writing samples and profile context to yet another third-party AI provider.

**Page-presentation problems (separate from the above):** the leftover draft watermark overlapping content, the unreconciled menu-bar-vs-full-app framing, and the undefined "Open loops" label all reduce confidence in the page's polish and completeness, independent of the product itself.

## 6. Who sorts and archives?
The **app itself, via an AI model, but only when a run is manually started** — not a silent background process, and not the user dragging mail. Evidence: "Start a run from zero's menu bar. The app sorts the Gmail accounts you connect," paired with the "Run zero now" / "Working…" button shown in the menu-bar popover. Dragging/clicking only appears in the *Undo* flow ("Put this email back in the inbox"), not in the sorting step. Nothing on the page describes a scheduled or always-on background daemon — the trigger shown is a manual button press.

## 7. Undoing a mistaken archive / what data leaves the Mac
**Undo:** In the Undo tab you can restore one email via its icon, or click "Restore all" to reverse an entire day's batch (e.g., "8 set aside · alex@example.com"). The page states archived mail "stays searchable in Gmail's All Mail under a dated recovery label," implying restore likely just moves the label back to Inbox — but the page never actually explains the underlying mechanism (e.g., whether this is a Gmail label swap via API), so **the precise technical undo mechanism is unclear** rather than stated.

**What leaves the Mac:** For sorting, TypeSafe's Jev model receives sender, subject, a preview of up to 160 characters, reply-status metadata, and your rules/preferences — explicitly *not* the full email body, per "No zero server receives your email." If you opt into AI-drafted replies, your chosen coding-tool provider (e.g., Claude Code) additionally receives thread previews, sent-mail samples, writing preferences, and saved profile context. Google sign-in keeps your password local ("zero never sees your password"). Retention time, encryption details, and whether Google Workspace accounts are supported despite the "Gmail only" line are **not addressed** — I won't guess at those.

## 8. Ratings

| Dimension | Score | Why |
|---|---|---|
| Job clarity | 4/5 | Hero line is clear and specific, but menu-bar-vs-full-app ambiguity costs a point. |
| Ease of following the story | 3/5 | Logical section order, but redundant reassurances, an unexplained "Open loops" tab, and a stray draft watermark disrupt the read. |
| Usefulness of visuals | 3/5 | Mockups clarify the UI shape, but everything is explicitly labeled "illustration, made up," so they can't be trusted as evidence of real behavior. |
| Finding safety/data/requirements/cost info | 4/5 | A dedicated "Before you install" section is genuinely useful and candid, but actual price and data-retention specifics are missing. |
| Readiness to decide | 3/5 | Good-faith disclosure exists, but gaps on cost, automation cadence, and undefined features leave real open questions. |

## Top 3 presentation changes, in priority order
1. **Remove or fix the leftover draft watermark** ("DRAFT comp · page A · recovery-first · Draft3 · not approved") overlapping the Inbox mock — a basic production-readiness issue that undercuts trust before any product content is even read.
2. **Clarify the operating model explicitly**: state whether sorting runs are always manual (via "Run zero now") or can be scheduled, and reconcile the small menu-bar popover with the full multi-tab Undo window so it's clear whether this is a lightweight utility or a full app.
3. **Define jargon and de-duplicate reassurances**: explain "Open loops," and say "nothing is deleted" and "keep using Gmail or Apple Mail" once each rather than repeating them across sections — tightening the copy would make room for the missing cost/retention specifics instead.
