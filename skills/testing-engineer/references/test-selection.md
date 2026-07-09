# Test Selection

Choose the test layer by the boundary where confidence is needed.

## Layers
- Unit: pure logic, validation, formatting, state transitions, and edge cases inside one module.
- Integration: database, framework wiring, queues, file system, caches, or multiple modules with real adapters.
- Contract: API, event, CLI, schema, package, or service boundary that another consumer depends on.
- E2E: user-critical flows, routing, browser behavior, authentication, payment, checkout, onboarding, or high-value release smoke.
- Visual smoke: layout, responsive, screenshot, canvas, or media rendering risks that static tests cannot prove.

## Default Choice
1. Start at the lowest layer that can fail for the real bug.
2. Move up a layer when the risk is in wiring, serialization, permissions, routing, persistence, browser behavior, or integration semantics.
3. Add E2E only for flows whose breakage would be expensive or invisible to lower-level tests.
4. Add a smoke test when exhaustive coverage is too slow but release risk still needs a gate.

## Regression Tests
- Capture the original failure condition before changing code when feasible.
- Keep the test near the contract that failed.
- Include the negative case when the fix is about validation, permissions, or boundaries.
- Do not add a broad E2E regression if a focused unit or integration test proves the exact failure.

## TDD Loop
1. Write the failing test for the intended behavior.
2. Confirm the failure message points at the missing behavior, not broken setup.
3. Implement the smallest correct change.
4. Refactor only after the test is green.
5. Add nearby edge cases only when they protect the same behavior.

## Data And Fixtures
- Use named fixture builders for repeated domain objects.
- Keep factories explicit enough that test intent remains visible.
- Avoid global mutable fixture state unless the runner isolates it.
- Prefer deterministic IDs, clocks, locales, and time zones for boundary-sensitive behavior.
