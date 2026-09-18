#!/usr/bin/env python3
"""HTTP client for TypeSafe AI's Jev "System One" endpoint.

Jev answers typed questions (noul / choice / score) against a state, with
calibrated probabilities. It does not generate prose — drafting stays on an
LLM provider (see lib/llm.py).

Endpoint: POST https://api.typesafe.ai/v1/systemone
Auth, in order: env JEV, then app/jev_key (written by onboarding/Settings),
then a .env at the repo root (source checkouts only).
Never logs or prints the key.
"""
import json
import http.client
import queue
import threading
from urllib.parse import urlsplit
import run_metrics as metrics
import os
import random
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENV_PATH = os.path.join(ROOT, ".env")
# Where the app stores a pasted key. ROOT is the repo in a source checkout and
# ~/Library/Application Support/zero in the installed app (main.swift copies the
# payload there and runs from it), so this one path serves both. The packaged app
# never ships .env, so without this there is no way to configure Jev at all.
KEY_PATH = os.path.join(ROOT, "app", "jev_key")
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

_key_cache = {"loaded": False, "value": None}


class JevError(Exception):
    """Raised for non-retryable API problems (401, 422, and exhausted retries)."""


def _parse_env_file(path):
    """Minimal KEY=VALUE parser for a .env file. No new dependency.

    Ignores blank lines and lines starting with '#'. Strips surrounding
    single/double quotes from values. Never raises for a malformed line."""
    out = {}
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip()
                if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
                    v = v[1:-1]
                if k:
                    out[k] = v
    except Exception:
        pass
    return out


def _get_key():
    """Resolve the JEV API key. Cached.

    Order: env JEV (lets a one-off run override), then app/jev_key (what the UI
    writes, and the only route that works in the installed app), then .env at the
    repo root (developer convenience in a source checkout)."""
    if _key_cache["loaded"]:
        return _key_cache["value"]
    key = os.environ.get("JEV")
    if not key:
        try:
            with open(KEY_PATH) as f:
                key = f.read().strip()
        except Exception:
            key = None
    if not key:
        key = _parse_env_file(ENV_PATH).get("JEV")
    _key_cache["loaded"] = True
    _key_cache["value"] = key or None
    return _key_cache["value"]


def set_key(key):
    """Persist the API key to app/jev_key (0600) and refresh the cache.

    Passing a blank key removes the stored key. Returns True if a key is now
    configured. Raises on write failure so the caller can report it rather than
    silently appearing to save."""
    key = (key or "").strip()
    os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
    if not key:
        try:
            os.remove(KEY_PATH)
        except FileNotFoundError:
            pass
    else:
        # Write via a temp file in the same dir, then replace, so an interrupted
        # write can't leave a truncated key behind.
        tmp = KEY_PATH + ".tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(key)
            os.replace(tmp, KEY_PATH)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    _key_cache["loaded"] = False
    _key_cache["value"] = None
    return _get_key() is not None


def available():
    """True if a JEV API key is configured (env JEV, app/jev_key, or .env)."""
    return _get_key() is not None


def verify_key(timeout=15.0):
    """Check the stored key against the real service. Returns (ok, detail).

    Sends the smallest possible real question rather than trusting the key's
    shape, so a typo or an unentitled key is caught while the user is still on
    the setup screen instead of at 7am tomorrow. Never raises and never logs the
    key: transport problems come back as ok=False with a reason, so the caller
    can tell "wrong key" apart from "no internet"."""
    key = _get_key()
    if not key:
        return False, "No API key configured"
    body = {
        "state": {"probe": "connectivity check"},
        "model": MODEL,
        "questions": {"ok": {"type": "noul", "instructions": "Answer yes."}},
    }
    try:
        status, parsed, raw = _post(body, key, timeout)
    except Exception as exc:
        return False, f"couldn't reach Jev ({exc.__class__.__name__})"
    if status == 200:
        return True, "ok"
    if status in (401, 403):
        return False, "the key was rejected — check you copied it correctly"
    if status == 429:
        # Valid key, just rate limited at this moment.
        return True, "ok (rate limited during the check, but the key is valid)"
    return False, str(_detail(parsed, raw) or f"HTTP {status}")


def _post_unpooled(body, key, timeout):
    """Perform the raw HTTP POST. Returns (status_code, parsed_json_or_None, raw_text).

    Never raises for HTTP error status codes — those are surfaced via status_code
    so the caller can decide whether to retry. Only transport-level failures
    (connection errors etc.) propagate as urllib exceptions to the caller."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    parsed = None
    try:
        parsed = json.loads(raw) if raw else None
    except Exception:
        parsed = None
    return status, parsed, raw


# A bounded pool, not one connection for every caller thread. Connections are
# leased exclusively until the full response is consumed. Failed sockets never
# return to the pool, and the existing ask() retry policy owns all retries.
_POOL_SIZE = 12
_pool = queue.LifoQueue(maxsize=_POOL_SIZE)
_slots = threading.BoundedSemaphore(_POOL_SIZE)


def _post(body, key, timeout):
    account = os.environ.get("ZERO_ACCOUNT", "")
    with metrics.measured("jev.systemone", account):
        if not _slots.acquire(timeout=timeout):
            raise TimeoutError("Jev connection pool busy")
        try:
            return _post_transport(body, key, timeout, account)
        finally:
            _slots.release()


def _post_transport(body, key, timeout, account):
    # urllib owns proxy negotiation; do not silently bypass enterprise proxies.
    if urllib.request.getproxies().get("https") or os.environ.get("ZERO_JEV_POOL") == "0":
        return _post_unpooled(body, key, timeout)
    target = urlsplit(ENDPOINT)
    if target.scheme != "https" or target.username or target.password:
        raise JevError("Jev endpoint must be HTTPS without URL credentials")
    origin = (target.hostname, target.port or 443)
    path = target.path or "/"
    if target.query:
        path += "?" + target.query
    conn = None
    reusable = False
    try:
        try:
            old_origin, conn = _pool.get_nowait()
            if old_origin != origin:
                conn.close()
                conn = None
        except queue.Empty:
            pass
        if conn is None:
            conn = http.client.HTTPSConnection(*origin, timeout=timeout)
            metrics.record("jev.transport", account, connections_created=1)
        else:
            conn.timeout = timeout
            if conn.sock is not None:
                conn.sock.settimeout(timeout)
            metrics.record("jev.transport", account, connections_reused=1)
        conn.request("POST", path, body=json.dumps(body).encode("utf-8"), headers={
            "Authorization": "Bearer " + key, "Content-Type": "application/json"})
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8", errors="replace")
        status = resp.status
        reusable = not resp.will_close
        resp.close()
        metrics.record("jev.transport", account, http_failures=int(status >= 400))
        try:
            parsed = json.loads(raw) if raw else None
        except ValueError:
            parsed = None
        return status, parsed, raw
    finally:
        if conn is not None:
            if reusable:
                _pool.put_nowait((origin, conn))
            else:
                conn.close()


def _detail(parsed, raw):
    """Best-effort extraction of an error detail message from a response body."""
    if isinstance(parsed, dict):
        for k in ("detail", "error", "message"):
            if k in parsed:
                return parsed[k]
        return parsed
    return raw


def ask(state, questions, timeout=30.0, retries=3):
    """One /v1/systemone call. Returns the `answers` map keyed by question id.

    Retries 429/529/5xx with exponential backoff + jitter. Raises JevError on
    failure (401/422 raise immediately without retrying)."""
    key = _get_key()
    if not key:
        raise JevError("no JEV API key configured (set env JEV or .env)")

    body = {"state": state, "model": MODEL, "questions": questions}
    retries = max(0, min(int(retries), 6))
    attempt = 0
    last_err = None
    while attempt <= retries:
        try:
            status, parsed, raw = _post(body, key, timeout)
        except Exception as e:
            # Transport-level failure (DNS, connection refused, timeout, etc.)
            last_err = str(e)
            if attempt >= retries:
                raise JevError(f"transport error after {attempt + 1} attempt(s): {last_err}")
            _sleep_backoff(attempt)
            attempt += 1
            continue

        if status == 200:
            if not isinstance(parsed, dict) or "answers" not in parsed:
                raise JevError(f"malformed 200 response body: {raw[:500]}")
            return parsed["answers"]

        if status in (401, 422):
            raise JevError(f"HTTP {status}: {_detail(parsed, raw)}")

        if status == 429 or status == 529 or 500 <= status < 600:
            last_err = f"HTTP {status}: {_detail(parsed, raw)}"
            if attempt >= retries:
                raise JevError(f"exhausted retries ({attempt + 1} attempts): {last_err}")
            _sleep_backoff(attempt)
            attempt += 1
            continue

        # Any other status: not documented as retryable, don't retry.
        raise JevError(f"HTTP {status}: {_detail(parsed, raw)}")

    raise JevError(f"exhausted retries: {last_err}")


def _sleep_backoff(attempt):
    """Exponential backoff with jitter: base 0.5s, doubling, plus up to 0.25s jitter."""
    delay = (0.5 * (2 ** attempt)) + random.uniform(0, 0.25)
    metrics.record("jev.retry", os.environ.get("ZERO_ACCOUNT", ""), retries=1, backoff_seconds=delay)
    time.sleep(delay)


def ask_many(items, max_workers=12, timeout=30.0):
    """items: list of (state, questions). Returns answers list in the SAME order.

    Failed items yield None rather than raising, so one bad thread never kills
    a run."""
    from concurrent.futures import ThreadPoolExecutor

    results = [None] * len(items)
    if not items:
        return results

    def _run(idx, state, questions):
        try:
            return idx, ask(state, questions, timeout=timeout)
        except Exception:
            return idx, None

    workers = max(1, min(max_workers, len(items), _POOL_SIZE))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_run, i, state, questions)
                   for i, (state, questions) in enumerate(items)]
        for fut in futures:
            idx, answers = fut.result()
            results[idx] = answers
    return results
