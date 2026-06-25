# Role Selection Reference
Use this when a request could trigger multiple broad skills or overlays.
## Default Routing
- Code-level implementation, bug fix, refactor, tests, or code review: use `senior-developer`.
- Cross-system design, service boundaries, API contracts, data ownership, or ADRs: use `software-architect`.
- Attacker behavior, trust boundaries, sensitive data, exploitability, or security controls: use `security-engineer`.
- Infrastructure, runtime operations, CI/CD, release, observability, incident, backup, or cost work: use `senior-devops-engineer`.
- UI/UX, visual design, frontend polish, responsive states, or vibe-coded design tells: use `design-engineer`.
- Technical SEO, on-page SEO, crawl/indexing, metadata, structured data, Search Console, AI Overviews, AEO/GEO, answer inclusion, or search visibility: use `seo-geo`.
- Manuscript, prose, docs, README text, publishing copy, KDP review, or AI-slop text checks: use `writing-assistant`.
- Explicit "be lazy", YAGNI, minimal solution, shortest path, or Ponytail mode: use `ponytail` as a minimality overlay.
- Explicit "caveman", terse, brief, no fluff, compact, knapp, or kurz: use `caveman` as an output-shape overlay.
## Overlay Rules
- Overlays do not replace the lead role. Pick the domain role first, then apply the overlay to scope or output.
- `ponytail` controls implementation scope and rejects unnecessary work. It does not control tone.
- `caveman` controls final answer length and prose density. It does not reduce implementation, safety, citation, or verification standards.
- If both `caveman` and `ponytail` apply, let `ponytail` minimize the work and `caveman` compress the final response.
- Do not let either overlay remove explicit requirements, security controls, accessibility basics, error handling, data-loss safeguards, blockers, or test gaps.
## Overlap Rules
- If the work changes code but the main risk is authz, tenant isolation, secrets, or exposure, security leads.
- If the work changes code but the main decision is service shape, ownership, or migration, architecture leads.
- If deployment, rollback, runtime, observability, or production blast radius dominates risk, DevOps leads.
- If the work touches frontend code but the user is asking about product feel, layout, states, or polish, design leads.
- If the work touches frontend or content code but the main goal is crawlability, indexability, metadata, snippets, structured data, AI-search visibility, or content discoverability, SEO/GEO leads.
- If the work changes code but the main request is reader-facing wording, docs, release notes, or AI-slop cleanup, writing leads.
- If the work is mostly code but includes user-visible copy, senior-developer leads and applies a writing lens to the text.
- If the user asks for code review without a domain, senior-developer leads and calls out when a specialist review is needed.
## Combination Rules
When two roles are genuinely needed, keep one lead role and one lens:

- senior-developer + security lens: implementation with targeted security checks
- software-architect + DevOps lens: architecture with rollout and operability
- design-engineer + senior-developer lens: UI direction implemented in code
- seo-geo + design lens: discoverable public page with visual and responsive quality
- seo-geo + writing lens: search-intent and answer-ready content without generic copy
- senior-developer + seo-geo lens: code change for metadata, schema, sitemap, redirects, or rendered crawlability
- senior-devops-engineer + security lens: runtime hardening and exposure review
- senior-developer + writing lens: code change with docs, messages, prompts, release notes, or AI-slop text cleanup
