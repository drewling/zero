#!/usr/bin/env python3
"""Final aggressive pass: keep ONLY genuine open loops that need Tayo's attention.

Thread-level. The core signal for "already dealt with" is who sent the LAST message:
- last message is from Tayo  -> he already responded; ball is in their court -> ARCHIVE.
- Tayo never engaged + sender is cold/no-history -> not a real loop -> ARCHIVE.
- last message is from a real person Tayo has corresponded with, with an open ask -> Haiku decides.

Always KEPT regardless: live payment problems, legal/disputes, explicit deadlines.
Reversible (dated recovery label). Dry-run by default.

Usage: review_open_loops.py <config_dir> <account_label> [--execute] [--chunk 50]
"""
import argparse, json, os, subprocess, sys
from email.utils import parseaddr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inbox_zero as iz       # noqa: E402
import thin_protected as tp   # noqa: E402
import draftutil as du        # noqa: E402
import learning               # noqa: E402

CLAUDE = os.environ.get("CLAUDE_BIN", "claude")

# Candidate set: inbox minus starred/Action and (optionally) recent mail. Unlike the
# blunt inbox_zero sweep, we do NOT pattern-exclude high-stakes mail here — the LLM
# reviewer reads each thread and keeps genuine sign/pay/legal/deadline items itself,
# so excluding them would only leave settled (already-signed/paid) mail stuck in inbox.
def _candidate_q(grace_days):
    keep = '-is:starred -label:"⚡ Action"'
    if grace_days and grace_days > 0:
        keep += f" -newer_than:{grace_days}d"
    return f"in:inbox {keep}"

# Fallback if the user hasn't written a keep-policy.md (owner-neutral).
DEFAULT_POLICY = (
    "Keep a thread only if it genuinely needs the user to act now: a real person awaiting their reply "
    "or decision; an unanswered direct question or request to them; a live payment PROBLEM; a legal or "
    "dispute matter; or an explicit deadline with a consequence.\n"
    "Archive everything else (reversibly): cold outreach, sales, pitches and prospecting even from "
    "named senders the user has never replied to; receipts, invoices, statements, confirmations, "
    "notifications, alerts, digests, newsletters, marketing, social, surveys, calendar RSVPs, meeting "
    "summaries, past security alerts; and any thread whose last message was from the user (already "
    "handled). When unsure, keep personal, family, legal, and payment-problem mail."
)

KEEP_POLICY_PATH = os.path.join(os.path.dirname(HERE), "keep-policy.md")


def _policy_text():
    """The user's keep-policy.md (authoritative), or the owner-neutral default."""
    try:
        if os.path.exists(KEEP_POLICY_PATH):
            t = open(KEEP_POLICY_PATH).read().strip()
            if t:
                return t
    except Exception:
        pass
    return DEFAULT_POLICY


# {policy} is filled from keep-policy.md at call time, so editing the policy
# (file or Policy tab) actually changes behaviour.
PROMPT_HEAD = (
    "You are tidying the user's inbox. For EACH numbered thread decide \"keep\" or \"archive\". "
    "Keep only what genuinely needs the user to act now; bias hard toward archive (everything archived "
    "is reversible, so when in doubt about noise, archive it). Each line gives: last_sender, "
    "last_from_owner (did the USER send the most recent message), replied_before (has the user ever "
    "written to this sender), subject, snippet.\n\n"
    "THE USER'S KEEP POLICY (authoritative -- follow it exactly):\n{policy}\n\n"
    "Hard rules regardless of the above: if last_from_owner=YES the user already replied, so archive "
    "(nothing left to do). Personal, family, legal, and live-payment-problem mail are kept even if "
    "unsure.\n\n"
    'Output ONLY a JSON object mapping each number to "keep" or "archive". No prose.\n\nTHREADS:\n'
)

_REPLIED = {}


def _replied_before(cfg, email):
    email = (email or "").lower()
    if not email:
        return False
    if email in _REPLIED:
        return _REPLIED[email]
    try:
        d = iz.gws(cfg, ["gmail", "users", "messages", "list", "--params",
                         json.dumps({"userId": "me", "q": f"from:me to:{email}", "maxResults": 1})])
        v = bool(d.get("messages"))
    except Exception:
        v = True
    _REPLIED[email] = v
    return v


def _thread_ids(cfg, grace_days):
    ids, tok = [], None
    cq = _candidate_q(grace_days)
    while True:
        p = {"userId": "me", "q": cq, "maxResults": 500}
        if tok:
            p["pageToken"] = tok
        d = iz.gws(cfg, ["gmail", "users", "threads", "list", "--params", json.dumps(p)])
        ids += [t["id"] for t in d.get("threads", []) or []]
        tok = d.get("nextPageToken")
        if not tok:
            break
    return ids


def _thread_info(cfg, tid, me):
    t = iz.gws(cfg, ["gmail", "users", "threads", "get", "--params",
                     json.dumps({"userId": "me", "id": tid, "format": "metadata",
                                 "metadataHeaders": ["From", "Subject"]})])
    msgs = t.get("messages", []) or []
    if not msgs:
        return None
    last = msgs[-1]
    h = {x["name"].lower(): x["value"] for x in last.get("payload", {}).get("headers", [])}
    last_from = h.get("from", "")
    subject = h.get("subject", "(no subject)")
    snippet = (last.get("snippet", "") or "")[:160]
    last_email = (parseaddr(last_from)[1] or "").lower()
    last_from_tayo = bool(me and me.lower() in last_from.lower())
    return {"id": tid, "ids": [m["id"] for m in msgs], "last_from": last_from,
            "last_email": last_email, "last_from_tayo": last_from_tayo,
            "subject": subject, "snippet": snippet}


def _learned_preface():
    """Preferences distilled from the user's past actions (lib/learn.py)."""
    try:
        txt = learning.learned_text().strip()
    except Exception:
        txt = ""
    if not txt:
        return ""
    return ("PREFERENCES LEARNED FROM THE USER'S PAST ACTIONS (apply these when deciding; "
            "they refine but never override keeping genuine personal/legal/payment loops):\n"
            + txt + "\n\n")


def _classify(chunk):
    lines = []
    for i, c in enumerate(chunk):
        lines.append(
            f'{i}. last_sender: {c["last_from"]} | last_from_owner: {"YES" if c["last_from_tayo"] else "NO"}'
            f' | replied_before: {"YES" if c["replied_before"] else "NO"} | subject: {c["subject"]}'
            f' | snippet: {c["snippet"]}')
    prompt = (_learned_preface() + PROMPT_HEAD.format(policy=_policy_text()) + "\n".join(lines))
    try:
        r = subprocess.run([CLAUDE, "-p", prompt, "--model", "haiku"],
                           capture_output=True, text=True, timeout=150)
    except subprocess.TimeoutExpired:
        return {}
    if r.returncode != 0:
        return {}
    txt = r.stdout
    s, e = txt.find("{"), txt.rfind("}")
    if s < 0 or e < 0:
        return {}
    try:
        return json.loads(txt[s:e + 1])
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config_dir")
    ap.add_argument("account_label")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--grace-days", type=int, default=2,
                    help="protect mail newer than N days from review (0 = review everything)")
    a = ap.parse_args()

    try:
        me = du._profile_email(a.config_dir)
    except Exception:
        me = a.account_label

    tids = _thread_ids(a.config_dir, a.grace_days)
    infos = []
    for tid in tids:
        info = _thread_info(a.config_dir, tid, me)
        if info:
            info["replied_before"] = _replied_before(a.config_dir, info["last_email"])
            infos.append(info)

    archive_msg_ids, kept, keep_s = [], 0, []
    # Deterministic fast-path: last message from Tayo -> dealt with -> archive.
    to_judge = []
    for c in infos:
        if c["last_from_tayo"]:
            archive_msg_ids += c["ids"]
        else:
            to_judge.append(c)

    for i in range(0, len(to_judge), a.chunk):
        chunk = to_judge[i:i + a.chunk]
        verdict = _classify(chunk)
        for j, c in enumerate(chunk):
            if verdict.get(str(j), "keep") == "archive":
                archive_msg_ids += c["ids"]
            else:
                kept += 1
                if len(keep_s) < 25:
                    keep_s.append({"from": c["last_from"], "subject": c["subject"]})

    result = {"account": a.account_label, "threads": len(infos),
              "dealt_with_last_from_tayo": sum(1 for c in infos if c["last_from_tayo"]),
              "to_archive_threads": len(infos) - kept, "to_keep_threads": kept,
              "mode": "execute" if a.execute else "dry-run", "keep_sample": keep_s}

    if a.execute and archive_msg_ids:
        lab = iz._dated_label(iz._BASE_LABEL)
        lid = iz._ensure_label(a.config_dir, lab)
        result["archived_messages"] = iz._batch_modify(a.config_dir, archive_msg_ids,
                                                        add_ids=[lid], remove_ids=["INBOX"])
        result["recovery_label"] = lab

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
