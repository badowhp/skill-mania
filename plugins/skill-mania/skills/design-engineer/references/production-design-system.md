# Production Design System
Use this when the task asks for production UI, design-system hardening, tokens, component libraries, shadcn/Tailwind cleanup, or handoff-quality frontend work.
## Production Bar
A production design system gives the next screen the same answer as this screen. It must define reusable decisions, not only a polished mockup.

Required outputs:

- foundations: color roles, type scale, spacing scale, radius scale, elevation/shadow, icon style, motion rules
- layout primitives: page shell, section bands, grids, split panes, tables, lists, sidebars, inspectors, media frames
- component contracts: variants, sizes, states, responsive behavior, accessibility, and content limits
- state inventory: default, hover, focus, active, selected, disabled, loading, empty, error, validation, overflow, mobile
- verification plan: build/lint/typecheck, static scanner, screenshot viewports, accessibility and long-content checks
## Discovery Pass
Before changing a system, inspect:

- existing token files, Tailwind config, CSS variables, theme providers, component wrappers, storybook, screenshots, and app shell
- reused primitives such as Button, Card, Dialog, Input, Table, Tabs, Menu, Toast, Badge, Sidebar, and Header
- data density and user jobs: compare, triage, edit, approve, monitor, buy, learn, or publish
- brand evidence: logo, product screenshots, photography, named competitors, domain conventions, and existing copy voice

Decide whether to preserve, extend, or replace each layer. Do not create parallel tokens or duplicate components unless the current contract cannot support the requested behavior.
## Token Rules
Use semantic roles first and raw colors second.

- Color: define background, surface, elevated surface, text, muted text, border, primary, secondary, success, warning, danger, info, focus, and data/category roles.
- Typography: define body, compact UI, display, mono/numeric usage, line-height, weight, and heading rhythm. Keep hero-scale type out of dense tools.
- Spacing: define a compact interaction scale and a page layout scale. Avoid padding as a substitute for information hierarchy.
- Radius and elevation: define small, medium, and large usage rules. Reserve pills and large radius for an intentional component role.
- Motion: define when motion communicates state, progress, or spatial relationship. Honor reduced motion.

Hard-coded one-offs are acceptable only for isolated assets, generated media, or explicitly local exceptions. Otherwise promote repeated values to tokens.
## Component Contracts
For reusable components, specify:

- purpose: what job the component performs and where not to use it
- variants: visual intent, hierarchy, destructive/primary/secondary roles, and density
- states: hover, focus, active, selected, disabled, loading, empty, error, validation, skeleton
- content limits: longest expected labels, wrapping rules, truncation, icon-only labels, and localization risk
- responsive behavior: breakpoints, min/max widths, stacking, sticky behavior, overflow, and touch targets
- accessibility: semantic element, ARIA only when needed, keyboard flow, visible focus, contrast, reduced motion

Avoid cosmetic wrappers around primitive components. If a component exists only to add a shadow, gradient, or large radius, the system is probably missing a layout primitive or token.
## Page And App Patterns
Choose structure from the user job:

- Operational tools: table/list plus filters, queue, detail inspector, bulk actions, clear empty/error/loading states.
- Dashboards: compare-first grids, timelines, alerts, drilldowns, and compact metrics with units and freshness.
- Editors/builders: canvas or preview, left navigation, inspector controls, persistent save/export state, undo/redo when relevant.
- Public pages: first viewport shows the product, person, place, object, output, or proof; next section remains visible; proof beats feature-card filler.
- Commerce/product pages: media, variants, price/availability, trust, specs, comparison, and post-purchase questions before generic benefits.
## Shadcn And Tailwind Hardening
Keep useful primitives, but make the system own the look.

- Theme CSS variables and Tailwind tokens before styling individual screens.
- Audit radius, border, shadow, typography, density, focus, and disabled states together. Changing only the primary color usually leaves a default feel.
- Replace repeated Card/Header/Content scaffolds with domain layouts: rows, forms, split panes, timelines, inspectors, tables, or media grids.
- Prefer component variants over repeated utility chains when the pattern appears three times.
- Keep utility classes for local layout and state, not as an ungoverned design language.
## Verification Checklist
Before calling production UI done:

- run build/lint/typecheck or the closest project gate
- run `scripts/scan-design-tells.mjs` on changed UI files or the app surface when applicable
- capture or inspect desktop and mobile renderings
- test long labels, empty/error/loading states, selected/disabled/focus states, and content overflow
- verify no overlapping sticky elements, clipped text, unreadable overlays, hidden actions, or focal-point collisions
- check contrast, keyboard focus, tap targets, and reduced motion
- name any verification gap in the final response
