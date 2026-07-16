# Verification Checklist

Verify against rendered output and live responses, never against source templates alone.

## Deterministic Floor
1. Fetch the changed URLs and read status codes, redirect chains, and response headers (`curl -sSIL`); a 200 body behind a 302 chain or a stray `noindex` header invalidates the work.
2. Compare rendered head to intent: title, meta description, canonical, robots meta, hreflang; when the page is client-rendered, check the rendered DOM rather than the HTML source.
3. Validate robots.txt syntax and confirm the changed paths are crawlable; validate sitemap XML (`xmllint --noout`) and that it lists the canonical URLs only.
4. Validate structured data with a schema validator; every required and recommended property of the chosen type is present or the omission is intentional.
5. Confirm canonicals are absolute, self-consistent across paginated or parameterized variants, and match the sitemap.

## Evidence Checklist
- Internal links to the changed pages resolve without redirects and use the canonical form.
- The change is observable in the named measurement baseline (Search Console coverage, log-file crawl hits, answer-engine citation checks) or the monitoring step is scheduled with an owner.
- No claim about ranking or traffic outcomes is made without post-release data; state what will be measured and when instead.
- Anything unverifiable in this environment (production headers, CDN behavior, live crawl) is listed as a pending check, not assumed done.
