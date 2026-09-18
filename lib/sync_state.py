#!/usr/bin/env python3
"""Incremental sync: read only what CHANGED since the last successful run.

WHY
---
Even after making the per-thread read cheap, a full pass still re-reads an inbox
that mostly did not move overnight. `history.list` costs 2 units and returns
exactly what changed since a stored `historyId`, so a second run costs seconds
instead of minutes. This is the difference between "fast because we optimised the
constant factor" and "fast because we stopped doing the work".

THE CONTRACT (all four matter more than the speed)
--------------------------------------------------
1. The cursor advances ONLY after a run completes successfully. `load()` reads a
   cursor; `save()` is called at the very end of main(). A crashed or partial run
   leaves the old cursor, so the next run re-reads that ground rather than
   skipping it. Re-reading is cheap; skipping loses mail.

2. Gmail expires old history (measured on the live account: `startHistoryId=1`
   returns "Requested entity was not found."). `changed_threads` reports
   "expired" and the caller does a FULL read. Never a failure, never a partial.

3. Uncertainty resolves to a full read, not to an empty delta. Every error path
   returns None for the changed-set, which callers must treat as "read
   everything". An empty set means "genuinely nothing changed" and is only ever
   returned when the API said so cleanly.

4. Because PRODUCT.md makes reversibility the product: a thread skipped by the
   delta is simply not looked at this run, so it keeps whatever state it already
   has. A missed delta can therefore leave a thread in the inbox (safe — caught
   next run); it can never cause an archive, because archiving only happens to
   threads we affirmatively read and classified this run.

The cursor is captured BEFORE the run's reads (from getProfile, 1 unit) and
persisted after success, so changes landing mid-run are re-examined next time
rather than falling into the gap between reading and saving.
"""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_PATH = os.path.join(ROOT, "app", "sync_state.json")

# Gmail keeps roughly a week of history. Past that a stored cursor is likely
# dead, so we pre-emptively do a full read rather than lean on the 404.
MAX_CURSOR_AGE_SECONDS = 5 * 24 * 3600

# History record types that can change what the classifier would decide. Label
# changes matter (something left or entered the inbox). We do not filter finely:
# over-including only costs a cheap re-read, while under-including risks missing
# a real change.
_HISTORY_TYPES = ("messagesAdded", "messagesDeleted",
                  "labelsAdded", "labelsRemoved")


def _read_state():
    try:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH) as f:
                d = json.load(f)
            return d if isinstance(d, dict) else {}
    except Exception:
        pass
    return {}


def load(account):
    """The stored cursor for an account, or None when there isn't a usable one.

    Returns None (meaning "do a full read") for a missing, malformed, or stale
    cursor. The account key keeps multi-account runs independent, so one
    account's failure never disturbs another's cursor."""
    rec = _read_state().get(account) or {}
    hid = rec.get("history_id")
    if not hid:
        return None
    ts = rec.get("updated_at") or 0
    if ts and (time.time() - ts) > MAX_CURSOR_AGE_SECONDS:
        return None                      # too old to trust; full read
    return str(hid)


def save(account, history_id, meta=None):
    """Persist the cursor after a SUCCESSFUL run. Never raises.

    Written atomically (tmp + os.replace) so a crash mid-write cannot leave a
    truncated cursor file that would later be misread."""
    if not history_id:
        return False
    try:
        state = _read_state()
        rec = {"history_id": str(history_id), "updated_at": int(time.time())}
        if meta:
            rec.update(meta)
        state[account] = rec
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        tmp = STATE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STATE_PATH)
        return True
    except Exception:
        return False                     # cursor is an optimisation, never fatal


def clear(account):
    """Forget an account's cursor, forcing a full read next time."""
    try:
        state = _read_state()
        if account in state:
            del state[account]
            os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
            tmp = STATE_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            os.replace(tmp, STATE_PATH)
    except Exception:
        pass


def is_expired_error(exc):
    """Whether a history.list failure means the cursor is too old to use.

    Measured against the live API: an ancient startHistoryId returns
    "Requested entity was not found." (404). Treated as "do a full read"."""
    t = str(exc).lower()
    return ("not found" in t or "404" in t or "failedprecondition" in t
            or "start history id" in t or "starthistoryid" in t)


def changed_threads(list_history, start_history_id):
    """Thread ids that changed since the cursor.

    `list_history(page_token)` must return one raw history.list page; injecting
    it keeps this module free of transport concerns and trivially testable.

    Returns (thread_ids, status) where status is:
      "ok"       -> thread_ids is COMPLETE and authoritative (may be empty)
      "expired"  -> cursor unusable; caller MUST do a full read
      "error"    -> anything else went wrong; caller MUST do a full read
    thread_ids is None whenever the caller must fall back, so an error can never
    be mistaken for "nothing changed"."""
    if not start_history_id:
        return None, "error"
    tids, token, pages = set(), None, 0
    while True:
        try:
            page = list_history(token)
        except Exception as exc:
            return (None, "expired") if is_expired_error(exc) else (None, "error")
        if not isinstance(page, dict):
            return None, "error"
        for rec in page.get("history", []) or []:
            for key in _HISTORY_TYPES:
                for item in rec.get(key, []) or []:
                    msg = item.get("message") or item
                    tid = msg.get("threadId")
                    if tid:
                        tids.add(tid)
            # Some records carry a bare `messages` list alongside the typed keys.
            for msg in rec.get("messages", []) or []:
                if msg.get("threadId"):
                    tids.add(msg["threadId"])
        token = page.get("nextPageToken")
        pages += 1
        if not token:
            return tids, "ok"
        if pages > 200:
            # Pathological history depth: a full read is cheaper and safer than
            # paging forever, and is always a correct answer.
            return None, "error"


if __name__ == "__main__":
    pages = [{"history": [{"id": "1", "messagesAdded": [
                  {"message": {"id": "m1", "threadId": "t1"}}]},
              {"id": "2", "labelsRemoved": [
                  {"message": {"id": "m2", "threadId": "t2"}}]}],
              "nextPageToken": "p2"},
             {"history": [{"id": "3", "messages": [{"id": "m3", "threadId": "t3"}]}]}]
    seq = iter(pages)
    got, status = changed_threads(lambda _t: next(seq), "100")
    assert status == "ok" and got == {"t1", "t2", "t3"}, (status, got)

    def boom(_t):
        raise RuntimeError("Requested entity was not found.")
    assert changed_threads(boom, "100") == (None, "expired")

    def other(_t):
        raise RuntimeError("connection reset by peer")
    assert changed_threads(other, "100") == (None, "error")

    assert changed_threads(lambda _t: {"history": []}, "100") == (set(), "ok")
    assert changed_threads(lambda _t: {}, None) == (None, "error")
    print("sync_state self-check OK")
