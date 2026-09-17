#!/usr/bin/env python3
"""Runnable checks for lib/jev.py — the Jev "System One" HTTP client.
Covers answer parsing for all three primitives, retry-then-succeed on 429,
no-retry on 401/422, ask_many order preservation, and ask_many returning
None for a failed item. No network: the transport (_post) is monkeypatched.
Run: python3 lib/tests/test_jev.py"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import jev  # noqa: E402

# Make available() report True without touching real env/.env state.
jev._key_cache["loaded"] = True
jev._key_cache["value"] = "test-key"

# ---------------------------------------------------------------------------
# 1. available()
# ---------------------------------------------------------------------------
assert jev.available() is True

jev._key_cache["loaded"] = True
jev._key_cache["value"] = None
assert jev.available() is False
jev._key_cache["loaded"] = True
jev._key_cache["value"] = "test-key"

# ---------------------------------------------------------------------------
# 2. Answer parsing for all three primitives (noul, choice, score) via ask()
# ---------------------------------------------------------------------------
def _stub_200(answers):
    def _fn(body, key, timeout):
        assert key == "test-key", "must never be logged, but must be passed through"
        return 200, {"model": "jev-latest", "answers": answers,
                      "usage": {"input_tokens": 1, "output_tokens": 1}}, "{}"
    return _fn

orig_post = jev._post

jev._post = _stub_200({"is_urgent": {"type": "noul", "noul": 0.92}})
r = jev.ask("state", {"is_urgent": {"type": "noul", "instructions": "?"}})
assert r["is_urgent"]["type"] == "noul"
assert r["is_urgent"]["noul"] == 0.92

jev._post = _stub_200({"department": {"type": "choice", "choice": "technical",
                                       "probabilities": {"billing": 0.08, "technical": 0.85, "sales": 0.07},
                                       "confidence": 0.82}})
r = jev.ask("state", {"department": {"type": "choice", "instructions": "?", "criteria": {}}})
assert r["department"]["choice"] == "technical"
assert r["department"]["confidence"] == 0.82

jev._post = _stub_200({"frustration": {"type": "score", "score": 1.6,
                                        "legend": {"0": "Calm", "1": "Frustrated", "2": "Very angry"},
                                        "probabilities": {"0": 0.05, "1": 0.3, "2": 0.65},
                                        "confidence": 0.78}})
r = jev.ask("state", {"frustration": {"type": "score", "instructions": "?", "criteria": ["a", "b", "c"]}})
assert r["frustration"]["score"] == 1.6
assert r["frustration"]["legend"]["1"] == "Frustrated"

# ---------------------------------------------------------------------------
# 3. Retry-then-succeed on 429
# ---------------------------------------------------------------------------
calls = {"n": 0}
def _flaky_429(body, key, timeout):
    calls["n"] += 1
    if calls["n"] < 3:
        return 429, {"detail": "rate limited"}, "{}"
    return 200, {"model": "jev-latest",
                 "answers": {"x": {"type": "noul", "noul": 0.5}},
                 "usage": {}}, "{}"

jev._post = _flaky_429
orig_sleep = jev._sleep_backoff
jev._sleep_backoff = lambda attempt: None  # skip real backoff delay in tests
r = jev.ask("s", {"x": {"type": "noul", "instructions": "?"}}, retries=5)
assert r["x"]["noul"] == 0.5
assert calls["n"] == 3, f"expected 2 retries then success, got {calls['n']} calls"

# ---------------------------------------------------------------------------
# 4. No retry on 401 / 422
# ---------------------------------------------------------------------------
calls_401 = {"n": 0}
def _always_401(body, key, timeout):
    calls_401["n"] += 1
    return 401, {"detail": "invalid key"}, "{}"

jev._post = _always_401
try:
    jev.ask("s", {"x": {"type": "noul", "instructions": "?"}}, retries=5)
    assert False, "401 must raise JevError"
except jev.JevError as e:
    assert "invalid key" in str(e)
assert calls_401["n"] == 1, f"401 must not retry, got {calls_401['n']} calls"

calls_422 = {"n": 0}
def _always_422(body, key, timeout):
    calls_422["n"] += 1
    return 422, {"detail": "missing field 'questions'"}, "{}"

jev._post = _always_422
try:
    jev.ask("s", {"x": {"type": "noul", "instructions": "?"}}, retries=5)
    assert False, "422 must raise JevError"
except jev.JevError as e:
    assert "missing field" in str(e)
assert calls_422["n"] == 1, f"422 must not retry, got {calls_422['n']} calls"

# Exhausted retries (persistent 5xx) also raises JevError.
def _always_500(body, key, timeout):
    return 500, {"detail": "server error"}, "{}"
jev._post = _always_500
try:
    jev.ask("s", {"x": {"type": "noul", "instructions": "?"}}, retries=2)
    assert False, "exhausted retries must raise JevError"
except jev.JevError:
    pass

# ---------------------------------------------------------------------------
# 5. ask_many: order preservation + None for a failed item
# ---------------------------------------------------------------------------
def _fake_ask(state, questions, timeout=30.0, retries=3):
    if state == "bad":
        raise jev.JevError("simulated failure")
    time.sleep(0.01 if state == "slow" else 0)
    return {"v": {"type": "noul", "noul": float(state)}}

orig_ask = jev.ask
jev.ask = _fake_ask

items = [("0.1", {}), ("bad", {}), ("0.3", {}), ("slow", {}), ("0.5", {})]
results = jev.ask_many(items, max_workers=4)
assert len(results) == 5
assert results[0]["v"]["noul"] == 0.1
assert results[1] is None, "failed item must yield None, not raise"
assert results[2]["v"]["noul"] == 0.3
assert results[3] is None, "slow: float('slow') raises internally -> must yield None"
assert results[4]["v"]["noul"] == 0.5

# "slow" isn't a valid float, so _fake_ask raises ValueError inside ask_many's
# try/except -> confirmed above it comes back as None, not propagated.

# Empty input.
assert jev.ask_many([]) == []

jev.ask = orig_ask
jev._post = orig_post
jev._sleep_backoff = orig_sleep

print("jev OK")
