#!/usr/bin/env python3
"""Offline checks for catchup's optional Jev typed-classification path.

Run: python3 lib/tests/test_catchup_jev.py
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

orig_active = catchup._llm._active_provider_name
orig_prompt = catchup._llm.run_prompt
orig_ask_many = catchup._jev.ask_many

try:
    # Jev uses one independently typed request per candidate and retains the
    # legacy public item shape, including a user-readable `why` and no snippet.
    captured = {}
    catchup._llm._active_provider_name = lambda: "jev"

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
    }], "Jev result must match the existing missed-item shape"

    # A failed, missing, or malformed Jev answer follows the old failed-parser
    # behavior: return None so the caller emits an evaluation error, not a claim
    # that no important mail exists.
    catchup._jev.ask_many = lambda items: [None] * len(items)
    assert catchup.filter_important(CANDIDATES, "") is None

    catchup._jev.ask_many = lambda items: [{
        "importance": {"type": "score", "score": 2.0},
        "needs_attention": {"type": "noul", "noul": 0.95},
    }] * len(items)
    assert catchup.filter_important(CANDIDATES, "") is None

    # Providers other than Jev retain the pre-existing prompt/JSON behavior.
    calls = {"n": 0}
    catchup._llm._active_provider_name = lambda: "claude"

    def _legacy(prompt, model, timeout):
        calls["n"] += 1
        assert model == "haiku" and timeout == 120
        return '[{"index": 1, "why": "legacy reason"}]', True

    catchup._llm.run_prompt = _legacy
    legacy = catchup.filter_important(CANDIDATES, "profile")
    assert calls["n"] == 1
    assert legacy == [{
        "thread_id": "noise", "from": "Vendor <sales@example.com>",
        "subject": "Special offer", "date": "Tue", "age_days": 4,
        "why": "legacy reason",
    }]
finally:
    catchup._llm._active_provider_name = orig_active
    catchup._llm.run_prompt = orig_prompt
    catchup._jev.ask_many = orig_ask_many

print("catchup_jev OK")
