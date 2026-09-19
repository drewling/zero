#!/usr/bin/env python3
"""A thread can only be archived if we remove INBOX from EVERY message that has it.

THE BUG THIS PINS
-----------------
The bulk index is built from a windowed scan (recent mail plus a margin), which
is fine for classification: a missing two-year-old message does not change who
the newest sender is. But the ids from that scan were also used as the archive
set, and a thread's INBOX-bearing messages can be older than the window.

Measured on the live account: a 9-message thread where the 6 in-window messages
were archived on every single run while the 2 messages still carrying INBOX sat
outside the window. batchModify reported success every time, the run counted 6
archives every time, and the inbox never moved. It was a permanent no-op loop
that looked like progress.

The fix is an UNWINDOWED in:inbox scan, whose per-thread ids are complete by
construction, unioned into the archive set.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mailbox_index  # noqa: E402


def test_inbox_ids_are_exposed_separately():
    idx = mailbox_index.MailboxIndex(
        order={"t": ["new2", "new1"]}, sent_ids=set(), pages=1,
        inbox_order={"t": ["new2", "OLD_OUTSIDE_WINDOW"]})
    assert idx.message_ids("t") == ["new2", "new1"], "windowed view is unchanged"
    assert idx.inbox_message_ids("t") == ["new2", "OLD_OUTSIDE_WINDOW"]


def test_missing_inbox_scan_returns_none_not_empty():
    """None means 'unknown, fall back'. An empty list would read as 'no INBOX
    messages', which would silently skip archiving the thread entirely."""
    idx = mailbox_index.MailboxIndex(order={"t": ["m"]}, sent_ids=set(), pages=1)
    assert idx.inbox_message_ids("t") is None


def test_thread_absent_from_inbox_scan_is_empty_not_none():
    """The scan ran and this thread simply has no INBOX messages: a real answer."""
    idx = mailbox_index.MailboxIndex(order={"t": ["m"]}, sent_ids=set(), pages=1,
                                     inbox_order={"other": ["x"]})
    assert idx.inbox_message_ids("t") == []


def test_archive_set_unions_out_of_window_inbox_messages():
    """The regression itself: the archive set must cover every INBOX message."""
    import review_open_loops as rol

    idx = mailbox_index.MailboxIndex(
        order={"t": ["in_window_2", "in_window_1"]}, sent_ids=set(), pages=1,
        inbox_order={"t": ["in_window_2", "OLD_STILL_IN_INBOX"]})

    rol._gws_read = lambda cfg, args, method=None: {
        "payload": {"headers": [{"name": "From", "value": "A <a@b.com>"},
                                {"name": "Subject", "value": "s"}]},
        "snippet": "x", "labelIds": ["INBOX"]}
    info = rol._thread_info_via_index("cfg", "t", "me@x.com", idx)

    assert "OLD_STILL_IN_INBOX" in info["ids"], (
        "the out-of-window message still carrying INBOX must be archived, "
        "or the thread never leaves the inbox")
    assert "in_window_1" in info["ids"], "in-window messages are still included"
    assert len(info["ids"]) == len(set(info["ids"])), "no duplicate ids"


def test_inbox_query_is_not_windowed():
    """If this scan is ever windowed the bug comes straight back."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "mailbox_index.py")).read()
    assert "_windowed(INBOX_QUERY" not in src, \
        "the inbox scan must stay unwindowed; see INBOX_QUERY"


def test_cache_schema_bumped_to_discard_truncated_rows():
    """Rows written before the fix hold truncated id lists and cannot be
    distinguished from good ones, so they must be discarded wholesale."""
    import thread_cache
    assert thread_cache.SCHEMA_VERSION >= 2


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    print("archive completeness: all tests passed")
