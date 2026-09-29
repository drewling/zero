# zero landing: content and structure proposal (slice 02b)

**For the owner.** The visual world B stays as you approved it. What changes here is what the page says and in what order. The current page is 901 words, and this draft is 600. See the comp at `proof/comp/index.html`, served from `proof/comp/` (for example `python3 -m http.server` in that folder). Shots are in `proof/shots/`.

**What I need from you:** approve, or edit, §2 (outline) and §3 (copy). Also answer the three product questions in §6. Nothing gets built until you do.

## 1. What was wrong with the content

- **It is a feature inventory.** The sections run sort table, then recovery, then facts, then install, then FAQ. A visitor never learns why zero is different from a Gmail filter. PRODUCT.md's real differentiator is that the judgment is a model with two signals from your own history, not a rule list. That appears nowhere on the page.
- **The same facts repeat.** "Nothing is deleted / All Mail / search still finds it" appears 4 times: the hero note, the recovery section, the FAQ, and the lede ("You can put it back"). The Jev data flow appears twice (the "Your mail" row and the FAQ), and so do cost, drafts sending nothing, and multiple accounts.
- **"Across every account" is buried in the FAQ.** It is half of PRODUCT.md's one job.
- **Ambient use is missing.** There's no "check it in the morning and close it", which is PRODUCT.md's second trust property.
- **The page promises a daily run the shipped app may not deliver.** "When you're happy, set a time in Settings → Daily routine." In v1.7.0 that setting only rewrites a schedule that already exists (§6, Q1).

## 2. Before and after outline

| # | Before (live B build, 901 words) | After (this draft, 600 words) | Visitor question it answers |
|---|---|---|---|
| 1 | Hero: "Keep the mail that needs you." + a "Nothing is deleted" note | **Hero: "Only the mail that still needs you."** One job across every account, "every archive can be undone", requirements, the real app | What is this, and is it for my Mac? |
| 2 | "What stays. What gets archived." with a 7-row default-rules table | **"It asks who's waiting, not who's writing."** Why filters fail on cold email, the two signals (last message yours, ever written to them), Jev reading against plain-English rules, "it will sometimes be wrong" | Why would this get it right when filters don't? |
| 3 | (none) | **"Check it with your coffee. Then close it."** Menu bar, Open loops across accounts, open in Gmail, learns from what you set aside | What does using it feel like? |
| 4 | "Nothing is deleted." Label mechanics + 3 recovery rows | **"Nothing is deleted."** The only home for this fact: the label, All Mail, Undo day or single email, starred never touched, no answer means kept | What if it's wrong? |
| 5 | "Before you install": 6 rows (Mac, Gmail, Jev key, Your mail, Replies, The app) | **"What it needs, sends and costs"**: 5 rows (Mac, Gmail, Your mail, Replies, Cost). The not-notarized and dependency facts move to the install warning, where the risk is taken | What does it need, where does my mail go, what does it cost? |
| 6 | "Install zero." 4 steps, the last one promising a daily routine | **"Install zero."** The same 4 steps. Adding accounts folds into step 2, and step 4 ends at the first run | How do I start? |
| 7 | "Questions": 5 FAQs | **Cut.** Every answer already has one home above (see §4) | none |

The real app screenshot stays in the hero as the proof. The generic default-rules table is replaced by the two-signal window, which is the thing a filter cannot do.

## 3. Full proposed copy

> Headlines use the line breaks shown in the comp. Bold marks the app's real UI labels.

**Menu bar:** How it decides · Undo · Before you install · Source ↗ · Install

**Hero**

# Only the mail that still needs you.

zero is a Mac menu-bar app for Gmail. Across every account you connect, it keeps the conversations that still need something from you and archives the rest. Every archive can be undone.

[Install zero for Mac] [Read the installer first]

Apple Silicon · macOS 26 or later · Gmail

*Image caption:* The real app. Names and subjects are made up.

**It asks who's waiting, not who's writing.**

Cold email comes with a real person's name on it, so a filter that asks "is this a human?" lets it through. zero looks at your own history instead.

TypeSafe's Jev model reads each thread against your rules, written in plain English. It keeps a person awaiting your answer, a direct question, a failed payment, a legal matter or a real deadline. Receipts, newsletters, notifications and sales pitches are archived. Edit the rules in **Settings → Rules**.

It will sometimes be wrong. Check your first few runs.

*Window "Two questions":*
- **Was the last message yours?** The ball is in their court. Archived.
- **Have you ever written to this sender?** Jev weighs it. A stranger who is selling was never an open loop.

**Check it with your coffee. Then close it.**

Your mail apps stay as they are. zero lives in the menu bar. Choose **Run zero now** and **Open loops** lists what's waiting on you across all your accounts. Tap one to open it in Gmail.

Set something aside and zero can learn to handle mail like it next time.

**Nothing is deleted.**

Archiving removes Gmail's Inbox label and adds one dated for that day. The mail stays in All Mail, and search still finds it.

`🗄️ Auto-Archived 2026-09-29`

- **Undo a day:** Open **Undo** and choose **Restore all**, or put back one email.
- **Starred mail:** Never touched.
- **No answer:** If Jev can't decide, the thread stays in your Inbox.

**What it needs, sends and costs**

- **Your Mac:** Apple Silicon with macOS 26 Tahoe or later. The installer stops on anything else.
- **Gmail:** You sign in with Google in your browser. zero never sees your password. Google may warn that zero is unverified. It hasn't finished Google's review.
- **Your mail:** zero runs on your Mac. To sort a thread, it sends Jev the sender, subject, a short preview and your rules. The zero project runs no server that receives your email. [Privacy policy](/privacy.html).
- **Replies:** Optional. Tap **Reply** and your agent CLI, Claude Code by default, drafts one. The thread goes to that provider. Nothing is sent until you click **Send reply**.
- **Cost:** zero is free and open source. Sorting needs your own TypeSafe Jev key, billed by TypeSafe. Drafts are billed to your agent CLI's account.

**Install zero.**

1. **Run the installer in Terminal.** *Read this first.* zero isn't notarized by Apple. The installer may add Homebrew, Python, Node, the Google Workspace CLI and Claude Code. [Read the script](/install.sh).
   `curl -fsSL https://zero.headless.com/install | bash` [Copy]
   It checks the download's SHA-256 and signature before installing. Or download it from [GitHub Releases](https://github.com/drewling/zero/releases).
2. **Connect Gmail.** Open zero from the menu bar and choose **Connect your first inbox**. Add more in **Accounts**.
3. **Add your Jev key.** In **Settings → Sorting engine**, choose **Get a key**, create one at [TypeSafe](https://console.typesafe.ai/keys), paste it in and click **Save**.
4. **Run it once.** Choose **Run zero now** and look at what stayed and what was archived.

**Footer:** zero · AGPL-3.0 · Source · Privacy · Terms

*Meta description:* zero is a Mac menu-bar app for Gmail. Across every account you connect, it keeps the conversations that still need something from you and archives the rest. Every archive can be undone.

## 4. Where each essential fact now lives (once)

| Fact | New single location | Old locations (count) | Source checked |
|---|---|---|---|
| One job across every account | Hero lede | FAQ only (1) | PRODUCT.md "The one job". `AccountsView` "Add a Gmail account" (`PanelView.swift` ~935). Panel "Across N accounts" (~492) |
| Reversible: label, All Mail, search | "Nothing is deleted" section | Hero note, recovery, FAQ, lede (4) | `lib/inbox_zero.py` ~26/37 `🗄️ Auto-Archived <YYYY-MM-DD>`. Removes INBOX label |
| Undo a day or one email | "Nothing is deleted" rows | Recovery, FAQ (2) | `PanelView.swift` ~1082 **Restore all**. ~1038 "put any of them back in one tap" |
| Starred never touched | "Nothing is deleted" rows | none (new) | `review_open_loops.py` ~154 `_candidate_q` excludes `is:starred` |
| No answer means kept | "Nothing is deleted" rows | none (new) | `review_open_loops.py` `_classify` ~1141-1200, and `_jev_decide` "uncertain -> keep" |
| Can be wrong, check first runs | "How it decides" | Sort section, table fine print, FAQ (3) | Required honesty. Model judgment, not a guarantee |
| Default rules, editable in plain English | "How it decides" (Settings → Rules) | Sort section + table (2) | `keep-policy.md`. `PanelView.swift` ~1320 "Rules" |
| last-message-yours signal | "Two questions" window | Table row (1) | `review_open_loops.py` `_classify` ~1161 (deterministic archive), `_jev_state` ~987 `last_from_owner` |
| replied-before signal | "Two questions" window | none | `_jev_state` ~988 `replied_before`, cold-outreach prompt ~936 ("weigh `thread.replied_before`"). It is a Jev input, not a hard rule, hence "Jev weighs it" |
| Ambient, menu bar, existing apps unchanged | "Check it with your coffee" | none | PRODUCT.md trust property 2. Menu-bar app (`main.swift`) |
| Learns from what you set aside | "Check it with your coffee" | none | `PanelView.swift` ~585 "AI archive — learn to handle mail like this" |
| Apple Silicon, macOS 26+, installer stops | Hero req line + "Your Mac" row | Hero, Mac row (2, kept as 2 on purpose: the short line is a scan-level gate) | `macapp/install-zero.sh` ~61-79 |
| Google unverified warning | "Gmail" row | Gmail row (1) | `OnboardingView.swift` ~107 |
| Password never seen | "Gmail" row | Gmail row (1) | `OnboardingView.swift` ~120 |
| What goes to Jev | "Your mail" row | Mail row, FAQ (2) | `_jev_state`: sender, subject, snippet (≤160 chars), keep_policy. `privacy.html` ~74 |
| No zero server receives mail | "Your mail" row | Mail row, FAQ (2) | privacy.html. Architecture: local `keeper_server.py` |
| Drafts optional, to your agent CLI, nothing sent until Send reply | "Replies" row | Replies row, FAQ ×2 (3) | `PanelView.swift` ~624 Reply, ~2587 Send reply. `lib/llm.py` providers claude/codex/hermes, default claude |
| Cost: free, Jev billed by TypeSafe, drafts billed to CLI account | "Cost" row | Jev row, FAQ, drafts row (3) | `keeper_server.py` ~372 `_require_jev_key` ("Add your TypeSafe API key in Settings to sort mail") |
| Not notarized + dependencies | Install step 1 warning | App row + install warning (2) | `install-zero.sh` header ~9 (ad-hoc, not notarized), ~145-156 (brew, python3, node, gws, Claude Code only if no agent CLI) |
| SHA-256 + signature check | Install step 1 fine print | Install fine print (1) | `install-zero.sh` ~184-199 (sha256), codesign verify ~252. `zero.dmg.sha256` on latest release returned HTTP 200 at 04:52Z |
| Read the installer first | Hero button + install warning link | Same (2, kept: the entry point and the point of risk) | nginx `/install.sh` 302 to the GitHub source |
| AGPL / open source | Footer + Cost row | Footer (1) | `LICENSE` AGPL-3.0 |
| Privacy, Terms | Mail row link + footer | Same | `landing/privacy.html`, `terms.html` |

**Duplicates removed:** "Nothing is deleted" 4 → 1, Jev data flow 2 → 1, drafts send nothing 3 → 1, cost 3 → 1, multiple accounts moved from the FAQ to the hero.

## 5. Corrections and deliberate cuts

**Corrections to the old copy (truth, not wording):**
1. **Daily routine promise removed from install step 4.** In the shipped v1.7.0 app (DMG checked 04:41Z), `_rewrite_schedule_plist` returns early if `~/Library/LaunchAgents/com.drewl.zero.daily.plist` doesn't exist, and nothing in the app or `install-zero.sh` creates it. Only `bin/zero schedule` (CLI) does. The app's own subtitle says "Changes take effect the next time the launch agent reschedules (if it's installed)." The default is weekdays at 07:00 (`_DEFAULT_SETTINGS`), and the time is user-editable, but an app-only user may never get a scheduled run. So the page says "check it with your coffee" and **Run zero now**, and does not promise an automatic morning run. See Q1.
2. **"Needs Apple Silicon Mac"** is now "Apple Silicon". The same fact, shorter.
3. **"The installer may add … Claude Code"**: true, but only when no agent CLI (claude, codex, opencode) is already installed (`install-zero.sh` ~149-156). Kept as "may add".
4. **The Jev data flow is now specific:** sender, subject, a short preview and your rules. This replaces "relevant thread text", which was vaguer than what the code sends for sorting. Drafts send the thread to your agent CLI, which is stated separately.
5. **"It gets things wrong sometimes"** stays as "It will sometimes be wrong." The page never claims zero doesn't misclassify.

**Deliberate cuts:**
- **FAQ section.** Every answer has a single home above.
- **7-row default-rules table.** Replaced by one sentence of keep/archive examples plus the two-signal window, the part that is actually different.
- **"The app" facts row.** Merged into the install warning, where the risk is taken.
- **"Four steps, from Terminal to your first run."** Redundant with the numbered list.
- **"In the app, mail that stays appears under Waiting on you in Open loops."** Replaced by the ambient section.
- **Hero "Nothing is deleted" note.** The hero keeps "Every archive can be undone", and the folder and empty-Trash illustration carries the idea visually. The details live once, in §4.
- **"TypeSafe bills and rate-limits usage."** Cut to "billed by TypeSafe". Rate limiting is TypeSafe's detail.
- **"Drafts use the account behind the agent CLI you set up."** Folded into the Cost row.

**Not advertised (aspirational in PRODUCT.md, not shipped as described):**
- `npx zero init` / `npx zero add-account`: not the shipped setup. Install is the curl script plus in-app onboarding.
- "Once a morning, you forget it's running": not guaranteed from the app alone (correction 1).
- A probability shown to users: Jev returns calibrated probabilities internally (`jev.py`), but the app doesn't show them, so the page doesn't claim it.
- Apple Mail: PRODUCT.md says "Gmail and Apple Mail stay as they are". Gmail labels are what change. The page says "your mail apps stay as they are" and doesn't claim Apple Mail integration.
- Categories (Finance, Clients…): shipped, but not needed for the decision. Left out to keep the page short.

## 6. Open product questions for the owner

1. **Daily run.** Should the page promise an automatic morning run? Right now only `bin/zero schedule` installs it, and the app does not. Options: (a) keep this draft's wording (manual **Run zero now**, no promise), (b) fix the app so Daily routine installs the LaunchAgent, then add one line, "Or let it run on weekday mornings at a time you set", to the coffee section. (b) needs an app change outside this slice.
2. **Headline.** Is "Only the mail that still needs you." acceptable? It is closer to PRODUCT.md's one job ("only what still needs you") than "Keep the mail that needs you." The old headline would also work with this outline.
3. **Section 3 headline, "Check it with your coffee. Then close it."** Is this the right register for you? A plainer option is "It lives in your menu bar."

## 7. Method and limits

- The code checked is this repo at HEAD `6067190`, plus the shipped v1.7.0 DMG (`releases/latest`, published 2026-09-20) mounted read-only. Its payload has the same `_rewrite_schedule_plist` early return and `_require_jev_key`.
- Line numbers are approximate (`~`), from HEAD.
- Word counts are visible body text, excluding script, style and comments, counted by the same script for both pages: 901 → 600.
- The comp reuses `landing/site.css` and `site.js` through symlinks. It has a small inline style block for the two-signal window, which the builder should fold into `site.css`. It is a content proof, not a pixel-final build.
- `landing/` is unchanged. There was no build, QA dispatch or deploy.
