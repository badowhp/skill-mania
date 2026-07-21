# Pixel-Perfect Replication

Use this workflow when the task is to replicate a screenshot, mockup, or reference design 1:1 rather than to create a direction. Extraction comes first; building from visual memory produces drift.

## Phase A: Extraction
Produce an extraction table before writing any code:

1. Colors: sample every distinct color (background, surfaces, text ramp, accents, borders) and record exact CSS values with their roles in a dedicated Colors block or table.
2. Typography: typeface or closest available match, and per text role the size, weight, line height, letter spacing, and case treatment.
3. Spacing: measure the spacing rhythm — section padding, gaps between repeated items, gutter widths — and derive the base unit if one exists.
4. Geometry: radii, border widths, shadow offsets/blur/color, icon sizes, media aspect ratios.
5. Layout: grid columns, alignment lines, and each element's anchor relative to the grid.

Record uncertainties explicitly (antialiased colors, ambiguous font) instead of guessing silently. When the reference is an image the user supplied, state the measured values back before building so wrong readings die early.

## Phase B: Build Against The Extraction
- Every value in the code traces to a row of the extraction table — the same fidelity rule as `DESIGN.md`, with the extraction as the token source. Run the scanner with `--design-md <extraction file> --fail-on medium` to enforce hex and CSS color-function traceability; inspect named colors and variable resolution manually.
- Build in the same order as the visual hierarchy: structure, then type, then color, then detail geometry, then states the reference implies but does not show (hover, focus).
- States the reference cannot show still follow accessibility rules: real focus visibility and keyboard order are not optional because the screenshot lacks them.

## Phase C: Compare
- Render the result at the reference's dimensions and compare side by side, region by region: alignment lines, spacing rhythm, type color and weight, shadow softness.
- Report deviations with reasons in three classes: rendering-platform limits, deliberate corrections (accessibility fixes), and unresolved mismatches still to fix.
- 1:1 means measured, not remembered: if a region was never compared against the reference, say so rather than claiming fidelity.
