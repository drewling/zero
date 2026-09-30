# Critique: "zero" (Mac Gmail inbox utility)

## 1. What it does / who it's for
It's a Mac menu-bar app that uses an AI service to auto-sort your connected Gmail inbox — archiving mail that doesn't need action and leaving mail that does — for a Gmail user comfortable running an unnotarized, terminal-installed tool and paying a small per-token AI fee.

## 2. Confusing or contradictory elements

- **"Keep using Gmail or Apple Mail."** vs. the requirements line directly below the hero: **"Apple Silicon. macOS 26 or later. Gmail only."** The hero implies Apple Mail is a supported client; the fine print says only Gmail accounts work. It's unclear if "Apple Mail" here just means "you can still *view* mail there" or if it's a real integration.
- **"Run zero now"** (manual button, "Working…" state) is the only sorting trigger described in the text, yet the hero illustration shows a folder labeled **"Auto-Archived 2026-09-29"** — implying scheduled/background archiving that's never explained. The page never says whether zero runs continuously, on a timer, or only when clicked.
- **Unexplained proper nouns**: "TypeSafe," "Jev," and "Jev key" are used as if the reader already knows them (e.g., "Your Jev key, billed by TypeSafe. Jev 1.13: $0.042 per million input tokens"). There's no plain-language sentence explaining what Jev is (a model? a routing service?) or who TypeSafe is, even though this is the company handling your email subject lines and previews.
- **"Free, open-source app (AGPL-3.0)"** sits directly beside a per-token billing line — "free" and "billed" in the same paragraph, with no total/typical monthly cost estimate to reconcile them.
- The installer line — **"May add Homebrew, Python, Node and Google Workspace CLI. Claude Code is added only if no supported coding tool is installed"** — silently installs a specific Anthropic product as a side effect, which is unexpected for someone who just wanted an inbox sorter.

## 3. What I'd skip / what repeats
- The "undo/nothing is deleted" reassurance appears three times (hero subhead, "Choose what needs to stay," and the whole "Restore archived mail." section) — could be stated once, prominently, and referenced elsewhere.
- The two nearly identical mock-inbox illustrations (hero and "Restore archived mail") show the same made-up senders/format; one could be cut without losing information.
- The "Ready to install?" section repeats install mechanics already implied by the top button ("Install zero for Mac" vs. the curl command) — two install paths shown late, without saying which one is recommended or how they differ.

## 4. Missing before I could decide
- Whether sorting is a one-click manual action or something that runs unattended/on a schedule.
- What "TypeSafe" and "Jev" actually are (company, model, jurisdiction).
- A real-world monthly cost estimate for a typical inbox (only a per-token rate is given).
- Whether attachments or full email bodies are ever transmitted, or only the stated 160-character preview.
- How to uninstall, and what happens to the Homebrew/Python/Node/CLI components it adds.
- Whether multiple Gmail accounts are supported.
- Any independent security review, given it's explicitly not Apple-notarized.

## 5. What would make me install / leave

**Install factors:**
- Open-source (AGPL-3.0), reversible archiving, Gmail OAuth (no password shared), explicit statement that data doesn't go to zero's own servers, and a written, editable rules file rather than a black box.

**Leave factors (product/security):**
- Not notarized by Apple, installed via `curl | bash`, and it silently adds several system tools (Homebrew/Python/Node/Google Workspace CLI/possibly Claude Code) — a meaningfully large attack surface for an inbox sorter.
- Data about my email (sender, subject, previews) goes to a third party ("TypeSafe") I know nothing about.

**Leave factors (page presentation, separate from the product itself):**
- Unexplained vendor names, the Gmail/Apple Mail contradiction, and the manual-vs-automatic archiving ambiguity would make me distrust the page's precision even if the product itself is fine.

## 6. Who sorts and archives the mail?
Based on the page, **the app does it after you start it** — the primary described mechanism is the **"Run zero now"** button, with the text "AI applies your rules" describing what happens once you click it, and a "Working…" status shown mid-run. Nothing on the page describes drag-and-drop by the user. However, the **"Auto-Archived 2026-09-29"** folder label in the hero illustration contradicts a purely manual, click-to-run model and suggests some background/scheduled process — this is not explained in the text, so I can't say for certain the process is manual-only.

## 7. Undo mechanism and what leaves the Mac

**Undo:** In the app's **Undo** tab, you can restore a single email (via the restore icon next to each item) or an entire day's batch at once with **"Restore all."** The page states archived mail is never deleted — it's kept in Gmail's **All Mail** under a dated recovery label, so restoring is described as reversible through the app UI.

**What leaves the Mac:** For sorting, **sender, subject, a preview of up to 160 characters, whether you sent the latest message, whether you've replied before, and your rules/preferences** go to TypeSafe (Jev). If you opt into AI-drafted replies, **thread previews, sent-mail samples, writing preferences, and saved profile context** go to your separate AI coding tool's provider. The page explicitly says neither destination is zero's own servers.

**Unclear, not invented:** Whether full email bodies or attachments are ever transmitted (only "a preview of up to 160 characters" is stated), and exactly how the archive/restore action talks to Gmail (API mechanics aren't shown) are not specified on the page.

## 8. Ratings (1–5)

| Dimension | Score | Why |
|---|---|---|
| Job clarity | 4 | The core pitch is clear and stated early, minus the Gmail/Apple Mail wording clash. |
| Ease of following the story | 3 | Logical section order, but safety-critical info is buried mid-page and key facts repeat rather than build. |
| Usefulness of visuals | 3 | Mock UI screens clearly show real screens and are honestly labeled as illustrations, but two are near-duplicates and don't add new information. |
| Finding safety/data/requirements/cost info | 3 | A dedicated "Before you install" section covers a lot, but relies on unexplained vendor names and gives no real-world cost total. |
| Readiness to decide | 2 | Manual-vs-automatic sorting is unresolved, vendor trust can't be assessed, and there's no cost estimate or uninstall path. |

## Three most important presentation changes, in priority order

1. **Resolve the automatic-vs-manual contradiction and the Gmail/Apple Mail claim.** State plainly whether archiving only happens when I click "Run zero now" or also runs in the background/on a schedule, and clarify that only Gmail accounts are actually sorted (drop or explain the Apple Mail mention).
2. **Define "TypeSafe" and "Jev" in plain language on first use**, since the entire data-sharing trust argument rests on an unexplained third party handling my email metadata.
3. **Surface a one-line safety/cost summary near the top install button** (not notarized, curl-installed, adds system tools, real-world monthly cost) instead of leaving it to a separate mid-page section — so the decision-relevant risk is visible before, not after, someone clicks "Install."
