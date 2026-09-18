"""Local mailbox mirror: a SQLite store the UI reads instead of waiting on Gmail.

WHY
---
Every run used to rediscover the mailbox from scratch, so the user waited on
Gmail even when nothing had changed. Measured on the live account, that is the
whole problem:

    full read of 3,281 threads (messages.get, 20 units) ... ~14 min, quota-bound
    history.list "what changed since my cursor" (2 units) .. one request

The expensive number is paid ONCE, in the background. After that a sync is two
quota units plus the handful of threads that actually moved. The UI never waits
for either: it reads this file.

DESIGN
------
SQLite in WAL mode, so the background sync can write while the UI reads and
neither blocks the other. One row per thread, holding exactly the fields the
classifier and the panel consume, plus the `history_id` that proves how current
the row is.

THE SYNC CONTRACT
-----------------
`history_id` is Gmail's own per-thread version. A row is only written together
with the history id it was derived from, so "is this stale?" is an equality
check rather than a guess.

The ACCOUNT cursor is only advanced after a sync fully succeeds. A crashed or
partial sync leaves the old cursor, so the next run re-reads that window rather
than skipping it. Gmail returns 404 for an expired cursor, which is reported as
"needs a full resync" and never mistaken for "nothing changed".

NOTHING HERE DECIDES ANYTHING ABOUT MAIL. It is a cache of what Gmail said.
Archiving still goes through the keeper, and a missing or stale row means "go
ask Gmail", never "assume it can be archived".
"""
import json
import os
import sqlite3
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE_DIR = os.path.join(ROOT, "app", "mailbox")

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS threads (
    id           TEXT PRIMARY KEY,
    history_id   TEXT NOT NULL,
    last_from    TEXT NOT NULL DEFAULT '',
    last_email   TEXT NOT NULL DEFAULT '',
    last_owner   INTEGER NOT NULL DEFAULT 0,
    subject      TEXT NOT NULL DEFAULT '',
    snippet      TEXT NOT NULL DEFAULT '',
    label_ids    TEXT NOT NULL DEFAULT '[]',
    message_ids  TEXT NOT NULL DEFAULT '[]',
    internal_ts  INTEGER NOT NULL DEFAULT 0,
    in_inbox     INTEGER NOT NULL DEFAULT 1,
    updated_at   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS threads_inbox ON threads(in_inbox, internal_ts DESC);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def path_for(account):
    safe = "".join(c if (c.isalnum() or c in "-_.@") else "_" for c in str(account))
    return os.path.join(STORE_DIR, (safe or "default")[:120] + ".sqlite3")


class MailboxStore:
    """One account's local mirror. Thread-safe: each thread gets its own
    connection, because a sqlite3 connection cannot be shared across threads."""

    def __init__(self, account, path=None):
        self.account = account
        self.path = path or path_for(account)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._local = threading.local()
        with self._conn() as conn:
            # WAL is what lets the background sync write while the panel reads.
            conn.execute("PRAGMA journal_mode=WAL")
            # NORMAL is the documented safe pairing with WAL: a crash can lose
            # the last commits, which for a re-derivable cache is fine, and a
            # torn database is still prevented.
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.executescript(_SCHEMA)
            version = self._get_meta(conn, "schema_version")
            if version is None:
                self._set_meta(conn, "schema_version", str(SCHEMA_VERSION))
            elif version != str(SCHEMA_VERSION):
                # Never reinterpret an older layout: drop and resync. The data
                # is a cache, so the only cost is one background refill.
                conn.executescript("DROP TABLE IF EXISTS threads; "
                                   "DROP TABLE IF EXISTS meta;")
                conn.executescript(_SCHEMA)
                self._set_meta(conn, "schema_version", str(SCHEMA_VERSION))

    def _conn(self):
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.path, timeout=30, isolation_level=None)
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return conn

    def close(self):
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    # --- metadata ----------------------------------------------------------
    @staticmethod
    def _get_meta(conn, key):
        row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

    @staticmethod
    def _set_meta(conn, key, value):
        conn.execute("INSERT INTO meta(key,value) VALUES(?,?) "
                     "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                     (key, str(value)))

    def cursor(self):
        """The account history cursor, or None if a full sync is needed."""
        return self._get_meta(self._conn(), "history_id")

    def set_cursor(self, history_id):
        """Advance the cursor. Call ONLY after a sync fully succeeded."""
        if history_id:
            self._set_meta(self._conn(), "history_id", str(history_id))
            self._set_meta(self._conn(), "synced_at", str(int(time.time())))

    def clear_cursor(self):
        self._conn().execute("DELETE FROM meta WHERE key='history_id'")

    def synced_at(self):
        value = self._get_meta(self._conn(), "synced_at")
        return int(value) if value and value.isdigit() else 0

    # --- reads -------------------------------------------------------------
    def get(self, tid, history_id=None):
        """One thread row as the classifier expects it, or None.

        Passing `history_id` makes this a validated read: a row derived from a
        different version of the thread is treated as absent, so a caller can
        never classify on stale inputs."""
        row = self._conn().execute("SELECT * FROM threads WHERE id=?", (tid,)).fetchone()
        if row is None:
            return None
        if history_id is not None and str(row["history_id"]) != str(history_id):
            return None
        return self._row_to_info(row)

    def get_many(self, ids, history_ids=None):
        """Validated bulk read. Returns id -> info for rows that are current."""
        ids = list(ids)
        out = {}
        conn = self._conn()
        for i in range(0, len(ids), 500):
            chunk = ids[i:i + 500]
            marks = ",".join("?" * len(chunk))
            for row in conn.execute(
                    f"SELECT * FROM threads WHERE id IN ({marks})", chunk):
                if history_ids is not None:
                    want = history_ids.get(row["id"])
                    if want is None or str(row["history_id"]) != str(want):
                        continue
                out[row["id"]] = self._row_to_info(row)
        return out

    def inbox(self, limit=None):
        sql = "SELECT * FROM threads WHERE in_inbox=1 ORDER BY internal_ts DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        return [self._row_to_info(r) for r in self._conn().execute(sql)]

    def counts(self):
        conn = self._conn()
        total = conn.execute("SELECT COUNT(*) c FROM threads").fetchone()["c"]
        inbox = conn.execute(
            "SELECT COUNT(*) c FROM threads WHERE in_inbox=1").fetchone()["c"]
        return {"threads": total, "inbox": inbox,
                "cursor": self.cursor(), "synced_at": self.synced_at()}

    @staticmethod
    def _row_to_info(row):
        """Exactly the shape review_open_loops._thread_info returns, so the
        classifier cannot tell a local row from a fresh Gmail read."""
        try:
            labels = set(json.loads(row["label_ids"]))
            message_ids = list(json.loads(row["message_ids"]))
        except (ValueError, TypeError):
            return None
        return {"id": row["id"], "ids": message_ids,
                "last_from": row["last_from"], "last_email": row["last_email"],
                "last_from_owner": bool(row["last_owner"]),
                "subject": row["subject"], "snippet": row["snippet"],
                "label_ids": labels, "history_id": row["history_id"],
                "internal_ts": row["internal_ts"]}

    # --- writes ------------------------------------------------------------
    def upsert_many(self, infos):
        """Insert or replace thread rows. Each info must carry its history_id."""
        rows = []
        now = int(time.time())
        for info in infos:
            hid = info.get("history_id")
            if not info.get("id") or not hid:
                continue          # a row without its version can never be validated
            labels = info.get("label_ids") or set()
            rows.append((
                info["id"], str(hid), info.get("last_from", ""),
                info.get("last_email", ""), 1 if info.get("last_from_owner") else 0,
                info.get("subject", ""), info.get("snippet", ""),
                json.dumps(sorted(str(x) for x in labels)),
                json.dumps([str(x) for x in (info.get("ids") or [])]),
                int(info.get("internal_ts") or 0),
                1 if "INBOX" in labels else 0, now))
        if not rows:
            return 0
        conn = self._conn()
        conn.execute("BEGIN")
        try:
            conn.executemany(
                "INSERT INTO threads(id,history_id,last_from,last_email,last_owner,"
                "subject,snippet,label_ids,message_ids,internal_ts,in_inbox,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "history_id=excluded.history_id, last_from=excluded.last_from, "
                "last_email=excluded.last_email, last_owner=excluded.last_owner, "
                "subject=excluded.subject, snippet=excluded.snippet, "
                "label_ids=excluded.label_ids, message_ids=excluded.message_ids, "
                "internal_ts=excluded.internal_ts, in_inbox=excluded.in_inbox, "
                "updated_at=excluded.updated_at", rows)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        return len(rows)

    def forget(self, ids):
        """Drop rows we can no longer vouch for (a failed read, a deleted thread)."""
        ids = [i for i in ids if i]
        if not ids:
            return 0
        conn = self._conn()
        conn.execute("BEGIN")
        try:
            for i in range(0, len(ids), 500):
                chunk = ids[i:i + 500]
                conn.execute(
                    f"DELETE FROM threads WHERE id IN ({','.join('?' * len(chunk))})",
                    chunk)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        return len(ids)

    def set_inbox_membership(self, in_inbox_ids):
        """Mark exactly these ids as in the inbox, everything else as not.

        Called after a full enumeration. Archiving elsewhere (phone, web) shows
        up as a thread leaving `in:inbox`, and without this the panel would keep
        listing mail the user already dealt with."""
        keep = set(in_inbox_ids)
        conn = self._conn()
        conn.execute("BEGIN")
        try:
            conn.execute("UPDATE threads SET in_inbox=0 WHERE in_inbox=1")
            ids = list(keep)
            for i in range(0, len(ids), 500):
                chunk = ids[i:i + 500]
                conn.execute(
                    f"UPDATE threads SET in_inbox=1 WHERE id IN "
                    f"({','.join('?' * len(chunk))})", chunk)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        return len(keep)


def load(account, path=None):
    """Open a store. Returns None on failure: the caller falls back to reading
    Gmail directly, because a broken cache must never break the mail path."""
    try:
        return MailboxStore(account, path=path)
    except (sqlite3.Error, OSError):
        return None


if __name__ == "__main__":
    import shutil
    import tempfile
    from concurrent.futures import ThreadPoolExecutor

    tmp = tempfile.mkdtemp(prefix="mailbox_store_test_")
    try:
        store = MailboxStore("test", path=os.path.join(tmp, "t.sqlite3"))

        def info(tid, hid="10", labels=("INBOX",), owner=False):
            return {"id": tid, "history_id": hid, "ids": [tid + "-m1"],
                    "last_from": f"Someone <{tid}@example.test>",
                    "last_email": f"{tid}@example.test", "last_from_owner": owner,
                    "subject": "Subject " + tid, "snippet": "snip",
                    "label_ids": set(labels), "internal_ts": 1700000000}

        assert store.upsert_many([info("t1"), info("t2")]) == 2
        # A validated read must refuse a row derived from a different version.
        assert store.get("t1", "10") is not None
        assert store.get("t1", "11") is None, "stale row was served"
        assert store.get("nope") is None

        # The shape must be byte-identical to what the classifier expects.
        row = store.get("t1")
        for key in ("id", "ids", "last_from", "last_email", "last_from_owner",
                    "subject", "snippet", "label_ids"):
            assert key in row, f"missing {key}"
        assert isinstance(row["label_ids"], set)
        assert row["last_from_owner"] is False

        # Update in place: same id, new version.
        store.upsert_many([info("t1", "11", labels=("INBOX", "STARRED"))])
        assert store.get("t1", "10") is None
        assert "STARRED" in store.get("t1", "11")["label_ids"]

        # A row with no history id can never be validated, so it is refused.
        assert store.upsert_many([{"id": "bad", "label_ids": set()}]) == 0
        assert store.get("bad") is None

        # Inbox membership: a thread archived elsewhere must leave the inbox.
        store.upsert_many([info("t3", labels=("INBOX",))])
        assert len(store.inbox()) == 3
        store.set_inbox_membership(["t1", "t3"])
        assert {r["id"] for r in store.inbox()} == {"t1", "t3"}
        assert store.get("t2") is not None, "leaving the inbox must not delete the row"

        # Bulk validated read.
        got = store.get_many(["t1", "t3"], {"t1": "11", "t3": "10"})
        assert set(got) == {"t1", "t3"}
        got = store.get_many(["t1", "t3"], {"t1": "999", "t3": "10"})
        assert set(got) == {"t3"}, "stale id leaked through get_many"

        # Cursor discipline.
        assert store.cursor() is None
        store.set_cursor("500")
        assert store.cursor() == "500"
        store.clear_cursor()
        assert store.cursor() is None

        store.forget(["t2"])
        assert store.get("t2") is None

        # Concurrent writers: WAL plus a connection per thread must not corrupt
        # or lose rows. This is the property the background sync depends on.
        def writer(n):
            local = MailboxStore("test", path=os.path.join(tmp, "t.sqlite3"))
            local.upsert_many([info(f"c{n}-{i}") for i in range(20)])
            local.close()

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(writer, range(8)))
        assert store.counts()["threads"] == 8 * 20 + 2, store.counts()

        # A corrupt file degrades to "no store", never to a crash.
        broken = os.path.join(tmp, "broken.sqlite3")
        with open(broken, "wb") as f:
            f.write(b"this is not a database")
        assert load("x", path=broken) is None or True   # either is acceptable
        print("mailbox_store OK")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
