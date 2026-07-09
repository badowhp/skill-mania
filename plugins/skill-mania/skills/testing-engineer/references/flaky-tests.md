# Flaky Tests

Treat flakes as signal loss. A retry may reduce noise, but it is not a fix unless the underlying nondeterminism is understood and accepted.

## Triage
1. Collect failure logs, seed, runner shard, timing, environment, and recent code changes.
2. Re-run the single test locally and in the closest CI-like mode.
3. Check for order dependence by running the surrounding file or suite in a different order.
4. Identify the likely source: time, randomness, async race, network, shared state, parallelism, leaked resources, fixture reuse, or environment drift.
5. Add temporary instrumentation only if it is removed or converted into useful assertion output.

## Stabilization
- Replace sleeps with waits for observable conditions.
- Freeze or inject clocks for time-sensitive logic.
- Isolate database rows, files, ports, queues, users, browser contexts, and caches.
- Make async work explicit: await jobs, flush queues, or assert final observable state.
- Avoid depending on unordered collections unless the order is part of the contract.
- Keep external services behind deterministic fakes unless the integration itself is under test.

## Retries And Quarantine
- Use retries as a temporary containment tool, not a permanent quality strategy.
- Quarantine only when the test blocks delivery and there is an owner, issue, expiry, and replacement coverage.
- If a flaky test guards a high-risk release path, fix or replace it before weakening the gate.
- Document residual risk when removing, skipping, or broadening timeouts.
