# Critique of "zero" Landing Page

## 1. What it does / who it's for
It's a Mac app that connects to your Gmail account, uses an AI model to automatically archive emails it judges unimportant (newsletters, receipts, cold sales) while keeping ones needing action, for Mac users who want a cleaner inbox without switching email clients.

## 2. Confusing or contradictory elements

- **"Undo any archive"** (hero) vs. **"Nothing sends automatically"** (info table) — the hero implies full automation of archiving, but the mail-sorting itself *is* automatic (that's the whole feature), while only *replies* are manual. This is muddled because "automatically" is used for one action (sending) but not clarified for the other (archiving), which could confuse readers about what runs unattended.
- **"zero never sees your password"** followed immediately by **"Google may show an unverified-app warning because zero hasn't completed its review."** These sit side by side but pull in opposite emotional directions — reassurance, then a red flag — with no explanation of what "review" means or when/if it will complete.
- **Claude Code appears twice for different jobs**: the installer silently adds "Claude Code" as a dependency (Install section), then later Claude Code is offered as an *optional* reply-draft tool ("Claude Code, or another AI coding tool you already use"). It's unclear if the installed Claude Code and the optional one are the same thing, or why a coding tool is required infrastructure for an email app at all.
- **Two different AI vendors, unexplained relationship**: "TypeSafe's Jev model" sorts mail; "Claude Code" (or "another AI coding tool") drafts replies. No visual or text ties these together or explains why an email utility depends on a coding assistant.
- **"Run zero now"** is bolded like a button both in the "How it works" copy and the Install instructions, but no screenshot shows this button in an actual app UI — only mocked Inbox/Stays/Archived/Undo windows are shown, never the control surface itself.

## 3. What I'd skip / what's repeated

- The **"See what stays / See what gets archived"** section repeats the Rules section's content almost exactly (colleague question stays, newsletter archived, payment problem stays, receipt archived) — this pattern is stated three separate times across two sections in nearly identical form.
- The **Stays/Archived mock windows** (Screenshot 4) add little beyond what the bullet list in Rules already says — same four "stays" examples, same category types for archived.
- The **Undo mock window** with greeked/placeholder text (Screenshots 5-6, 12) is pure visual filler — it shows redacted bars, not real content, so it's decorative rather than informative and could be cut or replaced with an annotated real screenshot.

## 4. Missing information before deciding

- What "Run zero now" actually looks like — is it a button in a menu bar app, a dock icon, a window? No real UI is shown.
- Whether sorting runs continuously in the background or only when manually triggered each time.
- What the "Jev key" costs — no pricing figure, tiers, or estimate of per-run cost is given.
- What data the Google Workspace CLI or Homebrew/Python/Node dependencies access or send — the installer note flags them but doesn't explain their role.
- Whether zero works with multiple Gmail accounts simultaneously, and how conflicts/rules apply per-account.
- What happens to the unverified-app warning practically — do I need to click through a scary Google screen, and is that safe?
- No screenshot of Settings → Rules, so I can't see how customizable/granular rule-editing actually is.

## 5. Install vs. leave

**Product/security tradeoffs:**
- Would install if: sorting logic is genuinely reversible (as claimed), data sent to TypeSafe is minimal (sender/subject/preview only, as stated), and I trust an unreviewed/unverified Google app.
- Would leave because: the installer adds several unrelated tools (Homebrew, Python, Node, Google Workspace CLI, Claude Code) just to sort email — that's a large, unaudited attack surface for a single-purpose utility. Also "not notarized by Apple" plus "unverified by Google" together is two separate trust warnings, which is a lot of unverified trust to extend to an inbox-altering tool.

**Page-presentation problems (not product flaws):**
- I'd leave the *page*, not necessarily the product, because I can't see the actual running app (no real screenshots, only mockups), so I can't evaluate the real UI/UX quality before installing.

## 6. Who sorts and archives the mail?

**You, by manually triggering it** — the app does not appear to run continuously in the background. Evidence: "Click **Run zero now** on your Mac to sort the Gmail accounts you connect" (How it works section), and again in Install: "Choose **Run zero now** and review the results." Both instances frame this as a deliberate, user-initiated action, not an automatic background process. There's no mention of a schedule, daemon, or menu-bar auto-run toggle anywhere on the page.

## 7. Undo process and data leaving the Mac

**Undo:** Reasonably clear. Archived mail gets a "dated recovery label" and stays in Gmail's All Mail. In zero's Undo tab, you can restore one email or click "Restore all" for an entire day's batch. This is stated plainly enough to act on.

**What leaves the Mac:** Partially clear, but incomplete. The page states sorting sends "the sender, subject, a short preview, reply-history signals, your rules and learned preferences" to TypeSafe's Jev model, and explicitly says "No zero server receives your email." However, it does **not** define what "reply-history signals" or "learned preferences" actually contain — these could include more email content than implied by "short preview." I would not assume the full email body is excluded with confidence; the page's own vagueness here means I can't say precisely how much of my email data leaves the Mac. For reply drafts, a *second* recipient (Claude Code or another coding tool's provider) gets "thread previews, sent-mail samples, writing preferences and saved profile context" — again undefined in scope. So: unclear, and I won't guess further.

## 8. Ratings (1–5)

| Category | Score | Reasoning |
|---|---|---|
| Job clarity | 4 | Hero line is clear and repeated consistently; only slightly muddied by the automation-vs-manual reply ambiguity. |
| Ease of following the story | 3 | Sections repeat the same stays/archived example three times, which slows the read without adding new info. |
| Usefulness of visuals | 2 | All mockups are explicitly labeled "illustration"/"made up," and the Undo screenshot is entirely greeked placeholder text — none show the real app. |
| Finding safety/data/cost info | 4 | The "Know what you connect, share and pay for" table is well-organized and put in one place — best section on the page. |
| Readiness to decide | 2 | No real UI, no concrete pricing figure, unclear background-vs-manual operation until inferred from repeated phrasing, and unexplained dependency stack (Node/Python/Claude Code) leaves too many open questions. |

---

## Top 3 presentation changes, in priority order

1. **Show real product screenshots**, not illustrations/mockups/greeked placeholders — I cannot assess an app I'm never shown running.
2. **Consolidate the three repeated stays/archived examples** into one clear explanation instead of restating the same four example senders and categories across multiple sections.
3. **Explain the installer's non-obvious dependencies** (Homebrew, Python, Node, Google Workspace CLI, Claude Code) — state *why* each is needed for an email-sorting tool, right where they're listed, instead of just naming them with a "read the installer" deflection.
