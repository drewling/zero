#!/usr/bin/env python3
"""No-network checks for bounded, ordered Gmail metadata reads.
Run: python3 lib/tests/test_parallel_reads.py
"""
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import review_open_loops as rol  # noqa: E402


calls = []
calls_lock = threading.Lock()


def reset_cache():
    with rol._REPLIED_LOCK:
        rol._REPLIED.clear()
        rol._REPLIED_IN_FLIGHT.clear()


def fake_gws(_cfg, args):
    """Stub both Gmail endpoints, with deliberately out-of-order completion times."""
    params = json.loads(args[args.index("--params") + 1])
    with calls_lock:
        calls.append(params)
    if "threads" in args and "get" in args:
        tid = params["id"]
        time.sleep(0.008 * (5 - (int(tid.split("-")[-1]) % 5)))
        if tid == "thread-3":
            return {"messages": []}  # Must remain skipped.
        email = "shared@example.com" if tid in ("thread-1", "thread-4") else f"{tid}@example.com"
        return {"messages": [{"id": tid + "-message", "snippet": "snippet " + tid,
                "labelIds": ["INBOX"], "payload": {"headers": [
                    {"name": "From", "value": "Sender <" + email + ">"},
                    {"name": "Subject", "value": "Subject " + tid},
                ]}}]}
    query = params["q"]
    email = query.split("to:", 1)[1]
    time.sleep(0.003)
    if email == "fail@example.com":
        raise RuntimeError("temporary network failure")
    return {"messages": [{"id": "reply"}]} if email == "thread-2@example.com" else {}


original_gws = rol.iz.gws
original_emit = rol._emit_progress
rol.iz.gws = fake_gws
try:
    tids = [f"thread-{i}" for i in range(6)]

    # The concurrent list must have exactly the content and source order of the old loop.
    reset_cache()
    sequential = [rol._read_one_thread("cfg", tid, "owner@example.com") for tid in tids]
    sequential = [item for item in sequential if item]
    reset_cache()
    progress = []
    rol._emit_progress = lambda pct, label="": progress.append((pct, label))
    parallel = rol._read_infos_parallel("cfg", tids, "owner@example.com", max_workers=4)
    assert parallel == sequential, (parallel, sequential)
    assert [item["id"] for item in parallel] == ["thread-0", "thread-1", "thread-2", "thread-4", "thread-5"]

    # Completion order is intentionally unstable, but UI markers are monotonic and complete.
    percentages = [pct for pct, _label in progress]
    assert len(percentages) == len(tids), percentages
    assert percentages == sorted(percentages), percentages
    assert percentages[-1] == 65, percentages

    # Many matching senders issue exactly one reply-history lookup, even concurrently.
    reset_cache()
    with calls_lock:
        calls.clear()
    same_sender = ["thread-1", "thread-4"] * 8
    infos = rol._read_infos_parallel("cfg", same_sender, "owner@example.com", max_workers=12)
    assert len(infos) == len(same_sender)
    reply_queries = [p for p in calls if "q" in p and "to:shared@example.com" in p["q"]]
    assert len(reply_queries) == 1, reply_queries
    assert rol._replied_before("cfg", "shared@example.com") is False

    # Failed reply-history reads remain keep-safe (assume the owner replied).
    reset_cache()
    assert rol._replied_before("cfg", "fail@example.com") is True
    assert rol._replied_before("cfg", "fail@example.com") is True
finally:
    rol.iz.gws = original_gws
    rol._emit_progress = original_emit

print("parallel_reads OK")
