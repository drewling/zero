# 1. What is it and who is it for?
zero is a free, open-source Mac menu-bar app that uses an AI (via a paid third-party key) to auto-archive low-priority Gmail messages while leaving action-needed emails in the inbox, aimed at Gmail users on Apple Silicon Macs who are comfortable running a shell installer and connecting third-party AI tools.

# 2. Confusing or contradictory items
- **"Free, open-source app"** sits directly next to **"Your Jev key, billed by TypeSafe... $0.042 per million input tokens."** The product is free but running it costs money — this isn't false, but the juxtaposition makes "Free" read as misleading at a glance.
- **"zero never sees your password"** (true of any OAuth flow) is presented as a reassurance right next to **"Google may show an unverified-app warning because zero hasn't completed its app review."** This pairs a non-issue (password safety) with a real unresolved issue (Google hasn't vetted this app) in a way that borrows credibility it hasn't earned yet.
- **"Neither goes to zero's servers"** is used to imply privacy, but two other companies (TypeSafe and your coding-tool provider) *do* get your email content. The line technically answers "does zero store it" while dodging "does anyone else store it," which is the question a reader actually has.
- The installer text says it **"May add Homebrew, Python, Node and Google Workspace CLI"** — vague ("may") for a piece of software that's about to run a `curl | bash` script against your Mac and your email.
- **"Claude Code is added only if no supported coding tool is installed"** — this only makes sense once you already know drafts are optional and tied to a coding tool's billing account; on first read it sounds like an unrelated dependency being silently installed.

# 3. What I'd skip / what felt repeated
- The **Terminal `curl | bash` block appears twice** (once in "Ready to install," identically in the footer/CTA area) — redundant given the page is short.
- **"Undo any archive" / "Nothing is deleted" / "Restore archived mail"** is stated three separate times (hero copy, Settings section, Undo section) — I understood it the first time.
- The **inbox illustration mockup** (Alex Rivera, Priya Sharma, etc.) repeats almost verbatim between the hero and the mobile view with no new information — one instance would do.
- I'd skip the **"Sorting cost" pricing snapshot** ("checked 30 Sep 2026") as presented — a timestamped spot price for a token rate isn't decision-useful without knowing typical monthly token usage for an inbox, so it reads as false precision.

# 4. Missing information
- **How much will this actually cost me per month?** Token price is given, but not typical usage, so I can't estimate real cost.
- **What happens on first run to an inbox with thousands of existing emails** — does it try to sort everything at once, or only new mail going forward?
- **How is "Jev" obtained** — is it a separate signup, a separate account, a separate vendor relationship? It's referenced like I already know what it is.
- **What exactly Claude Code/coding-tool integration requires** — do I need an existing Claude Code subscription, or does installation set one up?
- **Uninstall process** — if I stop trusting it, how do I remove it and revoke its Gmail access?
- **What "learned preferences" means concretely** — does the AI's behavior drift over time based on my corrections, and can I inspect/reset that model?
- Nothing about **how errors are surfaced** beyond "AI can make mistakes" — is there a log, an error rate, examples of past failure modes?

# 5. Install vs. leave
**Would make me install (page-presentation fixes):**
- A single, non-repeated, plain-English data flow diagram showing exactly what leaves my Mac, to whom, and why.
- One realistic cost estimate ("~$X/month for a typical inbox") instead of a raw per-token rate.
- A collapsed, single instance of the terminal command instead of two.

**Would make me leave (actual product/security tradeoffs, not fixable by copy edits):**
- Not notarized by Apple + unverified Google OAuth app + `curl | bash` installer that can silently add Homebrew/Python/Node/CLI tools is a real, structural trust gap for something with inbox-wide Gmail access — no amount of rewording removes the risk, only clearer disclosure of it.
- Email content (sender, subject, 160-char preview) going to a third party (TypeSafe) is a genuine data-sharing decision, separate from how well it's explained.

# 6. Who actually sorts and archives the mail?
**A person-initiated run that triggers a remote/cloud AI call**, not a silent background process and not manual dragging. Evidence: the button is literally labeled **"Run zero now"** with a **"Working…"** state shown in the mockup, and the copy says **"Use Run zero now to sort connected Gmail. AI applies your rules."** The sorting decision itself is made by "Jev" (a model accessed via TypeSafe, per the "Sorting data… Sent to TypeSafe (Jev)" box) — so it's a cloud AI evaluating rules you wrote, invoked by you clicking a button, not zero's own local logic and not an automatic daemon that runs without you starting it. Nothing on the page describes a schedule or trigger that runs without user action.

# 7. Undo mechanics and what leaves the Mac
**Undo:** Clear and well-explained. Go to the **Undo tab**, and restore either a single email (small icon buttons, tooltip "Put this email back in the inbox") or an entire day's batch via **"Restore all."** The page explicitly states **"Nothing is deleted. Archived mail stays searchable in Gmail's All Mail under a dated recovery label."** This part is unambiguous.

**What leaves the Mac:** Partially clear, partially not.
- Clearly stated as leaving: sender, subject, up to 160-character preview, latest-reply-sender flag, prior-reply-to-sender flag, your rules, and learned preferences — sent to **TypeSafe**.
- If you use optional AI drafts: thread previews, sent-mail samples, writing preferences, saved profile context — sent to **your coding tool's provider** (e.g., Anthropic via Claude Code).
- **Unclear / not stated:** the *full email body* is never explicitly confirmed as staying on-device or not — only a "160-character preview" is named for sorting, but drafting says "thread previews" and "sent-mail samples" without defining size or scope. I can't tell from this page whether full message content ever transits to a third party, only that *previews and samples* do. I won't guess further than the page states.

# 8. Ratings (1–5)

| Category | Score | Why |
|---|---|---|
| Job clarity | 4 | Hero line and "Choose what needs to stay" make the core function clear quickly; only the Jev/TypeSafe relationship is under-explained. |
| Ease of following the story | 3 | Logical order (install → before you install → run → undo), but repeated CTAs/terminal blocks and restated "nothing is deleted" points break the flow. |
| Usefulness of visuals | 3 | The Settings/Rules and Undo mockups are genuinely informative (real rule text, real restore UI); the Inbox illustration is decorative and adds little beyond what's already stated in words. |
| Finding safety/data/cost info | 3 | It's all present and disclosed more honestly than most landing pages (data flow table, pricing, notarization status), but scattered facts require assembly, and cost is a spot-rate, not a usable estimate. |
| Readiness to decide | 3 | I understand the risk profile and undo mechanism well enough to make a call, but I can't estimate real monthly cost, don't know the uninstall path, and don't know first-run behavior on a large existing inbox. |

# Three most important presentation changes, in priority order
1. **Replace the raw per-token pricing with a concrete usage-based cost estimate** (e.g., "$X–Y/month for an average inbox of N threads/day") so cost is decision-usable, not just technically disclosed.
2. **Consolidate repeated content** — one terminal install block, one "nothing is deleted" statement, one inbox illustration — to shorten the page and stop diluting the real safety information with restatement.
3. **Separate the two OAuth/trust caveats from their surrounding reassurance** so "zero never sees your password" doesn't visually soften "Google hasn't reviewed this app" and "not notarized by Apple" — give the unresolved trust signals their own clearly flagged block instead of pairing them with unrelated positive claims.
