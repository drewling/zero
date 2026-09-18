#!/usr/bin/env python3
"""Adversarial checks on the two places where a bad input can silently ARCHIVE
mail that must be kept. No network.

1. _noul/_score must never hand _jev_decide a non-finite number. NaN loses every
   comparison, so a NaN `is_protected` makes the "protected mail is always kept"
   guard fall through while the noise guards still fire -> a personal/legal
   thread gets archived. Note json.loads accepts a bare NaN literal, and
   float("nan")/float("1e999") succeed on strings, so this is reachable from a
   malformed API response rather than only from a hostile one.

2. last_from_owner must not be decided by a substring test. The owner's address
   is frequently a substring of another person's address at the same domain
   ("ben@gmail.com" inside "reuben@gmail.com"), and last_from_owner=True is a
   DETERMINISTIC archive that never even calls Jev.

Run: python3 lib/tests/test_decide_hardening.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import review_open_loops as rol  # noqa: E402

FAILS = []


def check(label, got, want):
    if got != want:
        FAILS.append(f"{label}: got {got!r}, want {want!r}")
        print(f"  FAIL {label}: got {got!r}, want {want!r}")
    else:
        print(f"  ok   {label}")


# --- 1. Non-finite answers must never unlock the archive path ----------------
print("non-finite answers are keep-biased:")

NOISE = {"awaiting_user": {"noul": 0.02}, "urgency": {"score": 0.0},
         "is_cold_outreach": {"noul": 0.95}, "is_automated": {"noul": 0.9}}


def with_protected(value):
    d = dict(NOISE)
    d["is_protected"] = {"noul": value}
    return d


# The baseline: genuine noise with a low protected score still archives, so the
# tool is not simply broken into keeping everything.
check("genuine noise still archives", rol._jev_decide(with_protected(0.02)), "archive")

# A NaN protected score must be treated as "unknown" -> the keep-biased default.
check("NaN is_protected keeps", rol._jev_decide(with_protected(float("nan"))), "keep")
check("'nan' string is_protected keeps", rol._jev_decide(with_protected("nan")), "keep")
check("inf is_protected keeps", rol._jev_decide(with_protected(float("inf"))), "keep")
check("'1e999' is_protected keeps", rol._jev_decide(with_protected("1e999")), "keep")

# Out-of-range probabilities are malformed too; they must not be trusted.
check("negative is_protected keeps", rol._jev_decide(with_protected(-1.0)), "keep")
check("is_protected > 1 keeps", rol._jev_decide(with_protected(5.0)), "keep")

# Non-finite values in the other slots must also resolve conservatively.
check("NaN awaiting keeps",
      rol._jev_decide({"is_protected": {"noul": 0.01}, "awaiting_user": {"noul": float("nan")},
                       "urgency": {"score": 0.0}, "is_cold_outreach": {"noul": 0.95}}), "keep")
check("NaN urgency keeps",
      rol._jev_decide({"is_protected": {"noul": 0.01}, "awaiting_user": {"noul": 0.02},
                       "urgency": {"score": float("nan")}, "is_cold_outreach": {"noul": 0.95}}), "keep")
check("NaN cold does not archive",
      rol._jev_decide({"is_protected": {"noul": 0.01}, "awaiting_user": {"noul": 0.02},
                       "urgency": {"score": 0.0}, "is_cold_outreach": {"noul": float("nan")},
                       "is_automated": {"noul": float("nan")}}), "keep")

# The helpers themselves must fall back rather than emit a non-finite number.
check("_noul(NaN) -> default", rol._noul({"k": {"noul": float("nan")}}, "k", default=1.0), 1.0)
check("_score(NaN) -> default", rol._score({"k": {"score": float("nan")}}, "k", default=2.0), 2.0)
check("_noul(valid) passes through", rol._noul({"k": {"noul": 0.4}}, "k", default=1.0), 0.4)
check("_score(valid) passes through", rol._score({"k": {"score": 1.0}}, "k", default=2.0), 1.0)


# --- 2. Owner detection must compare addresses, not substrings ---------------
print("\nlast_from_owner compares addresses, not substrings:")

check("exact owner address is the owner",
      rol._is_owner_sender("tayo@drewl.com", "Tayo <tayo@drewl.com>"), True)
check("bare owner address with no display name",
      rol._is_owner_sender("tayo@drewl.com", "tayo@drewl.com"), True)
check("owner match is case-insensitive",
      rol._is_owner_sender("Tayo@Drewl.com", "TAYO@DREWL.COM"), True)
# The bug: a real correspondent whose address merely CONTAINS the owner's.
check("reuben@gmail.com is NOT ben@gmail.com",
      rol._is_owner_sender("ben@gmail.com", "Reuben <reuben@gmail.com>"), False)
check("bojo@x.com is NOT jo@x.com",
      rol._is_owner_sender("jo@x.com", "Bo Jo <bojo@x.com>"), False)
check("owner address inside a display name is not the sender",
      rol._is_owner_sender("ben@gmail.com", '"ben@gmail.com via List" <list@lists.org>'), False)
check("different domain is not the owner",
      rol._is_owner_sender("ben@gmail.com", "ben@gmail.com.evil.ru"), False)
check("empty owner never matches", rol._is_owner_sender("", "someone@x.com"), False)
check("empty from never matches", rol._is_owner_sender("me@x.com", ""), False)
# Fallback: when `me` is not an address at all (main() falls back to the account
# label), the old substring behaviour is the only thing available.
check("non-address owner label still substring-matches",
      rol._is_owner_sender("work-account", "Me <me@x.com> (work-account)"), True)


if FAILS:
    print(f"\n{len(FAILS)} FAILURE(S)")
    for f in FAILS:
        print("  - " + f)
    sys.exit(1)
print("\ndecide_hardening OK")
