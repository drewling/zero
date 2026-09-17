#!/usr/bin/env bash
# deploy.sh — push the landing image to the server behind zero.headless.com.
#
# Why this exists: the homepage's primary call to action is
#   curl -fsSL https://zero.headless.com/install | bash
# and that URL 404s until this image is deployed. build.sh proves the image is
# good; this puts it live and then checks the live URL, so "deployed" is a fact
# rather than an assumption.
#
# The host is a GCP VM (34.66.84.21) running nginx. Pick whichever transport you
# actually use by setting ZERO_DEPLOY_TARGET:
#
#   ssh     — rsync the static files to the host and reload nginx (no Docker)
#   docker  — build, push to a registry, and restart the container over SSH
#
# Usage:
#   ZERO_DEPLOY_TARGET=ssh ZERO_DEPLOY_HOST=user@34.66.84.21 bash landing/deploy.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
TARGET="${ZERO_DEPLOY_TARGET:-}"
HOST="${ZERO_DEPLOY_HOST:-}"
SITE="${ZERO_SITE_URL:-https://zero.headless.com}"
REMOTE_ROOT="${ZERO_REMOTE_ROOT:-/usr/share/nginx/html}"
IMAGE="${ZERO_IMAGE:-zero-landing}"

step() { printf '\n==> %s\n' "$*"; }
die()  { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

[ -n "$TARGET" ] || die "set ZERO_DEPLOY_TARGET to 'ssh' or 'docker'.
       ssh:    ZERO_DEPLOY_TARGET=ssh ZERO_DEPLOY_HOST=user@34.66.84.21 bash landing/deploy.sh
       docker: ZERO_DEPLOY_TARGET=docker ZERO_DEPLOY_HOST=user@34.66.84.21 bash landing/deploy.sh"
[ -n "$HOST" ] || die "set ZERO_DEPLOY_HOST (e.g. user@34.66.84.21)."

# Never deploy a site whose install command is broken.
step "Verifying the image before deploying"
bash "$HERE/build.sh" "$IMAGE" >/dev/null || die "build/smoke test failed — not deploying."
echo "    ok  image builds and /install serves a valid script"

case "$TARGET" in
  ssh)
    # Static files + the nginx server block that adds /install.
    step "Copying site files to $HOST:$REMOTE_ROOT"
    rsync -avz --delete \
      --exclude 'Dockerfile' --exclude 'build.sh' --exclude 'deploy.sh' --exclude 'nginx.conf' \
      "$HERE/" "$HOST:$REMOTE_ROOT/"

    step "Installing the nginx config (adds /install)"
    scp "$HERE/nginx.conf" "$HOST:/tmp/zero-nginx.conf"
    # shellcheck disable=SC2029
    ssh "$HOST" 'sudo mv /tmp/zero-nginx.conf /etc/nginx/conf.d/default.conf \
                 && sudo nginx -t \
                 && sudo systemctl reload nginx'
    ;;
  docker)
    [ -n "${ZERO_REGISTRY:-}" ] || die "set ZERO_REGISTRY (e.g. docker.io/yourname) for the docker target."
    TAG="$ZERO_REGISTRY/$IMAGE:$(git -C "$REPO" rev-parse --short HEAD)"
    step "Pushing $TAG"
    docker tag "$IMAGE" "$TAG"
    docker push "$TAG"
    step "Restarting the container on $HOST"
    # shellcheck disable=SC2029
    ssh "$HOST" "docker pull '$TAG' \
              && docker rm -f zero-landing 2>/dev/null || true; \
                 docker run -d --restart unless-stopped --name zero-landing -p 80:80 '$TAG'"
    ;;
  *)
    die "unknown ZERO_DEPLOY_TARGET '$TARGET' (expected 'ssh' or 'docker')."
    ;;
esac

# ---------------------------------------------------------------------------
# Verify the LIVE site, not the local one. This is the whole point.
# ---------------------------------------------------------------------------
step "Checking the live site"
sleep 3
fail=0
code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE/")"
[ "$code" = "200" ] && echo "    ok   homepage 200" || { echo "    FAIL homepage $code"; fail=1; }

body="$(curl -fsSL "$SITE/install" 2>/dev/null || true)"
if printf '%s' "$body" | head -1 | grep -q '^#!/usr/bin/env bash'; then
  echo "    ok   $SITE/install returns a shell script"
  printf '%s' "$body" | bash -n && echo "    ok   and it parses"
else
  echo "    FAIL $SITE/install did not return a script — the homepage CTA is broken"
  fail=1
fi

[ "$fail" -eq 0 ] || { echo; echo "DEPLOY VERIFICATION FAILED."; exit 1; }
printf '\nLive. %s/install works.\n' "$SITE"
