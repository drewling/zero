# 1. What it does / who it's for

**zero** is a free, open-source Mac menu-bar app that scans a connected Gmail account, uses an AI model to archive low-priority mail (newsletters, receipts, cold sales) while leaving important messages in the inbox, and lets you undo any archive — aimed at Gmail users on Apple Silicon Macs who want a self-hosted, non-notarized alternative to built-in email triage.

# 2. Confusing or contradictory points

- **"Undo any archive"** (hero) vs. the Undo screen showing only **"8 set aside · alex@example.com"** for one day — it's unclear whether older runs stay undoable indefinitely or only "your first few runs," which the copy separately warns you to "check."
- **"No zero server receives your email"** vs. **"TypeSafe's Jev model receives sender, subject, a preview of up to 160 characters..."** — this is technically consistent (TypeSafe isn't "zero's server") but reads as a shell game: your data still leaves the Mac to a third party, just not to "zero" itself.
- **"The app is free and open source"** sits directly under **"Sorting cost: Bring your own Jev key, billed by TypeSafe"** — "free" is doing a lot of work here; the actual usage isn't free.
- **Installer section says "may add Homebrew, Python, Node and the Google Workspace CLI"** and **"adds Claude Code if no supported coding tool is installed"** — a Gmail-cleanup utility silently installing a coding agent and package managers is a jarring, unexplained scope jump.
- The **curl | bash** terminal command sits right below "zero is not notarized by Apple," with no explanation of what the script actually does before you pipe it into bash.

# 3. What I'd skip / what feels repeated

- The **inbox illustration mockup** ("Alex Rivera / Priya Sharma...") is repeated almost identically as a static image and then referenced again in captions — it's decorative, not informative, and takes real estate without adding facts.
- **"Nothing is deleted"** and **"stays searchable in Gmail's All Mail"** are stated twice (once in body copy, once implied by the Undo panel) — fine to state once.
- The **"How it works" / "See what went into the archive"** section restates the hero's core promise ("keeps what you need, archives the rest") in more words rather than adding new information until the third paragraph (Undo mechanics).

# 4. Missing information before deciding

- What exactly the install script does beyond adding Homebrew/Python/Node/Claude Code — no list of permissions, disk footprint, or uninstall path.
- Whether Gmail's own filters/labels interact with zero's archiving, or if the two can conflict.
- What happens to sorting if you have multiple Gmail accounts — does each need its own Jev key/billing?
- Rough cost of the Jev key usage (link to "TypeSafe pricing" is unfollowable here — no numbers shown).
- Retention: how long "under a dated recovery label" mail stays before Gmail's own retention rules apply.
- Any word on macOS Intel support (only "Apple Silicon" is stated) — no fallback mentioned.
- Whether "Optional drafts" is on by default or something you must explicitly enable.

# 5. What would make me install vs. leave

**Would install:**
- Clear confirmation that archiving is reversible and low-risk (partially shown).
- A pricing example for TypeSafe's Jev key so I know real monthly cost.
- Confidence that the installer's extra components (Homebrew/Node/Claude Code) are scoped, removable, and explained.

**Would leave:**
- *Product/security tradeoff:* Unnotarized installer + curl|bash pattern + silent install of unrelated dev tooling (Homebrew, Node, Claude Code) for a "simple" inbox cleaner — disproportionate system footprint for the stated job.
- *Product/security tradeoff:* Third-party model (TypeSafe) sees message metadata/content preview even though "zero" itself doesn't — data leaves the Mac either way.
- *Page-presentation problem:* No real pricing numbers, only a link — makes cost impossible to judge on this page alone.

# 6. Who sorts and archives the mail

**A background AI model run that you manually trigger.** Evidence: "Start a run from zero's menu bar" (you initiate it) and "An AI model uses your rules to keep..." (the model decides, not you dragging emails). There's also a "Run zero now" button in the mock menu-bar UI, confirming it's a triggered batch process, not continuous background monitoring and not manual dragging by the user.

# 7. Undo mechanics and data leaving the Mac

**Undo:** In zero's Undo tab, you can restore one email via a per-item button, or click "Restore all" for a whole day's archived batch. The text states archived mail "stays searchable in Gmail's All Mail under a dated recovery label," implying restoration re-labels/re-inboxes the message in Gmail itself — but the exact mechanism (does it remove the archive label, move it back to inbox, or just point you to search it manually?) **is not fully specified.**

**What leaves the Mac:** According to "Sorting data," TypeSafe's Jev model receives: sender, subject, up to a 160-character preview, whether you sent the last message, whether you've replied to that sender before, plus your rules and learned preferences. The page states "No zero server receives your email," but does **not** clarify whether "your email" means the full body is withheld while metadata/preview goes to TypeSafe, or something else — this distinction is left **unclear rather than fully answered**, so I won't guess further. Separately, if optional drafts are used, thread previews, sent-mail samples, and profile context go to whatever coding-tool provider (e.g., Anthropic via Claude Code) you've connected.

# 8. Ratings (1–5)

- **Job clarity: 4** — hero line and first section make the core function clear quickly; only the run-trigger mechanics need inference.
- **Ease of following the story: 3** — logical order (hero → how it works → before you install → install), but the "Before you install" section crams five distinct risk categories into a dense grid that requires careful reading, breaking the narrative flow.
- **Usefulness of visuals: 2** — inbox/Undo mockups are labeled "illustration, made up" and add little beyond what the text already says; they don't show the actual rules UI, actual archive volumes, or real cost/settings screens, which would've been more useful.
- **Finding safety/data/requirements/cost info: 3** — it's all consolidated in one grid (good), but "Sorting cost" links out with no numbers, and installer side-effects (Homebrew/Node/Claude Code) are stated but not justified or scoped.
- **Readiness to decide: 2** — missing pricing, unclear undo scope beyond "first few runs," and unexplained installer footprint leave real gaps before committing.

# Top 3 presentation changes (priority order)

1. **State actual Jev/TypeSafe pricing on the page** (e.g., "$X per 1,000 emails sorted") instead of only linking out — cost is central to a go/no-go decision and currently requires leaving the page to learn.
2. **Justify or scope the installer's side effects** — explain *why* a Gmail-sorting app needs Homebrew, Python, Node, and Claude Code, and confirm these are removable/optional, right next to the "Installer" note rather than as a bare list.
3. **Clarify Undo's actual limits** — state explicitly how many days/runs remain undoable, and what "restore" technically does in Gmail (label removed? moved to inbox?), since "Undo any archive" in the hero currently overpromises relative to the "check your first few runs" caveat later.
