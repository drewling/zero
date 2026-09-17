#!/usr/bin/env bash
# install-zero.sh — one-command install for zero on a fresh Mac.
#
# Does everything a new user would otherwise do by hand:
#   1. Installs the prerequisites (Homebrew → Python 3 / Node → gws / an agent CLI)
#   2. Installs zero.app to /Applications (or ~/Applications if that isn't writable)
#   3. Launches it
#
# ON GATEKEEPER: zero is signed ad-hoc, not notarized (no paid Apple Developer
# account). macOS blocks ad-hoc-signed apps carrying the `com.apple.quarantine`
# flag. That flag is applied by the *downloading application*: browsers set it,
# command-line tools do not. Verified 2026-09-17 on macOS 27.0 (26A5388g) — a
# release fetched with curl carries only `com.apple.provenance`, with no
# quarantine attribute anywhere in the bundle, and launches normally.
#
# So a curl install does not need to strip anything. We still CHECK (a DMG the
# user downloaded in a browser and passed as an argument will be quarantined)
# and only strip when the flag is actually present.
#
# Run it directly:
#     curl -fsSL https://raw.githubusercontent.com/drewling/zero/master/macapp/install-zero.sh | bash
#
# Or, if you already downloaded zero.dmg / zero.app, pass it:
#     bash install-zero.sh ~/Downloads/zero.dmg
#
# Re-running is safe: anything already installed is left alone.
#
# NB: deliberately not `set -e`. One failed prerequisite should not abort the
# whole install. Instead every failure is recorded in PREREQ_FAILED and reported
# at the end: the one thing this script must never do is print "Done" over an
# install that cannot work.
set -uo pipefail

DMG_URL="https://github.com/drewling/zero/releases/latest/download/zero.dmg"
APP_NAME="zero.app"
SRC="${1:-}"        # optional local .dmg or .app path
# DEST is resolved after the permission check below (/Applications may not be
# writable for a standard user; we fall back to ~/Applications rather than die).
DEST=""

bold=$(tput bold 2>/dev/null || true); dim=$(tput dim 2>/dev/null || true); rst=$(tput sgr0 2>/dev/null || true)
step() { printf '\n%s==>%s %s%s\n' "$bold" "$rst" "$bold" "$* $rst"; }
ok()   { printf '    %sok%s  %s\n' "$dim" "$rst" "$*"; }
warn() { printf '    !!  %s\n' "$*" >&2; }
die()  { printf '\nERROR: %s\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

# Prerequisites that failed. Reported at the end; a non-empty list downgrades
# "Done" to "Installed, but not ready yet" so a broken install never looks fine.
PREREQ_FAILED=""
note_failed() { PREREQ_FAILED="${PREREQ_FAILED}  - $1"$'\n'; warn "$2"; }

[ "$(uname)" = "Darwin" ] || die "zero is a macOS app."

# --- hard requirements: fatal, not warnings --------------------------------
# macapp/build.sh compiles one arm64-apple-macosx26.0 binary. On Intel, or on
# macOS < 26, the app genuinely cannot launch. Installing it anyway leaves a
# menu-bar app that silently does nothing — the worst failure mode for a tool
# with no window, because it looks identical to "nothing happened".
osver="$(sw_vers -productVersion 2>/dev/null || echo 0)"
if ! [ "${osver%%.*}" -ge 26 ] 2>/dev/null; then
  die "zero needs macOS 26 (Tahoe) or later; this Mac is on $osver.
       The app is built for macOS 26 and will not launch here. Stopping now
       rather than installing something that cannot work."
fi
if [ "$(uname -m)" != "arm64" ]; then
  die "zero is built for Apple Silicon only; this Mac is $(uname -m).
       There is no Intel build yet. Stopping now rather than installing
       something that cannot work."
fi
ok "macOS $osver, Apple Silicon"

# Make a Homebrew install visible to this shell immediately after installing it.
load_brew() {
  for p in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    [ -x "$p" ] && eval "$("$p" shellenv)" && return 0
  done
  return 1
}

# ---------------------------------------------------------------------------
# 1. Prerequisites
# ---------------------------------------------------------------------------
step "Checking prerequisites"

have brew || load_brew || true
if ! have brew; then
  step "Installing Homebrew (the macOS package manager)"
  # NONINTERACTIVE so it runs unattended; it still needs a TTY for the one-time
  # Xcode command-line-tools sudo prompt. Under `curl ... | bash` stdin is the
  # script itself, so we redirect from /dev/tty — but that only exists when a
  # terminal is attached. Check first, otherwise the redirect fails with a
  # confusing error instead of a useful instruction.
  if [ -r /dev/tty ]; then
    NONINTERACTIVE=1 /bin/bash -c \
      "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
      </dev/tty 2>/dev/tty \
      || note_failed "Homebrew" "Homebrew install failed — install it from https://brew.sh, then re-run."
  else
    note_failed "Homebrew" "No terminal available for Homebrew's sudo prompt.
        Install Homebrew first (https://brew.sh), then re-run this installer."
  fi
  load_brew || true
fi

ensure_brew_pkg() {        # ensure_brew_pkg <command> <formula> <label>
  local cmd="$1" formula="$2" label="$3"
  if have "$cmd"; then ok "$label already installed"; return; fi
  if have brew; then
    step "Installing $label"
    if brew install "$formula"; then ok "$label installed"
    else note_failed "$label" "couldn't install $label (brew install $formula)"; fi
  else
    note_failed "$label" "$label missing and Homebrew unavailable — install $label manually."
  fi
}

ensure_npm_pkg() {         # ensure_npm_pkg <command> <package> <label>
  local cmd="$1" pkg="$2" label="$3"
  if have "$cmd"; then ok "$label already installed"; return; fi
  if ! have npm; then
    note_failed "$label" "$label missing and npm unavailable — install Node, then: npm install -g $pkg"
    return
  fi
  step "Installing $label"
  if npm install -g "$pkg" 2>/dev/null; then ok "$label installed"; return; fi
  # Stock Node installs make npm's global prefix (e.g. /usr/local) root-owned, so
  # -g fails with EACCES. Retry into ~/.local, which is already on the app's PATH
  # (augmentedPath in main.swift), so no sudo and the app still finds the binary.
  if npm install -g --prefix "$HOME/.local" "$pkg"; then
    ok "$label installed (to ~/.local/bin)"
  else
    note_failed "$label" "couldn't install $label (npm install -g $pkg)"
  fi
}

ensure_brew_pkg python3 python3 "Python 3"
ensure_brew_pkg node    node    "Node.js (for the CLIs below)"
ensure_npm_pkg  gws     @googleworkspace/cli      "Google Workspace CLI (gws)"

# An AI engine is required, but Claude specifically is not: zero can use a Jev
# API key, or any already-installed agent CLI. Only install Claude if the user
# has none of them, so we never push a second CLI onto someone already set up.
if have claude || have codex || have opencode; then
  for c in claude codex opencode; do have "$c" && ok "AI engine found: $c"; done
else
  ok "no AI engine found yet — installing Claude Code as the default"
  ensure_npm_pkg claude @anthropic-ai/claude-code "Claude Code CLI (claude)"
fi

# ---------------------------------------------------------------------------
# 2. Locate the app (download the DMG unless a local source was given)
# ---------------------------------------------------------------------------
TMP=""; MNT=""
cleanup() {
  [ -n "$MNT" ] && hdiutil detach "$MNT" -quiet 2>/dev/null || true
  [ -n "$TMP" ] && rm -rf "$TMP" 2>/dev/null || true
}
trap cleanup EXIT

APP_SRC=""
if [ -n "$SRC" ] && [ -d "$SRC" ] && [[ "$SRC" == *.app ]]; then
  APP_SRC="$SRC"
else
  DMG="$SRC"
  if [ -z "$DMG" ]; then
    TMP="$(mktemp -d)"; DMG="$TMP/zero.dmg"
    step "Downloading the latest zero"
    curl -fL --progress-bar "$DMG_URL" -o "$DMG" || die "download failed ($DMG_URL)"
  fi
  [ -f "$DMG" ] || die "no such file: $DMG"
  step "Mounting $DMG"
  MNT="$(hdiutil attach "$DMG" -nobrowse -readonly -mountrandom /tmp | grep -Eo '/tmp/[^[:space:]]+' | tail -1)"
  { [ -n "$MNT" ] && [ -d "$MNT/$APP_NAME" ]; } || die "couldn't find $APP_NAME inside the DMG"
  APP_SRC="$MNT/$APP_NAME"
fi

# ---------------------------------------------------------------------------
# 3. Install + de-quarantine + launch
# ---------------------------------------------------------------------------
# Pick a destination we can actually write to. A standard (non-admin) macOS
# account cannot write to /Applications; ~/Applications works without sudo and
# Spotlight/Launchpad index it the same way.
if [ -w /Applications ]; then
  DEST="/Applications/$APP_NAME"
else
  mkdir -p "$HOME/Applications" 2>/dev/null || true
  if [ -w "$HOME/Applications" ]; then
    DEST="$HOME/Applications/$APP_NAME"
    ok "/Applications isn't writable — installing to ~/Applications instead"
  else
    die "can't write to /Applications or ~/Applications. Check permissions and re-run."
  fi
fi

step "Installing to $DEST"
# Stage beside the destination, then swap. The old install is only removed once
# the new one is fully copied, so an interrupted or failed copy can never leave
# the user with no app at all.
STAGE="$DEST.new-$$"
rm -rf "$STAGE" 2>/dev/null || true
if ! cp -R "$APP_SRC" "$STAGE"; then
  rm -rf "$STAGE" 2>/dev/null || true
  die "couldn't copy zero to $(dirname "$DEST") (permissions?)"
fi
# The app must be intact before we replace a working install with it.
[ -x "$STAGE/Contents/MacOS/zero" ] || { rm -rf "$STAGE"; die "the downloaded app looks incomplete — not installing it."; }

# Quarantine: a curl download never sets it, a browser download does. Only touch
# extended attributes when the flag is genuinely present, and never blanket-clear
# every attribute. Absolute /usr/bin/xattr because a Python/conda `xattr` earlier
# in PATH may not support -r and would fail silently.
if /usr/bin/xattr -lr "$STAGE" 2>/dev/null | grep -q com.apple.quarantine; then
  ok "this copy was quarantined (browser download) — clearing that one flag"
  /usr/bin/xattr -dr com.apple.quarantine "$STAGE" 2>/dev/null || true
  if /usr/bin/xattr -lr "$STAGE" 2>/dev/null | grep -q com.apple.quarantine; then
    warn "couldn't clear the quarantine flag. If zero won't open, use
        System Settings > Privacy & Security > Open Anyway."
  fi
else
  ok "no quarantine flag (command-line download)"
fi

# Ad-hoc signatures must still VERIFY. Reporting a genuinely broken signature as
# "expected" would hide a corrupted download, so say which one it is.
if codesign --verify --deep "$STAGE" 2>/dev/null; then
  ok "signature verified (ad-hoc, as expected for an un-notarized build)"
else
  rm -rf "$STAGE" 2>/dev/null || true
  die "the downloaded app failed signature verification — it may be corrupted.
       Not installing it. Re-run to download a fresh copy."
fi

[ -e "$DEST" ] && { ok "replacing existing install"; rm -rf "$DEST"; }
mv "$STAGE" "$DEST" || { rm -rf "$STAGE" 2>/dev/null || true; die "couldn't move zero into place at $DEST"; }

step "Launching zero"
open "$DEST" || warn "couldn't launch automatically — open $DEST from Finder."

# Final summary. If any prerequisite failed, say so plainly: an install that
# cannot run must never be reported as "Done".
if [ -n "$PREREQ_FAILED" ]; then
  printf '\n%sInstalled, but not ready yet.%s zero is at %s, but these are missing:\n\n' "$bold" "$rst" "$DEST"
  printf '%b' "$PREREQ_FAILED"
  printf '\nzero needs them to read your mail. Fix the above, then re-run this installer.\n'
  exit 1
fi

printf '\n%sDone.%s zero is in your menu bar — the icon at the top-right. Click it to set up.\n' "$bold" "$rst"
