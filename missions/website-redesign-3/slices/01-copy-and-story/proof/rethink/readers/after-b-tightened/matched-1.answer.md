# zero — Landing Page Critique

## 1. What it does, for whom
Zero is a Mac menu-bar app that uses an AI model (Jev, via TypeSafe) to automatically archive low-priority Gmail messages into a reversible "undo" bucket, for Gmail users who want their inbox to only show emails that need action.

## 2. Confusing or contradictory elements

- **"No zero server receives your email" vs. sending data to TypeSafe.** The sorting-data box says sender, subject, and a 160-character preview go to TypeSafe (Jev). That preview *is* email content. The reassurance is narrowly true (no "zero server") but reads as if no third party sees your email at all — a meaningful distinction buried in wording.
- **"Free, open-source app (AGPL-3.0)"** sits directly under "Sorting cost... $0.042 per million input tokens" — the app is free, but running it isn't really free since you pay per-token API costs. The juxtaposition implies "free" more broadly than it is.
- **Trash icon in the hero illustration.** The hero graphic shows a Trash can alongside "Auto-Archived" folder, but the copy insists nothing is ever deleted, only archived. Why is Trash pictured at all? It's never explained and contradicts the "nothing is deleted" promise made later.
- **"zero is a Mac app" vs. curl/bash Terminal install.** The final CTA is a shell script piped into bash — not a typical Mac app installer (.dmg/.pkg). This is a bigger trust/expectation gap for anyone who isn't a developer, especially paired with "May add Homebrew, Python, Node..."
- **Claude Code appears twice with different framing.** "Before you install" says Claude Code is added "only if no supported coding tool is installed" (implying it's a fallback dependency for drafts). But drafts are explicitly labeled "Optional." So why is a coding tool being silently installed for an "optional" feature at all?

## 3. What I'd skip / what's repeated

- **Repeated inbox illustration** (hero + "Choose what needs to stay" section) shows the same 4 fictional names with no new information the second time.
- **"Undo any archive" is stated at least three times** (hero copy, Settings section, Restore section) without adding detail until the very last mention.
- **The mobile "How it works / Undo / Before you install / Source" nav row** at the very top adds no value if I never scroll to a table of contents — it could be a persistent nav, but as a static screenshot element it's just clutter before I've read anything.

## 4. Missing information before deciding

- **What "Jev" actually is.** Is it Claude, GPT, a custom model? "Jev 1.13" is never defined — I don't know whose model is reading my email subject lines and previews.
- **How much this costs in practice.** Token pricing is meaningless without an estimate (e.g., "~$X/month for a typical inbox of Y emails/day").
- **What happens with Apple Mail specifically.** The page says "Keep using Gmail or Apple Mail," but all screenshots show only a Gmail-style inbox. Does Apple Mail get archived too, or only reflect changes made via Gmail?
- **Data retention/deletion policy** for what TypeSafe stores (the 160-char previews, "learned preferences") — is it stored indefinitely? Can I delete it?
- **How "Restore all" scoping works** — does it restore only one day, or is there a way to restore everything at once across many days?
- **What happens if I never review Jev pricing changes** — is there a spending cap or warning before charges scale up?

## 5. Install vs. leave

**Product/security tradeoffs:**
- Would install if: the "Jev" model were named/identified, cost estimates were concrete, and I trusted a non-notarized installer piping curl|bash with silent dependency additions (Homebrew/Python/Node/Claude Code).
- Would leave because: **non-notarized installer + curl|bash + auto-installs developer tooling** is a real security red flag for a "consumer" Gmail cleanup tool. That's a legitimate product-level reason to walk away, regardless of how well it's explained.

**Page-presentation problems (separate from the above):**
- Trash icon contradicting the "nothing deleted" promise is a presentation bug, not a product flaw — but it would make me second-guess everything else on the page.
- Unclear pricing math is a presentation gap, not necessarily a hidden cost problem.

## 6. Who actually sorts and archives the mail?

**The app does it, but only when you actively click "Run zero now"** — not a silent background daemon, not you dragging.
Evidence: The hero mock shows a "zero ... Run zero now" popover as a discrete button. The "Choose what needs to stay" section explicitly says "Use **Run zero now** to sort connected Gmail. AI applies your rules." This is a triggered action, not described anywhere as continuous/automatic monitoring. There's no visual or text indication of a background/scheduled process (no "runs every hour," no menu toggle for auto-run shown).

## 7. Undo and data leaving the Mac

**Undo:** In the Undo tab, you can restore a single email (via the icon button next to each item) or use "Restore all" to restore an entire day's batch. The text says "Nothing is deleted. Archived mail stays searchable in Gmail's All Mail under a dated recovery label" — so archiving appears to be a Gmail label change, and undo reverses that label.

**What leaves the Mac:** According to the "Sorting data" box, TypeSafe (running Jev) receives: sender, subject, a preview of up to 160 characters, whether you sent the latest message, whether you've replied to that sender before, and your rules/learned preferences. If you use optional AI drafts, thread previews, sent-mail samples, writing preferences, and saved profile context go to your separate coding-tool provider (e.g., Anthropic via Claude Code).

**Unclear:** Whether the "preview of up to 160 characters" could include sensitive content since it's pulled from the email body/subject — the page doesn't say how this preview is chosen (first line? most relevant sentence?) or whether attachments/metadata like recipient CC lists are included. I won't guess further.

## 8. Ratings (1–5)

| Category | Score | Why |
|---|---|---|
| Job clarity | 4 | Hero copy is clear and concrete in one sentence; only the Apple Mail interaction is fuzzy. |
| Ease of following the story | 3 | Logical top-to-bottom flow, but repeated illustrations and the Trash/no-delete contradiction disrupt trust in the narrative. |
| Usefulness of visuals | 3 | Mock UI screens (Settings rules, Undo list) are genuinely helpful for understanding mechanics; the hero inbox illustration is decorative and adds little. |
| Finding safety/data/requirements/cost info | 3 | It's all present in one consolidated "Before you install" block (good), but pricing lacks real-world estimates and "Jev" is unidentified. |
| Readiness to decide | 2 | Core mechanism is clear, but curl|bash installer, unnamed AI model, and unclear Apple Mail support leave real gaps before I'd commit.

---

## Top 3 presentation changes (priority order)

1. **Remove or explain the Trash icon.** It directly contradicts "nothing is deleted" and undermines the entire undo-safety pitch — this is the single most damaging inconsistency on the page.
2. **Identify "Jev" and give a real-world cost example.** Naming the underlying model and showing "~$X/month for a typical inbox" would resolve the biggest transparency gap without changing the product.
3. **Reconcile the "Mac app" framing with the curl|bash Terminal installer.** Either show a standard .dmg/notarized flow or clearly explain upfront (near the hero CTA, not buried in "Before you install") why a consumer utility requires shell-script installation and dependency additions.
