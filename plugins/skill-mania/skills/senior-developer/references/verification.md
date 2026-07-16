# Verification Checklist

Run the deterministic floor first; only then judge the softer evidence. Report every check with its real result — a check not run is a named gap, not a pass.

## Deterministic Floor
1. Build or typecheck the changed packages with the project's own commands.
2. Run the project linter on the changed files only.
3. Run the narrowest test that exercises the changed contract, then the module's suite.
4. For a bug fix: show the regression test failing before the fix and passing after. A fix without a failing-first test is unverified.
5. Diff scope: the final diff contains only hunks that serve the stated task. Unrelated formatting, renames, or drive-by edits are defects.

## Evidence Checklist
- The changed public contract (signature, schema, route, event) is either unchanged or the break is named with its callers.
- Error paths and empty/boundary inputs of the changed code are exercised, not just the happy path.
- Concurrency, ordering, or caching assumptions the change relies on are stated and tested where testable.
- Anything that could not be verified locally (external service, migration against real data, load behavior) is listed as residual risk with a suggested verification step.
