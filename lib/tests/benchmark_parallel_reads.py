#!/usr/bin/env python3
"""Local no-network latency benchmark for the Gmail read phase.
Run: python3 lib/tests/benchmark_parallel_reads.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import review_open_loops as rol  # noqa: E402

THREADS = 200
LATENCY_SECONDS = 0.5
WORKERS = 16


def fake_gws(_cfg, args):
    time.sleep(LATENCY_SECONDS)
    params = json.loads(args[args.index("--params") + 1])
    if "threads" in args and "get" in args:
        tid = params["id"]
        return {"messages": [{"id": tid + "-message", "snippet": "stub",
                "labelIds": ["INBOX"], "payload": {"headers": [
                    {"name": "From", "value": f"Sender <{tid}@example.com>"},
                    {"name": "Subject", "value": tid},
                ]}}]}
    return {"messages": []}


def reset_cache():
    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()


def run_sequential(tids):
    return [rol._read_one_thread("cfg", tid, "owner@example.com") for tid in tids]


original_gws = rol.iz.gws
original_emit = rol._emit_progress
rol.iz.gws = fake_gws
rol._emit_progress = lambda _pct, _label="": None
try:
    tids = [f"thread-{i}" for i in range(THREADS)]
    reset_cache()
    started = time.monotonic()
    sequential = run_sequential(tids)
    sequential_seconds = time.monotonic() - started

    reset_cache()
    started = time.monotonic()
    parallel = rol._read_infos_parallel("cfg", tids, "owner@example.com", WORKERS)
    parallel_seconds = time.monotonic() - started
finally:
    rol.iz.gws = original_gws
    rol._emit_progress = original_emit

assert parallel == sequential
print(f"parallel_reads benchmark: {THREADS} threads, 2 calls/thread, {LATENCY_SECONDS:.1f}s stub latency")
print(f"sequential: {sequential_seconds:.2f}s")
print(f"parallel ({WORKERS} workers): {parallel_seconds:.2f}s")
print(f"speedup: {sequential_seconds / parallel_seconds:.2f}x")
