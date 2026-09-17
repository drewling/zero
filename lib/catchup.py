#!/usr/bin/env python3
"""Missed-important-items sweep — the "you may have missed this" catch-up.

Scans the inbox over a lookback window for threads where:
  - the last message is from someone else (not the account owner), and
  - the owner never replied (no message from the owner after theirs), and
  - it isn't obvious noise (cold sales, automated, newsletters).
Then asks Jev to keep only genuinely important, still-actionable items and say why.

Outputs JSON: {"missed": [{"from","subject","date","thread_id","why","age_days"}]}

Usage: catchup.py <config_dir> [account_label] [lookback_days]
"""
import json, os, sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import draftutil as du  # noqa: E402
import context as ctx  # noqa: E402

import jev as _jev  # noqa: E402


_JEV_IMPORTANCE_QUESTIONS = {
    "importance": {
        "type": "score",
        "instructions": (
            "How important and still actionable is this unreplied inbox thread for "
            "the account owner? Ignore cold sales, marketing, newsletters, receipts, "
            "social notifications, calendar auto-confirmations, and subscription alerts."
        ),
        "criteria": [
            "Noise or no action needed",
            "Potentially useful but not clearly actionable",
            "Genuinely important and needs attention",
        ],
    },
    "needs_attention": {
        "type": "noul",
        "instructions": (
            "Is a real person, deadline, payment, security issue, legal or tax matter, "
            "or account problem awaiting attention from the account owner?"
        ),
    },
    "reason": {
        "type": "choice",
        "instructions": "Select the most useful concise reason to surface this thread.",
        "criteria": {
            "human_request": "A real person is awaiting a response or decision",
            "deadline": "A deadline, appointment, or time-sensitive action is involved",
            "money": "Payment, billing, tax, legal, or compliance needs action",
            "account_security": "An account, access, or security issue needs attention",
        },
    },
}

_JEV_REASONS = {
    "human_request": "A person may be awaiting your response",
    "deadline": "Time-sensitive action may be needed",
    "money": "Payment, compliance, or account action may be needed",
    "account_security": "An account or security issue may need attention",
}


def _hdr(msg, name):
    for h in msg.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _age_days(date_str):
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return None


def candidates(config_dir, profile_email, lookback_days):
    """Inbox threads older than 1d but within lookback, last msg not from the owner, no owner reply."""
    q = f"in:inbox -in:chats newer_than:{lookback_days}d older_than:1d -label:\"⚡ Action\""
    lst = du._gws(config_dir, ["gmail", "users", "messages", "list", "--params",
                               json.dumps({"userId": "me", "q": q, "maxResults": 60})])
    out = []
    seen = set()
    for m in lst.get("messages", []) or []:
        tid = m["threadId"]
        if tid in seen:
            continue
        seen.add(tid)
        try:
            thread = du._gws(config_dir, ["gmail", "users", "threads", "get", "--params",
                                          json.dumps({"userId": "me", "id": tid, "format": "metadata",
                                                      "metadataHeaders": ["From", "Subject", "Date"]})])
        except Exception:
            continue
        msgs = thread.get("messages", []) or []
        if not msgs:
            continue
        # Owner replied if any message is from the account owner.
        owner_replied = any(profile_email and profile_email.lower() in _hdr(x, "from").lower() for x in msgs)
        if owner_replied:
            continue
        last = msgs[-1]
        frm = _hdr(last, "from")
        if profile_email and profile_email.lower() in frm.lower():
            continue
        date = _hdr(last, "date")
        out.append({
            "thread_id": tid,
            "from": frm,
            "subject": _hdr(last, "subject") or "(no subject)",
            "date": date,
            "age_days": _age_days(date),
            "snippet": (last.get("snippet", "") or "")[:200],
        })
    return out


def filter_important(cands, profile):
    """Use Jev's typed judgments to select important catch-up items.

    Returns a list of important candidates, or None if the judgment could not be
    made (transport failure, missing or malformed answers).  Callers must treat
    None as "could not evaluate" rather than "nothing important", instead of
    guessing which messages are safe to omit.

    Jev cannot produce prose, so the selected choice supplies a fixed,
    user-readable `why`.
    """
    if not cands:
        return []
    items = []
    for c in cands:
        state = {
            "from": c.get("from", ""),
            "subject": c.get("subject", ""),
            "age_days": c.get("age_days"),
            "snippet": c.get("snippet", ""),
            "user_profile": profile or "",
        }
        items.append((state, _JEV_IMPORTANCE_QUESTIONS))
    try:
        answers_list = _jev.ask_many(items)
    except Exception:
        return None
    if not isinstance(answers_list, list) or len(answers_list) != len(cands):
        return None

    result = []
    for c, answers in zip(cands, answers_list):
        if not isinstance(answers, dict):
            return None
        importance = answers.get("importance")
        needs_attention = answers.get("needs_attention")
        reason = answers.get("reason")
        if (not isinstance(importance, dict) or importance.get("type") != "score"
                or not isinstance(importance.get("score"), (int, float))
                or not isinstance(needs_attention, dict) or needs_attention.get("type") != "noul"
                or not isinstance(needs_attention.get("noul"), (int, float))
                or not isinstance(reason, dict) or reason.get("type") != "choice"
                or reason.get("choice") not in _JEV_REASONS):
            return None
        # Both independent signals must be strong.  Ambiguity stays out of the
        # digest rather than becoming an asserted "important" item.
        if importance["score"] >= 1.5 and needs_attention["noul"] >= 0.75:
            kept = dict(c)
            kept["why"] = _JEV_REASONS[reason["choice"]]
            kept.pop("snippet", None)
            result.append(kept)
    return result


def main():
    config_dir = sys.argv[1]
    account_label = sys.argv[2] if len(sys.argv) > 2 else config_dir
    lookback = sys.argv[3] if len(sys.argv) > 3 else "14"
    try:
        profile_email = du._profile_email(config_dir)
    except Exception:
        profile_email = account_label
    cands = candidates(config_dir, profile_email, lookback)
    missed = filter_important(cands, ctx.user_profile())
    if missed is None:
        # Classification failed — surface as an error so the caller can distinguish
        # "nothing important" from "could not evaluate".
        print(json.dumps({
            "account": account_label,
            "scanned": len(cands),
            "missed": [],
            "error": "classification failed",
        }, ensure_ascii=False))
    else:
        print(json.dumps({"account": account_label, "scanned": len(cands), "missed": missed},
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
