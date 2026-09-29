# zero — Whole-Page Critique

## 1. What it does, for whom
zero is a Mac menu app that uses an AI model to automatically archive low-priority Gmail (newsletters, receipts, cold sales) while keeping mail that needs a reply, for Mac users comfortable running a terminal-based installer.

## 2. Confusing or contradictory
- **"Click Run zero now on your Mac to sort the Gmail accounts you connect"** vs. the earlier tagline **"Undo any archive. Keep using Gmail or Apple Mail."** — Apple Mail is mentioned in the hero but never explained again anywhere on the page. How does an Apple Mail user benefit if sorting is Gmail-only ("Gmail only" in the fine print)? This is a direct contradiction.
- The **Trash icon** appears in the hero illustration (Screenshot 1/3) right next to "Auto-Archived," but the copy insists "Nothing is deleted" and mail goes to Gmail's All Mail, not Trash. The visual implies deletion when the text says otherwise.
- **"zero never sees your password"** (Gmail access) sits oddly next to **"Sorting sends TypeSafe's Jev model the sender, subject, a short preview..."** — two different trust claims (password safety vs. content sharing) are bundled under a reassuring banner ("Know what you connect, share and pay for") that actually reveals the app shares more than the hero copy implies.
- **"zero is free and open source"** followed immediately by "Sorting needs your own Jev key, billed by TypeSafe" — "free" is contradicted by a mandatory paid third-party dependency in the very next sentence.

## 3. What I'd skip / what's repeated
- The "See what stays. See what gets archived." section and the "Rules" section repeat the same four examples (colleague question, newsletter, payment problem, receipt) almost word-for-word. One of these two sections could be cut entirely.
- The mock inbox illustrations (Stays/Archived columns) restate the prose above them one-for-one — decorative, not additive.
- "Undo any archive" appears in the hero, then again as its own full section — redundant given how simple the mechanism is (restore in Gmail's All Mail).

## 4. Missing information before deciding
- What "Jev key" costs (no pricing shown, just "billed by TypeSafe").
- What TypeSafe is / its privacy posture beyond one sentence.
- Whether sorting is one-time-per-click or scheduled/automatic ("Click Run zero now" suggests manual, but "Auto-Archived" label implies automation).
- Any explanation of the Apple Mail claim.
- What happens if you disconnect/uninstall — does it revoke Gmail access, leftover Homebrew/Node/Python/Claude Code installs?
- No version number, changelog, or evidence of real users/reviews.

## 5. Install vs. leave

**Product/security tradeoffs:**
- Leave: unmaintained third-party AI model (TypeSafe/Jev) reading email metadata is a real exposure; unnotarized installer that silently adds Homebrew, Python, Node, Google CLI, and Claude Code is a heavy, invasive footprint for an email sorter.
- Install: "Nothing is deleted," Gmail-native undo via All Mail, and starred-mail exclusion are genuinely reassuring safety mechanics if true.

**Page-presentation problems (not product flaws):**
- Leave: the Apple Mail/Gmail-only contradiction, and burying the real cost/dependency chain under a friendly "free and open source" banner, reduce trust in the page itself regardless of the product's actual safety.

## 6. Who sorts and archives the mail
**You, manually, by clicking "Run zero now."** Evidence: "Click **Run zero now** on your Mac to sort the Gmail accounts you connect" is explicit. However, the "Auto-Archived 2026-09-29" folder label in the hero illustration contradicts this by implying automatic/scheduled behavior — the page never clarifies whether there's a background/scheduled mode or if "Auto" just means "the app did it, not you," making this genuinely ambiguous.

## 7. Undo mechanism and data leaving the Mac
**Undo:** Archived mail gets a dated recovery label and stays in Gmail's All Mail; in zero's Undo tab you restore one email or click "Restore all" for that day's batch. This is clearly explained.

**Data leaving the Mac:** For sorting, TypeSafe's Jev model receives sender, subject, a short preview, reply-history signals, your rules, and learned preferences — this is stated clearly. If you use the optional reply-draft feature, thread previews, sent-mail samples, writing preferences, and saved profile context also go to that AI coding tool's provider (e.g., Anthropic via Claude Code). **What's unclear:** the page never says whether Jev/TypeSafe stores or retains this data, for how long, or whether it's used for model training — the "Privacy policy" link is the only pointer, and its contents aren't shown here.

## 8. Ratings (1–5)

| Category | Score | Why |
|---|---|---|
| Job clarity | 4 | Core action (archive low-priority mail, keep actionable mail) is clear and repeated consistently. |
| Ease of following story | 3 | Logical section order, but repeated examples and the Apple Mail/Gmail contradiction disrupt the flow. |
| Usefulness of visuals | 2 | Illustrations just restate adjacent text with fake names; the Trash icon actively misleads about deletion. |
| Finding safety/data/cost info | 3 | It's all there in "Know what you connect, share and pay for" — but cost is incomplete (no Jev price) and "free" is undercut by mandatory billing. |
| Readiness to decide | 2 | Missing pricing, unclear automation model, unexplained Apple Mail claim, and no notarization leave too many open questions. |

## Top 3 presentation fixes, in priority order
1. **Resolve the Apple Mail contradiction** — either explain how Apple Mail users benefit or remove "Keep using Gmail or Apple Mail" from the hero, since everything else says Gmail-only.
2. **Fix the Trash icon in the hero illustration** — it visually implies deletion, directly undercutting "Nothing is deleted." Replace with an archive-box icon or remove it.
3. **State actual Jev/TypeSafe pricing and clarify manual vs. automatic sorting** — "free and open source" next to an unstated recurring cost, and "Run zero now" next to an "Auto-Archived" label, are the two biggest blockers to a confident decision.
