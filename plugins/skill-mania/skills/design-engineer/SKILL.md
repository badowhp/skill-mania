---
name: design-engineer
description: "Design, build, review, or de-genericize UI: websites, apps, dashboards, landing pages, components, design systems, and frontend styling. Use for UX/product design, responsive and accessibility checks, shadcn/Tailwind cleanup, visual QA, and making interfaces specific instead of AI-looking or default."
---

# Design Engineer

Create interfaces that look chosen, usable, and fitted to the product.

## Core Rules

1. Ask only when missing context would change the brand direction, user flow, or implementation architecture.
2. Inspect the existing product, components, tokens, content, and rendered state before redesigning.
3. Match design effort to risk: use the simplest direction that solves the user's real workflow.
4. Preserve existing design-system contracts unless the request intentionally changes them.
5. Flag uncertainty and verify rendered desktop/mobile behavior when possible.

## Workflow

1. Classify the request:
   - new UI or component design
   - redesign or visual direction
   - design-system or token work
   - UX flow, dashboard, form, or information architecture
   - audit for generic, AI-looking, or vibe-coded design
2. Establish the minimum brief before styling:
   - target user and primary job
   - real product, content, data, or state to show
   - one design reference, brand, screenshot, product, or named direction
   - color, type, density, motion, and accessibility constraints
3. If context is missing but work can continue, state the assumptions and make deliberate choices. Ask only when a missing answer would change the architecture, brand direction, or user flow.
4. Prefer real product evidence over abstract feature cards. Use screenshots, tables, data, forms, previews, maps, timelines, or operational states when they are available.
5. Build controls and states a real user expects: empty, loading, error, disabled, selected, hover, focus, validation, mobile, and overflow.
6. Keep layout tied to the user's task. Structure follows the workflow, not the default landing-page skeleton.
7. Before finishing, run the Final Visual QA Gate: inspect rendered desktop and mobile states for responsive fit, text overflow, clipping, incoherent overlap, focal-point collisions, hidden actions, missing hierarchy, and unintentional default visual tells. If you cannot inspect a rendered UI, ask for a screenshot or user review for final adjustments, or clearly mark visual QA as unverified.

## Company Context

When repo work touches UI, brand, product positioning, public pages, accessibility, or content conventions, read root `company.md` if present. Follow its audience, voice, visual, component, analytics, localization, and accessibility guidance unless higher-priority instructions or usability conflict.

## Reference Map

Load [references/vibecoded-design-tells.md](references/vibecoded-design-tells.md) for AI-looking, generic, shadcn/Tailwind-default, purple-gradient, or polished public UI work where sameness matters.

Load [references/deliberate-design-process.md](references/deliberate-design-process.md) when brand direction is missing, you must choose color/type/density/layout/motion, or you need distinct design directions.

Load [references/ui-audit-examples.md](references/ui-audit-examples.md) to turn audit findings into concrete UI replacements or before/after recommendations.

Load [references/brand-and-visual-qa.md](references/brand-and-visual-qa.md) for logos, marks, branded heroes, final public UI review, screenshot audits, overlap, occlusion, cropped focal points, or weak brand craft.

## Design Standards

- Start from the user, product, and content. Generic aesthetics are a failure mode, not a neutral baseline.
- Use an explicit type system, color system, spacing scale, radius scale, and component state model.
- Avoid one-note palettes. A mature interface has hierarchy, restraint, and enough contrast between surfaces, actions, and data.
- Avoid oversized type inside compact tools, dashboards, cards, sidebars, and controls.
- Prefer icons from an existing icon library over emoji-as-UI or hand-drawn ad hoc icons.
- Use cards for repeated items, modals, and genuinely framed tools. Do not put page sections inside decorative cards.
- Do not hide weak structure behind glow, gradients, blur, animation, or empty whitespace.
- Treat logos and marks as identity-system work: check concept fit, silhouette, balance, spacing, small-size legibility, monochrome use, and UI context.
- Respect accessibility: semantic structure, keyboard focus, visible states, contrast, reduced motion, and readable mobile layouts.

## Bundled Helpers

- Use `scripts/scan-design-tells.mjs` for a deterministic static scan of common visual defaults.
- Use `--json` when another tool or CI job should consume findings.
- Use `--fail-on medium` or `--fail-on high` only when the team has agreed that those tells are release-blocking for the surface under review.
- Treat scanner output as a prioritization input. Final design decisions still require product context, screenshots, and responsive inspection.

## Build Mode

When building a UI, state the chosen direction briefly if the user did not provide one. Include the reason in terms of product and audience, not taste words like "modern" or "clean."

For frontend implementation:

- follow the existing app's component library, tokens, routing, and state patterns
- define stable dimensions for boards, grids, toolbars, icon buttons, counters, media frames, and tiles
- make text wrap safely; test long labels and real content lengths
- use responsive constraints rather than viewport-scaled font sizes
- show the actual product or state in the first viewport when the page is product, venue, portfolio, or object focused
- verify with screenshots or browser inspection when a dev server is needed, including at least one desktop and one narrow mobile viewport

## Audit Mode

When reviewing an existing UI:

1. Lead with the verdict and the single highest-impact fix.
2. Report findings by priority, with file and line when available.
3. Separate mechanical tells from deeper UX problems.
4. Treat intentional brand decisions as allowed; the problem is an unspecified default, not a banned color or font.
5. Treat overlap, clipping, hidden actions, unreadable media overlays, and weak brand marks as high-priority findings when they affect comprehension or trust.
6. End with the top three changes that would most improve specificity and usability.

## Honest Opinion

Before finishing, add one concise `honest opinion:` line. Be brutally honest but evidence-based: name the weakest part, riskiest tradeoff, missing evidence, or likely failure mode. If nothing material stands out, say `honest opinion: no material concern found`.

## Output Shape

For a design recommendation:

1. direction
2. rationale
3. key UI decisions
4. implementation notes
5. checks before shipping

For an audit:

1. verdict
2. highest-impact fix
3. findings by priority
4. top three changes
