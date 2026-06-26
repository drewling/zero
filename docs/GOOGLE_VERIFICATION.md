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

## What's left to get verified (needs you)

In order:

1. **Verify the domain in Google Search Console.** `headless.com` must be verified
   under tayo@drewl.com (DNS TXT record or HTML file). Until then branding
   verification can't pass. → https://search.google.com/search-console
   _Alternative: if headless.com is awkward to verify, move the landing +
   privacy/terms to a drewl.com URL (already org-verified) and update the three
   branding links + authorized domain to match._
2. **Publish to production + submit for verification** on the Audience page, then
   the Verification centre. (Branding verifies first, then data access.)
3. **CASA security assessment** — required for the restricted `gmail.modify` scope.
   It's an annual, paid, third-party assessment (a Google-authorized lab; ~$500–
   $4,000/yr depending on assessor). This is the long pole — weeks, and it needs
   payment, so only you can start it. Google emails the assessor details after you
   submit.
4. **Demo video** — a short YouTube video showing the consent flow and how
   `gmail.modify` is used (read a thread → archive → draft a reply). Paste the link
   in the "Demo video" field on the Data access page. Script lives in
   `docs/verification-demo-script.md` _(write when recording)_.

## App changes still to make (do NOT release until verified)

Releasing a build that bundles the new (unverified, testing) client would **break
existing users** — their current tokens are on the old client, and they aren't test
users on the new project. So these land in the repo but ship only once verification
is approved:

- **`macapp/build.sh`** — copy `~/.config/zero-build/client_secret.json` into the
  app payload as the default bundled client (keep it gitignored; inject at build
  time so the secret never enters the public repo).
- **Onboarding** — when a bundled client is present, use it as the default and skip
  the "paste your client JSON" step, so sign-in is one click.

## Local cutover (optional, for testing before verification)

To validate the new client end-to-end now, re-auth the three accounts against it
(they're test users, so testing mode works). Cost: Google expires testing-mode
tokens every ~7 days, so you'd re-auth weekly until verification lands. Recommended
to **hold** the cutover until verified, keeping the accounts on their current
durable tokens.

## Already done

- New project + Desktop client created and fully configured (table above).
- Scopes narrowed in code (`OAUTH_SCOPES`, committed).
- Privacy policy + Terms published at zero.headless.com/privacy.html and /terms.html.
- Shared `drewl-366215` reverted to its original scopes (n8n/Twenty/etc. unaffected).
