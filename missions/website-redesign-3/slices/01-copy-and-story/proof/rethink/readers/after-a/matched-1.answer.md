# zero — Landing Page Critique

**1. What it does / who it's for**
zero is a free, open-source Mac menu-bar app that uses an AI model to automatically archive low-priority Gmail (newsletters, receipts, cold sales) while leaving replies-owed and urgent mail in your inbox, for Gmail users on Apple Silicon Macs who want a lighter inbox without switching email clients.

**2. Confusing or contradictory elements**

- **"The app is free and open source"** vs. **"Bring your own Jev key, billed by TypeSafe"** — the app itself is free, but you can't actually use its core function (sorting) without paying a third party. This isn't stated as a contradiction, but the juxtaposition ("Sorting cost" sitting right under "free and open source") reads like a bait-and-switch if you don't read carefully.
- **"zero never sees your password"** (Google sign-in) immediately followed by **"You may see an unverified-app warning because zero hasn't completed Google's app review"** — this pairing is meant to reassure but actually raises the question: if it's safe enough to trust with Gmail access, why hasn't it passed Google's review? The page doesn't explain what "unverified" means for risk.
- **"No zero server receives your email"** vs. the Sorting data list, which includes sender, subject, 160-char preview, reply history, and rules — this is a lot of email metadata/content going to TypeSafe's Jev model. Calling this "no email" received is a semantic stretch; a 160-character preview *is* email content.
- **Installer section says it may silently add Homebrew, Python, Node, Google Workspace CLI, and Claude Code** — this is a substantial system footprint for what's pitched as "a Mac app," and it's disclosed almost as an aside, not as a headline fact.
- The **hero screenshot's Trash icon** sits next to "Auto-Archived" folder, but the copy explicitly says "Nothing is deleted" and mail goes to Gmail's All Mail — the Trash icon in the mockup visually contradicts the "nothing is deleted" promise.
- **"Keep using Gmail or Apple Mail"** in the hero, but the entire mechanism only works through Gmail (via Google sign-in) — Apple Mail is a *read* option, not an integration point. This could mislead someone into thinking Apple Mail is directly supported.

**3. What I'd skip / what's repeated**

- The "Nothing is deleted / archived mail stays searchable in All Mail" fact appears twice (How It Works section and implied again in Undo section) — could be stated once.
- "The app is free and open source under AGPL-3.0" appears in body copy and then again in the footer — redundant, not harmful, but could be trimmed to just the footer for legal record-keeping.
- The Terminal install command is shown twice (mid-page and bottom) with no visual difference — one instance would suffice, or clarify why it repeats (maybe a "jump to install" anchor, but that's not stated).

**4. What's missing before I could decide**

- **Actual pricing** for the Jev key / TypeSafe billing — "See TypeSafe pricing" is a link with no number given on this page. I can't judge cost without leaving the page.
- **How accurate the AI sorting actually is** — no stated error rate, no first-party testimonials (illustrations are explicitly fake), so I have zero evidence of real-world reliability.
- **What data Claude Code (or other AI coding tool) permanently retains** if I use optional drafts — "its provider receives thread previews, sent-mail samples, writing preferences, saved profile context" but no retention/deletion policy stated.
- **Uninstall process** — nothing about how to remove zero, or what happens to the Homebrew/Python/Node/Claude Code dependencies it installs if I stop using it.
- **What "unverified app warning" from Google actually looks like or means practically** — is this a one-time click-through, or a persistent scary banner? Not shown.
- **Frequency of runs** — is sorting continuous, scheduled, or only when I manually click "Run zero now"? The page implies manual runs only ("Start a run from zero's menu bar") but doesn't rule out background/scheduled runs.

**5. What would make me install / leave**

*Install triggers:*
- If TypeSafe pricing were transparent and low-cost/free-tier available
- If notarization status were resolved (Apple-notarized build) reducing installer trust friction
- If I could see the sorting rule engine specifics before committing my Gmail account

*Leave triggers — product/security tradeoffs:*
- Non-notarized installer that silently adds multiple system-level dependencies (Homebrew, Python, Node, a CLI) is a meaningful security/maintenance surface for a menu-bar utility
- Sending email metadata to a third-party AI model (TypeSafe) with a separate paid key is friction and an added data-sharing party beyond Google/zero
- No stated error rate for AI archiving accuracy — my first instinct is distrust of automatic action on my inbox

*Leave triggers — page presentation problems:*
- The Trash icon inconsistency (visual signals deletion; copy says no deletion)
- Pricing hidden behind an external link with no ballpark figure
- "Free and open source" framing that undersells the recurring cost of actually using the product

**6. Who sorts and archives the mail**

**You start it manually, and the app (via TypeSafe's Jev AI model) does the sorting once triggered — this does not appear to run as a passive/continuous background process.**

Evidence:
- "Start a run from zero's menu bar" — explicit user-initiated action
- The hero mockup shows a "Run zero now" button with a "Working…" status, implying a discrete run cycle, not continuous background operation
- No text anywhere states scheduled/automatic recurring runs; the only automation described is *within* a run ("An AI model uses your rules to keep... archive...")

However, the page doesn't explicitly say runs *can't* be scheduled — this is inferred from absence of contrary evidence, not confirmed.

**7. Undo mechanism and data leaving the Mac**

*Undo:* Clearly explained — go to zero's **Undo tab**, either restore a single email via the restore icon next to each entry, or click **Restore all** for an entire day's batch (grouped by date, e.g., "Tue 29 Sep · 8 set aside"). The page states archived mail is never deleted — it's tagged with a dated recovery label inside Gmail's All Mail, so in theory you could also manually recover it via Gmail directly, though the page doesn't confirm that path is officially supported (only the zero Undo tab is described as the recovery mechanism).

*What leaves the Mac:* This is **partially clear, partially not**:
- Confirmed to leave: sender, subject, up to a 160-character preview, reply-status metadata, your rules/learned preferences — sent to TypeSafe's Jev model for sorting decisions.
- Confirmed to leave (if using optional drafts): thread previews, sent-mail samples, writing preferences, saved profile context — sent to Claude Code or your chosen AI coding tool's provider.
- **Unclear:** whether the 160-character preview is a snippet of the *email body* or just a subject-adjacent field, whether attachments or full email bodies are ever transmitted, whether TypeSafe retains this data after a sorting decision is made, and whether "your email" in "No zero server receives your email" excludes the metadata/preview sent to TypeSafe (which is a different server) — the wording implies zero's own servers are clean, but doesn't fully account for TypeSafe as a distinct data recipient in that specific sentence. I won't guess further — the page doesn't specify data retention or deletion policies for TypeSafe.

**8. Ratings**

| Category | Score | Reasoning |
|---|---|---|
| Job clarity | 4/5 | Hero sentence is clear and specific; slight confusion from "Gmail or Apple Mail" framing diluting the Gmail-only reality. |
| Ease of following the story | 4/5 | Logical top-to-bottom flow (what it does → how it works → before you install → install), but repeated facts and the two identical Terminal blocks break rhythm. |
| Usefulness of visuals | 3/5 | Mockups (Inbox, Undo tab) do help visualize the workflow, but the Trash icon contradicts the "nothing deleted" claim, and illustrations are explicitly fake, so I can't judge real-world accuracy from them. |
| Finding safety/data/requirements/cost info | 3/5 | Requirements (Apple Silicon, macOS 26, Gmail only) are upfront and clear; safety/data info is present but dense and requires careful reading to catch the TypeSafe distinction; actual cost is not given (only a link). |
| Readiness to decide | 2/5 | Missing pricing numbers, no accuracy/error-rate data, unclear data retention by TypeSafe, and unclear whether app can run unattended — too many open questions to commit an inbox and a paid key to it. |

---

## Top 3 Presentation Changes (priority order)

1. **Resolve the Trash-icon vs. "nothing is deleted" contradiction** in the hero mockup — either remove the Trash icon or add a visual note clarifying its role, since it directly undercuts the page's core safety promise.

2. **State actual TypeSafe/Jev pricing on the page** (even a rough range) instead of only linking out — cost is a decision-blocking gap, not a nice-to-have.

3. **Separate "zero the app" cost claims from "using zero" cost reality** — clarify upfront, near the hero or first mention of "free and open source," that a paid third-party key is required for the core sorting feature to function, so the free/open-source framing doesn't read as misleading before the reader reaches the fine print.
