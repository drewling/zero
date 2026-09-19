#!/usr/bin/env python3
"""The throttle figure a run reports must mean wall-clock time.

total_wait sums across workers, so a 16-worker run reported "2,916 seconds
throttled" for an 8-minute run. That is a real number (worker-seconds) but it is
not the number anyone reads it as, and it made the run look far worse than it
was. stats() now reports the union of real time during which at least one worker
was blocked, and keeps the summed figure under a name that says what it is.
"""
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gmail_quota as gq  # noqa: E402


class Clock:
    """Virtual time, so a minute of throttling costs no real seconds."""

    def __init__(self):
        self.t = 0.0
        self.lock = threading.Lock()

    def __call__(self):
        return self.t

    def sleep(self, d):
        with self.lock:
            self.t += d


def test_wall_wait_never_exceeds_elapsed_time():
    clock = Clock()
    lim = gq.UnitLimiter(units_per_minute=100, clock=clock, sleep=clock.sleep,
                         units_per_second=None)
    start = clock.t
    for _ in range(12):
        lim.acquire(20)
    elapsed = clock.t - start
    s = lim.stats()
    assert s["throttled_seconds"] <= elapsed + 1e-6, \
        f"wall throttle {s['throttled_seconds']} exceeds elapsed {elapsed}"


def test_concurrent_waiters_are_not_double_counted():
    """Two workers blocked over the SAME interval is one interval of waiting."""
    clock = Clock()
    lim = gq.UnitLimiter(units_per_minute=100, clock=clock, sleep=clock.sleep,
                         units_per_second=None)
    lim.acquire(100)                      # exhaust the window

    barrier = threading.Barrier(2)

    def worker():
        barrier.wait()
        lim.acquire(10)

    ts = [threading.Thread(target=worker) for _ in range(2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()

    s = lim.stats()
    assert s["throttled_worker_seconds"] >= s["throttled_seconds"], \
        "summed worker time must be >= wall time, never less"
    assert s["throttled_seconds"] <= clock.t + 1e-6


def test_both_figures_are_reported():
    lim = gq.UnitLimiter(units_per_minute=6000)
    s = lim.stats()
    assert "throttled_seconds" in s
    assert "throttled_worker_seconds" in s


def test_no_waiting_reports_zero():
    lim = gq.UnitLimiter(units_per_minute=6000)
    lim.acquire(20)
    assert lim.stats()["throttled_seconds"] == 0.0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    print("throttle reporting: all tests passed")
