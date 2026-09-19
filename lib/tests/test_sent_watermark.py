#!/usr/bin/env python3
"""Cached "never replied" negatives may only survive a provably unchanged Sent box.

A negative ("the owner has never written to this address") is the dangerous
direction: it feeds the cold-outreach signal and biases toward ARCHIVING. The
cache used to discard every negative on load, which was safe but cost ~1,300
sender probes on each warm run. The watermark makes the reuse precise instead of
blanket, so these tests pin BOTH directions: reused when provable, dropped
whenever there is any doubt.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import thread_cache  # noqa: E402


def seed(path, watermark):
    """A cache holding one positive and one negative at `watermark`."""
    c = thread_cache.load("t", path=path, sent_watermark=watermark)
    c.put_replied("friend@example.test", True)
    c.put_replied("stranger@example.test", False)
    c.save(force=True)
    return c


def test_negative_survives_unchanged_sent():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.json")
        seed(p, "sent-1")
        c = thread_cache.load("t", path=p, sent_watermark="sent-1")
        assert c.replied_before("stranger@example.test") is False, \
            "negative must be reused when the Sent box has not moved"
        assert c.replied_before("friend@example.test") is True


def test_negative_dropped_when_owner_has_sent():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.json")
        seed(p, "sent-1")
        # The owner sent something: "never wrote to them" is no longer provable.
        c = thread_cache.load("t", path=p, sent_watermark="sent-2")
        assert c.replied_before("stranger@example.test") is None, \
            "negative must be re-probed once the owner has sent mail"
        assert c.replied_before("friend@example.test") is True, \
            "positives are unaffected by the watermark"


def test_negative_dropped_without_watermark():
    """No watermark = no proof = the old blanket-discard behaviour."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.json")
        seed(p, "sent-1")
        c = thread_cache.load("t", path=p)
        assert c.replied_before("stranger@example.test") is None
        assert c.replied_before("friend@example.test") is True


def test_stale_negative_not_resurrected_by_save_merge():
    """save() re-merges from disk; that must not undo the load-time discard."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.json")
        seed(p, "sent-1")
        c = thread_cache.load("t", path=p, sent_watermark="sent-2")
        c.put_replied("other@example.test", True)
        c.save(force=True)
        # A later run at the SAME new watermark must still not see the old
        # negative: it was never re-established, so it cannot come back.
        c2 = thread_cache.load("t", path=p, sent_watermark="sent-2")
        assert c2.replied_before("stranger@example.test") is None, \
            "a discarded negative must not be resurrected by the save merge"


def test_empty_sent_is_a_usable_watermark():
    """An account that has never sent anything is a real, stable state."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.json")
        seed(p, "empty-sent")
        c = thread_cache.load("t", path=p, sent_watermark="empty-sent")
        assert c.replied_before("stranger@example.test") is False


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    print("sent watermark: all tests passed")
