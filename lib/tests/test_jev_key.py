#!/usr/bin/env python3
"""Tests for Jev API-key storage (lib/jev.py set_key/_get_key/available).

Why this exists: the packaged app ships no `.env` (macapp/build.sh excludes it),
so before app/jev_key was added there was NO way to configure Jev outside a
source checkout. These tests pin the behavior that makes BYO-key work in the
installed app, and the file permissions that keep the key private.

Runs fully offline — no network, no real key. verify_key() is covered separately
because it needs a live service.
"""
import importlib
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)


def _fresh_jev(root):
    """Import lib/jev.py with ROOT pointed at a throwaway dir, so tests never
    touch the real repo or the user's installed app data."""
    libdir = os.path.join(root, "lib")
    os.makedirs(libdir, exist_ok=True)
    for name in ("jev.py", "run_metrics.py", "runtime_state.py"):
        shutil.copy(os.path.join(LIB, name), os.path.join(libdir, name))
    sys.path.insert(0, libdir)
    if "jev" in sys.modules:
        del sys.modules["jev"]
    import jev
    importlib.reload(jev)
    return jev


def main():
    failures = []

    def check(label, cond):
        if cond:
            print(f"  ok   {label}")
        else:
            print(f"  FAIL {label}")
            failures.append(label)

    root = tempfile.mkdtemp()
    os.environ.pop("JEV", None)
    jev = _fresh_jev(root)

    print("jev key storage")
    check("no key configured on a fresh install", jev.available() is False)
    check("key path lives under app/", jev.KEY_PATH.endswith(os.path.join("app", "jev_key")))

    # Save
    check("set_key reports configured", jev.set_key("test-key-abcdefgh") is True)
    check("available() is now True", jev.available() is True)
    check("key round-trips", jev._get_key() == "test-key-abcdefgh")
    mode = oct(os.stat(jev.KEY_PATH).st_mode & 0o777)
    check(f"key file is 0600 (got {mode})", mode == "0o600")

    # Whitespace is stripped: users paste keys with trailing newlines constantly.
    jev.set_key("  padded-key-123  \n")
    check("surrounding whitespace stripped", jev._get_key() == "padded-key-123")

    # Overwrite
    jev.set_key("second-key-xyz12")
    check("overwriting replaces the old key", jev._get_key() == "second-key-xyz12")

    # Remove
    check("blank key removes it", jev.set_key("") is False)
    check("available() is False after removal", jev.available() is False)
    check("key file is gone", not os.path.exists(jev.KEY_PATH))

    # Precedence: env beats the stored file, so a one-off run can override.
    jev.set_key("stored-key-aaaa")
    os.environ["JEV"] = "env-key-bbbb"
    jev._key_cache.update({"loaded": False, "value": None})
    check("env JEV wins over the stored file", jev._get_key() == "env-key-bbbb")
    os.environ.pop("JEV", None)
    jev._key_cache.update({"loaded": False, "value": None})
    check("stored key used again once env is unset", jev._get_key() == "stored-key-aaaa")

    # A corrupt/unreadable key dir must not crash callers.
    jev.set_key("")
    os.makedirs(jev.KEY_PATH, exist_ok=True)   # a DIRECTORY where the file should be
    jev._key_cache.update({"loaded": False, "value": None})
    check("unreadable key path degrades to 'no key' instead of raising",
          jev.available() is False)
    os.rmdir(jev.KEY_PATH)

    shutil.rmtree(root, ignore_errors=True)

    print()
    if failures:
        print(f"FAILED ({len(failures)}): {', '.join(failures)}")
        return 1
    print("all jev key-storage tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
