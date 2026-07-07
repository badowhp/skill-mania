# Local And Ecommerce Search Reference
Use this for location pages, local businesses, ecommerce catalogs, merchant feeds, product variants, inventory, reviews, shipping, returns, and structured-data parity.

## Local Search
- Treat each real location as an entity with a stable name, address, phone, hours, service area, canonical URL, and ownership process.
- Keep website facts, business-profile facts, citations, and visible page content consistent. Do not create fake offices, service areas, reviews, or doorway location pages.
- Give each useful location a page with unique operational information: services, access, hours, contact path, local proof, and relevant policies.
- Use the most specific supported `LocalBusiness` subtype that matches visible content. Verify current required and recommended properties against official search documentation.
- Separate organization-wide data from location-specific data and model departments only when they are real, user-visible entities.

## Ecommerce Search
- Keep product identity stable across canonical URLs, structured data, merchant feeds, inventory systems, and analytics.
- Model variants intentionally. Define the parent/group, variant-changing attributes, canonical behavior, availability, price, images, identifiers, and internal links.
- Keep price, availability, shipping, return policy, ratings, and review counts consistent between visible content, structured data, and feeds.
- Prefer crawlable category and product paths with useful pagination or incremental-loading fallbacks. Avoid indexable filter combinations that create duplicate or empty pages.
- Distinguish purchasable product pages from editorial product-review pages before choosing structured data.
- Never mark up hidden, fabricated, stale, or third-party claims as first-party product or review data.

## Verification
- Inspect rendered visible content and JSON-LD together.
- Validate representative product, variant, category, organization, and location pages.
- Check Merchant Center or equivalent feed diagnostics when a feed exists.
- Test out-of-stock, sale-price, variant-switching, discontinued, redirected, and location-closed states.
- Verify current platform rules before treating eligibility as guaranteed; valid markup does not guarantee a search feature.

## Primary Sources
When exact current requirements matter, verify against:

- Google Search Central local business structured data: https://developers.google.com/search/docs/appearance/structured-data/local-business
- Google Search Central ecommerce structured data: https://developers.google.com/search/docs/specialty/ecommerce/include-structured-data-relevant-to-ecommerce
- Google Search Central product structured data: https://developers.google.com/search/docs/appearance/structured-data/product
