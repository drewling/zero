# Cold-reader comprehension test

Date: 2026-09-29 UTC. Criterion: every reader must describe a Mac app that cleans/manages a Gmail inbox. Model replies are not human usability research or proof of a literal five-second reading time. All nine calls were single-turn, newly created sessions of `claude-sonnet-5`, with no prior conversation resumed. The JSON result files retain actual model ids, session ids, token counts and verbatim replies.

## Results and iteration

| Round | Copy | Reader 1 | Reader 2 | Reader 3 | Acceptance |
|---|---|---|---|---|---|
| 1 | V1 | Category PASS | Category PASS | FAIL: omitted Mac | FAIL, and invalid isolation |
| 2 | V2 | Category PASS | Category PASS | Category PASS | Invalid isolation, not accepted |
| 3 | V2 excerpt unchanged in V3 | PASS | PASS | PASS | Accepted: 3/3 |

V1 readers inferred continuous unattended operation, and one did not name Mac. V2 put Mac in the headline and named the manual Run zero now action. Round 2 reader 1 also named an account not supplied in the prompt. That demonstrates unwanted context in the test harness, not a copy result. Both earlier rounds therefore remain in this record but are not accepted as context-free proof.

Round 3 used a dedicated empty scratch working directory, an explicit replacement system prompt, disabled auto-memory, an empty setting-source list, no tools, empty strict MCP configuration, disabled skills and no session persistence. The returned usage lists 717 input tokens per reader. No tool calls, denials or extra turns were reported, and no unrelated account/product context appears in the answers. This is stronger practical isolation, not a forensic assertion about all internals of the CLI.

Replacement system prompt:

```text
You are a first-time visitor with no knowledge of the product or the person requesting this test. Use only the text in the user message. Answer their comprehension questions in plain words. Do not invent product capabilities.
```

Round 3 invocation (run three independent times; no resume flag):

```sh
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --model claude-sonnet-5 \
  --system-prompt "<replacement prompt above>" --setting-sources "" \
  --tools "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --disable-slash-commands --no-session-persistence --output-format json \
  < cold-reader-round2-prompt.txt
```

## Round 1

Not accepted. Strict category scores were 2/3 and this harness was later shown to carry unrelated context.

### User prompt, verbatim

```text
Clean up your Gmail inbox.

zero is a Mac app that keeps the emails you need to deal with and archives the rest. Undo any archive. Keep using Gmail or Apple Mail.

See what stays. See what gets archived.

A question from a colleague stays. A newsletter gets archived. A payment problem stays. A routine receipt gets archived.

Run zero from your menu bar to sort the Gmail accounts you connect. Open a kept email in Gmail when you're ready to deal with it.

What does this product do, who is it for, and what would worry you?
```

### Reader 1

Model: `claude-sonnet-5`. Session: `23cfe4e0-c00f-4f7e-ba26-c34b379f4898`. Raw evidence: [cold-reader-1.json](cold-reader-1.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
# What it does

Zero is a macOS menu bar utility that connects to your Gmail account(s) and runs a triage pass over your inbox: it classifies each message as either "needs a response/action" (keeps it in the inbox) or "low-priority noise" (archives it). It's explicitly not a replacement for Gmail or Apple Mail — those remain where you actually read and reply to email. Zero's whole job is upstream of that: deciding what deserves your attention in the first place, using signals like sender relationship (colleague vs. mailing list) and content type (a real problem vs. a routine confirmation).

# Who it's for

People with high email volume where the important stuff is buried in noise — newsletters, automated receipts, notifications — and who want an "inbox zero" outcome without manually reading and archiving hundreds of messages themselves. Likely audience: busy professionals, founders, or anyone running multiple Gmail accounts who wants a lightweight background filter rather than a full email client replacement.

# What would worry me

1. **Data access and where classification happens.** To triage every email, the app needs broad read access to your inbox content via OAuth. The critical unanswered question is whether classification runs on-device or is sent to a cloud service/LLM. If it's cloud-based, that means email bodies — including sensitive correspondence — are being transmitted to a third party. This is the single biggest thing I'd want clarified before connecting a real account.

2. **Misclassification risk on the "keep" side.** The examples given (payment problem vs. receipt, colleague question vs. newsletter) are the easy cases. Real inboxes have ambiguous ones — a colleague emailing through a listserv, a "receipt" that's actually a failed-payment notice, a newsletter with a genuinely time-sensitive one-off item. If the classifier defaults toward archiving on uncertainty, something urgent can silently disappear from view.

3. **Whether "archived" actually means "seen."** Undo is nice, but undo requires you to check what got archived. If the workflow doesn't surface a clear, easy-to-scan "here's what I archived, are you sure?" view, most users will never look, and archived-but-wrong items become invisible by default rather than truly reversible in practice.

4. **Opacity of the model.** There's no mention of *why* something was archived or a way to correct/tune the model's judgment over time (e.g., "this sender should always stay"). Without that, trust either never forms or forms blindly.

5. **Ongoing/persistent access.** This isn't a one-time import — it's continuous background access to a live inbox. That's a bigger and longer-lived attack surface than a tool you use occasionally, so the security posture of the app itself (how it stores tokens, whether it's sandboxed, etc.) matters a lot.

Bottom line: the concept is sound and the framing (thin layer on top of Gmail, not a replacement) is the right design choice. The thing I'd actually verify before trusting it with a real inbox is *where the email content goes during classification* — that's the make-or-break detail the pitch doesn't address.
```

### Reader 2

Model: `claude-sonnet-5`. Session: `daed6bdc-7fe2-4ef4-a738-401b0044b256`. Raw evidence: [cold-reader-2.json](cold-reader-2.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
# What it does

Zero is a Mac menu-bar app that connects to your Gmail account(s) and triages your inbox automatically: it archives messages it judges to be low-priority (newsletters, routine receipts) and leaves alone messages it judges to be actionable (a question from a colleague, a payment problem). It's reversible — you can undo any archive action — and it doesn't replace Gmail or Apple Mail; it just runs cleanup passes and lets you open "kept" emails in Gmail when you're ready to act on them.

So functionally: it's an automated inbox-triage layer sitting on top of Gmail, using some judgment (likely an LLM or heuristic classifier) to decide what's "signal" vs "noise."

# Who it's for

People with high email volume who use "inbox = to-do list" as a mental model and are drowning in newsletters/receipts/notifications burying the few emails that actually need a reply or a decision. Likely solo professionals, founders, freelancers — people who don't have an assistant or elaborate filter rules already doing this job, and who want a lightweight, low-setup fix rather than building their own Gmail filters/labels.

# What would worry me

1. **False negatives are the whole risk.** The cost of archiving a newsletter you didn't need is ~zero. The cost of archiving a "kept-worthy" email that got misclassified — a client escalation, a legal notice, a time-sensitive request that doesn't look like a "question from a colleague" — is potentially high, and you may not notice until it's too late, precisely because the tool's job is to keep things out of your sight. Undo helps only if you know to look for what's missing.

2. **Access scope and data handling.** For this to work, the app needs read access to your full Gmail content (or at least metadata/subject/sender/body snippets) to classify messages. Worth knowing: is classification done on-device or sent to a server/third-party model? Is content retained, logged, or used for training? "Connects to Gmail" via OAuth is a broad grant — worth checking exactly what scope it requests (read-only vs. modify vs. full access) and whether it needs "modify" scope to archive (it does) which typically also permits other actions.

3. **Opacity of the classifier.** "A newsletter gets archived, a payment problem stays" are the clean examples in the pitch. The uncomfortable cases are the ambiguous middle: a newsletter you actually read every day, a receipt that's actually a dispute, a colleague's message that reads like an automated notification. Without visibility into *why* something was archived (confidence score, matched rule, etc.), it's hard to build trust or catch systematic errors — you just get a vibe of "seems to work."

4. **Silent failure mode over time.** Early on you'll audit it closely. Weeks in, you'll trust it and stop checking the archived pile. That's exactly when a misclassification does damage — an important email sits archived, unread, for days.

5. **Business model / longevity.** A menu-bar utility connecting to Gmail accounts is the kind of thing that needs either a sustainable pricing model or it risks disappearing, changing terms, or (worse) monetizing data access later. Worth checking who's behind it and how it's funded before granting broad inbox access.

Net: reasonable idea, low switching cost (you keep Gmail/Apple Mail as the interface, and archives are undoable), but the value proposition rests entirely on classification accuracy at the margins — and that's exactly the part that's hardest to verify from the outside.
```

### Reader 3

Model: `claude-sonnet-5`. Session: `557d25b8-8a00-4726-a93f-c71f9a268219`. Raw evidence: [cold-reader-3.json](cold-reader-3.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
## What it does

Zero is a lightweight triage layer that sits on top of Gmail (via your menu bar, not a replacement mail client). It doesn't change how you read or write email — you still use Gmail or Apple Mail for that. Its only job is classification: for each incoming message, it decides "needs your attention" (stays in inbox) or "routine noise" (gets archived). Archiving is reversible, and presumably it shows you both piles so you can audit its judgment.

The examples given suggest it's making a semantic distinction, not just a sender/keyword filter — a "payment problem" and a "routine receipt" might come from the same company, but one needs a human decision and the other doesn't. That implies it's reading and understanding email content, likely with some ML/LLM-based classifier, not just pattern-matching senders.

## Who it's for

People with high email volume dominated by automated/transactional mail (receipts, notifications, newsletters, marketing) mixed in with a smaller number of messages that actually require a decision or reply. Likely individual professionals rather than teams, since it's a personal menu-bar app tied to connected Gmail accounts rather than a shared inbox tool. It's for people who want inbox-zero-style calm without switching away from Gmail's ecosystem or learning a new client.

## What would worry me

1. **Silent false negatives.** The real risk isn't archiving too little — it's archiving something important that looks routine (a colleague replying in a way that resembles a digest, an invoice dispute buried in receipt-style formatting). Since archiving happens automatically and continuously, if you stop spot-checking the archived pile, you may never notice what you missed until it's too late.

2. **Access scope and where classification happens.** To make a "keep vs. archive" call, it needs to read full message content, not just headers — which means fairly broad Gmail OAuth permissions (read + modify/archive). The key question is whether classification runs locally on-device or sends email content to a third-party/cloud service (especially if it's LLM-based). That matters a lot for financial, legal, or health-related mail.

3. **Trust creep.** "Undo any archive" is a good safety valve early on, but the entire value proposition depends on you *not* having to check — which is exactly when you'd stop verifying its calls and a bad classification would go unnoticed longest.

4. **Availability dependency.** It's described as running from the menu bar — worth knowing whether it needs to stay open/running to keep working, what happens on uninstall (do archived emails auto-restore or are you left to manually recover them?), and whether it conflicts with existing Gmail filters/rules you already have set up.

5. **Fuzzy category boundaries.** "Colleague" vs. "newsletter" is easy in the pitch's examples but harder in practice — cross-company collaborators, contractors, or personal contacts outside a recognizable domain could get misclassified by heuristics that work well for obvious cases but poorly at the edges.

None of this is disqualifying — it's a reasonable and common pattern (Gmail's own tabs/Priority Inbox do a cruder version of this) — but I'd want clarity on data handling and a habit of periodically reviewing the archive pile before trusting it fully.
```

## Round 2

Not accepted. All three named Mac and Gmail inbox triage, but reader 1 exposed unrelated account context.

### User prompt, verbatim

```text
Clean up your Gmail inbox on your Mac.

zero is a Mac app that keeps the emails you need to deal with and archives the rest. Undo any archive. Keep using Gmail or Apple Mail.

See what stays. See what gets archived.

A question from a colleague stays. A newsletter gets archived. A payment problem stays. A routine receipt gets archived.

Click Run zero now on your Mac to sort the Gmail accounts you connect. Open a kept email in Gmail when you're ready to deal with it.

What does this product do, who is it for, and what would worry you?
```

### Reader 1

Model: `claude-sonnet-5`. Session: `10912b16-edc6-40b0-9ba3-6cfbfc969b22`. Raw evidence: [cold-reader-r2-1.json](cold-reader-r2-1.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
# zero — What it does, who it's for, and what I'd worry about

## What it does
zero is a Mac app that connects to your Gmail account(s), scans your inbox, and automatically triages messages into two buckets:

- **Keeps** — things it judges need your attention: a question from a colleague, a payment problem, presumably anything that looks like it needs a reply or a decision.
- **Archives** — things it judges are noise-to-you-right-now: newsletters, routine receipts, and similar low-urgency mail.

It does this via an archive action (reversible — "Undo any archive"), and it doesn't replace Gmail or Apple Mail — you still read and reply there. The app's job is purely to pre-sort, not to be a new mail client. You trigger it manually ("Run zero now") rather than it running continuously in the background (at least as described).

## Who it's for
- People with high-volume Gmail inboxes who don't want to build/maintain their own filters and labels.
- Users who already have a mail client they like (Gmail web, Apple Mail) and don't want to switch — zero is a layer on top, not a replacement.
- People who trust "smart" triage more than manual rules, and want an inbox that's closer to zero unread/actionable items without deleting anything.
- Likely a solo user or small-team/freelancer persona — "a question from a colleague" and "a payment problem" as the flagship "keep" examples suggests knowledge workers and small business owners, not enterprise IT-managed accounts.

## What would worry me

**1. It requires broad Gmail account access.** To archive emails, it needs read + modify scope on your mailbox via OAuth. That's a lot of trust to place in a third-party Mac app — worth checking their privacy policy, whether email content is processed on-device or sent to a server/LLM, and whether it's retained.

**2. Classification errors on the "archive" side are the real risk.** Archiving is reversible, but only if you *notice* something was wrongly archived. The failure mode isn't data loss — it's a payment issue or a colleague's question silently sitting in Archived while you assume your inbox is clean. The examples given (colleague question vs. newsletter, payment problem vs. receipt) are the *easy* cases. The hard cases — an automated but urgent security alert, a "newsletter" that's actually a client update, a receipt with a lurking billing error — are where trust breaks down.

**3. Opacity of the model.** Is this a fixed heuristic, a local ML model, or a cloud LLM reading your email content? That materially changes both privacy exposure and how much you can predict/audit its behavior.

**4. "Run now" vs. continuous.** If it's not running automatically, you have to remember to invoke it, which limits how "zero" your inbox actually stays.

**5. Undo granularity.** "Undo any archive" — is that per-email, bulk, or only immediately after a run? If you don't catch a miscategorization same-day, does undo still work cleanly, or does it get buried?

If you're evaluating this for yourself (tayo@drewl.com's inbox), the practical move would be: run it once, manually audit everything it archived for a week or two before trusting it unsupervised, and confirm exactly what data leaves your machine during that OAuth connection.
```

### Reader 2

Model: `claude-sonnet-5`. Session: `0fe606f7-55d5-4c55-9aeb-9aadba6ce542`. Raw evidence: [cold-reader-r2-2.json](cold-reader-r2-2.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
# What Zero Does

Zero is a Mac app that auto-triages your Gmail inbox: it classifies incoming mail into "keep" (things you need to act on or read — questions from colleagues, payment problems, anything that looks like it needs a human decision) and "archive" (things that don't — newsletters, routine receipts, notifications). It archives the second bucket automatically, leaving your inbox with only what it judged important. You still read and respond to email in Gmail or Apple Mail as normal; Zero just runs in the background (or on-demand via "Run zero now") as a sorting layer, and archiving is reversible if it gets something wrong.

# Who It's For

- People with high-volume inboxes drowning in newsletters, receipts, and automated notifications who want the signal without unsubscribing from everything.
- Mac users who don't want to switch email clients or adopt a new inbox paradigm — it's designed to sit on top of Gmail/Apple Mail rather than replace them.
- Anyone who trusts (or wants to test) an automated "important vs. not" classifier rather than manually building filters/rules themselves.

# What Would Worry Me

1. **False negatives are the real risk.** A misclassified newsletter is a minor annoyance. A misclassified "payment problem" or urgent client email that gets silently archived is the failure mode that actually matters — and by design you won't see it in your inbox, so you might not notice until it's too late (missed deadline, angry colleague, unpaid invoice going to collections).

2. **How the classifier works and where.** Does it read email content, and if so, is that processed locally or sent to a cloud service? For something that needs access to your full Gmail inbox (OAuth scope) and reads message content/senders to classify, I'd want to know: is anything sent to third-party APIs (e.g., an LLM backend)? What's retained, and for how long?

3. **Gmail OAuth scope.** To archive/unarchive messages it likely needs broad Gmail API access (read + modify), not just metadata. Worth checking exactly which scopes it requests and whether it can be limited.

4. **Silent action model.** Auto-archiving without a review/approval step (vs. e.g. "suggest archive, you confirm") means errors compound before you catch them, especially if you don't check "what got archived" regularly.

5. **Undo scope and window.** "Undo any archive" — is that per-email, batch, or does it expire? If Zero re-runs and re-archives something you manually un-archived, that's a trust-breaker.

6. **Vendor maturity/trust.** A small app asking for full inbox access is a meaningful trust bet — worth checking who built it, its security/privacy posture, and reviews before connecting a primary email account.

If you're considering it, I'd start by connecting a secondary/less critical Gmail account first, watch what it archives for a week, and see how often you have to rescue something important before trusting it on your main inbox.
```

### Reader 3

Model: `claude-sonnet-5`. Session: `3e4e40c8-ca49-462e-be3d-af80cad10c45`. Raw evidence: [cold-reader-r2-3.json](cold-reader-r2-3.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
# What Zero Does

Zero is a Mac app that automatically triages your Gmail inbox: it decides which emails are worth your attention (keeps them) and archives the rest, based on some model of "importance" (colleague question → keep; newsletter → archive; payment problem → keep; routine receipt → archive). You run it manually ("Run zero now"), review what got archived, undo anything wrong, and then go deal with the kept emails in Gmail or Apple Mail as normal. It's a filter/pre-processor layered on top of your existing mail client, not a replacement for one.

**Who it's for:** People drowning in inbox volume — lots of newsletters, receipts, notifications — who want a lighter, curated view without switching email clients or providers. Likely appeals to people who've tried "inbox zero" methods manually and want automation, but still want to *read and reply* in familiar tools (Gmail/Apple Mail), not a new inbox app.

# What Would Worry Me

**1. Full Gmail account access.** To read, classify, and archive mail, it almost certainly needs OAuth scopes that let it read *everything* — not just metadata. That's a lot of trust for a smaller/newer app. I'd want to know:
- Is classification done on-device or sent to a cloud/LLM backend?
- If cloud-based, is email content (including attachments, financial details, sensitive threads) sent to a third party for classification, and is it retained/used for training?
- What's the data retention and deletion policy?

**2. Misclassification risk, silent failure mode.** The dangerous case isn't "newsletter kept" (annoying but safe) — it's "important email archived and never noticed." Archived isn't deleted, so nothing is lost, but if you don't habitually check what got archived, a client email, an interview request, or an urgent request from a boss could sit unseen for days. The product design (review + undo) mitigates this, but only if you actually do the review every time — which defeats some of the "set and forget" appeal.

**3. Trust calibration over time.** As you learn to trust it, you'll likely stop reviewing archived items carefully. That's exactly when a bad misclassification does the most damage (e.g., a "payment problem" email that looks routine, or a colleague's question buried in a newsletter-style automated system).

**4. Undo ≠ prevention.** Undo helps after you've caught a mistake, but there's no mention of confidence scores, per-sender rules, or a way to correct/train the classifier over time — so you may face the same misclassification repeatedly rather than the model improving from your corrections.

**5. Scope creep / permissions beyond archiving.** If it needs to archive, it may also have send/delete/modify-label scopes it doesn't need — worth checking the exact OAuth consent screen rather than trusting the marketing description.

**Bottom line:** Useful concept if you get real inbox fatigue and want to keep using Gmail/Apple Mail natively, but before connecting an account I'd want clarity on (a) where classification happens, (b) what's stored/retained, and (c) whether there's a low-friction way to audit what's been archived regularly — since the entire safety net depends on you actually doing that review.
```

## Round 3

Accepted. Every reader names a Mac app, Gmail inbox sorting, reversible archives and the manual run action.

### User prompt, verbatim

```text
Clean up your Gmail inbox on your Mac.

zero is a Mac app that keeps the emails you need to deal with and archives the rest. Undo any archive. Keep using Gmail or Apple Mail.

See what stays. See what gets archived.

A question from a colleague stays. A newsletter gets archived. A payment problem stays. A routine receipt gets archived.

Click Run zero now on your Mac to sort the Gmail accounts you connect. Open a kept email in Gmail when you're ready to deal with it.

What does this product do, who is it for, and what would worry you?
```

### Reader 1

Model: `claude-sonnet-5`. Session: `6751f0e7-9fb3-4300-a387-7cd1e9fcdd37`. Raw evidence: [cold-reader-r3-1.json](cold-reader-r3-1.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
Based only on what's written here:

**What it does**
It's a Mac app that connects to your Gmail (and works alongside Apple Mail too) and automatically sorts your inbox — it keeps emails that seem to need your attention and archives the ones that don't. You trigger it manually ("Run zero now"), and archiving can be undone. You keep using Gmail or Apple Mail as normal; this just tidies things in the background/on demand.

**How it decides what to keep vs. archive** (from the examples given):
- Kept: a question from a colleague, an email about a payment problem
- Archived: a newsletter, a routine receipt

So it sounds like it's trying to distinguish "needs a human decision or reply" from "informational/routine" email.

**Who it's for**
Anyone with a cluttered Gmail inbox on a Mac who wants the "important stuff" surfaced and the noise (newsletters, receipts) out of sight — without switching away from Gmail/Apple Mail or committing to a new email client.

**What would worry me / open questions:**
- **How does it actually decide?** The text doesn't say whether this is a fixed rule system, keyword matching, or an AI model reading my email content. If it's AI-based, that means something is scanning the content of my inbox to classify it — I'd want to know what "reading" my mail means for privacy.
- **Access and permissions**: To sort Gmail, it likely needs OAuth access to my Google account. What scope of access does it request (read-only, read/write, ability to archive)? Is my data stored anywhere, or processed only on-device?
- **Accuracy/trust**: "A question from a colleague stays" — but what about a question buried in a newsletter, or an urgent problem that looks routine? Misclassification risk is real, especially since archived items are (presumably) out of sight even if technically undoable.
- **"Undo any archive"** — good that it's reversible, but the text doesn't explain how long undo is available, or whether I'd even notice something important was archived before the undo window matters.
- **No pricing, no data-retention policy, no mention of the company behind it** — nothing here tells me who makes it or what happens to my email data.

I'd want clearer answers on privacy/data handling and the actual classification method before connecting a real Gmail account.
```

### Reader 2

Model: `claude-sonnet-5`. Session: `cbae3065-216e-45ee-8e61-22efcbbb82de`. Raw evidence: [cold-reader-r3-2.json](cold-reader-r3-2.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
Based only on the text you shared, here's my read:

**What it does**
It's a Mac app that connects to your Gmail (and apparently works alongside Apple Mail too) and automatically sorts your inbox: it archives stuff it decides is low-priority (like newsletters or routine receipts) and leaves alone stuff it decides you need to act on (like a colleague's question or a payment problem). You trigger it manually with a "Run zero now" button, you can undo any archiving it does, and you still use Gmail or Apple Mail as normal to actually read/reply to things.

**Who it's for**
Sounds aimed at people with cluttered Gmail inboxes who want the noise (newsletters, receipts, promotional stuff) automatically cleared out without deleting anything, while important messages stay visible. Probably people who get a high volume of email and don't want to manually triage it all.

**What would worry me**
- **How does it decide?** The text doesn't explain the actual logic — is it AI-based, rule-based, keyword matching? "A question from a colleague stays, a newsletter gets archived" are easy examples, but real email is messier. Misclassification risk is my biggest concern — what if it archives something urgent that doesn't fit its pattern?
- **Account access**: To sort Gmail it presumably needs fairly broad access to your inbox (read content, move/archive messages). No mention of what data it sees, stores, or whether anything leaves your Mac.
- **"Undo any archive"** is reassuring, but it's not clear how you'd notice a wrongly archived email in time to undo it, especially if you don't check the archive folder.
- **Manual trigger only** ("Run zero now") — no mention of automatic/scheduled runs, so you'd have to remember to use it, which is a UX limitation for a "clean up your inbox" tool.
- No pricing, no privacy policy, no mention of security/compliance — nothing about who's behind it either.

I'd want to test it on a low-stakes inbox first and check the archived folder for a while before trusting it fully.
```

### Reader 3

Model: `claude-sonnet-5`. Session: `24bc1482-84c9-47ed-80ab-347c3ae6abba`. Raw evidence: [cold-reader-r3-3.json](cold-reader-r3-3.json). Turns: 1. Error: false.

Answer below is verbatim, including mistaken assumptions in invalid rounds:

```text
Based only on what's written here:

**What it does:**
It's a Mac app that connects to your Gmail account(s) and automatically sorts your inbox — archiving things it decides you don't need to act on (like newsletters, routine receipts) and leaving behind things it thinks matter (like a colleague's question, a payment problem). You click "Run zero now" to trigger a sort. If it archives something you actually wanted, you can undo that. You keep reading/replying in Gmail or Apple Mail as normal — this isn't a replacement inbox.

**Who it's for:**
People with cluttered Gmail inboxes who want the noise (newsletters, receipts, etc.) cleared out automatically, but don't want to switch away from Gmail/Apple Mail to do their actual email reading and replying.

**What would worry me:**
- **How it decides "stays" vs "archived"** isn't explained — no mention of rules I can set, AI involved, or criteria beyond a couple of examples. That's the core function and it's a black box here.
- **Accuracy/false positives** — if it wrongly archives something important (not just a newsletter), I'm relying on "undo" to catch it, which means I'd have to check the archived pile regularly, somewhat defeating the point of automation.
- **Access/permissions** — it needs to connect to your Gmail account(s), so I'd want to know what access it requires and whether it reads/stores email content anywhere.
- **No mention of cost, multiple-account handling limits, or whether it works with non-Gmail providers** (only Gmail is mentioned, plus Apple Mail as a client).
- It's described as something you run manually ("Run zero now") rather than automatic/continuous — unclear if there's a background/auto mode or if you always have to trigger it.

I'd want answers on the sorting logic and data handling before trusting it with a real inbox.
```

## Concerns carried into the rest of the page

Readers consistently asked about errors, email access/data flow, undo scope and costs. The later sections already answer these with editable rules and a model-mistake warning, starred/uncertain protection, individual/day restore, explicit sorting/draft data disclosure, and own-provider costs. We do not put every concern into the hero. This test stops at the first demonstration, as the SPEC requests. V3 only shortens later sections and adds illustration strings outside the tested excerpt. Later independent QA must repeat the test on the built page.

