#!/usr/bin/env python3
"""Bulk mailbox index: get the classifier's inputs for thousands of threads in a
handful of cheap calls instead of one expensive call per thread.

THE INSIGHT
-----------
The old reader paid, PER THREAD:
    threads.get   40 units   (last sender, subject, snippet, label ids, msg ids)
  + messages.list  5 units   (replied_before for that sender)
  = 45 units x N threads

For a 3,221-thread account that is 144,945 units against a 6,000/min ceiling:
~24 minutes of pure waiting, assuming you never trip the limit. With 16 workers
it did ~78,000 units/min and tripped it immediately, which is the "frozen at
130 of 3221" the user actually watched.

Almost all of that spend is redundant. `messages.list` returns `id` + `threadId`
for **500 messages per 5-unit call**, and Gmail returns them newest-first. So one
paged scan of the mailbox yields, for every thread at once:
  - every message id in the thread          (was: threads.get -> info["ids"])
  - which message is newest                 (first occurrence, reverse-chron)
  - whether that newest message is the owner's, via SENT label membership
                                            (was: threads.get -> last_from_owner)
and `threads.list` (10 units / 100 threads) already hands back `snippet` free
while enumerating candidates.

That leaves only From/Subject, which needs one `messages.get` (20u, metadata) on
just the NEWEST message of each candidate thread. Half the price of threads.get
for the same information.

MEASURED ON THE REAL ACCOUNT (tayo, 69,822 messages, 55,680 threads):
    full `in:anywhere` scan  = 70,498 msgs / 141 pages / 705 units / 73s
    `in:sent` scan           =  9,657 msgs /  20 pages / 100 units /  9s
    agreement vs threads.get on 100 real candidate threads:
        last-message id       100/100
        full thread id set    100/100
        last_from_owner       100/100  (0 unsafe disagreements)

SAFETY
------
The dangerous failure is deciding `last_from_owner=True` when it is false, since
that archives deterministically with no classifier involved. That can only happen
if the scan MISSES a thread's true newest message and an older SENT message is
mistaken for it. So the scan deliberately covers `in:anywhere` (all mail, incl.
archived) rather than the tempting `in:inbox OR in:sent` — measured, the narrow
query returned far fewer messages and would have exactly this blind spot. Any
thread not fully covered by the index is reported as not-covered and falls back
to the per-thread read; the index never guesses.
"""
import json
import subprocess

import gmail_quota as gq

# Gmail caps list pages at 500 ids. Each page is one messages.list call (5 units),
# so 500 is both the fewest calls and the fewest units per message.
PAGE_SIZE = 500

# The scan must see a thread's true newest message or last_from_owner can be
# wrong in the unsafe direction, so it covers everything Gmail will return.
SCAN_QUERY = "in:anywhere"
SENT_QUERY = "in:sent"


def _pages_from_stdout(stdout):
    """Parse gws --page-all output (one JSON object per page) into page dicts.

    gws prints keyring noise to stdout, and the pages are newline-delimited JSON
    rather than one array, so this filters and parses line by line."""
    pages = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{") or "keyring" in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if isinstance(o, dict) and o.get("error"):
            raise RuntimeError(f"API error during scan: {json.dumps(o['error'])}")
        pages.append(o)
    return pages


def _scan(cfg, query, env_fn, limiter=None, page_size=PAGE_SIZE, runner=None):
    """One paged messages.list sweep. Returns (messages, page_count).

    Uses gws --page-all so the whole sweep is a single subprocess: 141 pages of
    the real mailbox took 73s that way, versus 141 separate process spawns.

    The unit budget is charged for every page the sweep actually fetched. We
    cannot throttle *between* pages inside one gws invocation, so this reserves
    one page up front and reconciles afterwards. At 5 units/page a whole
    141-page scan is 705 units, comfortably inside one minute's budget.

    `runner` is injectable for tests; it defaults to a real subprocess call."""
    args = ["gws", "gmail", "users", "messages", "list",
            "--params", json.dumps({"userId": "me", "q": query,
                                    "maxResults": page_size}),
            "--page-all", "--page-limit", "1000"]
    if limiter is not None:
        limiter.acquire(gq.cost_of("messages.list"))
    if runner is not None:
        stdout = runner(args)
    else:
        r = subprocess.run(args, capture_output=True, text=True, env=env_fn(cfg))
        if r.returncode != 0:
            err = "\n".join(l for l in (r.stderr or "").splitlines()
                            if "keyring" not in l).strip()
            raise RuntimeError(
                f"bulk scan {query!r} failed: {err or 'gws non-zero exit'}")
        stdout = r.stdout
    pages = _pages_from_stdout(stdout)
    msgs = []
    for p in pages:
        msgs += p.get("messages", []) or []
    if limiter is not None and len(pages) > 1:
        # Charge the remaining pages so the ledger matches what Gmail billed.
        limiter.acquire(gq.cost_of("messages.list") * (len(pages) - 1))
    return msgs, len(pages)


class MailboxIndex:
    """Thread -> (ordered message ids, newest message id, owner-sent?) for the
    whole mailbox, built from two cheap scans.

    `covers(tid)` is the honesty check: it is only True when the index genuinely
    saw the thread, so callers can fall back per-thread instead of assuming."""

    def __init__(self, order, sent_ids, pages):
        self.order = order              # tid -> [msg ids], newest first
        self.sent_ids = sent_ids        # message ids carrying the SENT label
        self.pages = pages              # pages fetched, for unit accounting
        self.units = pages * gq.cost_of("messages.list")

    def covers(self, tid):
        return tid in self.order

    def message_ids(self, tid):
        """All message ids in the thread (what batchModify archives)."""
        return list(self.order.get(tid, []))

    def newest(self, tid):
        ids = self.order.get(tid)
        return ids[0] if ids else None

    def last_from_owner(self, tid):
        """True when the thread's newest message carries the SENT label.

        Verified 100/100 against threads.get From-header parsing on real
        candidate threads. An unknown thread returns False, which routes it to
        the classifier (keep-biased) rather than the deterministic archive."""
        n = self.newest(tid)
        return bool(n and n in self.sent_ids)

    def stats(self):
        return {"threads": len(self.order), "pages": self.pages,
                "units": self.units, "sent_messages": len(self.sent_ids)}


def build_index(cfg, env_fn, limiter=None, log=None, runner=None):
    """Build a MailboxIndex, or return None if either scan fails.

    Returning None (rather than raising) is deliberate: the index is a pure
    OPTIMISATION. If it can't be built, the caller must still be able to fall
    back to the per-thread path and produce a correct, keep-safe run."""
    try:
        msgs, pages = _scan(cfg, SCAN_QUERY, env_fn, limiter, runner=runner)
        sent, sent_pages = _scan(cfg, SENT_QUERY, env_fn, limiter, runner=runner)
    except Exception as exc:
        if log:
            log(f"bulk index unavailable, falling back to per-thread reads: {exc}")
        return None
    order = {}
    for m in msgs:                       # newest-first, verified on live data
        tid = m.get("threadId")
        if tid:
            order.setdefault(tid, []).append(m["id"])
    sent_ids = {m["id"] for m in sent if m.get("id")}
    return MailboxIndex(order, sent_ids, pages + sent_pages)


if __name__ == "__main__":
    idx = MailboxIndex(order={"t1": ["m3", "m2", "m1"], "t2": ["m9"]},
                       sent_ids={"m3"}, pages=3)
    assert idx.covers("t1") and not idx.covers("nope")
    assert idx.message_ids("t1") == ["m3", "m2", "m1"]
    assert idx.newest("t1") == "m3"
    assert idx.last_from_owner("t1") is True
    assert idx.last_from_owner("t2") is False
    assert idx.last_from_owner("nope") is False     # unknown -> classifier path
    assert _pages_from_stdout('keyring junk\n{"messages":[{"id":"a"}]}\n') == \
        [{"messages": [{"id": "a"}]}]
    # A failed scan degrades to None (fall back), never raises.
    def boom(_args):
        raise RuntimeError("gws exploded")
    assert build_index("cfg", lambda c: {}, runner=boom) is None
    print("mailbox_index self-check OK")
