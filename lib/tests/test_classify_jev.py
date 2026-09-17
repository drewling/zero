#!/usr/bin/env python3
"""Runnable checks for review_open_loops._classify_jev — the Jev keep/archive path.

Covers the threshold boundaries, uncertain->keep, failure(None)->keep, the
category coming from categories.json (not hardcoded), the deterministic
owner-last rule, and the return shape matching _classify.
No network: jev.ask_many is stubbed.
Run: python3 lib/tests/test_classify_jev.py"""
import json, os, sys

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROOT = os.path.dirname(os.path.abspath(LIB))
sys.path.insert(0, LIB)
import jev  # noqa: E402
import review_open_loops as rol  # noqa: E402

R = rol  # shorthand


def _row(name="t", last_from="Someone <a@b.com>", subject="s", snippet="x",
         last_from_owner=False, replied_before=False):
    return {"id": name, "last_from": last_from, "subject": subject,
            "snippet": snippet, "last_from_owner": last_from_owner,
            "replied_before": replied_before}


def _ans(awaiting=0.5, cold=0.0, automated=0.0, protected=0.0, urgency=0.0,
         category=None, confidence=0.9):
    a = {
        "awaiting_user": {"type": "noul", "noul": awaiting},
        "is_cold_outreach": {"type": "noul", "noul": cold},
        "is_automated": {"type": "noul", "noul": automated},
        "is_protected": {"type": "noul", "noul": protected},
        "urgency": {"type": "score", "score": urgency,
                    "legend": {"0": "a", "1": "b", "2": "c"}, "confidence": 0.9},
    }
    if category is not None:
        a["category"] = {"type": "choice", "choice": category,
                         "probabilities": {}, "confidence": confidence}
    return a


def _stub(answers_list):
    """Stub jev.ask_many to return a fixed list, asserting item count matches."""
    def _fn(items, max_workers=12, timeout=30.0):
        assert len(items) == len(answers_list), \
            f"stub expected {len(answers_list)} items, got {len(items)}"
        return list(answers_list)
    return _fn


_orig_ask_many = jev.ask_many

# ---------------------------------------------------------------------------
# 1. Return shape matches _classify: {str(i): {"decision":..., "category":...}}
# ---------------------------------------------------------------------------
jev.ask_many = _stub([_ans(awaiting=0.9, category="Needs reply")])
out = R._classify_jev([_row()])
assert set(out.keys()) == {"0"}, out
assert isinstance(out["0"], dict)
assert set(out["0"].keys()) == {"decision", "category"}, out["0"]
assert out["0"]["decision"] in ("keep", "archive")
assert out["0"]["decision"] == "keep"
assert out["0"]["category"] == "Needs reply"

# Empty input mirrors _classify's empty-dict shape.
assert R._classify_jev([]) == {}

# ---------------------------------------------------------------------------
# 2. Threshold boundaries (exact constants, so tuning them is a visible change)
# ---------------------------------------------------------------------------
eps = 1e-6

# awaiting_user strictly ABOVE JEV_KEEP_AWAITING -> keep.
assert R._jev_decide(_ans(awaiting=R.JEV_KEEP_AWAITING + eps,
                          cold=1.0, automated=1.0)) == "keep"
# Exactly AT the keep threshold is not "above", but it is also not below the
# archive threshold, so it lands in the uncertain band -> keep.
assert R._jev_decide(_ans(awaiting=R.JEV_KEEP_AWAITING,
                          cold=1.0, automated=1.0)) == "keep"

# Strictly BELOW JEV_ARCHIVE_AWAITING + noise + low urgency -> archive.
assert R._jev_decide(_ans(awaiting=R.JEV_ARCHIVE_AWAITING - eps,
                          cold=1.0, urgency=0.0)) == "archive"
assert R._jev_decide(_ans(awaiting=R.JEV_ARCHIVE_AWAITING - eps,
                          automated=1.0, urgency=0.0)) == "archive"
# Exactly AT the archive threshold is NOT below it -> uncertain -> keep.
assert R._jev_decide(_ans(awaiting=R.JEV_ARCHIVE_AWAITING,
                          cold=1.0, urgency=0.0)) == "keep"

# Noise threshold: cold/automated below JEV_NOISE_MIN is not enough to archive.
assert R._jev_decide(_ans(awaiting=0.0, cold=R.JEV_NOISE_MIN - eps,
                          automated=R.JEV_NOISE_MIN - eps)) == "keep"
assert R._jev_decide(_ans(awaiting=0.0, cold=R.JEV_NOISE_MIN)) == "archive"

# Urgency at/above JEV_KEEP_URGENCY keeps even when everything else says noise.
assert R._jev_decide(_ans(awaiting=0.0, cold=1.0, automated=1.0,
                          urgency=R.JEV_KEEP_URGENCY)) == "keep"
assert R._jev_decide(_ans(awaiting=0.0, cold=1.0, automated=1.0,
                          urgency=R.JEV_KEEP_URGENCY - eps)) == "archive"

# Protected (personal/family/legal/live payment problem) is a hard keep.
assert R._jev_decide(_ans(awaiting=0.0, cold=1.0, automated=1.0,
                          protected=R.JEV_KEEP_PROTECTED + eps)) == "keep"
assert R._jev_decide(_ans(awaiting=0.0, automated=1.0,
                          protected=R.JEV_KEEP_PROTECTED)) == "archive"

# ---------------------------------------------------------------------------
# 3. Uncertain -> keep (the band between the two awaiting thresholds)
# ---------------------------------------------------------------------------
mid = (R.JEV_KEEP_AWAITING + R.JEV_ARCHIVE_AWAITING) / 2.0
assert R._jev_decide(_ans(awaiting=mid, cold=1.0, automated=1.0)) == "keep"
# Confidently "nobody waiting" but NOT noise (a human FYI) -> keep.
assert R._jev_decide(_ans(awaiting=0.01, cold=0.0, automated=0.0)) == "keep"

# ---------------------------------------------------------------------------
# 4. Failure paths ALWAYS keep. Never archive on an error.
# ---------------------------------------------------------------------------
jev.ask_many = _stub([None, None])
out = R._classify_jev([_row("a"), _row("b")])
assert out["0"] == {"decision": "keep", "category": None}, out
assert out["1"] == {"decision": "keep", "category": None}, out

# Empty / malformed answer payloads.
assert R._jev_decide(None) == "keep"
assert R._jev_decide({}) == "keep"
assert R._jev_decide("not a dict") == "keep"
# Partial answers: the archive-supporting judgments are missing -> keep.
assert R._jev_decide({"is_cold_outreach": {"type": "noul", "noul": 1.0}}) == "keep"
assert R._jev_decide({"awaiting_user": {"type": "noul", "noul": 0.0}}) == "keep"
# Malformed values inside otherwise-archivable answers -> keep.
bad = _ans(awaiting=0.0, cold=1.0)
bad["awaiting_user"] = {"type": "noul", "noul": "oops"}
assert R._jev_decide(bad) == "keep"

# ask_many raising (contract says it shouldn't, but if it does) -> all keep.
def _boom(items, max_workers=12, timeout=30.0):
    raise RuntimeError("simulated total failure")
jev.ask_many = _boom
out = R._classify_jev([_row("a"), _row("b")])
assert [out[k]["decision"] for k in ("0", "1")] == ["keep", "keep"], out

# A short results list (fewer answers than items) must not IndexError or archive.
jev.ask_many = lambda items, max_workers=12, timeout=30.0: []
out = R._classify_jev([_row("a"), _row("b")])
assert [out[k]["decision"] for k in ("0", "1")] == ["keep", "keep"], out

# ---------------------------------------------------------------------------
# 5. Category comes from categories.json, not a hardcoded list
# ---------------------------------------------------------------------------
cats = R._categories()
cat_names = [c["name"] for c in cats]
qs = R._jev_questions(cats)
assert qs["category"]["type"] == "choice"
for name in cat_names:
    assert name in qs["category"]["criteria"], f"{name} missing from choice criteria"
assert R.JEV_NO_CATEGORY in qs["category"]["criteria"]

# Prove it tracks the file: swap in a bespoke category set and re-derive.
_orig_categories = R._categories
R._categories = lambda: [{"name": "Zebra", "description": "a test-only category"}]
qs2 = R._jev_questions(R._categories())
assert "Zebra" in qs2["category"]["criteria"]
assert "Needs reply" not in qs2["category"]["criteria"], \
    "category options must come from categories.json, not be hardcoded"
jev.ask_many = _stub([_ans(awaiting=0.99, category="Zebra")])
out = R._classify_jev([_row()])
assert out["0"] == {"decision": "keep", "category": "Zebra"}, out
R._categories = _orig_categories

# A category name Jev returns that is not in categories.json -> None, not a bad label.
assert R._jev_category(_ans(category="Not A Real Category"), set(cat_names)) is None
assert R._jev_category(_ans(category=R.JEV_NO_CATEGORY), set(cat_names)) is None
# Low confidence -> no label rather than a wrong one.
assert R._jev_category(_ans(category=cat_names[0],
                            confidence=R.JEV_MIN_CATEGORY_CONF - eps),
                       set(cat_names)) is None
assert R._jev_category(_ans(category=cat_names[0],
                            confidence=R.JEV_MIN_CATEGORY_CONF),
                       set(cat_names)) == cat_names[0]
# Archived threads never carry a category.
jev.ask_many = _stub([_ans(awaiting=0.0, automated=1.0, category=cat_names[0])])
out = R._classify_jev([_row()])
assert out["0"] == {"decision": "archive", "category": None}, out

# ---------------------------------------------------------------------------
# 6. Deterministic owner-last rule: archived without spending an API call
# ---------------------------------------------------------------------------
jev.ask_many = _stub([_ans(awaiting=0.99, category="Needs reply")])  # only 1 item
out = R._classify_jev([_row("owner", last_from_owner=True), _row("other")])
assert out["0"] == {"decision": "archive", "category": None}, out
assert out["1"]["decision"] == "keep", out
assert len(out) == 2

# ---------------------------------------------------------------------------
# 7. The user's policy and learned preferences reach the model
# ---------------------------------------------------------------------------
st = R._jev_state(_row(replied_before=True), "MY POLICY TEXT", "MY LEARNED RULES")
assert st["keep_policy"] == "MY POLICY TEXT"
assert st["learned_preferences"] == "MY LEARNED RULES"
assert st["thread"]["replied_before"] is True
assert st["thread"]["last_from_owner"] is False
# Structured object, JSON-serializable (Jev takes text-only state).
json.dumps(st)
# Absent learned text is simply omitted rather than sent as an empty field.
assert "learned_preferences" not in R._jev_state(_row(), "P", "")

captured = {}
def _capture(items, max_workers=12, timeout=30.0):
    captured["items"] = items
    return [_ans(awaiting=0.9, category="Needs reply") for _ in items]
jev.ask_many = _capture
R._classify_jev([_row()])
state, questions = captured["items"][0]
assert state["keep_policy"] == R._policy_text(), "keep-policy.md must reach the model"
assert set(questions) == {"awaiting_user", "is_cold_outreach", "is_automated",
                          "is_protected", "urgency", "category"}, questions
for qid, q in questions.items():
    assert q["instructions"].strip(), f"{qid} needs instructions"
assert questions["urgency"]["criteria"] == R.JEV_URGENCY_LEVELS
assert len(R.JEV_URGENCY_LEVELS) >= 3

# ---------------------------------------------------------------------------
# 8. Provider dispatch: default (claude) must NOT route to Jev
# ---------------------------------------------------------------------------
_orig_provider = R._llm._active_provider_name
_orig_classify = R._classify
called = {"classify": 0, "jev": 0}
R._classify = lambda chunk: (called.__setitem__("classify", called["classify"] + 1)
                             or {"0": {"decision": "keep", "category": None}})
jev.ask_many = lambda items, max_workers=12, timeout=30.0: (
    called.__setitem__("jev", called["jev"] + 1)
    or [_ans(awaiting=0.9) for _ in items])

R._llm._active_provider_name = lambda: "claude"
R._classify_active([_row()])
assert called == {"classify": 1, "jev": 0}, called

R._llm._active_provider_name = lambda: "jev"
R._classify_active([_row()])
assert called == {"classify": 1, "jev": 1}, called

# Unknown provider / unreadable settings both fall back to the existing path.
R._llm._active_provider_name = lambda: "codex"
R._classify_active([_row()])
assert called == {"classify": 2, "jev": 1}, called

def _raise():
    raise RuntimeError("settings unreadable")
R._llm._active_provider_name = _raise
R._classify_active([_row()])
assert called == {"classify": 3, "jev": 1}, called

R._llm._active_provider_name = _orig_provider
R._classify = _orig_classify
jev.ask_many = _orig_ask_many

# The shipped default must still be claude (settings absent == claude).
assert R._llm._active_provider_name() != "jev" or \
    os.environ.get("ZERO_ALLOW_JEV_DEFAULT"), \
    "default provider must remain claude until the agreement check passes"

print("classify_jev OK")
