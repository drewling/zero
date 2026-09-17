# Read me first: making zero easy for other people

Plain-English summary of where distribution stands, what I measured today, and what to
do next. Three other docs go deeper; this one says what to actually do and why.

| Doc | What it covers |
| --- | --- |
| **this file** | The decisions, in plain English, and one new measured fact |
| `docs/DISTRIBUTION_PLAN.md` | Detailed installer spec (written by a parallel session) |
| `docs/FUNNEL_PLAN.md` | Detailed positioning, pricing, landing-page rewrite (same) |
| `docs/JEV_MIGRATION_PLAN.md` | Speed and the Jev engine swap |

Written 2026-09-17.

---

## The one new fact, and it simplifies everything

The whole distribution problem has been "we can't notarize without a $99/yr Apple
account, so how do we get past Gatekeeper?" `DISTRIBUTION_PLAN.md` answers it by making
users **build from source** locally, because a locally-built app never gets quarantined.
That works, but it's heavy: it needs Xcode Command Line Tools, a matching macOS SDK,
minutes of build time, and a separate download just to fetch the OAuth client.

I tested the simpler path on this Mac today (macOS 27.0, build 26A5388g):

```
curl -fsSL -o zero.dmg .../zero.dmg
xattr -l zero.dmg   ->  com.apple.provenance    (no com.apple.quarantine)

# mounted it, copied zero.app out, checked again:
xattr -l zero.app   ->  com.apple.provenance    (no com.apple.quarantine)
# binary runs.
```

**`curl` does not set the quarantine flag. Only browsers do.** Quarantine is applied by
the downloading application, and command-line tools don't apply it.

So a `curl | bash` installer that ships the **prebuilt** app is already quarantine-free.
No source build, no Xcode, no SDK, no wait. `spctl` still says "rejected" because the app
genuinely is unsigned, but that's the assessment tool, not the blocking path. The block
is triggered by the quarantine flag, which never gets set here.

**What this changes:** prebuilt should be the default one-line install, not the
"explicit alternative" that `DISTRIBUTION_PLAN.md` currently makes it. Source build
becomes the fallback for people who want to verify what they're running. That removes
the most complicated part of that plan, including the awkward step of downloading the
DMG only to extract `client_secret.json` from it.

**What stays true from that plan:** everything about failing honestly. Verify a published
checksum. Don't print "ad-hoc signature (expected)" when a signature fails to verify.
Don't remove the app before the new one is staged. Keep the "System Settings → Privacy &
Security → Open Anyway" instructions ready, because Apple can change this behaviour and
a policy change should degrade into an instruction, not a mystery.

I re-ran it a second time checking **every file in the bundle recursively**: 44 files,
all carrying only `com.apple.provenance`, and `grep -c quarantine` returns **0**.

Second thing that check settled: the shipped release **does already contain**
`Contents/Resources/payload/client_secret.json`. So the bundled Google sign-in works out
of the box today, and `DISTRIBUTION_PLAN.md`'s step of downloading the DMG purely to
extract that file is unnecessary when we ship prebuilt. It's only needed on the
source-build path.

> Caveat: measured on one machine, one OS build, today. Re-test before each release.

---

## The four things that actually block a stranger

Full detail with file:line in `docs/scratch/audit-install.md`.

**1. The Google 100-user cap.** zero ships your OAuth client. Google caps unverified apps
at 100 users, lifetime. Lifting it needs a ~$1,800/yr CASA audit you've declined. A good
Show HN could hit 100 sign-ins in an afternoon, so **the best case is currently a failure
mode.** Both other docs flag this too; everyone agrees it's the top issue.

Ship both paths: bundled client stays the default (it's a great first run), and a
"make your own Google client" walkthrough exists as the fallback. Count connected
accounts, and flip the default when it's near 100. For desktop apps Google's own docs
say the client secret isn't really a secret, so the walkthrough can be blunt.

**2. "Open source" isn't currently true.** `LICENSE` is PolyForm Noncommercial, which is
*source-available*. `privacy.html` already says "open source", `index.html` says
"source-available". Those contradict each other; one is wrong today.

`FUNNEL_PLAN.md` recommends AGPL-3.0, which is a good call: it makes "open source" true
while still blocking a competitor from running a closed SaaS clone, and it keeps your
hosted tier perfectly legal. The alternative is keeping PolyForm-NC and saying "free and
source-available" everywhere with zero drift. **Either is fine. Saying both is not.**
This is a ten-minute decision that blocks all the website copy.

**3. The installer can fail and still say "Done."** `macapp/install-zero.sh` runs without
`set -e` and only *warns* when Homebrew, Python, node, `gws` or Claude fail to install
(lines 68-101). It warns but doesn't stop on Intel or macOS < 26 (41-42) even though the
binary is arm64/macOS 26 only. It copies to `/Applications` without sudo (27, 133-135),
which fails for standard users. Piped through `curl | bash` there's no TTY, but the
Homebrew installer wants one.

**4. There's nowhere to enter an API key.** `lib/jev.py` reads the key from a `JEV` env
var or a repo-root `.env`, but `build.sh` deliberately doesn't ship `.env`. So **in the
installed app a Jev key cannot be entered at all.** Separately,
`KeeperModel.swift:66-70` makes Claude a hard requirement, so someone who wants Jev or
Codex still gets nagged to install Claude.

Fix: one "AI engine" onboarding step that detects what's already installed (this audience
usually has `claude` or `codex` already), or takes a pasted Jev key, stored in Application
Support. Don't start the first sweep until a provider actually works.

**Smaller:** `run.sh:35,51` hardcodes `/opt/homebrew/bin/python3` although `config.sh`
already has a portable resolver. `accounts.json.example` has literal `/Users/you/` paths.
`com.drewl.*` identifiers throughout.

---

## What the first run should feel like

```
$ curl -fsSL https://zero.headless.com/install | bash

  Checking your Mac...     macOS 27, Apple Silicon    ok
  Downloading zero...      checksum verified          ok
  Installing...                                       ok

  zero is in your menu bar. Finish setup there.
```

Then three screens:

1. **Connect Gmail.** Warn *before* the redirect that Google will say "hasn't verified
   this app", because it's expected and it looks alarming.
2. **Pick your AI.** Show what's already installed, pre-selected. Or paste a Jev key.
3. **First sweep, then show Undo.**

Screen 3 is the one that earns trust. **Show undo before they need it.** That's what makes
someone comfortable letting this near their email.

---

## The website

Section-by-section audit in `docs/scratch/audit-landing.md`, rewrite brief in
`FUNNEL_PLAN.md` §6. The page is one hand-written 1,342-line HTML file, inline CSS/JS, no
build step, served by an nginx Dockerfile. Easy to edit, with one trap: **claims are
duplicated between the visible HTML and the JSON-LD block at the top**, so every copy
change must be made twice or the page contradicts its own structured data.

Wrong today:

- **"Download for macOS"** (hero L780, final CTA L1103, footer) points at GitHub
  Releases. That's the *browser* download, which is the one path that **does** get
  quarantined. We're actively routing people down the worst route. Highest-value fix on
  the site: replace it with the install one-liner. The `.code-snippet` component at L933
  is already the right shape to reuse.
- **"Your own Google + Claude"** (L790, L1111, plus four spots in the JSON-LD) no longer
  describes the model. Jev isn't mentioned anywhere, including in the `#aiengine`
  section that's otherwise the best-built part of the page.
- **"Source-available" vs "open source"** drift between index.html and privacy.html.

Worth keeping: the hero panel mock, the 27→3 before/after animation (best thing on the
site), the trust bento grid, the provider chips.

Two things to **add** that the page doesn't say:

- **"Not on the App Store, not notarized."** Say it plainly, say why, and link the install
  script so people can read it before piping it into bash. This audience respects the
  honesty and notices the omission.
- **"Your mail text goes to whichever AI you choose."** The page implies everything is
  local. Having a CLI on your Mac doesn't mean the model runs there. This is the claim
  most likely to get taken apart on HN.

### The hero

Current headline "An inbox you can finally ignore" is good and sells the feeling, but
it's slightly wrong as the top promise, because some mail *does* still need you and
that's the entire product. Lead with the promise, keep the old line as a brand line.

> # Your inbox. Only what needs you.
>
> zero reads every Gmail thread each morning, keeps what still needs you, and archives
> the rest. Nothing is deleted. Any run undoes in one click.
>
> `curl -fsSL https://zero.headless.com/install | bash`
> [copy] · [read the install script] · [view source]
>
> macOS 26+ · Apple Silicon · bring a Jev key, or use the Claude/Codex/opencode you
> already have

---

## On the $4.99 price

You said $4.99/mo for the future hosted tier. `FUNNEL_PLAN.md` §3 argues hard against it
and I think it's right:

- Payment processing alone eats ~9% of a $4.99 charge.
- It's a one-way door. Going $4.99 → $12 later means angering early users or running two
  price tiers forever.
- Against Superhuman at $30/mo and SaneBox at ~$7-36/mo, $4.99 for something with full
  mailbox access reads as unserious rather than cheap.

Its suggestion: list at **$12/mo or $99/yr**, and put the $4.99 instinct where it belongs,
as a **founding rate for the first 100 people on the waitlist**. That's honest scarcity
you can actually honour, and it leaves list price intact.

Also worth internalising: **most free users will never pay, and that's fine.** They have
the skills and already have AI access. Don't cripple the free version to push them up;
that poisons the community you need. The paid customer is a different person, the one who
wants this but will never open a terminal. What they buy is "no install, no keys, no
Google Cloud Console." Which means the hosted tier needs the CASA verification and real
infrastructure, so it's genuinely a later project with costs to check first.

Cheap thing to do now: a waitlist link with the price on it. If nobody signs up, you
learned that for free.

---

## Who this is for right now

A terminal install, a possible Google Cloud fallback, an API key and an unsigned app
together select for **technical Mac users**: solo founders, freelance devs, indie hackers
who already have Claude Code installed. Not "every busy professional." That's the right
first audience because they can finish setup and give you real bug reports.

Where they are: Show HN, r/macapps, r/ClaudeAI, Mac Power Users forum, Indie Hackers.
Ranked list and a 30-day sequence in `docs/scratch/funnel.md` and `FUNNEL_PLAN.md` §2.

---

## Order of work

**Before telling anyone:**

1. **Decide the license.** Ten minutes, and all website copy depends on it.
2. **Make prebuilt the default install** and simplify the installer accordingly (the
   measurement above removes the source-build requirement).
3. **Make the installer unable to lie:** hard-fail on unsupported Mac, verify checksum,
   fall back to `~/Applications`, fatal prerequisites.
4. **Add the AI-engine onboarding step** with a Jev key field. Without it, a Jev-only
   user cannot configure the app at all.
5. **Test on a Mac that isn't yours.** A fresh user account is enough. This is the only
   way to find blocker #5, which certainly exists, and which nobody has found because
   every test so far ran on the machine that built it.

**Then the website:**

6. Replace the Download button with the install one-liner (hero, final CTA, footer, and
   the JSON-LD `downloadUrl`).
7. Fix credential copy in all eight places; add Jev to the provider chips.
8. Make license wording identical across index/privacy/terms.
9. Add the "not notarized" and "where your mail goes" notes.

**Then:**

10. Build the BYO Google client walkthrough for user 101.
11. Soft launch to five people you know. Watch them install it.
12. Show HN, only once a stranger has completed setup unaided.
13. Waitlist link with the founding price on it.

---

## How we'll know it worked

- Someone who isn't you, on a Mac that isn't yours, goes from one command to a first
  successful sweep without messaging you for help.
- They find Undo without being told it exists.
- The website says the same thing as the license, on every page.
- The installer fails loudly on an Intel Mac instead of installing something broken.

---

## Background research

- `docs/scratch/audit-install.md` — install/first-run blockers, with file:line
- `docs/scratch/audit-landing.md` — website audit and license analysis
- `docs/scratch/research-distribution.md` — Gatekeeper, OAuth caps, Jev pricing, agent
  CLI invocation, with sources and dates
- `docs/scratch/funnel.md` — avatar, communities, ladder, copy, 30-day launch
