# Setup Guide

Step-by-step first-time setup on a fresh Mac.

> **Just want to use the app?** Download it from the [Releases page](https://github.com/drewling/zero/releases),
> drag to Applications, and follow the in-app onboarding. The steps below are for contributors
> who want to build from source or run the Python engine directly.
>
> See also: [Architecture](ARCHITECTURE.md) · [API reference](api/) · [Maintenance](MAINTENANCE.md)

---

## 1. Install dependencies

```bash
# Node.js (needed for gws and claude CLI)
brew install node

# Google Workspace CLI (gws) — the official Google CLI
npm install -g @googleworkspace/cli
gws --version

# Claude Code CLI
npm install -g @anthropic-ai/claude-code
claude    # completes login on first run

# Python 3
brew install python3

# Optional: useful for debugging log JSON
brew install jq
```

---

## 2. Clone and run setup

```bash
git clone https://github.com/drewling/zero.git ~/zero
cd ~/zero
bash setup.sh
```

`setup.sh` checks that all dependencies are present and creates `logs/` and `drafts/`.

> **Note:** The distributed `zero.app` runs from `~/Library/Application Support/zero`
> (it copies itself there on first launch). The source checkout is only needed to build
> from source or to run the Python engine directly during development.

---

## 3. Create a Google Cloud OAuth client

zero uses your own OAuth credentials — no shared app, no third-party access. The
client is free. This takes about five minutes, and the console UI is exact below
(verified June 2026 — Google moved OAuth config to the new **Google Auth Platform**).

**3a. Create or select a project.**
Go to [console.cloud.google.com](https://console.cloud.google.com/), open the
project picker in the top bar, and create a project (any name) or pick one.

**3b. Enable the Gmail API.**
Menu (☰) → **APIs & Services → Library** → search **Gmail API** → click it →
**Enable**. (Direct: [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library))

**3c. Configure the consent screen — required before you can create a client.**
Menu → **Google Auth Platform** ([console.cloud.google.com/auth](https://console.cloud.google.com/auth)).
A fresh project shows "Google Auth Platform not configured yet" → **Get started**:

- **App Information** — app name (e.g. "zero") + your email → Next
- **Audience** — choose **External** (a personal `@gmail.com` has no Workspace org, so Internal isn't available) → Next
- **Contact Information** — your email → Next
- **Finish** — agree to the policy → **Create**

**3d. Publish to production — this is the step everyone misses.**
On the **Audience** tab, under **Publishing status**, click **Publish app** so the
status reads **In production**.

> **Why this matters (critical):** While the app is in **Testing**, Google expires
> your refresh token after **7 days** for any Gmail scope — so zero would silently
> stop syncing about a week after you set it up. Publishing to **In production**
> removes that expiry. You do **not** need to complete Google's verification
> (the "requires verification" banner is fine to ignore) — verification is a
> separate, optional process. Unverified + production works indefinitely for your
> own account; there's only a one-time browser warning (see 3g) and a lifetime cap
> of 100 users, which is irrelevant for personal use.

**3e. Create the Desktop client.**
**Google Auth Platform → Clients** ([console.cloud.google.com/auth/clients](https://console.cloud.google.com/auth/clients))
→ **Create client** → Application type: **Desktop app** → Name it (e.g. "zero") →
**Create**. (No redirect URIs needed for Desktop.)

**3f. Download `client_secret.json`.**
The dialog shows the Client ID and secret — click the **download (⬇ JSON)** icon.
It saves as `client_secret_<id>.json`; rename it to `client_secret.json`.

> The full secret is shown only at creation. If you lose it, open the client and
> add a new secret (or recreate the client).

**3g. First sign-in shows an "unverified app" warning — this is expected.**
Because the app is unverified, the first browser sign-in (step 5 / in-app) shows
**"Google hasn't verified this app."** Click **Advanced** → **Go to zero (unsafe)**
→ grant access. ("unsafe" is just Google's label for any unverified app; you wrote
this one, and access stays entirely on your Mac.)

When you launch zero for the first time, the onboarding screen prompts you to paste
`client_secret.json`. It stays on your Mac; it is never transmitted anywhere.

---

## 4. Configure accounts.json

```bash
cp accounts.json.example accounts.json
```

Edit `accounts.json`:

```json
[
  {
    "slug":       "work",
    "email":      "me@company.com",
    "config_dir": "~/.config/gws"
  },
  {
    "slug":       "personal",
    "email":      "me@gmail.com",
    "config_dir": "~/.config/gws/accounts/personal"
  }
]
```

- `slug` — short identifier (used in logs; no spaces)
- `email` — the Gmail address for this account
- `config_dir` — where `gws` stores OAuth tokens for this account

The **first entry is the primary account**.

---

## 5. Authenticate each account with gws

The `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file` env var is required — without it gws
tries to use the system keychain and may fail in headless or launchd contexts.

For the primary account:
```bash
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws \
  GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file \
  gws auth login --scope gmail
```

For additional accounts, point to their config dirs:
```bash
mkdir -p ~/.config/gws/accounts/personal
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws/accounts/personal \
  GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file \
  gws auth login --scope gmail
```

At the browser warning, click **Advanced → Go to zero (unsafe) → grant** (see 3g).

Verify each account:
```bash
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws \
  GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file \
  gws gmail users getProfile --params '{"userId":"me"}' 2>/dev/null | grep emailAddress
```

> **If you authorized while the app was still in Testing:** that token keeps its
> 7-day expiry permanently, even after you publish to production. After switching to
> **In production** (3d), delete the token and re-run `gws auth login` for each
> account, or it'll look like publishing didn't fix it. This is the #1 "auth dies
> after a week" cause.

---

## 6. Launch the app

```bash
./bin/zero app
```

On first launch, zero's onboarding walks you through pasting your OAuth client JSON
and connecting each Gmail account.

---

## 7. Optional: tune the knowledge file

`knowledge/profile.example.md` is the AI's context for drafting replies in your
voice. Copy and edit it:

```bash
cp knowledge/profile.example.md knowledge/profile.md
# edit knowledge/profile.md with your name, role, and tone
```

Per-account files at `knowledge/<slug>.md` are also supported. These files are
gitignored and stay on your machine.

---

## 8. Schedule daily triage

```bash
./bin/zero schedule
```

This registers a launchd agent that runs the keeper at 07:00 every morning.

---

## Troubleshooting

### gws returns empty or auth errors

- Make sure `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file` is set — this is the most
  common cause of silent auth failures.
- Re-run `gws auth login` for the affected account.
- Check the `config_dir` path in `accounts.json` is correct.

### launchd job not running

```bash
launchctl list | grep drewl
cat logs/latest.log
```

Verify `run.sh` is executable: `chmod +x run.sh`

### PATH issues in launchd

`config.sh` prepends common Homebrew, nvm, and `~/.local/bin` paths. If your tools
live elsewhere, add them to the `_mt_prepend` block in `config.sh`.
