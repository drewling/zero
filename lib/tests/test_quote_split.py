#!/usr/bin/env python3
"""Runnable check for keeper_server._split_quote — quoted-reply trimming for previews.
Run: python3 lib/tests/test_quote_split.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from keeper_server import _split_quote   # noqa: E402

# A real inbound reply (latest text on top, prior mail inlined as a quoted block).
SAMPLE = """Hi Tayo,

I just reviewed Drewl quickly. A few legal items came up.

Would you be open to seeing how our model works?

Lauren Wray
Head of Growth | LegalVision UK

P.S. Not the right moment? Reply "no thanks".

On Wed, Jun 24, 2026 at 11:05 AM UTC Lauren Wray <lauren.wray@legalvisionboost.com> wrote:

> Hey Tayo,
>
> It seems like scoping and change order disputes would be key for Drewl.
>
> Lauren Wray
"""

new, quoted = _split_quote(SAMPLE)
assert "Hi Tayo," in new, "new text kept"
assert "Would you be open" in new, "new body kept"
assert "On Wed, Jun 24" not in new, "attribution must be trimmed from new text"
assert "Hey Tayo" not in new, "quoted history must not leak into new text"
assert "Hey Tayo" in quoted, "quoted history captured"
assert quoted.startswith("On Wed, Jun 24"), "quoted starts at the attribution line"

# A plain message with no quote → all body, no quoted part.
n2, q2 = _split_quote("Just a quick note, no history here.\n\nThanks!")
assert q2 == "", "no false quote boundary"
assert "quick note" in n2

# A bare ">" quoted block with no attribution still cuts.
n3, q3 = _split_quote("My reply.\n\n> your earlier line\n> more")
assert n3 == "My reply.", n3
assert "your earlier line" in q3

# Whole body quoted → keep it all (never hide everything).
n4, q4 = _split_quote("> only quoted\n> nothing new")
assert q4 == "" and "only quoted" in n4, "all-quoted stays visible"

print("quote_split OK")
