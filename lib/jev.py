#!/usr/bin/env python3
"""HTTP client for TypeSafe AI's Jev "System One" endpoint.

Jev answers typed questions (noul / choice / score) against a state, with
calibrated probabilities. It does not generate prose — drafting stays on an
LLM provider (see lib/llm.py). See docs/JEV_CONTRACT.md for the interface
this module must implement.

Endpoint: POST https://api.typesafe.ai/v1/systemone
Auth: env JEV, else KEY=VALUE parsed from a .env file at the repo root.
Never logs or prints the key.
"""
import json
import os
import random
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENV_PATH = os.path.join(ROOT, ".env")
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
    """Resolve the JEV API key: env var JEV first, else .env at repo root. Cached."""
    if _key_cache["loaded"]:
        return _key_cache["value"]
    key = os.environ.get("JEV")
    if not key:
        key = _parse_env_file(ENV_PATH).get("JEV")
    _key_cache["loaded"] = True
    _key_cache["value"] = key or None
    return _key_cache["value"]


def available():
    """True if a JEV API key is configured (env JEV, or .env at repo root)."""
    return _get_key() is not None


def _post(body, key, timeout):
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

    workers = max(1, min(max_workers, len(items)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_run, i, state, questions)
                   for i, (state, questions) in enumerate(items)]
        for fut in futures:
            idx, answers = fut.result()
            results[idx] = answers
    return results
