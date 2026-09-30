# zero — Landing Page Critique

## 1. What it does, for whom
zero is a Mac menu-bar app that connects to your Gmail, uses an AI ("Jev," billed through a service called TypeSafe) to archive email you don't need to act on, and lets you undo any archive — aimed at Mac users with Gmail who want a cleaner inbox without losing anything permanently.

## 2. Confusing or contradictory
- **The name of the sorting engine is inconsistent and unexplained.** The page calls it "Jev key," "Jev 1.13," and "TypeSafe" as if these are self-evident, but never says what Jev *is* (a model? a proxy service? a company?). A first-time reader has no idea what they're actually trusting with metadata.
- **"Free, open-source app" sits directly next to a paid, metered cost** ("$0.042 per million input tokens"). The word "Free" is doing a lot of work it doesn't earn — the app is free, the sorting is not, and the two facts are crammed into one line ("Sorting cost... Free, open-source app (AGPL-3.0)") in a way that reads like it's describing the same thing.
- **"zero never sees your password" vs. "zero is not notarized by Apple. May add Homebrew, Python, Node and Google Workspace CLI."** The page reassures you about password safety in the same breath as admitting the installer silently adds multiple unrelated developer tools to your Mac. These two trust signals point in opposite directions and are never reconciled.
- **"Claude Code is added only if no supported coding tool is installed"** — this is presented under "Installer," but the "Optional drafts" section earlier implies drafting is optional and user-initiated. If the installer can *add* Claude Code automatically, "optional" is misleading — it sounds like the installer decides this for you, not you.
- The hero screenshot shows a folder icon labeled "Auto-Archived 2026-09-29" sitting loose next to the Trash icon, with no explanation of what that folder is or how it relates to "archive" vs. "trash" — visually it looks like archived mail might be heading toward Trash.

## 3. What I'd skip / what's repeated
- "Nothing is deleted" / reversibility is stated at least three times (hero copy, Choose-what-stays section, Restore section) — one clear statement would do.
- "zero never sees your password" and "No zero server receives your email" are two separate reassurances in two different sections that could be merged into one trust block.
- The illustration disclaimers ("Illustration. Names are made up," "Illustration. Made-up mail.") repeated twice each — fine to have once per image, but they interrupt reading rhythm without adding new information.

## 4. Missing before I could decide
- What "Jev" actually is (model name/vendor) and who TypeSafe is as a company.
- What happens if I *don't* have a supported coding tool and don't want Claude Code installed — can I decline the auto-install, or is it forced?
- Any real number for how much sorting typically costs per month (token pricing without a usage estimate is meaningless to a non-technical buyer).
- What "learned preferences" (sent to TypeSafe) actually contain — is my writing/behavior data retained indefinitely?
- Whether the Google "unverified app" warning is a one-time click-through or a recurring friction point.
- Any mention of support, update frequency, or how mistakes/misclassifications get reported or fixed beyond manual undo.

## 5. Install vs. leave
**Would make me install (product/security):** Clear statement that email content itself never leaves my Mac to zero's own servers, an easy undo, and a visible per-sender rule set I can edit.
**Would make me leave (product/security):** Non-notarized installer that silently adds Homebrew/Python/Node/CLI tools; unclear ownership of the "Jev/TypeSafe" data pipeline; automatic installation of a coding agent (Claude Code) I didn't ask for.
**Page-presentation problems (separate from the above):** unexplained jargon ("Jev," "TypeSafe"), the free/paid conflation, the ambiguous auto-archive folder icon in the hero graphic, and reversibility being stated three times while installer risk is stated once, in small print.

## 6. Who actually sorts and archives the mail
**The app, triggered by you, using a remote AI.** Evidence: "Use **Run zero now** to sort connected Gmail. AI applies your rules." This is a manual trigger (a menu-bar button), not a silent background daemon — there's no mention of a schedule, timer, or "runs automatically every X hours." The actual archiving decision is made by the AI service (Jev/TypeSafe), not by you dragging items, and not by an on-device process — the "Sorting data... Sent to TypeSafe (Jev)" line confirms an external service does the classification.

## 7. Undo and data leaving the Mac
**Undo:** In the Undo tab, either restore a single email or use "Restore all" for an entire day's batch; archived mail also remains manually recoverable in Gmail's All Mail under a dated label even without opening zero. This is clearly explained.
**What leaves the Mac:** For sorting — sender, subject, up to 160 characters of preview, latest-message/reply-history flags, and your rules/preferences, sent to TypeSafe. The page explicitly says "No zero server receives your email," but this doesn't mean *no data* leaves the Mac — it means email content doesn't go to *zero's own* server; it still goes to TypeSafe, a third party. If you use optional AI drafting, additional data (thread previews, sent-mail samples, writing profile) goes to your coding tool's provider (e.g., Anthropic via Claude Code). **What's unclear:** how long TypeSafe retains this data, whether it's used to train anything, and whether the 160-character preview could include sensitive content (a number, a name, a snippet of a contract) — the page doesn't say.

## 8. Ratings (1–5)

| Dimension | Score | Why |
|---|---|---|
| Job clarity | 4 | Hero line is clear and specific ("keeps what you need, archives the rest"), but the mechanism (AI + third-party billing) isn't previewed until much later. |
| Ease of following the story | 3 | Logical section order, but jargon ("Jev," "TypeSafe") breaks flow, and reversibility is repeated while risk facts are compressed. |
| Usefulness of visuals | 3 | The mock inbox and Undo screen usefully show the mechanic, but the loose "Auto-Archived" folder icon near Trash is genuinely confusing, and illustrations are clearly labeled fake, which limits their evidentiary value. |
| Finding safety/data/cost info | 3 | It's all present in one dense "Before you install" panel — good that it's consolidated, but density and unexplained vendor names hurt scannability. |
| Readiness to decide | 3 | Enough is disclosed to know the *shape* of the tradeoffs (third-party AI, metered cost, non-notarized installer) but not enough to size the actual cost or fully understand what happens to preview text long-term. |

## Top 3 presentation changes, in priority order
1. **Define "Jev" and "TypeSafe" in one sentence the first time they appear** — right now the page assumes prior knowledge of vendors nobody has heard of, which undermines trust in an otherwise transparent-sounding privacy section.
2. **Clarify the installer's automatic behavior versus user choice** — explicitly state whether adding Homebrew/Python/Node/Claude Code requires user confirmation or happens silently, since this currently contradicts the "optional drafts" framing.
3. **Fix or caption the hero's "Auto-Archived" folder icon** — as shown, it visually implies archived mail sits next to Trash with no distinction, which contradicts the "nothing is deleted" promise made everywhere else on the page.
