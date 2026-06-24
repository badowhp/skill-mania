# UI Audit Examples

Use these examples to turn heuristic design tells into product-specific recommendations. Treat them as patterns, not rules: the issue is an unchosen default, not the mere presence of a color, component, or library.

## Common Tells And Better Moves

| Tell | Why it feels generic | Stronger alternative |
| --- | --- | --- |
| Purple-to-blue gradient hero with vague headline | The visual direction says "SaaS template" before it says what the product does. | Lead with a real product state, user artifact, environment, or result. Choose color from brand, domain, or data semantics. |
| Big rounded cards nested inside bigger rounded cards | The page becomes a stack of decorative containers instead of a workflow. | Use full-width sections, tables, split panes, list rows, or tool surfaces. Reserve cards for repeated objects. |
| "Transform your workflow" copy | It avoids the actual user job and could fit any product. | Name the task, object, constraint, or outcome: invoices reconciled, incidents triaged, scenes revised, plans approved. |
| Emoji icons in buttons or feature grids | Emoji looks casual, inconsistent, and detached from the design system. | Use the existing icon library, align stroke weight, and reserve expressive illustration for intentional brand moments. |
| Default gray/slate Tailwind ramp everywhere | Neutral ramps without contrast decisions make hierarchy feel generated. | Define surfaces, borders, muted text, accent, warning, success, and destructive tokens with real contrast targets. |
| Empty whitespace around tiny content | It reads as padding used to create a false premium feel. | Increase useful density: show filters, state, metadata, preview content, or next actions. |

## Before/After Framing

When writing an audit finding, use this shape:

1. Name the tell.
2. Explain the product impact.
3. Recommend a concrete replacement.
4. Say how to verify the improvement.

Example:

```text
The pricing cards use the same purple gradient and oversized radius as the hero, so the plans blur together. Replace the decorative gradient with comparison-first structure: plan names, workload limits, support SLA, and the two real differentiators in the first row. Verify on mobile that the longest plan name wraps without changing card height.
```

## Dashboard-Specific Fixes

- Prefer rows, tables, timeline lanes, kanban columns, split panes, and inspector panels over decorative card grids when users compare or operate on many items.
- Keep hero-scale type out of dashboards. Use compact headings, dense metadata, and clear state badges.
- Use color to encode status, severity, ownership, or category. Do not let accent color become a background theme.
- Make empty, loading, error, filtered, selected, and bulk-action states look designed, not only the happy path.

## Landing-Page-Specific Fixes

- Show the product, place, person, object, or output in the first viewport.
- Let the headline identify the brand, object, or literal offer; put claims and value props in supporting copy.
- Avoid feature-card filler before proof, examples, screenshots, cases, or workflows.
- Keep the next section partially visible in the first viewport so the page does not feel like a poster.

## Shadcn And Component Library Fixes

- Keep shadcn components if they are the existing system; theme them intentionally instead of replacing them reflexively.
- Audit radius, border, shadow, typography, and density tokens together. Changing only color usually leaves the default feel intact.
- Replace repeated `CardHeader` and `CardContent` layouts with domain layouts when the content is operational: row groups, forms, tables, sidebars, inspectors, or timeline items.
