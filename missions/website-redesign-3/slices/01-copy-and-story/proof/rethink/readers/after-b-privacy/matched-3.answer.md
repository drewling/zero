# zero — Landing Page Critique

## 1. What it does, for whom
zero is a Mac app for Gmail users that automatically archives low-priority email (newsletters, receipts, sales pitches) using AI-applied rules, while leaving actionable messages in the inbox, with a full undo/restore option.

## 2. Confusing or contradictory moments
- **"Keep using Gmail or Apple Mail"** in the hero implies Apple Mail support, but the fine print immediately below says **"Gmail only."** These sit inches apart and directly conflict.
- **"zero never sees your password"** vs. the same panel noting Google will show an **"unverified-app warning."** For a first-time user this reads as: trust us on security, but Google itself won't vouch for us yet.
- **"Free, open-source app"** sits directly under a per-token cost line ("$0.042 per million input tokens"). The app is free; using it is not exactly free. This isn't false, but the juxtaposition invites a "wait, is this free or not?" moment.
- The installer command (`curl | bash`) is presented casually with a friendly "Copy command" button, right after a warning that the app **"is not notarized by Apple"** and **"may add Homebrew, Python, Node and Google Workspace CLI."** The tone of the two elements (playful vs. alarming) doesn't match.
- **Claude Code** is introduced as "another installed AI coding tool" for optional drafts, then reappears in the Installer line as something that gets silently added during install. It's unclear if I already need a coding tool, or if the installer gives me one whether I asked or not.

## 3. What I'd skip / what's repeated
- The macOS-window chrome (title bars, scroll arrows, striped patterns) is decorative retro styling repeated on every screenshot — it adds visual noise without adding information, and I'd skip processing it after the first instance.
- "Nothing is deleted" / "Undo any archive" / "Restore all" — this reassurance is stated at least three times (hero, Undo section, Restore section). One clear statement would do.
- The "Illustration. Names are made up." / "Illustration. Made-up mail." disclaimers are useful once but repeated per-screenshot; a single upfront note would suffice.
- The Rules panel (Settings screenshot) is long and reads like actual product documentation dropped into a marketing page — I'd skim it, not read line by line, since it's just a sample of a config file I'll edit myself later.

## 4. Missing information
- Whether Apple Mail is actually supported at all (see contradiction above).
- What happens to the **historical backlog** of an inbox — does the first run archive years of existing mail at once, or only new mail going forward?
- Any indication of **speed/volume**: how many emails, how long a run takes, whether it's a one-time click or continuous background monitoring.
- What **"Open loops" and "Accounts"** tabs (visible in every settings/undo screenshot) actually do — never explained in the copy.
- What happens if I **don't** have Claude Code or any coding tool — does sorting still work without drafts? (Implied yes, but never stated plainly.)
- Any **screenshot of an error state**, an unverified-app Google warning screen, or what "checking your first runs" actually looks like when the AI is wrong.
- No mention of **uninstalling** or what the Homebrew/Python/Node/Workspace CLI additions do afterward — do they stay on my Mac forever?

## 5. Install vs. leave
**Product/security tradeoffs:**
- Install-worthy: reversible archiving (nothing deleted), rules are visible/editable, open source, cheap sorting cost, clear separation of what data goes where.
- Leave-worthy: unnotarized installer via curl|bash, silent dependency installation (Homebrew/Python/Node/Workspace CLI), Google's own unverified-app warning, and my email content (subject/sender/preview) going to a third party (TypeSafe) I've never heard of.

**Page-presentation problems (separate from the product itself):**
- The Gmail/Apple Mail contradiction would make me stop and re-read rather than trust the page.
- The casual "Copy command" button next to a scary installer warning undersells the risk.
- Undefined tabs (Open loops, Accounts) leave gaps I'd have to guess at.

## 6. Who sorts and archives the mail?
**The app, running on-demand when I click "Run zero now."** Evidence: the button is explicitly labeled "Run zero now" and appears in a dropdown/menu-bar style widget; the copy says "Use Run zero now to sort connected Gmail. AI applies your rules." There's no language describing a persistent background daemon or scheduled job — it reads as a manual trigger, not an automatic background watcher. (The "Auto-Archived 2026-09-29" label is ambiguous, but nothing on the page describes a schedule, interval, or "runs automatically every X hours" — so I take "auto" to mean "the AI did the sorting when I ran it," not "it runs without me.")

## 7. Undo and data flow
**Undo:** In the Undo tab, I restore one email or click "Restore all" for a whole day's batch. Nothing is deleted — archived mail stays in Gmail's All Mail under a dated recovery label. This is reasonably clear and specific.

**What leaves the Mac:** This is only partly clear.
- To TypeSafe (for sorting): sender, subject, up to 160-character preview, reply-status flags, my rules/preferences.
- To my coding tool's provider (only if I use optional drafts): thread previews, sent-mail samples, writing preferences, saved profile context.
- The page explicitly says neither dataset goes to "zero's servers" — but it never says whether zero *has* servers of its own for anything else (e.g., license checks, crash reports, telemetry). That gap is unexplained, so I won't guess further.

## 8. Ratings

| Category | Rating | Why |
|---|---|---|
| Job clarity | 4/5 | Hero line is clear and specific; only docked for the Gmail/Apple Mail contradiction. |
| Ease of following the story | 3/5 | Sequence (install → before you install → choose rules → undo → install again) is logical, but the repeated "nothing is deleted" beats and undefined tabs break flow. |
| Usefulness of visuals | 2/5 | Screenshots are labeled as illustrations with made-up data, so they demonstrate UI layout but don't show real outcomes, error states, or the unverified-app warning that's discussed in text. Decorative retro chrome doesn't add information. |
| Finding safety/data/requirements/cost info | 4/5 | The "Before you install" section is genuinely thorough and well-organized in a single, scannable panel — best part of the page. |
| Readiness to decide | 3/5 | Enough is disclosed to make an informed risk decision, but backlog behavior, uninstall process, and Apple Mail status remain open questions I'd need answered first. |

---

## Top 3 presentation changes (priority order)
1. **Resolve the Gmail/Apple Mail contradiction.** Either state plainly "Gmail only, Apple Mail as a Gmail client is fine" or remove "Apple Mail" from the hero — right now it reads as false advertising to a new visitor.
2. **Match tone to risk in the installer section.** The curl|bash command and casual "Copy command" button need visual weight (warning color, confirmation step) consistent with the adjacent "not notarized," "adds Homebrew/Python/Node," and "unverified-app warning" disclosures.
3. **Define every tab and behavior referenced in screenshots** (Open loops, Accounts, whether sorting is manual-only or scheduled, what happens to an existing backlog on first run). Undefined UI elements repeated across six screenshots erode trust more than any single missing detail.
