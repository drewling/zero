# Critique of "zero" landing page

## 1. What it does / who it's for
zero is a Mac menu-bar app that uses a third-party AI model to automatically archive low-priority Gmail messages (leaving action-needed threads in the inbox) for Gmail users on Apple Silicon Macs running macOS 26+.

## 2. Confusing or contradictory content
- **"Auto-Archived 2026-09-29"** label in the hero illustration implies scheduled/automatic behavior, but the text later says **"Run zero from its menu bar to sort connected Gmail accounts"** and the app UI shows a manual **"Run zero now"** button with a **"Working…"** state. It's unclear if archiving ever happens without you triggering it.
- Naming is tangled: the product is "**zero**," the sorting model belongs to "**TypeSafe's Jev model**," and you need a "**Jev key**." The page never clarifies whether TypeSafe is the same company as zero, a required vendor, or an interchangeable backend — yet **"No zero server receives your email"** is stated as if this settles the privacy question, when the actual receiver (TypeSafe) is a separate entity.
- **"The app is free and open source under AGPL-3.0"** sits right next to **"Bring your own Jev key, billed by TypeSafe"** — "free" is true only for the software, not for using it.
- **"Optional drafts"** says Claude Code "can" draft replies, implying opt-in, but the Installer note says **"It adds Claude Code if no supported coding tool is installed"** — the installer forces this dependency onto your machine regardless of whether you use the feature.
- **"zero is not notarized by Apple"** and the installer **"may add Homebrew, Python, Node and the Google Workspace CLI"** is a significant system-level footprint for what's billed as "a Mac app" to clean an inbox — this scope is buried in secondary copy, not near the "Install zero for Mac" button.

## 3. What I'd skip / what's repeated
- **"Undo any archive"** appears in the hero, then again as a full section — fine as reinforcement, but could be one line with a link.
- **"The model can make mistakes"** / **"Check your first runs"** is stated twice (Settings section and implied in Before You Install) — redundant caution.
- **"No zero server receives your email"** is repeated in spirit across the Sorting data and Installer blocks without adding new information.
- The **"Optional drafts"** section, given it's not core to the archiving pitch, could move lower or into an appendix — it currently competes for attention with safety-critical installer info.

## 4. Missing information before deciding
- Actual price of the Jev key / TypeSafe billing (only a link, no numbers).
- What **"Open loops"** and **"Accounts"** tabs do (visible in every screenshot, never explained in text).
- Whether archiving runs on a schedule/background process or only when manually launched.
- How multiple Gmail accounts are handled (the Accounts tab implies multi-account support).
- Whether the first run scans your entire mail history or only new mail going forward.
- Uninstall process — does removing zero also remove Homebrew/Python/Node/Claude Code it installed?
- Whether attachments or full email bodies are ever transmitted, versus just the stated metadata/preview.

## 5. Install vs. leave triggers
**Product/security tradeoffs (inherent, not a presentation issue):**
- Install-worthy: reversible archiving, rules-based transparency, open source, only metadata/preview (not full email) sent to the sorting model.
- Leave-worthy: unnotarized installer, forced install of Homebrew/Python/Node/Claude Code, third-party AI model reads sender/subject/preview data, requires a paid third-party API key.

**Page-presentation problems (fixable without changing the product):**
- Critical installer disclosures are separated from the main CTA.
- Cost is not stated in concrete terms.
- Ambiguous automatic-vs-manual archiving language.
- Undefined UI tabs (Open loops, Accounts).

## 6. Who actually sorts and archives
The AI does the sorting/archiving according to your saved rules, and this is triggered when you run the app — evidenced by **"Run zero from its menu bar to sort connected Gmail accounts. AI applies your rules"** and the "Run zero now" / "Working…" states in the screenshots. It is not manual dragging. Whether it also runs unattended in the background is not stated; the **"Auto-Archived"** label suggests some automation, but no scheduling or daemon behavior is described anywhere in the text, so this is genuinely ambiguous on the page.

## 7. Undo and data leaving the Mac
**Undo:** In the Undo tab, you can restore a single email or use "Restore all" for a whole day's archived batch. The copy states **"Nothing is deleted. Find archived mail in Gmail's All Mail under a dated recovery label."** So archiving appears to just remove the inbox label/move it to All Mail with a recovery tag; restoring re-adds the inbox label.

**Data leaving the Mac:** For sorting, TypeSafe's Jev model receives sender, subject, up to a 160-character preview, whether you sent the last message, whether you've replied to that sender before, and your rules/preferences — explicitly **not** the full email body, per "No zero server receives your email." If you use the optional draft feature, the AI coding tool's provider (e.g., Claude Code's provider) additionally receives thread previews, sent-mail samples, writing preferences, and saved profile context. Beyond this, it's **unclear** whether TypeSafe is functionally the same as "zero's server" or a genuinely separate processor, and whether attachments ever leave the device — the page doesn't say, so I won't guess.

## 8. Ratings (1–5)

| Dimension | Score | Why |
|---|---|---|
| Job clarity | 4 | Headline and subhead clearly state the core function; muddied slightly by unclear zero/TypeSafe relationship. |
| Ease of following the story | 3 | Logical section order, but repeated points and unexplained UI tabs (Open loops, Accounts) break the flow. |
| Usefulness of visuals | 3 | Mockups clearly show rules, undo list, and inbox state, but everything is labeled illustrative/made-up, so it doesn't show real onboarding or real data handling. |
| Finding safety/data/requirements/cost info | 3 | A dedicated "Before you install" section exists and covers a lot, but pricing is only a link (no numbers) and the notarization/installer-scope warning is separated from the main install button. |
| Readiness to decide | 2 | Missing price, unclear automation model, unexplained tabs, and ambiguous vendor boundaries leave real open questions. |

## Top 3 presentation changes, in priority order
1. **State the actual cost** of running the sorting engine (a price range or example) directly on the page, and clarify plainly whether TypeSafe/Jev is the same company as zero or a required third-party dependency.
2. **Move the installer disclosure** (not notarized; installs Homebrew/Python/Node/Claude Code) up next to the "Install zero for Mac" button rather than only in a secondary section, since this is a major security decision point.
3. **Resolve the automatic-vs-manual contradiction** (the "Auto-Archived" label vs. the manual "Run zero now" workflow) and explain the unlabeled "Open loops" and "Accounts" tabs that appear in every screenshot but are never described in the copy.
