# zero — First Look Review

## 1. What it does / who it's for
zero is a Mac menu-bar app that runs on demand, uses a third-party AI model to sort your connected Gmail inbox (archiving what doesn't need action, leaving the rest), with a reversible undo — aimed at Mac users comfortable running a terminal install script and paying separately for an AI API key.

## 2. Confusing or contradictory elements
- **Stray dev watermark on the page itself:** "DRAFT comp · page B · risk-first · Draft3 · not approved" appears as a banner overlapping actual content (visible in Screenshot 3 and, worse, covering the "Priya Sharma" row in the mobile Screenshot 8). This looks like an internal QA artifact left on a "finished" landing page.
- **Gmail vs. Apple Mail claim:** Hero says "Keep using Gmail or Apple Mail," but the very next section header says "Read your connected Gmail in Gmail or Apple Mail" and the requirements line says "Gmail only." It's unclear if Apple Mail is actually supported or just usable as a plain IMAP viewer after the fact.
- **Mismatched counts in the Undo panel:** header reads "8 set aside," but only 5 items are listed (Weekly newsletter, Coffee receipt, Sales introduction, Shipping confirmation, Webinar invitation). No indication this is a partial/scrollable view.
- **Three different data recipients, never diagrammed:** "zero" (the app), "TypeSafe's Jev model," and "Claude Code" (optional) each receive different data for different reasons, all explained in dense prose inside one small table — easy to conflate.
- **No price shown for something billed:** "Bring your own Jev key, billed by TypeSafe" — no dollar figure anywhere on the page itself, only an external link.

## 3. What I'd skip / what's repeated
- "Undo any archive" is stated in the hero, then again in "Restore archived mail," then again inside the Undo tab UI — three times. Fine for reinforcement, but could be trimmed to two mentions.
- Two separate install paths (the "Install zero for Mac" button up top, and a `curl | bash` terminal command at the bottom) are shown without explaining which one a normal user should pick or why both exist — this isn't restating a fact so much as adding an unexplained fork in the decision.
- The floating "Auto-Archived 2026-09-29" folder icon next to the Inbox mock has no visible connective line or explanation tying it to the inbox list above — I'd skip trying to interpret it since it isn't explained in text.

## 4. Missing information before deciding
- Actual pricing for the Jev key / TypeSafe usage.
- What "Jev" is (model, company background) — no explanation beyond the name.
- Whether the installer's addition of Homebrew, Python, Node, and Google Workspace CLI happens silently or with prompts/consent at each step.
- Whether the shown Rules text is an editable default or just a sample.
- Data retention: how long TypeSafe (or the optional draft provider) keeps the previews/metadata sent to them — the "Privacy policy" is linked but its contents aren't shown here.
- Version number, changelog, or any indication of maturity/user base.
- What Gatekeeper/security steps a user will need to click through, given "zero is not notarized by Apple."

## 5. What would make me install vs. leave

**Product/security tradeoffs (independent of page quality):**
- *For:* Reversible undo with "nothing is deleted," open source under AGPL-3.0, starred mail explicitly protected, rules are user-editable and legible.
- *Against:* An unnotarized app whose installer silently adds multiple dev tools (Homebrew/Python/Node/Google CLI); a `curl | bash` install pattern piping straight into a shell; email metadata and previews sent to a third-party AI vendor (TypeSafe) for sorting; an optional feature that expands that data exposure further to yet another AI provider (sent-mail samples, writing preferences, saved profile context) for draft-writing.

**Page-presentation problems (fixable without touching the product):**
- The literal "not approved" watermark bleeding into content.
- The 8-vs-5 count mismatch in the Undo mock.
- No pricing numbers on-page, just a link.
- Two competing install paths presented with no guidance.

## 6. Who actually sorts and archives the mail
**The app does the sorting, but only when you manually trigger it — not silently in the background.** Evidence: the menu-bar mock shows an explicit **"Run zero now"** button with a **"Working…"** state, and the "Choose what needs to stay" section states "Run zero from its menu bar to sort connected Gmail accounts. AI applies your rules." There's no scheduling UI or "runs every X minutes" language anywhere on the page, so this reads as an on-demand batch action performed by the AI following your saved rules — not you dragging individual emails, and not a continuously-running background daemon.

## 7. Undo a mistaken archive / what data leaves the Mac
**Undo:** In the Undo tab, restore either a single email (tap the up-arrow icon, tooltip "Put this email back in the inbox") or a full day's batch via "Restore all." The page states "Nothing is deleted," and archived mail can alternatively be recovered directly in Gmail's "All Mail" under a dated recovery label. This part is reasonably clear.

**What leaves the Mac:** Clearly stated — for sorting, TypeSafe's Jev model receives sender, subject, a preview of up to 160 characters, whether you sent the latest message, whether you've replied to that sender before, and your rules/preferences. The page explicitly says no zero server receives your email. Separately (and only if you opt into drafts), an AI coding tool provider (e.g., Claude Code) receives "thread previews, sent-mail samples, writing preferences and saved profile context."

**What's unclear:** whether full email bodies are ever transmitted (the 160-character cap is stated for sorting, but "sent-mail samples" for the drafts feature is vague — how much content, how many messages), whether attachments are touched at all, and whether any of this data is stored/cached by TypeSafe or the draft provider versus discarded immediately. I can't answer this beyond what's stated, since the linked Privacy Policy content isn't included here.

## 8. Ratings (1–5)

| Dimension | Score | Why |
|---|---|---|
| Job clarity | 4 | Hero headline and subhead are clear about function and platform; docked for the muddled Gmail/Apple Mail claim. |
| Ease of following the story | 3 | Logical section order, but the "Before you install" table crams five distinct topics into a dense grid with no visual separation between the three different data recipients. |
| Usefulness of visuals | 3 | Retro UI mockups convey the feel of the app and are honestly labeled as illustrations, but no visual shows an actual sort/archive decision happening, the Undo count doesn't match its own list, and a leftover QA watermark overlaps content. |
| Finding safety/data/requirements/cost info | 3 | Data-sharing specifics are present and reasonably detailed, but no price appears on-page (external link only), and system requirements are minimal. |
| Readiness to decide | 2 | Missing price, unclear silent-install behavior, mismatched counts, and an unpolished visual bug leave too many open questions to commit to running a shell-piped installer. |

## Top 3 presentation fixes, in priority order
1. **Remove the internal QA watermark** ("DRAFT comp · page B · risk-first · Draft3 · not approved") that overlaps live content — it directly undermines trust on a page asking users to run an unnotarized installer.
2. **Fix the Undo panel's count mismatch** (8 set aside vs. 5 rows shown) and clarify scrolling/pagination so the "nothing is deleted" claim is visibly trustworthy.
3. **Add real pricing and a simple data-flow summary** (who gets what: TypeSafe vs. zero vs. optional draft provider) near the top of "Before you install," instead of burying it in a dense two-column table.
