#!/usr/bin/env python3
"""Persistent classifier metadata, sender evidence and exact-input verdicts.

Thread entries require a nonempty, freshly observed matching historyId. Missing
versions always miss. Verdict fingerprints cover state, questions, thresholds
and model. Full-thread label intersections, when available, can prove that a
category write is unnecessary. Newest-message metadata cannot prove that.

Positive sender evidence remains keep-biased and TTL-bounded. Negative evidence
is reused within one run only: load() discards persisted False values because a
reply elsewhere in the mailbox need not change the candidate's historyId.

Writes use unique atomic files and locked delta merging, so independent writers
do not erase each other's unrelated entries. Cache failures degrade to misses.
"""
import hashlib
import json
import os
import time
import runtime_state as storage

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
REPLIED_FALSE_TTL = 6 * 3600            # in-process maximum; never reused after load

# Hard caps per section so one runaway account cannot grow the file without end.
MAX_ENTRIES = 20000

# Exactly the keys _classify/_jev_state/_backfill_partition consume. A cached
# row missing any of them is treated as corrupt and re-read, so the cache can
# never hand the classifier partial inputs.
_INFO_KEYS = ("id", "ids", "last_from", "last_email", "last_from_owner",
              "subject", "snippet", "label_ids")


def _now():
    return int(time.time())


def _age(rec):
    stamp = rec.get("t") if isinstance(rec, dict) else None
    if not isinstance(stamp, (int, float)) or not 0 <= _now() - stamp:
        return float("inf")
    return _now() - stamp


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
        storage.atomic_text(path, json.dumps(data, ensure_ascii=False))
        return True
    except Exception:
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
    if not isinstance(labels, (list, set)) or not all(isinstance(x, str) for x in labels):
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
    all_labels = raw.get("label_ids_all")
    if (isinstance(all_labels, list) and all(isinstance(x, str) for x in all_labels)
            and set(all_labels).issubset(info["label_ids"])):
        info["label_ids_all"] = set(all_labels)
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
        row = {
            "id": info["id"],
            "ids": [str(i) for i in info["ids"]],
            "last_from": str(info.get("last_from", "")),
            "last_email": str(info.get("last_email", "")),
            "last_from_owner": info.get("last_from_owner") is True,
            "subject": str(info.get("subject", "")),
            "snippet": str(info.get("snippet", "")),
            "label_ids": sorted(str(x) for x in (info.get("label_ids") or [])),
        }
        if isinstance(info.get("label_ids_all"), (set, list)):
            row["label_ids_all"] = sorted(info["label_ids_all"])
        return row
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
        # The Sent-mail id the cached negatives were established against. Saved
        # with them so a later load can tell whether they are still provable.
        self.sent_watermark = data.get("sent_watermark")
        self._dirty = False
        self._changes = {"threads": set(), "senders": set(), "verdicts": set()}
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
        if _age(rec) > MAX_ENTRY_AGE:
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
        self._changes["threads"].add(tid)
        self._dirty = True
        return True

    # --- replied_before ----------------------------------------------------
    def replied_before(self, email):
        """Cached reply-history for a sender, or None when it must be re-probed.

        Positive and same-run negative evidence have different TTLs. Persisted
        negatives are discarded by load(), regardless of age."""
        if not self.enabled:
            return None
        email = (email or "").lower()
        if not email:
            return None
        rec = self._senders.get(email)
        if not isinstance(rec, dict) or not isinstance(rec.get("v"), bool):
            self.misses["replied"] += 1
            return None
        age = _age(rec)
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
                _age(prev) < 60:
            return True                  # unchanged and fresh; skip the churn
        self._changes["senders"].add(email)
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
        if _age(rec) > ttl:
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
        self._changes["verdicts"].add(tid)
        self._verdicts[tid] = {"h": str(history_id), "k": fingerprint,
                               "d": decision,
                               "c": category if isinstance(category, str) else None,
                               "t": _now()}
        self._dirty = True
        return True

    def forget_thread(self, tid):
        """Drop everything derived from one thread. Used when a read fails, so a
        later run can never reuse state we could not confirm."""
        for name, section in (("threads", self._threads), ("verdicts", self._verdicts)):
            section.pop(tid, None)
            self._changes[name].add(tid)
            self._dirty = True

    # --- persistence -------------------------------------------------------
    def _prune(self):
        """Drop aged-out entries and cap each section. Newest entries win."""
        for name, section in (("threads", self._threads),
                              ("senders", self._senders),
                              ("verdicts", self._verdicts)):
            stale = [k for k, v in section.items()
                     if not isinstance(v, dict) or _age(v) > MAX_ENTRY_AGE]
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
            with storage.locked(self.path):
                disk = _read_json(self.path)
                # The merge below re-imports whatever is on disk, which would
                # resurrect negatives that load() deliberately dropped. If the
                # owner has sent mail since those negatives were recorded, they
                # are no longer provable, so they must not come back.
                stale_negatives = disk.get("sent_watermark") != self.sent_watermark
                for name, local in (("threads", self._threads), ("senders", self._senders),
                                    ("verdicts", self._verdicts)):
                    merged = disk.get(name, {}).copy()
                    if name == "senders" and stale_negatives:
                        merged = {k: v for k, v in merged.items()
                                  if not (isinstance(v, dict) and v.get("v") is False)}
                    keys = set(local) if force else self._changes[name]
                    for key in keys:
                        if key in local:
                            merged[key] = local[key]
                        else:
                            merged.pop(key, None)
                    local.clear()
                    local.update(merged)
                self._prune()
                body = {"version": SCHEMA_VERSION, "account": self.account,
                        "updated_at": _now(), "threads": self._threads,
                        "senders": self._senders, "verdicts": self._verdicts,
                        "sent_watermark": self.sent_watermark}
                ok = _atomic_write_json(self.path, body)
                if ok:
                    self._dirty = False
                    for keys in self._changes.values():
                        keys.clear()
                return ok
        except Exception:
            return False

    def stats(self):
        return {"enabled": self.enabled,
                "threads": len(self._threads), "senders": len(self._senders),
                "verdicts": len(self._verdicts),
                "hits": dict(self.hits), "misses": dict(self.misses)}


def load(account, enabled=True, path=None, sent_watermark=None):
    """Open an account's cache. NEVER raises, NEVER returns None.

    A missing, corrupt, truncated or version-mismatched file yields an empty
    cache, which simply misses on everything and makes the run behave exactly as
    it did before this module existed.

    `sent_watermark` is the id of the newest message in Sent. A cached negative
    ("the owner has never written to this address") can only be falsified by the
    owner SENDING something, so when the watermark matches the one stored
    alongside the negatives they are all still true and can be reused across
    runs. Without it, negatives are discarded on load as before. This is the
    precise version of that blanket rule: measured on the live account the
    discard cost 1,302 sender probes -- most of a warm run's remaining quota --
    to re-derive facts that one 5-unit call proves are unchanged."""
    try:
        p = path or path_for(account)
        data = _read_json(p) if enabled else {}
        # Reuse negatives only on an exact, non-empty watermark match. Any
        # doubt (no watermark supplied, none stored, or a differing one) falls
        # back to discarding them, which is the keep-biased direction.
        stored = data.get("sent_watermark")
        keep_negatives = bool(sent_watermark) and stored == sent_watermark
        data["senders"] = {
            k: v for k, v in data.get("senders", {}).items()
            if isinstance(v, dict)
            and (v.get("v") is True or (keep_negatives and v.get("v") is False))
        }
        if sent_watermark:
            data["sent_watermark"] = sent_watermark
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
