"""Exact full-thread metadata shared by read-only dashboard and catch-up views.

A newest-message classifier row is NOT equivalent: catch-up checks every sender,
and dashboard needs dates and labels. Reuse only full responses for the identical
header set, validated by a fresh listing's nonempty per-thread historyId. Missing
historyId, changed mail, corruption and read failure all take the live path.
No mutation decision consumes this cache.
"""
import json
import os
import time
import runtime_state as storage
import run_metrics as metrics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(ROOT, 'app', 'metadata_cache')
HEADERS = ['From', 'Subject', 'Date']
MAX_AGE = 86400
MAX_ENTRIES = 500


def _valid(thread, tid, history_id):
    if not isinstance(thread, dict) or thread.get('id') != tid:
        return False
    if not history_id or str(thread.get('historyId') or '') != str(history_id):
        return False
    messages = thread.get('messages')
    if not isinstance(messages, list) or not messages:
        return False
    for msg in messages:
        if not isinstance(msg, dict) or not isinstance(msg.get('id'), str):
            return False
        headers = (msg.get('payload') or {}).get('headers')
        if not isinstance(headers, list) or not all(
                isinstance(h, dict) and isinstance(h.get('name'), str)
                and isinstance(h.get('value'), str) for h in headers):
            return False
        if not isinstance(msg.get('labelIds', []), list):
            return False
    return True


def get(config_dir, tid, history_id, fetch):
    path = os.path.join(CACHE_DIR, storage.account_id(config_dir) + '.json')
    try:
        data = storage.read_json(path)
        row = data.get(tid, {})
        if (row.get('version') == 1 and row.get('headers') == HEADERS
                and 0 <= time.time() - row.get('at', 0) < MAX_AGE
                and _valid(row.get('thread'), tid, history_id)):
            metrics.record('cache.full_metadata', config_dir, hits=1)
            return row['thread']
    except (ValueError, TypeError, AttributeError):
        pass
    metrics.record('cache.full_metadata', config_dir, misses=1)
    thread = fetch(config_dir, ['gmail', 'users', 'threads', 'get', '--params',
                                json.dumps({'userId': 'me', 'id': tid, 'format': 'metadata',
                                            'metadataHeaders': HEADERS})])
    # Bind to the actual read version, not the earlier enumeration. An intervening
    # mutation makes the live result newer, never a snapshot of the old version.
    actual = thread.get('historyId') if isinstance(thread, dict) else None
    try:
        if _valid(thread, tid, actual):
            def merge(data):
                data[tid] = {'version': 1, 'headers': HEADERS, 'at': time.time(), 'thread': thread}
                keep = sorted(((k, v) for k, v in data.items()
                               if isinstance(v, dict) and isinstance(v.get('at'), (int, float))
                               and 0 <= time.time() - v['at'] < MAX_AGE),
                              key=lambda kv: kv[1]['at'], reverse=True)[:MAX_ENTRIES]
                data.clear()
                data.update(keep)
            storage.update_json(path, merge)
    except (OSError, ValueError, TypeError, AttributeError):
        pass  # cache failure must not turn a successful read into a failed view
    return thread


def histories(config_dir, query, fetch, limit=100):
    """One bounded validation page. Missing entries simply get live reads."""
    try:
        page = fetch(config_dir, ['gmail', 'users', 'threads', 'list', '--params',
                                  json.dumps({'userId': 'me', 'q': query, 'maxResults': limit})])
        return {t['id']: t['historyId'] for t in page.get('threads', [])
                if isinstance(t, dict) and t.get('id') and t.get('historyId')}
    except Exception:
        return {}
