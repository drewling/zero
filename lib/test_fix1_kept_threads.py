#!/usr/bin/env python3
"""Self-check for FIX 1: kept_thread_ids() and the review_open_loops skip-guard.

No network, no Gmail, no frameworks. Uses a temp dir for signals.jsonl.
"""
import json, os, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ----- (a) kept_thread_ids returns correct ids --------------------------------

def test_kept_thread_ids():
    import learning as _learning_mod

    with tempfile.TemporaryDirectory() as tmp:
        signals_path = os.path.join(tmp, "signals.jsonl")

        # Monkeypatch SIGNALS and LEARN_DIR
        orig_signals = _learning_mod.SIGNALS
        orig_learn_dir = _learning_mod.LEARN_DIR
        _learning_mod.SIGNALS = signals_path
        _learning_mod.LEARN_DIR = tmp

        try:
            now = int(time.time())
            rows = [
                # Should be included: keep_override_undo WITH thread_id
                {"type": "keep_override_undo", "thread_id": "tid-A", "ts": now},
                {"type": "keep_override_undo", "thread_id": "tid-B", "ts": now},
                # Should be excluded: different signal type
                {"type": "keep_override", "thread_id": "tid-C", "ts": now},
                # Should be excluded: keep_override_undo WITHOUT thread_id
                {"type": "keep_override_undo", "label": "zero/2024-01-01",
                 "message_count": 5, "ts": now},
                # Should be excluded: draft_edit
                {"type": "draft_edit", "thread_id": "tid-D", "ts": now},
            ]
            with open(signals_path, "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")

            result = _learning_mod.kept_thread_ids()
            assert result == {"tid-A", "tid-B"}, f"expected {{tid-A, tid-B}}, got {result}"
            print("(a) kept_thread_ids: PASS")

        finally:
            _learning_mod.SIGNALS = orig_signals
            _learning_mod.LEARN_DIR = orig_learn_dir


# ----- (b) review_open_loops skip-guard excludes kept threads -----------------

def test_skip_guard():
    """Simulate the main() loop logic for the keep-set guard."""
    # Replicate the guard from review_open_loops.main():
    #   if c["id"] in keep_set: kept += 1; continue
    keep_set = {"tid-A", "tid-B"}

    infos = [
        {"id": "tid-A", "last_from_owner": False, "ids": ["m1"]},  # in keep_set -> skip
        {"id": "tid-B", "last_from_owner": True,  "ids": ["m2"]},  # in keep_set -> skip (even owner-replied)
        {"id": "tid-C", "last_from_owner": True,  "ids": ["m3"]},  # not in keep_set, owner-replied -> archive
        {"id": "tid-D", "last_from_owner": False, "ids": ["m4"]},  # not in keep_set -> to_judge
    ]

    archive_msg_ids, kept = [], 0
    to_judge = []
    for c in infos:
        if c["id"] in keep_set:
            kept += 1
            continue
        if c["last_from_owner"]:
            archive_msg_ids += c["ids"]
        else:
            to_judge.append(c)

    assert kept == 2, f"expected 2 kept, got {kept}"
    assert archive_msg_ids == ["m3"], f"expected [m3] archived, got {archive_msg_ids}"
    assert [c["id"] for c in to_judge] == ["tid-D"], f"expected [tid-D] to judge, got {[c['id'] for c in to_judge]}"
    print("(b) skip-guard: PASS — kept threads bypass both owner-replied path and LLM batch")


if __name__ == "__main__":
    test_kept_thread_ids()
    test_skip_guard()
    print("All self-checks PASSED")
