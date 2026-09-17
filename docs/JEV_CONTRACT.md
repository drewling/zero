# Jev integration contract (authoritative)

All workers code against THIS interface. Do not change it without telling the coordinator.

## Module: `lib/jev.py` (built by worker A)

```python
# Raised for non-retryable API problems (401, 422, and exhausted retries).
class JevError(Exception): ...

def available() -> bool:
    """True if a JEV API key is configured (env JEV, or .env at repo root)."""

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
