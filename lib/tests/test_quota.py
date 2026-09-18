#!/usr/bin/env python3
"""Runnable checks for the Gmail quota governor in lib/draftutil.py.

Gmail bills per quota UNIT (threads.get = 40, messages.list = 5, ...) and allows
6,000 units per minute per user. Exceeding it returns a 403 whose reason is
rateLimitExceeded — which the old code classified as fatal, so a large run failed
every read instantly, retried at the wrong layer, and looked frozen while burning
still more quota.

These checks pin the three things that has to keep being true:
  1. a quota 403 is treated as transient, while a real 403 stays fatal,
  2. per-method unit costs are attributed to the right method,
  3. the limiter keeps concurrent callers under the budget.

No network: the limiter is pure bookkeeping.
Run: python3 lib/tests/test_quota.py
"""
import os, sys, threading, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import draftutil as du   # noqa: E402


# --- 1. quota errors are transient, real auth failures are not ----------------
QUOTA_MSG = ("Quota exceeded for quota metric 'Total Query Cost' and limit "
             "'Units per minute per user' of service 'gmail.googleapis.com'").lower()
assert any(p in QUOTA_MSG for p in du._QUOTA), "quota 403 must be recognised as quota"

RATE_MSG = '{"code": 403, "reason": "rateLimitExceeded"}'.lower()
assert any(p in RATE_MSG for p in du._QUOTA), "rateLimitExceeded must be recognised"

# A genuine permission problem must NOT be mistaken for a quota blip, or the app
# would retry a hopeless call instead of telling the user to fix access.
PERM_MSG = "error 403: caller does not have required permission".lower()
assert not any(p in PERM_MSG for p in du._QUOTA), "real 403 must not look transient"
assert any(p in PERM_MSG for p in du._FATAL), "real 403 must stay fatal"


# --- 2. unit costs are attributed to the right method -------------------------
CASES = [
    (["gmail", "users", "threads", "get", "--params", "{}"], "threads.get", 40),
    (["gmail", "users", "threads", "list", "--params", "{}"], "threads.list", 10),
    (["gmail", "users", "messages", "get", "--params", "{}"], "messages.get", 20),
    (["gmail", "users", "messages", "list", "--params", "{}"], "messages.list", 5),
    (["gmail", "users", "labels", "list", "--params", "{}"], "labels.list", 1),
    (["gmail", "users", "history", "list", "--params", "{}"], "history.list", 2),
]
for args, method, cost in CASES:
    got = du._method_of(args)
    assert got == method, (args, got, method)
    assert du._UNIT_COST[method] == cost, (method, du._UNIT_COST[method], cost)

# An unrecognised call must still be charged something, never treated as free —
# otherwise a new call type could silently blow the budget.
du._quota_spent.clear()
du._await_quota(["gmail", "users", "somethingNew", "--params", "{}"])
assert du._quota_spent and du._quota_spent[0][1] > 0, "unknown methods must still cost"


# --- 3. the limiter holds concurrent callers under budget ---------------------
# The expensive case: many workers all issuing the priciest call.
du._quota_spent.clear()
ARGS = ["gmail", "users", "threads", "get", "--params", "{}"]
admitted = [0]
lock = threading.Lock()
deadline = time.time() + 3.0


def hammer():
    while time.time() < deadline:
        du._await_quota(ARGS)
        with lock:
            admitted[0] += 1


threads = [threading.Thread(target=hammer) for _ in range(16)]
start = time.time()
for t in threads:
    t.start()
for t in threads:
    t.join()
elapsed = max(time.time() - start, 0.001)

units = admitted[0] * du._UNIT_COST["threads.get"]
# The real bound that matters: whatever the window boundaries, throughput must stay
# under Gmail's hard 6,000/min ceiling. (It can exceed the internal budget slightly,
# because reservations made just before the run age out during it and free capacity —
# that headroom between _UNIT_BUDGET and 6,000 is exactly what absorbs it.)
rate_per_min = units / elapsed * 60.0
assert rate_per_min <= 6000, (
    f"admitted {units} units in {elapsed:.1f}s = {rate_per_min:.0f}/min, over Gmail's limit")

# And the unthrottled rate this replaces really was far over, so the limiter is
# doing real work rather than sitting inert: 16 workers x ~1.8 calls/s x 40 units
# is ~78,000 units/min.
assert rate_per_min < 20000, f"limiter looks inert at {rate_per_min:.0f} units/min"

# And the budget itself must leave headroom under Gmail's real 6,000/min ceiling.
assert du._UNIT_BUDGET < 6000, "budget must sit below Gmail's hard limit"

# Sliding window, not a bucket: entries older than a minute are forgotten, so a
# quiet period restores full capacity rather than staying penalised forever.
du._quota_spent[:] = [(time.time() - 120, 5000)]
du._await_quota(ARGS)
assert all(time.time() - t < 60.0 for t, _ in du._quota_spent), "stale units must expire"

print("quota OK")
