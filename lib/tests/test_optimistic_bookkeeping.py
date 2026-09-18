#!/usr/bin/env python3
"""Checks that a failure in the POST-WRITE bookkeeping of an optimistic op is not
mistaken for a failed Gmail write. No network.

_dismiss/_undo_thread run `write_fn` in a background thread; on ANY exception the
rollback runs. But `write_fn` does two things: the Gmail call, and then
learning.record(). learning.record() touches the filesystem (it appends to
learning/signals.jsonl under an flock) and can raise on its own — a read-only
directory, a full disk, a permissions change.

When that happens the Gmail write HAS already succeeded: the thread really is out
of the inbox and carrying its recovery label. Rolling back then makes the app
assert the opposite of reality — it re-adds the row as if the mail were still in
the inbox, decrements the Undo bucket that is the user's route back to it, and
toasts "Couldn't set aside". The mail is not lost (the recovery label is still on
it), but the reversibility affordance the product promises is degraded and the
UI is actively wrong.

A missing learning signal is a lost preference hint. A bogus rollback is a lie
about where the user's mail is. The first must not cause the second.

Run: python3 lib/tests/test_optimistic_bookkeeping.py
"""
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import keeper_server as ks   # noqa: E402
import draftutil as du       # noqa: E402
import inbox_zero as iz      # noqa: E402
import learning              # noqa: E402

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        FAILS.append(f"{label}: {detail}")
        print(f"  FAIL {label}: {detail}")


def _fresh_state(path):
    state = {"accounts": [{
        "slug": "acct1", "ok": True, "inbox_threads": 1,
        "loops": [{"thread_id": "t1", "sender": "Jane", "sender_email": "jane@x.com",
                   "subject": "Hi", "snippet": "...", "epoch": 100,
                   "account_slug": "acct1"}],
        "undo_points": [],
    }], "total_loops": 1}
    with open(path, "w") as f:
        json.dump(state, f)


def _read():
    with open(ks.STATE_PATH) as f:
        return json.load(f)


def _loop_ids():
    return [l["thread_id"] for l in _read()["accounts"][0].get("loops", [])]


def _wait_for(cond, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if cond():
            return True
        time.sleep(0.02)
    return False


def main():
    saved = (ks._acct, du._gws, iz._ensure_label, iz._dated_label, learning.record,
             ks.STATE_PATH, ks._STATE_LOCK_PATH)
    gmail_calls = []

    def stub_gws(config_dir, args, allow_empty=False, _retries=3):
        gmail_calls.append(args)
        if args[:4] == ["gmail", "users", "labels", "list"]:
            return {"labels": [{"id": "LID", "name": "🗄️ Auto-Archived 2026-09-17"}]}
        return {}

    def exploding_record(event):
        raise OSError("learning/signals.jsonl is not writable")

    ks._acct = lambda slug: {"config_dir": "/tmp/fake-cfg"}
    du._gws = stub_gws
    iz._ensure_label = lambda cfg, name: "LID"
    iz._dated_label = lambda base: "🗄️ Auto-Archived 2026-09-17"
    learning.record = exploding_record

    try:
        with tempfile.TemporaryDirectory() as tmp:
            ks.STATE_PATH = os.path.join(tmp, "state.json")
            ks._STATE_LOCK_PATH = ks.STATE_PATH + ".lock"

            # --- dismiss: Gmail write succeeds, learning.record blows up ---------
            print("dismiss with a failing learning signal:")
            _fresh_state(ks.STATE_PATH)
            ks._pop_pending_notification()      # drain anything left over
            gmail_calls.clear()

            ks._dismiss({"slug": "acct1", "thread_id": "t1", "sender": "Jane",
                         "sender_email": "jane@x.com", "subject": "Hi",
                         "snippet": "...", "epoch": 100, "learn": True})

            check("the Gmail write actually ran",
                  _wait_for(lambda: any(a[:3] == ["gmail", "users", "threads"]
                                        for a in gmail_calls)),
                  f"calls={gmail_calls}")
            # Give the background thread time to reach (and survive) the record call.
            time.sleep(0.15)

            st = _read()["accounts"][0]
            check("the row stays dismissed (no bogus rollback)",
                  "t1" not in _loop_ids(), f"loops={_loop_ids()}")
            check("inbox count stays decremented",
                  st["inbox_threads"] == 0, f"inbox_threads={st['inbox_threads']}")
            check("the Undo bucket keeps its entry (the route back to the mail)",
                  any(p.get("count", 0) >= 1 for p in st.get("undo_points", [])),
                  f"undo_points={st.get('undo_points')}")
            check("no misleading 'couldn't set aside' toast",
                  ks._pop_pending_notification() is None)

            # --- undo_thread: same shape --------------------------------------
            print("\nundo_thread with a failing learning signal:")
            _fresh_state(ks.STATE_PATH)
            st0 = _read()
            st0["accounts"][0]["loops"] = []
            st0["accounts"][0]["inbox_threads"] = 0
            with open(ks.STATE_PATH, "w") as f:
                json.dump(st0, f)
            ks._pop_pending_notification()
            gmail_calls.clear()

            ks._undo_thread({"slug": "acct1", "label": "🗄️ Auto-Archived 2026-09-17",
                             "id": "m1", "thread_id": "t1", "sender": "Jane",
                             "sender_email": "jane@x.com", "subject": "Hi",
                             "snippet": "...", "epoch": 100})

            check("the Gmail restore actually ran",
                  _wait_for(lambda: any(a[:3] == ["gmail", "users", "messages"]
                                        for a in gmail_calls)),
                  f"calls={gmail_calls}")
            time.sleep(0.15)
            check("the restored row stays in Open loops",
                  "t1" in _loop_ids(), f"loops={_loop_ids()}")
            check("no misleading 'couldn't restore' toast",
                  ks._pop_pending_notification() is None)

            # --- a genuinely failed Gmail write must STILL roll back ------------
            print("\na real Gmail failure still rolls back:")
            _fresh_state(ks.STATE_PATH)
            ks._pop_pending_notification()

            def failing_gws(config_dir, args, allow_empty=False, _retries=3):
                raise RuntimeError("simulated Gmail failure")

            du._gws = failing_gws
            ks._dismiss({"slug": "acct1", "thread_id": "t1", "sender": "Jane",
                         "sender_email": "jane@x.com", "subject": "Hi",
                         "snippet": "...", "epoch": 100, "learn": True})
            check("the row comes back when Gmail really failed",
                  _wait_for(lambda: "t1" in _loop_ids()), f"loops={_loop_ids()}")
            st2 = _read()["accounts"][0]
            check("the Undo bucket bump is reverted",
                  not st2.get("undo_points"), f"undo_points={st2.get('undo_points')}")
            note = ks._pop_pending_notification()
            check("the user is told it didn't happen",
                  note is not None and "set aside" in note["body"].lower(), f"note={note}")
    finally:
        (ks._acct, du._gws, iz._ensure_label, iz._dated_label, learning.record,
         ks.STATE_PATH, ks._STATE_LOCK_PATH) = saved

    if FAILS:
        print(f"\n{len(FAILS)} FAILURE(S)")
        for f in FAILS:
            print("  - " + f)
        sys.exit(1)
    print("\noptimistic_bookkeeping OK")


if __name__ == "__main__":
    main()
