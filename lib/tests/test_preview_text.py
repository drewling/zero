#!/usr/bin/env python3
"""Runnable checks for keeper_server's preview-text cleanup pipeline:
_strip_html, _extract_body, and _tidy_preview. Covers the reported "ugly email
preview" bug and adjacent edge cases found while fixing it.
Run: python3 lib/tests/test_preview_text.py"""
import base64
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from keeper_server import _extract_body, _strip_html, _tidy_preview  # noqa: E402


def b64(s):
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("ascii")


# --- The exact reported regression -----------------------------------------
# "Anchor text <https://very-long-url>" is how a plaintext email renders an HTML
# link. Before the fix this produced a dangling "<", a truncated host, and no
# closing ">": "Demo buchen <mkto.nosto.com".
REGRESSION = ("Demo buchen <https://mkto.nosto.com/NzU5LU1BUi03NzctTVNZAAABbG9uZ3VybA"
              "/abcdefghijklmnop?x=1>")
out = _tidy_preview(REGRESSION)
assert out == "Demo buchen", out
assert "<" not in out and ">" not in out, out
assert "mkto.nosto.com" not in out, "raw/truncated URL must not leak into the anchor text"

# A second, more realistic anchored-link marketing paragraph: multiple anchors,
# a rule line, and an unsubscribe tracking parenthetical.
MARKETING = (
    "Hi Alex,\n\n"
    "Demo buchen <https://mkto.nosto.com/NzU5LU1BUi03NzctTVNZAAABbG9uZ3VybA/"
    "abcdefghijklmnop?x=1> und entdecken, wie Nosto Ihnen hilft.\n\n"
    "Unser Team freut sich <https://mkto.nosto.com/NzU5LU1BUi03NzctTVNZAAABbG9uZ3VybA/"
    "short> auf das Gesprach.\n\n"
    "Mit freundlichen Gruessen,\nDas Nosto Team\n\n"
    "********************************\n"
    "Sie erhalten diese E-Mail, weil Sie sich angemeldet haben. "
    "( https://mkto.nosto.com/unsubscribe/" + "a" * 100 + " )\n"
)
out = _tidy_preview(MARKETING)
assert "<" not in out and ">" not in out, out
assert "Demo buchen und entdecken" in out, out
assert "Unser Team freut sich auf das Gesprach." in out, out
assert "****" not in out, "ASCII rule line must be dropped"
assert "mkto.nosto.com/unsubscribe" not in out, "unsubscribe tracking URL must be dropped"
# Every real word from the sender survives somewhere in the output.
for word in ("Hi", "Alex", "Nosto", "Team", "angemeldet"):
    assert word in out, f"real word {word!r} was dropped: {out!r}"

# --- Balanced-bracket / no-truncation cases for the general URL shortener --
CASES = [
    ("(see https://example.com/very/long/path/that/is/quite/long/indeed)",
     "(see example.com)"),
    ('Check "https://example.com/very/long/path/that/is/quite/long" now',
     'Check "example.com" now'),
    ("Visit [https://example.com/very/long/path/that/is/quite/long/x] today",
     "Visit [example.com] today"),
    ("End of sentence https://example.com/very/long/path/that/is/quite/long.",
     "End of sentence example.com."),
    ("Comma, https://example.com/very/long/path/that/is/quite/long, then more",
     "Comma, example.com, then more"),
    ("Bare https://example.com/very/long/path/that/is/quite/long here",
     "Bare example.com here"),
]
for src, expected in CASES:
    got = _tidy_preview(src)
    assert got == expected, f"{src!r} -> {got!r}, expected {expected!r}"
    # No unbalanced bracket/quote anywhere in the output.
    for opener, closer in [("(", ")"), ("[", "]"), ("{", "}")]:
        assert got.count(opener) == got.count(closer), got
    assert got.count('"') % 2 == 0, got

# A bracketed URL with no adjacent label (starts a line / inside other brackets)
# must not leave a stray "<" or ">" either, and must not be truncated mid-token.
out = _tidy_preview("See (details <https://example.com/x>) for more")
assert out == "See (details) for more", out
out = _tidy_preview(
    "<https://example.com/onlylink/that/is/pretty/long/for/sure/yes> is worth checking")
assert "<" not in out and ">" not in out, out
assert out == "example.com is worth checking", out

# --- HTML entity leftovers / invisible characters ---------------------------
html = (
    "<p>Hi&nbsp;Alex,&nbsp;save&nbsp;20%!</p>"
    "<p>Check it out &amp; save.</p>"
    "<p>\u200b\u200c&nbsp;</p>"          # zero-width chars + nbsp, no real content
)
stripped = _strip_html(html)
assert "\xa0" not in stripped, "nbsp must be normalized to a plain space"
assert "&nbsp;" not in stripped and "&amp;" not in stripped, "entities must be unescaped"
assert "\u200b" not in stripped and "\u200c" not in stripped, "zero-width chars must be stripped"
assert "Hi Alex, save 20%!" in stripped, stripped
assert "Check it out & save." in stripped, stripped

# --- Hidden preheader padding never shown -----------------------------------
html = ('<div style="display:none;max-height:0;overflow:hidden;">'
        'Hidden preheader padding text should not appear in the preview.</div>'
        '<p>Real visible content starts here.</p>')
stripped = _strip_html(html)
assert "Hidden preheader padding" not in stripped, stripped
assert "Real visible content starts here." in stripped, stripped

# --- List bullets survive tag stripping (not fused into one run-on line) ---
html = "<p>Intro text.</p><ul><li>Free shipping</li><li>20% off everything</li></ul><p>Check it out.</p>"
tidy = _tidy_preview(_strip_html(html))
assert "\u2022 Free shipping" in tidy, tidy
assert "\u2022 20% off everything" in tidy, tidy
assert "Free shipping 20%" not in tidy, "bullets must not fuse into one line: " + tidy

# Plaintext "* item" bullets must also survive the paragraph-unwrap step.
plain_list = "Intro line.\n\n* Free shipping\n* 20% off everything\n\nCheck it out."
tidy = _tidy_preview(plain_list)
assert "* Free shipping" in tidy, tidy
assert "* 20% off everything" in tidy, tidy
assert "Free shipping * 20%" not in tidy, "plaintext bullets must not fuse: " + tidy

# --- Heading doesn't collide with the next paragraph ------------------------
html = "<h1>Big Sale This Week</h1><p>Hi Alex, check out our sale.</p>"
tidy = _tidy_preview(_strip_html(html))
assert "Big Sale This Week\n\nHi Alex" in tidy, tidy

# --- Inline-tag stripping doesn't leave a space before trailing punctuation -
html = 'Read more <a href="https://example.com/very/long/tracking/path/here">here</a>.'
tidy = _tidy_preview(_strip_html(html))
assert tidy == "Read more here.", tidy

# --- No real words dropped across a realistic full paragraph ---------------
PARAGRAPH = (
    "Hi Alex,\n\nThanks for reaching out about the proposal. I reviewed it "
    "carefully and have a few questions before we move forward. Could we "
    "schedule a call <https://calendly.com/somebody/very-long-scheduling-link-"
    "that-goes-on-and-on-and-on> sometime this week?\n\nBest,\nJordan"
)
out = _tidy_preview(PARAGRAPH)
for word in ("Hi", "Alex", "Thanks", "reaching", "proposal", "reviewed",
             "carefully", "questions", "forward", "Could", "schedule", "call",
             "sometime", "this", "week", "Best", "Jordan"):
    assert word in out, f"real word {word!r} dropped from: {out!r}"
assert "<" not in out and ">" not in out, out
assert "calendly.com" not in out, "the anchor's own URL should be dropped, not shortened: " + out

# --- _extract_body: text/plain preferred for real, non-stub mail -----------
personal_plain = "Hey,\n\nCan we move our call to 3pm?\n\nThanks,\nSam"
payload = {"mimeType": "text/plain", "body": {"data": b64(personal_plain)}}
assert _extract_body(payload) == personal_plain

# A real short reply must never be treated as a stub, even though it's brief.
for short in ("Thanks!", "OK", "Sounds good, thanks!"):
    payload = {"mimeType": "text/plain", "body": {"data": b64(short)}}
    assert _extract_body(payload) == short, short

# --- _extract_body: marketing "view in browser" stub falls back to HTML ----
stub = ("View this email in your browser: https://mkto.nosto.com/view/" + "a" * 100)
rich_html = "<h1>Big Sale</h1><p>Lots of real content lives only here, not in the stub.</p>"
payload = {"parts": [
    {"mimeType": "text/plain", "body": {"data": b64(stub)}},
    {"mimeType": "text/html", "body": {"data": b64(rich_html)}},
]}
out = _extract_body(payload)
assert "Lots of real content" in out, out
assert "view this email" not in out.lower(), out

print("preview_text OK")
