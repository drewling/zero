#!/usr/bin/env python3
"""Fail-closed mailbox history cursors with locked per-account persistence.

Expired, malformed or partially failed history scans return None, never an
empty delta. Cursor expiry falls back to full reads. review_open_loops currently
uses these for diagnostics, not to bypass exact decision-input validation:
mailbox history alone cannot detect policy, model or learned-preference edits.
"""
import json
import os
import time
import runtime_state as storage

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
    rec = _read_state().get(account)
    if not isinstance(rec, dict):
        return None
    hid, ts = rec.get("history_id"), rec.get("updated_at")
    if (not isinstance(hid, str) or not hid.isdigit()
            or not isinstance(ts, (int, float))
            or not 0 <= time.time() - ts <= MAX_CURSOR_AGE_SECONDS):
        return None
    return hid


def save(account, history_id, meta=None):
    """Persist the cursor after a SUCCESSFUL run. Never raises.

    Written atomically (tmp + os.replace) so a crash mid-write cannot leave a
    truncated cursor file that would later be misread."""
    if not history_id:
        return False
    try:
        rec = {"history_id": str(history_id), "updated_at": int(time.time())}
        if meta:
            rec.update(meta)
        storage.update_json(STATE_PATH, lambda state: state.update({account: rec}))
        return True
    except Exception:
        return False                     # cursor is an optimisation, never fatal


def clear(account):
    """Forget an account's cursor, forcing a full read next time."""
    try:
        storage.update_json(STATE_PATH, lambda state: state.pop(account, None))
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
        if not isinstance(page, dict) or page.get("error"):
            return None, "error"
        try:
            records = page.get("history", [])
            if not isinstance(records, list):
                return None, "error"
            for rec in records:
                for key in _HISTORY_TYPES:
                    for item in rec.get(key, []) or []:
                        msg = item.get("message") or item
                        tid = msg.get("threadId")
                        if tid:
                            if not isinstance(tid, str):
                                return None, "error"
                            tids.add(tid)
                for msg in rec.get("messages", []) or []:
                    if msg.get("threadId"):
                        if not isinstance(msg["threadId"], str):
                            return None, "error"
                        tids.add(msg["threadId"])
            next_token = page.get("nextPageToken")
            if next_token and (not isinstance(next_token, str) or next_token == token):
                return None, "error"
            token = next_token
        except (AttributeError, TypeError, ValueError):
            return None, "error"
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
