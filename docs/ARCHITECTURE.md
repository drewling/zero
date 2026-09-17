# Architecture

> See also: [API reference](api/) · [Setup](SETUP.md) · [Maintenance](MAINTENANCE.md)

How zero is put together: a native macOS menu-bar app over a small local HTTP
service that drives Gmail through your own credentials. Everything runs on your
Mac. Nothing is deleted, and no mail is sent without you.

## The three pieces

1. **The app** (`macapp/`) — a SwiftUI menu-bar app (`LSUIElement`) hosted in a
   custom `NSPanel` with the macOS 26 Liquid Glass surface. It is the only
   front end. It owns no mail logic; it talks to the local service over HTTP.
2. **The service** (`lib/keeper_server.py`) — a stdlib-only JSON API bound to
   `127.0.0.1:8765`. The app spawns it (detached, so it survives panel
   open/close) and re-attaches on next launch. It reads cached state, runs the
   keeper, generates drafts, and reads/writes settings.
3. **The tools** — `gws` (the Google Workspace CLI) for all Gmail access, one
   OAuth config dir per account; TypeSafe's Jev model for thread classification;
   and a text LLM (Claude by default) for reply drafts.

```
┌──────────────────────────────┐     HTTP 127.0.0.1:8765
│  zero.app (Swift / SwiftUI)  │ ───────────────┐
│  menu-bar panel, Liquid Glass│                │
└──────────────────────────────┘                ▼
                                   ┌──────────────────────────────┐
                                   │   lib/keeper_server.py        │
                                   │   local JSON API (detached)   │
                                   │   /api/state /run /draft …    │
                                   └───────┬───────────────┬───────┘
                                           │               │
                                  Jev + lib/llm.py    gws (per account)
                                  classify + draft    Gmail API, keyring
                                           │               │
                                           ▼               ▼
                                    typed decision    list · modify ·
                                    + probability     create draft · send
```

## Request flow

- **State** — `GET /api/state` returns the cached `app/state.json` (open loops
  per account, counts, last run). On boot the service rebuilds state if the
  cache is missing or stale (any account failed), so a transient error never
  sticks. `lib/dashboard_state.py` writes the cache.
- **A run** — `POST /api/run` kicks a background job. For each enabled account
  it calls `lib/review_open_loops.py`, which reads each inbox thread and asks
  TypeSafe's Jev model for a typed keep-or-archive decision and its probability.
  It archives only the threads that do not need you, reversibly. `lib/learn.py`
  rolls your edits into a voice profile. Progress is polled via `GET /api/job`.
- **A reply** — `POST /api/draft` builds a draft in your voice. `lib/context.py`
  gathers the thread and sender history; a text LLM writes the reply (Claude by
  default), because Jev returns decisions rather than prose;
  `lib/draftutil.py` builds the MIME message, appends your Gmail signature
  (`sendAs`), and creates the Gmail draft. `POST /api/draft/send` sends it.
  Nothing sends without you pressing send.
- **Configuration** — `GET/PUT /api/policy` (your Rules), `/api/categories`
  (labels), `/api/settings` (grace window, schedule, provider, notifications),
  `/api/provider-status` (which agent SDK is connected), and
  `/api/credentials-status` + `/api/set-credentials` (in-app Google OAuth setup).

## The optional daily routine

`run.sh` is a launchd job you opt into from Settings (or `bin/zero schedule`).
It runs the same keeper across accounts on your schedule (hour, minutes, and
weekdays are configurable; the plist is regenerated when you change them), then
refreshes state and, if enabled, posts a macOS notification with the result.

## Reversibility and privacy

- **Nothing is ever deleted.** Archiving removes the `INBOX` label and adds a
  dated `zero/undo` recovery label. Mail stays in All Mail; the Undo view
  restores it with one search. There is no delete path in the code.
- **Your keys, your machine.** zero signs in with your own Google OAuth client
  and your own Claude credentials. There is no server in the middle and no
  account to create. gws tokens live in the system keyring (file backend) under
  `~/.config/gws/`, never in this repo.

## Key files

| File | Purpose |
|------|---------|
| `macapp/Sources/` | The SwiftUI app (panel, model, API client, styles, onboarding) |
| `lib/keeper_server.py` | Local JSON API the app talks to |
| `lib/llm.py` | Text-model provider abstraction for reply drafting |
| `lib/review_open_loops.py` | Core keep/archive classifier using Jev's typed decisions |
| `lib/dashboard_state.py` | Builds `app/state.json` (the cached inbox view) |
| `lib/draftutil.py` | MIME build, Gmail signature, draft create/send |
| `lib/context.py` | Thread + sender history for drafting |
| `lib/learn.py` | Voice learning from your edits |
| `run.sh` | Optional daily launchd pipeline |
| `bin/zero` | CLI: run, state, schedule, stop |
| `app/state.json` · `app/settings.json` | Runtime cache and settings (gitignored) |
| `accounts.json` | Per-account registry: slug, email, gws config_dir (gitignored) |
| `keep-policy.md` | The default Rules shown on first run |

## Config contract

| Env var | Default | Purpose |
|---------|---------|---------|
| `MAIL_TRIAGE_DIR` | directory of `config.sh` / `config.py` | Override the app root |
| `MAIL_TRIAGE_PYTHON` | `python3` (shell) / `sys.executable` (Python) | Override the Python binary |
| `CLAUDE_BIN` | `claude` | Override the Claude CLI binary |
| `GWS_BIN` | `gws` | Override the gws binary |
| `KEEPER_HOST` | `127.0.0.1` | Bind address for the local engine (never change in production) |
| `KEEPER_PORT` | `8765` | Port for the local engine |
| `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND` | `file` | gws keyring backend (set by the app) |
