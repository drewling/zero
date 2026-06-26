<div align="center">

# zero

**Keep your inbox at "only what still needs you," across every account, and never lose anything.**

A quiet macOS menu-bar app that reads each Gmail thread, sets aside everything that
isn't waiting on you, and keeps the rest one tap away. Nothing is ever deleted.

<img src="design/screenshots/panel-loops.png" width="320" alt="zero open loops panel">

[![Website](https://img.shields.io/badge/website-zero.headless.com-1A73E8)](https://zero.headless.com)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS%2026%2B-black?logo=apple)](https://github.com/drewling/zero/releases)
[![License: PolyForm-NC](https://img.shields.io/badge/license-PolyForm--NC-blue)](LICENSE)

</div>

---

## What it is

Most "inbox zero" tools make you do the sorting. zero does the one part
you'd never finish by hand: continuously deciding what in your inbox is still an
**open loop** (something genuinely awaiting your action) and quietly setting
everything else aside.

It lives in the menu bar. You glance at it between meetings and see, across all
your accounts, the few things that actually need you. Everything else is archived
reversibly, so the inbox stops being a swamp without anything going missing.

**What it refuses to be:**

- An auto-replier. Replies are drafted in your voice on demand; you review, edit,
  and decide when (or whether) to send. It never sends on your behalf.
- A unified mail client. Your Gmail stays exactly as it is.
- A rule engine. There is no DSL, no regex, no filter list to maintain.
- A real-time tool. It runs once a morning.

## The panel

Four views, one icon in the menu bar:

| Open loops | Accounts | Undo | Settings |
|:---:|:---:|:---:|:---:|
| ![Open loops](design/screenshots/panel-loops.png) | ![Accounts](design/screenshots/panel-accounts.png) | ![Undo](design/screenshots/panel-undo.png) | ![Settings](design/screenshots/panel-policy.png) |
| What still needs you, across all accounts | Per-account inbox and archive counts | Restore any day's archived mail in one tap | Your **Rules** (plain English), categories, daily schedule, and AI engine |

The panel is a dark "Raycast"-style liquid-glass overlay. Tap any thread to open
it in Gmail, hover it to **Reply** (drafts in your voice, stays local until you
tap Send) or **Set aside** (archived reversibly, immediately restorable).

## How it works

```
menu-bar app (SwiftUI)  -->  local server (keeper_server.py, 127.0.0.1)
                                 |  reads
                             app/state.json  <--  dashboard_state.py
                                 ^                (per-account status, open loops, undo points)
                                 |  Run / Undo
                             review_open_loops.py  (Claude Haiku + keep-policy.md)
                                 |
                             gws CLI  -->  Gmail (reversible label swaps only)
```

The Swift shell is deliberately thin: it starts the local Python server and
renders a native SwiftUI panel against its JSON API. All judgment runs in Python
with Gmail reached via the `gws` CLI. The panel reads a cached state file so it
opens instantly; it never talks to Gmail directly.

## Why you can trust it

Three properties, in priority order:

1. **Reversible by construction.** "Archive" means remove the INBOX label and add
   a dated recovery label (e.g. `zero/undo/2026-06-24`). Mail stays in All Mail,
   fully searchable. Any day's sweep restores in one tap from the **Undo** view.
   Nothing is ever deleted.
2. **Ambient.** No new app to live in. Your Gmail and Apple Mail stay exactly as
   they are. zero works quietly behind them, once a morning.
3. **The judgment is an agent, not a rule list.** What counts as "needs you" is
   written in plain English (see [keep-policy.md](keep-policy.md)) and enforced by
   Claude Haiku reading each thread in full. Cold outreach with a real person's
   name gets archived; a real person actually awaiting your reply is kept. A filter
   rule cannot tell those two apart.

## How "needs you" is decided

You edit one plain-language file, [keep-policy.md](keep-policy.md), or the
**Rules** section under the **Settings** tab in the panel. No regex, no DSL. The default:

> Keep a thread only if a real person is awaiting your reply or decision, there is
> an unanswered direct question or request addressed to you, a payment has actually
> failed, it is a legal or contractual matter, or there is an explicit deadline with
> a real consequence. Archive everything else reversibly.

Two signals settle most cases automatically:

- **Last message from you:** you already responded, the ball is in their court.
  Archive it.
- **Never replied to this sender, plus cold/sales content:** not a real loop, even
  with a person's name on it. Archive it.

When unsure, the policy keeps the thread. Everything archived is one tap away.

---

## Install

> **Requirements:** macOS 26 (Tahoe) on Apple Silicon. Everything else — Python, Node,
> the `gws` and `claude` CLIs — the installer sets up for you.

### One command

```bash
curl -fsSL https://raw.githubusercontent.com/drewling/zero/master/macapp/install-zero.sh | bash
```

This installs any missing prerequisites (Homebrew → Python 3 / Node → the `gws` and
`claude` CLIs), copies `zero.app` to `/Applications`, clears the macOS quarantine flag,
and launches it. Re-running is safe. When it opens, skip to **[First run](#first-run)**.

<details>
<summary><b>Why the quarantine step?</b></summary>

zero is signed ad-hoc, not notarized (there's no paid Apple Developer account behind a
free app). macOS quarantines *downloaded* un-notarized apps, and Gatekeeper then refuses
to launch them — so a hand-dragged DMG silently does nothing, and because zero is a
menu-bar app with no window, the block is invisible. Clearing the flag is the standard
install path for un-notarized open-source Mac apps; the script does it for you.
</details>

<details>
<summary><b>Manual install</b> — prefer to do each step yourself</summary>

```bash
# 1. Prerequisites
brew install node python3
npm install -g @googleworkspace/cli @anthropic-ai/claude-code
claude            # finish Claude login on first run

# 2. Download zero from the Releases page, then clear the quarantine flag.
#    Use the FULL path — a Homebrew/Python `xattr` earlier in PATH may silently no-op.
/usr/bin/xattr -cr /Applications/zero.app
```

Grab the app from the [Releases page](https://github.com/drewling/zero/releases) and drag
it to `/Applications` before running the `xattr` line. Then open it and follow
**[First run](#first-run)** below.
</details>

### First run

Open zero — it lives in the menu bar (no Dock icon, no window). The onboarding walks you
through connecting Google and your AI, both in your browser, and **nothing leaves your Mac**:

1. **Connect Google.** Sign in to each Gmail account you want zero to watch. zero asks for
   one Gmail permission and your basic identity — [nothing else](#privacy-and-trust). For
   now this uses *your own* Google OAuth client (a one-time setup — see **Bring your own
   Google Cloud project** below); built-in one-click sign-in is in Google verification.
2. **Connect your AI.** zero uses the `claude` CLI you logged into above to read and judge
   threads. Prefer a different engine? Pick Codex, a local model, or another agent CLI
   under **Settings → AI engine**.
3. **Run it.** Hit **Run zero now** for the first sweep. To run it automatically each
   morning, set a time under **Settings → Daily schedule** (or `./bin/zero schedule`).

<details>
<summary><b>Bringing your own Google Cloud project</b> — advanced</summary>

Until zero's own Google client clears verification, sign-in uses a Cloud project you
create. It's a one-time setup: make a **Desktop app** OAuth client at
[console.cloud.google.com](https://console.cloud.google.com/) (APIs & Services →
Credentials), enable the **Gmail API**, and paste the downloaded JSON into zero's
onboarding screen.

One catch worth knowing: Gmail's `gmail.modify` is a *restricted* scope, so an
**unverified** personal client can only grant it while the consent screen is in
**Testing** with your address added as a **test user** — and Google then expires that
grant after **7 days**, so you'll re-authorize weekly. (A client in "production" but
unverified can't grant restricted scopes at all.) Verifying your own client removes the
weekly re-auth. See [docs/SETUP.md](docs/SETUP.md) for the full click-path.
</details>

### Build from source

Requires Xcode command-line tools (`xcode-select --install`) on macOS 26 (Apple Silicon).

```bash
git clone https://github.com/drewling/zero.git
cd zero/macapp
./build.sh           # produces zero.app in macapp/build/
./make-dmg.sh        # optional: packages it as a .dmg
```

> **Contributor resources:** [Architecture](docs/ARCHITECTURE.md) · [API reference](docs/api/) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

---

## Configuration

**One file.** Edit [keep-policy.md](keep-policy.md) directly or via the **Rules**
section under the **Settings** tab in the panel. Write it in plain English. No syntax to learn.

Everything else is optional and lives under **Settings**: your **categories**, the
**daily schedule** (what time, which days, whether macOS notifies you), how far back
to label archived mail, and which **AI engine** to use (Claude by default; Codex,
Hermes, or another agent CLI if you have one installed).

**Optional voice grounding.** Copy `knowledge/profile.example.md` to
`knowledge/profile.md` and fill it in. The drafter uses it as background when
composing replies in your voice. You can also create per-account files at
`knowledge/<account-slug>.md`. These files are gitignored and stay on your machine.

There is nothing else to configure.

---

## Privacy and trust

- **No project-operated backend.** Everything runs on your Mac. The only data that
  leaves your machine is per-thread text sent to the Claude API through your own
  `claude` CLI (for the keep/archive judgment and draft generation). See
  [SECURITY.md](SECURITY.md).
- **The local server binds to `127.0.0.1` only.** Nothing is reachable from the
  network.
- **Nothing is ever deleted.** Archiving is a reversible label change. Mail stays
  in All Mail, fully searchable in Gmail.
- **Your data stays on your machine.** `accounts.json` and `knowledge/*.md` are
  gitignored and never committed.
- **Gmail access uses your own credentials.** The `gws` CLI authenticates with
  your Google account via OAuth; zero never handles your password or OAuth
  tokens directly.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[PolyForm Noncommercial 1.0.0](LICENSE). Free to use, fork, modify, and share for
noncommercial purposes. Commercial use and reselling are not permitted.
