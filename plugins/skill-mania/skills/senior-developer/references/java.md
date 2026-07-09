# Java

## Build And Runtime
- Use the repository wrapper (`./mvnw` or `./gradlew`) and declared toolchain before relying on a globally installed JDK or build tool.
- Keep dependency, plugin, annotation-processor, and test changes reproducible. Do not mix broad version upgrades into a focused application fix.
- Treat generated sources, migration tooling, and framework configuration as contracts; inspect their ownership before changing build files.

## Concurrency And Services
- Use virtual threads only for workloads with large numbers of concurrent, mostly blocking I/O tasks. Do not convert a fixed pool into an equally sized virtual-thread pool.
- Diagnose virtual-thread pinning and saturation with JFR or `jcmd` before changing concurrency architecture.
- Keep request timeouts, cancellation, executor ownership, retry budgets, and connection pools explicit. Do not mix blocking request paths into a reactive stack without a measured boundary.
- For Spring services, protect actuator and management endpoints, propagate observation context across async work, and preserve existing validation and transaction boundaries.

## Caching And Verification
- Define cache keys, TTL, invalidation, serialization, and failure behavior before adding `@Cacheable`, a local map, or a distributed cache.
- Do not make caching mandatory for every test environment; keep tests able to run with a controlled or disabled cache implementation.
- Run the narrowest affected test class first, then the module suite. Use an integration test when configuration, serialization, transactions, or framework wiring carries the risk.
