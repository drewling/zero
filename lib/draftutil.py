#!/usr/bin/env python3
"""Gmail reply-draft utilities built on the gws CLI.

Subcommands:
  create       Build a reply draft on an existing thread. Prints the draft id.
  send         Send an existing draft by id.
  discard      Delete an existing draft by id.
  update-send  Replace a draft's body then send it (used by the Slack edit flow).

Subject and body are passed base64 (utf-8) to avoid shell-escaping problems.
All gws calls run against the account whose config dir is given, using the
file keyring backend so they work headlessly.
"""
import argparse, base64, html as _html, json, os, subprocess, sys, time
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

GWS = os.environ.get("GWS_BIN", "gws")

_SIG_CACHE = {}  # ponytail: module-level cache, keyed by config_dir

# Transient error patterns that are safe to retry (rate-limit, server-side, network).
# Note: "quota" is deliberately NOT here — Gmail surfaces hard per-project quota
# denials that won't clear in seconds; only genuine rate-limiting (429 / "rate limit")
# is transient.
_RETRYABLE = ("429", "500", "502", "503", "504", "rate limit", "timeout",
              "connection", "reset by peer", "temporarily unavailable")

# Permanent failures — never retry these, even if the message also happens to contain
# a retryable keyword. Checked first so auth/permission always wins over a coincidence.
_FATAL = ("401", "403", "404", "unauthorized", "forbidden", "permission",
          "insufficient", "invalid_grant", "not found", "invalid credentials")


def _fetch_signature(config_dir):
    if config_dir in _SIG_CACHE:
        return _SIG_CACHE[config_dir]
    try:
        data = _gws(config_dir, ["gmail", "users", "settings", "sendAs", "list",
                                  "--params", json.dumps({"userId": "me"})])
        entries = data.get("sendAs", [])
        sig = ""
        fallback = ""
        for e in entries:
            if e.get("isDefault"):
                sig = e.get("signature", "")
                break
            if e.get("isPrimary") and not fallback:
                fallback = e.get("signature", "")
        result = sig if sig else fallback
    except Exception:
        result = ""
    _SIG_CACHE[config_dir] = result
    return result


def _env(config_dir):
    e = dict(os.environ)
    e["GOOGLE_WORKSPACE_CLI_CONFIG_DIR"] = config_dir
    e["GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND"] = "file"
    return e


def _gws(config_dir, args, allow_empty=False, _retries=3):
    """Run a gws subcommand, retrying transient errors with exponential backoff.

    Retries up to _retries times (delays: 1s, 2s, 4s) on 429/5xx/network blips.
    Auth/permission/not-found errors are raised immediately (no retry).
    """
    last_exc = None
    for attempt in range(_retries):
        r = subprocess.run([GWS] + args, capture_output=True, text=True, env=_env(config_dir))
        # Check returncode first — a non-zero exit always means failure.
        if r.returncode != 0:
            err = "\n".join(l for l in r.stderr.splitlines() if "keyring" not in l).strip()
            if not err:
                err = "\n".join(l for l in r.stdout.splitlines() if "keyring" not in l).strip()
            msg = err or f"gws exited with code {r.returncode}"
            msg_lc = msg.lower()
            # Fatal-first: auth/permission/not-found never retry, even if the message
            # also contains a retryable keyword (e.g. a 403 body mentioning "connection").
            if any(p in msg_lc for p in _FATAL):
                raise RuntimeError(msg)
            # Only retry on transient/rate-limit errors.
            if any(p in msg_lc for p in _RETRYABLE) and attempt < _retries - 1:
                last_exc = RuntimeError(msg)
                time.sleep(2 ** attempt)   # 1s, 2s, 4s
                continue
            raise RuntimeError(msg)
        line = "\n".join(l for l in r.stdout.splitlines() if "keyring" not in l)
        if not line.strip():
            # Some endpoints (e.g. drafts.delete) return 204 No Content on success.
            if allow_empty:
                return {}
            err = "\n".join(l for l in r.stderr.splitlines() if "keyring" not in l)
            raise RuntimeError(err or "empty gws response")
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"gws response not valid JSON: {exc} — snippet: {line[:200]!r}"
            ) from exc
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(json.dumps(data["error"]))
        return data
    raise last_exc  # all retries exhausted


def _b64d(s):
    return base64.b64decode(s).decode("utf-8")


def _profile_email(config_dir):
    return _gws(config_dir, ["gmail", "users", "getProfile",
                             "--params", json.dumps({"userId": "me"})])["emailAddress"]


def _thread_reply_headers(config_dir, thread_id):
    """Return (in_reply_to, references) from the latest message in the thread."""
    t = _gws(config_dir, ["gmail", "users", "threads", "get",
                          "--params", json.dumps({"userId": "me", "id": thread_id,
                                                   "format": "metadata",
                                                   "metadataHeaders": ["Message-ID", "References"]})])
    msgs = t.get("messages", []) or []
    if not msgs:
        return None, None
    last = msgs[-1]
    headers = {h["name"].lower(): h["value"] for h in last.get("payload", {}).get("headers", [])}
    mid = headers.get("message-id")
    refs = headers.get("references", "")
    new_refs = (refs + " " + mid).strip() if mid else refs
    return mid, new_refs


def _build_raw(config_dir, thread_id, to, subject, body, html=None):
    """Build a reply. `body` is the plain-text part; if `html` is given, the
    message is multipart/alternative (plain + html) so rich formatting renders in
    clients that support it and degrades gracefully where they don't.
    The account's default Gmail sendAs signature is appended to the HTML part only."""
    msg = EmailMessage()
    msg["From"] = _profile_email(config_dir)
    msg["To"] = to
    subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    msg["Subject"] = subj
    in_reply_to, references = _thread_reply_headers(config_dir, thread_id)
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references
    msg.set_content(body)
    sig = _fetch_signature(config_dir)
    if html and html.strip():
        body_html = html
    elif sig:
        # No HTML body supplied but we have a signature: synthesise one so the sig rides along.
        body_html = _html.escape(body).replace("\n", "<br>")
    else:
        body_html = None
    if body_html is not None:
        sig_block = f"<br><br>{sig}" if sig else ""
        doc = f"<!doctype html><html><body>{body_html}{sig_block}</body></html>"
        msg.add_alternative(doc, subtype="html", charset="utf-8")
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")


def cmd_create(a):
    raw = _build_raw(a.config_dir, a.thread_id, a.to, _b64d(a.subject_b64), _b64d(a.body_b64))
    d = _gws(a.config_dir, ["gmail", "users", "drafts", "create",
                            "--params", json.dumps({"userId": "me"}),
                            "--json", json.dumps({"message": {"raw": raw, "threadId": a.thread_id}})])
    print(d["id"])


def cmd_send(a):
    d = _gws(a.config_dir, ["gmail", "users", "drafts", "send",
                            "--params", json.dumps({"userId": "me"}),
                            "--json", json.dumps({"id": a.draft_id})])
    print(json.dumps({"ok": True, "id": d.get("id")}))


def cmd_discard(a):
    _gws(a.config_dir, ["gmail", "users", "drafts", "delete",
                        "--params", json.dumps({"userId": "me", "id": a.draft_id})],
         allow_empty=True)
    print(json.dumps({"ok": True}))


def cmd_update(a):
    """Update a draft's body in place without sending. Prints the draft id."""
    raw = _build_raw(a.config_dir, a.thread_id, a.to, _b64d(a.subject_b64), _b64d(a.body_b64))
    d = _gws(a.config_dir, ["gmail", "users", "drafts", "update",
                            "--params", json.dumps({"userId": "me", "id": a.draft_id}),
                            "--json", json.dumps({"message": {"raw": raw,
                                                              "threadId": a.thread_id}})])
    print(d.get("id") or a.draft_id)


def cmd_update_send(a):
    # Reaching update-send means the user edited the system's draft before sending,
    # so capture it as a voice signal (original vs final) for the learning rollup.
    orig = ""
    try:
        g = _gws(a.config_dir, ["gmail", "users", "drafts", "get",
                                "--params", json.dumps({"userId": "me", "id": a.draft_id,
                                                        "format": "metadata"})])
        orig = ((g.get("message") or {}).get("snippet") or "")
    except Exception:
        pass
    final = _b64d(a.body_b64)
    raw = _build_raw(a.config_dir, a.thread_id, a.to, _b64d(a.subject_b64), final)
    _gws(a.config_dir, ["gmail", "users", "drafts", "update",
                        "--params", json.dumps({"userId": "me", "id": a.draft_id}),
                        "--json", json.dumps({"message": {"raw": raw, "threadId": a.thread_id}})])
    d = _gws(a.config_dir, ["gmail", "users", "drafts", "send",
                            "--params", json.dumps({"userId": "me"}),
                            "--json", json.dumps({"id": a.draft_id})])
    try:
        import learning
        learning.record({"type": "draft_edit", "thread_id": a.thread_id,
                         "original_snippet": orig, "final": final})
    except Exception:
        pass
    print(json.dumps({"ok": True, "id": d.get("id")}))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create"); c.add_argument("--config-dir", dest="config_dir", required=True)
    c.add_argument("--thread-id", dest="thread_id", required=True)
    c.add_argument("--to", required=True)
    c.add_argument("--subject-b64", dest="subject_b64", required=True)
    c.add_argument("--body-b64", dest="body_b64", required=True)
    c.set_defaults(func=cmd_create)

    s = sub.add_parser("send"); s.add_argument("--config-dir", dest="config_dir", required=True)
    s.add_argument("--draft-id", dest="draft_id", required=True)
    s.set_defaults(func=cmd_send)

    d = sub.add_parser("discard"); d.add_argument("--config-dir", dest="config_dir", required=True)
    d.add_argument("--draft-id", dest="draft_id", required=True)
    d.set_defaults(func=cmd_discard)

    up = sub.add_parser("update"); up.add_argument("--config-dir", dest="config_dir", required=True)
    up.add_argument("--draft-id", dest="draft_id", required=True)
    up.add_argument("--thread-id", dest="thread_id", required=True)
    up.add_argument("--to", required=True)
    up.add_argument("--subject-b64", dest="subject_b64", required=True)
    up.add_argument("--body-b64", dest="body_b64", required=True)
    up.set_defaults(func=cmd_update)

    u = sub.add_parser("update-send"); u.add_argument("--config-dir", dest="config_dir", required=True)
    u.add_argument("--draft-id", dest="draft_id", required=True)
    u.add_argument("--thread-id", dest="thread_id", required=True)
    u.add_argument("--to", required=True)
    u.add_argument("--subject-b64", dest="subject_b64", required=True)
    u.add_argument("--body-b64", dest="body_b64", required=True)
    u.set_defaults(func=cmd_update_send)

    a = p.parse_args()
    try:
        a.func(a)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
