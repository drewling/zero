"""Background mailbox sync: fill the local store once, then keep it current.

THE SHAPE OF THE PROBLEM, measured on the live account (3,281 inbox threads):

    enumerate the inbox (threads.list) ............. 3.3s, 70 units
    read every thread (messages.get, 20 units) ..... quota-bound, ~14 min
    ask "what changed?" (history.list, 2 units) .... one request

The middle number is why the app felt slow: it was paid on every run, in the
foreground, while the user waited. It only ever needed to be paid ONCE. After
that, Gmail will tell us exactly what moved for two quota units.

So:

    initial()     one-time backfill. Slow, quota-bound, runs in the background,
                  resumable: progress is committed continuously, so a crash or
                  a quit costs only the batch in flight.
    incremental() the steady state. One history.list, then read only the
                  threads it names. Typically a second or two.
    sync()        picks the right one, and falls back to a full resync when the
                  cursor has expired.

WHY THE CURSOR IS ONLY ADVANCED AT THE END
------------------------------------------
The cursor means "the store reflects Gmail as of here". Advancing it before the
rows are committed would silently skip that window forever: the next sync would
ask for changes since a point we never actually processed. So it is written
last, only on success. Re-reading a window is free-ish; skipping one loses mail
from the panel.

The read cost per thread is messages.get (20 units) on the newest message, not
threads.get (40). Verified equivalent for the fields used here: the newest
message's From/Subject, plus the label set, plus the message ids. Halving the
unit cost halves the only number that still binds.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gmail_api                  # noqa: E402
import gmail_quota as gq          # noqa: E402
import mailbox_store              # noqa: E402
import run_metrics as metrics     # noqa: E402
from email.utils import parseaddr  # noqa: E402

# Commit every N threads during the initial backfill, so a 14-minute job that
# is interrupted at minute 13 keeps 13 minutes of work.
COMMIT_EVERY = 200

# Gmail caps a batch at 100 sub-requests; reading the newest message of each
# thread costs 20 units, so one batch is 2,000 units of the 4,800/min budget.
READ_WORKERS = 4


def _message_info(tid, message, message_ids, me):
    """Build a row from the thread's NEWEST MESSAGE plus its known message ids.

    This is the cheap path. `messages.get` is 20 quota units against
    `threads.get`'s 40, and since the classifier only ever looks at the newest
    message's From/Subject, the thread's label set and its message ids, the two
    carry identical information here. Quota is the only thing still binding the
    initial sync, so halving it halves that wait.

    Returns None if anything required is missing, so a partial response is
    re-read rather than stored as a half-known thread."""
    if not message:
        return None
    headers = {h["name"].lower(): h["value"]
               for h in (message.get("payload", {}) or {}).get("headers", []) or []}
    last_from = headers.get("from", "")
    last_email = (parseaddr(last_from)[1] or "").lower()
    # The newest message's labels stand in for the thread's. INBOX/UNREAD/SENT
    # live on messages, and the newest one is what the panel and the keep-bar
    # actually reason about.
    labels = set(message.get("labelIds") or [])
    me_addr = (me or "").strip().lower()
    owner = bool(last_email and me_addr and last_email == me_addr) or "SENT" in labels
    try:
        internal_ts = int(message.get("internalDate") or 0) // 1000
    except (TypeError, ValueError):
        internal_ts = 0
    history_id = message.get("historyId")
    if not history_id:
        return None
    return {"id": tid, "history_id": history_id,
            "ids": list(message_ids),
            "last_from": last_from, "last_email": last_email,
            "last_from_owner": owner,
            "subject": headers.get("subject", "(no subject)"),
            "snippet": (message.get("snippet") or "")[:160],
            "label_ids": labels, "internal_ts": internal_ts}


def _thread_info(tid, thread, me):
    """Authoritative fallback: build a row from a full thread resource.

    Used when the cheap path cannot cover a thread (no message index for it),
    so correctness never depends on the optimisation being available."""
    messages = thread.get("messages") or []
    if not messages:
        return None
    newest = messages[-1]
    headers = {h["name"].lower(): h["value"]
               for h in (newest.get("payload", {}) or {}).get("headers", []) or []}
    last_from = headers.get("from", "")
    last_email = (parseaddr(last_from)[1] or "").lower()
    labels = set()
    for message in messages:
        labels.update(message.get("labelIds") or [])
    me_addr = (me or "").strip().lower()
    owner = bool(last_email and me_addr and last_email == me_addr)
    if not owner and "SENT" in (newest.get("labelIds") or []):
        owner = True
    try:
        internal_ts = int(newest.get("internalDate") or 0) // 1000
    except (TypeError, ValueError):
        internal_ts = 0
    return {"id": thread.get("id") or tid,
            "history_id": thread.get("historyId"),
            "ids": [m["id"] for m in messages if m.get("id")],
            "last_from": last_from, "last_email": last_email,
            "last_from_owner": owner,
            "subject": headers.get("subject", "(no subject)"),
            "snippet": (newest.get("snippet") or "")[:160],
            "label_ids": labels, "internal_ts": internal_ts}


def _index_messages(config_dir, query, limiter):
    """One paged messages.list sweep: thread id -> (all message ids, newest id).

    5 units per 500 messages, so indexing a 70k-message mailbox costs a couple
    of hundred units. It is what makes the 20-unit read path possible, because
    it already knows every thread's message ids and which one is newest."""
    messages = gmail_api.list_messages(config_dir, query, limiter)
    index = {}
    for message in messages:
        tid, mid = message.get("threadId"), message.get("id")
        if not tid or not mid:
            continue
        entry = index.get(tid)
        if entry is None:
            index[tid] = ([mid], mid)
        else:
            entry[0].append(mid)
    # messages.list returns newest first, so the first id seen per thread is
    # the newest one. Verified against threads.get on live threads.
    return index


def _read_threads(config_dir, tids, me, limiter, progress=None, index=None):
    """Read metadata for these threads. Returns (infos, failed_ids, gone_ids).

    Prefers the 20-unit messages.get path for threads the index covers, and
    falls back to the 40-unit threads.get for anything it does not.

    `gone_ids` are threads Gmail answered 404 for: deleted, not failed. That
    distinction matters because a failure must hold the sync cursor back while a
    deletion must not. Verified on the live account: a history window routinely
    names threads that no longer exist, and treating those as failures pinned
    the cursor forever, so every sync re-read the same window and never
    advanced."""
    if not tids:
        return [], [], []
    infos, failed = [], []
    cheap = {}
    if index:
        cheap = {tid: index[tid][1] for tid in tids if tid in index}
    if cheap:
        by_message = {mid: tid for tid, mid in cheap.items()}
        got = gmail_api.batch_get_all(
            config_dir, "messages", list(by_message),
            {"format": "metadata", "metadataHeaders": ["From", "Subject"]},
            limiter=limiter, workers=READ_WORKERS, progress=progress)
        for mid, message in got.items():
            tid = by_message[mid]
            info = _message_info(tid, message, index[tid][0], me)
            if info:
                infos.append(info)
        resolved = {info["id"] for info in infos}
        remaining = [t for t in tids if t not in resolved]
    else:
        remaining = list(tids)

    gone = []
    if remaining:
        got = gmail_api.batch_get_all(
            config_dir, "threads", remaining,
            {"format": "metadata", "metadataHeaders": ["From", "Subject"]},
            limiter=limiter, workers=READ_WORKERS, progress=progress)
        missing = []
        for tid in remaining:
            thread = got.get(tid)
            info = _thread_info(tid, thread, me) if thread else None
            if info and info.get("history_id"):
                infos.append(info)
            else:
                missing.append(tid)
        # Separate "deleted" from "could not read". A 404 means the thread is
        # gone for good; anything else must hold the cursor back. The probes run
        # concurrently because a history window can name dozens of deleted
        # threads at once (measured: 27 of them, 74s serially).
        if missing:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=min(8, len(missing)),
                                    thread_name_prefix="gmail-404") as pool:
                verdicts = list(pool.map(
                    lambda t: (t, _is_deleted(config_dir, t, limiter)), missing))
            for tid, deleted in verdicts:
                (gone if deleted else failed).append(tid)
    return infos, failed, gone


def _is_deleted(config_dir, tid, limiter=None):
    """True when Gmail says this thread no longer exists (404)."""
    try:
        status, _raw, _ct = gmail_api._request(
            config_dir, "GET",
            f"{gmail_api.API}/users/me/threads/{tid}?format=minimal")
        return status == 404
    except gmail_api.GmailError:
        return False          # unknown, so treat it as a failure, not a deletion


def initial(config_dir, store, me, limiter=None, query="in:inbox",
            progress=None, should_stop=None):
    """One-time backfill of the whole inbox. Resumable and interruptible.

    Rows are committed in batches as they arrive, so stopping early keeps
    everything read so far. The cursor is only set if the sweep COMPLETES: a
    partial store with a current cursor would never fill its gaps.
    """
    started = time.time()
    limiter = limiter or gq.UnitLimiter()
    # Capture the cursor BEFORE reading, so anything that lands mid-sweep is
    # picked up by the next incremental sync instead of falling in the gap.
    try:
        cursor = gmail_api.get_profile(config_dir, limiter).get("historyId")
    except gmail_api.GmailError:
        cursor = None

    stubs = gmail_api.list_threads(config_dir, query, limiter)
    ids = [s["id"] for s in stubs if s.get("id")]
    known = store.get_many(ids, {s["id"]: s.get("historyId") for s in stubs
                                 if s.get("id") and s.get("historyId")})
    todo = [i for i in ids if i not in known]
    total, done, failed_total = len(todo), 0, 0

    # One messages.list sweep (5 units per 500) buys the 20-unit read path for
    # every thread it covers, instead of 40 units each. It only pays for itself
    # when there is real reading left to do.
    index = _index_messages(config_dir, query, limiter) if todo else {}

    for start in range(0, len(todo), COMMIT_EVERY):
        if should_stop and should_stop():
            # Interrupted: keep what we have, do NOT advance the cursor.
            return {"status": "interrupted", "read": done, "total": total,
                    "cached": len(known), "seconds": round(time.time() - started, 1)}
        chunk = todo[start:start + COMMIT_EVERY]
        infos, failed, gone = _read_threads(config_dir, chunk, me, limiter,
                                            index=index)
        if infos:
            store.upsert_many(infos)
        if gone:
            store.forget(gone)
        failed_total += len(failed)
        done += len(infos)
        if progress:
            progress(done, total)

    # Inbox membership is only authoritative when the enumeration completed.
    store.set_inbox_membership(ids)
    complete = failed_total == 0
    if complete and cursor:
        store.set_cursor(cursor)
    metrics.record("sync.initial", config_dir, threads=done, failures=failed_total,
                   seconds=time.time() - started)
    return {"status": "complete" if complete else "partial",
            "read": done, "total": total, "cached": len(known),
            "failed": failed_total, "inbox": len(ids),
            "seconds": round(time.time() - started, 1)}


def incremental(config_dir, store, me, limiter=None, progress=None):
    """Apply everything that changed since the stored cursor.

    Returns None if a full resync is required (no cursor, or Gmail says the
    cursor is too old). None is deliberately distinct from an empty change set:
    one means "we don't know", the other means "nothing moved"."""
    cursor = store.cursor()
    if not cursor:
        return None
    started = time.time()
    limiter = limiter or gq.UnitLimiter()
    try:
        records = gmail_api.history_since(config_dir, cursor, limiter)
    except gmail_api.GmailError:
        return None                    # transport problem: caller decides
    if records is None:
        return None                    # 404: cursor expired -> full resync

    touched, removed = set(), set()
    for record in records:
        for key in ("messagesAdded", "messagesDeleted",
                    "labelsAdded", "labelsRemoved"):
            for entry in record.get(key) or []:
                message = entry.get("message") or {}
                tid = message.get("threadId")
                if tid:
                    touched.add(tid)
        # A permanently deleted message can leave a thread that no longer exists.
        for entry in record.get("messagesDeleted") or []:
            message = entry.get("message") or {}
            if message.get("threadId"):
                removed.add(message["threadId"])

    new_cursor = None
    try:
        new_cursor = gmail_api.get_profile(config_dir, limiter).get("historyId")
    except gmail_api.GmailError:
        pass

    infos, failed, gone = [], [], []
    if touched:
        # Only index when there is enough to read for the sweep to pay for
        # itself; a handful of changed threads is cheaper read directly.
        index = None
        if len(touched) >= 20:
            try:
                index = _index_messages(config_dir, "in:inbox", limiter)
            except gmail_api.GmailError:
                index = None
        infos, failed, gone = _read_threads(config_dir, sorted(touched), me,
                                            limiter, progress, index=index)
    if infos:
        store.upsert_many(infos)
    # Threads Gmail 404s are deleted, not unread-able. Drop their rows and do
    # NOT let them hold the cursor: a permanently deleted thread never becomes
    # readable, so waiting for it would pin the cursor forever.
    if gone:
        store.forget(gone)

    # Only advance when every touched thread was actually resolved. Otherwise
    # the next sync must see this window again.
    if not failed and new_cursor:
        store.set_cursor(new_cursor)
    metrics.record("sync.incremental", config_dir, changed=len(touched),
                   applied=len(infos), failures=len(failed), deleted=len(gone),
                   seconds=time.time() - started)
    return {"status": "complete" if not failed else "partial",
            "changed": len(touched), "applied": len(infos), "deleted": len(gone),
            "failed": len(failed), "seconds": round(time.time() - started, 1)}


def sync(config_dir, account_label, me, limiter=None, progress=None,
         should_stop=None, query="in:inbox"):
    """Bring the local store up to date by whichever route is valid.

    Tries the cheap incremental path first and falls back to a full sweep when
    there is no usable cursor. Never raises: a sync failure degrades to "the
    store is stale", which callers already handle by reading Gmail."""
    store = mailbox_store.load(account_label)
    if store is None:
        return {"status": "unavailable", "reason": "local store could not be opened"}
    limiter = limiter or gq.UnitLimiter()
    try:
        result = incremental(config_dir, store, me, limiter, progress)
        if result is not None:
            result["mode"] = "incremental"
            result.update(store.counts())
            return result
        result = initial(config_dir, store, me, limiter, query,
                         progress, should_stop)
        result["mode"] = "initial"
        result.update(store.counts())
        return result
    except gmail_api.AuthUnavailable as exc:
        return {"status": "unavailable", "reason": str(exc)}
    except gmail_api.GmailError as exc:
        return {"status": "error", "reason": str(exc)}
    finally:
        store.close()


if __name__ == "__main__":
    import json
    # Live sync against a real account. READ-ONLY: it reads mail and writes the
    # local mirror; it never modifies anything in Gmail.
    # Usage: mailbox_sync.py <gws-config-dir> <account-label> [max-seconds]
    if len(sys.argv) < 3:
        print("usage: mailbox_sync.py <gws-config-dir> <account-label> [max-seconds]")
        raise SystemExit(2)
    cfg, label = sys.argv[1], sys.argv[2]
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 0
    if not gmail_api.available(cfg):
        print("direct Gmail access unavailable for this account")
        raise SystemExit(1)
    profile = gmail_api.get_profile(cfg)
    me = profile.get("emailAddress", "")
    deadline = time.time() + budget if budget else None
    last = [0.0]

    def show(done, total):
        now = time.time()
        if now - last[0] > 2:
            last[0] = now
            print(f"  ... {done}/{total} threads", flush=True)

    started = time.time()
    out = sync(cfg, label, me, progress=show,
               should_stop=(lambda: deadline and time.time() > deadline))
    out["wall_seconds"] = round(time.time() - started, 1)
    print(json.dumps(out, indent=2))
    gmail_api.close_all()
