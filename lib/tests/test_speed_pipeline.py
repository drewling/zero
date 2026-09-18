#!/usr/bin/env python3
"""Offline pipeline acceptance fixtures: exact reuse, failures and real file locks.

No gws, real provider, mailbox mutation, credentials, or personal fixtures.
Run: ZERO_METRICS=0 python3 lib/tests/test_speed_pipeline.py
"""
import concurrent.futures
import copy
import http.client
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import catchup
import dashboard_state as dashboard
import draftutil as du
import jev
import keeper_server as keeper
import learn
import learning
import metadata_cache as metadata
import review_open_loops as review
import run_metrics
import runtime_state as storage
import sync_state
import thread_cache


def thread(tid='t', hid='10', sender='Person <person@example.test>'):
    return {'id': tid, 'historyId': hid, 'messages': [{
        'id': 'm-' + tid, 'internalDate': '1700000000000', 'labelIds': ['INBOX'],
        'snippet': 'synthetic message', 'payload': {'headers': [
            {'name': 'From', 'value': sender}, {'name': 'Subject', 'value': 'Synthetic'},
            {'name': 'Date', 'value': 'Tue, 14 Nov 2023 22:13:20 +0000'}]}}]}


def info(tid):
    return {'id': tid, 'ids': ['m-' + tid], 'last_from': 'Sender <s@example.test>',
            'last_email': 's@example.test', 'last_from_owner': False,
            'subject': 'Synthetic', 'snippet': 'Fixture', 'label_ids': {'INBOX'}}


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.edits = [{'type': 'draft_edit', 'original_snippet': 'original', 'final': 'short'}] * 2
        self.signals = copy.deepcopy(self.edits)
        self.rejected = set()
        self.calls = 0
        for obj, name, value in [(learning, 'LEARN_DIR', self.tmp.name),
                                 (learning, 'REJECTED', os.path.join(self.tmp.name, 'rejected.jsonl')),
                                 (learning, 'LEARNED', os.path.join(self.tmp.name, 'learned.md'))]:
            p = patch.object(obj, name, value)
            p.start()
            self.addCleanup(p.stop)
        for p in [patch.object(learning, 'recent', lambda n: copy.deepcopy(self.signals)),
                  patch.object(learn, '_rejected_norms', lambda: set(self.rejected)),
                  patch.object(learn._llm, '_active_provider_name', lambda: 'claude'),
                  patch.object(learn._llm, 'run_prompt', self.generate),
                  patch.object(sys, 'argv', ['learn.py'])]:
            p.start()
            self.addCleanup(p.stop)

    def generate(self, *args, **kwargs):
        self.calls += 1
        return '## Draft voice\n- Be concise\n- Be warm', True

    def text(self):
        with open(learning.LEARNED) as f:
            return f.read()

    def test_exact_warm_skip_and_same_count_edit(self):
        learn.main()
        before = (self.text(), os.stat(learning.LEARNED).st_mtime_ns)
        learn.main()
        self.assertEqual(self.calls, 1)
        self.assertEqual((self.text(), os.stat(learning.LEARNED).st_mtime_ns), before)
        self.signals[0]['final'] = 'changed at same count'
        learn.main()
        self.assertEqual(self.calls, 2)

    def test_rules_and_rejections_reuse_voice_without_stale_preferences(self):
        learn.main()
        self.signals.append({'type': 'keep_override_undo', 'subject': 'Keep fixture'})
        learn.main()
        self.assertIn('Keep fixture', self.text())
        self.assertEqual(self.calls, 1)
        self.rejected = {'be concise'}
        learn.main()
        self.assertNotIn('Be concise', self.text())
        self.rejected = {'be warm'}  # same count, different rejection
        learn.main()
        self.assertIn('Be concise', self.text())
        self.assertNotIn('Be warm', self.text())
        self.assertEqual(self.calls, 1)

    def test_manual_edit_preserved_on_unchanged_inputs(self):
        learn.main()
        storage.atomic_text(learning.LEARNED, 'User authored note')
        learn.main()
        self.assertEqual(self.text(), 'User authored note')
        self.assertEqual(self.calls, 1)

    def test_failed_generation_is_retried_and_never_published(self):
        with patch.object(learn._llm, 'run_prompt', return_value=('', False)):
            learn.main()
        self.assertFalse(os.path.exists(learning.LEARNED))
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, 'rollup-inputs.json')))
        learn.main()
        self.assertEqual(self.calls, 1)

    def test_concurrent_rollups_only_generate_once(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            list(ex.map(lambda _: learn.main(), range(4)))
        self.assertEqual(self.calls, 1)
        self.assertIn('Draft voice', self.text())

    def test_missing_output_rebuilds_and_provider_change_invalidates(self):
        learn.main()
        os.unlink(learning.LEARNED)
        learn.main()
        self.assertTrue(os.path.exists(learning.LEARNED))
        self.assertEqual(self.calls, 1)
        with patch.object(learn._llm, '_active_provider_name', return_value='codex'):
            learn.main()
        self.assertEqual(self.calls, 2)

    def test_real_rejection_during_generation_cannot_be_republished(self):
        entered, release = threading.Event(), threading.Event()
        def slow(*args, **kwargs):
            entered.set()
            if not release.wait(3):
                raise AssertionError('fixture generation stalled')
            return '## Draft voice\n- Be concise\n- Be warm', True
        def rejected():
            if not os.path.exists(learning.REJECTED):
                return set()
            with open(learning.REJECTED) as f:
                return {json.loads(line)['norm'] for line in f if line.strip()}
        with patch.object(learn._llm, 'run_prompt', slow), \
             patch.object(learn, '_rejected_norms', rejected):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(learn.main)
                self.assertTrue(entered.wait(2))
                learning.reject_learning('Be concise')  # must not await the LLM
                release.set()
                future.result(timeout=3)
            self.assertFalse(os.path.exists(learning.LEARNED))
            learn.main()  # successful voice is reused, newest rejection is applied
            self.assertNotIn('Be concise', self.text())
            self.assertIn('Be warm', self.text())


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = patch.object(metadata, 'CACHE_DIR', self.tmp.name)
        p.start()
        self.addCleanup(p.stop)
        self.calls = []
        self.value = thread()

    def fetch(self, cfg, args):
        self.calls.append(args)
        return copy.deepcopy(self.value)

    def test_cold_warm_equivalence_and_missing_history(self):
        cold = metadata.get('account', 't', '10', self.fetch)
        warm = metadata.get('account', 't', '10', self.fetch)
        self.assertEqual(cold, warm)
        self.assertEqual(len(self.calls), 1)
        metadata.get('account', 't', None, self.fetch)
        self.assertEqual(len(self.calls), 2)

    def test_changed_mail_and_account_isolation(self):
        metadata.get('account', 't', '10', self.fetch)
        self.value = thread(hid='11', sender='Owner <owner@example.test>')
        changed = metadata.get('account', 't', '11', self.fetch)
        self.assertIn('Owner', changed['messages'][0]['payload']['headers'][0]['value'])
        metadata.get('different-account', 't', '11', self.fetch)
        self.assertEqual(len(self.calls), 3)

    def test_no_stale_fallback_after_failed_read(self):
        metadata.get('account', 't', '10', self.fetch)
        with self.assertRaises(RuntimeError):
            metadata.get('account', 't', '11', lambda *a: (_ for _ in ()).throw(RuntimeError('offline')))

    def test_corrupt_and_wrong_shape_fall_back(self):
        metadata.get('account', 't', '10', self.fetch)
        path = os.path.join(self.tmp.name, storage.account_id('account') + '.json')
        storage.atomic_text(path, '{bad')
        metadata.get('account', 't', '10', self.fetch)
        storage.atomic_text(path, json.dumps({'t': {'version': 1, 'headers': metadata.HEADERS,
                                                  'at': 'not-a-number'}}))
        metadata.get('account', 't', '10', self.fetch)
        self.assertEqual(len(self.calls), 3)

    def test_dashboard_to_catchup_full_thread_equivalence(self):
        # Crucially, an earlier owner message suppresses catch-up despite an
        # external last sender. Newest-message classifier caches cannot prove this.
        self.value['messages'].insert(0, thread(sender='Owner <owner@example.test>')['messages'][0])
        with patch.object(du, '_gws', self.fetch):
            cold_row = dashboard._thread_row('account', 't', 'slug', history_id='10')
            warm_row = dashboard._thread_row('account', 't', 'slug', history_id='10')
        self.assertEqual(cold_row, warm_row)
        count = len(self.calls)
        def gmail(cfg, args):
            method = '.'.join(args[2:4])
            if method == 'messages.list':
                return {'messages': [{'id': 'm-t', 'threadId': 't'}]}
            if method == 'threads.list':
                return {'threads': [{'id': 't', 'historyId': '10'}]}
            return self.fetch(cfg, args)
        with patch.object(du, '_gws', gmail):
            self.assertEqual(catchup.candidates('account', 'owner@example.test', 14), [])
        self.assertEqual(len(self.calls), count, 'catch-up should reuse the full-thread response')

    def test_read_version_not_enumeration_version_is_stored(self):
        self.value['historyId'] = '11'
        metadata.get('account', 't', '10', self.fetch)
        metadata.get('account', 't', '10', self.fetch)
        self.assertEqual(len(self.calls), 2)
        metadata.get('account', 't', '11', self.fetch)
        self.assertEqual(len(self.calls), 2)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_real_processes_merge_without_lost_updates(self):
        path = os.path.join(self.tmp.name, 'shared.json')
        code = ('import sys; from runtime_state import update_json; '
                'update_json(sys.argv[1], lambda d: d.update({sys.argv[2]: True}))')
        env = dict(os.environ, PYTHONPATH=os.path.dirname(os.path.dirname(__file__)), ZERO_METRICS='0')
        processes = [subprocess.Popen([sys.executable, '-c', code, path, str(i)], env=env)
                     for i in range(12)]
        self.assertEqual([p.wait(timeout=10) for p in processes], [0] * 12)
        self.assertEqual(len(storage.read_json(path)), 12)

    def test_thread_cache_concurrent_merges_and_tombstones(self):
        path = os.path.join(self.tmp.name, 'cache.json')
        caches = [thread_cache.load('fixture', path=path) for _ in range(12)]
        for i, c in enumerate(caches):
            c.put_thread(str(i), '10', info(str(i)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            self.assertTrue(all(ex.map(lambda c: c.save(), caches)))
        current = thread_cache.load('fixture', path=path)
        self.assertEqual(current.stats()['threads'], 12)
        older = thread_cache.load('fixture', path=path)
        current.forget_thread('0')
        current.save()
        older.put_thread('new', '10', info('new'))
        older.save()
        self.assertIsNone(thread_cache.load('fixture', path=path).thread_info('0', '10'))

    def test_negative_sender_not_reused_across_runs(self):
        path = os.path.join(self.tmp.name, 'cache.json')
        cache = thread_cache.load('fixture', path=path)
        cache.put_replied('person@example.test', False)
        self.assertIs(cache.replied_before('person@example.test'), False)
        cache.save()
        self.assertIsNone(thread_cache.load('fixture', path=path).replied_before('person@example.test'))

    def test_cursor_expiry_partial_failure_and_concurrent_accounts(self):
        path = os.path.join(self.tmp.name, 'sync.json')
        with patch.object(sync_state, 'STATE_PATH', path):
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                self.assertTrue(all(ex.map(lambda i: sync_state.save(str(i), str(i + 100)), range(8))))
            self.assertEqual(len(storage.read_json(path)), 8)
            sync_state.clear('0')
            self.assertIsNone(sync_state.load('0'))
            self.assertEqual(sync_state.load('1'), '101')
        def expired(_):
            raise RuntimeError('404 expired')
        self.assertEqual(sync_state.changed_threads(expired, '100'), (None, 'expired'))
        pages = iter([{'history': [{'messages': [{'threadId': 'a'}]}], 'nextPageToken': 'next'}, None])
        self.assertEqual(sync_state.changed_threads(lambda _: next(pages), '100'), (None, 'error'))

    def test_write_failure_keeps_old_document(self):
        path = os.path.join(self.tmp.name, 'state.json')
        storage.atomic_text(path, 'old')
        with patch.object(storage.os, 'replace', side_effect=OSError('fixture failure')):
            with self.assertRaises(OSError):
                storage.atomic_text(path, 'new')
        with open(path) as f:
            self.assertEqual(f.read(), 'old')
        self.assertEqual(os.listdir(self.tmp.name), ['state.json'])


class ProcessAndMetricsTests(unittest.TestCase):
    def test_app_drains_large_stderr_and_reaps_timeout(self):
        command = [sys.executable, '-c',
                   'import sys; sys.stderr.write("e" * 2000000); '
                   'sys.stderr.flush(); print("\\x1fP\\x1f50\\x1fworking"); print("{}")']
        with patch.object(keeper, '_set_job_message') as progress:
            rc, output, errors = keeper._run_child(command, 0, 80, 10)
            self.assertEqual(rc, 0)
            self.assertEqual(output.strip(), '{}')
            self.assertLessEqual(len(errors), 256 * 4096)
            progress.assert_called_once_with('working', 40)
        rc, _, error = keeper._run_child([sys.executable, '-c', 'import time; time.sleep(5)'], 0, 1, .1)
        self.assertEqual((rc, error), (1, 'timed out'))
        started = time.monotonic()
        rc, _, error = keeper._run_child([sys.executable, '-c',
                'import sys,time; sys.stdout.write("partial"); sys.stdout.flush(); time.sleep(5)'],
                0, 1, .1)
        self.assertEqual((rc, error), (1, 'timed out'))
        self.assertLess(time.monotonic() - started, 1.5)

    def test_scheduled_stage_failure_reaches_exit_code(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            shutil.copy(os.path.join(root, 'run.sh'), os.path.join(tmp, 'run.sh'))
            os.mkdir(os.path.join(tmp, 'lib'))
            shutil.copy(storage.__file__, os.path.join(tmp, 'lib', 'runtime_state.py'))
            accounts = os.path.join(tmp, 'accounts.json')
            storage.atomic_text(accounts, json.dumps([{'config_dir': 'fixture', 'email': 'fixture'}]))
            import shlex
            config = {'MAIL_TRIAGE_DIR': tmp, 'MAIL_TRIAGE_LIB': os.path.join(tmp, 'lib'),
                      'MAIL_TRIAGE_PYTHON': sys.executable, 'MAIL_TRIAGE_ACCOUNTS': accounts,
                      'MAIL_TRIAGE_LOGS': os.path.join(tmp, 'logs')}
            storage.atomic_text(os.path.join(tmp, 'config.sh'),
                                '\n'.join(k + '=' + shlex.quote(v) for k, v in config.items()))
            for name in ('demote_automated', 'review_open_loops', 'learn', 'dashboard_state', 'missed_sweep'):
                storage.atomic_text(os.path.join(tmp, 'lib', name + '.py'),
                                    'raise SystemExit(' + ('7' if name == 'demote_automated' else '0') + ')')
            result = subprocess.run(['/bin/bash', os.path.join(tmp, 'run.sh')], timeout=10,
                                    capture_output=True, env=dict(os.environ, ZERO_METRICS='0'))
            self.assertEqual(result.returncode, 1)
            with open(os.path.join(tmp, 'logs', 'latest.log')) as f:
                self.assertIn('demote_automated failed', f.read())

    def test_account_quotas_independent_and_people_not_charged(self):
        with patch.object(du, '_account_limiters', {}):
            du._await_quota(['gmail', 'users', 'getProfile'], 'account-one')
            du._await_quota(['gmail', 'users', 'getProfile'], 'account-two')
            self.assertEqual(len(du._account_limiters), 2)
            self.assertEqual([l.total_units for l in du._account_limiters.values()], [1, 1])
            du._await_quota(['people', 'people', 'get'], 'account-one')
            self.assertEqual([l.total_units for l in du._account_limiters.values()], [1, 1])

    def test_metrics_exclude_private_input_and_include_failed_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'metrics.jsonl')
            with patch.dict(os.environ, ZERO_METRICS='1', ZERO_METRICS_PATH=path), \
                 patch.object(run_metrics, '_rows', __import__('collections').defaultdict(
                     lambda: __import__('collections').defaultdict(float))), \
                 patch.object(du.subprocess, 'run', return_value=subprocess.CompletedProcess(
                     [], 1, '', '401 secret@example.test private-body')):
                with self.assertRaises(RuntimeError):
                    du._gws('/private/account@example.test', ['gmail', 'users', 'messages', 'get',
                            '--params', '{"id":"secret-mail-id"}'])
                run_metrics.report()
            with open(path) as f:
                raw = f.read()
            for forbidden in ('secret-mail-id', 'private-body', '/private/', 'account@example.test'):
                self.assertNotIn(forbidden, raw)
            row = json.loads(raw)['rows'][0]
            self.assertEqual(row['calls'], 1)
            self.assertEqual(row['command_failures'], 1)
            self.assertEqual(row['quota_units_estimated'], 20)


class ConnectionTests(unittest.TestCase):
    def test_real_http11_socket_reuse_and_server_close(self):
        # Real local TCP/HTTP framing, substituting only TLS creation. No external
        # network or credentials. TLS verification itself stays stdlib's default.
        seen = []
        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'
            def log_message(self, *args):
                pass
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                seen.append(self.client_address[1])
                output = json.dumps({'answers': body['questions']}).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(output)))
                if body.get('close'):
                    self.send_header('Connection', 'close')
                self.end_headers()
                self.wfile.write(output)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        pool = __import__('queue').LifoQueue(maxsize=12)
        try:
            with patch.object(jev, 'ENDPOINT', f'https://127.0.0.1:{server.server_port}/v1'), \
                 patch.object(jev, '_pool', pool), \
                 patch.object(jev.urllib.request, 'getproxies', return_value={}), \
                 patch.object(jev.http.client, 'HTTPSConnection', http.client.HTTPConnection):
                for i in range(4):
                    status, parsed, _ = jev._post({'questions': {'i': i}, 'close': i == 2}, 'fixture', 2)
                    self.assertEqual(status, 200)
                    self.assertEqual(parsed['answers'], {'i': i})
                self.assertEqual(seen[0], seen[1])
                self.assertEqual(seen[1], seen[2])
                self.assertNotEqual(seen[2], seen[3])
        finally:
            while not pool.empty():
                pool.get()[1].close()
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_failed_socket_dropped_and_proxy_fallback(self):
        from unittest.mock import MagicMock
        conn = MagicMock()
        conn.request.side_effect = OSError('stale connection')
        pool = __import__('queue').LifoQueue(maxsize=12)
        with patch.object(jev, '_pool', pool), \
             patch.object(jev.urllib.request, 'getproxies', return_value={}), \
             patch.object(jev.http.client, 'HTTPSConnection', return_value=conn):
            with self.assertRaises(OSError):
                jev._post({}, 'fixture', 1)
            conn.close.assert_called_once()
            self.assertTrue(pool.empty())
        with patch.object(jev.urllib.request, 'getproxies', return_value={'https': 'fixture'}), \
             patch.object(jev, '_post_unpooled', return_value=(200, {}, '{}')) as fallback:
            self.assertEqual(jev._post({}, 'fixture', 1)[0], 200)
            fallback.assert_called_once()


class KeeperExecutionTests(unittest.TestCase):
    def test_full_execute_cold_warm_and_changed_inputs(self):
        from speed_fixture import KeeperFixture
        with tempfile.TemporaryDirectory() as directory:
            f = KeeperFixture(directory, size=12)
            cold, warm = f.run(), f.run()
            self.assertEqual((cold['kept'], warm['kept']), (12, 12))
            self.assertEqual(warm['jev_calls'], 0)
            self.assertEqual(warm['gmail_calls'].get('threads.get', 0), 0)
            self.assertEqual(warm['gmail_calls'].get('threads.modify', 0), 0)
            f.policy += ' changed'
            self.assertEqual(f.run()['jev_calls'], 12)
            f.learned += ' changed'
            self.assertEqual(f.run()['jev_calls'], 12)
            f.history['0'] = '11'
            changed = f.run()
            self.assertEqual(changed['jev_calls'], 1)
            self.assertEqual(changed['gmail_calls'].get('threads.get'), 1)
            f.fail_history = True
            expired = f.run()
            self.assertEqual(expired['kept'], 12)
            self.assertEqual(expired['sync_mode'], 'full')
            f.history['0'] = '12'
            f.fail_thread = '0'
            failed = f.run()
            self.assertEqual(failed['to_archive'], 0)
            self.assertEqual(failed['kept'], 11)

    def test_shared_label_map_creation_and_intersection_guard(self):
        labels = []
        calls = []
        def gmail(cfg, args, **kwargs):
            method = du._method_of(args)
            calls.append(method)
            if method == 'threads.get':
                return {'messages': [{'id': 'a', 'labelIds': []}, {'id': 'b', 'labelIds': ['L1']}]}
            if method == 'labels.create':
                return {'id': 'L1'}
            if method == 'threads.modify':
                return {}
            raise AssertionError(method)
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(review, '_LABEL_HISTORY_PATH', os.path.join(tmp, 'history.json')), \
             patch.object(review, '_categories', return_value=[{'name': 'Reply', 'emoji': 'X'}]), \
             patch.object(review.iz, 'gws', gmail):
            partial = dict(info('t'), label_ids={'L1'}, label_ids_all=set())
            self.assertTrue(review.apply_category('cfg', 't', 'Reply', labels, partial))
            self.assertTrue(review.apply_category('cfg', 'u', 'Reply', labels, partial))
            self.assertEqual(calls.count('labels.create'), 1)
            self.assertEqual(calls.count('threads.modify'), 2,
                             'union-only labels cannot skip labeling the other message')
            calls.clear()
            complete = dict(info('t'), label_ids={'L1'}, label_ids_all={'L1'})
            self.assertTrue(review.apply_category('cfg', 't', 'Reply', labels, complete))
            self.assertEqual(calls, [], 'exactly current labels should skip all per-thread calls')

    def test_cursor_corruption_and_error_payload_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(sync_state, 'STATE_PATH', os.path.join(tmp, 'sync.json')):
            for value in ['wrong', {'history_id': '1', 'updated_at': 'wrong'},
                          {'history_id': '1', 'updated_at': time.time() + 100}]:
                storage.atomic_text(sync_state.STATE_PATH, json.dumps({'account': value}))
                self.assertIsNone(sync_state.load('account'))
        for page in [{'error': 'failure'}, {'history': [None]}, {'history': 'wrong'}]:
            self.assertEqual(sync_state.changed_threads(lambda _: page, '1'), (None, 'error'))


if __name__ == '__main__':
    unittest.main()
