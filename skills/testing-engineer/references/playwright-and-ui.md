# Playwright And UI Testing

Use browser tests for behavior that depends on actual rendering, routing, JavaScript execution, browser APIs, or user interaction.

## Setup
- Inspect existing routes, test helpers, selectors, auth setup, and server startup before adding tests.
- Use stable user-facing locators first: role, name, label, placeholder, text, or test ID where the UI has no accessible handle.
- Keep authentication, seed data, and network interception local to the test or fixture.
- Avoid arbitrary sleeps. Wait for visible state, URL, response, event, or locator condition.

## Coverage
- Cover the primary happy path plus one meaningful failure or empty state for release-critical flows.
- Add mobile viewport checks when layout, navigation, overflow, or touch controls are part of the risk.
- Use screenshots for visual smoke only when the expected state is stable and reviewable.
- Include keyboard focus, accessible names, form validation, and disabled/loading states for interactive UI.

## Visual QA
- Confirm the page is not blank and the primary content is in the viewport.
- Check desktop and narrow mobile viewports.
- Look for clipping, overlap, hidden actions, offscreen modals, text overflow, and disabled focus styles.
- For canvas or 3D scenes, verify nonblank pixels and that motion or interactivity is observable.

## Network And State
- Mock third-party services when the app contract is already tested elsewhere.
- Use real backend calls when the risk is in integration, permissions, serialization, or data lifecycle.
- Clear storage, cookies, and test data between tests unless a worker-scoped fixture intentionally owns isolation.
