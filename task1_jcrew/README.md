# Task 1 - Scrape & Parse a J.Crew Product Page (Nimble Web API)

## Objective
Use Nimble's Web API to fetch a J.Crew product page and return structured data
(title, price, color) using a custom parser, alongside the raw HTML.

## Product page used
**Washed piqué button-down shirt** (Union Blue)
https://www.jcrew.com/p/mens/categories/clothing/tshirts-and-polos/t-shirts/washed-piqueacute-button-down-shirt/CV409?display=standard&fit=Classic&color_name=union-blue&colorProductCode=CV409

Chose this page because it has a single, unambiguous price (no sale pricing), a clear color variant selected via the URL query string, and a best-seller badge confirming it's a stable, real product page.

## Endpoint
POST https://api.webit.live/api/v1/realtime/web

## Files in this submission
- `extract.py` - the main script: fetches the page, and (once `parse: true`
  is set) returns the parsed structured data.
- `find_selectors.py` - exploratory script used to test CSS selectors
  offline against the saved HTML, before spending API calls on the real
  parsed request.
- `check_html.py` - verifies the saved HTML is genuine page content, not a
  bot-block/CAPTCHA page.
- `jcrew.html` - the raw HTML snapshot fetched from the API, used for
  offline selector development.
- `result.json` - the final parsed output from the API.
- `test_bearer_auth.py` - a small side-experiment, not part of the required
  solution. After finding that the API key doesn't work with Basic auth, I tested whether it works under the `Bearer` scheme instead. It
  does. Included for completeness since the task asked for an
  API key to be created.

## Approach
1. Made one API call with `render: true, parse: false` to fetch the raw,
   fully-rendered HTML and saved it to `jcrew.html`. All further selector
   work was done offline against this file, no additional API calls spent
   guessing selectors.
2. Verified the saved HTML was real content, not a block page (checked file
   size, searched for "Access Denied" text, and investigated a "captcha"
   substring match, which turned out to be a disabled `enableReCaptcha`
   feature flag inside a JSON config block, not an active challenge).
3. Found selectors using Chrome DevTools on the live page, then verified
   each one against the saved HTML using BeautifulSoup, since DevTools
   selectors weren't always identical to what was in the API-rendered
   snapshot.
4. Made a final API call with `parse: true` and the working parser object,
   confirming all three fields extracted correctly.

## Final selectors used
**Title - `h1`**
Simple, and works because there's exactly one `<h1>` on this page. This is
the least robust of the three: it would break if a second `<h1>` appeared
elsewhere on the page.

**Price - `[data-testid="price"]`**
Chose the `data-testid` attribute over the CSS class sitting on the same
element (`ProductColor__price___K8vPV`). That class has a short
auto-generated suffix (`___K8vPV`) typical of CSS-module hashing, which can
regenerate on every rebuild. `data-testid` attributes are usually added
deliberately by developers for test automation, so they tend to be more
stable.

**Color - `[data-testid="color-name"]`**
Same reasoning as price - chose the attribute over
`.ProductColor__color-name___caUX_` for the same durability reason.

## Auth format - how it was determined
The task specifies Basic authentication but doesn't state the exact
credential format. Three attempts were made:

1. **API key as username, blank password** - `base64("API_KEY:")` →
   `401 - No supported authentication method found for the provided
   credentials`. Ruled out.
2. **Account email as username, API key as password** -
   `base64("email:API_KEY")` → `500 internal server error`. A different
   failure category from 401 (auth accepted, something else failed
   downstream), which suggested the credential *shape* was closer to
   correct.
3. **Account email + actual dashboard password** -
   `base64("email:password")` → `200 success`.

**Conclusion:** Basic auth on this endpoint requires
`base64("account_email:account_password")`, the dashboard login
credentials, not the API key.

**Side note on the API key.** The task asks for a personal API key to be
created under the account, which was done (`heisenbug-hunter`). It isn't
used by this implementation, since this endpoint's Basic auth requires
account credentials rather than the key. Out of curiosity I tested the key
separately under `Bearer` auth against the same endpoint, and it does work
that way, see `test_bearer_auth.py`. The Basic auth version was kept as the final implementation since that's
what the task specifies.

## Parser schema - a second debugging round
The Nimble documentation I initially found (for the `nimble-python` SDK's
`Extract` function) describes a parser schema using a `terminal` type with
nested `selector`/`extractor` objects:

```json
"parser": {
    "title": {
        "type": "terminal",
        "selector": { "type": "css", "css_selector": "h1" },
        "extractor": { "type": "text" }
    }
}
```

Submitting this to `api.webit.live/api/v1/realtime/web` returned:

```json
{"status": "error", "error": "invalid schema: field dynamicParser.extractor is not of type object"}
```

This endpoint uses a different, simpler schema than the SDK wrapper
(confirmed against Nimble's own "Parsing Templates" documentation, which is
specific to this exact endpoint):

```json
"parser": {
    "title": {
        "type": "item",
        "selectors": ["h1"]
    }
}
```

Key differences: `"type": "item"` instead of `"terminal"`, and `"selectors"`
is a plain array of CSS strings rather than a nested selector/extractor
object pair. Switching to this schema fixed the error immediately.

**Takeaway:** Nimble has multiple products/endpoints (the newer
`nimble-python` SDK's `Extract`, and the older/direct `realtime/web`
endpoint used here) with different parser schemas. Documentation for one
doesn't necessarily apply to the other, worth checking the schema against
the specific endpoint in use, not just the first matching example found.

## Note on "Nimble SDK"
The task summary mentions "Nimble SDK" while the detailed instructions
specify the `realtime/web` endpoint with Basic auth. Per Nimble's own
documentation, "Nimble SDK" refers to their hosted infrastructure broadly,
including this Web API, not specifically the `nimble-python` package. This
implementation follows the detailed instructions.

## Result

```json
{
    "color": "Union Blue",
    "entity_type": "Dynamic",
    "price": "$128",
    "title": "Washed piqué button-down shirt"
}
```
All three fields extracted correctly, alongside the raw HTML (available via
`html_content` in the same response when `parse: true` is set).

## Known limitation / further insight
- **Price is returned as a raw string (`"$128"`)**, not a clean number.
  This endpoint's `item`/`selectors` schema doesn't appear to support a
  `post_processor` step (unlike the SDK's `terminal` schema, which does).
  In production, the `$` would need to be stripped and the value cast to a
  number downstream in the consuming application.
- **JSON-LD alternative found and considered.** J.Crew embeds a
  `schema.org/Product` JSON-LD block on this page, containing `name`,
  `sku`, `brand`, `color`, and `offers.price`, with price already as a
  clean number (`128`), not a string with a currency symbol. This would be
  a more robust extraction method than CSS selectors, since JSON-LD is a
  semantic data standard less likely to change than CSS implementation
  details. Not used here since the task explicitly asked for CSS
  selectors, but worth noting as a stronger production approach if field
  format stability mattered more than following the literal instructions.
- **`h1` for title is the least durable of the three selectors** — it
  works only because this page has exactly one `<h1>`. A more robust
  choice, found during exploration, would be `[data-qaid="pdpProductNameTitle"]`,
  which is also present on the page.