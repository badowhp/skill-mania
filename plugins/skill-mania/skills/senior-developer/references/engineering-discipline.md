# Engineering Discipline
Use this when ordinary code-level work needs a higher professional bar than "make the diff pass."
## Context Intake
- Identify the behavior being changed, the caller that observes it, and the contract it must preserve.
- Search for existing helpers, fixtures, patterns, and parallel implementations before adding a new one.
- Read enough of the surrounding code to understand ownership boundaries and invariants.
- Check for generated files, package managers, formatters, and test conventions before editing.
- Treat missing requirements as assumptions only when the wrong answer would be low risk.
## Change Design
- Prefer a local fix when the defect is local.
- Introduce an abstraction only when it removes real duplication, clarifies a contract, or matches an established repository pattern.
- Keep parsing, serialization, validation, authorization, and persistence boundaries explicit.
- Preserve backward compatibility unless the user asks for a breaking change.
- Consider edge cases before coding: empty input, null or missing fields, invalid types, duplicates, ordering, time zones, retries, and partial failure.
- For migrations or data-shape changes, define read compatibility, write compatibility, rollout order, and rollback behavior.
## Implementation Discipline
- Make illegal states harder to represent with types, schemas, validation, or small helper functions already used in the repo.
- Avoid broad rewrites while fixing a narrow bug.
- Do not hide errors behind catch-all fallbacks unless the fallback is a real product decision.
- Keep logging useful and safe. Never log secrets, tokens, credentials, or sensitive personal data.
- Keep code reviewable: cohesive commits or patches, clear names, and no unrelated formatting churn.
- Prefer deterministic behavior over ambient state, time, network, global mutation, or implicit ordering.
## Testing And Verification
- Start from a reproduction for bugs and a behavior contract for features.
- Add a regression test when the changed behavior has user impact or could return.
- Cover the edge case that caused the bug, not only the happy path.
- Use integration tests when the risk is at a boundary between modules, services, storage, or UI state.
- Treat snapshots and broad smoke tests as weak evidence unless paired with a targeted assertion.
- Run formatting, linting, type checking, or tests according to repository norms and report anything skipped.
## Review Discipline
- Lead with correctness, data loss, security, reliability, and user-visible regressions.
- Tie each finding to file, line, behavior, and impact.
- Separate required fixes from preferences.
- Avoid style comments unless they affect maintainability or violate local convention.
- Recommend the smallest remediation that closes the risk.
## Professional Bar
- Leave the touched area easier to reason about.
- Make assumptions visible.
- Keep changes reversible when requirements are uncertain.
- Make failure modes observable.
- Respect user changes and repository conventions.
- Prefer durable correctness over cleverness.
