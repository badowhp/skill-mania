---
name: seo-geo
description: Improve visibility in search engines and generative answer surfaces. Use for technical/on-page SEO, content audits, metadata, structured data, crawl/indexing, canonicals, sitemaps, robots, internal links, local/ecommerce search, AI Overviews, AEO/GEO, entity clarity, citation readiness, and launch or migration review.
---

# SEO/GEO

Improve discoverability without hacks: make pages crawlable, indexable, understandable, useful to humans, and easy for answer engines to cite accurately.

## Core Rules

1. Ask only when missing context changes the market, audience, crawl/indexing risk, migration plan, or claims.
2. Inspect rendered output, templates, routes, metadata, canonicals, robots, and sitemaps before recommending changes when available.
3. Match solution weight to search risk. Prefer exact, low-risk fixes over speculative visibility work.
4. Preserve URL, canonical, metadata, and content contracts unless a migration or cleanup intentionally changes them.
5. Flag freshness, evidence, and platform uncertainty; verify current rules when exact external requirements matter.

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
3. If root `company.md` exists or the user provides company guidelines, read it before recommending changes. Apply brand, content, compliance, localization, platform, analytics, and release constraints unless higher-priority instructions or search quality conflict.
4. Prioritize fixes by impact, confidence, and risk. Separate blockers from nice-to-have optimizations.
5. Prefer implementation-ready recommendations: exact metadata, route rules, schema type, redirect map, content section, internal link, or test command.
6. Avoid manipulative tactics: keyword stuffing, doorway pages, mass query-variant pages, fake reviews, inauthentic mentions, hidden text, or claims without evidence.

## Reference Map

Load [references/technical-seo.md](references/technical-seo.md) for crawl/indexing, metadata, canonicals, robots, sitemaps, structured data, JavaScript SEO, migrations, local/ecommerce/docs visibility, launch audits, and post-release checks.

Load [references/generative-search.md](references/generative-search.md) for AI Overviews, AEO/GEO, answer inclusion, entity clarity, citation readiness, freshness, evidence, and brand visibility in answer engines.

## Tool Output

- Use RTK when available for verbose crawl, build, lint, test, or log output.
- Inspect raw rendered HTML, headers, robots, sitemap, schema, and Search Console or analytics exports when exact tags, URLs, or evidence matter.

## Honest Opinion

Before finishing, add one concise `honest opinion:` line. Be brutally honest but evidence-based: name the weakest part, riskiest tradeoff, missing evidence, or likely failure mode. If nothing material stands out, say `honest opinion: no material concern found`.

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
