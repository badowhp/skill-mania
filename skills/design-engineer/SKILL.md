---
name: design-engineer
description: "Context-first UI design workflow for websites, apps, dashboards, components, design systems, redesigns, and styling. Use to interview for design context, create or update DESIGN.md, plan and implement UI, de-genericize AI-looking design, inspect colors/technology/examples, or route work through design-reviewer gates. Prefer design-reviewer for standalone critique, senior-developer for non-visual frontend logic, and seo-geo for search visibility."
---
# Design Engineer
Design through durable context, then build. Do not guess a visual system when the repository can carry one in `DESIGN.md`.

## Core Rules
1. Start with context: inspect the product, tech stack, existing UI, routes, tokens, components, assets, screenshots, `company.md`, `PRODUCT.md`, and `DESIGN.md` when present.
2. Run the interview phase before substantial design work when `DESIGN.md` is missing, stale, or too vague.
3. Write or update `DESIGN.md` as the first artifact for new design direction. Keep it concrete enough that another agent can continue the work.
4. Separate phases: interview, `DESIGN.md`, plan, implementation, review. Do not collapse them unless the user asks for a tiny local change and `DESIGN.md` is already fit.
5. Route every substantial `DESIGN.md`, plan, and implementation through `design-reviewer`. Treat review as a gate, not commentary: a user-facing visual rework is not done until the relevant artifact gets `PASS`, or the user explicitly accepts named remaining defects.
6. Use real product evidence: rendered pages, screenshots, existing components, product data, states, user flows, reference sites, brand assets, and actual copy.
7. Distinguish brand surfaces from product surfaces before choosing style. Brand surfaces can be expressive; product surfaces must serve repeated task completion.
8. Preserve existing design-system contracts unless the request intentionally changes them.
9. Verify rendered desktop and mobile behavior when possible. A passing build is not visual QA.

## Phase 1: Interview
Ask only for missing answers that would change the design direction. Otherwise inspect and infer, then state assumptions.

Gather:

- audience, job to be done, primary workflow, and emotional posture
- register: `brand` for marketing, editorial, portfolio, campaign, or showcase; `product` for apps, dashboards, admin, tools, forms, and settings
- target surfaces, routes, components, states, and success criteria
- examples, competitors, screenshots, references, and anti-references
- color, typography, density, motion, accessibility, localization, and content constraints
- technology: framework, router, styling system, component library, tokens, icon library, image pipeline, test/browser tooling
- assets: logos, photos, generated images, product screenshots, fonts, charts, maps, videos, and sample data

When useful references are missing, ask for one real product/site/screenshot or choose a named direction and explain why it fits. Do not use empty words such as "modern", "clean", or "professional" as a direction.

## Phase 2: DESIGN.md
Create or update root `DESIGN.md` before the plan when the work changes visual direction, tokens, component rules, register, or design-system behavior. Load [references/design-md-format.md](references/design-md-format.md) for the exact compact format.

`DESIGN.md` must include:

- creative north star and register
- audience, surface, and task priorities
- colors with semantic roles and rationale
- typography with hierarchy and usage rules
- spacing, radius, elevation, border, icon, media, and motion rules
- component rules for buttons, cards, forms, tables, nav, dialogs, feedback, empty/loading/error states, and content limits
- examples and anti-references
- technology notes and source-of-truth files
- review date or freshness signal

After writing `DESIGN.md`, review it with `design-reviewer`. If it fails, revise the interview assumptions or `DESIGN.md` before planning.

## Phase 3: Plan
Plan from `DESIGN.md`, not from vibes.

Include:

- information architecture and first viewport intent
- token and component changes
- layout grid, spacing rhythm, responsive behavior, and overflow rules
- state inventory: loading, empty, error, disabled, selected, hover, focus, validation, long content, and permission-limited states
- media and data requirements
- accessibility requirements: semantic structure, contrast, focus, keyboard, reduced motion, touch targets
- implementation sequence and smallest reviewable edits
- verification: build/lint/typecheck, design scanner, browser screenshots or inspection, mobile width, long-content checks

Review the plan with `design-reviewer`. If review fails, return to `DESIGN.md` when direction is wrong, or rewrite the plan when execution detail is missing.

## Phase 4: Implement
Implement only after the plan passes, unless the user explicitly asks for exploration or a quick local fix.

- Follow the existing framework, routing, component library, tokens, and state patterns.
- Extend tokens and primitives before scattering one-off styles.
- Use the existing icon library, usually lucide or the local design-system icons.
- Use real or generated bitmap imagery for websites, product pages, portfolios, venues, objects, games, or visual experiences where assets matter.
- Keep dashboards and operational tools dense, scannable, and quiet. Avoid landing-page composition for repeated workflows.
- Keep cards for repeated items, modals, and genuinely framed tools. Do not nest cards.
- Use stable dimensions for boards, grids, toolbars, icon buttons, counters, media frames, and tiles.
- Make text wrap, clamp, or scroll intentionally with worst-case content.
- Avoid reflexive AI tells unless documented in `DESIGN.md`: purple gradients, cream/serif/sage defaults, gradient text, side accent borders, huge rounded icon tiles, identical card grids, nested cards, full-screen hero traps, fake screenshots, vague SaaS copy, and decorative motion.

## Phase 5: Review Loop
Run review after implementation:

1. Run local quality commands available in the repo.
2. Run the bundled `scripts/scan-design-tells.mjs` from the loaded `design-engineer` skill directory when the changed surface is static UI, Tailwind, shadcn, public UI, or likely AI-looking.
3. Inspect rendered desktop and narrow mobile states with browser automation or screenshots when possible.
4. Self-audit the rendered result against `DESIGN.md`, the plan, and the original user ask before asking for final review. Fix obvious weak hierarchy, generic AI defaults, broken mobile layout, missing states, unreadable text, and visual direction drift first.
5. Ask `design-reviewer` for a final implementation review and provide evidence: changed surfaces, screenshot paths or live page notes, scanner output, quality-command results, states inspected, and evidence that could not be gathered.
6. If review returns `FAIL`, return to implementation for execution defects. Return to plan or `DESIGN.md` when the failure is strategic, generic, off-brand, or structurally wrong.
7. If review returns `PASS WITH FIXES`, apply the named fixes and rerun targeted verification plus review. Do not close user-facing visual rework on `PASS WITH FIXES`; close only on `PASS`, or when the user explicitly accepts the named remaining defects.

Do not claim a pass when rendered inspection, scanner output, or review could not run. Name the missing evidence and residual risk. For substantial redesigns, missing desktop or mobile rendered evidence blocks final sign-off.

## Routing Notes
- `design-engineer` owns creation: interview, `DESIGN.md`, plan, and implementation.
- `design-reviewer` owns critique: pass/fail, consultant review, scorecards, and loop decisions.
- Keep this portable. Do not depend on slash commands, plugin-only hooks, or one vendor's skill format in `SKILL.md`.
- Codex can often use browser automation, screenshots, and image generation for visual work. Claude Code may have stronger plugin command routing. The shared skill should still express the same phases and gates in plain Markdown.

## Bundled Helper
Use `scripts/scan-design-tells.mjs` as a deterministic anti-pattern scan. It prioritizes common generated-UI tells; it does not replace rendered review or design judgment.

Use `design-tell-ignore` only for a narrow intentional exception with a product or brand reason.

## Honest Opinion
Use `honest opinion:` when it adds decision value: reviews, audits, recommendations, plans, tradeoffs, or implementation close-outs with a material risk or gap. Be brutally honest and evidence-based. Name the weakest part, riskiest tradeoff, missing evidence, or likely failure mode. Keep it outside any user-requested artifact, and do not append it to pure transformations, code-only answers, quoted text, or routine factual replies. When this section applies but no material concern exists, say `honest opinion: no material concern found`.

## Output Shape
For interview results:

1. assumptions
2. questions still needed
3. `DESIGN.md` changes
4. review result

For a plan:

1. direction from `DESIGN.md`
2. implementation steps
3. states and responsive behavior
4. verification
5. review result

For implementation close-out:

1. direction used
2. files changed
3. verification run
4. reviewer verdict
5. remaining risks, only if material
