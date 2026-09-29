# 1. What does it do, for whom?

zero is a free, open-source Mac utility that uses an AI model to automatically sort your Gmail inbox — keeping mail that needs action and archiving the rest — aimed at Gmail users on Apple Silicon Macs who want a less noisy inbox without switching email clients.

# 2. Confusing or contradictory moments

- **"Keep using Gmail or Apple Mail"** in the hero, but every other mention of connectivity ("Gmail access," "Gmail only," the whole Undo mechanism using Gmail's All Mail) only talks about Gmail. Apple Mail is never explained — is it just an alternate viewer, unsupported, or does it also get sorted? This line reads like leftover copy from a broader-scope product.
- **"Click Run zero now on your Mac"** implies a manual, on-demand action, yet the hero copy says zero "archives the rest" as if it's ongoing/automatic. Screenshot 1 even shows a folder icon labeled "**Auto-Archived 2026-09-29**" — "Auto" suggests scheduled/background behavior, but the only trigger described anywhere in the text is you manually clicking "Run zero now." These two mental models (automatic vs. you press a button) are never reconciled.
- **Reply drafts section** says "Claude Code, **or another AI coding tool you already use**, can draft replies." Using a coding tool to draft emails is an odd, unexplained pairing — it's stated as a given rather than justified, which reads as confusing scope creep for an email utility.
- **Notarization contradiction**: the page proudly shows a clean "Install zero for Mac" button, but buried later: "zero is not notarized by Apple" and the installer runs a raw `curl | bash` command that may silently add Homebrew, Python, Node, a Google CLI, and Claude Code. The tone of the hero (simple, safe) contradicts the technical reality revealed later (developer-tool-level install with a broad footprint).

# 3. What I'd skip / what's repeated

- The "Email data" disclosure block is repeated nearly verbatim across three screenshots (before-1440, install-1440, before-390) — that's just the page's own scroll/crop redundancy, not new info, but as a reader I'd only need to see it once.
- The "Stays / Archived" illustration (Screenshot 2/8) repeats almost the same point already made in prose immediately above it ("A question from a colleague stays... a newsletter gets archived...") — the mockup adds little beyond restating the same four examples visually. I'd skip the mockup or the prose, not both.
- "The model can make mistakes. Check your first few runs." and "Sorting leaves starred mail alone. If the model can't decide, the email stays in your inbox" are two separate safety-net disclaimers that could be merged — they're making the same underlying point (the AI is imperfect, here's your safety net).

# 4. Missing information before deciding

- Does zero run continuously/on a schedule, or strictly only when I click "Run zero now"? Never stated outright.
- What "learned preferences" means and where they're stored/for how long.
- What happens with multiple Gmail accounts — is behavior per-account, and can rules differ?
- Any concrete pricing for the Jev key/TypeSafe billing — "billed by TypeSafe" with no rate, tier, or estimate.
- What data Claude Code's "provider" is, specifically, and what "saved profile context" contains.
- Whether zero can be fully uninstalled cleanly, including the Homebrew/Python/Node/Google CLI it may install.
- Any word on how many emails/day this scales to, error rates, or real user experience — the only "results" shown are explicitly labeled fictional illustrations.

# 5. What would make me install / leave

**Would install if:**
- Notarization existed or the install script were auditable and transparent up front (not buried after the CTA).
- Clear confirmation that only metadata (sender/subject/preview) leaves the Mac, not full email bodies — this is stated, which is good.
- A visible undo history to build trust before trusting the AI at scale.

**Would leave because of (product/security):**
- Non-notarized installer that runs `curl | bash` and can install multiple unrelated dev tools (Homebrew, Node, Python, Google CLI, Claude Code) — a large, opaque system footprint for what's pitched as a simple inbox cleaner.
- Dependence on a third-party AI model (TypeSafe's Jev) with my own paid key, sending email metadata to that provider — an ongoing cost and data-sharing surface with no pricing shown.
- Unverified-app warning from Google on sign-in, which the page acknowledges but doesn't fully de-risk.

**Would leave because of (page presentation, separate from the product itself):**
- The safety-critical disclosures (notarization, installer footprint, data sharing) are all pushed to the bottom, after the CTA already asked me to install — that ordering itself is a trust problem regardless of whether the product is fine.
- The Apple Mail mention going nowhere, and the automatic-vs-manual sorting ambiguity, make it hard to form an accurate mental model even if I wanted to trust the product.

# 6. Who actually sorts and archives the mail?

Based on the page, **you trigger it, then the app (calling an external AI model) does the sorting** — but it is not a passive background process. Evidence: "Click **Run zero now** on your Mac to sort the Gmail accounts you connect." This is the only stated trigger mechanism. The AI model itself does the classification ("An AI model checks each thread against your rules"), but only after you manually invoke the run. The "Auto-Archived 2026-09-29" folder label in Screenshot 1 muddies this — it implies scheduled automation — but no scheduling feature, background daemon, or launch-agent is ever described in the text. I'd conclude: manual trigger, automated decision-making once triggered, with the "Auto-Archived" label being an unexplained (possibly inconsistent) illustration detail.

# 7. Undo mechanism and what data leaves the Mac

**Undo:** Archived mail is not deleted — it remains in Gmail's "All Mail" with a dated recovery label. Inside zero's own "Undo" tab, you can restore a single email, or click "Restore all" to bring back an entire day's batch of archived mail at once. This is reasonably clear.

**What leaves the Mac:** For sorting, zero sends TypeSafe's Jev model the sender, subject, a short preview, reply-history signals, your rules, and learned preferences — explicitly not the full email body, and explicitly no zero-operated server receives your email. If you use the optional reply-draft feature, more leaves: thread previews, sent-mail samples, writing preferences, and saved profile context go to whatever provider powers your chosen AI coding tool (e.g., Claude Code) — but the page doesn't specify who that provider is by default or how that differs from the Jev/TypeSafe path. Whether "reply-history signals" includes any actual message content beyond metadata is unclear — the page doesn't define that term, so I won't assume.

# 8. Ratings (1–5)

- **Job clarity: 3** — the core pitch ("keeps what you need, archives the rest") is clear, but the automatic-vs-manual trigger confusion and the unexplained Apple Mail mention undercut it.
- **Ease of following the story: 3** — logical section order (how it works → undo → before you install → install), but critical safety info is sequenced last, after the ask, weakening the narrative flow for a cautious reader.
- **Usefulness of the visuals: 2** — the Stays/Archived mockup restates prose almost exactly rather than adding new understanding, and it's explicitly labeled fictional, so it can't build real confidence in accuracy.
- **Finding safety/data/requirements/cost info: 3** — it's all there (data flow, cost model, notarization status, system requirements), and to the page's credit it doesn't hide these facts entirely — but it's positioned only at the bottom, past the primary CTA, so a fast scanner might install before ever seeing it.
- **Readiness to make a decision: 2** — too many open questions remain (trigger mechanism, actual pricing, Apple Mail's role, uninstall/footprint cleanup) for me to commit either way with confidence.

# Three most important presentation changes, in priority order

1. **Move the notarization/installer-footprint warning and the data-sharing disclosure above or immediately beside the "Install" button**, not after it — a reader shouldn't have to scroll past the CTA to learn the installer is unsigned and modifies their system.
2. **Resolve the automatic-vs-manual sorting contradiction** — pick one consistent story (either it's a manual "Run zero now" tool, or it runs automatically/on schedule) and remove or explain the "Auto-Archived" label and the "keep using Gmail or Apple Mail" line that implies broader passive behavior.
3. **Cut the redundant Stays/Archived illustration or the paragraph that precedes it** — they say the same thing twice; use the saved space to add a concrete cost figure/range and clarify what Apple Mail support actually means, since both are currently unexplained gaps.
