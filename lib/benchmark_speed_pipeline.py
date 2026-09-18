#!/usr/bin/env python3
"""Deterministic API call-count benchmark, no timing or live account claims.

Exercises keeper main() with --execute against a fixture that rejects mutations.
Cold/warm output equivalence and changed-policy invalidation are assertions.
"""
import json
import os
import sys
import tempfile
os.environ['ZERO_METRICS'] = '0'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
from speed_fixture import KeeperFixture

with tempfile.TemporaryDirectory() as directory:
    fixture = KeeperFixture(directory, size=60)
    cold = fixture.run()
    warm = fixture.run()
    assert cold['kept'] == warm['kept'] == 60
    assert cold['to_archive'] == warm['to_archive'] == 0
    assert warm['gmail_calls'].get('threads.get', 0) == 0
    assert warm['gmail_calls'].get('threads.modify', 0) == 0
    assert warm['jev_calls'] == 0
    fixture.policy += ' Updated policy.'
    policy = fixture.run()
    assert policy['jev_calls'] == 60
    assert policy['gmail_calls'].get('threads.get', 0) == 0
    positive = {'cold': cold, 'warm': warm, 'changed_policy': policy}

with tempfile.TemporaryDirectory() as directory:
    fixture = KeeperFixture(directory, size=60)
    fixture.replied = False
    fixture.run()
    negative_warm = fixture.run()
    assert negative_warm['gmail_calls']['messages.list'] == 2
    assert negative_warm['jev_calls'] == 0
    fixture.replied = True  # reply elsewhere, target thread historyIds do not change
    new_reply = fixture.run()
    assert new_reply['jev_calls'] == 60
    assert new_reply['gmail_calls'].get('threads.get', 0) == 0
    print(json.dumps({'fixture_threads': 60, 'single_sender': True, **positive,
                      'negative_sender_warm': negative_warm,
                      'reply_elsewhere': new_reply}, indent=2))
