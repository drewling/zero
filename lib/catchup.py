#!/usr/bin/env python3
"""Missed-important-items sweep — the "you may have missed this" catch-up.

Scans the inbox over a lookback window for threads where:
  - the last message is from someone else (not the account owner), and
  - the owner never replied (no message from the owner after theirs), and
  - it isn't obvious noise (cold sales, automated, newsletters).
Then asks Haiku to keep only genuinely important, still-actionable items and say why.

Outputs JSON: {"missed": [{"from","subject","date","thread_id","why","age_days"}]}

Usage: catchup.py <config_dir> [account_label] [lookback_days]
"""
import json, os, sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, parseaddr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import draftutil as du  # noqa: E402
import context as ctx  # noqa: E402

import llm as _llm  # noqa: E402
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
    """Ask Haiku to keep only genuinely important, still-worth-surfacing items.

    Returns a list of important candidates, or None if the claude call failed
    (timeout, non-zero exit, or unparseable output).  Callers should treat None
    as "could not evaluate" rather than "nothing important".
    """
    if not cands:
        return []
    if _llm._active_provider_name() == "jev":
        return _filter_important_jev(cands, profile)
    listing = "\n".join(
        f'{i}. from={c["from"]} | subject={c["subject"]} | {c["age_days"]}d ago | {c["snippet"]}'
        for i, c in enumerate(cands)
    )
    prompt = f"""From this list of un-replied inbox emails the user may have missed, return ONLY the ones that are genuinely important and still worth their attention. EXCLUDE: cold sales/outbound pitches, financing offers, vendor/webinar invites, recruiters, newsletters, marketing, receipts, social notifications, and calendar "Accepted:"/"Declined:"/"Invitation:" auto-confirmations (these need no action), subscription alerts (property/job/price alerts). KEEP things that need action or a human response: payment/billing failures, real two-way threads awaiting the user, time-sensitive deadlines, client/partner asks, account/security problems, tax/legal compliance.

{profile}

EMAILS:
{listing}

Output ONLY a JSON array of objects for the important ones:
[{{"index": <number>, "why": "<short reason it matters>"}}]
If none are important, output []."""
    txt_raw, ok = _llm.run_prompt(prompt, model="haiku", timeout=120)
    if not ok:
        return None  # classification timed out or failed
    txt = txt_raw.strip()
    start, end = txt.find("["), txt.rfind("]")
    if start < 0 or end < 0:
        return None  # unparseable output
    try:
        keep = json.loads(txt[start:end + 1])
    except Exception:
        return None
    result = []
    for k in keep:
        idx = k.get("index")
        if isinstance(idx, int) and 0 <= idx < len(cands):
            c = dict(cands[idx])
            c["why"] = k.get("why", "")
            c.pop("snippet", None)
            result.append(c)
    return result


def _filter_important_jev(cands, profile):
    """Use Jev's typed judgments to select important catch-up items.

    Unlike the text-model path, Jev cannot produce a prose explanation.  The
    selected choice supplies a fixed, user-readable reason while preserving the
    existing output shape.  An incomplete or failed batch is reported as None,
    exactly like an unparseable legacy classification, rather than guessing
    which messages are safe to omit.
    """
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
