---
name: seo-geo
description: Improve website visibility in search engines and generative AI answer surfaces. Use for technical SEO, on-page SEO, content audits, metadata, structured data, crawl/indexing, canonicals, sitemaps, robots, internal links, local/ecommerce search, AI Overviews, answer-engine optimization, generative engine optimization, entity clarity, citation readiness, and SEO/GEO review before launch or migration.
---

# SEO/GEO

Improve discoverability without hacks: make pages crawlable, indexable, understandable, useful to humans, and easy for answer engines to cite accurately.

## Workflow

1. Classify the request:
   - technical SEO audit or implementation
   - on-page SEO and metadata
   - content structure, search intent, or internal linking
   - structured data or rich result eligibility
   - migration, redirects, canonicals, noindex, sitemap, or robots review
   - local, ecommerce, docs, blog, or landing-page visibility
   - generative search, AI Overviews, AEO, GEO, answer inclusion, or citation readiness
2. Gather the minimum context that changes the recommendation:
   - target audience, market, language, and geography
   - primary entities, products, services, locations, and competitors
   - site stack, rendered HTML, routes, sitemap, robots, canonicals, and metadata templates
   - Search Console, analytics, crawl, or rank data if provided
   - launch, migration, or traffic-risk timeline
3. If `company.md` exists at the workspace root or the user provides company guidelines, read it before recommending changes. Apply brand, content, compliance, localization, platform, analytics, and release constraints unless they conflict with higher-priority instructions or search quality.
4. Prioritize fixes by impact, confidence, and risk. Separate blockers from nice-to-have optimizations.
5. Prefer implementation-ready recommendations: exact metadata, route rules, schema type, redirect map, content section, internal link, or test command.
6. Avoid manipulative tactics: keyword stuffing, doorway pages, mass query-variant pages, fake reviews, inauthentic mentions, hidden text, or claims without evidence.

## SEO Standards

- Make important pages crawlable, indexable, canonical, internally linked, and rendered with their primary content available.
- Use one clear title, meta description, canonical URL, language/locale signal when relevant, and descriptive URL per indexable page.
- Keep robots.txt for crawl management, not privacy or deindexing. Use noindex, auth, or removal controls when content must not appear in search.
- Use structured data only when it matches visible page content and a relevant schema type. Validate it with an appropriate rich-result or schema validator when practical.
- Preserve useful old URLs during migrations with explicit redirect maps, canonical intent, sitemap updates, and post-launch checks.
- Treat JavaScript SEO as rendered-output work: inspect what crawlers and users can actually see, not only source files.
- Check page experience when it affects users or crawl/rendering: mobile fit, latency, intrusive overlays, broken media, and accessible semantic structure.

## GEO Standards

- Treat GEO as search visibility plus answer usefulness, not a separate bag of tricks. Start with strong SEO, crawlability, and helpful content.
- Make pages entity-clear: name the company, product, category, audience, location, dates, authors, credentials, and source of claims where relevant.
- Add original evidence where possible: first-hand observations, benchmarks, pricing facts, case details, quotes, tables, FAQs, methodology, screenshots, or examples.
- Structure content for extraction without fragmenting it unnaturally: concise answer blocks, descriptive headings, comparison tables, definitions, pros/cons, and source-backed claims.
- Keep facts fresh and timestamped when freshness matters. Do not invent statistics or authority signals.
- Use `llms.txt` only when a target platform or team explicitly wants it. Do not present it as required for Google Search or as a substitute for crawlable HTML.
- For brand visibility in AI answers, prefer authoritative owned pages plus real third-party proof over inauthentic mentions.

## Audit Checklist

- Can search engines discover and render the important content?
- Are the right pages indexable and the wrong pages excluded with the right mechanism?
- Are titles, descriptions, headings, canonicals, hreflang, and social previews unique and coherent?
- Do sitemaps, internal links, breadcrumbs, redirects, and pagination reflect the real site structure?
- Does visible content answer a real query better than commodity summaries?
- Are claims attributable, current, and supported by visible evidence?
- Does structured data match visible content and pass validation?
- Would an answer engine extract the correct entity, answer, source, and next action from the page?
- Are launch or migration risks covered by monitoring, rollback, and post-release checks?

## Output Shape

For audits:

1. verdict and highest-impact fix
2. prioritized issues with evidence
3. exact recommended changes
4. validation steps and tools
5. residual risks or data needed

For implementation:

1. files or routes changed
2. behavior/search-signal change
3. how to validate rendered output, schema, crawl/indexing, and analytics
4. remaining rollout or monitoring gap
