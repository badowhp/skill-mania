# Browser Evidence

## Choose The Smallest Existing Runner
- Use the repository's Playwright suite when it already owns browser setup, auth, fixtures, and stable selectors.
- Use the bundled helper when Playwright is already installed and a running URL is available.
- Use `agent-browser` or another approved browser tool when it is already configured; do not add auth plugins or save credentials for a one-off review.
- Do not add browser automation only to make an unverified claim look verified.

## Minimum Matrix
- Capture the changed route at desktop and narrow-mobile sizes.
- Exercise the primary task and one relevant empty, loading, error, validation, permission-limited, or long-content state.
- Inspect accidental horizontal overflow, page and console errors, failed requests, and a keyboard-focus step. Capture the focused state so the visible indicator can be reviewed.
- Capture the first stable paint. Capture fallback and final content separately when streaming or loading behavior is material.

## Stable Visual Comparisons
- Freeze time, random seeds, locale, timezone, feature flags, API fixtures, and animations before comparing images.
- Mask or remove volatile areas such as clocks, ads, avatars, live metrics, maps, and randomized media.
- Review a visual diff manually. A small pixel delta can hide a broken action, and a large delta can be harmless font rasterization.

## Interpret Findings
- Horizontal overflow, a failed required request, or an uncaught console error is a concrete finding.
- A visible focus target is evidence of keyboard reachability, not complete accessibility proof.
- A clean browser report does not prove hierarchy, copy quality, brand fit, authorization, or business behavior.
- Report missing auth, data, device, and browser evidence plainly instead of inferring success.
