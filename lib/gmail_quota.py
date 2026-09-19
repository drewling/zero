#!/usr/bin/env python3
"""Cost-aware Gmail quota governor: a units-per-minute limiter plus Google's
documented truncated exponential backoff.

WHY THIS EXISTS
---------------
Gmail bills API calls in "quota units", not requests, and enforces
**6,000 quota units per minute per user per project**
(https://developers.google.com/workspace/gmail/api/reference/quota).
Different methods cost wildly different amounts: `threads.get` is 40 units,
`messages.get` is 20, `messages.list` is 5, `labels.list` is 1.

That is why a worker-count is the wrong knob, and why raising it made things
worse. 16 workers doing `threads.get` + `messages.list` (45 units) per thread is
~29 threads/sec = ~78,000 units/min, which is 13x over the limit. The run then
died with:

    Quota exceeded for quota metric 'Total Query Cost' and limit
    'Units per minute per user' of service 'gmail.googleapis.com'

Concurrency is still the right tool for LATENCY (these calls are network-bound
subprocesses), but it has to be bounded by a UNIT budget rather than a thread
count. This module supplies that budget, so callers can keep concurrency and
still stay legal.

SLIDING WINDOW, NOT A LEAKY BUCKET
----------------------------------
Google's limit is "units per minute". A classic token bucket pre-filled to
capacity would permit a full 6,000-unit burst and then keep refilling, so a
60-second window straddling the burst can observe close to 2x the budget. This
uses an exact sliding-window ledger instead: every grant is recorded with its
timestamp, entries older than the window are retired, and a request that would
push the trailing-60s total over budget sleeps until enough of the oldest
entries have aged out. The invariant is therefore literal, and testable:

    the sum of costs granted in ANY 60-second window never exceeds the budget.
"""
import random
import threading
import time
from collections import deque

# Official per-method quota units. Only the methods this codebase actually calls
# are listed; `cost_of` falls back to a deliberately pessimistic default so a new
# call site can never be silently under-billed against the budget.
# Source: https://developers.google.com/workspace/gmail/api/reference/quota
UNIT_COSTS = {
    "getProfile": 1,
    "history.list": 2,
    "labels.get": 1,
    "labels.list": 1,
    "labels.create": 5,
    "messages.list": 5,
    "messages.get": 20,
    "messages.modify": 5,
    "messages.batchModify": 50,
    "threads.list": 10,
    "threads.get": 40,
    "threads.modify": 10,
    "drafts.create": 10,
    "drafts.get": 20,
    "drafts.update": 15,
    "drafts.send": 100,
    "drafts.delete": 10,
    "settings.sendAs.list": 1,
    "sendAs.list": 1,        # method_from_args collapses the nested settings path
}

# The published ceiling, and the fraction of it we actually spend. The headroom
# absorbs (a) other processes on the same account — run.sh sweeps several
# accounts and the panel makes its own reads — and (b) the fact that our
# accounting is client-side and cannot see a retry Google counted but we didn't.
GMAIL_UNITS_PER_MINUTE = 6000
# The headroom used to be 20%, a blunt guard against bursts we could not see.
# The per-second pacer below is the precise version of that guard, and the
# cross-process ledger handles the sibling-process case, so the fraction now
# only covers accounting drift (a retry Google counted and we did not).
DEFAULT_BUDGET_FRACTION = 0.95         # 5,700 units/min of the 6,000 ceiling
DEFAULT_WINDOW_SECONDS = 60.0

# The limit that actually bites. Gmail publishes a 250 units/SECOND per-user
# ceiling alongside the 6,000/minute one, and enforces it strictly: a burst
# that respects the minute budget still gets 429s if it arrives all at once.
# Measured on the live account, an unpaced batch sweep came back 19% 429 and
# the retry storm made higher concurrency *slower* (8 workers took 76s to do
# what 4 did in 22s). Pacing to this rate removes the retries entirely, so the
# minute budget is spent on useful reads instead of being burned twice.
GMAIL_UNITS_PER_SECOND = 250
BURST_WINDOW_SECONDS = 1.0

# Truncated exponential backoff, exactly as Google documents it:
#   wait = min((2^n) + random_number_milliseconds, maximum_backoff)
# with random_number_milliseconds <= 1000, recalculated every retry.
MAX_BACKOFF_SECONDS = 64.0
DEFAULT_MAX_RETRIES = 6


def cost_of(method, default=40):
    """Quota units for a method name like "messages.get".

    Unknown methods bill at `default` (the price of the most expensive call we
    make, threads.get). Over-billing only slows us down; under-billing is what
    trips the 429, so the default errs toward the safe side."""
    return UNIT_COSTS.get(method, default)


def method_from_args(args):
    """Infer the API method from a gws argv, e.g.
    ["gmail","users","messages","get","--params",...] -> "messages.get".

    Returns None when the shape isn't recognised, so callers can fall back to an
    explicit cost rather than guessing."""
    parts = [a for a in args if not a.startswith("-")]
    try:
        i = parts.index("users")
    except ValueError:
        return None
    tail = parts[i + 1:]
    # Drop positional values that follow a flag (e.g. the JSON blob after --params).
    verbs = [p for p in tail if p and not p.startswith("{")]
    if not verbs:
        return None
    if len(verbs) == 1:
        return verbs[0]                       # getProfile
    return ".".join(verbs[:2]) if len(verbs) == 2 else ".".join(verbs[-2:])


def is_quota_error(exc):
    """Whether a gws failure is a rate-limit / quota denial worth backing off on.

    Covers Gmail's two distinct shapes: the per-second user rate limit
    (rateLimitExceeded / 429) and the per-minute unit budget denial, which
    arrives as the verbose "Quota exceeded for quota metric 'Total Query Cost'"
    message. draftutil._gws deliberately treats bare "quota" as fatal; here we
    know it is a time-based limit, which Google's own docs say to retry with
    backoff, so we handle it rather than failing the account."""
    t = str(exc).lower()
    if "quota exceeded" in t or "total query cost" in t:
        return True
    if "ratelimitexceeded" in t or "userratelimitexceeded" in t:
        return True
    if "429" in t or "too many requests" in t:
        return True
    if "resource_exhausted" in t or "resource exhausted" in t:
        return True
    return "403" in t and "rate" in t


def backoff_delay(attempt, max_backoff=MAX_BACKOFF_SECONDS, rand=random.random):
    """Google's documented algorithm: min((2^n) + random_ms, maximum_backoff).

    `attempt` is 0-based, so the sequence is ~1s, 2s, 4s, 8s ... capped at
    max_backoff. The jitter (<= 1000ms, recomputed per retry) is what stops many
    workers that were throttled together from retrying in a synchronised wave —
    which matters here precisely because we run reads concurrently."""
    return min((2 ** attempt) + rand(), max_backoff)


class UnitLimiter:
    """Shared, thread-safe, cost-aware sliding-window rate limiter.

    One instance is shared by every worker reading a given account, so the
    budget is enforced across the whole run rather than per thread. `acquire`
    blocks until spending `cost` keeps the trailing window within budget.

    `clock`/`sleep` are injectable so tests can simulate a minute of traffic
    instantly and assert the invariant without real waiting."""

    def __init__(self, units_per_minute=None, window=DEFAULT_WINDOW_SECONDS,
                 clock=time.monotonic, sleep=time.sleep, account=None,
                 units_per_second=GMAIL_UNITS_PER_SECOND):
        if units_per_minute is None:
            units_per_minute = int(GMAIL_UNITS_PER_MINUTE * DEFAULT_BUDGET_FRACTION)
        self.budget = max(1, int(units_per_minute))
        # Gmail's budget belongs to the ACCOUNT, not to this process. With an
        # account id we also book every grant in a cross-process ledger, so the
        # keeper run, the background sync and the state builder share one
        # budget instead of each believing it owns the whole thing (which is
        # what produced live 403s and a stalled-looking progress bar).
        self.shared = None
        if account:
            try:
                import quota_ledger
                self.shared = quota_ledger.SharedLedger(account, self.budget,
                                                        window=float(window))
            except Exception:
                self.shared = None      # degrade to in-process only
        self.window = float(window)
        # Second tier: the per-second ceiling. Scaled with the minute budget so
        # a caller asking for a small budget (tests, probes) is not silently
        # allowed to burst at the full account rate.
        if units_per_second is None:
            self.burst_budget = None
        else:
            share = self.budget / float(GMAIL_UNITS_PER_MINUTE)
            self.burst_budget = max(1, int(min(float(units_per_second),
                                               units_per_second * share)))
        self._burst = deque()       # (timestamp, cost) within BURST_WINDOW
        self._burst_spent = 0
        self._clock = clock
        self._sleep = sleep
        self._events = deque()      # (timestamp, cost) granted within the window
        self._spent = 0             # running sum of self._events costs
        self._lock = threading.Lock()
        self.total_units = 0        # lifetime units, for reporting
        self.total_calls = 0
        self.total_wait = 0.0       # seconds spent throttled, for reporting

    def _retire(self, now):
        """Drop ledger entries that have aged out of the window. Caller holds lock."""
        cutoff = now - self.window
        while self._events and self._events[0][0] <= cutoff:
            self._spent -= self._events.popleft()[1]
        bcut = now - BURST_WINDOW_SECONDS
        while self._burst and self._burst[0][0] <= bcut:
            self._burst_spent -= self._burst.popleft()[1]

    def acquire(self, cost):
        """Block until `cost` units can be spent without breaching the window."""
        cost = max(0, int(cost))
        if cost == 0:
            return 0.0
        waited = 0.0
        while True:
            with self._lock:
                now = self._clock()
                self._retire(now)
                # A single call pricier than the whole budget would deadlock; let
                # it through alone once the window is clear, and let backoff
                # handle the fallout. (No Gmail method we call is this big.)
                # Both ceilings must have room: the trailing minute AND the
                # trailing second. Whichever is tighter decides when we go.
                minute_ok = self._spent + cost <= self.budget or not self._events
                if self.burst_budget is None:
                    burst_ok = True
                else:
                    burst_ok = (self._burst_spent + cost <= self.burst_budget
                                or not self._burst)
                if minute_ok and burst_ok:
                    self._events.append((now, cost))
                    self._spent += cost
                    self._burst.append((now, cost))
                    self._burst_spent += cost
                    self.total_units += cost
                    self.total_calls += 1
                    self.total_wait += waited
                    grant = True
                else:
                    grant = False
            if grant:
                # This process has room. Now check whether the ACCOUNT does:
                # another process may already have spent the window. Done
                # outside the in-process lock so siblings are not blocked while
                # we wait on the shared ledger.
                if self.shared is not None:
                    shared_wait = self.shared.acquire(cost, sleep=self._sleep)
                    # Only the NEW wait is added: `waited` was already folded
                    # into total_wait above, and counting it twice would make
                    # the throttle figure the run reports meaningless.
                    self.total_wait += shared_wait
                    waited += shared_wait
                return waited
            with self._lock:
                # Sleep exactly until the ceiling that blocked us frees up. If
                # only the per-second tier is full that is a few milliseconds,
                # not a minute, so pacing costs almost nothing in wall time.
                delay = 0.0
                if not minute_ok and self._events:
                    delay = max(delay, (self._events[0][0] + self.window) - now)
                if not burst_ok and self._burst:
                    delay = max(delay,
                                (self._burst[0][0] + BURST_WINDOW_SECONDS) - now)
                delay = max(0.0, delay)
            delay = min(delay, self.window) + 0.001
            self._sleep(delay)
            waited += delay

    def penalise(self, units=None):
        """Charge the budget for a throttle we were told about but didn't predict.

        When Gmail returns a quota error our client-side ledger is provably
        behind reality (another process on the account, or a retry Google counted
        and we didn't). Booking a synthetic charge makes every worker sharing
        this limiter slow down, instead of each one independently retrying into
        the same wall."""
        if units is None:
            units = self.budget // 2
        with self._lock:
            now = self._clock()
            self._retire(now)
            self._events.append((now, int(units)))
            self._spent += int(units)
            # Charge the burst tier too, otherwise the next instant after a
            # throttle we would immediately fire another full-rate burst.
            self._burst.append((now, int(units)))
            self._burst_spent += int(units)

    def stats(self):
        return {"units": self.total_units, "calls": self.total_calls,
                "throttled_seconds": round(self.total_wait, 2),
                "budget_per_minute": self.budget}


def call_with_quota(fn, method, limiter=None, max_retries=DEFAULT_MAX_RETRIES,
                    sleep=time.sleep, rand=random.random, on_retry=None):
    """Run one Gmail call under the unit budget, retrying quota errors properly.

    Order matters: we pay the budget BEFORE issuing the call (so the limiter
    reflects what is in flight), and on a quota error we both back off and
    penalise the shared limiter so sibling workers slow down too.

    Non-quota errors propagate immediately — an auth failure must not be retried
    six times, and callers upstream already resolve a failed read to "keep"."""
    cost = cost_of(method)
    last = None
    for attempt in range(max_retries + 1):
        if limiter is not None:
            limiter.acquire(cost)
        try:
            return fn()
        except Exception as exc:
            if not is_quota_error(exc) or attempt >= max_retries:
                raise
            last = exc
            if limiter is not None:
                limiter.penalise()
            delay = backoff_delay(attempt, rand=rand)
            if on_retry is not None:
                on_retry(attempt, delay, exc)
            sleep(delay)
    raise last


if __name__ == "__main__":
    assert cost_of("messages.get") == 20 and cost_of("threads.get") == 40
    assert cost_of("totally.unknown") == 40          # pessimistic default
    assert method_from_args(["gmail", "users", "messages", "get", "--params", "{}"]) \
        == "messages.get"
    assert method_from_args(["gmail", "users", "getProfile", "--params", "{}"]) \
        == "getProfile"
    assert is_quota_error(RuntimeError(
        "Quota exceeded for quota metric 'Total Query Cost'"))
    assert not is_quota_error(RuntimeError("401 unauthorized"))
    assert [round(backoff_delay(n, rand=lambda: 0.5), 1) for n in range(4)] == \
        [1.5, 2.5, 4.5, 8.5]
    print("gmail_quota self-check OK")
