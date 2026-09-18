#!/usr/bin/env python3
"""No-network checks for the persistent thread cache (lib/thread_cache.py) and
its wiring into lib/review_open_loops.py.

The cache exists to stop a daily run re-paying ~35,000 Gmail quota units and
~1,557 Jev calls for facts that did not change. That is only worth having if it
cannot cost the user mail, so these tests are mostly about what the cache
REFUSES to do. The properties asserted here:

  1. a hit at a matching historyId skips the per-thread read entirely (0 units),
  2. a CHANGED historyId forces a real re-read and a real re-decision, and a
     cached ARCHIVE verdict is never served for a changed thread,
  3. a corrupt, truncated, version-mismatched or garbage cache degrades to a
     cold run, never to a spurious archive,
  4. editing the keep policy, the categories, the learned preferences or any
     JEV_* threshold invalidates every cached verdict,
  5. replied_before is cached asymmetrically: True (keep-biased, monotone) for
     30 days, False (archive-biased, falsified by one reply) for hours,
  6. writes are atomic, so a crash mid-write cannot publish a truncated file
     that a later run misreads as "nothing changed".

Run: python3 lib/tests/test_thread_cache.py
"""
import json
import os
import shutil
import sys
import tempfile

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, LIB)
import jev                       # noqa: E402
import thread_cache as tc        # noqa: E402
import review_open_loops as rol  # noqa: E402

TMP = tempfile.mkdtemp(prefix="thread_cache_test_")
_n = {"i": 0}


def cache_path():
    _n["i"] += 1
    return os.path.join(TMP, f"c{_n['i']}.json")


def info(tid="t1", email="a@b.com", owner=False, subject="Subject", snippet="snip"):
    """Exactly the shape lib/review_open_loops._thread_info returns."""
    return {"id": tid, "ids": [tid + "-m1"], "last_from": f"Someone <{email}>",
            "last_email": email, "last_from_owner": owner, "subject": subject,
            "snippet": snippet, "label_ids": {"INBOX"}}


# ===========================================================================
# 1. Thread metadata: historyId is the contract
# ===========================================================================
p = cache_path()
c = tc.load("acct", path=p)

# Cold: nothing is known, so everything is a miss -> a real read.
assert c.thread_info("t1", "100") is None

c.put_thread("t1", "100", info())
# Same historyId -> hit, and the shape survives the JSON round trip exactly
# (label_ids must come back as a SET: _backfill_partition does set membership).
hit = c.thread_info("t1", "100")
assert hit == info(), hit
assert isinstance(hit["label_ids"], set), hit["label_ids"]
assert isinstance(hit["ids"], list)

# CHANGED historyId -> miss. This is the whole safety mechanism.
assert c.thread_info("t1", "101") is None
# A missing historyId is not proof of anything, so it is also a miss.
assert c.thread_info("t1", None) is None
assert c.thread_info("t1", "") is None
# An unknown thread is a miss.
assert c.thread_info("nope", "100") is None

# Survives a save/load cycle, which is the point of the whole module.
assert c.save() is True
assert tc.load("acct", path=p).thread_info("t1", "100") == info()
assert tc.load("acct", path=p).thread_info("t1", "999") is None

# A disabled cache is a correct no-op: every getter misses, every putter is inert.
off = tc.load("acct", enabled=False, path=p)
assert off.thread_info("t1", "100") is None
assert off.put_thread("t2", "1", info("t2")) is False
assert off.replied_before("a@b.com") is None
assert off.save() is False

# put_thread refuses anything it cannot validate later or hand back intact.
c2 = tc.load("acct2", path=cache_path())
assert c2.put_thread("t1", None, info()) is False      # no historyId to validate
assert c2.put_thread("", "100", info()) is False
assert c2.put_thread("t1", "100", {"id": "t1"}) is False          # missing keys
assert c2.put_thread("t1", "100", "not a dict") is False


# ===========================================================================
# 2. Corrupt / truncated / version-mismatched caches degrade, never guess
# ===========================================================================
for broken in [
    '{"version": 1, "threads": {"t1": {"h": "100", "info":',   # truncated mid-write
    "",                                                        # empty (crashed create)
    "not json at all",
    "[1, 2, 3]",                                               # valid JSON, wrong type
    '{"version": 999, "threads": {"t1": {"h":"100","info":{}}}}',   # future schema
    '{"version": 0, "threads": {"t1": {"h":"100","info":{}}}}',     # older schema
    '{"version": 1, "threads": "not a dict"}',                 # mangled section
    '{"version": 1}',                                          # sections absent
]:
    bp = cache_path()
    with open(bp, "w") as f:
        f.write(broken)
    b = tc.load("acct", path=bp)
    assert b.thread_info("t1", "100") is None, broken[:40]
    assert b.replied_before("a@b.com") is None, broken[:40]
    assert b.verdict("t1", "100", "fp") is None, broken[:40]
    # And it must still be usable: a degraded cache re-populates rather than
    # failing the run.
    assert b.put_thread("t1", "100", info()) is True
    assert b.save() is True
    assert tc.load("acct", path=bp).thread_info("t1", "100") == info()

# Individually corrupt ROWS inside an otherwise valid file are also misses. A
# half-written row must never be handed to the classifier as partial inputs.
bp = cache_path()
good = tc.load("acct", path=bp)
good.put_thread("ok", "100", info("ok"))
good.save()
raw = json.load(open(bp))
raw["threads"]["missing_keys"] = {"h": "100", "t": tc._now(), "info": {"id": "x"}}
raw["threads"]["bad_ids"] = {"h": "100", "t": tc._now(),
                             "info": dict(tc._dump_info(info("bad_ids")), ids="nope")}
raw["threads"]["no_history"] = {"t": tc._now(), "info": tc._dump_info(info("no_history"))}
raw["threads"]["null_row"] = None
raw["threads"]["empty_ids"] = {"h": "100", "t": tc._now(),
                               "info": dict(tc._dump_info(info("empty_ids")), ids=[])}
# The dangerous one: last_from_owner is the DETERMINISTIC archive path, so a
# non-boolean truthy value must never be trusted as True.
raw["threads"]["truthy_owner"] = {
    "h": "100", "t": tc._now(),
    "info": dict(tc._dump_info(info("truthy_owner")), last_from_owner="yes")}
json.dump(raw, open(bp, "w"))

recovered = tc.load("acct", path=bp)
assert recovered.thread_info("ok", "100") == info("ok")        # good row still works
for bad in ("missing_keys", "bad_ids", "no_history", "null_row", "empty_ids"):
    assert recovered.thread_info(bad, "100") is None, bad
coerced = recovered.thread_info("truthy_owner", "100")
assert coerced is not None and coerced["last_from_owner"] is False, coerced

# Entries older than MAX_ENTRY_AGE are not served, and are pruned on save.
ap = cache_path()
aged = tc.load("acct", path=ap)
aged.put_thread("old", "100", info("old"))
aged._threads["old"]["t"] = tc._now() - tc.MAX_ENTRY_AGE - 10
assert aged.thread_info("old", "100") is None
aged.save(force=True)
assert "old" not in json.load(open(ap))["threads"]

# The size cap keeps the file bounded however long the tool runs.
cap = tc.load("acct", path=cache_path())
old_max, tc.MAX_ENTRIES = tc.MAX_ENTRIES, 5
for i in range(20):
    cap.put_thread(f"t{i}", "100", info(f"t{i}"))
    cap._threads[f"t{i}"]["t"] = tc._now() - 20 + i   # newest last, all timestamps in the past
cap._prune()
assert len(cap._threads) == 5, len(cap._threads)
assert cap.thread_info("t19", "100") is not None      # newest survived
assert cap.thread_info("t0", "100") is None           # oldest evicted
tc.MAX_ENTRIES = old_max


# ===========================================================================
# 3. replied_before: the asymmetry, which is the mail-loss direction
# ===========================================================================
# Stated plainly because getting it backwards is how a cache starts losing mail:
#   replied_before=False  -> the thread looks like cold outreach -> ARCHIVE.
#   replied_before=True   -> the owner knows this sender         -> keep-biased.
# A stale False is therefore UNSAFE (it can archive a thread from someone the
# owner started corresponding with this morning) while a stale True merely costs
# an unnecessary keep. So False expires in hours and True lasts for weeks.
assert tc.REPLIED_FALSE_TTL < tc.REPLIED_TRUE_TTL
assert tc.REPLIED_FALSE_TTL <= 12 * 3600, "a False must expire in hours, not days"

r = tc.load("acct", path=cache_path())
assert r.replied_before("unknown@x.com") is None      # unknown -> go and probe

r.put_replied("knows@x.com", True)
r.put_replied("cold@x.com", False)
assert r.replied_before("knows@x.com") is True
assert r.replied_before("cold@x.com") is False
assert r.replied_before("KNOWS@X.COM") is True        # case-insensitive

# Age each one to just past the SHORT ttl.
just_past_false = tc._now() - tc.REPLIED_FALSE_TTL - 1
r._senders["knows@x.com"]["t"] = just_past_false
r._senders["cold@x.com"]["t"] = just_past_false
# The True is still trusted (monotone, keep-biased); the False is NOT.
assert r.replied_before("knows@x.com") is True
assert r.replied_before("cold@x.com") is None, "a stale False must force a re-probe"

# A True eventually expires too, so the cache stays bounded in time.
r._senders["knows@x.com"]["t"] = tc._now() - tc.REPLIED_TRUE_TTL - 1
assert r.replied_before("knows@x.com") is None

# Non-boolean or empty input is never stored or served.
assert r.put_replied("", True) is False
assert r.put_replied("x@y.com", "yes") is False
r._senders["weird@x.com"] = {"v": "yes", "t": tc._now()}
assert r.replied_before("weird@x.com") is None


# ===========================================================================
# 4. The verdict fingerprint: what invalidates what
# ===========================================================================
state = {"thread": {"subject": "s", "replied_before": False},
         "keep_policy": "keep real people"}
questions = {"category": {"criteria": {"Needs reply": "d"}}}
thresholds = {"archive_awaiting": 0.25}
base = tc.verdict_fingerprint(state, questions, thresholds)

# Stable across calls and across dict ordering (so it is usable as a key at all).
assert base == tc.verdict_fingerprint(state, questions, thresholds)
assert base == tc.verdict_fingerprint(
    {"keep_policy": "keep real people",
     "thread": {"replied_before": False, "subject": "s"}}, questions, thresholds)

# Each of the four invalidating inputs changes it.
policy_edit = dict(state, keep_policy="keep everything from clients")
assert tc.verdict_fingerprint(policy_edit, questions, thresholds) != base
learned = dict(state, learned_preferences="archive newsletters from Acme")
assert tc.verdict_fingerprint(learned, questions, thresholds) != base
new_cats = {"category": {"criteria": {"Needs reply": "d", "Finance": "money"}}}
assert tc.verdict_fingerprint(state, new_cats, thresholds) != base
assert tc.verdict_fingerprint(state, questions, {"archive_awaiting": 0.30}) != base
# And so does the thread's own content, including replied_before flipping —
# which matters because that can change WITHOUT the thread's historyId moving.
flipped = {"thread": {"subject": "s", "replied_before": True},
           "keep_policy": "keep real people"}
assert tc.verdict_fingerprint(flipped, questions, thresholds) != base
assert tc.verdict_fingerprint(
    {"thread": {"subject": "different", "replied_before": False},
     "keep_policy": "keep real people"}, questions, thresholds) != base

# Types must not collide: 0.75 and "0.75" are different policies.
assert tc.verdict_fingerprint(state, questions, {"t": 0.75}) != \
       tc.verdict_fingerprint(state, questions, {"t": "0.75"})

# The real signature covers every JEV_* constant, so tuning one is never inert.
sig = rol._threshold_signature()
for const in ("JEV_KEEP_AWAITING", "JEV_ARCHIVE_AWAITING", "JEV_KEEP_URGENCY",
              "JEV_NOISE_MIN", "JEV_KEEP_PROTECTED", "JEV_MIN_CATEGORY_CONF"):
    original = getattr(rol, const)
    try:
        setattr(rol, const, original + 0.01)
        assert rol._threshold_signature() != sig, const
    finally:
        setattr(rol, const, original)
assert rol._threshold_signature() == sig


# ===========================================================================
# 5. Verdict cache: three-way agreement, and archive is the guarded direction
# ===========================================================================
v = tc.load("acct", path=cache_path())
assert v.verdict("t1", "100", base) is None
v.put_verdict("t1", "100", base, "keep", "Needs reply")
assert v.verdict("t1", "100", base) == {"decision": "keep", "category": "Needs reply"}
assert v.verdict("t1", "101", base) is None            # thread changed
assert v.verdict("t1", "100", "other-fp") is None      # policy/category/threshold moved
assert v.verdict("other", "100", base) is None
assert v.verdict("t1", None, base) is None
assert v.verdict("t1", "100", None) is None

# THE headline rule: a cached ARCHIVE is never served for a changed thread.
v.put_verdict("arch", "100", base, "archive")
assert v.verdict("arch", "100", base) == {"decision": "archive", "category": None}
assert v.verdict("arch", "101", base) is None
# An archive verdict also ages out faster than a keep.
assert tc.ARCHIVE_VERDICT_TTL < tc.KEEP_VERDICT_TTL
v._verdicts["arch"]["t"] = tc._now() - tc.ARCHIVE_VERDICT_TTL - 1
assert v.verdict("arch", "100", base) is None
# A garbage decision is never served, whatever it says.
for junk in ("delete", "", None, 1, True):
    v._verdicts["junk"] = {"h": "100", "k": base, "d": junk, "t": tc._now()}
    assert v.verdict("junk", "100", base) is None, junk
assert v.put_verdict("t9", "100", base, "delete") is False

# forget_thread drops derived state so an unconfirmed read is never reused.
v.put_thread("gone", "100", info("gone"))
v.put_verdict("gone", "100", base, "archive")
v.forget_thread("gone")
assert v.thread_info("gone", "100") is None
assert v.verdict("gone", "100", base) is None


# ===========================================================================
# 6. Atomic writes survive a simulated crash
# ===========================================================================
# The nightmare is a half-written file that still parses: it would claim threads
# are unchanged when we never verified them. tmp + fsync + os.replace means the
# published name always points at a complete file.
cp = cache_path()
w = tc.load("acct", path=cp)
w.put_thread("t1", "100", info())
w.save()
before = open(cp).read()

crashed = tc.load("acct", path=cp)
crashed.put_thread("t2", "200", info("t2"))
real_replace = os.replace
try:
    os.replace = lambda *a, **k: (_ for _ in ()).throw(OSError("crash mid-write"))
    assert crashed.save() is False           # reports failure, does not raise
finally:
    os.replace = real_replace

# The old file is intact and still correct, and no stray tmp file was left.
assert open(cp).read() == before
assert not os.path.exists(cp + ".tmp"), "a partial temp file must be cleaned up"
after = tc.load("acct", path=cp)
assert after.thread_info("t1", "100") == info()
assert after.thread_info("t2", "200") is None            # the lost write is simply a miss

# A crash that leaves a truncated TEMP file never corrupts the live file either.
with open(cp + ".tmp", "w") as f:
    f.write('{"version": 1, "threads": {"t1": {"h": "10')
assert tc.load("acct", path=cp).thread_info("t1", "100") == info()
os.remove(cp + ".tmp")

# An unwritable location fails quietly rather than killing the run.
blocked = tc.load("acct", path=os.path.join(TMP, "nodir\x00bad", "c.json"))
blocked.put_thread("t1", "100", info())
assert blocked.save() is False

# load() never raises, whatever it is handed.
assert tc.load("acct", path=os.path.join(TMP, "does", "not", "exist.json")) is not None
assert tc.load(None, path=cache_path()) is not None
assert tc.clear("acct", path=os.path.join(TMP, "nothing-here.json")) is True


# ===========================================================================
# 7. Wiring: a hit skips the READ, a change forces one, and nothing archives
#    on a broken cache. gws is stubbed; no network.
# ===========================================================================
reads = []


def fake_gws(_cfg, args):
    params = json.loads(args[args.index("--params") + 1])
    if "threads" in args and "get" in args:
        reads.append(("threads.get", params["id"]))
        tid = params["id"]
        return {"messages": [{"id": tid + "-m1", "snippet": "live snippet",
                              "labelIds": ["INBOX"], "payload": {"headers": [
                                  {"name": "From", "value": "Someone <a@b.com>"},
                                  {"name": "Subject", "value": "Subject"}]}}]}
    if "messages" in args and "get" in args:
        reads.append(("messages.get", params["id"]))
        return {"id": params["id"], "labelIds": ["INBOX"], "snippet": "live snippet",
                "payload": {"headers": [
                    {"name": "From", "value": "Someone <a@b.com>"},
                    {"name": "Subject", "value": "Subject"}]}}
    reads.append(("messages.list", params.get("q", "")))
    return {}


def reset_process_state():
    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()
    rol._SNIPPETS.clear()
    rol._HISTORY_IDS.clear()
    reads.clear()


orig_gws, orig_cache = rol.iz.gws, rol._CACHE
rol.iz.gws = fake_gws
try:
    wp = cache_path()

    # --- cold run: the read happens and is remembered -----------------------
    reset_process_state()
    rol._CACHE = tc.load("acct", path=wp)
    rol._HISTORY_IDS["t1"] = "100"
    cold = rol._thread_info("cfg", "t1", "owner@x.com")
    assert cold["subject"] == "Subject"
    assert reads == [("threads.get", "t1")], reads
    rol._CACHE.save()

    # --- warm run, SAME historyId: zero reads -------------------------------
    reset_process_state()
    rol._CACHE = tc.load("acct", path=wp)
    rol._HISTORY_IDS["t1"] = "100"
    warm = rol._thread_info("cfg", "t1", "owner@x.com")
    assert reads == [], reads                     # the whole point: 0 units spent
    assert warm == cold, (warm, cold)
    assert rol._CACHE.hits["thread"] == 1

    # --- warm run, CHANGED historyId: the read happens again ----------------
    reset_process_state()
    rol._CACHE = tc.load("acct", path=wp)
    rol._HISTORY_IDS["t1"] = "101"                # Gmail bumped it
    changed = rol._thread_info("cfg", "t1", "owner@x.com")
    assert reads == [("threads.get", "t1")], reads
    assert changed["id"] == "t1"

    # --- no historyId at all: never assume unchanged ------------------------
    reset_process_state()
    rol._CACHE = tc.load("acct", path=wp)
    rol._thread_info("cfg", "t1", "owner@x.com")  # _HISTORY_IDS empty
    assert reads == [("threads.get", "t1")], reads

    # --- a corrupt cache produces a normal cold run -------------------------
    reset_process_state()
    with open(wp, "w") as f:
        f.write('{"version": 1, "threads": {"t1": {"h": "100", "inf')
    rol._CACHE = tc.load("acct", path=wp)
    rol._HISTORY_IDS["t1"] = "100"
    recovered = rol._thread_info("cfg", "t1", "owner@x.com")
    assert reads == [("threads.get", "t1")], reads
    assert recovered["subject"] == "Subject"

    # --- replied_before: the persisted True is reused, the False expires ----
    reset_process_state()
    rol._CACHE = tc.load("acct", path=cache_path())
    rol._CACHE.put_replied("knows@x.com", True)
    assert rol._replied_before("cfg", "knows@x.com") is True
    assert reads == [], reads                      # 5 units saved, no call made

    reset_process_state()
    rol._CACHE.put_replied("cold@x.com", False)
    assert rol._replied_before("cfg", "cold@x.com") is False
    assert reads == [], reads
    # Age it past the short False TTL: the run MUST re-probe rather than keep
    # assuming the owner never replied (the archive-biased direction).
    reset_process_state()
    rol._CACHE._senders["cold@x.com"]["t"] = tc._now() - tc.REPLIED_FALSE_TTL - 1
    assert rol._replied_before("cfg", "cold@x.com") is False   # re-probed, still false
    assert len(reads) == 1 and reads[0][0] == "messages.list", reads

    # --- a FAILED lookup is keep-biased but is NEVER persisted --------------
    def boom_gws(_cfg, args):
        raise RuntimeError("temporary network failure")

    reset_process_state()
    rol._CACHE = tc.load("acct", path=cache_path())
    rol.iz.gws = boom_gws
    try:
        assert rol._replied_before("cfg", "flaky@x.com") is True    # keep-biased
    finally:
        rol.iz.gws = fake_gws
    # The True was a safety default, not an observation. Persisting it would
    # freeze a network blip into 30 days of fiction.
    assert rol._CACHE.replied_before("flaky@x.com") is None
finally:
    rol.iz.gws = orig_gws
    rol._CACHE = orig_cache


# ===========================================================================
# 8. Wiring: _classify reuses a verdict only when EVERYTHING matches, and a
#    policy edit invalidates it. jev.ask_many is stubbed; no network.
# ===========================================================================
asked = {"n": 0}


def stub_ask_many(items, max_workers=12, timeout=30.0):
    asked["n"] += len(items)
    return [{"awaiting_user": {"type": "noul", "noul": 0.05},
             "is_cold_outreach": {"type": "noul", "noul": 0.95},
             "is_automated": {"type": "noul", "noul": 0.9},
             "is_protected": {"type": "noul", "noul": 0.0},
             "urgency": {"type": "score", "score": 0.0, "confidence": 0.9}}
            for _ in items]


orig_ask, orig_policy, orig_cache = jev.ask_many, rol._policy_text, rol._CACHE
jev.ask_many = stub_ask_many
try:
    row = {"id": "t1", "ids": ["m1"], "last_from": "Cold <c@x.com>",
           "last_email": "c@x.com", "last_from_owner": False, "subject": "Pitch",
           "snippet": "buy my thing", "label_ids": set(), "replied_before": False}
    vp = cache_path()

    rol._HISTORY_IDS.clear()
    rol._HISTORY_IDS["t1"] = "100"
    rol._CACHE = tc.load("acct", path=vp)
    rol._policy_text = lambda: "archive cold outreach"

    # Cold: one real Jev call, and the archive verdict is remembered.
    asked["n"] = 0
    first = rol._classify([row])
    assert first["0"]["decision"] == "archive", first
    assert asked["n"] == 1
    rol._CACHE.save()

    # Warm, identical inputs: the verdict is reused, Jev is not called.
    asked["n"] = 0
    rol._CACHE = tc.load("acct", path=vp)
    again = rol._classify([row])
    assert again == first, (again, first)
    assert asked["n"] == 0, "an unchanged thread must not be re-classified"

    # CHANGED historyId: a cached ARCHIVE is never reused. Re-decide for real.
    asked["n"] = 0
    rol._HISTORY_IDS["t1"] = "101"
    rol._classify([row])
    assert asked["n"] == 1, "a changed thread must be re-decided"
    rol._HISTORY_IDS["t1"] = "100"

    # POLICY EDIT: the user rewrites keep-policy.md. If the cache kept serving
    # yesterday's verdicts their edit would silently do nothing.
    asked["n"] = 0
    rol._CACHE = tc.load("acct", path=vp)
    rol._policy_text = lambda: "keep absolutely everything, archive nothing"
    rol._classify([row])
    assert asked["n"] == 1, "a policy edit must invalidate cached verdicts"
    rol._policy_text = lambda: "archive cold outreach"

    # THRESHOLD CHANGE: same requirement for the JEV_* knobs.
    asked["n"] = 0
    rol._CACHE = tc.load("acct", path=vp)
    original = rol.JEV_ARCHIVE_AWAITING
    try:
        rol.JEV_ARCHIVE_AWAITING = original + 0.1
        rol._classify([row])
        assert asked["n"] == 1, "a threshold change must invalidate cached verdicts"
    finally:
        rol.JEV_ARCHIVE_AWAITING = original

    # CATEGORY LIST CHANGE: the categories are the choice options, so adding one
    # has to re-run the judgment or the new category is never applied.
    asked["n"] = 0
    rol._CACHE = tc.load("acct", path=vp)
    orig_cats = rol._categories
    try:
        rol._categories = lambda: list(orig_cats()) + [
            {"name": "Finance", "description": "money", "emoji": "💰"}]
        rol._classify([row])
        assert asked["n"] == 1, "a category change must invalidate cached verdicts"
    finally:
        rol._categories = orig_cats

    # LEARNED PREFERENCES CHANGE: same again.
    asked["n"] = 0
    rol._CACHE = tc.load("acct", path=vp)
    orig_learned = rol._learned_rules
    try:
        rol._learned_rules = lambda: "the owner always keeps mail from c@x.com"
        rol._classify([row])
        assert asked["n"] == 1, "new learned preferences must invalidate verdicts"
    finally:
        rol._learned_rules = orig_learned

    # replied_before flipping False->True must re-decide even though the thread
    # itself did not change: the sender stopped being a stranger.
    asked["n"] = 0
    rol._CACHE = tc.load("acct", path=vp)
    rol._classify([dict(row, replied_before=True)])
    assert asked["n"] == 1, "replied_before flipping must invalidate the verdict"

    # A corrupt verdict cache re-classifies rather than serving a stale archive.
    asked["n"] = 0
    with open(vp, "w") as f:
        f.write('{"version": 1, "verdicts": {"t1": {"h": "100", "k"')
    rol._CACHE = tc.load("acct", path=vp)
    out = rol._classify([row])
    assert asked["n"] == 1, "a corrupt cache must force a real classification"
    assert out["0"]["decision"] == "archive"       # decided live, not served stale

    # A FAILED classification is a keep-biased default, not a judgment, so it is
    # never persisted. Otherwise one bad night freezes into tomorrow's answer.
    asked["n"] = 0
    rol._CACHE = tc.load("acct", path=cache_path())
    jev.ask_many = lambda items, max_workers=12, timeout=30.0: [None] * len(items)
    failed = rol._classify([row])
    assert failed["0"] == {"decision": "keep", "category": None}, failed
    fp = tc.verdict_fingerprint(rol._jev_state(row, rol._policy_text(), rol._learned_rules()),
                                rol._jev_questions(rol._categories()),
                                rol._threshold_signature())
    assert rol._CACHE.verdict("t1", "100", fp) is None, "a failed call must not be cached"

    # With NO cache at all the classifier behaves exactly as it did before.
    jev.ask_many = stub_ask_many
    asked["n"] = 0
    rol._CACHE = None
    plain = rol._classify([row])
    assert plain["0"]["decision"] == "archive" and asked["n"] == 1

    # The deterministic owner-last archive never consults the cache or Jev.
    asked["n"] = 0
    owner_row = dict(row, last_from_owner=True)
    assert rol._classify([owner_row])["0"] == {"decision": "archive", "category": None}
    assert asked["n"] == 0
finally:
    jev.ask_many = orig_ask
    rol._policy_text = orig_policy
    rol._CACHE = orig_cache
    rol._HISTORY_IDS.clear()


# ===========================================================================
# 9. threads.list harvests the free historyId (the change-detector)
# ===========================================================================
# Verified against the live account, each entry looks like
#   {'id': '1a0b28e0e2352dbc', 'historyId': '7148783', 'snippet': '...'}
# and costs nothing beyond the enumeration the run already pays for.
def listing_gws(_cfg, _args):
    return {"threads": [{"id": "t1", "historyId": "7148783", "snippet": "one"},
                        {"id": "t2", "historyId": "7148460"},
                        {"id": "t3", "snippet": "no history id here"}]}


orig_gws = rol.iz.gws
rol.iz.gws = listing_gws
try:
    rol._HISTORY_IDS.clear()
    rol._SNIPPETS.clear()
    ids = rol._thread_ids_q("cfg", "in:inbox")
    assert ids == ["t1", "t2", "t3"], ids
    assert rol._HISTORY_IDS == {"t1": "7148783", "t2": "7148460"}, rol._HISTORY_IDS
    # t3 has no historyId, so it is simply absent -> it can never hit the cache.
    assert "t3" not in rol._HISTORY_IDS
    assert rol._SNIPPETS["t1"] == "one"
finally:
    rol.iz.gws = orig_gws
    rol._HISTORY_IDS.clear()
    rol._SNIPPETS.clear()


shutil.rmtree(TMP, ignore_errors=True)
print("thread_cache OK")
