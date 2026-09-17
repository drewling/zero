# Jev integration contract (authoritative)

All workers code against THIS interface. Do not change it without telling the coordinator.

## Module: `lib/jev.py` (built by worker A)

```python
# Raised for non-retryable API problems (401, 422, and exhausted retries).
class JevError(Exception): ...

def available() -> bool:
    """True if a JEV API key is configured (env JEV, or .env at repo root)."""

def set_key(key: str) -> bool:
    """Persist the API key to app/jev_key (0600); blank removes it. Returns
    whether a key is now configured. Raises on write failure."""

def verify_key(timeout: float = 15.0) -> tuple[bool, str]:
    """Check the stored key against the live service. Returns (ok, detail).
    Never raises and never logs the key."""

def ask(state, questions: dict, timeout: float = 30.0, retries: int = 3) -> dict:
    """One /v1/systemone call. Returns the `answers` map keyed by question id.
    Retries 429/529/5xx with exponential backoff. Raises JevError on failure."""

def ask_many(items: list, max_workers: int = 12, timeout: float = 30.0) -> list:
    """items: list of (state, questions). Returns answers list in the SAME order.
    Failed items yield None rather than raising, so one bad thread never kills a run."""
```

Answer shapes returned by the API (per docs.typesafe.ai/api):
- noul   -> `{"type":"noul","noul":0.92}`
- choice -> `{"type":"choice","choice":"x","probabilities":{...},"confidence":0.82}`
- score  -> `{"type":"score","score":1.6,"legend":{...},"probabilities":{...},"confidence":0.78}`

Endpoint: `POST https://api.typesafe.ai/v1/systemone`, `Authorization: Bearer <key>`,
body `{"state":..., "model":"jev-latest", "questions":{...}}`.

## Settings flag

`app/settings.json` key `"provider"` already exists (default `"claude"`).
Jev classification is ON when `provider == "jev"`. Anything else keeps today's behavior
byte-for-byte. Default MUST remain `claude` until the agreement check passes.

## Key storage (added 2026-09-17)

Key lookup order is **env `JEV` → `app/jev_key` → `.env` at the repo root**.

`app/jev_key` exists because the packaged app ships no `.env` (`macapp/build.sh`
deliberately excludes it), so without it Jev could not be configured at all outside a
source checkout. `ROOT` is the repo in a checkout and
`~/Library/Application Support/zero` in the installed app, so the one path serves both.
`app/` is never in `seedFromBundle`'s overwrite list, so a saved key survives updates,
exactly like `settings.json`.

The key is gitignored and included in `macapp/build.sh`'s payload leak guard.

HTTP surface on the local server:
- `GET  /api/jev-key-status` → `{"configured": bool}` — never returns the key.
- `POST /api/set-jev-key` `{"key": "..."}` → saves, then verifies against the live
  service and reports `verified` plus a human-readable `message`. An empty key removes it.

## Hard rules for every worker

1. **Do not touch `macapp/Sources/**`.** The UI stays intact. (Worker C changes only the
   Python server side of dismiss/archive.)
2. **Drafting stays on Claude.** Never route `gen_drafts.py` or the reply-generation path
   at `keeper_server.py:1118` to Jev. Jev cannot generate prose.
3. **Reversibility is the product.** When a judgment is missing, failed, or uncertain,
   the outcome MUST be "keep". Never archive on an error path.
4. **No secrets in code or commits.** Read the key from env/.env only. `.env` is gitignored.
5. Preserve existing behavior when `provider != "jev"`. This is a strictly additive change.
6. Write a runnable test under `lib/tests/` in the existing style (plain asserts, prints
   `<name> OK`, runnable via `python3 lib/tests/<file>.py`). No network in tests: stub it.
