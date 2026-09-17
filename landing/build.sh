#!/usr/bin/env bash
# build.sh — build and smoke-test the landing-page image.
#
# The homepage's primary call to action is
#   curl -fsSL https://zero.headless.com/install | bash
# so this script does not just build: it starts the image and proves that URL
# actually works before you ship it. A broken /install means the headline CTA is
# a dead command, which is exactly the bug this script exists to catch.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
IMAGE="${1:-zero-landing}"
PORT="${PORT:-8099}"

command -v docker >/dev/null || { echo "ERROR: docker not found." >&2; exit 1; }

# The installer lives in the repo and is served by redirect, not baked into the
# image — but if it's broken, the site is pointing people at a broken script.
bash -n "$REPO/macapp/install-zero.sh" \
  || { echo "ERROR: macapp/install-zero.sh has a syntax error." >&2; exit 1; }
echo "ok  installer parses"

docker build -t "$IMAGE" "$HERE"
echo "ok  built image: $IMAGE"

# ---------------------------------------------------------------------------
# Smoke test: run it and check the routes that matter.
# ---------------------------------------------------------------------------
CID="$(docker run -d --rm -p "$PORT:80" "$IMAGE")"
cleanup() { docker stop "$CID" >/dev/null 2>&1 || true; }
trap cleanup EXIT

for _ in $(seq 1 25); do
  curl -fsS -o /dev/null "http://127.0.0.1:$PORT/" 2>/dev/null && break
  sleep 0.4
done

fail=0
check() { # check <label> <actual> <expected>
  if [ "$2" = "$3" ]; then printf '    ok  %-34s %s\n' "$1" "$2"
  else printf '    FAIL %-33s got %s, want %s\n' "$1" "$2" "$3"; fail=1; fi
}

check "homepage" \
  "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/")" "200"
check "/install redirects" \
  "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/install")" "302"
check "/install.sh redirects" \
  "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/install.sh")" "302"
check "privacy" \
  "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/privacy.html")" "200"
check "terms" \
  "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/terms.html")" "200"
check "unknown path 404s" \
  "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/nope")" "404"

# The real test: follow the redirect the way `curl -fsSL` does and confirm a
# usable script comes back.
body="$(curl -fsSL "http://127.0.0.1:$PORT/install" 2>/dev/null || true)"
if printf '%s' "$body" | head -1 | grep -q '^#!/usr/bin/env bash'; then
  echo "    ok  /install returns a bash script ($(printf '%s' "$body" | wc -l | tr -d ' ') lines)"
  printf '%s' "$body" | bash -n && echo "    ok  and it parses"
else
  echo "    FAIL /install did not return a shell script"; fail=1
fi

[ "$fail" -eq 0 ] || { echo; echo "SMOKE TEST FAILED — do not deploy."; exit 1; }
echo
echo "All checks passed. Deploy $IMAGE."
