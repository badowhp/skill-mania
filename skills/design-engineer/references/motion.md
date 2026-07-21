# Motion And Scroll Choreography

Motion is a distinct implementation layer: add it last, after layout and states are locked, and only over a composition that already works static.

## Motion Tokens
- Define motion in `DESIGN.md` as tokens per role, not per element: enter, exit, move, emphasis. Each role gets a duration and an easing curve.
- Choose curves deliberately. Framework defaults (`ease-in-out`, `linear`) read as generated on brand surfaces; a custom `cubic-bezier` per role is the cheapest distinctiveness available.
- Durations: micro-interactions 100–200ms, structural transitions 200–400ms, scroll-driven reveals tied to scroll progress rather than fixed time. Anything above 500ms must justify itself.

## Register Rules
- Product surfaces: motion confirms causality (this opened because you clicked). Quiet, short, interruptible, never blocking input. No scroll choreography in repeated workflows.
- Brand surfaces: motion can carry the narrative — staged reveals, parallax depth, kinetic type — but each moving element needs a reason in the composition, and the page must still read with motion removed.

## Scroll Choreography
- Prefer CSS scroll-driven animations or IntersectionObserver over raw scroll listeners; a `scroll` listener needs throttling, passive flags, and a performance check on mid-range mobile.
- Choreograph in stages: what the reader sees at 0%, at first scroll commitment, and at each section boundary. One idea moves at a time; competing simultaneous animations read as noise.
- Pin/scrub effects (progress-linked transforms) must degrade to a static readable layout when JavaScript fails or the viewport is short.

## Non-Negotiables
- `prefers-reduced-motion` is mandatory: reduced variants keep opacity fades at most and remove transforms, parallax, and autoplaying movement.
- Animate only `transform` and `opacity` on scroll paths; layout-triggering properties (top, height, margin) cause jank.
- Motion never hides content from keyboard or assistive tech: animated elements stay in the accessibility tree, and focus order matches visual reveal order.
- Verify on a narrow viewport and with reduced motion enabled before claiming the motion layer done.
