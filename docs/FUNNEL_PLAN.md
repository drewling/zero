# zero — funnel plan

> Positioning, audience, ladder, and a section-by-section rewrite brief for the
> landing page, under the new business model (free self-hosted + a future hosted
> tier). Strategy only. No code in this doc; nothing here edits the app.
>
> Written 2026-09-17. Sources: `PRODUCT.md`, `README.md`, `keep-policy.md`,
> `landing/index.html`, `landing/llms.txt`, `docs/JEV_MIGRATION_PLAN.md`,
> `docs/GOOGLE_VERIFICATION.md`.

---

## 0. Two things that outrank everything else in this doc

Before the funnel: two facts in the repo will break a successful launch. Fix
them first or the rest is wasted motion.

**1. The 100-user lifetime cap is a hard ceiling on the whole funnel.**
`docs/GOOGLE_VERIFICATION.md` says zero runs "production + unverified" under
Google's 100-user cap, and CASA verification was declined at ~$1,800/yr. That
means user 101 cannot sign in. A Show HN that goes well produces 100 sign-ins in
an afternoon. The funnel's realistic best case is currently a **failure mode**.

Three options, pick one before launching:
- **Ship BYO-OAuth-client as the documented free path.** The user creates their
  own Google Cloud project and pastes their own client JSON. Removes the cap
  entirely, adds ~10 minutes of setup, and is honest with the audience we're
  actually targeting. This is the recommended one.
- **Pay for CASA** ($1,800/yr) before launch. Only sane if the hosted tier is
  real and already selling.
- **Cap the launch on purpose.** "First 100 people" as a genuine, stated limit.
  Turns the constraint into scarcity that is actually true. Works once.

Do not launch wide on a bundled client with 100 seats and no plan.

**2. "Open source" is not accurate under the current license, and this is a
launch risk, not a nitpick.**

`LICENSE` is PolyForm Noncommercial 1.0.0. That is **source-available**. It is
not open source under the OSI definition, because it restricts commercial use,
and field-of-use restrictions fail OSD clause 6. The audience being targeted —
HN, r/opensource, r/selfhosted — knows this precisely and enforces it socially.
A Show HN titled or framed as "open source" under PolyForm-NC produces a top
comment that is about licensing, not about the product. That comment sets the
tone of the entire thread, and the thread is the launch.

There are exactly two honest resolutions. Pick one before any copy is written.

**Option 1 — change the license to AGPL-3.0. Recommended if "open source" is
genuinely wanted.**
AGPL-3.0 is OSI-approved, so "open source" becomes true with no asterisk. It
also does the job people usually reach for PolyForm-NC to do: anyone who runs a
modified zero as a network service must publish their source, which makes a
closed competitor SaaS clone unattractive. Critically for §3, AGPL does **not**
stop you selling the hosted tier — you hold the copyright, so you can license
your own hosted build however you like, and you can dual-license. AGPL is the
standard choice for exactly this shape of business (open core plus a hosted
tier) and the audience recognises it as such.

The real cost: some companies ban AGPL internally, so a few users will not
install it at work. For a personal-inbox Mac tool that is close to irrelevant.
Apache-2.0 would maximise adoption but gives away the anti-clone protection for
nothing in return; do not pick it here.

**Option 2 — keep PolyForm-NC and never write "open source" anywhere.**
Use "free and source-available" in the hero pills, README, llms.txt, Show HN
body, Product Hunt copy, and every Reddit post. Add one FAQ line: "It is
source-available under PolyForm Noncommercial, not OSI open source. You can read
it, run it, and modify it for yourself. You cannot sell it." Stating the limit
yourself defuses the objection entirely; being corrected on it does the reverse.

**The recommendation: Option 1, relicense to AGPL-3.0.** The word is worth more
than the restriction. "Open source" is a distribution asset in every channel in
§2 — it gets the directory listings, the awesome-list entries, the newsletter
pickups, and the benefit of the doubt on HN — and AGPL preserves essentially all
the practical protection PolyForm-NC was bought for. If relicensing is off the
table for any reason, Option 2 is fine and costs little, but it must then be
applied with zero drift across every surface. The one unacceptable path is
PolyForm-NC plus "open source" in the copy.

One caveat if relicensing: if there are outside contributors already, their
contributions need their sign-off to relicense. Check `git log` for non-founder
authors first. If it is a solo repo, this is a one-commit change.

---

## 1. The dream customer

### The you-five-years-ago read

The founder is a technical person running three or more Gmail accounts, already
comfortable with a terminal, already paying for Claude, and already losing
things. That person is the avatar. Do not invent a second one.

**Name:** call him Dan. 34. Senior engineer or solo technical founder or a
contractor with clients. Mac, Apple Silicon, upgrades to new macOS quickly.
Lives in three to five Gmail accounts: one work, one personal, one for the side
project, one dead domain from a company that folded, one shared with a partner.

**What he actually does all day with email:**
- Opens Gmail to check one thing. Leaves 20 minutes later with nothing done.
- Has 4,000 unread in one account and pretends that account doesn't exist.
- Reads on his phone, marks something unread to deal with later, never does.
- Once lost a client invoice under a pile of Notion digests and Stripe payout
  summaries. It cost him money and he still remembers it.

**The pain, in his words** (this is the copy source, do not translate it):
- "I'm not behind on email. I'm behind on *knowing* whether I'm behind."
- "I have four inboxes and none of them are real."
- "I've tried filters. I spend more time maintaining filters than reading mail."
- "Every AI email tool wants to be my new email app. I don't want a new email app."
- "I'm not letting some startup read my mail."
- "I'll archive it and then I'll never find it again."

**The false belief the story must overturn:**
> "Anything that automates my inbox will eventually lose something important,
> and I will only find out when it is too late."

This is the whole belief. It is why he still does it by hand. Every trust claim
on the site exists to break exactly this one sentence, and reversibility is the
crowbar. Note the shape: he does not disbelieve that AI can sort mail. He
disbelieves that it is *safe*. Copy that argues "our AI is smart" argues against
the wrong objection.

**Secondary false belief, newer and rising:**
> "This is a thin wrapper. I could build this in a weekend."

He could build the sort loop in a weekend. He could not build reversible archive
semantics, multi-account auth, a menu-bar UI, undo, and a calibrated keep-bar in
a weekend, and he will never actually do it. The counter is not to argue. It is
to show the install command and let the two minutes beat the weekend.

**The psychographic trait that predicts follow-through:**
Not "busy" and not "productivity nerd." The predictor is **he already runs
things on his own machine.** He has a Homebrew list he's proud of. He self-hosts
something. He pastes `curl | bash` without flinching (and reads the script
first, sometimes). That trait predicts he will survive the unverified warning,
get a key, and finish setup. The GTD-app-hopper who wants a pretty inbox will
not, and will leave a bad review about "too technical." Select for the first
guy; the second guy is the hosted tier's customer later, not now.

**Who this is explicitly not for, and say so:**
- Outlook, iCloud, Fastmail, Proton. Gmail only.
- Non-technical people, until the hosted tier ships.
- Anyone who wants real-time. It runs once a morning by design.
- Anyone who wants an inbox that answers mail for itself.

Naming the non-customer out loud is the cheapest conversion tool on the page. It
makes every other claim more believable.

---

## 2. Where he congregates (Dream 100)

The rule: he is already gathered somewhere. Go to the pond. Nothing here is a
paid channel, because there is nothing to pay for yet.

### Tier 1 — the launch channels that can actually move the needle

**Hacker News.** This is the single highest-leverage pond for this exact
product, because the avatar and the HN median user are the same person, and
because the honest-friction story (see §5) is a genre HN rewards.

Verified from <https://news.ycombinator.com/showhn.html>:
- Show HN is for something people can *run*. zero qualifies; a landing page
  would not. "Please don't post landing pages or fundraisers" is explicit. This
  means **do not Show HN the waitlist.**
- "Please make it easy for users to try your thing out, ideally without barriers
  such as signups or emails." The one-line installer satisfies this. A gated
  download would not.
- "Please don't ask friends to upvote or comment." No vote-ring. None.
- "New features and upgrades generally aren't substantive enough." So there is
  one Show HN, not a series.

Timing: the community-reported consensus is a **weekday morning US Eastern,
roughly 8–10am ET, Tuesday through Thursday**, to catch the US-morning /
EU-afternoon overlap while the new-submissions queue is still shallow. Some
analyses argue Sunday gives the best odds of surviving because competition is
thinner. This is all folklore built on observed ranking, not on a published
rule, so treat it as a tiebreak and not a strategy. What actually decides it is
upvote velocity in the first 30–60 minutes and whether the maker is in the
thread answering.

Title format: `Show HN: zero – a macOS menu bar app that keeps only the email
that still needs you`. Plain, no adjectives, no "AI-powered," en dash, under
80 chars. What kills Show HN posts: marketing voice in the title, a title that
hides what it is, a signup wall, absent maker, and defensive replies. The
number-one predictor of a good outcome is the maker answering the hostile
comment well within ten minutes.

**Lobsters** (<https://lobste.rs>). Smaller, harsher, higher signal. Invite-only
to post, so line up an invite in advance or skip. Do not post the same hour as
HN.

**Reddit.** These are the specific subs where he already is. Read each sub's
rules first; most of these ban naked self-promo and several require a flair or
a "I built this" framing:
- r/macapps — the single best-fit sub. Explicitly welcomes developer self-posts
  when labelled. Start here.
- r/MacOS, r/apple (strict, mostly news), r/macsysadmin
- r/selfhosted — strong fit for the "runs on your machine, your keys" angle.
  Note it leans toward server software; frame it as local-first, not SaaS.
- r/opensource, r/degoogle (partial fit, they will object to Gmail)
- r/SideProject, r/IndieHackers, r/EntrepreneurRideAlong
- r/productivity, r/getdisciplined, r/gtd (softer fit; less technical)
- r/gmail, r/GoogleWorkspace, r/Emailmarketing (no — wrong side of the market)
- r/LocalLLaMA, r/ChatGPTCoding, r/ClaudeAI, r/OpenAI, r/AI_Agents — the "agent
  that does one real job" framing plays well here
- r/swift, r/SwiftUI, r/Python — technique posts, not product posts
- r/commandline, r/homelab, r/privacy, r/Python
- r/consulting and r/freelance — the multi-account pain is sharpest here

Realistic read: r/macapps, r/selfhosted, r/SideProject and r/ClaudeAI are the
four worth real effort. The rest are one post each, at most.

**Product Hunt.** Worth doing, with reduced expectations. Current mechanics
(verified against 2026 launch guides, corroborating each other):
- The hunter-boost weighting was removed; self-hunting ranks the same. Pay
  nobody for a hunt. A hunter only matters if their audience genuinely overlaps.
- Posts go live at 12:01am PT regardless of submission time. Submit the evening
  before; sleep.
- Tue–Thu = most traffic and most competition. Sat/Sun = least of both and
  better odds of a top-5 finish for a niche tool. For zero, **Sunday or Monday**
  is the better bet.
- Dev-tool categories need roughly 700–1200 upvotes for #1 and that is not the
  goal. Realistic outcome for a free Mac tool: a few hundred visits, a permanent
  backlink, and a second audience for the waitlist.
- Do not DM people for upvotes. PH deranks it.

### Tier 2 — the Dream 100 list (audience owners, not customers)

Work your way in over weeks, do not cold-blast on launch day. The pattern that
works: use the tool, write something genuinely useful, mention it once.

*Mac and indie-app press and newsletters:*
MacStories / Club MacStories, Six Colors, Daring Fireball, The Sweet Setup,
Macworld's Mac apps coverage, iMore, 9to5Mac, MacRumors, Cult of Mac, Indie Mac
User, Mac Power Users (Relay FM), Automators (Relay FM), Mac Geek Gab.
Route: most take tips at a public tips@ address; Relay shows take listener
submissions. Send a two-sentence note and a 30-second screen recording, not a
press release.

*Dev / indie-founder newsletters:*
TLDR, Console.dev (specifically covers new dev tools and loves this shape),
Changelog News + the Changelog podcast, Bytes/JavaScript-adjacent lists,
Hacker Newsletter, Indie Hackers newsletter, Software Lead Weekly, Pointer.io,
Ben's Bites and The Rundown (AI-side), Dense Discovery, Refind.

*Directories that compound quietly:*
alternativeto.net (create the listing yourself; it ranks), MacUpdate, Homebrew
cask submission, the `awesome-macos` / `awesome-mac` / `awesome-selfhosted`
GitHub lists, Uneed, BetaList, and r/macapps' own wiki.

*People and channels:* Mac indie-dev and AI-tooling accounts on X and YouTube —
target by *overlap* not follower count. The test is whether their audience
already runs CLIs on a Mac. A 12k-follower account whose whole feed is
Claude-Code workflows is worth more than a 400k general-tech account.

I am not going to invent a list of twenty handles I cannot verify from here.
Build the list the correct way instead, in an afternoon: open the follower lists
of the five Mac indie devs you already read, take every account that appears in
three or more of them, and you have a real Dream 100 with overlap already
proven. Do the same on YouTube with "Claude Code" and "menu bar app" searches
sorted by date.

*Communities:* the Claude/Anthropic Discord, indie-Mac-dev Slacks and Discords,
Indie Hackers, the Rands Leadership Slack (no promo, relationships only),
and any Discord for the agent CLIs zero supports.

### The one congregation nobody else is serving

People who already installed an agent CLI and are looking for something real to
point it at. That group is large, new, under-served, and exactly matches "bring
your own CLI." It is also the only congregation where the free tier's friction
is a *feature* rather than a tax. Bias the launch toward it.

---

## 3. The value ladder — and why $4.99 is the wrong number

### The ladder as it should be

| Rung | Offer | Price | What it buys | Job in the funnel |
|---|---|---|---|---|
| 0 | keep-policy.md + the "three questions" as a public artifact | free, no email | A better way to think about the inbox | Ranks, gets linked, costs nothing |
| 1 | zero, self-hosted | free (you pay ~$0.0025/run in Jev + your own CLI) | The whole product, honestly | **The first yes** |
| 2 | zero hosted | see below, not $4.99 | No keys, no CLI, no warnings, no terminal | **The second yes** |
| 3 | zero for a team / shared inbox | $15–25 per seat | Same job across support@, billing@, a founder + EA | The only real rung above |

### The first yes and the second yes

**The first yes is not the download. It is the first morning.** The moment the
product works is when he wakes up, glances at the menu bar, sees three things
instead of forty, and does not panic. Everything upstream exists to get him to
one completed run. That means the install command and the first-run flow are the
funnel, more than the copy is.

**The second yes is earned by the free tier working and then annoying him.**
That is the whole ascension mechanism, and it is unusually clean here:

- He installs free. It works. Trust is established by his own mail, not by copy.
- Then he hits the friction on his own schedule: he re-auths on a new Mac, or a
  key expires, or he wants it on his laptop too, or he wants to put his
  non-technical co-founder on it, or he just gets tired of being the sysadmin
  for his own inbox.
- At that exact moment, "we run it, nothing to set up" is worth money.

Do not pitch hosted to a stranger. Pitch it to someone who has already had
thirty good mornings. The site seeds it; the app converts it.

### Why $4.99/month is wrong — this is a real call, not a nitpick

**1. It is below the cost floor you already documented.** Ungated Gmail access
needs CASA at ~$1,800/yr (`GOOGLE_VERIFICATION.md`). Add hosting, add Jev, add
an LLM for drafting (drafting stays a text model per `JEV_MIGRATION_PLAN.md`,
and that is the expensive call, not the classification). Then add the thing
nobody budgets: **support for a product that touches people's email.** One
"where did my mail go" ticket eats a year of one subscriber's revenue. Payment
processing alone takes about 9% of a $4.99 charge before anything else.

**2. It prices the wrong thing.** The hosted tier does not sell inbox sorting.
The free tier already does that, perfectly, forever. The hosted tier sells
*never touching this again* to someone whose hour is worth $100+. That is not a
$4.99 feeling. $4.99 is the price of a thing you cancel in month three because
you forgot you had it.

**3. It is a one-way door.** Raising from $4.99 to $12 later means either
grandfathering forever or annoying your first and best users. Starting at $12
and discounting for founding users is the same money with the opposite optics.

**4. $4.99 signals toy.** Against Superhuman at $30/mo and SaneBox at ~$7–36/mo,
a $4.99 AI agent with access to your entire mailbox reads as unserious. Price is
a trust signal in the security category, not just a number.

**The recommendation:** price the hosted tier at **$12/month or $99/year**, and
offer the waitlist a real founding rate — say **$7/month locked for life for the
first 100** — which is where the $4.99 instinct actually belongs. The founding
rate does three jobs: it makes the waitlist worth joining today, it creates
honest scarcity you can actually honour, and it leaves list price intact.

Test the ceiling rather than assuming it. Put **one question in the waitlist
form**: "what do you pay for email tools today?" You will have the answer in a
month, for free, from the only people whose opinion counts.

### The license is a hidden line item on this ladder

PolyForm-NC does not block you selling the hosted tier — you own the copyright.
But it does have a cost that shows up nowhere on a P&L: **it deters
contributors.** A one-person product with a two-rung ladder depends on free
labour more than it depends on upsells. Under a noncommercial license, the
people most likely to send a good PR (other indie devs, the exact avatar) read
"I cannot ever use this commercially" and close the tab. Nobody argues; they
just do not contribute, and you never see the PRs you did not get.

Price that against the ladder. Rung 1 is free and its only return is
contributors, stars, feedback, and word of mouth — every one of those is
suppressed by the license. Rung 2 is unaffected either way. So PolyForm-NC costs
you at the rung where you need help and protects you at the rung where you
already had protection. That is the same conclusion §0 reached from the
messaging side, arriving from the economics side: **relicense to AGPL-3.0.**

### Is there anything above rung 2? Honestly, maybe not

Rung 3 (teams / shared inboxes) is real but it is a different product with a
different trust story, and it is years away for one person. Do not design for it
now. Be honest with yourself: this is most likely a **two-rung ladder**, which
means the money comes from retention and not ascension. For a two-rung ladder
the important discipline is not upselling, it is **never going quiet** — a
monthly changelog email to everyone who ever installed, forever. That single
habit is worth more than a third rung you never build.

---

## 4. Hook, story, offer for the landing page

### Three headline options

**Option A — keep the current one.**
> **An inbox you can finally ignore.**

The best of the three. Short, plain, third-grade, and it names the outcome he
actually wants (permission to stop checking) instead of the mechanism. It also
sidesteps the "inbox zero" category, which is exhausted. *Weakness:* it does not
say Gmail, Mac, or agent, so the sub-headline is carrying a lot. Keep it and fix
the sub-headline.

**Option B — the loss angle.**
> **Stop checking. Nothing goes missing.**

Two short sentences, and the second one answers the objection inside the hook
itself. This is the single most on-belief headline available, because the false
belief is "it will lose something." *Weakness:* slightly defensive. It raises
the fear in order to kill it, and some readers only hear the fear.

**Option C — the multi-account angle.**
> **Four inboxes. Three things that need you.**

Most specific, most self-selecting, and it speaks directly to the avatar's
actual life instead of to "email" in general. Anyone with one inbox bounces,
which is correct. *Weakness:* it is a narrower net, and it reads as a stat
rather than a promise.

**Pick A, with B as the sub-headline.** A stops the scroll on outcome; B closes
the belief gap immediately underneath it. C becomes the multi-account section
headline further down the page, where it is perfect.

### The story beat

Three sentences, told once, on the page, in first person. Not a founder essay.

> I had four Gmail accounts and I checked all of them all day. Not because
> anything was urgent, but because I could not tell if something was. So I built
> a thing that reads every thread each morning, leaves the few that need me, and
> files the rest where I can always get them back. Nothing is ever deleted. That
> is the only reason I trust it.

That last line does the work. The belief being rewritten is not "AI can sort
mail." It is "a machine touching my inbox will cost me something." Reversibility
is the answer, and it is a *design property* rather than a promise, which is
why it converts.

### The offer stack (free tier)

Stated plainly, in his language:

- Every Gmail account you own, read every morning — **no per-account price**
- Only the threads that still need you stay in the inbox
- Everything else archived with a dated label, **never deleted**
- One tap restores an entire day
- A reply drafted in your voice when *you* ask, never sent for you
- Your keep-rule is one file of plain English you can edit
- Runs on your Mac, on your keys. No account, no server, nothing uploaded
- Read every line of the source before you run it
- Cost: about a quarter of a cent per morning run, paid to the model provider,
  not to us

Then the honest half, which is part of the offer and not a disclaimer:

- You will see a macOS "unidentified developer" warning. The installer handles it.
- You will see Google's "this app isn't verified" screen. You click Advanced.
- You need an API key and an agent CLI you already have or can install in a minute.
- If you would rather not do any of that, join the list for the hosted version.

That last bullet is the whole funnel in one line: the friction disclosure *is*
the waitlist's call to action. This is what makes the honesty compound instead
of just costing you installs.

### The offer stack (hosted tier, waitlist only)

- Everything above
- No keys, no CLI, no terminal, no warnings
- Works on every Mac you sign into
- One price, all your accounts

Say what it costs (or "around $12/month"), say it is not built yet, and give no
date. Then stop. Any promise beyond that is a debt you pay in credibility.

---

## 5. The honest-friction question — lead with it

This is the most important call in the doc, so here is the argument in full.

**The decision: lead with the friction. Name it above the install command, in
plain words, before he types anything.** Not buried in an FAQ, not in a
`<details>` block, not "advanced setup."

### Why

**1. Hidden friction on this product fails silently, which is the worst
possible failure.** zero is a menu-bar app with no window. If Gatekeeper blocks
it, *nothing visibly happens.* The user double-clicks, sees nothing, concludes
the app is broken, and leaves. The README already understands this ("because
zero is a menu-bar app with no window, the block is invisible"). A user who was
warned and hits the warning is executing a step. A user who was not warned and
hits it is a lost install and a bad first impression you never get to answer.

**2. The friction is the proof of the privacy claim.** "Your keys, your machine,
no server" and "you have to supply a key" are *the same fact*. The site
currently states the benefit and hides the cost, which makes both feel like
marketing. Stating them together — "there is no server, which is why you bring
the key" — converts a tax into evidence. This is the single strongest move
available on the page.

**3. The audience punishes concealment far harder than it punishes friction.**
This launches on HN, r/macapps, and r/selfhosted. Those readers install
un-notarized software weekly. What they react badly to is a page that reads
smooth and a setup that reads rough. The top comment writes itself either way;
you choose which one. And a page that says "you will see a scary Google screen,
here is exactly why, here is what we decided and what it cost" *is* the
Show HN story. It is more interesting than the product.

**4. Unwarned warnings destroy trust exactly where you cannot afford it.** You
are asking for `gmail.modify`. If the first surprise in the flow is a security
warning the site never mentioned, every trust claim on that page retroactively
becomes suspect. Pre-warning inverts it: you predicted the scary thing, so you
are the trustworthy narrator when it appears.

**5. Friction is the qualifier that builds the right first hundred.** Per §0
there may literally be only 100 seats. Those seats should go to people who can
survive setup and give useful feedback, not to people who will bounce at the
Gatekeeper dialog. The friction disclosure is free segmentation.

**6. Friction is the hosted tier's entire sales argument.** You cannot sell
"no keys, no CLIs, no warnings" to someone who has never been told there are
keys, CLIs and warnings. Hiding the friction on the free page silently deletes
the value proposition of the paid page. The two decisions are the same decision,
and this is the part most people miss.

### The case against, taken seriously

Leading with friction costs installs. Some fraction of visitors read "API key"
and "unverified" and leave who would otherwise have finished. That is real and
it is the price. Two things make it acceptable: those visitors were mostly going
to fail at setup anyway (so you are losing failed installs, not customers), and
the honest path captures them on the waitlist instead of losing them entirely.
An email address from someone who bounced on friction is worth more than a
half-finished install from the same person.

### How to lead with it without killing the page

Sequencing matters. Leading with friction does not mean opening with it.

- **Hero: outcome only.** No friction in the H1. The hero's job is to earn
  thirty more seconds. Do not put "unverified" next to "finally ignore."
- **One honest block, immediately above the install command,** titled something
  like **"Before you install, three honest things."** Three short lines, each
  with a one-line reason. Reason attached to fact is what makes disclosure read
  as confidence rather than apology.
- **The second CTA lives inside that block:** "Don't want to do any of that?
  The hosted version handles all three. Join the list."
- **FAQ carries the detail,** including the 100-user cap, the CASA decision, and
  the $1,800 number. Naming a real dollar figure is the most credible thing on
  the page.

Tone rule: state, then explain, then move on. "macOS will say zero is from an
unidentified developer. That is because notarizing costs $99/yr for an Apple
account we do not have. The installer clears it for you." No apology, no
hedging, no exclamation marks. Confidence is in the brevity.

---

## 6. Section-by-section rewrite brief for `landing/index.html`

Nobody should edit this file until the code agent is done. This is the brief for
whoever does.

**Global changes first:**
- Both CTAs change everywhere. Primary CTA becomes **"Copy install command"**
  (a one-click copy of the `curl | bash` line) instead of "Download for macOS."
  A DMG download for an un-notarized menu-bar app is a silent-failure machine;
  the installer is the supported path and the page should say so.
  Secondary CTA becomes **"Get the hosted version"** (waitlist anchor), not
  "How it stays safe."
- Every "Claude" reference becomes "your agent CLI (Claude, Codex, opencode)"
  plus "Jev for judgment." The site currently sells Claude as the engine; the
  architecture changed.
- Every cost claim changes from "a few cents a day" to "about a quarter of a
  cent per run."
- Wording follows the §0 license decision. Under AGPL-3.0, "open source" is
  true and should be used everywhere, because it is worth real distribution.
  Under PolyForm-NC, it is "free and source-available" everywhere and "open
  source" nowhere. Do not mix the two.

| # | Section | What it says now | What it should say | Why |
|---|---|---|---|---|
| 1 | `#nav` | Star + **Download** | Star + **Install** (scrolls to install block) + a small text link **"Hosted →"** | Download is the wrong verb for a curl install; the hosted link seeds tier 2 from the first pixel |
| 2 | `#hero` | "An inbox you can finally ignore." / lead about reading every thread / CTA Download + How it stays safe / req pills incl. "Your own Google + Claude", "Free" | Keep the H1. Sub-headline becomes **"Stop checking. Nothing goes missing."** Lead: "zero reads every Gmail account you have, each morning. It leaves the few threads that still need you and sets the rest aside. Nothing is ever deleted." CTAs: **Copy install command** / **Get the hosted version**. Pills: `macOS 26` · `Source-available` · `Runs on your Mac` · `Free` | The H1 is genuinely good. The pills currently leak the friction as a feature list ("your own Google + Claude") without explaining it, which is the worst of both worlds — name it properly further down instead |
| 3 | Hero panel mock | "3 kept / 24 set aside" | Unchanged. It is the best asset on the page | Shows the outcome in under a second |
| 4 | Trust strip | Nothing deleted / your keys / source-available | Keep, but change cell 2 from "Runs on your keys. No server." to **"No server. That's why you bring the key."** | One-line version of the §5 argument, at the top of the page, costing nothing |
| 5 | `#problem` | "You don't have an email problem. You have a 'did I miss something' problem." | Keep the H2. Rewrite the body in first person as the story beat from §4 (four accounts, could not tell, built it, nothing deleted) | The section is currently written *about* the reader. Told as the founder's own story it does the belief-shift work instead of asserting it |
| 6 | `#howitworks` | Three questions + before/after inbox visual | Keep entirely. Add one line under question 3: "When it is not sure, it keeps the thread." | Strongest section on the page. The uncertainty line is a direct answer to the false belief and is now literally true given calibrated thresholds |
| 7 | `#trust` | 5 bento cells: reversible / your keys your machine / ambient / plain language / source-available | Keep 4. Replace "Your keys. Your machine." with **"No account. No server. No upload."** and move the key requirement into the new honest block. Add a 6th cell: **"You can see why"** — the agent's reason for each thread | Splits the benefit (no server) from the cost (you bring a key) and gives each the right place. "You can see why" is a real differentiator against every hosted competitor |
| 8 | **NEW — honest block** | *does not exist* | Directly above the install section. **"Before you install, three honest things."** (1) macOS will warn you — no paid Apple account, installer handles it. (2) Google will say the app isn't verified — verification needs a $1,800/yr audit we didn't buy, click Advanced. (3) You bring an API key and an agent CLI — about a quarter of a cent per run, paid to them, not us. Then: **"Don't want to deal with any of that? The hosted version won't have any of it →"** | **The most important new section on the page.** Full argument in §5. It also carries the waitlist CTA at the exact moment of maximum motivation |
| 9 | **NEW — install** | *does not exist* (the page only links to Releases) | The `curl` one-liner in a copy-block, the three things it does, "re-running is safe," and a link to the manual steps | The README has a good install story the site never tells. A visible command is more credible than a download button for this audience |
| 10 | `#reply` | "Drafts in your voice. On demand. Never on its own." | Keep the copy. Add one line: "Drafting uses your own agent CLI, on your Mac." | The never-sends promise is a genuine differentiator; just make the new architecture honest |
| 11 | `#multiaccount` | "Every account. One calm." | Change H2 to **"Four inboxes. Three things that need you."** (headline option C, reused here) and keep the body | The most specific, most self-selecting line available, placed where specificity helps rather than narrows |
| 12 | `#aiengine` | "Works with your AI engine" — Claude default, Codex, Hermes chips | Retitle **"Two engines, both yours."** Explain the split plainly: a small judgment model decides keep-or-archive for about a quarter of a cent a run; your own agent CLI writes the drafts. Chips: Claude · Codex · opencode | Reflects the actual architecture in `JEV_MIGRATION_PLAN.md`. The two-engine split is also a *reason to believe* the cost claim |
| 13 | **NEW — hosted waitlist** | *does not exist* | Between AI engine and FAQ. Eyebrow "Coming later." H2 **"Or let us run it."** Four bullets (no keys, no CLI, no warnings, every Mac). One line: "Around $12/month. First 100 on the list get $7/month for as long as they stay." Then: "It is not built yet and we are not taking money. Leave an email and one line about what you pay for email tools today." Email field + one text field | The entire second rung. The price question doubles as free pricing research (§3) |
| 14 | `#faq` | 6 questions; the cost and requirements answers are now wrong | Fix "What does it cost" (quarter of a cent per run, your key). Fix "What do I need" (macOS 26, Gmail, an API key, an agent CLI). **Add four:** "Why does macOS warn me?" · "Why does Google say it isn't verified?" (name the $1,800 CASA figure and the 100-user cap) · "What if it archives something I needed?" · "When is the hosted version?" (answer: no date, here's the list) | The FAQ is where honest detail belongs once the top of the page has already been honest. A dollar figure and a real cap are the most trust-building sentences available |
| 15 | `#cta` | "Let your inbox keep itself." Download + GitHub | Keep the H2. CTAs become **Copy install command** / **Get the hosted version**. Req line drops "+ Claude" | Both rungs offered at the end; whichever the reader is, there is a yes available |
| 16 | Footer | Product / Project / Trust columns | Add "Hosted (waitlist)" under Product and "Why unverified" under Trust | Honesty gets permanent navigation, not a one-time mention |

**Where the waitlist goes, summarised:** three places, ranked by expected yield.
(1) Inside the honest block, as the escape hatch from friction — highest intent.
(2) The dedicated section before the FAQ. (3) The final CTA. Nowhere else, and
never as a modal or exit-intent popup; that audience will hold it against you.

**The two CTAs, everywhere on the page:**
- **Primary: "Copy install command."** The free tier, the first yes.
- **Secondary: "Get the hosted version."** The second yes, seeded.

One page, two rungs, no third option. Delete "Download for macOS" entirely.

---

## 7. Launch sequence — 30 days, one person

Assumes one person with a day job's worth of other commitments. Everything here
fits in about two hours a day. The launch event is Day 22, not Day 1, because
launching into a 100-user cap with an out-of-date site is how a good product
gets one shot and wastes it.

### Week 1 (Days 1–7) — fix what would break

| Day | Task |
|---|---|
| 1 | Decide the two §0 questions: the OAuth cap (BYO-client, buy CASA, or a deliberate 100-person cap) and the license (AGPL-3.0, or PolyForm-NC with disciplined "source-available" wording). Nothing else matters until both are decided. A Show HN spike can burn 100 seats in an afternoon, and the license word choice is baked into every asset written in weeks 2–3. |
| 2 | Implement the decision far enough that a stranger can sign in. If it's BYO-client, write that doc. |
| 3 | Test the whole install on a **clean Mac account**, with no Homebrew, no Python, no CLIs. Record the screen. Every place you hesitate is a page-copy fix. |
| 4 | Fix the top three setup failures the recording found. |
| 5 | Rewrite `landing/index.html` sections 1–9 from §6 (nav, hero, trust strip, problem, honest block, install). |
| 6 | Rewrite sections 10–16 (engine, waitlist, FAQ, CTA, footer). Wire the waitlist form to something that actually stores emails. |
| 7 | Update `README.md` and `landing/llms.txt` to match. The llms.txt currently says "Claude by default" and "free, pay for Claude usage" — both now wrong. |

### Week 2 (Days 8–14) — proof and assets

| Day | Task |
|---|---|
| 8 | Record the 45-second demo: menu bar click → 3 kept → hover → set aside → Undo restores it. No talking head, no intro card. This one asset carries every channel. |
| 9 | Get 3–5 real people installed. Friends, but real inboxes. Watch at least one do it live, silently. |
| 10 | Fix what they hit. There will be something. |
| 11 | Write the Show HN post body: why you built it, what it refuses to do, what the friction is and why, what you'd like feedback on. |
| 12 | Write the launch blog post / README top section that the HN post points to. |
| 13 | Build the Dream 100 list properly using the overlap method in §2. Target 60–100 names in a spreadsheet with a contact route for each. |
| 14 | Submit to the quiet directories: alternativeto, MacUpdate, the awesome-* lists, Homebrew cask. These take a day each to appear and compound forever. |

### Week 3 (Days 15–21) — warm the ponds

| Day | Task |
|---|---|
| 15 | Post in r/macapps. Not a launch post — a "here's what I built and here's the part that's ugly" post. Answer every comment. |
| 16 | Post the technical angle somewhere technical: the reversible-archive design, or the two-engine split, or the cost-per-run number. Not a product post. |
| 17 | Reach out to the first 20 Dream 100 names. Two sentences and the video. No ask beyond "thought you might find this interesting." |
| 18 | Fix whatever Reddit surfaced. It will surface something. |
| 19 | Next 20 Dream 100 names. |
| 20 | Freeze the code. Tag a release. Re-test the clean-Mac install one final time. |
| 21 | Rest. Genuinely. Day 22 is a 16-hour day. |

### Week 4 (Days 22–30) — launch and follow through

| Day | Task |
|---|---|
| 22 | **Show HN**, 8–10am ET, Tuesday–Thursday. Title: `Show HN: zero – a macOS menu bar app that keeps only the email that still needs you`. Then sit in the thread all day. Answer the hostile comment first and answer it well. No upvote asks, none. |
| 23 | Post the results and the thread's best criticism publicly. Ship one fix from the thread same-day and say so. |
| 24 | r/selfhosted and r/ClaudeAI, each with a different angle. Never the same post twice. |
| 25 | Product Hunt. Submit the evening before for a **Sunday or Monday** go-live. Self-hunt. First comment within 90 seconds, in the four-part shape: why you built it, what it is, three specifics, one real question. |
| 26 | Remaining Dream 100 outreach, now with the HN thread as proof. The first yes is the hard one; after that use it. |
| 27 | Write "what I learned launching zero" — the friction decision, the numbers, what broke. This ranks and it recruits. |
| 28 | Read every piece of feedback in one sitting. Sort into: breaks trust / breaks setup / feature wish. Only the first two matter. |
| 29 | Ship a fix release. Tell everyone who reported something, by name. |
| 30 | Email the waitlist for the first time. What happened, what you shipped, what's next, no date promised. Then set a monthly reminder to do this forever. |

**What "worked" looks like at Day 30, honestly:** 300–800 GitHub stars, 40–120
completed installs, 150–400 waitlist emails, and 5–15 people still running it
daily in week four. That last number is the only one that matters. If 10 people
are on day 30 and still using it, the product is real and the hosted tier is
worth building. If nobody is, no amount of funnel fixes that, and the honest
next step is to find out why from the people who quit.

---

## Summary of the calls

1. **Fix the 100-user OAuth cap before launching.** A successful launch
   currently breaks the product at user 101.
2. **Relicense to AGPL-3.0** so "open source" is true. It still blocks a
   competitor SaaS clone, still lets you sell the hosted tier, and removes the
   contributor tax PolyForm-NC charges at rung 1. If you keep PolyForm-NC, then
   say "free and source-available" everywhere with zero drift and never write
   "open source."
3. **The avatar is you-five-years-ago:** technical, 3–5 Gmail accounts, already
   runs things locally, believes automation will lose something important.
4. **$4.99 is the wrong price.** List at $12/mo or $99/yr; put the $4.99
   instinct into a founding rate of $7/mo for the first 100 on the list.
   Assume a two-rung ladder and win on retention, not ascension.
5. **Lead with the friction,** one honest block above the install command, with
   the waitlist as its escape hatch. The friction is the proof of the privacy
   claim and the entire sales argument for the paid tier.
6. **Two CTAs, page-wide:** copy the install command, or join the hosted list.
   Delete "Download for macOS."
7. **Launch on Day 22, not Day 1.**
