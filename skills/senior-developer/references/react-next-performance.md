# React And Next.js Performance

## Rendering And Data
- Start independent server work early and await it only where the result is needed. Preserve dependency order when work is not independent.
- Keep client component boundaries narrow. Avoid serializing large data or server-only dependencies into client bundles.
- Use Suspense and loading states where streaming improves the task. Verify fallback and final content in a browser rather than inferring behavior from a successful build.
- Avoid module-level mutable request state in server-rendered code. Use request-scoped deduplication for repeated reads before adding a cross-request cache.

## Cache Components And CDN Behavior
- Apply Cache Components only to supported App Router projects and verify the installed Next.js version and migration guidance first.
- Translate existing route-cache behavior deliberately. Dynamic request data, cookies, headers, parameters, and search parameters need an explicit cache or request-time boundary.
- Preserve `Vary` and representation boundaries for HTML, RSC, and prefetch responses. Do not configure a CDN to serve an RSC payload as an HTML response.
- Test the route in development and in a browser after changing cache or routing behavior; a passing build alone does not prove the static shell, fallback, or final content is correct.

## Client Cost
- Remove waterfalls and direct unnecessary barrel imports before reaching for micro-optimizations.
- Load feature-only, heavy client code on demand. Keep third-party scripts non-blocking and measurable.
- Use memoization only for demonstrated expensive work or stable component boundaries. Avoid turning simple expressions into opaque dependency management.
