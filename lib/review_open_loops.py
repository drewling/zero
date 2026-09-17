#!/usr/bin/env python3
"""Final aggressive pass: keep ONLY genuine open loops that need the account owner's attention.

Thread-level. The core signal for "already dealt with" is who sent the LAST message:
- last message is from the owner -> they already responded; ball is in their court -> ARCHIVE.
- Owner never engaged + sender is cold/no-history -> not a real loop -> ARCHIVE.
- last message is from a real person the owner has corresponded with, with an open ask -> Jev decides.

Always KEPT regardless: live payment problems, legal/disputes, explicit deadlines.
Reversible (dated recovery label). Dry-run by default.

Usage: review_open_loops.py <config_dir> <account_label> [--execute] [--chunk 50]
"""
import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.utils import parseaddr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import inbox_zero as iz       # noqa: E402
import draftutil as du        # noqa: E402
import learning               # noqa: E402

_CATEGORIES_PATH = os.path.join(ROOT, "categories.json")
_LABEL_HISTORY_PATH = os.path.join(ROOT, "app", "category_label_history.json")

# --- Jev decision thresholds -------------------------------------------------
# The keep/archive rule for the Jev path lives HERE, in code, not in a prompt.
# Jev returns calibrated probabilities, so aggressiveness is one number to tune
# and the uncertain case is explicit. Every path that isn't a confident archive
# ends in "keep" (PRODUCT.md: reversible by construction, never lose mail).
#
# JEV_KEEP_AWAITING     : p(a real person is awaiting the owner) above this -> keep
#                         outright. Lower it to keep more, raise it to archive more.
# JEV_ARCHIVE_AWAITING  : archiving is only ever allowed when p(awaiting) is below
#                         this. Between the two values the thread is "uncertain" and
#                         is kept. Widening this gap makes the tool more conservative.
# JEV_KEEP_URGENCY      : urgency score (0=no consequence, 1=minor, 2=real deadline
#                         or money/legal at stake) at or above which we keep no matter
#                         what else says. 1.5 = leaning toward the top level.
# JEV_NOISE_MIN         : p(cold outreach) or p(automated) needed before a thread may
#                         be called noise. A thread must look like noise AND have no
#                         one awaiting AND be low urgency before it is archived.
# JEV_KEEP_PROTECTED    : p(personal/family/legal/live-payment-problem) above this is
#                         kept unconditionally — the hard rule from PRODUCT.md.
# JEV_MIN_CATEGORY_CONF : below this confidence we apply no category label rather than
#                         a bad one. Labels are cosmetic; a wrong one is worse than none.
JEV_KEEP_AWAITING = 0.75
JEV_ARCHIVE_AWAITING = 0.25
JEV_KEEP_URGENCY = 1.5
JEV_NOISE_MIN = 0.5
JEV_KEEP_PROTECTED = 0.5
JEV_MIN_CATEGORY_CONF = 0.35

# Concurrency/timeout for the per-thread Jev calls (one call per thread, all
# questions answered in parallel inside that call).
JEV_MAX_WORKERS = 12
JEV_TIMEOUT = 30.0

# Urgency levels. Each level describes a CONCRETE situation, per TypeSafe's
# guidance that a Score's levels must be describable positions on a spectrum.
JEV_URGENCY_LEVELS = [
    "No consequence: nothing happens if this is never opened — newsletter, "
    "marketing, digest, social or app notification, or a receipt/confirmation for "
    "something already completed.",
    "Minor: mildly useful to know, but nobody is blocked and nothing is at stake — "
    "an FYI, a status update, or a routine request with no deadline.",
    "Real consequence: a person is blocked waiting on this, or money, access, "
    "legal standing or a stated deadline is at stake — a failed payment, a dispute, "
    "an overdue filing, or an unanswered direct question holding someone up.",
]

# Choice option meaning "no category fits"; mapped back to None so the Gmail
# labeler never invents a label. Never collides with a real category name.
JEV_NO_CATEGORY = "No category fits"


def _emit_progress(pct, label=""):
    """Live progress marker for the parent (keeper_server) to map onto the run bar.
    The parent reads these off stdout as we go; the only line that starts with '{'
    is the final result JSON, so these markers never collide with it."""
    sys.stdout.write(f"\x1fP\x1f{int(pct)}\x1f{label}\n")
    sys.stdout.flush()


def _load_label_history():
    """Return the persisted set of category label names (past + present)."""
    try:
        if os.path.exists(_LABEL_HISTORY_PATH):
            with open(_LABEL_HISTORY_PATH) as f:
                data = json.load(f)
            return set(data.get("labels", []))
    except Exception:
        pass
    return set()


def _add_to_label_history(names):
    """Union names into the persisted label history file. Non-fatal."""
    try:
        existing = _load_label_history()
        merged = existing | set(names)
        tmp = _LABEL_HISTORY_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"labels": sorted(merged)}, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _LABEL_HISTORY_PATH)
    except Exception:
        pass

_DEFAULT_CATEGORIES = [
    {"name": "Needs reply",      "description": "Someone is waiting on a direct response from me.", "emoji": "✉️"},
    {"name": "Waiting on others","description": "I'm blocked on someone else; tracking, no action yet.", "emoji": "⏳"},
    {"name": "To schedule",      "description": "Needs a meeting, call, or calendar action.",       "emoji": "📅"},
    {"name": "Read later",       "description": "Worth reading but not urgent or action-bearing.",  "emoji": "🔖"},
    {"name": "Action required",  "description": "A task or deadline I personally need to handle.",  "emoji": "⚡"},
]


def _categories():
    """Return the categories list from categories.json, or built-in defaults."""
    try:
        if os.path.exists(_CATEGORIES_PATH):
            with open(_CATEGORIES_PATH) as f:
                data = json.load(f)
            cats = data.get("categories", [])
            if cats:
                return cats
    except Exception:
        pass
    return _DEFAULT_CATEGORIES


def _category_label_name(cat):
    """Compose the Gmail label name for a category: '<emoji> <name>'."""
    return f"{cat['emoji']} {cat['name']}"

# Candidate set: inbox minus starred/Action and (optionally) recent mail. Unlike the
# blunt inbox_zero sweep, we do NOT pattern-exclude high-stakes mail here — the
# classifier reads each thread and keeps genuine sign/pay/legal/deadline items itself,
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


_REPLIED = {}
_REPLIED_LOCK = threading.Lock()
_REPLIED_IN_FLIGHT = {}

# Gmail reads are network-bound.  Keep this deliberately bounded so one account cannot
# stampede the API; callers can tune it for accounts with lower rate-limit headroom.
DEFAULT_READ_WORKERS = 16
_GMAIL_READ_RETRIES = 3
_GMAIL_BACKOFF_SECONDS = 0.25


def _is_rate_limited(exc):
    """Whether a gws failure is Gmail's retryable rate-limit response."""
    text = str(exc).lower()
    return ("ratelimitexceeded" in text or "userratelimitexceeded" in text
            or "429" in text
            or ("403" in text and "rate" in text))


def _gws_read(cfg, args):
    """Run a read with bounded backoff for Gmail rate limits, then preserve its error."""
    for attempt in range(_GMAIL_READ_RETRIES + 1):
        try:
            # iz.gws delegates to draftutil's subprocess.run wrapper.  Each invocation
            # owns its subprocess and input data, so independent reads are thread-safe.
            return iz.gws(cfg, args)
        except Exception as exc:
            if not _is_rate_limited(exc) or attempt == _GMAIL_READ_RETRIES:
                raise
            time.sleep(_GMAIL_BACKOFF_SECONDS * (2 ** attempt))


def _replied_before(cfg, email):
    email = (email or "").lower()
    if not email:
        return False
    # Only one worker may query an address at a time.  Other workers wait for its
    # conservative result, preserving the old memoization while avoiding duplicate I/O.
    with _REPLIED_LOCK:
        if email in _REPLIED:
            return _REPLIED[email]
        pending = _REPLIED_IN_FLIGHT.get(email)
        if pending is None:
            pending = threading.Event()
            _REPLIED_IN_FLIGHT[email] = pending
            owner = True
        else:
            owner = False
    if not owner:
        pending.wait()
        with _REPLIED_LOCK:
            return _REPLIED[email]
    try:
        d = _gws_read(cfg, ["gmail", "users", "messages", "list", "--params",
                            json.dumps({"userId": "me", "q": f"from:me to:{email}", "maxResults": 1})])
        v = bool(d.get("messages"))
    except Exception as e:
        # Lookup failed (transient gws/network blip). Bias conservatively toward "keep"
        # (assume replied-before) so we never wrongly archive, but log it: a spike of
        # these means classification is silently keep-biased, not that you reply to everyone.
        print(f"replied_before({email}) lookup failed, assuming replied: {e}", file=sys.stderr)
        v = True
    with _REPLIED_LOCK:
        _REPLIED[email] = v
        _REPLIED_IN_FLIGHT.pop(email).set()
    return v


def _thread_ids_q(cfg, q):
    """All thread ids matching a Gmail query, paged."""
    ids, tok = [], None
    while True:
        p = {"userId": "me", "q": q, "maxResults": 500}
        if tok:
            p["pageToken"] = tok
        d = iz.gws(cfg, ["gmail", "users", "threads", "list", "--params", json.dumps(p)])
        ids += [t["id"] for t in d.get("threads", []) or []]
        tok = d.get("nextPageToken")
        if not tok:
            break
    return ids


def _thread_ids(cfg, grace_days):
    return _thread_ids_q(cfg, _candidate_q(grace_days))


def _thread_info(cfg, tid, me):
    t = _gws_read(cfg, ["gmail", "users", "threads", "get", "--params",
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
    last_from_owner = bool(me and me.lower() in last_from.lower())
    label_ids = set()
    for m in msgs:
        label_ids.update(m.get("labelIds") or [])
    return {"id": tid, "ids": [m["id"] for m in msgs], "last_from": last_from,
            "last_email": last_email, "last_from_owner": last_from_owner,
            "subject": subject, "snippet": snippet, "label_ids": label_ids}


def _read_one_thread(cfg, tid, me):
    """Fetch all classifier inputs for one thread; a None metadata result stays skipped."""
    info = _thread_info(cfg, tid, me)
    if info:
        info["replied_before"] = _replied_before(cfg, info["last_email"])
    return info


def _read_infos_parallel(cfg, tids, me, max_workers=DEFAULT_READ_WORKERS):
    """Read threads concurrently while returning the sequential loop's ordered result."""
    total = len(tids)
    if not total:
        return []
    ordered = [None] * total
    completed = 0
    workers = max(1, int(max_workers))
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="gmail-read") as pool:
        futures = {pool.submit(_read_one_thread, cfg, tid, me): idx
                   for idx, tid in enumerate(tids)}
        for future in as_completed(futures):
            ordered[futures[future]] = future.result()
            completed += 1
            _emit_progress(2 + int(63 * completed / total),
                           f"Reading mail ({completed} of {total})")
    return [info for info in ordered if info]


# --- Classification ----------------------------------------------------------
# There is ONE classification path: Jev. Instead of one prompt asking a text model
# to emit JSON for a batch of 100 threads, each thread becomes its own small set of
# TYPED questions answered in ONE parallel call, and the keep/archive rule is
# Python (see the JEV_* constants at the top of this file).
#
# Why decomposed questions rather than one "should I keep this?" noul:
#   - TypeSafe's System One models answer snap judgments well and compound
#     reasoning badly. "Is a person awaiting a reply?" is answerable in a second;
#     "decide what to do with this email" is not.
#   - Each factor the keep-bar cares about (someone awaiting, cold outreach,
#     automated mail, consequence of delay, protected categories) is independent.
#     Asking them separately means the policy that combines them is readable,
#     testable and tunable code instead of prompt wording.
#   - Every answer carries a calibrated probability, so "uncertain" becomes a
#     state we can see and deliberately resolve to keep.


def _learned_rules():
    """The raw learned-preference text (lib/learn.py), or "" — no prompt framing.

    Jev takes it as a named field of the state rather than as prose."""
    try:
        return learning.learned_text().strip()
    except Exception:
        return ""


def _jev_questions(cats):
    """Build the typed question set. Category options come from categories.json
    (via _categories()), never hardcoded, so editing that file changes the choice
    options with no code change.

    The user's keep-policy.md and their learned preferences travel in the STATE
    (as `keep_policy` / `learned_preferences`) and every instruction points the
    model at them, which is how TypeSafe recommends supplying a policy a judgment
    must be made against. They stay authoritative for the judgments; the code
    thresholds only decide how confident an answer must be before we act on it."""
    criteria = {c["name"]: c.get("description", c["name"]) for c in cats}
    criteria[JEV_NO_CATEGORY] = (
        "None of the above fit, or the thread is noise that will be archived.")
    policy_ref = ("Judge against the owner's own rules in `keep_policy`, refined by "
                  "`learned_preferences` (distilled from their past actions). Where "
                  "the two conflict, `keep_policy` wins.")
    return {
        "awaiting_user": {
            "type": "noul",
            "instructions": (
                "Is a real, identifiable person waiting on a reply, decision, or "
                "action from the account owner in `thread`? " + policy_ref),
            "criteria": {
                "yes": "A human sent this and there is an unanswered question, "
                       "request, or decision genuinely addressed to the owner.",
                "no": "Nobody is actually waiting on the owner: it is broadcast, "
                      "automated, informational, already handled, or its 'ask' is a "
                      "generic sales call-to-action rather than a real request.",
            },
        },
        "is_cold_outreach": {
            "type": "noul",
            "instructions": (
                "Is `thread` unsolicited sales, prospecting, pitching, recruiting or "
                "marketing? Cold-email tools use real human names and personal "
                "phrasing, so weigh `thread.replied_before`: if the owner has never "
                "written to this sender and the message is selling something, it is "
                "cold outreach. " + policy_ref),
        },
        "is_automated": {
            "type": "noul",
            "instructions": (
                "Was `thread` generated by a system rather than typed by a person to "
                "the owner? Receipts, invoices, order and delivery confirmations, "
                "statements, digests, newsletters, marketing, social and calendar "
                "notifications all count as automated. " + policy_ref),
        },
        "is_protected": {
            "type": "noul",
            "instructions": (
                "Is `thread` personal or family correspondence, a legal, contractual "
                "or dispute matter, or a payment that has actually FAILED or is a "
                "live problem the owner must fix? A routine receipt or a successful "
                "payment confirmation is NOT a payment problem. " + policy_ref),
        },
        "urgency": {
            "type": "score",
            "instructions": (
                "How consequential is it if `thread` is set aside today and not "
                "acted on? Judge the real-world consequence, not the sender's tone "
                "or their wording. " + policy_ref),
            "criteria": JEV_URGENCY_LEVELS,
        },
        "category": {
            "type": "choice",
            "instructions": (
                "If the owner keeps `thread` in their inbox, which single category "
                "best describes what it needs from them?"),
            "criteria": criteria,
        },
    }


def _jev_state(c, policy, learned):
    """Structured program state for one thread.

    Jev is optimized for structured state, so this is a JSON object with named
    fields rather than the flat one-line-per-thread string the text prompt builds.
    The owner's policy travels WITH the thread so every judgment is made against
    it (docs.typesafe.ai/concepts/state: put the record and the policy in one
    state when the decision requires comparing them)."""
    state = {
        "thread": {
            "last_sender": c.get("last_from", ""),
            "subject": c.get("subject", ""),
            "snippet": c.get("snippet", ""),
            "last_from_owner": bool(c.get("last_from_owner")),
            "replied_before": bool(c.get("replied_before")),
        },
        "field_meanings": {
            "last_from_owner": "true means the owner sent the most recent message.",
            "replied_before": "true means the owner has written to this sender before.",
        },
        "keep_policy": policy,
    }
    if learned:
        state["learned_preferences"] = learned
    return state


def _noul(answers, key, default=None):
    """Read a noul probability, or `default` when the answer is missing/malformed.

    Defaults are chosen by the CALLER so a missing answer can never be the thing
    that causes an archive."""
    try:
        a = answers.get(key) or {}
        v = a.get("noul")
        return float(v) if v is not None else default
    except Exception:
        return default


def _score(answers, key, default=None):
    """Read a score value, or `default` when the answer is missing/malformed."""
    try:
        a = answers.get(key) or {}
        v = a.get("score")
        return float(v) if v is not None else default
    except Exception:
        return default


def _jev_category(answers, cat_names):
    """The chosen category name, or None (no label) when it doesn't apply.

    JEV_NO_CATEGORY and anything not in categories.json both map to None, so the
    Gmail labeler can never be handed a label that doesn't exist."""
    try:
        a = answers.get("category") or {}
        name = a.get("choice")
        conf = a.get("confidence")
        if name not in cat_names:
            return None
        if conf is not None and float(conf) < JEV_MIN_CATEGORY_CONF:
            return None
        return name
    except Exception:
        return None


def _jev_decide(answers):
    """Turn typed answers into "keep"/"archive". THE safety-critical function.

    Every branch that is not a confident, corroborated archive returns "keep".
    Missing or malformed answers fall back to keep-biased defaults, so a partial
    response can only ever make the outcome MORE conservative."""
    if not isinstance(answers, dict) or not answers:
        return "keep"                        # no answers at all -> keep

    # Keep-biased defaults: an absent "awaiting"/"protected"/"urgency" reads as a
    # real loop, an absent "cold"/"automated" reads as written by a human.
    awaiting = _noul(answers, "awaiting_user", default=1.0)
    protected = _noul(answers, "is_protected", default=1.0)
    cold = _noul(answers, "is_cold_outreach", default=0.0)
    automated = _noul(answers, "is_automated", default=0.0)
    urgency = _score(answers, "urgency", default=float(len(JEV_URGENCY_LEVELS) - 1))

    # Hard rule (PRODUCT.md / keep-policy.md): personal, family, legal and live
    # payment problems are kept even when the other signals call it noise.
    if protected > JEV_KEEP_PROTECTED:
        return "keep"
    # A real person is waiting, or setting this aside has a real consequence.
    if awaiting > JEV_KEEP_AWAITING or urgency >= JEV_KEEP_URGENCY:
        return "keep"
    # The ONLY archive path: nobody waiting, nothing at stake, and it looks like
    # cold outreach or machine-generated mail.
    if (awaiting < JEV_ARCHIVE_AWAITING and urgency < JEV_KEEP_URGENCY
            and (cold >= JEV_NOISE_MIN or automated >= JEV_NOISE_MIN)):
        return "archive"
    return "keep"                            # uncertain -> keep, never lose mail


def _classify(chunk):
    """Classify threads with Jev. Returns
    {str(index): {"decision": "keep"|"archive", "category": <name>|None}}.

    One Jev call per thread, all issued concurrently via jev.ask_many, so a
    200-thread inbox classifies in parallel rather than serially. Any failed call
    comes back as None from ask_many and is resolved to "keep"."""
    if not chunk:
        return {}
    try:
        import jev  # local import: keeps the module load cheap and failure-tolerant
    except Exception:
        # Can't even load the client -> keep everything. Never archive on error.
        return {str(i): {"decision": "keep", "category": None}
                for i in range(len(chunk))}

    cats = _categories()
    cat_names = {c["name"] for c in cats}
    questions = _jev_questions(cats)
    policy = _policy_text()
    learned = _learned_rules()

    out = {}
    items, order = [], []
    for i, c in enumerate(chunk):
        # Deterministic, no API call needed: the owner sent the last message, so
        # the ball is in the other party's court. main() already pre-filters these
        # out; repeated here because _classify can be handed unfiltered rows.
        if c.get("last_from_owner"):
            out[str(i)] = {"decision": "archive", "category": None}
            continue
        items.append((_jev_state(c, policy, learned), questions))
        order.append(i)

    try:
        results = jev.ask_many(items, max_workers=JEV_MAX_WORKERS, timeout=JEV_TIMEOUT)
    except Exception as e:
        # ask_many is contracted not to raise, but if it ever does: keep everything.
        print(f"jev: classification failed, keeping all threads: {e}", file=sys.stderr)
        results = [None] * len(items)

    failures = 0
    for pos, i in enumerate(order):
        answers = results[pos] if pos < len(results) else None
        if not answers:
            failures += 1
            out[str(i)] = {"decision": "keep", "category": None}
            continue
        decision = _jev_decide(answers)
        category = _jev_category(answers, cat_names) if decision == "keep" else None
        out[str(i)] = {"decision": decision, "category": category}

    if failures:
        # A spike of these means the run is silently keep-biased, not that the
        # inbox is suddenly full of open loops. Say so, same as _replied_before.
        print(f"jev: {failures}/{len(items)} thread(s) failed to classify, kept",
              file=sys.stderr)
    return out


def apply_category(cfg, thread_id, category_name, _labels_cache=None):
    """Apply a category label to a kept thread: add '<emoji> <name>', remove any other
    category labels from our set (current OR historical). Never touches non-category
    labels. Non-fatal on error. Returns True on success, False on failure.

    Args:
        cfg:            gws config_dir for the account.
        thread_id:      Gmail thread id.
        category_name:  The category name string (must be in _categories()), or None to
                        only remove stale category labels without adding a new one.
        _labels_cache:  Optional pre-fetched labels list (list of dicts with id/name)
                        to avoid a redundant labels.list API call. Pass when calling
                        in a batch loop; omit for one-off calls.
    """
    cats = _categories()
    cat_label_names = {_category_label_name(c) for c in cats}
    # Union current names into persistent history so renamed labels are tracked.
    _add_to_label_history(cat_label_names)
    # The full set of labels we'll clean up = current ∪ historical.
    all_known_cat_labels = cat_label_names | _load_label_history()

    target_label = None
    if category_name:
        cat = next((c for c in cats if c["name"] == category_name), None)
        if cat:
            target_label = _category_label_name(cat)

    try:
        # Fetch current labels on this thread to find stale category labels to remove.
        t = iz.gws(cfg, ["gmail", "users", "threads", "get",
                         "--params", json.dumps({"userId": "me", "id": thread_id,
                                                 "format": "metadata",
                                                 "metadataHeaders": []})])
        thread_label_ids = set()
        for m in (t.get("messages") or []):
            thread_label_ids.update(m.get("labelIds") or [])

        # Resolve label ids -> names; use the caller-supplied cache if available.
        if _labels_cache is not None:
            all_labels = _labels_cache
        else:
            label_data = iz.gws(cfg, ["gmail", "users", "labels", "list",
                                      "--params", json.dumps({"userId": "me"})])
            all_labels = label_data.get("labels", []) or []
        id_to_name = {l["id"]: l["name"] for l in all_labels}
        name_to_id = {l["name"]: l["id"] for l in all_labels}

        # Labels to remove: any current/historical category label on the thread
        # (excluding the new target, if any).
        remove_ids = [
            lid for lid in thread_label_ids
            if id_to_name.get(lid, "") in all_known_cat_labels
            and id_to_name.get(lid, "") != target_label
        ]

        if not target_label and not remove_ids:
            return True  # nothing to do

        add_ids = []
        if target_label:
            # Ensure the target label exists in Gmail (create if missing).
            if target_label not in name_to_id:
                created = iz.gws(cfg, ["gmail", "users", "labels", "create",
                                       "--params", json.dumps({"userId": "me"}),
                                       "--json", json.dumps({"name": target_label,
                                                             "labelListVisibility": "labelShow",
                                                             "messageListVisibility": "show"})])
                add_ids = [created["id"]]
            else:
                add_ids = [name_to_id[target_label]]

        if add_ids or remove_ids:
            iz.gws(cfg, ["gmail", "users", "threads", "modify",
                         "--params", json.dumps({"userId": "me", "id": thread_id}),
                         "--json", json.dumps({"addLabelIds": add_ids,
                                               "removeLabelIds": remove_ids})],
                   allow_empty=True)
        return True
    except Exception:
        return False  # category labeling is additive; never block the keeper run


def _known_category_label_names():
    """All category label names we'd ever apply: current categories ∪ history."""
    return {_category_label_name(c) for c in _categories()} | _load_label_history()


def _backfill_partition(infos, cat_label_names, id_to_name):
    """Pure split of candidate threads for the label-only backfill.

    Returns (to_judge, skipped_labeled, skipped_handled):
    - skip a thread already carrying any of our category labels (don't reclassify),
    - skip a thread whose last message is the owner's (already handled, never a loop),
    - everything else needs the classifier.
    """
    to_judge, skipped_labeled, skipped_handled = [], 0, 0
    for info in infos:
        names = {id_to_name.get(lid, "") for lid in info.get("label_ids", set())}
        if names & cat_label_names:
            skipped_labeled += 1
            continue
        if info.get("last_from_owner"):
            skipped_handled += 1
            continue
        to_judge.append(info)
    return to_judge, skipped_labeled, skipped_handled


def _run_label_only(cfg, me, window_days, chunk, archive_days=0):
    """Label-only backfill: classify recent inbox mail and apply category labels to
    keepers. Never archives. Light: bounded window, skips already-labeled and
    owner-handled threads (no classifier call for those), batched classification.

    If archive_days > 0, also labels recently-archived mail (non-inbox) so the
    label taxonomy stays populated across the full mailbox view.
    """
    cat_label_names = _known_category_label_names()
    # One labels.list for the whole run — shared with apply_category via _labels_cache
    # to avoid 2 extra API calls per thread (cuts volume = fewer 429s).
    label_data = iz.gws(cfg, ["gmail", "users", "labels", "list",
                              "--params", json.dumps({"userId": "me"})])
    all_labels_list = label_data.get("labels") or []
    id_to_name = {l["id"]: l["name"] for l in all_labels_list}

    # Inbox window.
    inbox_tids = set(_thread_ids_q(cfg, f"in:inbox newer_than:{window_days}d"))
    # Archived window (non-inbox recent mail), unioned with inbox set.
    archived_tids = set()
    if archive_days and archive_days > 0:
        archived_tids = set(_thread_ids_q(
            cfg, f"-in:inbox in:all newer_than:{archive_days}d")) - inbox_tids

    _emit_progress(2, "Finding recent mail")
    all_tids = list(inbox_tids | archived_tids)
    # Same parallel read the main path uses. This loop used to be sequential, which
    # at a few thousand threads meant hours of one-at-a-time network round-trips
    # with the progress bar apparently frozen.
    infos = _read_infos_parallel(cfg, all_tids, me)
    to_judge, skipped_labeled, skipped_handled = _backfill_partition(
        infos, cat_label_names, id_to_name)

    # _read_infos_parallel already resolved replied_before for every thread it read,
    # concurrently and memoised per sender, so there is nothing left to look up here.

    labeled = label_failed = 0
    n_judge = max(len(to_judge), 1)
    for i in range(0, len(to_judge), chunk):
        batch = to_judge[i:i + chunk]
        _emit_progress(65 + int(30 * i / n_judge),
                       f"Sorting {len(to_judge)} thread{'' if len(to_judge) == 1 else 's'} with AI")
        verdict = _classify(batch)
        for j, c in enumerate(batch):
            v = verdict.get(str(j), {})
            if isinstance(v, dict) and v.get("decision") == "keep" and v.get("category"):
                ok = apply_category(cfg, c["id"], v["category"],
                                    _labels_cache=all_labels_list)
                if ok:
                    labeled += 1
                else:
                    label_failed += 1

    if label_failed:
        print(f"label-only: labeled {labeled}, {label_failed} failed", file=sys.stderr)

    return {"mode": "label-only", "window_days": window_days,
            "archive_days": archive_days, "considered": len(infos),
            "skipped_already_labeled": skipped_labeled,
            "skipped_handled": skipped_handled, "labeled": labeled,
            "label_failed": label_failed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config_dir")
    ap.add_argument("account_label")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--chunk", type=int, default=100)
    ap.add_argument("--read-workers", type=int, default=DEFAULT_READ_WORKERS,
                    help=f"concurrent Gmail metadata reads (default: {DEFAULT_READ_WORKERS})")
    ap.add_argument("--grace-days", type=int, default=2,
                    help="protect mail newer than N days from review (0 = review everything)")
    ap.add_argument("--label-only", action="store_true",
                    help="don't archive; just apply category labels to recent keepers")
    ap.add_argument("--window-days", type=int, default=30,
                    help="label-only: only consider inbox mail newer than N days")
    ap.add_argument("--archive-days", type=int, default=0,
                    help="label-only: also label archived mail newer than N days (0=off)")
    a = ap.parse_args()

    try:
        me = du._profile_email(a.config_dir)
    except Exception:
        me = a.account_label

    if a.label_only:
        result = _run_label_only(a.config_dir, me, a.window_days, a.chunk,
                                 archive_days=a.archive_days)
        result["account"] = a.account_label
        print(json.dumps(result, ensure_ascii=False))
        return

    _emit_progress(2, "Finding recent mail")
    tids = _thread_ids(a.config_dir, a.grace_days)
    # Reading per-thread metadata is the long silent phase (2 gws calls/thread),
    # so fetch bounded-concurrently while emitting 2→65% as work completes.
    infos = _read_infos_parallel(a.config_dir, tids, me, a.read_workers)

    # Threads the user explicitly restored must never be re-archived.
    keep_set = learning.kept_thread_ids()

    archive_msg_ids, kept, keep_s = [], 0, []
    label_ok = label_failed = 0
    # Deterministic fast-path: last message from the owner -> dealt with -> archive.
    # Guard runs FIRST so restored threads skip both this path and the classifier batch.
    to_judge = []
    for c in infos:
        if c["id"] in keep_set:
            kept += 1  # count as kept; never archive
            continue
        if c["last_from_owner"]:
            archive_msg_ids += c["ids"]
        else:
            to_judge.append(c)

    n_judge = max(len(to_judge), 1)
    for i in range(0, len(to_judge), a.chunk):
        chunk = to_judge[i:i + a.chunk]
        _emit_progress(65 + int(30 * i / n_judge),
                       f"Sorting {len(to_judge)} thread{'' if len(to_judge) == 1 else 's'} with AI")
        verdict = _classify(chunk)
        for j, c in enumerate(chunk):
            # Classifiers always return normalized dicts; fall back to keep on missing key.
            v = verdict.get(str(j), {"decision": "keep", "category": None})
            decision = v.get("decision", "keep") if isinstance(v, dict) else v
            category = v.get("category") if isinstance(v, dict) else None
            if decision == "archive":
                archive_msg_ids += c["ids"]
            else:
                kept += 1
                if len(keep_s) < 25:
                    keep_s.append({"from": c["last_from"], "subject": c["subject"],
                                   "category": category})
                # Apply category label when executing; tally ok/failed (never fatal).
                if a.execute and category:
                    if apply_category(a.config_dir, c["id"], category):
                        label_ok += 1
                    else:
                        label_failed += 1

    if label_failed:
        print(f"keeper: labeled {label_ok}, {label_failed} label failures",
              file=sys.stderr)

    result = {"account": a.account_label, "threads": len(infos),
              "dealt_with_last_from_owner": sum(1 for c in infos if c["last_from_owner"]),
              "to_archive_threads": len(infos) - kept, "to_keep_threads": kept,
              "mode": "execute" if a.execute else "dry-run", "keep_sample": keep_s,
              "label_ok": label_ok, "label_failed": label_failed}

    if a.execute and archive_msg_ids:
        lab = iz._dated_label(iz._BASE_LABEL)
        lid = iz._ensure_label(a.config_dir, lab)
        result["archived_messages"] = iz._batch_modify(a.config_dir, archive_msg_ids,
                                                        add_ids=[lid], remove_ids=["INBOX"])
        result["recovery_label"] = lab

    print(json.dumps(result, ensure_ascii=False))


def _demo():
    """Offline self-check for the backfill partition: --self-check, no network."""
    id_to_name = {"L1": "✉️ Needs reply", "L2": "INBOX", "L3": "⏳ Waiting on others"}
    cat_label_names = {"✉️ Needs reply", "⏳ Waiting on others"}
    infos = [
        {"id": "a", "label_ids": {"L1", "L2"}, "last_from_owner": False},  # already labeled
        {"id": "b", "label_ids": {"L2"}, "last_from_owner": True},         # owner handled
        {"id": "c", "label_ids": {"L2"}, "last_from_owner": False},        # needs classify
        {"id": "d", "label_ids": set(), "last_from_owner": False},         # needs classify
    ]
    to_judge, labeled, handled = _backfill_partition(infos, cat_label_names, id_to_name)
    assert [c["id"] for c in to_judge] == ["c", "d"], to_judge
    assert labeled == 1, labeled
    assert handled == 1, handled
    print("review_open_loops self-check OK")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-check":
        _demo()
    else:
        main()
