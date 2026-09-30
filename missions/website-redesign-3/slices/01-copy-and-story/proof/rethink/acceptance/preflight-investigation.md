# Tightened B preflight and Chromium asset-delivery investigation

Status: preflight only, not a stable-SHA acceptance record. Final designer freeze, new readers and independent QA remain pending.

## Observations

- At 01:29Z the working-tree page-B HTML Git blob was `04b58710f0e36b57cc8932bb8b21997204682c93` before and after each whole-page preflight. Shared kit assets were not frozen.
- WebKit returned 142 PASS / 0 FAIL. Chromium returned 136 PASS / 10 FAIL. The latter failures included repeated `net::ERR_CONNECTION_RESET` for `/kit/sections.js`, incomplete section beats and a hidden Copy command control. An exit status of zero was not a pass: the old designer-owned harness did not set a failing exit status. Its live version now sets `process.exitCode = fail ? 1 : 0` (observed 01:36Z).
- A sequential Chromium reproduction after both whole-page jobs ended still failed to load `sections.js` in both success and denied clipboard contexts. This rejected the narrow hypothesis that only simultaneous WebKit and Chromium jobs caused the issue.
- Native HTTP fetching succeeded. The 4568-byte local script had no working-tree modification. No owner proof-server restart or change was made.
- Two bounded comparisons at 01:35Z and 01:36Z then passed on both the shared Python proof origin and a temporary read-only Node origin. Both parser script requests and a client fetch returned 200. Adding the same success/denied clipboard init script still passed on both origins. The temporary server was closed by the diagnostic script.
- The issue is therefore intermittent on the checked surface. These later passes do not establish a root cause, do not show that it was fixed, and do not erase the earlier failed preflight. One sequential whole-page repeat was started at 01:39Z. Its result will be added after completion.

Raw whole-page logs remain in:

- `/Users/light/.jcode/scratch/zero-tightened-preflight-chromium-1790731599/pages-chromium.log`
- `/Users/light/.jcode/scratch/zero-tightened-preflight-webkit-1790731621/pages-webkit.log`

The read-only diagnostic script and its two raw results are retained beside this note. They compare origin delivery, not user comprehension or conversion.

## Verifier correction

The copywriter-owned public-edge verifier previously accepted the unavailable-clipboard state solely because the Copy button was hidden and the command remained present. A dropped section script could produce that same state. Each fault context now records its own resource failures and runtime errors and requires a successful `sections.js` response before evaluating its clipboard state. Success and denial wait for the announced status rather than using a fixed 80 ms delay.

The extracted unchanged decision first reproduced two false-positive regressions (3 PASS / 2 FAIL). After the guard, all five new clipboard decision tests passed. The combined existing plus new regression suite returned 33 PASS / 0 FAIL at 01:39Z. This is a harness-unit and package regression result, not final selected-B browser acceptance.

## Acceptance boundary

Do not reuse these moving-source preflight logs as the final result. Receive the designer's stable B SHA, verify served HTML and every shared kit asset against it, include the two clipboard states in the 549-word inventory, then run the final public interfaces, canonical destinations, browser paths, readers and exact-SHA QA. Deployment and production edits remain held.
