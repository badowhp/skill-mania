# Caching And Routing

## Start With The Contract
- State who owns the data, which responses may be stale, the maximum acceptable age, and what happens when the cache or origin is unavailable.
- Separate per-request deduplication, process-local memoization, shared application cache, browser cache, CDN cache, and persistent data. They have different keys, failure modes, and invalidation paths.
- Include every response dimension that changes meaning in the cache key or `Vary`: tenant, authorization class, locale, device variant when intentional, feature flag, and representation version.
- Never put user-specific or authorization-dependent content in a shared cache without an explicit isolation proof.

## Make Invalidation Real
- Prefer a named invalidation path tied to the write or publish event over a vague TTL-only promise.
- Bound cache stampedes with request coalescing, a lock with expiry, stale-while-revalidate, or another measured strategy. Do not let an expired hot key fan out unrestricted origin requests.
- Decide whether negative results, failures, and partial data are cacheable. Keep their TTL shorter and observable when they can hide recovery.
- Measure hit rate, stale-served rate, eviction, origin latency, invalidation delay, and errors before tuning TTLs or capacity.

## Routing And Edges
- Preserve stable public URLs, method semantics, status codes, redirects, canonical headers, and idempotency behavior unless a migration is planned.
- Put authentication, authorization, request limits, timeouts, retries, and upstream selection at deliberate boundaries. Do not rely on a proxy default for a security or reliability property.
- Preserve `Cache-Control`, `Vary`, `ETag`, and representation-specific headers through reverse proxies and CDNs. Test the browser and edge response, not only the origin.
- Treat a route rewrite, cache-key change, or redirect change as a compatibility change. Verify deep links, back/forward navigation, error pages, and old URLs.
