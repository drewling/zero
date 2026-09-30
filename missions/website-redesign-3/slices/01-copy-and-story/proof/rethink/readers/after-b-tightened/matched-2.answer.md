# Zero — Landing Page Critique

## 1. What it does, for whom
Zero is a free, open-source Mac app that uses an AI service to automatically archive low-priority Gmail (newsletters, receipts, sales pitches) while leaving action-needed emails in your inbox, with a one-click undo — aimed at Gmail power users comfortable with terminal installs and AI billing keys.

## 2. Confusing or contradictory
- **"Undo any archive" vs. actual mechanism.** The hero says "Undo any archive," but the Undo tab shows a "Restore" button per email, not a classic undo (a short-window reversal of the last action). It's really "un-archive," not "undo."
- **"No zero server receives your email"** sits directly next to a box that says sender, subject, and a 160-character preview *are* sent to TypeSafe (Jev), a third party. That's not "your email," technically, but visually the two claims sit in tension and a skimming user could read this as "nothing leaves your Mac."
- **Two different taglines for the same action.** "Run zero now" (in the mock menu bar and Settings section) vs. "Choose what needs to stay" (section header) vs. "sorts the rest" (hero) — three phrasings for one action without a single consistent verb (sort/archive/clean).
- **Installer contradiction.** The page insists on safety and reversibility, then casually states "zero is not notarized by Apple" and "may add Homebrew, Python, Node and Google Workspace CLI" — a significant trust gap that isn't reconciled with the reassuring tone elsewhere.
- **Claude Code appears unannounced.** The hero and main flow never mention AI coding tools; "Optional drafts" suddenly introduces Claude Code as a dependency that may get silently installed. This capability is not foreshadowed anywhere before "Before you install."

## 3. What I'd skip / what's repeated
- The **mock inbox illustration** (Alex Rivera, Priya Sharma, etc.) appears twice in near-identical form (hero and again in the narrow view) — same names, same fake urgency, no new information the second time.
- **"Free, open-source app (AGPL-3.0)"** is stated in two separate places (Sorting cost box and footer) — could be consolidated.
- The **Rules code block** is long and reads like documentation dropped onto a marketing page, not curated for a landing page. First-time visitors don't need to see the full keep/archive rule syntax to decide whether to install; a two-line summary would do, with the full rules available on click-through.
- **"Undo any archive"** in the hero and "restore one email or a day's archives" in the Undo section repeat the same promise with different words.

## 4. Missing information
- **What happens on first run** — does it archive silently before I can react, or does it show me a preview/batch to approve? "Check your first runs" implies after-the-fact review, not before-the-fact confirmation.
- **Volume/scale**: how many emails, how far back, does it process my whole historical inbox or just new mail going forward?
- **Total cost in practice** — token price per email is given, but not what a typical inbox costs per month, so "$0.042 per million tokens" is meaningless to a non-technical buyer.
- **What "learned preferences" means** — the rules box says AI "learns," but there's no explanation of what it learns from, or whether that learning data is stored/shared.
- **Retention/deletion** — how long does TypeSafe retain the subject lines/previews it receives? Is there a data deletion process?
- **Multi-account support** — the Accounts tab appears in the app screenshots but is never explained in the text.
- **What happens if I stop paying** or revoke the Jev key — does the app stop working, or do already-archived emails get restored?

## 5. What would make me install / leave

**Install:**
- Confidence that the AI's judgment matches the stated rules well (the crafted keep/archive rules are sensible and specific)
- True on-device processing of email content, with only metadata leaving the Mac (as claimed)
- A trial "preview" mode before it archives anything for real

**Leave:**
- **Product/security tradeoffs:** unnotarized installer, silent dependency installation (Homebrew/Python/Node/Google CLI), third-party AI service handling my email metadata, unverified Google OAuth warning
- **Page-presentation problems:** the reassurance ("no server receives your email") sitting too close to the disclosure that data does leave the machine, in a way that could mislead a skimmer; the missing pre-run preview step; the AGPL/free framing overshadowing the recurring API cost

## 6. Who sorts and archives
**The app, after you click "Run zero now,"** using the AI service (Jev/TypeSafe) applying your saved rules. Evidence: the floating "zero … Run zero now" panel in the hero, the text "Use Run zero now to sort connected Gmail. AI applies your rules," and the "Working…" state shown under the app icon. There is no evidence of a continuous background daemon — the copy implies a manual trigger each time ("Run zero now"), not automatic/scheduled sorting. Dragging is not mentioned anywhere as a sorting mechanism.

## 7. Undo mechanism and data leaving the Mac
**Undo:** In the Undo tab, you can restore a single email or use "Restore all" for a whole day's batch. The page states "Nothing is deleted" and archived mail remains in Gmail's "All Mail" under a dated recovery label — so the underlying mechanism is a normal Gmail archive/label, not a Mac-side trash. This part is fairly clear.

**What leaves the Mac:** For sorting, "sender, subject, a preview of up to 160 characters, whether you sent the latest message, whether you've replied before, your rules and learned preferences" go to TypeSafe (Jev). For optional AI drafts, "thread previews, sent-mail samples, writing preferences and saved profile context" go to your coding tool's provider (e.g., Claude Code's account). The page says "No zero server receives your email" — but it's **unclear** whether the 160-character preview could include sensitive body content (a preview is still content, not just metadata), and it's unclear how long TypeSafe or the coding-tool provider retains this data. I won't guess further than what's stated.

## 8. Ratings

| Criterion | Score | Reasoning |
|---|---|---|
| Job clarity | 4 | Hero sentence is clear and specific about the core action (archive non-actionable Gmail, keep the rest). |
| Ease of following the story | 3 | Section order is logical, but the narrow mock inbox illustration repeats, and the Rules code block breaks the narrative flow with raw text. |
| Usefulness of visuals | 3 | The Undo/Settings mockups are informative, but the inbox illustration is generic and adds little; it's clearly labeled fake but takes up prominent hero space. |
| Finding safety/data/cost info | 4 | The "Before you install" section is a genuinely dense, well-organized disclosure block — better than most product pages — though the preview-vs-metadata ambiguity and retention silence dock a point. |
| Readiness to decide | 2 | Missing first-run behavior, historical-mail scope, and real-world monthly cost leave too many open questions for a confident yes/no. |

## Top 3 presentation changes, in priority order
1. **Reconcile the privacy claim with the data-sharing disclosure.** Move "No zero server receives your email" so it's not immediately adjacent to (and doesn't visually contradict) the list of data sent to TypeSafe; clarify that a content preview is being shared, not just metadata.
2. **Show what a first run actually looks like** — a "preview before archive" screenshot or explicit statement of whether the first run archives silently or asks for confirmation, since "check your first runs" currently implies after-the-fact damage control.
3. **Replace the raw Rules code block with a plain-language summary**, keeping the full YAML/Markdown rules behind a "view full rules" link — this shortens the page, removes documentation clutter from the narrative, and reduces the sense that this is a developer tool wearing a consumer-app costume.
