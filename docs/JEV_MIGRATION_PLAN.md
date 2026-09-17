# Plan: move zero to Jev, and make it fast

## What I checked first

Before planning I verified the things that could invalidate the whole plan:

- **Your API key works.** `POST https://api.typesafe.ai/v1/systemone` with the `JEV` key
  from `.env` returned `HTTP 200` in **0.41s**, model `jev-1.13.0`. Real key, real service.
- **Jev is a genuine fit.** It's TypeSafe AI's "System One" model: you send state plus
  typed questions, it returns typed answers with calibrated probabilities. No text
  generation. That is exactly the shape of zero's core decision.
- **I measured where the lag actually comes from** (details below). It is *not* what
  you'd guess, and it changes the Rust recommendation.

## The one honest finding that reframes everything

You suggested Rust for performance. I measured before agreeing, and the numbers say
Rust would be mostly wasted effort:

| Measured | Result |
| --- | --- |
| `gws` process startup | ~50ms |
| One real Gmail call through `gws` | **440-800ms** |
| Gmail calls per thread in a run | 2-3, **strictly sequential** |
| Your inbox size | ~200 threads |

So a run spends roughly `200 threads x 2.5 calls x 0.55s` = **~4.5 minutes sitting idle,
waiting on the network, one call at a time.** Python's slowness contributes almost
nothing. Rewriting that loop in Rust would make a 50ms slice faster while the 550ms
network wait stays identical.

**The lag is sequential network I/O, not CPU or memory.** The fix is concurrency and
fewer round-trips. That's a change worth doing regardless of language, and it's a far
bigger win than a rewrite. I'd rather tell you this than hand you a Rust project that
doesn't fix your actual complaint.

Rust is still worth considering later, and I've kept a place for it at the end, but it
should not be step one.

## Part 1: Where Jev goes (and where it doesn't)

There are 5 places the code calls an AI today. They are not all the same job:

| Where | What it does | Verdict |
| --- | --- | --- |
| `review_open_loops.py:239` | Keep or archive each thread, pick a category | **Jev.** This is the core decision and the main win. |
| `catchup.py:107` | Pick out important threads | **Jev.** Same shape. |
| `learn.py:213` | Distill preferences from past actions | **Jev**, restructured as scored judgments. |
| `keeper_server.py:1118` | Generate reply text | **Stays an LLM.** Jev doesn't write prose. |
| `gen_drafts.py:153` | Generate draft replies | **Stays an LLM.** Same reason. |

This is the important nuance: **Jev replaces the judgment, not the writing.** zero keeps
a text LLM for drafting replies in your voice. Anyone promising a 100% Jev migration
would be breaking your drafting feature.

### Why this is a genuine upgrade, not just a swap

Today one call classifies a **batch of 100 threads** by asking a text model to return a
JSON blob, then the code hunts for `{`, parses it, and falls back to "keep" when parsing
fails. That design has three problems Jev removes outright:

1. **It can silently mis-parse.** `_classify` returns `{}` on any bad JSON, and every
   thread then defaults to "keep". A bad parse looks identical to "nothing to archive".
2. **One bad thread can skew its 99 neighbours.** They share one prompt and one response.
3. **No confidence.** A coin-flip decision and a certain one are indistinguishable.

With Jev, each thread becomes its own small set of typed questions:

```json
{
  "state": { "last_sender": "...", "subject": "...", "snippet": "...",
             "last_from_owner": false, "replied_before": true },
  "model": "jev-latest",
  "questions": {
    "awaiting_user": { "type": "noul",
      "instructions": "Is a real person awaiting a reply or decision from the account owner?" },
    "is_cold_outreach": { "type": "noul",
      "instructions": "Is this unsolicited sales, prospecting, or marketing?" },
    "urgency": { "type": "score",
      "instructions": "How consequential is it if this is set aside today?",
      "criteria": ["No consequence", "Minor", "Real deadline or money at stake"] },
    "category": { "type": "choice",
      "instructions": "Best-fit category for this thread",
      "criteria": { "Needs reply": "...", "Waiting on others": "...", "...": "..." } }
  }
}
```

All questions answer **in parallel in one call**. Type errors become impossible, so the
JSON-hunting and the silent keep-everything failure mode both disappear.

### The safety upgrade you get for free

Jev returns calibrated probabilities, so the keep/archive rule becomes **your policy in
plain code**, not something buried in a prompt:

```python
if awaiting_user > 0.75 or urgency >= 1.8:   keep
elif awaiting_user < 0.25 and is_cold:       archive
else:                                        keep   # uncertain -> keep, never lose mail
```

This directly serves PRODUCT.md's first principle. Uncertainty becomes visible and
tunable instead of hidden. You can also tighten or loosen aggressiveness by changing one
number, with no reclassification needed.

### Cost and speed

Jev is $0.042 per million input tokens with **free output**. At ~300 input tokens per
thread, classifying 200 threads costs about **$0.0025 a run**. Cheaper and faster than
the current per-batch Claude calls, and the calls can run concurrently.

## Part 2: Fixing the actual lag

This is the part that addresses "laggy, especially when performing operations."

### 2a. Parallelize the read phase (the single biggest win)

`review_open_loops.py` lines 471-481 loop through threads one at a time, each one
blocking on a ~0.55s network call. Running 16 at once against the Gmail API turns
**~4.5 minutes into roughly 20 seconds**. This is a contained change to one loop and it
alone likely fixes most of what you feel.

### 2b. Stop paying subprocess and auth costs per call

Every Gmail call currently spawns a fresh `gws` process that re-reads credentials and
re-initialises the keyring. Using a persistent authenticated HTTP client instead removes
that fixed cost from thousands of calls.

### 2c. Make UI operations optimistic

This is the "operations feel laggy" complaint specifically. `_dismiss` in
`keeper_server.py:717` is deliberately synchronous, so clicking dismiss blocks the panel
for a full Gmail round-trip. The fix: update the UI immediately, perform the Gmail write
in the background, and roll back with the existing toast if it fails. Dismiss goes from
~0.6s to instant.

### 2d. Use Gmail's batch endpoints

`batchModify` is already used for archiving, but thread reads are still one-by-one.
Batching metadata reads cuts round-trips further.

### Realistic outcome

| Phase | Now | After |
| --- | --- | --- |
| Reading mail | ~4.5 min | ~20s |
| Classification | ~60-150s | ~5-10s |
| Dismiss / archive click | ~0.6s block | instant |

### Where Rust genuinely earns its place

After the above, if the run is still not fast enough, the remaining hot spot is
`dashboard_state.py` plus JSON state churn under a file lock. That is real CPU work and a
fair Rust candidate. I'd rather revisit it with measurements after the I/O fix than guess
now. The SwiftUI panel is untouched throughout, as you asked.

## Part 3: Order of work

Each step is independently shippable and independently revertible.

1. **Add Jev as a provider** in `lib/llm.py`. It becomes a new entry alongside claude and
   codex, selectable in settings. Nothing breaks; existing providers keep working.
2. **Port thread classification to Jev** behind a settings toggle.
3. **Run both side by side on your real inbox** and compare every disagreement before
   trusting it. This is the checkpoint that matters; see below.
4. **Parallelize the read phase.** The big speed win.
5. **Make dismiss and archive optimistic.** The felt-responsiveness win.
6. **Port catchup and learn** to Jev once classification is proven.
7. **Persistent HTTP client**, replacing per-call subprocesses.
8. **Re-measure, then decide on Rust** with real numbers.

Drafting stays on Claude throughout.

## Part 4: How we'll know it worked

Not vibes. Concrete checks:

- **Agreement check.** Run old and new classification over the same ~200 real threads,
  diff every decision, and review each disagreement by hand. Jev only takes over when you
  are satisfied with the disagreements.
- **No-loss check.** Confirm zero threads that the old path kept get archived by the new
  one without you explicitly agreeing. Reversibility is the product.
- **Timing check.** Measure end-to-end run time before and after, on your real inbox.
- **Feel check.** Click dismiss and confirm the row disappears with no perceptible pause.

## The honest risks

- **Jev is days old** (launched Sep 15, 2026) and in early access. Benchmarks are
  vendor-reported. Keeping Claude as a selectable fallback provider is not optional.
- **The judgment will differ**, not necessarily worsen. Step 3 exists precisely to catch
  this before it touches your mail.
- **Concurrency can hit Gmail rate limits.** Needs exponential backoff, and the API docs
  specify the same for Jev's 429 and 529 responses.
- **The key is in `.env`.** Worth confirming `.env` is gitignored before any commit.

## Summary in one paragraph

Jev is a real fit for zero's core job: it turns "should this thread stay in your inbox?"
into typed, confidence-scored decisions that can't mis-parse and can't hallucinate, at
about a quarter of a cent per run. But it will not fix the lag on its own, because the
lag is ~4.5 minutes of sequential network waiting, not slow Python. Doing both, Jev for
judgment and concurrency for I/O, takes a run from minutes to seconds and makes clicks
feel instant. Rust is a reasonable later step for a smaller remaining slice, and the plan
defers it until there are measurements to justify it rather than spending your time on a
rewrite that wouldn't touch the real bottleneck.
