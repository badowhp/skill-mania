# Brand-Surface Expressiveness

Generated UI regresses to the mean: safe type scales, default shadows, centered symmetric layouts. On brand surfaces (marketing, editorial, portfolio, campaign, showcase) the mean is the failure mode — distinctiveness is the requirement, executed with intent rather than decoration.

## Typographic Contrast
- The most common weakness is a too-safe scale. Display type on a brand surface should contrast hard with body text: think 4x or more between hero display and body size, and pair the size jump with a weight or width change.
- Pick one expressive move for the display face (scale, weight, width, or an earned typeface choice) and keep body text disciplined and readable. Two expressive moves compete; three collapse.
- Set real headline copy, not lorem: expressive type exposes weak copy, and line breaks are a design decision at display sizes.

## Composition Vocabulary
Name the composition style in `DESIGN.md` before building — it is a decision, not an emergent property. Useful vocabulary:
- editorial grid: strong columns, generous margins, type-led hierarchy
- asymmetric split: weighted halves, content anchored off-center
- layered depth: overlapping media, type over image, controlled z-axis
- brutalist block: flat planes, hard edges, oversized type, exposed structure
- object-centered: one product or artifact staged like photography, everything else recessive

Grid-breaks, overlap, and dramatic negative space are legitimate tools when the underlying grid exists to break; a first viewport must still communicate subject, audience, and next action.

## Distinctive Materials
- Shadows, easings, radii, and textures are identity carriers. Define bespoke values in `DESIGN.md` (a lighting direction for shadows, a signature easing) instead of accepting framework defaults — the scanner flags `shadow-md`-style defaults on purpose.
- One signature detail used consistently (a rule line, a corner treatment, a hover behavior) does more than five unrelated flourishes.

## Guardrails
- Expressiveness never buys out of accessibility: contrast ratios, focus visibility, keyboard order, and reduced-motion behavior hold on brand surfaces exactly as on product surfaces.
- The register boundary holds: expressive treatment stops where repeated task completion begins. A dashboard linked from the hero is a product surface.
- Every expressive choice traces to `DESIGN.md` like any other token; edge-seeking is not an exemption from the fidelity gate.
