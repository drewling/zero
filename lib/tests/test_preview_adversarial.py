#!/usr/bin/env python3
"""Adversarial checks on the preview-text pipeline: cases where the cleanup can
DROP real words from a legitimate personal email, or render text that misleads
the reader about where a link points. No network.

The preview is what the user reads before deciding to reply, so silently eating
a sentence is a correctness bug even though no mail moves.

Run: python3 lib/tests/test_preview_adversarial.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from keeper_server import _strip_html, _tidy_preview  # noqa: E402

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        FAILS.append(f"{label}: {detail}")
        print(f"  FAIL {label}: {detail}")


# --- 1. The link-reference stripper must not eat a real parenthetical --------
# "(\s*https?://[^)]+)" matches from the "(" to the FIRST ")" anywhere after it,
# so any prose that follows a URL inside parentheses is deleted along with it.
print("parentheticals keep their words:")

A = "Please confirm (https://acme.com and let me know by Friday) before we ship."
out_a = _tidy_preview(A)
check("words after a URL inside parens survive", "Friday" in out_a, repr(out_a))

B = "Sign here (https://acme.com/sign, it expires tonight) or call me."
out_b = _tidy_preview(B)
check("second clause inside parens survives", "expires tonight" in out_b, repr(out_b))

C = "The deck (https://acme.com/deck) is attached."
out_c = _tidy_preview(C)
check("a pure link parenthetical is still removed",
      "acme.com/deck" not in out_c and "attached" in out_c, repr(out_c))


# --- 2. A bare URL must not be collapsed into a misleading different target --
# Shortening "https://evil.com/login?bank=chase" to its host is fine; shortening
# so aggressively that the remaining text names a DIFFERENT site than the link
# actually goes to is not. The concrete risk is a path-carrying URL on a
# user-content host.
print("\nshortened URLs stay truthful:")

D = "Docs: https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing"
out_d = _tidy_preview(D)
check("shortened URL keeps its real host", "drive.google.com" in out_d, repr(out_d))
check("shortened URL does not invent a different host",
      "evil" not in out_d and out_d.count("://") == 0, repr(out_d))


# --- 3. Angle-bracket collapse must not misattribute a link ----------------
# "Anchor <https://real-target>" is how plaintext mail renders an HTML link. When
# the ANCHOR TEXT is itself a URL, dropping the bracketed real target leaves text
# that asserts one destination while the actual link went somewhere else. The
# preview must not claim the reader is looking at accounts.google.com when the
# underlying link is a phishing host.
print("\nlink text that disagrees with its target is not asserted:")

E = "Log in here: https://accounts.google.com <https://evil-phish.ru/steal>"
out_e = _tidy_preview(E)
check("a URL-shaped anchor over a different target is not left standing alone",
      not (out_e.rstrip().endswith("accounts.google.com")
           and "evil-phish.ru" not in out_e),
      repr(out_e))


# --- 4. Plain prose containing "<" or ">" must not lose words ---------------
# _strip_html's generic "<[^>]+>" tag eater runs on text that reached it as HTML,
# but a sender writing "5 < 10 and 10 > 5" has written real words between what
# look like a tag's delimiters.
print("\nmath and comparisons in HTML mail keep their words:")

F = "<p>Budget is 5 &lt; 10 and 10 &gt; 5 so we are fine.</p>"
out_f = _strip_html(F)
check("escaped comparisons survive",
      "5 < 10" in out_f and "we are fine" in out_f, repr(out_f))


# --- 5. Hidden-content stripping must not swallow visible copy -------------
# The display:none rule is a non-greedy match to the FIRST matching close tag, so
# a hidden wrapper containing nested same-name tags ends early and the visible
# remainder of the wrapper is emitted, while genuinely visible text placed before
# the true close tag is lost. Whatever the nesting, real visible words must
# survive.
print("\nhidden-preheader stripping keeps visible copy:")

G = ('<div style="display:none">hidden preheader</div>'
     '<p>Hi Sam, are we still on for Thursday?</p>')
out_g = _strip_html(G)
check("visible sentence survives a hidden preheader",
      "still on for Thursday" in out_g, repr(out_g))
check("hidden preheader is removed", "hidden preheader" not in out_g, repr(out_g))

H = '<div style="display:none">hidden<div>inner</div>tail</div><p>Real body.</p>'
out_h = _strip_html(H)
check("visible body survives a nested hidden block", "Real body." in out_h, repr(out_h))


if FAILS:
    print(f"\n{len(FAILS)} FAILURE(S)")
    for f in FAILS:
        print("  - " + f)
    sys.exit(1)
print("\npreview_adversarial OK")
