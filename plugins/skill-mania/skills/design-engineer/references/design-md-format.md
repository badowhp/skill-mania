# DESIGN.md Format
Use this when creating or updating root `DESIGN.md`.

Keep it concise, concrete, and reusable by any agent. If a section cannot be backed by the interview, repo inspection, rendered UI, or explicit user preference, mark it as provisional rather than inventing certainty.

## Required Shape
Use these six headings in this order:

```markdown
# Design System: <product or project name>

## 1. Overview
## 2. Colors
## 3. Typography
## 4. Elevation
## 5. Components
## 6. Do's And Don'ts
```

## 1. Overview
Include:

- creative north star: one named direction or metaphor
- register: brand, product, or mixed with route-level notes
- audience and primary job
- tone and density
- technology detected: framework, styling, component library, icon/media libraries, route or page structure
- source-of-truth files: token files, CSS, theme config, component folders, screenshots, brand assets
- references and anti-references
- freshness date or "seed" status

## 2. Colors
Use semantic roles rather than only swatches:

- page surface, raised surface, inset surface
- text, muted text, disabled text
- primary action, secondary action, focus
- border, divider, shadow or glow when allowed
- success, warning, danger, info
- chart or status colors when the UI needs data

Prefer OKLCH when the project already uses modern CSS color. Otherwise match the existing stack. Explain why the palette fits the product, not just what it looks like.

## 3. Typography
Define:

- body face
- display or heading face, if different
- monospace role, if any
- type scale and line-height rules
- numeric behavior for prices, metrics, tables, logs, and counters
- content limits: line length, truncation, wrapping, labels, and long words

## 4. Elevation
Define the depth model:

- flat, bordered, raised, overlay, modal, popover
- radius scale and where each radius is allowed
- border style
- shadow or glow rules
- motion rules for entering, exiting, hover, focus, loading, and reduced motion

## 5. Components
Document the components that matter for the target surface:

- buttons and links
- nav, tabs, filters, command bars
- cards, list rows, tables, charts, timelines
- forms, inputs, validation, help text
- dialogs, menus, popovers, toasts
- empty, loading, error, success, disabled, selected, hover, focus, and permission-limited states
- media frames, screenshots, image crops, and captions
- responsive rules for mobile, desktop, and dense data

Name content limits where layout can break.

## 6. Do's And Don'ts
Write sharp rules that prevent drift:

- use these tokens, components, and assets
- avoid these AI-looking defaults and anti-references
- keep these accessibility and responsive checks
- document intentional exceptions with a reason

Good rules are enforceable. Weak rules like "make it clean" do not belong here.
