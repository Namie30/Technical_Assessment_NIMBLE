Subject: storeFulfillment API investigation — findings and current status

Hello,

We've completed our investigation into the high failure rate you reported on
Home Depot's storeFulfillment endpoint. Here's what we found, what we've
fixed, and where things currently stand.

## Two real defects in the request, both fixable

**1. The request was being sent as GET, not POST.**
Your payload didn't specify a `method`, which means it defaulted to GET. The
GraphQL query was being attached as a body on a GET request, which isn't how
GraphQL endpoints expect to be called. Adding `"method": "POST"` and
`"Content-Type": "application/json"` corrects this.

**2. Only one of Home Depot's session cookies was being sent.**
The request included `bm_s` alone. In our testing, we observed Home Depot
issuing a matched set together, `bm_s`, `_abck`, `bm_sz`, and `bm_so`,
generated simultaneously by the same browser session. Sending one in
isolation is unlikely to satisfy validation expecting a complete set. Worth
correcting, though we should be clear: we tested with all of these supplied
fresh from a live session, and it did not resolve the block on its own.

Both of these are worth correcting in your integration regardless of what
follows.

## The remaining blocker and honest status
We tested this extensively: ten distinct approaches, including forcing our
highest-stealth browser driver, using our dedicated Home Depot integration,
capturing the call from inside a live rendered browser session, sending the
request with XHR-style headers rather than page-navigation headers, and
supplying genuinely fresh, correctly-paired session cookies captured
moments earlier.

Every approach was blocked. The most common response was a clean 403 from
Home Depot's servers; deeper attempts (loading product pages, triggering the
call in-session) timed out entirely rather than returning any error.

**What this tells us:** the block is happening at Akamai's bot-detection
layer, based on signals beyond the request's contents, likely IP
reputation, TLS fingerprinting, and behavioural session analysis. It isn't
something correctable by adjusting headers, cookies, or request structure
alone. Notably, we confirmed that Home Depot's homepage loads without issue
through the same infrastructure, so this is targeted protection on their
inventory data specifically, not a general access problem.

## What we'd recommend in the meantime
- **Apply both fixes above.** They're genuine defects, and you want them
  corrected whichever route you take.
- **Treat timeouts as failures in your monitoring**, not just error codes.
  Several of our deeper attempts stalled silently rather than returning a
  403, if your system only watches for explicit errors, some failures may
  be going unrecorded.
- **Build in retry-with-backoff** rather than assuming a reliable
  connection. This endpoint's protection appears to be actively maintained,
  and behaviour may shift over time.

## Next steps on our side
We're continuing to look at options for this target specifically. Home
Depot's protection on this endpoint is unusually aggressive at present, and
we'll update you if that changes or if we identify a reliable approach.

Happy to walk through any of the above in more detail, or to look at
alternative data sources if per-store inventory is a hard requirement for
your use case.

Kind regards,
Nikoloz