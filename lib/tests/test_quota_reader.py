#!/usr/bin/env python3
"""No-network checks for the READER's quota governor, the bulk mailbox index,
and incremental history sync.

(Companion to lib/tests/test_quota.py, which covers the transport-layer governor
in lib/draftutil.py. This file covers lib/gmail_quota.py, lib/mailbox_index.py,
lib/sync_state.py and the read path in lib/review_open_loops.py.)

The run this fixes died with a real "Quota exceeded ... Units per minute per
user" error, so these are the properties that must not silently regress:

  1. the limiter never exceeds the unit budget in ANY 60-second window,
  2. each method is billed its documented cost,
  3. a 429/quota error backs off (Google's algorithm) and retries instead of
     failing the account,
  4. and no failure, missing datum or skipped delta can ever produce a spurious
     ARCHIVE — everything uncertain resolves to keep.

Run: python3 lib/tests/test_quota.py
"""
import json
import os
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import draftutil as du       # noqa: E402
import gmail_quota as gq      # noqa: E402
import mailbox_index as mbi   # noqa: E402
import sync_state             # noqa: E402
import review_open_loops as rol  # noqa: E402


class FakeClock:
    """Virtual time: lets a simulated minute of API traffic run instantly."""

    def __init__(self):
        self.t = 0.0
        self.lock = threading.Lock()

    def now(self):
        return self.t

    def sleep(self, d):
        with self.lock:
            self.t += d


# --- 1. cost accounting ------------------------------------------------------
# Costs are load-bearing: under-billing a method is what trips the 429.
assert gq.cost_of("threads.get") == 40
assert gq.cost_of("messages.get") == 20
assert gq.cost_of("messages.list") == 5
assert gq.cost_of("threads.list") == 10
assert gq.cost_of("history.list") == 2
assert gq.cost_of("getProfile") == 1
assert gq.cost_of("labels.list") == 1
# An unknown method must bill pessimistically, never cheaply.
assert gq.cost_of("some.future.method") == 40

# The cost is inferred from the real argv shapes used across the codebase.
cases = {
    "messages.get": ["gmail", "users", "messages", "get", "--params", '{"id":"x"}'],
    "messages.list": ["gmail", "users", "messages", "list", "--params", "{}"],
    "threads.get": ["gmail", "users", "threads", "get", "--params", "{}"],
    "threads.list": ["gmail", "users", "threads", "list", "--params", "{}"],
    "history.list": ["gmail", "users", "history", "list", "--params", "{}"],
    "labels.list": ["gmail", "users", "labels", "list", "--params", "{}"],
    "getProfile": ["gmail", "users", "getProfile", "--params", "{}"],
    "messages.batchModify": ["gmail", "users", "messages", "batchModify",
                             "--params", "{}", "--json", "{}"],
}
for expected, argv in cases.items():
    assert gq.method_from_args(argv) == expected, (argv, gq.method_from_args(argv))


# --- 2. the limiter never exceeds the budget in any 60s window ---------------
# This is the invariant that was violated in production (~78,000 units/min
# against a 6,000 ceiling). Asserted over a sliding window, not just in total.
clock = FakeClock()
budget = 6000
lim = gq.UnitLimiter(units_per_minute=budget, window=60.0,
                     clock=clock.now, sleep=clock.sleep)

grants = []          # (timestamp, cost)
for _ in range(400):  # 400 x threads.get = 16,000 units, ~2.7 minutes of budget
    lim.acquire(gq.cost_of("threads.get"))
    grants.append((clock.now(), gq.cost_of("threads.get")))

# Check every window anchored at a grant: the worst case always starts at one.
for start, _ in grants:
    spent = sum(c for t, c in grants if start <= t < start + 60.0)
    assert spent <= budget, f"window at {start}: {spent} > {budget}"

# Budget honoured => the work took at least the arithmetic minimum time.
assert clock.now() >= (400 * 40) / budget * 60 - 60, clock.now()
assert lim.total_units == 400 * 40
assert lim.stats()["calls"] == 400

# Mixed costs are billed individually, not averaged.
clock2 = FakeClock()
lim2 = gq.UnitLimiter(units_per_minute=1000, window=60.0,
                      clock=clock2.now, sleep=clock2.sleep)
for m in ["messages.get", "messages.list", "threads.get", "labels.list"]:
    lim2.acquire(gq.cost_of(m))
assert lim2.total_units == 20 + 5 + 40 + 1

# Concurrent workers share one budget (the real usage pattern).
clock3 = FakeClock()
lim3 = gq.UnitLimiter(units_per_minute=600, window=60.0,
                      clock=clock3.now, sleep=clock3.sleep)
seen = []
seen_lock = threading.Lock()


def worker():
    for _ in range(10):
        lim3.acquire(20)
        with seen_lock:
            seen.append((lim3._clock(), 20))


threads = [threading.Thread(target=worker) for _ in range(8)]
[t.start() for t in threads]
[t.join() for t in threads]
assert lim3.total_units == 8 * 10 * 20
for start, _ in seen:
    spent = sum(c for t, c in seen if start <= t < start + 60.0)
    assert spent <= 600, f"concurrent window at {start}: {spent} > 600"


# --- 3. quota errors: detection, backoff, retry ------------------------------
# The verbatim production error must be recognised as retryable.
PROD_ERROR = ("error[api]: Quota exceeded for quota metric 'Total Query Cost' "
              "and limit 'Units per minute per user' of service "
              "'gmail.googleapis.com' for consumer 'project_number:288799635323'")
assert gq.is_quota_error(RuntimeError(PROD_ERROR))
assert gq.is_quota_error(RuntimeError("429 Too Many Requests"))
assert gq.is_quota_error(RuntimeError("rateLimitExceeded"))
assert gq.is_quota_error(RuntimeError("userRateLimitExceeded"))
# Auth/permanent failures must NOT be retried as if they were transient.
assert not gq.is_quota_error(RuntimeError("401 unauthorized"))
assert not gq.is_quota_error(RuntimeError("404 not found"))

# Google's documented algorithm: min((2^n) + random_ms, maximum_backoff).
assert gq.backoff_delay(0, rand=lambda: 0.0) == 1.0
assert gq.backoff_delay(1, rand=lambda: 0.0) == 2.0
assert gq.backoff_delay(2, rand=lambda: 0.0) == 4.0
assert gq.backoff_delay(3, rand=lambda: 0.0) == 8.0
# Jitter is bounded by 1000ms and increases the delay.
assert 4.0 < gq.backoff_delay(2, rand=lambda: 0.5) <= 5.0
# Truncated at maximum_backoff however large n gets.
assert gq.backoff_delay(30, rand=lambda: 1.0) == gq.MAX_BACKOFF_SECONDS
# Delays increase monotonically until the cap.
seq = [gq.backoff_delay(n, rand=lambda: 0.0) for n in range(8)]
assert seq == sorted(seq) and seq[-1] <= gq.MAX_BACKOFF_SECONDS

# A quota error retries with backoff and then SUCCEEDS (the account is not failed).
slept = []
attempts = {"n": 0}


def flaky():
    attempts["n"] += 1
    if attempts["n"] <= 2:
        raise RuntimeError(PROD_ERROR)
    return {"ok": True}


clock4 = FakeClock()
lim4 = gq.UnitLimiter(units_per_minute=6000, window=60.0,
                      clock=clock4.now, sleep=clock4.sleep)
out = gq.call_with_quota(flaky, "messages.get", limiter=lim4,
                         sleep=slept.append, rand=lambda: 0.0)
assert out == {"ok": True}
assert attempts["n"] == 3
assert slept == [1.0, 2.0], slept
# Every attempt was billed, and the shared limiter was penalised hard enough that
# it actually had to wait, which is how sibling workers get slowed down too.
assert lim4.total_calls == 3
assert lim4.total_units == 3 * 20
assert lim4.total_wait > 0, lim4.stats()

# A non-quota error is raised immediately, with no retry storm.
calls = {"n": 0}


def auth_fail():
    calls["n"] += 1
    raise RuntimeError("401 unauthorized")


try:
    gq.call_with_quota(auth_fail, "messages.get", sleep=slept.append)
    raise AssertionError("should have raised")
except RuntimeError as e:
    assert "401" in str(e)
assert calls["n"] == 1, calls

# Exhausting retries re-raises rather than returning a bogus success.
try:
    gq.call_with_quota(lambda: (_ for _ in ()).throw(RuntimeError(PROD_ERROR)),
                       "messages.get", max_retries=2,
                       sleep=lambda d: None, rand=lambda: 0.0)
    raise AssertionError("should have raised")
except RuntimeError as e:
    assert "Quota exceeded" in str(e)


# --- 4. bulk index correctness and honesty -----------------------------------
# Models the live shape: messages.list is newest-first, so the first occurrence
# of a thread id is its newest message.
idx = mbi.MailboxIndex(
    order={"t1": ["m5", "m3", "m1"], "t2": ["m9"], "t3": ["m8", "m7"]},
    sent_ids={"m5", "m7"}, pages=4)
assert idx.newest("t1") == "m5"
assert idx.message_ids("t1") == ["m5", "m3", "m1"]     # what batchModify archives
assert idx.last_from_owner("t1") is True               # newest IS the owner's
assert idx.last_from_owner("t3") is False              # owner's msg is older, not newest
assert idx.last_from_owner("t2") is False
# An unknown thread must never claim owner-sent: that is the deterministic
# ARCHIVE path, so an unknown has to fall through to the classifier instead.
assert idx.covers("nope") is False
assert idx.last_from_owner("nope") is False
assert idx.message_ids("nope") == []
assert idx.units == 4 * 5

# A failed scan degrades to None (use the per-thread path); it never raises and
# never returns a half-built index that would under-report a thread's messages.
def exploding(_args):
    raise RuntimeError("gws exploded")


assert mbi.build_index("cfg", lambda c: {}, runner=exploding) is None

# A successful build parses gws' page-per-line output and ignores keyring noise.
def fake_runner(args):
    q = json.loads(args[args.index("--params") + 1])["q"]
    if q == mbi.SENT_QUERY:
        return '{"messages":[{"id":"m5","threadId":"t1"}]}\n'
    return ('keyring noise line\n'
            '{"messages":[{"id":"m5","threadId":"t1"},{"id":"m3","threadId":"t1"}]}\n'
            '{"messages":[{"id":"m9","threadId":"t2"}]}\n')


built = mbi.build_index("cfg", lambda c: {}, runner=fake_runner)
assert built.message_ids("t1") == ["m5", "m3"]
assert built.newest("t1") == "m5"
assert built.last_from_owner("t1") is True
assert built.last_from_owner("t2") is False


# --- 5. incremental sync: uncertainty always means "read more", never "skip" --
pages = [{"history": [{"id": "1", "messagesAdded": [
              {"message": {"id": "m1", "threadId": "t1"}}]}],
          "nextPageToken": "p2"},
         {"history": [{"id": "2", "labelsRemoved": [
              {"message": {"id": "m2", "threadId": "t2"}}]}]}]
it = iter(pages)
got, status = sync_state.changed_threads(lambda _t: next(it), "500")
assert status == "ok" and got == {"t1", "t2"}, (status, got)

# An EXPIRED cursor (measured live: "Requested entity was not found") must report
# expired with NO thread set, forcing a full read rather than an empty delta.
def expired(_t):
    raise RuntimeError("error[api]: Requested entity was not found.")


assert sync_state.changed_threads(expired, "1") == (None, "expired")
assert sync_state.is_expired_error(RuntimeError("Requested entity was not found."))

# Any other failure also yields None => full read. Critically, an error must
# never be representable as "nothing changed".
assert sync_state.changed_threads(
    lambda _t: (_ for _ in ()).throw(RuntimeError("connection reset")), "5") \
    == (None, "error")
assert sync_state.changed_threads(lambda _t: None, "5") == (None, "error")
assert sync_state.changed_threads(lambda _t: {}, None) == (None, "error")
# Only a clean API response may report an empty (genuinely unchanged) delta.
assert sync_state.changed_threads(lambda _t: {"history": []}, "5") == (set(), "ok")

# Cursor round-trip is per-account and isolated.
sync_state.STATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".test_sync_state.json")
try:
    if os.path.exists(sync_state.STATE_PATH):
        os.remove(sync_state.STATE_PATH)
    assert sync_state.load("a@x.com") is None          # no cursor -> full read
    assert sync_state.save("a@x.com", "12345") is True
    assert sync_state.load("a@x.com") == "12345"
    assert sync_state.load("b@x.com") is None          # accounts independent
    sync_state.save("b@x.com", "999")
    assert sync_state.load("a@x.com") == "12345"       # unaffected by the other
    # A stale cursor is refused rather than trusted.
    import time as _t
    raw = json.load(open(sync_state.STATE_PATH))
    raw["a@x.com"]["updated_at"] = int(_t.time()) - (sync_state.MAX_CURSOR_AGE_SECONDS + 10)
    json.dump(raw, open(sync_state.STATE_PATH, "w"))
    assert sync_state.load("a@x.com") is None
    # A falsy history id is never persisted (would otherwise look like a cursor).
    assert sync_state.save("c@x.com", None) is False
    assert sync_state.load("c@x.com") is None
    # Clearing forces a full read next time.
    sync_state.clear("b@x.com")
    assert sync_state.load("b@x.com") is None
    # A corrupt state file degrades to "full read", never to a bogus cursor.
    open(sync_state.STATE_PATH, "w").write("{not json")
    assert sync_state.load("a@x.com") is None
finally:
    if os.path.exists(sync_state.STATE_PATH):
        os.remove(sync_state.STATE_PATH)


# --- 6. THE SAFETY PROPERTY: no failure can produce a spurious archive --------
# PRODUCT.md: reversibility is the product. A read that fails, or data that is
# missing, must resolve to "keep" and never to "archive".

# (a) A thread the bulk index does not cover is never called owner-handled, so it
#     cannot take the deterministic archive path on missing information.
sparse = mbi.MailboxIndex(order={}, sent_ids=set(), pages=1)
assert sparse.last_from_owner("unknown-thread") is False

# (b) A failed classifier call keeps the thread.
assert rol._jev_decide({}) == "keep"
assert rol._jev_decide(None) == "keep"
# Missing answers use keep-biased defaults.
assert rol._jev_decide({"is_cold_outreach": {"noul": 0.99}}) == "keep"
assert rol._jev_decide({"awaiting_user": {"noul": 0.0}}) == "keep"  # no cold/automated signal

# (c) Only a confident, corroborated archive archives.
archivable = {"awaiting_user": {"noul": 0.01}, "is_protected": {"noul": 0.01},
              "is_cold_outreach": {"noul": 0.95}, "urgency": {"score": 0.0}}
assert rol._jev_decide(archivable) == "archive"
# ...and any single missing/uncertain signal flips it back to keep.
for drop in ("awaiting_user", "is_protected", "urgency"):
    partial = {k: v for k, v in archivable.items() if k != drop}
    assert rol._jev_decide(partial) == "keep", drop
# Protected mail is kept even when everything else says noise.
protected = dict(archivable, is_protected={"noul": 0.9})
assert rol._jev_decide(protected) == "keep"

# (d) A failed reply-history lookup assumes "replied" (keep-biased), never "cold".
original_gws = rol.iz.gws
try:
    def failing_gws(_cfg, _args):
        raise RuntimeError("temporary network failure")

    rol.iz.gws = failing_gws
    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()
    assert rol._replied_before("cfg", "unknown@example.com") is True

    # (e) The grouped prefetch must not mark senders "never replied" unless it has
    #     PROVEN the grouped query discriminates. A broken/empty-returning query
    #     would otherwise make every sender look cold and bias the run to archive.
    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()

    def always_empty(_cfg, _args):
        return {}          # no sent mail => positive control cannot be built

    rol.iz.gws = always_empty
    resolved = rol._prefetch_replied("cfg", ["a@x.com", "b@x.com"])
    assert resolved == 0, resolved
    with rol._REPLIED_LOCK:
        assert "a@x.com" not in rol._REPLIED     # nothing asserted without proof

    # (f) With a working positive control, grouped negatives ARE trusted, and a
    #     positive group is left for individual resolution (never marked False).
    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()

    def working_gws(_cfg, args):
        params = json.loads(args[args.index("--params") + 1])
        if "messages" in args and "get" in args:
            return {"payload": {"headers": [
                {"name": "To", "value": "known@partner.com"}]}}
        q = params.get("q", "")
        if q == "in:sent":
            return {"messages": [{"id": "sent-1"}]}
        if "known@partner.com" in q:
            return {"messages": [{"id": "hit"}]}      # positive control passes
        if "hot@x.com" in q:
            return {"messages": [{"id": "hit"}]}      # group contains a match
        return {}                                     # genuine negative

    rol.iz.gws = working_gws
    n = rol._prefetch_replied("cfg", ["cold1@x.com", "cold2@x.com"])
    assert n == 2, n
    with rol._REPLIED_LOCK:
        assert rol._REPLIED["cold1@x.com"] is False
        assert rol._REPLIED["cold2@x.com"] is False

    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()
    n = rol._prefetch_replied("cfg", ["hot@x.com", "other@x.com"])
    assert n == 0, n                 # ambiguous group: nobody marked "never replied"
    with rol._REPLIED_LOCK:
        assert "other@x.com" not in rol._REPLIED
finally:
    rol.iz.gws = original_gws
    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()

# (g) A thread whose read raised is dropped from the result, so it is never
#     handed to the archiver. Dropped == left in the inbox == safe.
original_emit = rol._emit_progress
try:
    rol._emit_progress = lambda pct, label="": None

    def half_failing(_cfg, tid, _me, _index=None):
        if tid == "bad":
            raise RuntimeError("quota exceeded for quota metric 'Total Query Cost'")
        return {"id": tid, "ids": [tid + "-m"], "last_from": "s@x.com",
                "last_email": "s@x.com", "last_from_owner": False,
                "subject": "s", "snippet": "x", "label_ids": set()}

    original_info = rol._thread_info
    original_prefetch = rol._prefetch_replied
    original_replied = rol._replied_before
    rol._thread_info = half_failing
    rol._prefetch_replied = lambda *a, **k: 0
    rol._replied_before = lambda _cfg, _e: True
    try:
        infos = rol._read_infos_parallel("cfg", ["good1", "bad", "good2"],
                                         "me@x.com", max_workers=2)
        ids = sorted(i["id"] for i in infos)
        assert ids == ["good1", "good2"], ids     # 'bad' silently kept, not archived
        assert all("replied_before" in i for i in infos)
    finally:
        rol._thread_info = original_info
        rol._prefetch_replied = original_prefetch
        rol._replied_before = original_replied
finally:
    rol._emit_progress = original_emit


# --- 7. the classifier's input contract is unchanged -------------------------
# The fast path must produce EXACTLY the keys _classify/_jev_state consume;
# a missing key would silently change a judgment.
REQUIRED = {"id", "ids", "last_from", "last_email", "last_from_owner",
            "subject", "snippet", "label_ids"}
index = mbi.MailboxIndex(order={"t1": ["m2", "m1"]}, sent_ids=set(), pages=1)
original_gws = rol.iz.gws
try:
    def meta_gws(_cfg, args):
        return {"labelIds": ["INBOX", "UNREAD"], "snippet": "hello there",
                "threadId": "t1", "payload": {"headers": [
                    {"name": "From", "value": "Real Person <p@x.com>"},
                    {"name": "Subject", "value": "A subject"}]}}

    rol.iz.gws = meta_gws
    info = rol._thread_info_via_index("cfg", "t1", "me@x.com", index)
    assert REQUIRED <= set(info), REQUIRED - set(info)
    assert info["ids"] == ["m2", "m1"]            # full thread, for batchModify
    assert info["last_email"] == "p@x.com"
    assert info["subject"] == "A subject"
    assert info["last_from_owner"] is False
    assert isinstance(info["label_ids"], set)
    # The owner's own address in From is still detected without the SENT label.
    info2 = rol._thread_info_via_index("cfg", "t1", "p@x.com", index)
    assert info2["last_from_owner"] is True
finally:
    rol.iz.gws = original_gws

# Both paths provide classifier inputs. Only a full read can additionally
# prove label membership on EVERY message, for safe category no-op detection.
original_gws = rol.iz.gws
try:
    def thread_gws(_cfg, _args):
        return {"messages": [
            {"id": "m1", "labelIds": ["INBOX"], "snippet": "old",
             "payload": {"headers": [{"name": "From", "value": "A <a@x.com>"},
                                     {"name": "Subject", "value": "S"}]}},
            {"id": "m2", "labelIds": ["INBOX"], "snippet": "new",
             "payload": {"headers": [{"name": "From", "value": "B <b@x.com>"},
                                     {"name": "Subject", "value": "S"}]}}]}

    rol.iz.gws = thread_gws
    slow = rol._thread_info_via_get("cfg", "t1", "me@x.com")
    assert set(slow) == REQUIRED | {"label_ids_all"}, set(slow) ^ REQUIRED
    assert slow["label_ids_all"] == {"INBOX"}
    assert "label_ids_all" not in info, "newest-message metadata cannot prove full-thread labels"
finally:
    rol.iz.gws = original_gws

# --- 8. no double-throttling against the transport-layer governor ------------
# lib/draftutil._gws grew its own units/minute governor, and it sits UNDERNEATH
# this reader. If both enforced a budget, every read would be billed twice: two
# ledgers each believing they spent the units, both throttling on half-true books
# and both reporting inflated totals. The reader must defer when the transport
# governs, while still doing its own cost accounting and quota-aware retries.
assert rol._TRANSPORT_GOVERNS == hasattr(du, "_await_quota")
if rol._TRANSPORT_GOVERNS:
    # Deferred: effectively unlimited, so the transport layer alone paces the run.
    assert rol._LIMITER.budget > gq.GMAIL_UNITS_PER_MINUTE, rol._LIMITER.budget
else:
    # Standalone: the reader must enforce a real budget under Gmail's ceiling.
    assert rol._LIMITER.budget <= gq.GMAIL_UNITS_PER_MINUTE, rol._LIMITER.budget
# Either way the reader still ACCOUNTS for cost, which is what the report uses.
before = rol._LIMITER.total_units
rol._LIMITER.acquire(gq.cost_of("threads.get"))
assert rol._LIMITER.total_units == before + 40

print("quota_reader OK")
