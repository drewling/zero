# Google OAuth verification — zero

Goal: ship zero with **built-in Google sign-in** (no "bring your own OAuth client"
step) by getting zero's own Google Cloud project verified for the restricted
`gmail.modify` scope.

_Last updated 2026-06-26._

---

## The dedicated project

zero now has its **own** Google Cloud project, separate from the shared
`drewl-366215` (which is used by n8n, Twenty CRM, the Knowledge Base, OpenClaw,
Audit Platform — those were left untouched).

| | |
|---|---|
| **Project** | `zero` — project ID **`zero-500617`** (org drewl.com, billing "Drewl Internal Systems") |
| **OAuth client** | "zero macOS app" — **Desktop** type |
| **Client ID** | `288799635323-2dhpg1v4mhuj1q1dvsldcjbitdeedf9l.apps.googleusercontent.com` |
| **Client secret** | stored at `~/.config/zero-build/client_secret.json` (chmod 600, **not** in the repo) |
| **Consent screen** | External · currently **Testing** |
| **Scopes** | `openid`, `userinfo.email`, `userinfo.profile`, `gmail.modify` — nothing else |
| **Branding** | name "zero" · home `https://zero.headless.com/` · privacy `…/privacy.html` · terms `…/terms.html` · authorized domain `headless.com` |
| **Test users** | tayo@drewl.com, alexander.onabule@gmail.com, lightstormvisuals@gmail.com |

The Gmail API is enabled on the project. `gws` is told to request exactly the four
scopes above via `--scopes` (see `lib/keeper_server.py` `OAUTH_SCOPES`).

## Why a single restricted scope matters

`gmail.modify` is a **restricted** scope (it can read + change mail). An app that
also asks for Drive/Calendar/Docs/Sheets it doesn't use gets auto-rejected — that
(plus the old "Drewl" branding) is why the earlier attempt on the shared project
was turned down. zero now asks for one restricted scope and three non-sensitive
identity scopes, with a written justification already filled in on the Data access
page.

## Decision: skip full verification, run production-unverified (2026-06-26)

Full verification of the restricted `gmail.modify` scope requires a **CASA security
assessment** — an annual, paid, third-party audit. The quote came in at **~$1,800/yr**,
which isn't worth it at zero's current scale. So we are **not** pursuing CASA or the
data-access verification submission.

**The chosen model: production + unverified, under the 100-user cap.** This is the
standard path for small/indie Gmail apps and it's already in effect:

- ✅ Publishing status pushed to **In production** (External). The key win: production
  refresh tokens are **durable** — they no longer expire every ~7 days the way they
  did in Testing. The user's own accounts benefit immediately (once migrated to the
  new client; see below) and so do fresh installs.
- ✅ `headless.com` verified as a Search Console Domain property under tayo@drewl.com.
- **Cost of staying unverified:** each new user sees Google's "**Google hasn't verified
  this app**" screen on first sign-in and must click **Advanced → Go to zero**. The
  onboarding now tells them this is expected and safe. There is also a **100-user
  lifetime cap** on the project — plenty for now.
- **Branding verification** was attempted but Google's automated check flagged the
  homepage (purpose/name match). Not pursued, because branding verification does **not**
  remove the unverified warning while the restricted scope is unverified — it's only a
  prerequisite for the CASA path we're declining. No user-facing benefit, so skipped.

**Revisit CASA only if** zero approaches the 100-user cap or the unverified warning
becomes a real adoption blocker. Until then, this costs $0 and works.

## Demo video / branding fixes — only needed if CASA is ever pursued

Parked, not deleted. If verification is revived later:
- Fix the landing homepage so the automated branding check passes (it wants the app
  name "zero" and a plain-text purpose statement crawlable on `zero.headless.com/`).
- Record a demo video (consent flow + `gmail.modify` usage: read → archive → draft).

## App changes — shipped (v1.6.21)

Done and live (the "no other users but me" + production-unverified model makes this safe):

- **`macapp/build.sh`** — copies `~/.config/zero-build/client_secret.json` into the
  app payload as the default bundled client (gitignored; injected at build time so the
  secret never enters the public repo).
- **Onboarding** — when a bundled client is present it's used as the default and the
  "paste your client JSON" step is skipped, so sign-in is one click. The sign-in step
  now also coaches the user past the "unverified app" warning.

## Local cutover — migrating your own 3 accounts to the new client

The app (v1.6.21+) already bundles the new client, so **fresh installs** get
one-click login. Your existing accounts still run on the old `drewl-366215` client
(durable tokens) — the bundled client only seeds when `~/.config/gws/client_secret.json`
is absent, so it never disturbed them.

To move your own accounts onto the new client, the client files must be swapped and
each account re-authenticated. Re-auth is an **interactive Google sign-in** (you must
click through the consent), so run these yourself — in this chat prefix with `!`, or
in a terminal. The old clients are backed up under `~/.config/zero-build/oldclient-backup-*`.

```bash
NEW=~/.config/zero-build/client_secret.json
SCOPES="openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile,https://www.googleapis.com/auth/gmail.modify"
for d in pending-1782485992 lightstormvisuals alexander; do
  cp "$NEW" ~/.config/gws/accounts/$d/client_secret.json
  GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws/accounts/$d \
  GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file \
    gws auth login --scopes "$SCOPES"   # sign in as the matching account, Advanced → proceed → Allow
done
cp "$NEW" ~/.config/gws/client_secret.json   # default, for future add-account
```

**Cost while unverified:** Google expires testing-mode tokens every ~7 days, so
you'd re-auth weekly until verification is approved. **Recommended: hold this until
verification lands** (the new client becomes durable then) and keep using the current
durable tokens meanwhile. Nothing breaks by waiting — the old client still works.

## Already done

- New project + Desktop client created and fully configured (table above).
- Scopes narrowed in code (`OAUTH_SCOPES`, committed).
- Privacy policy + Terms published at zero.headless.com/privacy.html and /terms.html.
- Shared `drewl-366215` reverted to its original scopes (n8n/Twenty/etc. unaffected).
- `headless.com` verified in Search Console under tayo@drewl.com (Domain property,
  auto-verified via domain provider) — branding-domain requirement satisfied.
