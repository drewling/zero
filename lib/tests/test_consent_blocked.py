#!/usr/bin/env python3
"""Runnable check for keeper_server._is_consent_blocked — the matcher that decides
whether a post-sign-in failure means the OAuth consent screen is Internal/Testing.
Run: python3 lib/tests/test_consent_blocked.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from keeper_server import _is_consent_blocked   # noqa: E402

# Genuine consent-screen blocks — unambiguous wording → True.
assert _is_consent_blocked("Error: org_internal — app is internal")
assert _is_consent_blocked("user has not been registered as a test user")
assert _is_consent_blocked("caller does not have permission")
assert _is_consent_blocked("does not have required permission to use project drewl-1")

# access_denied PAIRED with a testing/internal signal → still True.
assert _is_consent_blocked("access_denied: app has not been verified by Google")
assert _is_consent_blocked("access_denied — this app is in testing")

# Bare access_denied (user hit Cancel/Deny, or unverified-app block on an app that
# is already External/In-production) → must NOT misfire as a consent-screen problem.
assert not _is_consent_blocked("access_denied"), "bare access_denied must not match"
assert not _is_consent_blocked("Error 403: access_denied, the user denied the request")

# Unrelated errors → False.
assert not _is_consent_blocked("")
assert not _is_consent_blocked(None)
assert not _is_consent_blocked("gmail api has not been used in project 123 before")

print("consent_blocked OK")
