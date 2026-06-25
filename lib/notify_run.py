#!/usr/bin/env python3
"""Queue a 'run complete' notification for the zero app to post natively.

Used by the scheduled launchd run (bin/zero run), which runs the per-account
sweep directly and never touches keeper_server. Reuses the server's writer so
the file format, path, and notify_on_run gate stay in exactly one place.

Usage: notify_run.py <set_aside> <kept>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keeper_server as ks  # noqa: E402  (importing only pulls in defs; server boot is __main__-gated)


def _int(arg):
    try:
        return int(arg)
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    ks._queue_run_notification(_int(sys.argv[1] if len(sys.argv) > 1 else 0),
                               _int(sys.argv[2] if len(sys.argv) > 2 else 0))
