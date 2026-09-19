#!/usr/bin/env python3
"""Batched category labelling must make exactly the same decisions as the
per-thread path, and must never guess.

Labelling is additive and reversible, but a WRONG label change is still visible
to the user, so the planner is only allowed to act on facts it can prove from
the thread's own label sets:

  label_ids_all = the INTERSECTION across the thread's messages (proves a label
                  is on every message, so adding it would be a no-op)
  label_ids     = the UNION (proves a label is present somewhere, so a stale
                  category still gets cleaned up)

Anything it cannot prove locally is returned as "unplannable" and handed to the
authoritative path, which reads the thread from Gmail. These tests pin that
boundary.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import review_open_loops as rol  # noqa: E402

LABELS = [
    {"id": "L_reply", "name": "✉️ Needs reply"},
    {"id": "L_sched", "name": "📅 To schedule"},
    {"id": "INBOX", "name": "INBOX"},
]


def fake_categories():
    return [{"name": "Needs reply", "emoji": "✉️"},
            {"name": "To schedule", "emoji": "📅"}]


def setup_module():
    rol._categories = fake_categories
    rol._category_label_name = lambda c: f"{c['emoji']} {c['name']}"
    rol._load_label_history = lambda: set()


def info(tid, all_labels, union=None, ids=None):
    return {"id": tid, "ids": ids or [tid + "-m1"],
            "label_ids_all": set(all_labels),
            "label_ids": set(union if union is not None else all_labels)}


def test_already_correct_is_a_noop():
    """Target on EVERY message and no stale category = no write at all."""
    setup_module()
    plan = rol._plan_category("cfg", info("t1", {"L_reply", "INBOX"}),
                              "Needs reply", LABELS)
    assert plan is None, f"expected no-op, got {plan}"


def test_missing_target_is_added():
    setup_module()
    add, remove, ids = rol._plan_category("cfg", info("t2", {"INBOX"}),
                                          "Needs reply", LABELS)
    assert add == ["L_reply"] and remove == [] and ids == ["t2-m1"]


def test_stale_category_is_removed():
    setup_module()
    add, remove, _ = rol._plan_category(
        "cfg", info("t3", {"INBOX"}, union={"INBOX", "L_sched"}),
        "Needs reply", LABELS)
    assert add == ["L_reply"], add
    assert remove == ["L_sched"], remove


def test_partial_target_still_adds():
    """On some messages but not all: adding is still required, and safe."""
    setup_module()
    add, remove, _ = rol._plan_category(
        "cfg", info("t4", {"INBOX"}, union={"INBOX", "L_reply"}),
        "Needs reply", LABELS)
    assert add == ["L_reply"], "intersection, not union, decides the add"
    assert remove == []


def test_missing_intersection_is_unplannable():
    """Without label_ids_all we cannot prove a no-op; defer, never guess."""
    setup_module()
    bad = {"id": "t5", "ids": ["m"], "label_ids": {"INBOX"}, "label_ids_all": None}
    assert rol._plan_category("cfg", bad, "Needs reply", LABELS) == "unplannable"


def test_uncreated_label_is_unplannable():
    """A label Gmail does not have yet must go down the path that creates it."""
    setup_module()
    rol._categories = lambda: [{"name": "Brand new", "emoji": "🆕"}]
    plan = rol._plan_category("cfg", info("t6", {"INBOX"}), "Brand new", LABELS)
    assert plan == "unplannable", plan


def test_identical_changes_share_one_call():
    """The whole point: same change = one batchModify for many threads."""
    setup_module()
    calls = []
    rol.iz._batch_modify = lambda cfg, ids, add, rem: calls.append((ids, add, rem))
    pairs = [(info(f"t{i}", {"INBOX"}), "Needs reply") for i in range(50)]
    ok, failed, leftover = rol._apply_categories_batched("cfg", pairs, LABELS)
    assert ok == 50 and failed == 0 and leftover == []
    assert len(calls) == 1, f"expected 1 grouped call, got {len(calls)}"
    assert len(calls[0][0]) == 50, "every message id must be in the call"


def test_distinct_changes_do_not_merge():
    setup_module()
    calls = []
    rol.iz._batch_modify = lambda cfg, ids, add, rem: calls.append((ids, add, rem))
    pairs = ([(info(f"a{i}", {"INBOX"}), "Needs reply") for i in range(3)] +
             [(info(f"b{i}", {"INBOX"}), "To schedule") for i in range(3)])
    ok, failed, _ = rol._apply_categories_batched("cfg", pairs, LABELS)
    assert ok == 6 and failed == 0
    assert len(calls) == 2, f"two distinct changes must not merge: {calls}"


def test_failed_group_does_not_sink_the_others():
    setup_module()
    def flaky(cfg, ids, add, rem):
        if add == ["L_sched"]:
            raise RuntimeError("Gmail said no")
    rol.iz._batch_modify = flaky
    pairs = ([(info(f"a{i}", {"INBOX"}), "Needs reply") for i in range(4)] +
             [(info(f"b{i}", {"INBOX"}), "To schedule") for i in range(2)])
    ok, failed, _ = rol._apply_categories_batched("cfg", pairs, LABELS)
    assert ok == 4, f"the healthy group must still be applied, got {ok}"
    assert failed == 2, f"only the failed group is counted failed, got {failed}"


def test_noops_count_as_success_and_cost_nothing():
    setup_module()
    calls = []
    rol.iz._batch_modify = lambda cfg, ids, add, rem: calls.append(ids)
    pairs = [(info(f"t{i}", {"L_reply", "INBOX"}), "Needs reply") for i in range(10)]
    ok, failed, leftover = rol._apply_categories_batched("cfg", pairs, LABELS)
    assert ok == 10 and failed == 0 and leftover == []
    assert calls == [], "already-correct threads must not be written at all"


def test_unplannable_is_handed_back_not_dropped():
    setup_module()
    rol.iz._batch_modify = lambda cfg, ids, add, rem: None
    good = (info("good", {"INBOX"}), "Needs reply")
    bad = ({"id": "bad", "ids": ["m"], "label_ids": set(), "label_ids_all": None},
           "Needs reply")
    ok, failed, leftover = rol._apply_categories_batched("cfg", [good, bad], LABELS)
    assert ok == 1 and failed == 0
    assert [i["id"] for i, _ in leftover] == ["bad"], \
        "a thread we cannot plan must be returned for the slow path, never lost"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    print("batched category labelling: all tests passed")
