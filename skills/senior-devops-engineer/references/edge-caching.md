# Edge Caching And Routing

## Cache Contract
- Define which routes are public, private, personalized, mutable, or safe to serve stale before configuring a CDN or proxy rule.
- Make cache keys and `Vary` dimensions explicit. Include representation, locale, tenant, or device dimensions only when they genuinely change a response; never share authorization-dependent content without an isolation proof.
- Preserve origin `Cache-Control`, `ETag`, `Last-Modified`, `Vary`, and representation headers unless an edge policy intentionally replaces them and the owner understands the consequence.
- Record the invalidation path, propagation expectation, stale policy, and rollback for every cached mutable surface.

## Edge Safety
- Put TLS, redirect policy, WAF, rate limits, bot controls, request limits, upstream timeouts, and origin access behind explicit, reviewed rules.
- Keep origins private where possible. Allow edge-to-origin traffic through an identity, narrow network policy, or provider control rather than a broad public rule.
- Test deep links, redirect chains, HTTP methods, error pages, browser navigation, and cache behavior at the edge. Origin-only tests do not prove edge behavior.
- Measure cache status, age, origin errors, hit rate, stale responses, purge latency, and origin load before changing TTLs or capacity.

## Implementation Patterns
- Immutable fingerprinted assets: `Cache-Control: public, max-age=31536000, immutable`. HTML and other entry points: short or no edge TTL (`no-cache` or `max-age=0, must-revalidate`) with validators so clients revalidate cheaply.
- Authenticated or personalized responses: `Cache-Control: private` (or `no-store` for sensitive payloads) plus an edge rule that bypasses cache when the session cookie or `Authorization` header is present. Never rely on the origin header alone if the edge is configured to override.
- APIs that can tolerate brief staleness: small `s-maxage` with `stale-while-revalidate`; keep browser `max-age` at 0 so the edge stays the single point of invalidation.
- Normalize the cache key: strip marketing query parameters, lowercase the host, and collapse encodings before keying — every accidental key dimension divides the hit rate.
- Tie deploys to invalidation: fingerprint assets so no purge is needed, and purge or version the few mutable paths (HTML, manifests, sitemaps) as a release step with a named owner.

## Verify With
- `curl -sSI` the same URL twice and read the provider's cache status header (`CF-Cache-Status`, `X-Cache`, `Age`) — first MISS then HIT proves the key works; two MISSes prove it does not.
- `scripts/inspect-http-cache.py <url>` for a redacted, read-only capture of cache and routing headers.
- Test one personalized route while authenticated to prove isolation: a cached private response is a release blocker, not a tuning issue.
- Compare edge response and origin response for the same path; an edge-only or origin-only difference is where the incident will start.

## Release Checklist
- Validate a cache-busting or purge path before deploying a content or routing change.
- Roll out path, cache-key, or WAF changes progressively when the edge supports it.
- Keep a fast rollback: previous rule version, disabled policy, traffic shift, or purge procedure with an owner.
