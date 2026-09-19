# Why zero was slow, and what actually fixed it

Updated 2026-09-19. Every number here was measured on the live account
(tayo@drewl.com, ~3,000 inbox threads). Where an earlier document guessed, this
one states what was observed and how.

Read this first if you are about to "optimise" something: almost every real win
below came from deleting unnecessary work, and almost every hour wasted came
from making necessary work faster.

---

## The short version

The app was not slow because Gmail is slow, or because the classifier is slow.
It was slow because of five separate bugs that each caused the same thing:
**doing work over again that had already been done.**

| # | Bug | Effect |
|---|-----|--------|
| 1 | The run opened a different mirror file than the sync wrote | Re-read all 3,027 threads, every run |
| 2 | `needs_read` ignored the mirror | Would have planned 3,027 reads to perform 188 |
| 3 | Cached "never replied" facts discarded on every load | ~1,300 sender probes per run |
| 4 | Category labels applied one thread at a time | ~7 minutes of an execute run |
| 5 | Archive used a windowed message list | Threads never left the inbox, forever |

Plus two that made it look worse than it was: a quota limiter that modelled only
the per-minute ceiling (so we triggered 429 storms), and a throttle figure that
summed across workers (so an 8-minute run reported "2,916 seconds throttled").

Result on the same inbox, same verdicts:

```
before:  killed at the 600s timeout, still reading, never finished, inbox never shrank
after:   2.3s steady state, 18 quota units, 0s throttled
```

---

## How we got the diagnosis wrong twice first

**Round 1** blamed Gmail quota and wrote a caching plan. Wrong.

**Round 2** found a real problem (every Gmail call shelled out to a Node CLI:
830ms of local overhead around a 46ms network call) and fixed it with a pooled
HTTPS transport. Real win, but it was not the reason runs never finished.

**Round 3-4** chased stalls and fixed a genuine multi-process quota collision.
Still not the reason.

**Round 5** asked the question that should have been first: *is the inbox
actually shrinking?* It was not. Runs had been reporting "archive 2,812" for days
while the inbox sat at 3,285, because archiving happened once at the very end and
the parent killed the child at 600s first. **No run had ever completed.**

The lesson, written down because it cost days: **measure the outcome the user
cares about, not the thing that is easy to measure.** Dry runs skip archiving
entirely, so benchmarking them reported fast numbers for runs that were dying
every single time.

---

## The five bugs

### 1. Two names for the same mailbox mirror

`mailbox_sync`, `dashboard_state` and `keeper_server` key the local mirror on the
account **slug** (the gws config directory name, `tayo`). `review_open_loops`
keyed it on the account **label**, which is the email address.

So the sync diligently filled `tayo.sqlite3` (3,286 threads, 1.7 MB) and every
run opened `tayo@drewl.com.sqlite3` (0 threads, 24 KB).

Both files existed. Both opened cleanly. Nothing ever errored. The mirror had
been built and kept current for days and **not one row had ever been read.**

Fixed by resolving the name in one place, `mailbox_store.slug_for()`.

> This is the most expensive class of bug in the codebase: a cache that silently
> misses looks exactly like a cache that is working, only slower. If you add a
> cache, add an assertion or a metric that proves it is being hit.

### 2. `needs_read` disagreed with the code that does the reading

`_thread_info` checks three tiers: mirror (0 units), then persistent cache, then
Gmail. `needs_read` decided how much work a run faced by checking **only the
cache**, while its own comment claimed it used "the same predicate".

Even with bug 1 fixed, the run would have planned 3,027 reads (60,540 units,
11 minutes of budget) to perform 188 (3,760 units, 40 seconds).

### 3. Sender negatives were thrown away on every load

A "this sender has never been replied to" fact was discarded whenever the cache
loaded. That was **sound** (a reply elsewhere in the mailbox does not change the
candidate thread's historyId) but blunt, and it cost ~1,300 probes per run.

The precise version: a negative can only be falsified by the owner **sending**
something. The newest message id in Sent proves whether that has happened, for
5 units. Negatives now survive exactly when that watermark matches.

Every uncertain case (no watermark, none stored, a differing one, a failed probe)
falls back to discarding, so this can only make a run slower, never wrong.

### 4. Category labels were applied one thread at a time

A `threads.get` to see current labels, then a `threads.modify` to change them,
per thread, serially, through the Node CLI. 361 threads, about 7 minutes, and it
ran *after* all the reads.

None of that needed a network call. `label_ids_all` (the intersection across a
thread's messages) proves whether the target label is already on every message;
`label_ids` (the union) proves whether a stale category is present anywhere. The
mirror already carries both. Threads needing the same change now share one
`batchModify`.

The planner refuses to guess: a missing intersection, or a label Gmail has not
created yet, returns `"unplannable"` and goes down the authoritative path.

### 5. Archiving used a windowed list, so threads never left the inbox

This one was invisible for the longest and is the most instructive.

The bulk index is built from a **windowed** scan (recent mail plus a margin).
That is correct for classification: a missing two-year-old message does not
change who the newest sender is. But those same ids were used as the **archive**
set, and a thread's INBOX-bearing messages can be older than the window.

Proven on a real 9-message thread:

```
  Gmail has 9 messages; the archive set listed 6
  MISSING from the archive set: 3
     19f6c91212122997  INBOX=True     <-- still holding the thread in the inbox
     19f6c9241d28a46f  INBOX=True     <-- still holding the thread in the inbox
     19f6cece8c71864a  INBOX=False
```

The messages missing from the archive set were **exactly** the ones keeping the
thread in the inbox. `batchModify` removed INBOX from the 6 it knew about,
returned success, and the thread stayed put. The run reported "archived 6
threads" on every run, forever, while the inbox never moved. A permanent no-op
loop that looked precisely like progress.

Fixed with an additional **unwindowed** `in:inbox` scan, whose per-thread ids are
complete by construction, unioned into the archive set.

```
before: "archived 6 threads",  inbox 430 -> 430, every run
after:  "archived 13 threads", inbox 429 -> 416, 13 actually left
```

---

## Two things that made it look worse than it was

### Gmail's per-second ceiling

The limiter modelled the published 6,000 units/minute but not the 250
units/**second** that Gmail also enforces. A burst that respects the minute
budget still gets 429s if it arrives at once.

Measured, unpaced: 19% of batch sub-requests came back 429, and more concurrency
made it **slower and lossy**.

```
   4 parallel batches: 21.6s for 500/500
   8 parallel batches: 76.0s for 381/500   <-- more workers, worse, and losing mail
  16 parallel batches: 77.3s for 378/500
```

With pacing: 500/500 at every concurrency. Because bursts are now governed
precisely, the blunt 20% safety headroom dropped to 5%.

### A throttle figure nobody could read

`total_wait` sums across workers, so 16 threads waiting 3 minutes reported "2,916
seconds throttled" on an 8-minute run. Real number, wrong units for a human.
`stats()` now reports the union of real time during which at least one worker was
blocked, keeping the summed figure as `throttled_worker_seconds`.

---

## The sync could not finish either

After the run archived 2,547 threads, the background sync started a 2,045-thread
download that kept restarting. Two races:

1. **Cursor rewind.** A full sweep captures its cursor *before* reading (correct
   in isolation). If an incremental sync finished meanwhile, the sweep wrote its
   older id back afterwards and lost the newer position. Live: incremental set
   `7167910`, a sweep wrote back `7158487`, and the next sync faced a 9,354-record
   window it could never clear. `set_cursor` now refuses to move backwards.

2. **Overlapping syncs.** `_sync_lock` only guarded the results dict, so the
   interval loop and a manual `POST /api/sync` could sweep the same account at
   once, split its quota and reset each other's progress counter. A second caller
   is now told "busy".

Separately, Gmail reports every archive as a `labelsRemoved` record, so a big
sweep makes most of the inbox look "changed". The sync was re-reading those at 20
units each to learn what the run had just done deliberately. It now drops them
from the mirror instead, which is the correct end state for a mirror whose job is
to describe the inbox.

---

## Things that are true about Gmail and are not going to change

Established by direct measurement, so nobody re-litigates them:

- **`threads.get`/`messages.get` cost 20 units per thread for headers.** The
  `format` and `fields` parameters cut bandwidth, not quota.
- **`threads.list` and `messages.list` return IDs only** (plus `historyId` and a
  free `snippet`). Tested `fields`; it does not make them return headers.
- **Batching fixes latency, not cost.** A 100-id batch is one round trip but
  Google still bills each sub-request: 100 messages = 2,000 units either way.
- **A cold first pass has a hard floor.** 3,000 threads x 20 units / 6,000 per
  minute = about 10 minutes. There is no way around that except not reading
  threads you have already read, which is what the mirror is for.
- **Gmail's own categories are free.** `category:promotions` and friends
  classified 2,511 of 3,025 threads in 3 seconds for 120 units. Deliberately
  **not** used: the product's judgment is the point, not Gmail's.

---

## Test coverage added

All pinned against the live behaviour that motivated them:

- `test_sent_watermark.py` - negatives reused only when provable, including that
  a discarded negative is not resurrected by the save merge.
- `test_batched_categories.py` - no-op detection, partial targets, stale removal,
  grouping, failure isolation, unplannable threads returned not lost, and that
  only written threads are evicted from the mirror.
- `test_archive_completeness.py` - the windowed-archive bug. **Confirmed to fail
  when the fix is reverted.**
- `test_throttle_reporting.py` - wall time never exceeds elapsed time.
- `test_sync_departed.py` - archived threads are not re-downloaded, and absence
  is only concluded from an index we actually have.
- `test_sync_cursor.py` - the exact live cursor rewind, and the sync mutex.

74 tests pass.
