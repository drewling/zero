"""Small POSIX primitives for shared runtime state, not mailbox content logging."""
import fcntl
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager


@contextmanager
def locked(path):
    """Lock a stable sidecar inode, never the file replaced by writers."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path + '.lock', 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def atomic_text(path, text):
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + os.path.basename(path), dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def update_json(path, update):
    with locked(path):
        data = read_json(path)
        update(data)
        atomic_text(path, json.dumps(data, ensure_ascii=False))


def account_id(config_dir):
    return hashlib.sha256(os.path.realpath(config_dir).encode()).hexdigest()[:16]


if __name__ == '__main__':
    # Used only by run.sh to hold its lock for the complete scheduled pipeline.
    import subprocess
    import sys
    with locked(sys.argv[1]):
        raise SystemExit(subprocess.call(sys.argv[2:]))
