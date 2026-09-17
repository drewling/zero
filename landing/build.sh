#!/usr/bin/env bash
# build.sh — build the landing-page image.
#
# Exists because the homepage advertises
#   curl -fsSL https://zero.headless.com/install | bash
# and that URL has to serve the REAL installer. Docker can only COPY files from
# inside the build context, so the canonical script at macapp/install-zero.sh is
# staged here as ./install first. Without this step the image builds without an
# installer and the command on the homepage 404s.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
SRC="$REPO/macapp/install-zero.sh"
IMAGE="${1:-zero-landing}"

[ -f "$SRC" ] || { echo "ERROR: missing $SRC" >&2; exit 1; }

# Fail early rather than shipping an installer that can't run.
bash -n "$SRC" || { echo "ERROR: $SRC has a syntax error; refusing to publish it." >&2; exit 1; }

cp "$SRC" "$HERE/install"
echo "staged install-zero.sh -> landing/install"

docker build -t "$IMAGE" "$HERE"
echo "built image: $IMAGE"

cat <<EOF

Run it locally with:
  docker run --rm -p 8080:80 $IMAGE

Then check the install URL actually resolves:
  curl -fsSL http://localhost:8080/install | head -5
EOF
