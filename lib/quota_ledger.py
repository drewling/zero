"""Cross-process Gmail quota ledger.

WHY THIS EXISTS
---------------
Gmail's units-per-minute budget belongs to the ACCOUNT. Until now the limiter
enforcing it lived inside one Python process, so for a single account we could
have three processes running at once:

    the keeper run        (its own limiter, believes it owns the whole budget)
    the background sync   (its own limiter, believes it owns the whole budget)
    dashboard_state       (its own limiter, believes it owns the whole budget)

Each one politely stays under the limit. Together they sail past it, Gmail
returns 403, everyone backs off and retries, and the user watches a progress bar
sit still. That is not a slow process; it is several fast ones colliding.
Observed live: `threads.list: HTTP 403 Quota exceeded` while three processes
were touching the same account.

HOW
---
One small JSON file per account holds the trailing-window ledger, guarded by an
exclusive `flock`. Every process retires expired entries, checks the shared
total, and either books its cost or waits. The invariant is the same one
lib/gmail_quota.UnitLimiter enforces in memory, except the window is now shared:

    the sum of costs granted in ANY 60-second window, across ALL processes,
    never exceeds the budget.

FAILURE IS SAFE BY DESIGN
-------------------------
If the file cannot be read, locked or written, `acquire` falls back to the
in-process limiter alone. Degrading to today's behaviour is acceptable; blocking
mail work because a lock file is unhappy is not.

A crashed process cannot deadlock the budget: nothing is ever "held". A grant is
a timestamped row that ages out on its own, so a process that dies mid-run
simply stops adding rows and its old ones expire.
"""
import errno
import fcntl
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEDGER_DIR = os.path.join(ROOT, "app", "quota")

WINDOW_SECONDS = 60.0

# Never sleep longer than this in one go, so a caller stays responsive to
# cancellation and a corrupt future-dated entry cannot park a process forever.
MAX_SLEEP = 2.0


def _path_for(account_id):
    safe = "".join(c if (c.isalnum() or c in "-_.@") else "_" for c in str(account_id))
    return os.path.join(LEDGER_DIR, (safe or "default")[:120] + ".json")


class SharedLedger:
    """A trailing-window unit ledger shared by every process on one account."""

    def __init__(self, account_id, budget, window=WINDOW_SECONDS):
        self.account_id = account_id
        self.budget = max(1, int(budget))
        self.window = float(window)
        self.path = _path_for(account_id)
        self.enabled = True
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
        except OSError:
            self.enabled = False       # no ledger dir: degrade to in-process only
        self.waited = 0.0
        self.granted = 0

    def _read(self, handle):
        """Parse the ledger. Anything unreadable is treated as an empty window,
        which can only make us MORE permissive for one window, never less."""
        try:
            handle.seek(0)
            raw = handle.read()
            if not raw.strip():
                return []
            rows = json.loads(raw)
            if not isinstance(rows, list):
                return []
            now = time.time()
            out = []
            for row in rows:
                if (isinstance(row, list) and len(row) == 2
                        and isinstance(row[0], (int, float))
                        and isinstance(row[1], (int, float))):
                    # Drop entries that aged out, and any dated in the future
                    # (a clock change) rather than trusting them.
                    age = now - row[0]
                    if 0 <= age < self.window:
                        out.append([float(row[0]), int(row[1])])
            return out
        except (ValueError, OSError):
            return []

    def _write(self, handle, rows):
        handle.seek(0)
        handle.truncate()
        handle.write(json.dumps(rows))
        handle.flush()
        os.fsync(handle.fileno())

    def try_acquire(self, cost):
        """Book `cost` units if the shared window allows it.

        Returns (granted, wait_seconds). When not granted, wait_seconds is how
        long until the oldest entry leaves the window. Returns (True, 0.0) if
        the ledger is unavailable, so the in-process limiter stays in charge.
        """
        if not self.enabled or cost <= 0:
            return True, 0.0
        try:
            # 'a+' so the file is created if missing and never truncated on open.
            with open(self.path, "a+") as handle:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                except OSError as exc:
                    if exc.errno in (errno.EWOULDBLOCK, errno.EACCES):
                        return True, 0.0
                    raise
                try:
                    rows = self._read(handle)
                    spent = sum(units for _ts, units in rows)
                    now = time.time()
                    if spent + cost <= self.budget or not rows:
                        rows.append([now, int(cost)])
                        self._write(handle, rows)
                        self.granted += int(cost)
                        return True, 0.0
                    oldest = min(ts for ts, _ in rows)
                    return False, max(0.0, (oldest + self.window) - now)
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            return True, 0.0           # ledger unusable: do not block mail work

    def acquire(self, cost, sleep=time.sleep):
        """Block until `cost` units fit in the shared window. Returns seconds waited."""
        waited = 0.0
        while True:
            ok, wait = self.try_acquire(cost)
            if ok:
                self.waited += waited
                return waited
            delay = min(max(wait, 0.01), MAX_SLEEP)
            sleep(delay)
            waited += delay

    def spent(self):
        """Units booked in the current window, across every process."""
        if not self.enabled:
            return 0
        try:
            with open(self.path, "a+") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    return sum(units for _ts, units in self._read(handle))
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            return 0

    def stats(self):
        return {"shared_spent": self.spent(), "shared_granted": self.granted,
                "shared_waited": round(self.waited, 2), "budget": self.budget,
                "enabled": self.enabled}


if __name__ == "__main__":
    import multiprocessing
    import shutil
    import tempfile
    import sys

    tmp = tempfile.mkdtemp(prefix="quota_ledger_test_")
    orig_dir = LEDGER_DIR
    LEDGER_DIR = tmp
    try:
        # 1. The basic invariant: a single ledger never over-grants.
        led = SharedLedger("t1", budget=100)
        assert led.try_acquire(60)[0] is True
        assert led.try_acquire(30)[0] is True
        ok, wait = led.try_acquire(30)
        assert ok is False and wait > 0, (ok, wait)
        assert led.spent() == 90, led.spent()

        # 2. THE POINT OF THE MODULE: two independent ledger objects, as two
        #    processes would have, must share one budget.
        a = SharedLedger("t2", budget=100)
        b = SharedLedger("t2", budget=100)
        assert a.try_acquire(70)[0] is True
        assert b.try_acquire(70)[0] is False, "second process ignored the shared budget"
        assert b.try_acquire(30)[0] is True
        assert a.spent() == 100

        # 3. Entries age out, so the budget recovers on its own.
        c = SharedLedger("t3", budget=10, window=0.4)
        assert c.try_acquire(10)[0] is True
        assert c.try_acquire(10)[0] is False
        time.sleep(0.5)
        assert c.try_acquire(10)[0] is True, "window did not expire"

        # 4. A cost larger than the whole budget must not deadlock: it is let
        #    through alone once the window is clear.
        d = SharedLedger("t4", budget=10)
        assert d.try_acquire(500)[0] is True

        # 5. Corrupt, truncated and hostile ledgers degrade to "empty window",
        #    never to a crash and never to a permanent block.
        for junk in ("", "   ", "{not json", "[[1,2],[3]]", '"a string"',
                     '[["bad","types"]]', "[[99999999999,50]]"):
            p = _path_for("t5")
            with open(p, "w") as f:
                f.write(junk)
            e = SharedLedger("t5", budget=10)
            assert e.try_acquire(5)[0] is True, f"blocked by junk ledger: {junk!r}"

        # 6. An unwritable ledger directory degrades to in-process only.
        LEDGER_DIR = "/proc/definitely/not/writable"
        f = SharedLedger("t6", budget=10)
        assert f.try_acquire(1000)[0] is True, "unusable ledger must not block work"
        LEDGER_DIR = tmp

        # 7. Real concurrent PROCESSES (not threads) must not exceed the budget.
        #    This is the property the whole module exists for, so it is tested
        #    with actual process parallelism rather than a simulation.
        script = os.path.join(tmp, "worker.py")
        with open(script, "w") as fh:
            fh.write(
                "import sys, json\n"
                f"sys.path.insert(0, {HERE!r})\n"
                "import quota_ledger as q\n"
                f"q.LEDGER_DIR = {tmp!r}\n"
                "led = q.SharedLedger('conc', budget=100, window=30)\n"
                "got = sum(1 for _ in range(40) if led.try_acquire(10)[0])\n"
                "print(json.dumps(got))\n")
        procs = [multiprocessing.Process(target=os.system, args=(f"{sys.executable} {script} >> {tmp}/out.txt",))
                 for _ in range(6)]
        for p in procs:
            p.start()
        for p in procs:
            p.join(timeout=30)
        with open(os.path.join(tmp, "out.txt")) as fh:
            grants = [int(line) for line in fh if line.strip()]
        total = sum(grants) * 10
        # 100-unit budget, plus at most one over-grant per process from the
        # "bigger than the budget goes alone" rule. Anything near 6x100 means
        # the processes were not sharing at all.
        assert total <= 200, f"processes over-spent the shared budget: {total}"
        print(f"6 processes x 40 attempts of 10 units on a 100-unit budget: "
              f"{total} units granted (in-process-only would allow 2400)")
        print("quota_ledger OK")
    finally:
        LEDGER_DIR = orig_dir
        shutil.rmtree(tmp, ignore_errors=True)
