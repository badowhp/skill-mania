# Vibe-Coded Design Tells
Use this as a priority guide, not a list of banned aesthetics. A tell is an unchosen default. If the project deliberately chose a flagged pattern for brand or product reasons, keep it and record why.

This reference is based on JCarterJohnson's `vibecoded-design-tells` research and Claude `unslop-ui` skill: https://github.com/JCarterJohnson/vibecoded-design-tells. The repo reports a Reddit-mined study of AI-built site complaints and packages those findings as build and audit guidance.
## Table Of Contents
1. Highest priority tells
2. Medium priority tells
3. Lower priority tells
4. Do not over-chase
5. Manual checks
## Highest Priority Tells
### Untouched shadcn or Tailwind defaults
Signals:

- stock `Card` styling repeated across the page
- slate, zinc, gray, or neutral defaults everywhere
- generated radius, border, ring, and spacing tokens left unchanged
- components look like the docs screenshot

Fix:

- set real theme tokens before building
- choose a primary color, neutral ramp, spacing rhythm, and radius scale for the project
- keep shadcn/Tailwind if useful; theme them so the framework is not the visual identity
### AI purple, violet, indigo, and purple-blue gradients
Signals:

- violet, indigo, purple, or fuchsia as the default primary color
- purple-to-blue or purple-to-pink hero gradients
- gradient-filled headings or CTA text

Fix:

- use a project-specific brand color or sampled palette
- keep gradients rare, restrained, and justified
- never use gradient text as the default heading treatment
### The newer tasteful default
Signals:

- warm cream or beige page background
- serif display face such as Instrument Serif, Fraunces, Playfair, Cormorant, Spectral, or DM Serif
- sage, forest, or emerald green as the primary accent
- generated product card or screenshot on the right side of a split hero

Fix:

- do not replace purple-gradient defaults with cream-serif-sage defaults
- anchor color and type to a real brand, product, place, image, or reference
- if this look is intentional, keep it and document the choice
## Medium Priority Tells
### Centered hero plus three feature cards
Signals:

- centered headline, two CTAs, and a symmetric three-card feature grid
- repeated "Features," "Benefits," or "How it works" grids with icon, title, and blurb

Fix:

- structure the page around the user's goal
- show the product, real data, or real workflow
- vary section density and layout instead of stacking identical grids
### Large rounded corners and pills everywhere
Signals:

- `rounded-2xl`, `rounded-3xl`, or `rounded-full` applied broadly
- all buttons are pills
- cards, inputs, images, and panels share one large radius

Fix:

- define a small radius scale by component role
- reserve pills for a deliberate interaction or brand reason
### Unmotivated animation and glow
Signals:

- every section fades in on scroll
- hover-grow on every card
- neon glows, colored shadows, or text shadows added without a brand reason

Fix:

- use motion to communicate state, hierarchy, or progress
- honor `prefers-reduced-motion`
- remove glow unless the brand or content explicitly calls for it
### Emoji-as-icons
Signals:

- emoji used as feature icons, section bullets, or heading markers

Fix:

- use a real icon set such as Lucide, Heroicons, or Phosphor
- use no icon when the icon adds no meaning
## Lower Priority Tells
- Generic font defaults: Inter, Geist, Roboto, Arial, or plain system fonts used without a type decision.
- Generic AI marketing copy: "Transform your...", "Supercharge...", "Unleash...", "Effortlessly...", "reimagined."
- Stock illustration sources such as undraw-style blobs when a real screenshot or domain image would be stronger.
- Centered everything with oversized whitespace and no information hierarchy.

Fix these when cheap, but do not let them distract from the core direction, layout, color, type, and product evidence.
## Do Not Over-Chase
The upstream research treats these as low-signal or contested:

- mesh, blob, and aurora backgrounds
- bento grids
- glassmorphism
- dark mode itself
- Tailwind or shadcn as tools

Only flag them when the implementation is visibly default, incoherent, or unsupported by the product direction.
## Manual Checks
The strongest scanner cannot judge these reliably, so inspect by eye:

- text overflow, clipping, or labels that do not fit
- inconsistent spacing and misaligned edges
- repeated section shapes with no hierarchy
- fake screenshots, fake metrics, or abstract visuals where real product evidence should appear
- mobile layouts that hide the primary action or crush important content
