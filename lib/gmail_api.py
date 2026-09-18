"""Direct Gmail HTTP transport: pooled connections, batch requests, own auth.

WHY THIS REPLACES SHELLING OUT TO gws
-------------------------------------
Measured on the live account (3,281-thread inbox), reading thread metadata:

    per-thread `gws` subprocess, 16 workers ......    2.4 threads/sec
    this module, batch of 100, 8 workers ......... 1,266 threads/sec

`gws` is a fine CLI and a terrible inner loop. Every invocation re-parses a
217KB discovery document, decrypts credentials and opens a fresh TLS
connection: ~830ms of local overhead to wrap a ~46ms API call, an 18x tax, paid
once per thread. This module pays that setup ONCE per process instead.

Two mechanisms do the work:

  1. **Connection reuse.** One pooled HTTPS connection per worker, so the TLS
     handshake is amortised instead of repeated.
  2. **Gmail's batch endpoint.** Up to 100 sub-requests inside one HTTP request
     (https://developers.google.com/workspace/gmail/api/guides/batch). One round
     trip returns 100 threads.

WHAT THIS DOES NOT CHANGE
-------------------------
Quota. Batching is a TRANSPORT optimisation: Google bills each sub-request
individually, so 100 batched `threads.get` calls still cost 100 x 40 units. The
UnitLimiter in lib/gmail_quota.py therefore still governs, and this module
charges it per sub-request, not per HTTP request. Getting that wrong would turn
a 6,000 units/minute budget into a 600,000 unit stampede.

Credentials are gws's own, read from its config dir. We never write them, never
log them, and never take over the login flow: `gws auth login` remains the only
way tokens are created. If anything here fails, callers fall back to gws.
"""
import base64
import json
import os
import threading
import time
import urllib.parse
import http.client

HERE = os.path.dirname(os.path.abspath(__file__))
import aesgcm                     # noqa: E402
import gmail_quota as gq          # noqa: E402
import run_metrics as metrics     # noqa: E402

GMAIL_HOST = "gmail.googleapis.com"
OAUTH_HOST = "oauth2.googleapis.com"
API = "/gmail/v1"

# Google's documented ceiling for one batch request. Exceeding it is rejected,
# and large batches also mean a bigger blast radius per failure.
MAX_BATCH = 100

# Refresh this long before the token actually expires, so a long batch cannot
# start with a valid token and finish with an expired one.
TOKEN_SKEW_SECONDS = 300


class GmailError(Exception):
    """A Gmail API or transport failure. Callers may fall back to gws."""


class AuthUnavailable(GmailError):
    """Credentials could not be read. The caller MUST fall back to gws."""


# --- credentials -------------------------------------------------------------
def _read_encrypted(config_dir, name):
    """Decrypt one AES-256-GCM blob from a gws config dir (12-byte nonce prefix)."""
    path = os.path.join(config_dir, name)
    key_path = os.path.join(config_dir, ".encryption_key")
    try:
        with open(key_path) as f:
            key = base64.b64decode(f.read().strip())
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as exc:
        raise AuthUnavailable(f"cannot read {name}: {exc}") from exc
    if len(raw) < 13:
        raise AuthUnavailable(f"{name} is too short to be a GCM blob")
    try:
        return json.loads(aesgcm.decrypt(key, raw[:12], raw[12:]))
    except aesgcm.DecryptError as exc:
        raise AuthUnavailable(f"cannot decrypt {name}: {exc}") from exc
    except ValueError as exc:
        raise AuthUnavailable(f"{name} did not contain JSON: {exc}") from exc


class _Token:
    """One account's access token, refreshed on demand and shared by workers."""

    def __init__(self, config_dir):
        self.config_dir = config_dir
        self._lock = threading.Lock()
        self._value = None
        self._expires = 0.0

    def _refresh(self):
        cred = _read_encrypted(self.config_dir, "credentials.enc")
        missing = [k for k in ("client_id", "client_secret", "refresh_token")
                   if not cred.get(k)]
        if missing:
            raise AuthUnavailable(f"credentials missing {', '.join(missing)}")
        body = urllib.parse.urlencode({
            "client_id": cred["client_id"], "client_secret": cred["client_secret"],
            "refresh_token": cred["refresh_token"], "grant_type": "refresh_token",
        }).encode()
        conn = http.client.HTTPSConnection(OAUTH_HOST, timeout=30)
        try:
            with metrics.measured("oauth.refresh", self.config_dir):
                conn.request("POST", "/token", body=body,
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
                resp = conn.getresponse()
                payload = resp.read()
        except OSError as exc:
            raise GmailError(f"token refresh failed: {exc}") from exc
        finally:
            conn.close()
        if resp.status != 200:
            # Deliberately does NOT include the response body: it can echo the
            # client secret back on some error paths.
            raise AuthUnavailable(f"token refresh returned HTTP {resp.status}")
        try:
            data = json.loads(payload)
        except ValueError as exc:
            raise GmailError("token refresh returned non-JSON") from exc
        token = data.get("access_token")
        if not token:
            raise AuthUnavailable("token refresh returned no access_token")
        self._value = token
        self._expires = time.time() + float(data.get("expires_in", 3600))

    def get(self):
        with self._lock:
            if self._value is None or time.time() >= self._expires - TOKEN_SKEW_SECONDS:
                self._refresh()
            return self._value

    def invalidate(self):
        """Force the next get() to refresh. Called on a 401."""
        with self._lock:
            self._value = None


_tokens = {}
_tokens_lock = threading.Lock()


def _token_for(config_dir):
    key = os.path.realpath(config_dir)
    with _tokens_lock:
        tok = _tokens.get(key)
        if tok is None:
            tok = _tokens[key] = _Token(key)
        return tok


# --- connection pool ---------------------------------------------------------
class _Pool:
    """Bounded pool of keep-alive HTTPS connections to one host."""

    def __init__(self, host, size=8):
        self.host = host
        self.size = size
        self._free = []
        self._lock = threading.Lock()

    def take(self, timeout):
        with self._lock:
            while self._free:
                conn = self._free.pop()
                if conn.sock is not None:
                    conn.timeout = timeout
                    return conn, True
                conn.close()
        return http.client.HTTPSConnection(self.host, timeout=timeout), False

    def give(self, conn, reusable):
        if not reusable:
            conn.close()
            return
        with self._lock:
            if len(self._free) < self.size:
                self._free.append(conn)
                return
        conn.close()

    def drain(self):
        with self._lock:
            conns, self._free = self._free, []
        for conn in conns:
            conn.close()


_pools = {}
_pools_lock = threading.Lock()


def _pool_for(host):
    with _pools_lock:
        pool = _pools.get(host)
        if pool is None:
            pool = _pools[host] = _Pool(host)
        return pool


def close_all():
    """Drop every pooled connection. For clean shutdown and tests."""
    with _pools_lock:
        pools = list(_pools.values())
    for pool in pools:
        pool.drain()


# --- request plumbing --------------------------------------------------------
def _request(config_dir, method, path, body=None, content_type=None,
             timeout=60, _retry=True):
    """One authenticated HTTP request on a pooled connection.

    Returns (status, body_bytes, content_type_header). The response's own
    Content-Type is returned because a batch reply carries the server-chosen
    multipart boundary there, and it cannot be recovered reliably from the body.

    Retries ONCE on 401 (expired token) and once on a dropped keep-alive
    connection, because a pooled socket the server closed between requests is
    normal and not an error worth surfacing."""
    token = _token_for(config_dir).get()
    pool = _pool_for(GMAIL_HOST)
    conn, reused = pool.take(timeout)
    headers = {"Authorization": "Bearer " + token,
               "Accept-Encoding": "gzip, deflate"}
    if content_type:
        headers["Content-Type"] = content_type
    reusable = False
    try:
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        status = resp.status
        reusable = not resp.will_close
        encoding = (resp.getheader("Content-Encoding") or "").lower()
        reply_type = resp.getheader("Content-Type") or ""
    except (http.client.HTTPException, OSError) as exc:
        conn.close()
        # A reused socket the server had already closed: retry once on a fresh
        # one. A failure on a BRAND NEW connection is a real error.
        if reused and _retry:
            return _request(config_dir, method, path, body, content_type,
                            timeout, _retry=False)
        raise GmailError(f"{method} {path.split('?')[0]} failed: {exc}") from exc
    finally:
        pool.give(conn, reusable)

    if encoding in ("gzip", "deflate") and raw:
        import gzip
        import zlib
        try:
            raw = gzip.decompress(raw) if encoding == "gzip" else zlib.decompress(raw)
        except (OSError, zlib.error) as exc:
            raise GmailError(f"could not decompress {encoding} response: {exc}") from exc

    if status == 401 and _retry:
        _token_for(config_dir).invalidate()
        return _request(config_dir, method, path, body, content_type,
                        timeout, _retry=False)
    return status, raw, reply_type


def _check(status, raw, what):
    if status == 200:
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise GmailError(f"{what}: non-JSON 200 response") from exc
    detail = ""
    try:
        detail = json.loads(raw).get("error", {}).get("message", "")
    except Exception:
        detail = raw[:200].decode("utf-8", "replace") if isinstance(raw, bytes) else ""
    raise GmailError(f"{what}: HTTP {status} {detail}")


def _spend(config_dir, method, count=1, limiter=None):
    """Charge the quota ledger. Batching does not make sub-requests free."""
    units = gq.cost_of(method) * count
    if limiter is not None:
        limiter.acquire(units)
    metrics.record("gmail." + method, config_dir, calls=count,
                   quota_units_estimated=units)
    return units


# --- public API --------------------------------------------------------------
def available(config_dir):
    """Whether direct access can be used for this account. Never raises."""
    try:
        _token_for(config_dir).get()
        return True
    except (GmailError, OSError):
        return False


def get_profile(config_dir, limiter=None):
    _spend(config_dir, "getProfile", 1, limiter)
    status, raw, _ = _request(config_dir, "GET", f"{API}/users/me/profile")
    return _check(status, raw, "getProfile")


def list_threads(config_dir, query, limiter=None, page_limit=50):
    """Every thread matching `query`, paginated. Returns the raw thread stubs,
    each carrying the per-thread historyId the caches use as a change detector."""
    out = []
    token = None
    for _ in range(page_limit):
        params = {"q": query, "maxResults": 500}
        if token:
            params["pageToken"] = token
        _spend(config_dir, "threads.list", 1, limiter)
        status, raw, _ = _request(
            config_dir, "GET",
            f"{API}/users/me/threads?{urllib.parse.urlencode(params)}")
        data = _check(status, raw, "threads.list")
        out.extend(data.get("threads", []) or [])
        token = data.get("nextPageToken")
        if not token:
            break
    return out


def list_messages(config_dir, query, limiter=None, page_limit=100):
    out = []
    token = None
    for _ in range(page_limit):
        params = {"q": query, "maxResults": 500}
        if token:
            params["pageToken"] = token
        _spend(config_dir, "messages.list", 1, limiter)
        status, raw, _ = _request(
            config_dir, "GET",
            f"{API}/users/me/messages?{urllib.parse.urlencode(params)}")
        data = _check(status, raw, "messages.list")
        out.extend(data.get("messages", []) or [])
        token = data.get("nextPageToken")
        if not token:
            break
    return out


def _parse_batch(raw, boundary, count):
    """Split a multipart/mixed batch response into per-sub-request results.

    Returns a list of (status, parsed_json_or_None) in Content-ID order. A
    sub-request that failed yields its own status, so one bad thread never
    invalidates the other 99.

    Each part looks like:

        Content-Type: application/http
        Content-ID: <response-0>
        <blank>
        HTTP/1.1 200 OK
        Content-Type: application/json
        <blank>
        {...body...}

    so there are THREE header blocks, not two: the part's own headers, the
    embedded response's status line plus headers, and then the body.
    """
    results = [None] * count
    marker = b"--" + boundary.encode()
    for part in raw.split(marker):
        stripped = part.strip()
        if not stripped or stripped == b"--":
            continue
        # 1) the part's own headers, up to the first blank line
        split = part.split(b"\r\n\r\n", 1)
        if len(split) < 2:
            continue
        part_headers, remainder = split
        index = None
        for line in part_headers.split(b"\r\n"):
            if line.lower().startswith(b"content-id:"):
                # Google echoes our id back with a "response-" prefix.
                tag = line.split(b":", 1)[1].strip().strip(b"<>")
                digits = bytes(c for c in tag if 48 <= c <= 57)
                if digits:
                    index = int(digits)
        # 2) the embedded HTTP response: status line + its own headers, then body
        inner = remainder.split(b"\r\n\r\n", 1)
        head = inner[0]
        body = inner[1] if len(inner) > 1 else b""
        status_line = head.split(b"\r\n", 1)[0]
        try:
            status = int(status_line.split(b" ")[1])
        except (IndexError, ValueError):
            continue
        parsed = None
        text = body.strip()
        if text.startswith(b"{"):
            try:
                parsed = json.loads(text)
            except ValueError:
                parsed = None
        if index is not None and 0 <= index < count:
            results[index] = (status, parsed)
    return results


def batch_get(config_dir, kind, ids, params=None, limiter=None, timeout=180):
    """Fetch up to MAX_BATCH threads/messages in ONE HTTP request.

    `kind` is "threads" or "messages". Returns a dict of id -> resource for
    everything that succeeded; ids that failed are simply absent, so the caller
    re-reads or skips them rather than acting on partial data.
    """
    ids = list(ids)
    if not ids:
        return {}
    if len(ids) > MAX_BATCH:
        raise ValueError(f"batch of {len(ids)} exceeds Gmail's limit of {MAX_BATCH}")
    method = f"{kind}.get"
    # Charge PER SUB-REQUEST: Google bills each one, batching only saves round trips.
    _spend(config_dir, method, len(ids), limiter)

    query = "?" + urllib.parse.urlencode(params, doseq=True) if params else ""
    boundary = "zero_batch_" + base64.urlsafe_b64encode(os.urandom(9)).decode()
    chunks = []
    for i, rid in enumerate(ids):
        chunks.append(
            f"--{boundary}\r\n"
            f"Content-Type: application/http\r\n"
            f"Content-ID: <{i}>\r\n\r\n"
            f"GET {API}/users/me/{kind}/{urllib.parse.quote(str(rid))}{query}\r\n\r\n")
    payload = ("".join(chunks) + f"--{boundary}--\r\n").encode()

    with metrics.measured(f"gmail.batch.{method}", config_dir, sub_requests=len(ids)):
        status, raw, reply_type = _request(
            config_dir, "POST", "/batch/gmail/v1", body=payload,
            content_type=f"multipart/mixed; boundary={boundary}", timeout=timeout)
    if status != 200:
        raise GmailError(f"batch {method}: HTTP {status}")

    # The reply boundary is chosen by the SERVER and announced in the response's
    # Content-Type. Do not try to recover it from the body: the payload begins
    # with a blank line, so splitting on the first line yields "".
    reply_boundary = None
    if "boundary=" in reply_type:
        reply_boundary = reply_type.split("boundary=", 1)[1].strip().strip('"').split(";")[0]
    if not reply_boundary:
        for line in raw[:2000].split(b"\r\n"):
            if line.startswith(b"--") and len(line) > 2:
                reply_boundary = line[2:].decode("utf-8", "replace")
                break
    if not reply_boundary:
        raise GmailError("batch response had no multipart boundary")

    out = {}
    failures = 0
    throttled = 0
    for i, result in enumerate(_parse_batch(raw, reply_boundary, len(ids))):
        if not result:
            failures += 1
            continue
        sub_status, parsed = result
        if sub_status == 200 and isinstance(parsed, dict):
            out[ids[i]] = parsed
        else:
            failures += 1
            if sub_status in (403, 429):
                throttled += 1
    if throttled and limiter is not None:
        # Slow down, but do not seize up. penalise() defaults to booking HALF the
        # whole budget, which is right for a single unexpected 429 on one call
        # and catastrophic here: two throttled batches would book the entire
        # minute and every worker would sleep out the window (measured: 60s of
        # dead time). Charge in proportion to how much of the batch was actually
        # refused instead, so repeated throttling paces the run rather than
        # stopping it.
        share = throttled / float(len(ids))
        limiter.penalise(int(limiter.budget * 0.1 * share) or 1)
    if failures:
        metrics.record(f"gmail.batch.{method}", config_dir, sub_failures=failures,
                       sub_throttled=throttled)
    return out


def batch_get_all(config_dir, kind, ids, params=None, limiter=None,
                  workers=8, progress=None, max_attempts=5):
    """batch_get over any number of ids, several batches in flight at once.

    Returns id -> resource. Ids throttled with 429 are RETRIED with backoff
    rather than dropped: measured on the live account, a 100-id batch commonly
    comes back part 200 and part 429, and treating those as permanent failures
    would silently lose half the inbox. A thread only stays absent if it still
    fails after max_attempts, and the caller must then leave it untouched.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    ids = list(ids)
    if not ids:
        return {}
    out = {}
    pending = ids
    for attempt in range(max_attempts):
        chunks = [pending[i:i + MAX_BATCH] for i in range(0, len(pending), MAX_BATCH)]
        done = 0
        active = max(1, min(workers, len(chunks)))
        with ThreadPoolExecutor(max_workers=active,
                                thread_name_prefix="gmail-batch") as pool:
            futures = [pool.submit(batch_get, config_dir, kind, chunk, params, limiter)
                       for chunk in chunks]
            for future in as_completed(futures):
                try:
                    out.update(future.result())
                except GmailError:
                    pass      # those ids stay pending and are retried below
                done += 1
                if progress:
                    progress(len(out), len(ids))
        pending = [i for i in pending if i not in out]
        if not pending:
            break
        # Throttled, not broken. Sleep on Google's documented schedule before
        # the next sweep, and shrink concurrency so we stop pushing as hard.
        if attempt < max_attempts - 1:
            workers = max(1, workers // 2)
            delay = gq.backoff_delay(attempt)
            metrics.record(f"gmail.batch.{kind}.get", config_dir,
                           retry_sweeps=1, retry_ids=len(pending),
                           backoff_seconds=delay)
            time.sleep(delay)
    if pending:
        metrics.record(f"gmail.batch.{kind}.get", config_dir,
                       unresolved_ids=len(pending))
    return out


def modify_messages(config_dir, message_ids, add_labels=None, remove_labels=None,
                    limiter=None):
    """messages.batchModify in 1,000-id chunks. Returns the number modified."""
    ids = [m for m in message_ids if m]
    if not ids:
        return 0
    body = {"addLabelIds": list(add_labels or []),
            "removeLabelIds": list(remove_labels or [])}
    total = 0
    for i in range(0, len(ids), 1000):
        chunk = ids[i:i + 1000]
        _spend(config_dir, "messages.batchModify", 1, limiter)
        payload = json.dumps(dict(body, ids=chunk)).encode()
        status, raw, _ = _request(config_dir, "POST",
                                  f"{API}/users/me/messages/batchModify",
                                  body=payload, content_type="application/json")
        if status not in (200, 204):
            raise GmailError(f"batchModify: HTTP {status}")
        total += len(chunk)
    return total


def list_labels(config_dir, limiter=None):
    _spend(config_dir, "labels.list", 1, limiter)
    status, raw, _ = _request(config_dir, "GET", f"{API}/users/me/labels")
    return _check(status, raw, "labels.list").get("labels", []) or []


def history_since(config_dir, start_history_id, limiter=None, page_limit=50):
    """Raw history records since a cursor, or None if the cursor is too old.

    None means "do a full read": Gmail returns 404 for an expired startHistoryId
    and the caller must not mistake that for "nothing changed"."""
    records = []
    token = None
    for _ in range(page_limit):
        params = {"startHistoryId": str(start_history_id), "maxResults": 500}
        if token:
            params["pageToken"] = token
        _spend(config_dir, "history.list", 1, limiter)
        status, raw, _ = _request(
            config_dir, "GET",
            f"{API}/users/me/history?{urllib.parse.urlencode(params)}")
        if status == 404:
            return None
        data = _check(status, raw, "history.list")
        records.extend(data.get("history", []) or [])
        token = data.get("nextPageToken")
        if not token:
            return records
    return records


if __name__ == "__main__":
    import sys
    # Live smoke test against a real account. READ-ONLY: lists and reads only,
    # never modifies. Usage: python3 lib/gmail_api.py <gws-config-dir>
    if len(sys.argv) < 2:
        print("usage: gmail_api.py <gws-config-dir>")
        raise SystemExit(2)
    cfg = sys.argv[1]
    if not available(cfg):
        print("direct access unavailable for this account (would fall back to gws)")
        raise SystemExit(1)
    # Batching saves round trips, NOT quota: 3,281 threads.get is 131,240 units
    # against a 4,800/min budget however it is transported. Without a limiter
    # this smoke test just earns a 403, which is itself the proof that the
    # binding constraint moved from transport back to quota.
    limiter = gq.UnitLimiter()
    start = time.time()
    profile = get_profile(cfg, limiter)
    print(f"getProfile {time.time() - start:.3f}s  "
          f"{profile.get('messagesTotal')} messages, historyId {profile.get('historyId')}")
    start = time.time()
    threads = list_threads(cfg, "in:inbox", limiter)
    enumerate_s = time.time() - start
    print(f"enumerate  {enumerate_s:.3f}s  {len(threads)} inbox threads")
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    if threads:
        ids = [t["id"] for t in threads][:limit]
        start = time.time()
        got = batch_get_all(cfg, "threads", ids,
                            {"format": "metadata",
                             "metadataHeaders": ["From", "Subject"]},
                            limiter=limiter)
        read_s = time.time() - start
        print(f"read {len(ids):>5} {read_s:.3f}s  {len(got)}/{len(ids)} threads "
              f"({len(ids) / read_s:.0f}/sec)")
        sample = got.get(ids[0])
        if sample:
            headers = (sample.get("messages", [{}])[-1]
                       .get("payload", {}).get("headers", []))
            names = {h["name"] for h in headers}
            print(f"  sanity: newest message carries {sorted(names)}, "
                  f"historyId {sample.get('historyId')}")
        print(f"  quota spent: {limiter.stats()}")
    close_all()
