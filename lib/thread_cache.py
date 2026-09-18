#!/usr/bin/env python3
"""Persistent per-account cache so a daily run stops re-discovering what it
already knew. A cache that can only ever SKIP WORK, never cause an archive.

WHY
---
Measured on the live account, every run re-paid for facts that had not changed
overnight:

    ~1,557 threads x threads.get/messages.get     = 31,140 units
    ~800 replied_before sender probes x 5 units   =  4,000 units
    ~1,557 Jev classifications                    = the same verdicts as yesterday

Against Gmail's 6,000 units/min/user ceiling, that spend IS the runtime. And
almost none of it was necessary: an inbox that did not move overnight has the
same senders, the same subjects, and deserves the same decisions.

THE CHANGE-DETECTOR IS FREE
---------------------------
`threads.list` costs 10 units per 100 threads and the run ALREADY pays it to
enumerate candidates. Verified on the live account, each entry it returns carries
a per-thread `historyId`:

    {'id': '1a0b28e0e2352dbc', 'historyId': '7148783'}

Gmail bumps that value whenever anything about the thread changes (a new message,
a label added or removed). So equality with the stored historyId is a sound
"this thread has NOT changed" test that costs nothing extra, and it turns the
20-40 unit per-thread read into a dictionary lookup.

This is a different mechanism from lib/sync_state.py and they compose. sync_state
asks Gmail "what changed since my cursor?" (2 units, but the cursor expires and a
crashed run correctly refuses to advance it). This asks, per thread, "is what I
stored still current?" — which stays true across cursor expiry, across full
reads, and across a run that died halfway.

THE SAFETY CONTRACT (this is someone's real mail)
-------------------------------------------------
PRODUCT.md makes reversibility the product, and the one irrecoverable mistake is
archiving something that needed the user. So the cache is built to be incapable
of causing one:

1. **A miss is always safe.** Every lookup returns None for anything not
   positively verified: missing key, historyId mismatch, expired entry, wrong
   schema version, corrupt or truncated JSON, unreadable file, wrong types. None
   means "do the real read / the real classification", which is exactly the
   behaviour of the code before this module existed.

2. **Nothing is served for a thread that changed.** Thread info, and the Jev
   verdict, are both keyed on the historyId they were derived from. A changed
   thread cannot hit; it is re-read and re-decided.

3. **The verdict key covers everything that can change the verdict.** Not just
   the thread: the keep-policy text, the category list, the learned preferences,
   the threshold constants and the question set all go into the fingerprint. If
   the user edits keep-policy.md and the tool kept serving yesterday's verdicts,
   their edit would silently do nothing — so any change to those inputs
   invalidates every cached verdict at once.

4. **`replied_before` is cached ASYMMETRICALLY**, because its two answers have
   opposite risk. "The owner HAS written to this sender" is monotone — a sent
   message never un-sends — and it biases toward KEEP, so it is cached for
   REPLIED_TRUE_TTL (30 days). "The owner has NOT written to this sender" stops
   being true the moment they reply, and it feeds the cold-outreach signal that
   biases toward ARCHIVE, so it expires after REPLIED_FALSE_TTL (6 hours). A
   stale False is the mail-loss direction; a stale True merely costs an
   unnecessary keep.

5. **Writes are atomic** (tmp + os.replace, fsync'd) so a crash mid-write cannot
   leave a truncated file that a later run misparses. A half-written cache that
   happened to read as valid JSON is the nightmare case: it would claim threads
   are unchanged when we never verified them.

6. **Bounded.** Entries older than MAX_ENTRY_AGE are dropped, and each section is
   capped at MAX_ENTRIES (newest-first) so the file cannot grow forever on an
   account that churns through thread ids.

Nothing here raises. The cache is an optimisation; a broken cache must degrade
into the slow-but-correct path, never into a failed run.
"""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE_DIR = os.path.join(ROOT, "app", "thread_cache")

# Bump when the stored shape changes. A mismatch DISCARDS the cache rather than
# trying to interpret an older layout, because misreading a field here means
# claiming a thread is unchanged when it is not.
SCHEMA_VERSION = 1

# --- Time-to-live, per kind of fact -----------------------------------------
# Thread info and verdicts are validated by historyId, so age is only a bound on
# file growth, not a correctness mechanism.
MAX_ENTRY_AGE = 30 * 24 * 3600          # 30 days

# A cached ARCHIVE verdict is the only entry whose reuse points at mail loss, so
# it gets a deliberately shorter life than a cached KEEP. Candidates come from
# `in:inbox`, so re-serving one at all means the earlier archive did not happen
# (a dry run, or a failed batchModify) — worth re-deciding sooner.
ARCHIVE_VERDICT_TTL = 7 * 24 * 3600     # 7 days
KEEP_VERDICT_TTL = MAX_ENTRY_AGE

# THE ASYMMETRY. See point 4 in the module docstring: True is monotone and
# keep-biased; False is falsified by a single reply and is archive-biased.
REPLIED_TRUE_TTL = 30 * 24 * 3600       # 30 days
REPLIED_FALSE_TTL = 6 * 3600            # 6 hours

# Hard caps per section so one runaway account cannot grow the file without end.
MAX_ENTRIES = 20000

# Exactly the keys _classify/_jev_state/_backfill_partition consume. A cached
# row missing any of them is treated as corrupt and re-read, so the cache can
# never hand the classifier partial inputs.
_INFO_KEYS = ("id", "ids", "last_from", "last_email", "last_from_owner",
              "subject", "snippet", "label_ids")


def _now():
    return int(time.time())


def _safe_name(account):
    """A filesystem-safe file stem for an account label."""
    keep = [ch if (ch.isalnum() or ch in "-_.@") else "_" for ch in str(account or "default")]
    return ("".join(keep) or "default")[:120]


def path_for(account):
    return os.path.join(CACHE_DIR, _safe_name(account) + ".json")


def _atomic_write_json(path, data):
    """tmp + fsync + os.replace. Returns True on success, never raises.

    The fsync matters as much as the replace: os.replace is atomic with respect
    to the directory entry, but without flushing the temp file first a crash can
    publish a name that points at unwritten blocks."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        return True
    except Exception:
        try:
            if os.path.exists(path + ".tmp"):
                os.remove(path + ".tmp")
        except Exception:
            pass
        return False


def _read_json(path):
    """Parsed cache file, or {} for anything we cannot fully trust.

    Truncated JSON, a wrong schema version, a non-dict body and an unreadable
    file all collapse to the same answer: no cache. That is the whole safety
    story of this function — there is no "partially usable" branch."""
    try:
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}                        # corrupt/truncated -> behave as empty
    if not isinstance(data, dict):
        return {}
    if data.get("version") != SCHEMA_VERSION:
        return {}                        # schema bump -> discard, never reinterpret
    for section in ("threads", "senders", "verdicts"):
        if not isinstance(data.get(section), dict):
            data[section] = {}
    return data


def _clean_info(raw):
    """Validate a cached info row back into the exact shape the reader produces.

    Returns None if ANYTHING is off, so a mangled row routes the thread to a real
    read instead of to the classifier with half its inputs."""
    if not isinstance(raw, dict):
        return None
    for k in _INFO_KEYS:
        if k not in raw:
            return None
    ids = raw.get("ids")
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        return None
    labels = raw.get("label_ids")
    if not isinstance(labels, (list, set)):
        return None
    info = {
        "id": raw["id"],
        "ids": list(ids),
        "last_from": raw["last_from"],
        "last_email": raw["last_email"],
        # Coerced, not trusted: last_from_owner=True is the DETERMINISTIC archive
        # path, so a non-boolean must never sneak through as truthy.
        "last_from_owner": raw["last_from_owner"] is True,
        "subject": raw["subject"],
        "snippet": raw["snippet"],
        # label_ids is a set in the live path (set-membership test in
        # _backfill_partition); JSON can only hold a list.
        "label_ids": set(labels),
    }
    for k in ("id", "last_from", "last_email", "subject", "snippet"):
        if not isinstance(info[k], str):
            return None
    if not info["id"] or not info["ids"]:
        return None
    return info


def _dump_info(info):
    """The JSON-safe form of an info row, or None if it isn't cacheable."""
    if not isinstance(info, dict):
        return None
    try:
        return {
            "id": info["id"],
            "ids": [str(i) for i in info["ids"]],
            "last_from": str(info.get("last_from", "")),
            "last_email": str(info.get("last_email", "")),
            "last_from_owner": info.get("last_from_owner") is True,
            "subject": str(info.get("subject", "")),
            "snippet": str(info.get("snippet", "")),
            "label_ids": sorted(str(x) for x in (info.get("label_ids") or [])),
        }
    except Exception:
        return None


def _stable(obj):
    """Deterministic JSON for hashing: sorted keys, sets normalised to lists.

    Values are TYPE-TAGGED. Without that, the float 0.75 and the string "0.75"
    serialise identically, so changing a threshold from a number to a string (or
    a policy field between the two) would leave the fingerprint unchanged and
    silently keep serving verdicts made under the old value. Tagging makes the
    hash distinguish them."""
    def _norm(o):
        if isinstance(o, dict):
            return {str(k): _norm(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
        if isinstance(o, (set, frozenset)):
            return sorted(_norm(v) for v in o)
        if isinstance(o, (list, tuple)):
            return [_norm(v) for v in o]
        if isinstance(o, bool):
            return ["b", o]              # before int: bool IS an int in Python
        if isinstance(o, float):
            return ["f", repr(o)]        # repr round-trips exactly; str() does not
        if isinstance(o, int):
            return ["i", o]
        if isinstance(o, str):
            return ["s", o]
        if o is None:
            return ["n", None]
        return ["o", repr(o)]
    return json.dumps(_norm(obj), ensure_ascii=False, sort_keys=True)


def verdict_fingerprint(state, questions, thresholds):
    """Hash of EVERY input that can change a Jev verdict.

    Deliberately broad. What goes in:

      state       - the per-thread state handed to Jev. That is the thread's
                    sender/subject/snippet/last_from_owner AND `replied_before`
                    AND the keep-policy text AND the learned preferences, since
                    lib/review_open_loops._jev_state packs all of them together.
                    So a policy edit, a new learned rule, or replied_before
                    flipping False->True all land here — the last one matters
                    because a sender can start being someone the owner writes to
                    without the thread's historyId moving at all.
      questions   - the typed question set, whose choice options ARE the category
                    list from categories.json. Editing categories therefore
                    invalidates verdicts, which is what the user expects when
                    they add a category and want it applied.
      thresholds  - the JEV_* constants. They are the keep/archive rule itself;
                    tuning one and having yesterday's verdicts served would make
                    the tuning silently inert.

    Erring wide is nearly free (a miss costs one Jev call) while erring narrow
    means a stale verdict, so anything plausibly relevant belongs in here."""
    h = hashlib.sha256()
    h.update(_stable(state).encode("utf-8"))
    h.update(b"\x00")
    h.update(_stable(questions).encode("utf-8"))
    h.update(b"\x00")
    h.update(_stable(thresholds).encode("utf-8"))
    return h.hexdigest()[:32]


class ThreadCache:
    """Per-account store of thread info, sender reply-history, and Jev verdicts.

    Every getter answers None ("not known, go find out") rather than guessing,
    and `enabled=False` turns the whole object into a correct no-op so callers
    need no branches."""

    def __init__(self, account, data=None, enabled=True, path=None):
        self.account = account
        self.enabled = bool(enabled)
        self.path = path or path_for(account)
        data = data if isinstance(data, dict) else {}
        self._threads = data.get("threads") or {}
        self._senders = data.get("senders") or {}
        self._verdicts = data.get("verdicts") or {}
        self._dirty = False
        self.hits = {"thread": 0, "replied": 0, "verdict": 0}
        self.misses = {"thread": 0, "replied": 0, "verdict": 0}

    # --- thread metadata ---------------------------------------------------
    def thread_info(self, tid, history_id):
        """Cached classifier inputs for `tid`, ONLY if its historyId still matches.

        `history_id` comes free from threads.list. When it is missing (an older
        page shape, a thread the enumeration didn't report), we have no proof the
        thread is unchanged, so this returns None and the caller pays for a real
        read. Re-reading is cheap; serving unverified state is not."""
        if not self.enabled or not tid or not history_id:
            self.misses["thread"] += 1
            return None
        rec = self._threads.get(tid)
        if not isinstance(rec, dict) or str(rec.get("h") or "") != str(history_id):
            self.misses["thread"] += 1
            return None
        if _now() - int(rec.get("t") or 0) > MAX_ENTRY_AGE:
            self.misses["thread"] += 1
            return None
        info = _clean_info(rec.get("info"))
        if info is None:
            self.misses["thread"] += 1
            return None
        self.hits["thread"] += 1
        return info

    def put_thread(self, tid, history_id, info):
        """Remember a freshly-read thread against the historyId it was read at."""
        if not self.enabled or not tid or not history_id:
            return False
        row = _dump_info(info)
        if row is None:
            return False
        self._threads[tid] = {"h": str(history_id), "t": _now(), "info": row}
        self._dirty = True
        return True

    # --- replied_before ----------------------------------------------------
    def replied_before(self, email):
        """Cached reply-history for a sender, or None when it must be re-probed.

        The TTL depends on the ANSWER, not on the entry: see REPLIED_TRUE_TTL /
        REPLIED_FALSE_TTL and point 4 of the module docstring. A False that has
        aged past its short window is treated as unknown, so the run re-probes
        rather than assuming the owner still hasn't replied."""
        if not self.enabled:
            return None
        email = (email or "").lower()
        if not email:
            return None
        rec = self._senders.get(email)
        if not isinstance(rec, dict) or not isinstance(rec.get("v"), bool):
            self.misses["replied"] += 1
            return None
        age = _now() - int(rec.get("t") or 0)
        ttl = REPLIED_TRUE_TTL if rec["v"] else REPLIED_FALSE_TTL
        if age > ttl:
            self.misses["replied"] += 1
            return None
        self.hits["replied"] += 1
        return rec["v"]

    def put_replied(self, email, value):
        if not self.enabled:
            return False
        email = (email or "").lower()
        if not email or not isinstance(value, bool):
            return False
        prev = self._senders.get(email)
        if isinstance(prev, dict) and prev.get("v") == value and \
                _now() - int(prev.get("t") or 0) < 60:
            return True                  # unchanged and fresh; skip the churn
        self._senders[email] = {"v": value, "t": _now()}
        self._dirty = True
        return True

    # --- Jev verdicts ------------------------------------------------------
    def verdict(self, tid, history_id, fingerprint):
        """A cached {"decision", "category"} pair, or None.

        Three independent things must all agree before a verdict is reused: the
        thread id, the historyId it was decided at, and the fingerprint of every
        other input that could change the answer. An archive verdict additionally
        has to be recent (ARCHIVE_VERDICT_TTL)."""
        if not self.enabled or not tid or not history_id or not fingerprint:
            self.misses["verdict"] += 1
            return None
        rec = self._verdicts.get(tid)
        if not isinstance(rec, dict):
            self.misses["verdict"] += 1
            return None
        if str(rec.get("h") or "") != str(history_id) or rec.get("k") != fingerprint:
            self.misses["verdict"] += 1
            return None
        decision = rec.get("d")
        if decision not in ("keep", "archive"):
            self.misses["verdict"] += 1
            return None
        ttl = ARCHIVE_VERDICT_TTL if decision == "archive" else KEEP_VERDICT_TTL
        if _now() - int(rec.get("t") or 0) > ttl:
            self.misses["verdict"] += 1
            return None
        category = rec.get("c")
        if category is not None and not isinstance(category, str):
            category = None
        self.hits["verdict"] += 1
        return {"decision": decision, "category": category}

    def put_verdict(self, tid, history_id, fingerprint, decision, category=None):
        if not self.enabled or not tid or not history_id or not fingerprint:
            return False
        if decision not in ("keep", "archive"):
            return False
        self._verdicts[tid] = {"h": str(history_id), "k": fingerprint,
                               "d": decision,
                               "c": category if isinstance(category, str) else None,
                               "t": _now()}
        self._dirty = True
        return True

    def forget_thread(self, tid):
        """Drop everything derived from one thread. Used when a read fails, so a
        later run can never reuse state we could not confirm."""
        for section in (self._threads, self._verdicts):
            if tid in section:
                del section[tid]
                self._dirty = True

    # --- persistence -------------------------------------------------------
    def _prune(self):
        """Drop aged-out entries and cap each section. Newest entries win."""
        now = _now()
        for name, section in (("threads", self._threads),
                              ("senders", self._senders),
                              ("verdicts", self._verdicts)):
            stale = [k for k, v in section.items()
                     if not isinstance(v, dict) or now - int(v.get("t") or 0) > MAX_ENTRY_AGE]
            for k in stale:
                del section[k]
            if len(section) > MAX_ENTRIES:
                ordered = sorted(section.items(), key=lambda kv: int(kv[1].get("t") or 0),
                                 reverse=True)
                keep = dict(ordered[:MAX_ENTRIES])
                section.clear()
                section.update(keep)

    def save(self, force=False):
        """Persist atomically. Returns True on write, False on skip or failure."""
        if not self.enabled or (not self._dirty and not force):
            return False
        try:
            self._prune()
            body = {"version": SCHEMA_VERSION, "account": self.account,
                    "updated_at": _now(), "threads": self._threads,
                    "senders": self._senders, "verdicts": self._verdicts}
        except Exception:
            return False
        ok = _atomic_write_json(self.path, body)
        if ok:
            self._dirty = False
        return ok

    def stats(self):
        return {"enabled": self.enabled,
                "threads": len(self._threads), "senders": len(self._senders),
                "verdicts": len(self._verdicts),
                "hits": dict(self.hits), "misses": dict(self.misses)}


def load(account, enabled=True, path=None):
    """Open an account's cache. NEVER raises, NEVER returns None.

    A missing, corrupt, truncated or version-mismatched file yields an empty
    cache, which simply misses on everything and makes the run behave exactly as
    it did before this module existed."""
    try:
        p = path or path_for(account)
        data = _read_json(p) if enabled else {}
    except Exception:
        p, data = (path or path_for(account)), {}
    return ThreadCache(account, data=data, enabled=enabled, path=p)


def clear(account, path=None):
    """Forget an account's cache entirely (forces a full cold run)."""
    try:
        p = path or path_for(account)
        if os.path.exists(p):
            os.remove(p)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import tempfile

    d = tempfile.mkdtemp()
    p = os.path.join(d, "demo.json")
    c = load("demo", path=p)
    info = {"id": "t1", "ids": ["m1"], "last_from": "A <a@b.com>",
            "last_email": "a@b.com", "last_from_owner": False, "subject": "s",
            "snippet": "x", "label_ids": {"INBOX"}}
    assert c.thread_info("t1", "100") is None          # cold -> real read
    c.put_thread("t1", "100", info)
    assert c.thread_info("t1", "100") == info          # hit, same shape
    assert c.thread_info("t1", "101") is None          # changed -> re-read
    assert c.save() is True and os.path.exists(p)
    assert load("demo", path=p).thread_info("t1", "100") == info

    # Corrupt file reads as "no cache", never as "nothing changed".
    open(p, "w").write('{"version": 1, "threads": {"t1"')
    assert load("demo", path=p).thread_info("t1", "100") is None
    print("thread_cache self-check OK")
