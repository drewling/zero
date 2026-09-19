#!/usr/bin/env python3
"""The sync cursor must only ever move forward, and syncs must not overlap.

TWO BUGS THIS PINS
------------------
1. CURSOR REWIND. A full sweep captures its cursor BEFORE it starts reading,
   which is right in isolation: anything landing mid-sweep should be picked up
   next time. But if an incremental sync finishes while the sweep is running,
   the sweep's older id is written afterwards and the newer position is lost.
   Observed live: incremental set 7167910, a sweep wrote back 7158487, and the
   next sync faced a 9,354-record window it could never clear. The mirror sat
   at the same cursor while the panel showed a download restarting forever.

2. OVERLAPPING SYNCS. _sync_lock only guarded the results dict, so the
   background interval loop and a manual POST /api/sync could sweep the same
   account simultaneously, split its quota and reset each other's progress
   count. That is what "the download keeps going back to the beginning" was.
"""
import os
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mailbox_store  # noqa: E402


def store():
    d = tempfile.mkdtemp(prefix="cursor_test_")
    return mailbox_store.MailboxStore("t", path=os.path.join(d, "s.sqlite3"))


def test_cursor_advances():
    s = store()
    s.set_cursor("100")
    s.set_cursor("200")
    assert s.cursor() == "200"
    s.close()


def test_cursor_never_rewinds():
    """The exact live failure: a slow full sweep writing a stale id."""
    s = store()
    s.set_cursor("7167910")           # incremental finished first
    s.set_cursor("7158487")           # slow sweep writes its older captured id
    assert s.cursor() == "7167910", \
        "a stale writer must not drag the cursor backwards"
    s.close()


def test_equal_cursor_is_accepted():
    """Re-writing the same position is harmless and refreshes synced_at."""
    s = store()
    s.set_cursor("500")
    before = s.synced_at()
    s.set_cursor("500")
    assert s.cursor() == "500"
    assert s.synced_at() >= before
    s.close()


def test_first_cursor_is_always_stored():
    s = store()
    s.set_cursor("42")
    assert s.cursor() == "42"
    s.close()


def test_empty_cursor_is_ignored():
    s = store()
    s.set_cursor("100")
    s.set_cursor(None)
    s.set_cursor("")
    assert s.cursor() == "100"
    s.close()


def test_non_numeric_cursor_is_stored_not_dropped():
    """Gmail ids are numeric today; if that ever changes, do not silently
    discard the write and freeze the cursor forever."""
    s = store()
    s.set_cursor("100")
    s.set_cursor("abc")
    assert s.cursor() == "abc"
    s.close()


def test_only_one_sync_runs_at_a_time():
    import keeper_server as ks

    started = threading.Event()
    release = threading.Event()
    outcomes = []

    def slow(payload, mailbox_sync, gmail_api):
        started.set()
        release.wait(5)
        return {"status": "complete"}

    real = ks._sync_accounts_locked
    ks._sync_accounts_locked = slow
    try:
        t = threading.Thread(target=lambda: outcomes.append(ks._sync_accounts()))
        t.start()
        assert started.wait(5), "first sync did not start"
        # Second caller arrives while the first is still running.
        second = ks._sync_accounts()
        assert second.get("status") == "busy", \
            f"a concurrent sync must be refused, got {second}"
        release.set()
        t.join(5)
        assert outcomes and outcomes[0]["status"] == "complete"
        # And the lock is released, so a later sync is allowed again.
        assert ks._sync_accounts().get("status") == "complete"
    finally:
        ks._sync_accounts_locked = real
        release.set()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    print("sync cursor and mutex: all tests passed")
