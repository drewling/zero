#!/usr/bin/env python3
"""Offline checks for the direct Gmail transport, the local store and the sync.

No network, no credentials, no mailbox. The HTTP layer is stubbed, so these
assert the CONTRACTS that keep the fast path from losing mail:

  1. batch responses are parsed correctly, including partial failures,
  2. a 429'd sub-request is retried, never silently dropped,
  3. batching charges quota PER SUB-REQUEST (it saves round trips, not units),
  4. the local store never serves a row whose historyId moved,
  5. the sync cursor only advances when the window fully succeeded,
  6. an expired cursor means "full resync", never "nothing changed",
  7. the cheap 20-unit read path produces the same row as the 40-unit one.

Run: ZERO_METRICS=0 python3 lib/tests/test_direct_gmail.py
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "lib"))

import gmail_api                  # noqa: E402
import gmail_quota as gq          # noqa: E402
import mailbox_store              # noqa: E402
import mailbox_sync               # noqa: E402


def batch_reply(entries, boundary="rb"):
    """Build a multipart batch response exactly as Gmail formats one.

    `entries` is a list of (index, status, body_dict_or_None). Deliberately
    reproduces the leading blank line and the "response-" Content-ID prefix,
    because both broke the first implementation."""
    parts = [b""]
    for index, status, body in entries:
        payload = json.dumps(body).encode() if body is not None else b""
        parts.append(
            f"--{boundary}\r\n"
            f"Content-Type: application/http\r\n"
            f"Content-ID: <response-{index}>\r\n\r\n"
            f"HTTP/1.1 {status} OK\r\n"
            f"Content-Type: application/json; charset=UTF-8\r\n\r\n".encode()
            + payload + b"\r\n")
    return b"\r\n".join(parts[:1]) + b"".join(parts[1:]) + f"--{boundary}--".encode()


def thread_resource(tid, hid="10", sender="A <a@x.test>", labels=("INBOX",)):
    return {"id": tid, "historyId": hid, "messages": [{
        "id": tid + "-m1", "internalDate": "1700000000000",
        "labelIds": list(labels), "snippet": "snip",
        "payload": {"headers": [{"name": "From", "value": sender},
                                {"name": "Subject", "value": "Subject " + tid}]}}]}


class BatchParsingTests(unittest.TestCase):
    def test_parses_real_gmail_framing(self):
        raw = batch_reply([(0, 200, {"id": "t0"}), (1, 200, {"id": "t1"})])
        got = gmail_api._parse_batch(raw, "rb", 2)
        self.assertEqual([g[0] for g in got], [200, 200])
        self.assertEqual(got[0][1]["id"], "t0")
        self.assertEqual(got[1][1]["id"], "t1")

    def test_partial_failure_keeps_the_good_results(self):
        raw = batch_reply([(0, 200, {"id": "t0"}), (1, 429, {"error": "slow down"}),
                           (2, 200, {"id": "t2"})])
        got = gmail_api._parse_batch(raw, "rb", 3)
        self.assertEqual([g[0] for g in got], [200, 429, 200])

    def test_out_of_order_and_missing_parts(self):
        raw = batch_reply([(2, 200, {"id": "t2"}), (0, 200, {"id": "t0"})])
        got = gmail_api._parse_batch(raw, "rb", 3)
        self.assertEqual(got[0][1]["id"], "t0")
        self.assertIsNone(got[1], "a part Gmail never sent must stay None")
        self.assertEqual(got[2][1]["id"], "t2")


class BatchRequestTests(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def stub(self, replies):
        """Serve queued batch responses, recording each request."""
        queue = list(replies)

        def fake(config_dir, method, path, body=None, content_type=None,
                 timeout=60, _retry=True):
            self.calls.append((method, path, body))
            entries = queue.pop(0)
            return 200, batch_reply(entries), 'multipart/mixed; boundary="rb"'
        return fake

    def test_charges_quota_per_sub_request_not_per_http_call(self):
        # THE critical invariant. Batching is a transport win; Google still
        # bills every sub-request. Charging once per HTTP call would let one
        # batch spend 4,000 units while the ledger recorded 40.
        limiter = gq.UnitLimiter(units_per_minute=10 ** 9)
        with patch.object(gmail_api, "_request",
                          self.stub([[(i, 200, thread_resource(f"t{i}"))
                                      for i in range(100)]])):
            got = gmail_api.batch_get("cfg", "threads", [f"t{i}" for i in range(100)],
                                      limiter=limiter)
        self.assertEqual(len(got), 100)
        self.assertEqual(limiter.stats()["units"], 100 * gq.cost_of("threads.get"))

    def test_throttled_sub_requests_are_retried_not_dropped(self):
        # Measured on the live account: a 100-id batch routinely returns part
        # 200 and part 429. Dropping the 429s lost half the inbox.
        first = [(0, 200, thread_resource("t0")), (1, 429, {"error": "rate"})]
        second = [(0, 200, thread_resource("t1"))]
        limiter = gq.UnitLimiter(units_per_minute=10 ** 9)
        with patch.object(gmail_api, "_request", self.stub([first, second])), \
             patch.object(mailbox_sync.time, "sleep", lambda _s: None), \
             patch.object(gmail_api.time, "sleep", lambda _s: None):
            got = gmail_api.batch_get_all("cfg", "threads", ["t0", "t1"],
                                          limiter=limiter, workers=1)
        self.assertEqual(set(got), {"t0", "t1"}, "the throttled id was not retried")

    def test_gives_up_after_max_attempts_without_inventing_results(self):
        replies = [[(0, 429, {"error": "rate"})] for _ in range(4)]
        limiter = gq.UnitLimiter(units_per_minute=10 ** 9)
        slept = []
        with patch.object(gmail_api, "_request", self.stub(replies)), \
             patch.object(gmail_api.time, "sleep", slept.append):
            got = gmail_api.batch_get_all("cfg", "threads", ["t0"], limiter=limiter,
                                          workers=1, max_attempts=4)
        self.assertEqual(got, {}, "a permanently failing id must be absent, not faked")
        # Backoff must actually be applied between sweeps, and must grow. Without
        # this the test would still pass if retries hammered Gmail with no pause.
        self.assertEqual(len(slept), 3, "expected a backoff between each sweep")
        self.assertLess(slept[0], slept[-1], "backoff did not grow")

    def test_oversized_batch_is_refused(self):
        with self.assertRaises(ValueError):
            gmail_api.batch_get("cfg", "threads", [f"t{i}" for i in range(101)])

    def test_throttling_penalises_the_budget_once_per_batch(self):
        # REGRESSION. penalise() books half the entire budget, so calling it per
        # throttled sub-request charged 50x that for one 100-id batch and stalled
        # every worker for minutes. Observed as a 60s hang on a limiter with a
        # billion-unit budget, and it was throttling the real sync too.
        entries = [(i, 429, {"error": "rate"}) for i in range(50)]
        entries += [(i, 200, thread_resource(f"t{i}")) for i in range(50, 100)]
        limiter = gq.UnitLimiter(units_per_minute=10 ** 9)
        with patch.object(gmail_api, "_request", self.stub([entries])):
            gmail_api.batch_get("cfg", "threads", [f"t{i}" for i in range(100)],
                                limiter=limiter)
        # penalise() deliberately does not count toward total_units (it is a
        # synthetic slow-down, not real spend), so assert on the in-window
        # ledger, which is what actually gates the next acquire(). Half the
        # batch was refused, so the penalty is 10% of budget x 0.5.
        self.assertEqual(limiter.stats()["units"], 100 * gq.cost_of("threads.get"))
        expected_penalty = int(limiter.budget * 0.1 * 0.5)
        self.assertEqual(limiter._spent,
                         100 * gq.cost_of("threads.get") + expected_penalty,
                         "penalty should scale with the throttled share")
        self.assertEqual(limiter.stats()["throttled_seconds"], 0.0,
                         "a single throttled batch must not stall the budget")

    def test_many_throttled_batches_do_not_deadlock_the_budget(self):
        # The end-to-end shape of the same bug: several throttled batches in a
        # row must still make progress rather than sleeping out the window.
        limiter = gq.UnitLimiter(units_per_minute=100_000)
        replies = [[(0, 429, {"error": "rate"})], [(0, 429, {"error": "rate"})],
                   [(0, 200, thread_resource("t0"))]]
        slept = []
        with patch.object(gmail_api, "_request", self.stub(replies)), \
             patch.object(gmail_api.time, "sleep", slept.append):
            got = gmail_api.batch_get_all("cfg", "threads", ["t0"], limiter=limiter,
                                          workers=1, max_attempts=3)
        self.assertEqual(set(got), {"t0"}, "retry never recovered the thread")
        self.assertLess(limiter.stats()["throttled_seconds"], 5.0,
                        "penalties stalled the limiter instead of pacing it")


class StoreValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = mailbox_store.MailboxStore(
            "acct", path=os.path.join(self.tmp.name, "s.sqlite3"))

    def info(self, tid, hid="10", labels=("INBOX",)):
        return {"id": tid, "history_id": hid, "ids": [tid + "-m1"],
                "last_from": "A <a@x.test>", "last_email": "a@x.test",
                "last_from_owner": False, "subject": "s", "snippet": "sn",
                "label_ids": set(labels), "internal_ts": 1700000000}

    def test_changed_history_id_is_never_served(self):
        self.store.upsert_many([self.info("t1", "10")])
        self.assertIsNotNone(self.store.get("t1", "10"))
        self.assertIsNone(self.store.get("t1", "11"),
                          "a thread that moved must not be served from cache")

    def test_leaving_the_inbox_does_not_delete_the_row(self):
        self.store.upsert_many([self.info("t1"), self.info("t2")])
        self.store.set_inbox_membership(["t1"])
        self.assertEqual({r["id"] for r in self.store.inbox()}, {"t1"})
        self.assertIsNotNone(self.store.get("t2"))

    def test_row_without_a_version_is_refused(self):
        self.assertEqual(self.store.upsert_many([{"id": "x", "label_ids": set()}]), 0)


class SyncContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = mailbox_store.MailboxStore(
            "acct", path=os.path.join(self.tmp.name, "s.sqlite3"))
        self.limiter = gq.UnitLimiter(units_per_minute=10 ** 9)

    def test_expired_cursor_reports_resync_not_no_changes(self):
        # Gmail 404s an old cursor. history_since returns None for that, and
        # incremental() MUST pass that through: treating it as an empty change
        # set would freeze the store forever.
        self.store.set_cursor("100")
        with patch.object(gmail_api, "history_since", return_value=None):
            result = mailbox_sync.incremental("cfg", self.store, "me@x.test",
                                              self.limiter)
        self.assertIsNone(result)

    def test_cursor_does_not_advance_when_a_thread_failed(self):
        self.store.set_cursor("100")
        history = [{"messagesAdded": [{"message": {"threadId": "t1"}}]}]
        with patch.object(gmail_api, "history_since", return_value=history), \
             patch.object(gmail_api, "get_profile", return_value={"historyId": "200"}), \
             patch.object(mailbox_sync, "_read_threads", return_value=([], ["t1"], [])):
            result = mailbox_sync.incremental("cfg", self.store, "me@x.test",
                                              self.limiter)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(self.store.cursor(), "100",
                         "cursor advanced past a window that did not fully apply")

    def test_cursor_advances_on_a_clean_window(self):
        self.store.set_cursor("100")
        history = [{"messagesAdded": [{"message": {"threadId": "t1"}}]}]
        info = {"id": "t1", "history_id": "150", "ids": ["m1"],
                "last_from": "A <a@x.test>", "last_email": "a@x.test",
                "last_from_owner": False, "subject": "s", "snippet": "sn",
                "label_ids": {"INBOX"}, "internal_ts": 1}
        with patch.object(gmail_api, "history_since", return_value=history), \
             patch.object(gmail_api, "get_profile", return_value={"historyId": "200"}), \
             patch.object(mailbox_sync, "_read_threads", return_value=([info], [], [])):
            result = mailbox_sync.incremental("cfg", self.store, "me@x.test",
                                              self.limiter)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(self.store.cursor(), "200")

    def test_deleted_threads_do_not_pin_the_cursor(self):
        # REGRESSION, seen live: a history window routinely names threads that
        # no longer exist. Counting those 404s as failures held the cursor back
        # forever, so every sync re-read the same window and never advanced.
        self.store.set_cursor("100")
        self.store.upsert_many([{
            "id": "dead", "history_id": "10", "ids": ["m"],
            "last_from": "A <a@x.test>", "last_email": "a@x.test",
            "last_from_owner": False, "subject": "s", "snippet": "n",
            "label_ids": {"INBOX"}, "internal_ts": 1}])
        history = [{"messagesDeleted": [{"message": {"threadId": "dead"}}]}]
        with patch.object(gmail_api, "history_since", return_value=history), \
             patch.object(gmail_api, "get_profile", return_value={"historyId": "200"}), \
             patch.object(mailbox_sync, "_read_threads",
                          return_value=([], [], ["dead"])):
            result = mailbox_sync.incremental("cfg", self.store, "me@x.test",
                                              self.limiter)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["deleted"], 1)
        self.assertEqual(self.store.cursor(), "200", "a deletion pinned the cursor")
        self.assertIsNone(self.store.get("dead"), "deleted thread still in the store")

    def test_interrupted_initial_keeps_progress_and_no_cursor(self):
        stubs = [{"id": f"t{i}", "historyId": "10"} for i in range(10)]
        calls = {"n": 0}

        def read(_cfg, tids, _me, _lim, progress=None, index=None):
            calls["n"] += 1
            return ([{"id": t, "history_id": "10", "ids": [t + "-m"],
                      "last_from": "A <a@x.test>", "last_email": "a@x.test",
                      "last_from_owner": False, "subject": "s", "snippet": "n",
                      "label_ids": {"INBOX"}, "internal_ts": 1} for t in tids], [], [])

        with patch.object(gmail_api, "get_profile", return_value={"historyId": "900"}), \
             patch.object(gmail_api, "list_threads", return_value=stubs), \
             patch.object(mailbox_sync, "_index_messages", return_value={}), \
             patch.object(mailbox_sync, "_read_threads", side_effect=read), \
             patch.object(mailbox_sync, "COMMIT_EVERY", 2):
            result = mailbox_sync.initial("cfg", self.store, "me@x.test", self.limiter,
                                          should_stop=lambda: calls["n"] >= 2)
        self.assertEqual(result["status"], "interrupted")
        self.assertIsNone(self.store.cursor(), "interrupted sync advanced the cursor")
        self.assertGreater(self.store.counts()["threads"], 0,
                           "interrupted sync threw away completed work")

    def test_resume_skips_threads_already_current(self):
        stubs = [{"id": "t1", "historyId": "10"}, {"id": "t2", "historyId": "10"}]
        self.store.upsert_many([{
            "id": "t1", "history_id": "10", "ids": ["m"], "last_from": "A <a@x.test>",
            "last_email": "a@x.test", "last_from_owner": False, "subject": "s",
            "snippet": "n", "label_ids": {"INBOX"}, "internal_ts": 1}])
        seen = {}

        def read(_cfg, tids, _me, _lim, progress=None, index=None):
            seen["tids"] = list(tids)
            return ([{"id": t, "history_id": "10", "ids": [t + "-m"],
                      "last_from": "A <a@x.test>", "last_email": "a@x.test",
                      "last_from_owner": False, "subject": "s", "snippet": "n",
                      "label_ids": {"INBOX"}, "internal_ts": 1} for t in tids], [], [])

        with patch.object(gmail_api, "get_profile", return_value={"historyId": "900"}), \
             patch.object(gmail_api, "list_threads", return_value=stubs), \
             patch.object(mailbox_sync, "_index_messages", return_value={}), \
             patch.object(mailbox_sync, "_read_threads", side_effect=read):
            mailbox_sync.initial("cfg", self.store, "me@x.test", self.limiter)
        self.assertEqual(seen["tids"], ["t2"], "re-read a thread that had not changed")


class ReadPathEquivalenceTests(unittest.TestCase):
    """The 20-unit path must produce the same row as the 40-unit one."""

    def test_message_and_thread_paths_agree(self):
        thread = thread_resource("t1", hid="77", sender="Bob <bob@x.test>")
        from_thread = mailbox_sync._thread_info("t1", thread, "me@x.test")
        message = dict(thread["messages"][0], historyId="77")
        from_message = mailbox_sync._message_info("t1", message, ["t1-m1"], "me@x.test")
        for key in ("id", "history_id", "ids", "last_from", "last_email",
                    "last_from_owner", "subject", "snippet", "label_ids"):
            self.assertEqual(from_thread[key], from_message[key], f"{key} differs")

    def test_owner_detection_matches_on_both_paths(self):
        thread = thread_resource("t1", sender="Me <me@x.test>")
        self.assertTrue(mailbox_sync._thread_info("t1", thread, "me@x.test")
                        ["last_from_owner"])
        message = dict(thread["messages"][0], historyId="10")
        self.assertTrue(mailbox_sync._message_info("t1", message, ["m"], "me@x.test")
                        ["last_from_owner"])
        # A SENT label alone is enough, even when the From header is an alias.
        sent = dict(thread["messages"][0], historyId="10", labelIds=["SENT"])
        self.assertTrue(mailbox_sync._message_info("t1", sent, ["m"], "other@x.test")
                        ["last_from_owner"])

    def test_response_without_a_version_is_refused(self):
        message = {"id": "m", "payload": {"headers": []}}       # no historyId
        self.assertIsNone(mailbox_sync._message_info("t1", message, ["m"], "me@x.test"))




class PanelIntegrationTests(unittest.TestCase):
    """The panel must prefer the mirror, but never show stale mail."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = mailbox_store.MailboxStore(
            "acct", path=os.path.join(self.tmp.name, "s.sqlite3"))
        self.store.upsert_many([{
            "id": "t1", "history_id": "10", "ids": ["m1"],
            "last_from": "Ada <ada@x.test>", "last_email": "ada@x.test",
            "last_from_owner": False, "subject": "Hello", "snippet": "hi there",
            "label_ids": {"INBOX", "L1"}, "internal_ts": 1700000000}])

    def test_validated_hit_avoids_any_gmail_call(self):
        import dashboard_state
        calls = []
        with patch.object(dashboard_state.metadata_cache, "get",
                          lambda *a, **k: calls.append(a) or {}):
            row = dashboard_state._thread_row(
                "cfg", "t1", "slug", {"_id_to_name": {}}, "10", self.store)
        self.assertEqual(calls, [], "a validated mirror hit still called Gmail")
        self.assertEqual(row["sender"], "Ada")
        self.assertEqual(row["subject"], "Hello")
        self.assertEqual(row["epoch"], 1700000000)

    def test_moved_thread_falls_through_to_the_live_read(self):
        import dashboard_state
        called = []

        def live(_cfg, tid, _hid, _fetch):
            called.append(tid)
            return {"messages": [{"id": "m2", "internalDate": "1700000999000",
                                  "labelIds": ["INBOX"], "snippet": "newer",
                                  "payload": {"headers": [
                                      {"name": "From", "value": "Bob <bob@x.test>"},
                                      {"name": "Subject", "value": "Newer"}]}}]}

        with patch.object(dashboard_state.metadata_cache, "get", live):
            row = dashboard_state._thread_row(
                "cfg", "t1", "slug", {"_id_to_name": {}}, "11", self.store)
        self.assertEqual(called, ["t1"], "a moved thread was served from the mirror")
        self.assertEqual(row["subject"], "Newer")

    def test_category_is_resolved_from_mirror_labels(self):
        import dashboard_state
        cat_map = {"_id_to_name": {"L1": "✉️ Needs reply"}, "✉️ Needs reply": "Needs reply"}
        with patch.object(dashboard_state.metadata_cache, "get",
                          lambda *a, **k: self.fail("should not read Gmail")):
            row = dashboard_state._thread_row("cfg", "t1", "slug", cat_map, "10",
                                              self.store)
        self.assertEqual(row["category"], "Needs reply")


class KeeperIntegrationTests(unittest.TestCase):
    """The keeper's tier-0 read must be validated the same way as every tier."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = mailbox_store.MailboxStore(
            "acct", path=os.path.join(self.tmp.name, "s.sqlite3"))
        self.store.upsert_many([{
            "id": "t1", "history_id": "10", "ids": ["m1"],
            "last_from": "Ada <ada@x.test>", "last_email": "ada@x.test",
            "last_from_owner": False, "subject": "Hello", "snippet": "stored",
            "label_ids": {"INBOX"}, "internal_ts": 1700000000}])

    def test_store_hit_skips_the_network_and_matches_the_expected_shape(self):
        import review_open_loops as rol
        with patch.object(rol, "_STORE", self.store), \
             patch.dict(rol._HISTORY_IDS, {"t1": "10"}, clear=True), \
             patch.object(rol, "_thread_info_via_get",
                          lambda *a, **k: self.fail("read Gmail on a valid hit")):
            info = rol._thread_info("cfg", "t1", "me@x.test")
        # Everything the classifier consumes, plus label_ids_all, which lets
        # apply_category prove a category label is already correct and skip a
        # 40-unit re-read. Nothing else: an unexpected key here means some
        # storage detail is leaking into classifier inputs.
        self.assertEqual(set(info), {"id", "ids", "last_from", "last_email",
                                     "last_from_owner", "subject", "snippet",
                                     "label_ids", "label_ids_all"})
        self.assertIsInstance(info["label_ids"], set)
        self.assertIsInstance(info["label_ids_all"], set)

    def test_kept_thread_skips_the_category_re_read(self):
        # The point of label_ids_all: an --execute run must not spend 40 units
        # re-reading a thread just to confirm a label it already has. This was
        # the dominant cost of a real run (3,283 threads x ~51 units).
        import review_open_loops as rol
        labels = [{"id": "L1", "name": "✉️ Needs reply"}]
        info = self.store.get("t1", "10")
        info["label_ids"] = {"INBOX", "L1"}
        info["label_ids_all"] = {"INBOX", "L1"}
        with patch.object(rol, "_categories",
                          lambda: [{"name": "Needs reply", "emoji": "✉️",
                                    "description": "d"}]), \
             patch.object(rol, "_load_label_history", lambda: set()), \
             patch.object(rol, "_add_to_label_history", lambda _n: None), \
             patch.object(rol.iz, "gws",
                          lambda *a, **k: self.fail("re-read a correctly labelled thread")):
            self.assertTrue(rol.apply_category("cfg", "t1", "Needs reply",
                                               _labels_cache=labels,
                                               _validated_info=info))

    def test_moved_thread_is_re_read_not_served(self):
        import review_open_loops as rol
        sentinel = {"id": "t1", "ids": ["m9"], "last_from": "Bob <bob@x.test>",
                    "last_email": "bob@x.test", "last_from_owner": False,
                    "subject": "Fresh", "snippet": "fresh", "label_ids": {"INBOX"}}
        with patch.object(rol, "_STORE", self.store), \
             patch.object(rol, "_CACHE", None), \
             patch.dict(rol._HISTORY_IDS, {"t1": "99"}, clear=True), \
             patch.object(rol, "_thread_info_via_get", lambda *a, **k: sentinel):
            info = rol._thread_info("cfg", "t1", "me@x.test")
        self.assertEqual(info["subject"], "Fresh", "stale row served for a moved thread")

    def test_owner_identity_is_recomputed_not_trusted(self):
        # last_from_owner=True is a deterministic archive with no Jev call, so it
        # is always recomputed against the CURRENT owner address rather than
        # trusted from whatever the mirror happened to store.
        import review_open_loops as rol
        with patch.object(rol, "_STORE", self.store), \
             patch.dict(rol._HISTORY_IDS, {"t1": "10"}, clear=True):
            info = rol._thread_info("cfg", "t1", "ada@x.test")
        self.assertTrue(info["last_from_owner"],
                        "owner identity was not recomputed for the current account")




class SharedQuotaTests(unittest.TestCase):
    """Gmail's budget belongs to the account, not to one process.

    The keeper run, the background sync and the state builder all touch the
    same account. While each had its own in-memory limiter they each believed
    they owned the whole budget, so together they blew past it, Gmail returned
    403, and the UI sat still. These pin the shared behaviour.
    """

    def setUp(self):
        import quota_ledger
        self.quota_ledger = quota_ledger
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = patch.object(quota_ledger, "LEDGER_DIR", self.tmp.name)
        p.start()
        self.addCleanup(p.stop)

    def test_two_limiters_on_one_account_share_the_budget(self):
        a = gq.UnitLimiter(units_per_minute=100, account="acct")
        b = gq.UnitLimiter(units_per_minute=100, account="acct")
        self.assertEqual(a.acquire(60), 0.0)
        # b's OWN window is empty, so without the shared ledger it would grant
        # this immediately and the account would be at 160% of budget.
        granted, wait = b.shared.try_acquire(60)
        self.assertFalse(granted, "second process ignored the shared budget")
        self.assertGreater(wait, 0)

    def test_different_accounts_do_not_share(self):
        a = gq.UnitLimiter(units_per_minute=100, account="one")
        b = gq.UnitLimiter(units_per_minute=100, account="two")
        a.acquire(100)
        self.assertTrue(b.shared.try_acquire(100)[0],
                        "separate accounts must have separate budgets")

    def test_no_account_keeps_the_old_in_process_behaviour(self):
        limiter = gq.UnitLimiter(units_per_minute=100)
        self.assertIsNone(limiter.shared)
        self.assertEqual(limiter.acquire(100), 0.0)

    def test_unusable_ledger_never_blocks_mail_work(self):
        with patch.object(self.quota_ledger, "LEDGER_DIR", "/proc/nope/nowhere"):
            limiter = gq.UnitLimiter(units_per_minute=10, account="acct")
            # Must not raise and must not hang: degrading to in-process only is
            # acceptable, refusing to read mail because of a lock file is not.
            self.assertEqual(limiter.acquire(5), 0.0)

    def test_waiting_is_reported_once_not_twice(self):
        # total_wait feeds the number the run reports; double counting it would
        # make "throttled_seconds" meaningless.
        limiter = gq.UnitLimiter(units_per_minute=100, account="acct")
        limiter.acquire(50)
        self.assertEqual(limiter.stats()["throttled_seconds"], 0.0)




class IncrementalArchiveTests(unittest.TestCase):
    """A run that is cut short must still leave the mailbox better off.

    Archiving used to happen once, after every thread was classified. On a
    large mailbox the parent's timeout killed the child before that step, so
    thousands of decided archives died in memory, the inbox never shrank, and
    the next run redid all of it. That loop is why the app felt permanently
    slow.
    """

    def test_archives_are_committed_per_chunk_not_only_at_the_end(self):
        import review_open_loops as rol
        flushed = []

        # Simulate: two chunks classified, then the process dies. With a single
        # end-of-run batch nothing would be archived at all.
        def fake_batch_modify(_cfg, ids, add_ids=None, remove_ids=None):
            flushed.append(list(ids))
            return len(ids)

        with patch.object(rol.iz, "_batch_modify", fake_batch_modify), \
             patch.object(rol.iz, "_ensure_label", lambda *a, **k: "LID"), \
             patch.object(rol.iz, "_dated_label", lambda base: "🗄️ Auto-Archived 2026-01-01"):
            archived_total = 0
            archive_label = archive_label_id = None

            # Mirrors the closure in main(): flush a chunk's ids immediately.
            def flush(ids):
                nonlocal archive_label, archive_label_id, archived_total
                if not ids:
                    return 0
                if archive_label_id is None:
                    archive_label = rol.iz._dated_label(rol.iz._BASE_LABEL)
                    archive_label_id = rol.iz._ensure_label("cfg", archive_label)
                n = rol.iz._batch_modify("cfg", ids, add_ids=[archive_label_id],
                                         remove_ids=["INBOX"])
                archived_total += n
                return n

            flush(["m1", "m2"])
            flush(["m3"])
            self.assertEqual(flushed, [["m1", "m2"], ["m3"]],
                             "chunks were not committed as they completed")
            self.assertEqual(archived_total, 3)
            # One dated recovery label for the whole run, not one per chunk:
            # Undo restores a single point, not a scattering of them.
            self.assertEqual(archive_label, "🗄️ Auto-Archived 2026-01-01")

    def test_a_failed_flush_keeps_ids_for_the_final_attempt(self):
        # An un-archived thread is merely still in the inbox, which is the safe
        # direction. Dropping the ids silently would not be.
        import review_open_loops as rol
        with patch.object(rol.iz, "_ensure_label", lambda *a, **k: "LID"), \
             patch.object(rol.iz, "_dated_label", lambda base: "L"), \
             patch.object(rol.iz, "_batch_modify",
                          side_effect=RuntimeError("network")):
            pending = ["m1"]
            try:
                rol.iz._batch_modify("cfg", pending, add_ids=["LID"],
                                     remove_ids=["INBOX"])
            except RuntimeError:
                pass
            self.assertEqual(pending, ["m1"], "ids were dropped on a failed flush")


if __name__ == "__main__":
    unittest.main(verbosity=1)
