#!/usr/bin/env python3
"""Offline checks for catchup's typed Jev classification — the only path.

Run: python3 lib/tests/test_catchup.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import catchup  # noqa: E402


CANDIDATES = [
    {"thread_id": "important", "from": "Client <client@example.com>",
     "subject": "Contract signature", "date": "Mon", "age_days": 3,
     "snippet": "Please sign before Friday."},
    {"thread_id": "noise", "from": "Vendor <sales@example.com>",
     "subject": "Special offer", "date": "Tue", "age_days": 4,
     "snippet": "Book a demo today."},
]

orig_ask_many = catchup._jev.ask_many

try:
    # One independently typed request per candidate; the public item shape keeps
    # a user-readable `why` and drops the raw snippet.
    captured = {}

    def _answers(items):
        captured["items"] = items
        return [
            {"importance": {"type": "score", "score": 2.0},
             "needs_attention": {"type": "noul", "noul": 0.93},
             "reason": {"type": "choice", "choice": "deadline"}},
            {"importance": {"type": "score", "score": 0.1},
             "needs_attention": {"type": "noul", "noul": 0.02},
             "reason": {"type": "choice", "choice": "human_request"}},
        ]

    catchup._jev.ask_many = _answers
    result = catchup.filter_important(CANDIDATES, "User prefers concise mail")
    assert len(captured["items"]) == 2, "each thread must be judged independently"
    state, questions = captured["items"][0]
    assert state["subject"] == "Contract signature"
    assert state["user_profile"] == "User prefers concise mail"
    assert set(questions) == {"importance", "needs_attention", "reason"}
    assert questions["importance"]["type"] == "score"
    assert questions["needs_attention"]["type"] == "noul"
    assert questions["reason"]["type"] == "choice"
    assert result == [{
        "thread_id": "important", "from": "Client <client@example.com>",
        "subject": "Contract signature", "date": "Mon", "age_days": 3,
        "why": "Time-sensitive action may be needed",
    }], "Jev result must match the missed-item shape"

    # Nothing to judge is an empty digest, not an evaluation failure.
    assert catchup.filter_important([], "profile") == []

    # A failed, missing, or malformed Jev answer returns None so the caller emits
    # an evaluation error, not a claim that no important mail exists.
    catchup._jev.ask_many = lambda items: [None] * len(items)
    assert catchup.filter_important(CANDIDATES, "") is None

    catchup._jev.ask_many = lambda items: [{
        "importance": {"type": "score", "score": 2.0},
        "needs_attention": {"type": "noul", "noul": 0.95},
    }] * len(items)
    assert catchup.filter_important(CANDIDATES, "") is None

    # A raising transport is reported as "could not evaluate" too.
    def _boom(items):
        raise RuntimeError("simulated transport failure")
    catchup._jev.ask_many = _boom
    assert catchup.filter_important(CANDIDATES, "") is None

    # There is no provider toggle and no legacy prompt path left.
    assert not hasattr(catchup, "_filter_important_jev"), \
        "the jev-variant name must be gone"
    assert not hasattr(catchup, "_llm"), \
        "catchup must not import the text-provider abstraction"
    src = open(os.path.join(os.path.dirname(__file__), "..", "catchup.py")).read()
    assert "_active_provider_name" not in src and "run_prompt" not in src, \
        "catchup classification must not consult a text provider"
finally:
    catchup._jev.ask_many = orig_ask_many

print("catchup OK")
