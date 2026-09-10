# Task 2 - Home Depot Federation Gateway (`storeFulfillment`) Investigation

## Overview
A customer reported a high failure rate when calling Home Depot's internal
`storeFulfillment` GraphQL API via Nimble's Web API. This document describes
the investigation: reproduction of the failure, identification of concrete
bugs in the original request, and enumeration of every dependency the
request relies on, including the layers that remain blocked even after
those bugs are fixed.

## Files in this submission

- `investigate.py` - the main investigation script, containing all test
  variants (baseline through TRY 10). Earlier tests are commented out so
  only the active one runs; each writes its result to the log.
- `investigation_log.jsonl` - timestamped raw output from every test run,
  appended automatically. This is the primary evidence for the findings
  below.
- `extract_cookies.py` - helper script used to pull the real Akamai cookie
  values out of the log for TRY 7, rather than copying them by hand from a
  large JSON file.
- `customer_email.md` - the customer-facing summary of findings.

## Executive Summary
The original request had **two real, fixable defects**:
1. Sent as `GET` with a GraphQL body attached (should be `POST`)
2. Included only one (`bm_s`) of the ~4 cookies Akamai issues as a matched
   set (`bm_s`, `_abck`, `bm_sz`, `bm_so`)

Both were identified, fixed, and tested. **Neither fix, nor any combination
of fixes, resolved the underlying block.** The endpoint remains protected by
Akamai Bot Manager at a layer that persists regardless of request
correctness.

Across the baseline reproduction and nine further test variants, the
dominant outcome was a clean `403 Forbidden` from Home Depot's server,
occurring on the large majority of direct-call attempts. A minority of runs
instead returned `500` ("can't download the query response") or `555`
(execution timeout), and the deeper session-based variants (product-page
network capture, the dedicated e-commerce endpoint, and in-session
`http_request`) consistently timed out rather than returning any explicit
error at all.

The predominance of a clean, repeatable `403` indicates a deliberate,
rule-based rejection by Akamai's bot detection rather than a flaky or
overloaded target. Notably, the less explicit failure modes (timeouts,
"can't download") clustered specifically around the deeper, more complex
access attempts, suggesting protection that escalates the further into the
site's infrastructure a request tries to reach, and which is harder to
diagnose from the client side than a clean rejection would be.

## Target
POST https://apionline.homedepot.com/federation-gateway/graphql?opname=storeFulfillment

via Nimble's Web API: `https://api.webit.live/api/v1/realtime/web`

## Auth
`Basic base64(account_email:account_password)`, confirmed working, same
method established in Task 1.

## Investigation Log
All tests were run against the live endpoint. Full timestamped raw output
for every attempt is preserved in `investigation_log.jsonl`. Test numbering
matches the `# TRY N` markers in `investigate.py`.

**Baseline - reproduce the customer's exact request**
Sent the request as documented in the ticket: same URL, same single `bm_s`
cookie, same GraphQL body, no explicit method set.
Result: `403` on the large majority of runs, with occasional `500`
("can't download the query response") and one `555` (execution timeout).
Confirms accurate reproduction of the reported failure. The dominant,
repeatable `403` indicates a deliberate rejection rather than a flaky
target; the rarer variants show some variability in how the protection
responds.

**Driver override - `driver: vx10-pro`**
Forced Nimble's highest stealth tier (headfull, "heavily fortified targets"
per Nimble's documentation), leaving everything else unchanged.
Result: `403`, consistently, across repeated runs.
Rules out driver selection and browser-fingerprint quality as the fix, even
maximum available stealth does not change the outcome.

**TRY 1 - Network capture on the Home Depot homepage**
Loaded `homedepot.com` with `render: true` and a `network_capture` filter
watching for any `storeFulfillment` call.
Result: `200`, page loaded cleanly with full content, but `results` was
empty. Notably, the response headers contained **real, freshly-issued Akamai
cookies** (`bm_s`, `_abck`, `bm_sz`, `bm_so`), proving Nimble's proxy
network can reach and be trusted by the site at this depth.
Confirms the call only fires in a product-page context, and that basic site
access is not the problem.

**TRY 2 - Network capture on a real product page**
Same approach, pointed at an actual product page rather than the homepage.
Result: Timed out after 60 seconds.
Deeper page access stalls where the homepage did not, the first sign that
resistance escalates with depth.

**TRY 3 - Nimble's dedicated e-commerce endpoint (`vendor: homedepot`)**
Used `/realtime/ecommerce` with `vendor: homedepot` and `zip: 10001`,
Nimble's own purpose-built, maintained integration for this retailer, rather
than a hand-constructed request.
Result: Timed out after 90 seconds.
Even Nimble's specialized tooling for this exact site is affected.

**TRY 4 - Same endpoint, simpler product page**
Repeated TRY 3 against a minimal product (a $3.98 bucket: no variants, no
sale pricing, minimal page weight) to isolate whether page complexity was
causing the stall.
Result: Timed out after 90 seconds.
Rules out page size/complexity as the cause.

**TRY 5 - `http_request` fired from inside a live rendered session**
Loaded a real product page with `render: true`, waited for the page and its
Akamai sensor scripts to settle, then fired the `storeFulfillment` call from
*within* that same live browser session via `render_flow`.
Result: Timed out after 90 seconds.
Session-based triggering is blocked as well, not only cold replay.

**TRY 6 - Explicit `method: POST`**
The original request never set `"method"`; per Nimble's documentation it
defaults to `GET`, meaning a GraphQL body was being sent over GET. Corrected
to `POST` with `Content-Type: application/json`, all else unchanged.
Result: `500` ("can't download the query response").
Confirms the method defect was real. Fixing it alone is not sufficient.

**TRY 7 - Method fix plus the complete, real, matched cookie family**
Captured genuine `bm_s`, `_abck`, and `bm_sz` values from the successful
TRY 1 session and sent all three together (rather than the single stale
`bm_s` the original request used).
Result: Timed out after 90 seconds.
Genuinely fresh, correctly-paired cookies still did not resolve the block.

**TRY 8 - Same-session cookie capture and immediate reuse**
Eliminated any gap between cookie minting and use: loaded the page,
captured cookies via `get_cookies`, and fired the API call in the same
`render_flow` execution, on the same connection.
Result: Timed out after 200 seconds.
Rules out cross-session/IP cookie binding as the remaining fixable cause.

**TRY 9 - `Origin` and `Referer` headers plus NY geo-targeting**
Added the browser headers a real in-page fetch would always carry
(`Origin: https://www.homedepot.com`, `Referer:` the product page), and set
`state: NY` so the exit IP matched the `10001` Manhattan zip in the request
variables.
Result: `403`, on repeated runs.
Standard browser-fingerprint headers and geographic consistency did not
change the outcome.

**TRY 10 - `is_xhr: true` (XHR-style request headers)**
Every prior direct call was sent as a page navigation, meaning Nimble
attached document-request headers (`Sec-Fetch-Mode: navigate`,
`Sec-Fetch-Dest: document`, and an HTML `Accept` header). This is a
mismatch: the target is an internal API that a real browser only ever
reaches via background JavaScript, never by navigation. Nimble's `is_xhr`
parameter switches the request to XHR-style headers
(`Sec-Fetch-Mode: cors`, `Sec-Fetch-Dest: empty`, JSON `Accept`), matching
how the call is actually made in practice. Tested with the method fix,
`Origin`/`Referer`, and NY geo-targeting all applied.
Result: `500` ("can't download the query response"), on repeated runs.
The request-type mismatch was real and worth correcting, but resolving it
did not change the outcome.

## Confirmed Root Causes (fixable, real bugs)
**1. HTTP method mismatch.** The original request never set `"method"` in
the payload. Per Nimble's own documentation, `method` defaults to `GET`.
Sending a GraphQL body via `GET` is non-standard and was confirmed, via
Nimble's own request/response docs, to default this way unless explicitly
overridden.

**2. Incomplete Akamai cookie set.** The original request sent only `bm_s`.
A real browser session sends a *matched family* of cookies together
(`bm_s`, `_abck`, `bm_sz`, `bm_so`), generated simultaneously by the same
session. Sending one in isolation, even a fresh one, is itself an
inconsistency Akamai's validation likely flags, independent of staleness.

Both are legitimate findings a customer can act on immediately, even though
neither resolves the deeper issue below.

## The Unresolved Layer: Akamai Bot Manager
After both bugs above were fixed, requests continued to fail, inconsistently,
across every architecture tried:
- Direct replay (with corrected method, headers, and genuinely fresh,
  correctly-paired cookies)
- Nimble's dedicated `homedepot` vendor endpoint
- Session-based capture (`network_capture`)
- In-session request triggering (`http_request` inside `render_flow`),
  including zero-gap same-session execution

**Independent corroborating evidence:** the investigator's own browser(mine),
tested from two separate networks (home connection and mobile data),
received an Akamai edge-level "Access Denied" (`errors.edgesuite.net`) when
attempting to load `homedepot.com` directly, confirming this is not a
scripted-traffic-only phenomenon, but broad, currently-aggressive protection
at the network/IP-reputation level, separate from anything fixable through
request construction.

The **predominance of a clean, repeatable `403`** across direct-call
attempts indicates a deliberate, rule-based rejection by Akamai's bot
detection rather than a flaky or overloaded target. The less explicit
failure modes, `500`/"can't download the query response", `555` execution
timeouts, and outright connection timeouts, clustered specifically around
the deeper, more complex access attempts (product-page network capture, the
dedicated e-commerce endpoint, and in-session `http_request`). This pattern
suggests protection that escalates the further into the site's
infrastructure a request tries to reach, and which becomes progressively
harder to diagnose from the client side: a clean `403` at least tells you
you've been rejected, whereas a silent stall gives no signal to react to at
all.

## Known Limitations of This Investigation
- The task's example GraphQL `query` field was provided truncated
  (`query storeFulfillment(...)`); no complete, valid GraphQL query text was
  available. Even in a hypothetical scenario where Akamai's layer were
  bypassed, the request body itself may be malformed for reasons unrelated
  to bot detection, this could not be verified, since no test reached that
  point.
- It could not be confirmed whether `itemId: 325573249` (from the task's
  example) is still a valid, in-catalog product, independent of the
  blocking.
- Given that a small number of runs produced different failure modes than
  the dominant `403`, it's possible a fraction of attempts would succeed
  under the same conditions. The sample size (baseline plus ten variants,
  several repeated 2-4 times) supports "resistant," though the consistency
  observed across repeats makes occasional success unlikely.
- Home Depot's site-specific headers could not be replicated. Their
  frontend attaches identifying headers to internal GraphQL calls
  (`x-experience-name`, `apollographql-client-name`, `apollographql-client-version`,
  and similar). Capturing the real values requires observing a live page make
  the call in browser DevTools, which was not possible, the site returned an
  Akamai "Access Denied" page from two separate networks. Sending invented
  values would not have produced an interpretable result (a failure could
  mean either the headers don't matter, or that the guessed values were
  wrong), so this was left as a documented gap rather than a test.


## Recommendations
1. **Apply both confirmed fixes** (explicit `POST`, full matched cookie
   set) as baseline hygiene, they are real defects worth correcting
   regardless of the Akamai layer.
2. **Do not rely on cookie replay across separate requests**, even fresh
   ones. If cookies must be used, they should be captured and used within
   the same session/connection, immediately, this reduces but does not
   eliminate risk.
3. **Expect a persistent, non-zero failure rate on this endpoint** given
   current Akamai protection levels observed during this investigation.
   Recommend the customer's system treat both explicit error codes *and*
   long timeouts as failure signals, and implement retry-with-backoff logic
   rather than expecting a fully reliable direct integration.