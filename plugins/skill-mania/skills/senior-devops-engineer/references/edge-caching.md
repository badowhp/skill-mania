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

## Release Checklist
- Validate a cache-busting or purge path before deploying a content or routing change.
- Roll out path, cache-key, or WAF changes progressively when the edge supports it.
- Keep a fast rollback: previous rule version, disabled policy, traffic shift, or purge procedure with an owner.
