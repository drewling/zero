#!/usr/bin/env python3
"""Runnable check for the optimistic per-item ops in keeper_server.py (_dismiss,
_undo_thread): the HTTP response must return before the slow Gmail write completes,
the cached state must be updated optimistically, a failed background write must roll
the state back, and the learning signal must be recorded exactly once (and only on
success). No network — the Gmail layer (draftutil._gws / inbox_zero._ensure_label)
is stubbed. Run: python3 lib/tests/test_optimistic_ops.py
"""
import json, os, sys, tempfile, threading, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import keeper_server as ks   # noqa: E402
import draftutil as du       # noqa: E402
import inbox_zero as iz      # noqa: E402
import learning              # noqa: E402

SLOW_WRITE_S = 0.6


def _fresh_state(tmp):
    """Point keeper_server at a scratch state.json with one account/loop."""
    ks.STATE_PATH = os.path.join(tmp, "state.json")
    ks._STATE_LOCK_PATH = ks.STATE_PATH + ".lock"
    state = {
        "accounts": [{
            "slug": "acct1", "ok": True, "inbox_threads": 1,
            "loops": [{"thread_id": "t1", "sender": "Jane", "sender_email": "jane@x.com",
                      "subject": "Hi", "snippet": "...", "epoch": 100,
                      "account_slug": "acct1"}],
            "undo_points": [],
        }],
        "total_loops": 1,
    }
    with open(ks.STATE_PATH, "w") as f:
        json.dump(state, f)
    return ks.STATE_PATH


def _read_state():
    with open(ks.STATE_PATH) as f:
        return json.load(f)


def _loop_ids(st, slug="acct1"):
    a = next(a for a in st["accounts"] if a["slug"] == slug)
    return [l["thread_id"] for l in a.get("loops", [])]


class _StubGws:
    """Records calls, sleeps SLOW_WRITE_S to simulate the real ~0.6s Gmail round-trip,
    and can be told to fail on the next call."""
    def __init__(self):
        self.calls = []
        self.fail_next = False
        self.delay = SLOW_WRITE_S

    def __call__(self, config_dir, args, allow_empty=False, _retries=3):
        self.calls.append(args)
        time.sleep(self.delay)
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("simulated Gmail failure")
        if args[:3] == ["gmail", "users", "labels"] and args[2] not in ("list", "get", "delete"):
            return {"id": "LID"}
        if args[:3] == ["gmail", "users", "labels", "list"]:
            return {"labels": [{"id": "LID", "name": "🗄️ Auto-Archived 2026-09-17"}]}
        return {}


def _wait_for(cond, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if cond():
            return True
        time.sleep(0.02)
    return False


def main():
    orig_acct = ks._acct
    orig_gws = du._gws
    orig_ensure = iz._ensure_label
    orig_dated = iz._dated_label
    orig_record = learning.record
    orig_state_path = ks.STATE_PATH
    orig_lock_path = ks._STATE_LOCK_PATH

    stub = _StubGws()
    records = []

    def fake_acct(slug):
        return {"config_dir": "/tmp/fake-cfg"}

    def fake_ensure_label(cfg, name):
        stub(cfg, ["gmail", "users", "labels", "create"])
        return "LID"

    def fake_record(event):
        records.append(event)
        return event

    ks._acct = fake_acct
    du._gws = stub
    iz._ensure_label = fake_ensure_label
    iz._dated_label = lambda base: "🗄️ Auto-Archived 2026-09-17"
    learning.record = fake_record

    try:
        with tempfile.TemporaryDirectory() as tmp:
            _fresh_state(tmp)

            # --- 1. Response returns before the slow write completes ------------
            t0 = time.monotonic()
            resp = ks._dismiss({"slug": "acct1", "thread_id": "t1", "sender": "Jane",
                                "sender_email": "jane@x.com", "subject": "Hi",
                                "snippet": "...", "epoch": 100, "learn": True})
            elapsed = time.monotonic() - t0
            assert elapsed < 0.2, f"_dismiss must return before the Gmail write; took {elapsed:.3f}s"
            assert resp["ok"] is True and resp["thread_id"] == "t1" and "label" in resp, resp
            print(f"dismiss() returned in {elapsed*1000:.1f}ms (stubbed write is {SLOW_WRITE_S*1000:.0f}ms)")

            # --- 2. State updated optimistically (loop gone immediately) --------
            st = _read_state()
            assert "t1" not in _loop_ids(st), "loop should be dropped optimistically"
            a = st["accounts"][0]
            assert a["inbox_threads"] == 0
            assert any(p["count"] == 1 for p in a["undo_points"]), "undo bucket should bump immediately"

            # Let the background write finish, and confirm the learning signal fired
            # exactly once, only after the write succeeded.
            assert _wait_for(lambda: len(stub.calls) >= 1), "background write never ran"
            assert _wait_for(lambda: len(records) == 1), "learning signal not recorded"
            assert records[0]["type"] == "keep_override"
            assert records[0]["thread_id"] == "t1"

            # --- 3. A failed background write rolls the state back --------------
            _fresh_state(tmp)
            stub.calls.clear()
            records.clear()
            stub.fail_next = True

            t0 = time.monotonic()
            resp2 = ks._dismiss({"slug": "acct1", "thread_id": "t1", "sender": "Jane",
                                 "sender_email": "jane@x.com", "subject": "Hi",
                                 "snippet": "...", "epoch": 100, "learn": True})
            elapsed2 = time.monotonic() - t0
            assert elapsed2 < 0.2, "must still return fast even though the write will fail"
            assert resp2["ok"] is True

            # Immediately after the response, the optimistic (now-wrong) state says
            # the loop is gone.
            st_mid = _read_state()
            assert "t1" not in _loop_ids(st_mid)

            # Once the failing write resolves, the loop must be put back and the
            # undo bucket decremented, so the user is never told mail moved when it
            # didn't (reversibility is the product).
            assert _wait_for(lambda: "t1" in _loop_ids(_read_state())), \
                "failed write must roll the optimistic drop back"
            st_after = _read_state()
            a2 = st_after["accounts"][0]
            assert a2["inbox_threads"] == 1, "inbox_threads must be restored on rollback"
            assert not a2.get("undo_points"), "undo bucket bump must be reverted on rollback"

            # The learning signal must NOT have been recorded for a write that failed.
            time.sleep(0.05)
            assert len(records) == 0, "learning signal must not fire on a failed write"

            # A failure toast must have been queued via the existing notification channel.
            note = ks._pop_pending_notification()
            assert note is not None and "set aside" in note["body"].lower(), note

            print("rollback correctly restored state, skipped the learning signal, "
                  "and queued a user-facing notification")

            # --- 4. undo_thread: same optimistic + rollback + exactly-once record ---
            _fresh_state(tmp)
            # simulate: t1 already archived, not currently a loop
            st0 = _read_state()
            st0["accounts"][0]["loops"] = []
            st0["accounts"][0]["inbox_threads"] = 0
            with open(ks.STATE_PATH, "w") as f:
                json.dump(st0, f)
            stub.calls.clear()
            records.clear()

            t0 = time.monotonic()
            resp3 = ks._undo_thread({"slug": "acct1", "label": "🗄️ Auto-Archived 2026-09-17",
                                     "id": "m1", "thread_id": "t1", "sender": "Jane",
                                     "sender_email": "jane@x.com", "subject": "Hi",
                                     "snippet": "...", "epoch": 100})
            elapsed3 = time.monotonic() - t0
            assert elapsed3 < 0.2, f"_undo_thread must return before the write; took {elapsed3:.3f}s"
            assert resp3 == {"ok": True}
            assert "t1" in _loop_ids(_read_state()), "undo_thread must re-add the loop optimistically"

            assert _wait_for(lambda: len(records) == 1)
            assert records[0]["type"] == "keep_override_undo"

    finally:
        ks._acct = orig_acct
        du._gws = orig_gws
        iz._ensure_label = orig_ensure
        iz._dated_label = orig_dated
        learning.record = orig_record
        ks.STATE_PATH = orig_state_path
        ks._STATE_LOCK_PATH = orig_lock_path

    print("optimistic_ops OK")


if __name__ == "__main__":
    main()
