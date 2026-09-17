#!/usr/bin/env python3
"""Agreement + safety check: compare Jev classification against the current (LLM) path.

This is the checkpoint from docs/JEV_MIGRATION_PLAN.md Part 4. It answers the only
two questions that matter before Jev is allowed near real mail:

  1. AGREEMENT  - how often does Jev reach the same verdict as the current path?
  2. NO-LOSS    - does Jev ever archive something the current path kept?

(2) is the one that can lose mail, so it is reported separately and loudly. Per
PRODUCT.md, reversibility is the product: a new-archive is the only truly costly
disagreement, and it is the number to look at before flipping the default.

Usage:
  # Offline: run against the bundled fixture set (no network, no mail touched)
  python3 lib/tests/agreement_check.py --fixtures

  # Live: run both classifiers over real threads from an account (READ-ONLY,
  # never archives anything - it only compares verdicts)
  python3 lib/tests/agreement_check.py --account primary --limit 100
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
ROOT = os.path.dirname(LIB)
sys.path.insert(0, LIB)

# Fixtures: representative threads with the verdict a careful human would give.
# Kept deliberately small and legible; the point is to catch gross behavior changes
# and to make disagreements inspectable by a person, not to be a benchmark.
FIXTURES = [
    {
        "name": "real person awaiting reply",
        "last_from": "Sarah Chen <sarah@acmelegal.com>",
        "subject": "Re: contract review",
        "snippet": "Thanks for sending this over. Could you confirm the indemnity clause by Friday?",
        "last_from_owner": False, "replied_before": True,
        "expect": "keep",
    },
    {
        "name": "cold outreach, named sender, never replied",
        "last_from": "Jake Morrison <jake@growthscale.io>",
        "subject": "Quick question about your sales stack",
        "snippet": "I noticed you're scaling the team - would love 15 mins to show you how we help.",
        "last_from_owner": False, "replied_before": False,
        "expect": "archive",
    },
    {
        "name": "owner sent last message (already handled)",
        "last_from": "me@example.com",
        "subject": "Re: invoice question",
        "snippet": "Sent the updated invoice just now, let me know if that works.",
        "last_from_owner": True, "replied_before": True,
        "expect": "archive",
    },
    {
        "name": "live payment problem",
        "last_from": "Stripe <notifications@stripe.com>",
        "subject": "Action required: your payout failed",
        "snippet": "We couldn't deposit your payout. Update your bank details to avoid interruption.",
        "last_from_owner": False, "replied_before": False,
        "expect": "keep",
    },
    {
        "name": "newsletter",
        "last_from": "Morning Brew <crew@morningbrew.com>",
        "subject": "\u2615 The Fed blinks",
        "snippet": "Markets rallied on the news. Plus: why everyone's talking about lab-grown coffee.",
        "last_from_owner": False, "replied_before": False,
        "expect": "archive",
    },
    {
        "name": "receipt",
        "last_from": "Apple <no_reply@apple.com>",
        "subject": "Your receipt from Apple",
        "snippet": "iCloud+ 2TB monthly subscription. Total: $9.99.",
        "last_from_owner": False, "replied_before": False,
        "expect": "archive",
    },
    {
        "name": "explicit deadline with consequence",
        "last_from": "Companies House <noreply@companieshouse.gov.uk>",
        "subject": "Confirmation statement overdue",
        "snippet": "Your confirmation statement is overdue. The company may be struck off the register.",
        "last_from_owner": False, "replied_before": False,
        "expect": "keep",
    },
    {
        "name": "personal / family",
        "last_from": "Mum <mum@gmail.com>",
        "subject": "Sunday lunch?",
        "snippet": "Are you around this Sunday? Let me know so I can sort the food.",
        "last_from_owner": False, "replied_before": True,
        "expect": "keep",
    },
    {
        "name": "calendar notification",
        "last_from": "Google Calendar <calendar-notification@google.com>",
        "subject": "Notification: Standup @ Mon 9am",
        "snippet": "This is a notification for the event Standup.",
        "last_from_owner": False, "replied_before": False,
        "expect": "archive",
    },
    {
        "name": "direct unanswered question from colleague",
        "last_from": "Dev Patel <dev@company.com>",
        "subject": "Which deploy target for the hotfix?",
        "snippet": "Do you want this on staging first or straight to prod? Blocked until you say.",
        "last_from_owner": False, "replied_before": True,
        "expect": "keep",
    },
]


def _rows(items):
    """Normalize fixture/live items into the shape the classifiers consume."""
    out = []
    for it in items:
        out.append({
            "id": it.get("id", it.get("name", "")),
            "last_from": it["last_from"],
            "subject": it["subject"],
            "snippet": it["snippet"],
            "last_from_owner": it["last_from_owner"],
            "replied_before": it["replied_before"],
            "expect": it.get("expect"),
            "name": it.get("name", it.get("subject", "")),
        })
    return out


def _jev_verdicts(rows):
    """Classify with the Jev path. Returns list of (decision, category, detail)."""
    import review_open_loops as rol
    fn = getattr(rol, "_classify_jev", None)
    if fn is None:
        print("FAIL: review_open_loops._classify_jev not found. Is the Jev port complete?")
        sys.exit(2)
    verdict = fn(rows)
    out = []
    for i, _ in enumerate(rows):
        v = verdict.get(str(i)) or {}
        out.append((v.get("decision", "keep"), v.get("category"), v))
    return out


def _report(rows, jev, baseline=None, label="expected"):
    """Print a per-row comparison and the two headline numbers."""
    agree = 0
    new_archives = []          # the dangerous class: baseline kept, jev archives
    new_keeps = []             # harmless: jev is more conservative
    print(f"\n{'':2} {'thread':<42} {label:<9} {'jev':<9} {'':3}")
    print("-" * 78)
    for i, r in enumerate(rows):
        want = baseline[i] if baseline else r.get("expect")
        got = jev[i][0]
        ok = (want == got)
        agree += 1 if ok else 0
        mark = "ok" if ok else ("LOSS" if (want == "keep" and got == "archive") else "diff")
        if not ok:
            (new_archives if want == "keep" and got == "archive" else new_keeps).append(r)
        name = (r["name"] or "")[:40]
        print(f"{i:>2} {name:<42} {str(want):<9} {str(got):<9} {mark}")

    n = len(rows)
    pct = (100.0 * agree / n) if n else 0.0
    print("-" * 78)
    print(f"AGREEMENT : {agree}/{n} ({pct:.1f}%)")
    print(f"NEW ARCHIVES (would lose mail vs {label}) : {len(new_archives)}")
    for r in new_archives:
        print(f"    !! {r['name']} <- REVIEW THIS BEFORE TRUSTING JEV")
    print(f"NEW KEEPS (more conservative, safe)       : {len(new_keeps)}")
    for r in new_keeps:
        print(f"     - {r['name']}")
    return pct, len(new_archives)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", action="store_true",
                    help="run against bundled fixtures (no network beyond Jev)")
    ap.add_argument("--account", help="account slug to sample real threads from (READ-ONLY)")
    ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()

    if not a.fixtures and not a.account:
        ap.error("pass --fixtures or --account")

    if a.fixtures:
        rows = _rows(FIXTURES)
        print(f"Agreement check on {len(rows)} fixtures (expected = careful human verdict)")
        t0 = time.time()
        jev = _jev_verdicts(rows)
        dt = time.time() - t0
        pct, losses = _report(rows, jev, baseline=None, label="expected")
        print(f"\nJev classified {len(rows)} threads in {dt:.2f}s ({dt/max(len(rows),1)*1000:.0f}ms/thread)")
        # Fixtures encode unambiguous verdicts, so a new-archive here is a real defect.
        if losses:
            print("\nRESULT: FAIL - Jev archives mail the policy says to keep.")
            sys.exit(1)
        if pct < 90.0:
            print(f"\nRESULT: FAIL - agreement {pct:.1f}% is below the 90% bar.")
            sys.exit(1)
        print("\nRESULT: PASS - no mail-losing disagreements.")
        return

    # Live mode: read real threads, compare both classifiers, archive NOTHING.
    import review_open_loops as rol
    accounts = json.load(open(os.path.join(ROOT, "accounts.json")))
    acct = next((x for x in accounts if x["slug"] == a.account), None)
    if not acct:
        print(f"no such account: {a.account}")
        sys.exit(2)
    cfg = acct["config_dir"]
    me = acct.get("email", "")
    print(f"Sampling up to {a.limit} threads from {a.account} (READ-ONLY, nothing is archived)")
    tids = rol._thread_ids(cfg, 0)[: a.limit]
    infos = []
    for tid in tids:
        info = rol._thread_info(cfg, tid, me)
        if info:
            info["replied_before"] = rol._replied_before(cfg, info["last_email"])
            info["name"] = f"{info['last_from'][:24]} | {info['subject'][:24]}"
            infos.append(info)
    # Only threads that actually reach the model (owner-last is a deterministic archive).
    rows = [c for c in infos if not c["last_from_owner"]]
    print(f"{len(rows)} threads reach the classifier ({len(infos)-len(rows)} deterministic)")

    t0 = time.time(); base_raw = rol._classify(rows); base_dt = time.time() - t0
    baseline = [(base_raw.get(str(i)) or {}).get("decision", "keep") for i in range(len(rows))]
    t1 = time.time(); jev = _jev_verdicts(rows); jev_dt = time.time() - t1

    pct, losses = _report(rows, jev, baseline=baseline, label="current")
    print(f"\ncurrent path: {base_dt:.1f}s   jev path: {jev_dt:.1f}s   speedup: {base_dt/max(jev_dt,0.01):.1f}x")
    print("\nReview every NEW ARCHIVE above by hand before setting provider=jev.")


if __name__ == "__main__":
    main()
