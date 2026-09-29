# Critique of "zero" landing page

## 1. What it does / who it's for
zero is a Mac app for Gmail users that automatically decides which inbox emails need action and archives the rest, while letting you undo any archive and keep working from Gmail (or possibly Apple Mail) as usual.

## 2. Confusing or contradictory elements

- **Apple Mail vs. Gmail-only**: The hero line says "Keep using Gmail or **Apple Mail**." But the requirements line right below it says "Apple Silicon. macOS 26 or later. **Gmail only**." and the entire "zero Info" table (Screenshot 7/8) only discusses Gmail access, Gmail's All Mail, Gmail labels. Apple Mail is never mentioned again. It's unclear if Apple Mail is genuinely supported or if that's leftover/aspirational copy.

- **Manual click vs. automatic**: The instructional text says "**Click Run zero now** on your Mac to sort the Gmail accounts you connect" — implying a manual trigger. But the hero illustration (Screenshot 3) shows a folder labeled "**Auto-Archived 2026-09-29**" next to a Trash icon, which visually implies something automatic and ongoing happened already, before any "Run zero now" click is described. These two cues point in different directions about whether sorting is a one-off action you initiate or something running in the background.

- **Trash icon vs. "Nothing is deleted"**: The hero screenshot places a literal **Trash** can icon next to the archive folder (Screenshot 3), even though the page later insists "Undo an archive. **Nothing is deleted**." Putting a trash icon in the primary illustration undercuts the safety message made later in the page.

## 3. Sections/lines I'd skip — repeated facts

- The four names (Alex Rivera, Priya Sharma, Daniel Kim, Sarah Mitchell) and their subject lines appear **twice**, verbatim, in the hero inbox mock and again in the "See what stays" Stays panel. Nothing new is learned the second time — it could be cut or replaced with different examples to actually add information.
- "Undo any archive" is stated in the hero, again as a nav tab, and again as its own full section with near-identical wording ("Undo an archive. Nothing is deleted."). Three touches on the same point without adding new mechanics until the third one — could be compressed.
- "Read the installer first/before running it" is repeated near-identically in the hero and again in the footer install block — fine as a safety reminder, but it reads as filler the second time since no new detail is added.

## 4. Missing information before I could decide

- Actual **price** of the "Jev key" from TypeSafe — the page says sorting "needs your own Jev key, billed by TypeSafe" but never states a rate or estimated cost per run/month.
- Whether "**Run zero now**" is a one-time manual action every time, or can be scheduled/automated — directly contradicted by the "Auto-Archived" visual.
- What "**short preview**" means in terms of amount of email body text sent to TypeSafe — is it a snippet, first line, or something longer?
- No real screenshots of the actual app UI — everything shown is explicitly labeled "Illustration" or has "DRAFT / not approved" watermarks, so I can't judge the real interface.
- How Apple Mail fits in, if at all (see contradiction above).
- What happens to multiple Gmail accounts, rate limits, or how often "learned preferences" are stored/updated locally.

## 5. What would make me install vs. leave

**Product/security tradeoffs (independent of page quality):**
- Would lean toward leaving: the installer is **not notarized by Apple**, runs via `curl | bash`, and can silently add Homebrew, Python, Node, a Google Workspace CLI, and Claude Code — a fairly invasive footprint for a "clean my inbox" utility.
- Would lean toward leaving: email metadata (sender, subject, preview, reply signals) goes to a third-party AI model (TypeSafe's Jev) — acceptable to some, a dealbreaker to others handling sensitive mail.
- Would lean toward installing: archiving is non-destructive, reversible, doesn't touch starred mail, and is open source (AGPL-3.0) — meaningful trust signals.

**Presentation problems (independent of the product itself):**
- The Gmail/Apple Mail contradiction and the auto/manual ambiguity would make me hesitate purely because the page contradicts itself, not because of the product's actual behavior.
- Everything visual is marked as fake/illustrative, and every screenshot carries a "DRAFT... not approved" watermark — this reads as an unfinished, pre-release page, which lowers confidence regardless of the underlying app's quality.

## 6. Who actually sorts and archives the mail?

Based on the page, **the app itself sorts and archives, after you manually trigger it** — not you dragging mail, and not (clearly) a silent background process. Evidence: "Click **Run zero now** on your Mac to sort the Gmail accounts you connect" and "An AI model checks each thread against your rules. It keeps... Receipts, newsletters and cold sales emails may be archived." This describes an automated AI decision process, but one that starts from a user-initiated action ("Run zero now"), not the user dragging individual emails. The "Auto-Archived" folder label in the hero muddies this, suggesting it might also run unattended, but the explicit instructions only describe a manual trigger.

## 7. Undo mechanics and what data leaves the Mac

**Undo:** Archived mail is not deleted — it moves to Gmail's All Mail with a dated recovery label. To undo, you go to zero's **Undo** tab and either restore a single email or click **Restore all** to bring back an entire day's worth of archives at once. The mechanism is stated clearly enough to act on.

**What leaves the Mac:** For sorting, zero sends TypeSafe's Jev model the sender, subject, a short preview, reply-history signals, your rules, and learned preferences — explicitly stated that "No zero server receives your email." If you use the *optional* reply-draft feature, the AI coding tool's provider additionally receives thread previews, sent-mail samples, writing preferences, and saved profile context. Beyond this, it's **unclear** exactly how much of the email body counts as a "short preview," and the page doesn't say whether attachments are ever touched — I won't guess at those details since they aren't stated.

## 8. Ratings (1–5)

- **Job clarity: 4** — The core pitch (sort inbox, archive rest, undo) is clear on first read; loses a point for the Gmail/Apple Mail contradiction.
- **Ease of following the story: 3** — Flow moves logically (how it works → undo → safety → install), but redundant examples and the auto/manual ambiguity break the thread.
- **Usefulness of visuals: 2** — Visuals are wireframe mockups explicitly labeled as fake and carry unresolved "DRAFT/not approved" watermarks; they illustrate the concept but tell me nothing about the real product's look or trustworthiness.
- **Finding safety/data/requirements/cost info: 4** — The dedicated "zero Info" table is genuinely thorough and well-organized on access, data flow, and billing; only missing an actual price figure.
- **Readiness to make a decision: 3** — I understand the tradeoffs (non-notarized installer, third-party AI, reversible archiving) well enough to have an opinion, but contradictions and missing pricing/automation details leave real gaps.

## Three most important presentation changes, in priority order

1. **Resolve the Gmail-only vs. Apple Mail contradiction.** Either explain concretely how Apple Mail fits in, or remove the Apple Mail mention entirely — right now it directly conflicts with the stated requirement.
2. **State plainly whether sorting is a manual, on-demand action or an automatic/scheduled background process**, and align the "Auto-Archived" visual label with whichever is true.
3. **Replace the fake wireframe illustrations with real product screenshots** (and remove the "DRAFT / not approved" watermarks before this is shown to real users) — as-is, the visuals actively prevent judging what the product looks like or how trustworthy the interface feels.
