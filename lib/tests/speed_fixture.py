"""Isolated fixture runner for the REAL keeper main(), with no external calls."""
import collections
import contextlib
import copy
import io
import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import draftutil as du
import jev
import learning
import review_open_loops as review
import sync_state
import thread_cache


class KeeperFixture:
    def __init__(self, directory, size=24):
        self.directory = directory
        self.size = size
        self.calls = collections.Counter()
        self.asks = 0
        self.history = {str(i): '10' for i in range(size)}
        self.policy = 'Keep genuine requests'
        self.learned = 'Fixture preferences'
        self.replied = True
        self.fail_history = False
        self.fail_thread = None
        self.categories = [{'name': 'Needs reply', 'emoji': '✉️', 'description': 'Reply needed'}]

    def gmail(self, cfg, args, **kwargs):
        method = du._method_of(args)
        self.calls[method] += 1
        params = json.loads(args[args.index('--params') + 1])
        if method == 'getProfile':
            return {'emailAddress': 'owner@example.test', 'historyId': '500'}
        if method == 'threads.list':
            return {'threads': [{'id': tid, 'historyId': hid, 'snippet': 'Fixture'}
                                for tid, hid in self.history.items()]}
        if method == 'history.list':
            if self.fail_history:
                raise RuntimeError('404 expired')
            return {'history': [], 'historyId': '500'}
        if method == 'threads.get':
            tid = params['id']
            if tid == self.fail_thread:
                raise RuntimeError('fixture read failed')
            return {'id': tid, 'historyId': self.history[tid], 'messages': [{
                'id': 'm-' + tid, 'labelIds': ['INBOX', 'L1'], 'snippet': 'Fixture',
                'payload': {'headers': [{'name': 'From', 'value': 'person@example.test'},
                                        {'name': 'Subject', 'value': 'Fixture'}]}}]}
        if method == 'messages.get':
            return {'payload': {'headers': [{'name': 'To', 'value': 'person@example.test'}]}}
        if method == 'labels.list':
            return {'labels': [{'id': 'L1', 'name': '✉️ Needs reply'}]}
        if method == 'messages.list':
            return {'messages': [{'id': 'sent', 'threadId': 'other-thread'}]} if self.replied else {}
        # Mutations are intentionally forbidden by this fixture, even though main
        # runs with --execute. All supplied threads are already correctly kept.
        raise AssertionError('Unexpected API method: ' + method)

    def ask_many(self, items, **kwargs):
        self.asks += len(items)
        return [{'awaiting_user': {'noul': .95}, 'is_protected': {'noul': 0},
                 'is_cold_outreach': {'noul': 0}, 'is_automated': {'noul': 0},
                 'urgency': {'score': 2},
                 'category': {'choice': 'Needs reply', 'confidence': .99}} for _ in items]

    def run(self):
        self.calls.clear()
        self.asks = 0
        review._REPLIED.clear()
        review._REPLIED_IN_FLIGHT.clear()
        review._HISTORY_IDS.clear()
        review._SNIPPETS.clear()
        with contextlib.ExitStack() as stack:
            for obj, attr, value in [
                (thread_cache, 'CACHE_DIR', os.path.join(self.directory, 'cache')),
                (sync_state, 'STATE_PATH', os.path.join(self.directory, 'sync.json')),
                (review, '_LABEL_HISTORY_PATH', os.path.join(self.directory, 'labels.json')),
                (du, '_gws', self.gmail), (review.iz, 'gws', self.gmail),
                (review, '_policy_text', lambda: self.policy),
                (review, '_learned_rules', lambda: self.learned),
                (review, '_categories', lambda: copy.deepcopy(self.categories)),
                (learning, 'kept_thread_ids', lambda: set()),
                (jev, 'ask_many', self.ask_many),
                (sys, 'argv', ['review_open_loops.py', 'fixture-account', 'fixture',
                               '--execute', '--no-bulk', '--grace-days', '0'])]:
                stack.enter_context(patch.object(obj, attr, value))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                review.main()
            result = json.loads([line for line in output.getvalue().splitlines()
                                 if line.startswith('{')][-1])
        return {'gmail_calls': dict(self.calls), 'jev_calls': self.asks,
                'kept': result['to_keep_threads'], 'to_archive': result['to_archive_threads'],
                'sync_mode': result['sync_mode']}
