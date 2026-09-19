#!/usr/bin/env python3
"""An incremental sync must not re-download mail that just left the inbox.

The keeper run archives thousands of threads at once. Every one of those shows
up in Gmail's history as a labelsRemoved record, so the next sync treated them
all as "changed" and re-read them at 20 units each. Measured on the live
account: right after archiving 2,547 threads, the sync started a 2,045-thread,
~13 minute download to learn something the run had just done on purpose.

The inbox index the sync already builds is keyed by thread id over an in:inbox
sweep, so membership answers "is this still in the inbox" for free. Threads that
are not are dropped from the mirror, which is the correct end state for a mirror
whose job is to describe the inbox.

The safety rule: absence may only be concluded from an index we actually have.
Without one we cannot distinguish "gone" from "unknown", so we must still read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mailbox_sync  # noqa: E402


class FakeStore:
    def __init__(self):
        self.forgotten = []
        self.upserted = []
        self._cursor = "100"

    def cursor(self):
        return self._cursor

    def set_cursor(self, c):
        self._cursor = c

    def upsert_many(self, infos):
        self.upserted.extend(infos)

    def forget(self, ids):
        self.forgotten.extend(ids)


def run_sync(history_tids, index, read_calls):
    """Drive incremental() with a fake Gmail and capture what it reads."""
    store = FakeStore()

    records = [{"labelsRemoved": [{"message": {"threadId": t}}]}
               for t in history_tids]

    class FakeAPI:
        GmailError = mailbox_sync.gmail_api.GmailError

        @staticmethod
        def history_since(cfg, cursor, limiter):
            return records

        @staticmethod
        def get_profile(cfg, limiter):
            return {"historyId": "200"}

    real_api = mailbox_sync.gmail_api
    real_index = mailbox_sync._index_messages
    real_read = mailbox_sync._read_threads
    mailbox_sync.gmail_api = FakeAPI
    mailbox_sync._index_messages = lambda cfg, q, lim: index

    def fake_read(cfg, tids, me, limiter, progress, index=None):
        read_calls.extend(tids)
        return ([{"id": t} for t in tids], [], [])

    mailbox_sync._read_threads = fake_read
    try:
        result = mailbox_sync.incremental("cfg", store, "me@x.com")
    finally:
        mailbox_sync.gmail_api = real_api
        mailbox_sync._index_messages = real_index
        mailbox_sync._read_threads = real_read
    return store, result


def test_departed_threads_are_not_re_read():
    """The regression: archived threads must not be downloaded again."""
    touched = [f"t{i}" for i in range(30)]
    still_in_inbox = {"t0": (["m"], "m"), "t1": (["m"], "m")}
    reads = []
    store, result = run_sync(touched, still_in_inbox, reads)

    assert sorted(reads) == ["t0", "t1"], \
        f"only threads still in the inbox may be read, got {sorted(reads)}"
    assert len(store.forgotten) == 28, \
        "threads that left the inbox are dropped from the mirror"
    assert result["left_inbox"] == 28


def test_no_index_means_everything_is_still_read():
    """Without an index we cannot prove absence, so we must not assume it."""
    touched = [f"t{i}" for i in range(30)]
    reads = []
    store, _ = run_sync(touched, None, reads)
    assert len(reads) == 30, "absence may only be concluded from a real index"
    assert store.forgotten == [], "nothing may be dropped on a guess"


def test_small_change_sets_skip_the_index_and_read_normally():
    """Under the index threshold the sync reads directly; must still work."""
    touched = ["a", "b", "c"]
    reads = []
    store, _ = run_sync(touched, {"a": (["m"], "m")}, reads)
    assert sorted(reads) == ["a", "b", "c"], \
        "with too few changes to index, every thread is read as before"
    assert store.forgotten == []


def test_all_departed_reads_nothing():
    touched = [f"t{i}" for i in range(25)]
    reads = []
    store, result = run_sync(touched, {"unrelated": (["m"], "m")}, reads)
    assert reads == [], "a pure archive sweep costs no re-reads at all"
    assert result["left_inbox"] == 25


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    print("sync departure: all tests passed")
