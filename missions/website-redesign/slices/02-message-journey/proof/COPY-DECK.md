# Slice 02: copy deck, claims ledger and funnel diagnosis

Author: design-lead@zero (claude-opus-5-5), 2026-09-28. Status: **for mission-owner wording approval. The builder must not start until approved.**
Final visitor copy: `proof/copy-cleansed.md`. It maps onto the approved mockup sections (slice 01 `proof/mockup/index.html`).

## 1. Funnel diagnosis (/funnels, Hook-Story-Offer)

This is a product-install funnel with one rung: visitor, then install, then first run. There is no lead capture, upsell, urgency or email field. The plan rules them out, and zero has nothing to sell after install.

| Stage | Decision | Why |
| --- | --- | --- |
| **Who** | A Mac user whose Gmail has silted up, where a reply someone is waiting for is buried under receipts and cold outreach. They are wary of letting AI touch mail. Default heuristic: the founder, before zero. | README audience plus PRODUCT.md intent. No persona data exists, so this is a hypothesis, not research. |
| **Hook** | Board headline **KEEP THE MAIL THAT NEEDS YOU.** It states the outcome plainly, and the tiles are the pattern interrupt. The curiosity gap is "how does it decide?", which the next section answers. | HSO: the headline buys attention, and the outcome stays plain (third-grade rule). |
| **Story (false belief to rewrite)** | The belief is "letting an AI clean my inbox means losing something important." The rewrite comes in three beats. First, the real app screenshot: it is a short list, not magic. Second, the default-rules board shows what stays. Third, **Nothing is deleted**: a dated label, All Mail, and Undo. Honesty, including "it gets things wrong sometimes", does the persuading, not superlatives. | The objection that stops this audience is fear of loss, not price. |
| **Offer** | Free, open source app. The costs are stated next to the action: a Jev key billed by TypeSafe, Apple Silicon, macOS 26+. The CTA is **Install zero for Mac**, with **Read the installer first** as the trust valve. | Raycast pattern observed: requirements directly under the button. |
| **First action** | Anchor to the install band, then copy the command, then run it in Terminal. | One CTA label is repeated in the header, hero and install band, and it always points to `#install`. |
| **Activation** | Steps 2-4 end on **Run zero now**, then review, then set **Daily routine**. The copy tells the user to check first runs before scheduling. | Setting a schedule before trust exists is the activation risk. |

**Weakest link (predicted):** the install step itself. `curl | bash`, not notarized, possible Homebrew and developer tools, and Google's unverified warning add up to the highest-friction moment. The copy puts every warning **before** the command and offers the script and GitHub Releases as alternatives. It does not hide the friction. No analytics exist, so this is a clarity diagnosis, not a conversion claim.

## 2. Section-by-section copy notes

- **Hero lead:** "zero is a Mac menu-bar app for Gmail. It keeps conversations that still need your attention and archives the rest. Archived mail stays in Gmail. You can put it back." That is three short sentences, with the category, the mechanism and the safety in the first 30 words.
- **Requirements list** under the CTA: Needs / Sorting / Price. Cost is the third row, so it can't be missed.
- **What stays:** the board rows paraphrase `keep-policy.md` defaults. "Archived" replaces the slice-01 mockup's "Set aside" on the board, because visitors know "archive" from Gmail. "Set aside" is the app's toast wording, and the mockup can use either. Recommendation: **Archived** on the board, for plain language.
- **Nothing is deleted:** the label is shown as a format only.
- **Before you install:** six rows (Your Mac, Gmail, Jev key, Your mail, Replies, The app). Every caveat from the plan is present.
- **FAQ:** adds "What does it cost?", which is billing truth in one place.

### FAQ "Does my email stay on my Mac?" (scrutinized per main-lead)

Final: *"No. zero runs on your Mac, but it sends relevant thread text to TypeSafe's Jev to decide what to keep. If you ask for a reply draft, that text also goes to the AI provider you chose. Both handle it under their own terms. The zero project doesn't run a server that receives your email. Your Google sign-in tokens stay on your Mac. The privacy policy lists what else zero stores there."*

- The answer starts with **"No"**. Draft 1's "Not all of it" softened a real transfer, so it was replaced.
- Token clause, retained and explicit: "Your Google sign-in tokens stay on your Mac." Primary citation: privacy.html:103. Corroborated by lib/keeper_server.py:47-49 and macapp/Sources/main.swift:729-732 (gws uses per-account keyring credentials, never a global token). main-lead supplied these at 04:59Z, and I re-read them myself.
- "No server" is scoped to "a server that receives your email" (README wording). It is not a broad privacy promise.

## 3. Claims ledger

Authority order: **app source > README > install-zero.sh > privacy.html**. PRODUCT.md is not authoritative. App source outranks README for UI strings, because the README was stale on "Daily schedule" and "AI engine" when audited (fixed by main-lead at cbb4073).

| # | Visitor claim (copy-cleansed.md) | Source |
| --- | --- | --- |
| 1 | Mac menu-bar app for Gmail. Keeps what needs attention, archives the rest | README "What zero does" |
| 2 | Archived mail stays in Gmail, can be put back | README "Safety and data"; PanelView.swift:2774 "Only labels are removed… every thread stays in All Mail" |
| 3 | Apple Silicon, macOS 26+. The installer stops otherwise | install-zero.sh:64-79 (`sw_vers` ≥26, `uname -m` = arm64, `die`) |
| 4 | Your own Jev key, required. TypeSafe bills and rate-limits | README "Before you install", "Safety and data" |
| 5 | Free and open source, AGPL-3.0 | README, LICENSE |
| 6 | Rules in plain English, editable in Settings → Rules | PanelView.swift:1320 `SettingsHeader("Rules")`; keep-policy.md |
| 7 | It gets things wrong sometimes. Check the first runs | README "The model can be wrong. Review your first few runs" |
| 8 | Board rows (reply, failed payment, deadline stay; receipts, newsletters, cold sales, last-from-you archived) | keep-policy.md defaults; labelled illustration, not a guarantee |
| 9 | Waiting on you, Open loops | PanelView.swift:353; KeeperModel.swift tab |
| 10 | Removes Inbox label, adds dated recovery label `🗄️ Auto-Archived YYYY-MM-DD` | lib/inbox_zero.py:37, 225-232 |
| 11 | Undo tab, Restore all | PanelView.swift:1082 `Button("Restore all")` |
| 12 | Sign in from the app. zero never sees the password | README First run 1 |
| 13 | Google may warn the app is unverified. Verification not completed | README First run 1 |
| 14 | Thread text goes to Jev. Draft text goes to the chosen provider | README "Safety and data"; privacy.html:74, 97 |
| 15 | The project doesn't run a server that receives your email | README "Safety and data"; privacy.html:73 |
| 16 | Send only on **Send reply** | PanelView.swift:2587; README First run 3 |
| 17 | Drafts use the account behind your agent CLI | README "Safety and data" |
| 18 | Ad-hoc signed, not notarized, not in the App Store | README "Before you install" |
| 19 | The installer may add Homebrew, Python, Node, gws, Claude Code | install-zero.sh:5, 94-108; README |
| 20 | The installer checks the SHA-256 before installing | install-zero.sh:35-40; README |
| 21 | Connect your first inbox | OnboardingView.swift:82 |
| 22 | Settings → Sorting engine, Get a key, Save | PanelView.swift:1618, 1629; README First run 2 |
| 23 | Run zero now | PanelView.swift (footer button); README First run 4 |
| 24 | Settings → Daily routine | PanelView.swift:1396; README matches since cbb4073 (said "Daily schedule" when audited) |
| 25 | Multiple accounts together in Open loops | README; screenshot shows 2 accounts |
| 26 | Google sign-in tokens stay on your Mac | privacy.html:103 (primary); lib/keeper_server.py:47-49; macapp/Sources/main.swift:729-732 |
| 27 | "When zero sorts a conversation…" (scoped; no every-thread claim) | README "checks your connected Gmail inboxes"; main-lead 04:41Z/05:01Z |
| 28 | "The recovery label is dated for the day" | lib/inbox_zero.py:225-232 (`f"{user_label} {today}"`, so same-day runs share one label) |

**Excluded:** "once a day", "every thread", "Nothing leaves your account", "never goes through one of ours" (broad), all metrics, logos, testimonials and conversion claims.

## 4. Linter and cleanse evidence

| Step | Result | File |
| --- | --- | --- |
| Lint draft 1 (deslop.py) | **5/5 CLEAN**, 921 words | `lint-draft-1.txt` |
| Rival-family cleanse (`cleanse.sh` via codex CLI; writer is Anthropic, cleanser is OpenAI family) | Ran, exit 0, 921 → 901 words | `copy-cleansed.md`, `cleanse-notes.txt` |
| Cleanse fact check | Diffed line by line. Only phrasing changed: no facts added or removed, and the "can sort wrongly" warning kept | this section |
| Post-cleanse claim fixes (main-lead 04:58-05:00Z) | Server wording scoped. Token clause re-added with citations. "Daily routine" kept (app source) | `copy-cleansed.md` |
| Re-lint final | **5/5 CLEAN** | `lint-final.txt` |

## 5. Long mobile yellow: tonal break (builder)

Already approved in slice 01 DESIGN-BRIEF §7. Use ticket-stock off-white `#F6F1E4` for **Before you install** and **Questions**. Yellow stays for the hero, What stays and Nothing is deleted. The navy install band sits between them. On mobile this caps any single yellow run at three sections. Navy on off-white is 14.4:1.
