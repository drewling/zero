"""Opt-in JSON metrics. Never record mail, paths, addresses, prompts or errors."""
import atexit
import json
import os
import sys
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from runtime_state import account_id, locked

_lock = threading.Lock()
_rows = defaultdict(lambda: defaultdict(float))
_started = time.monotonic()


def record(api, account='', **values):
    if os.environ.get('ZERO_METRICS', '1') != '1':
        return
    with _lock:
        row = _rows[(api, account_id(account) if account else 'process')]
        for key, value in values.items():
            row[key] += value


@contextmanager
def measured(api, account='', **values):
    start = time.monotonic()
    failed = 0
    try:
        yield
    except BaseException:
        failed = 1
        raise
    finally:
        record(api, account, calls=1, failures=failed,
               seconds=time.monotonic() - start, **values)


def report():
    if os.environ.get('ZERO_METRICS', '1') != '1':
        return
    with _lock:
        rows = [{'api': api, 'account': account, **{k: round(v, 6) for k, v in vals.items()}}
                for (api, account), vals in sorted(_rows.items())]
    # Prefix ensures existing stdout result parsers cannot confuse this with mail data.
    payload = json.dumps({'stage': os.environ.get('ZERO_STAGE', os.path.basename(sys.argv[0])),
                          'elapsed_seconds': round(time.monotonic() - _started, 6), 'rows': rows})
    print('METRICS ' + payload, file=sys.stderr, flush=True)
    # App subprocess stderr is captured, so keep a bounded local metrics-only log.
    path = os.environ.get('ZERO_METRICS_PATH', os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'logs', 'pipeline-metrics.jsonl'))
    try:
        with locked(path):
            if os.path.exists(path) and os.path.getsize(path) > 2_000_000:
                os.replace(path, path + '.1')
            with open(path, 'a', encoding='utf-8') as f:
                f.write(payload + '\n')
    except OSError:
        pass  # metrics cannot fail a mail operation



atexit.register(report)
