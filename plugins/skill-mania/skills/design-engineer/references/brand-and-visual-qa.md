# Brand And Visual QA
Use this for logo work and the final visual review pass before shipping polished UI.
## Logo Consultant Pass
Treat the logo as a small identity system, not a generated icon.

- Start from the brand brief: name, audience, category, positioning, personality, usage contexts, and nearby competitors.
- If the brief is missing but work can continue, choose a direction and state the assumption. Ask only when the answer would change the mark.
- Avoid default monograms in rounded squares unless the concept, category, and usage context justify that exact form.
- Prefer vector-simple marks with a clear silhouette, strong negative space, and enough distinctiveness to survive small sizes.
- Check optical balance, clear space, alignment, stroke consistency, corner treatment, and wordmark spacing.
- Test the mark as favicon/app icon, header lockup, social avatar, monochrome, reversed, and on light/dark backgrounds.
- Do not rely on shadows, gradients, blur, tiny interior details, or color alone for recognition.
- Flag obvious resemblance to major brands or category cliches. Do not claim legal trademark clearance.
## Final Visual QA Gate
Inspect the rendered surface, not just isolated components.

- Check at least one desktop and one narrow mobile viewport. Add tablet and 320px/200% zoom checks when the surface is public, complex, or likely to wrap.
- Capture or inspect the actual changed route, story, or component state. Do not treat a passing build as visual QA.
- Verify that text, cards, headers, CTAs, menus, media, and sticky elements do not overlap, clip, hide each other, or cover the image focal point.
- Test real or worst-case content: long names, long nav labels, multiline headings, empty/error/loading states, and translated or narrow words when relevant.
- Confirm the first viewport has a clear subject, hierarchy, primary action, and a visible path into the next section when the page is public-facing.
- Check that interactive states have stable dimensions and do not cause layout shift.
- Check that focus rings, keyboard navigation, reduced motion, contrast, and tap targets still work after visual changes.
- When media sits behind text or cards, confirm the focal point remains visible and the foreground remains readable at every tested viewport.
- Check that token and component changes did not regress other common states: dialog, menu, toast, form validation, destructive action, and disabled action.
- If a browser or screenshot is unavailable, ask the user for a screenshot or final review pass and name the exact issues to inspect before making last adjustments.
