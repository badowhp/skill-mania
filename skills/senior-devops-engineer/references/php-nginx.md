# PHP And Nginx Reference
## Runtime Model
- Treat Nginx, PHP-FPM, the application, cache, session store, queue workers, cron, and database as one operational system.
- Separate static asset delivery, web execution, background jobs, and scheduled jobs in both process model and monitoring.
- Prefer explicit health endpoints and readiness behavior over “port is open” checks.
## Nginx Standards
- Keep one clear server block per site or concern.
- Route PHP requests through explicit `fastcgi_pass` upstreams and avoid overly broad location rules.
- Serve static assets directly with caching headers where appropriate.
- Set request size, timeout, and buffering values according to application behavior rather than copying internet snippets.
- Log request time, upstream time, status, host, URI, request ID, and client IP chain in a parseable format.
- Use TLS termination, redirects, and security headers deliberately. Avoid duplicate or conflicting header injection across layers.
## PHP-FPM Standards
- Use separate pools for materially different apps or trust boundaries.
- Size `pm.max_children`, `pm.max_requests`, and process manager mode from actual memory and latency behavior, not default examples.
- Enable OPcache in production and review memory, revalidation, and deployment invalidation strategy.
- Expose pool status or metrics through a protected path for observability.
- Keep upload limits, memory limits, execution timeouts, and slowlog thresholds aligned with real workload needs.
- Run PHP-FPM under the least-privileged account that still supports filesystem and socket requirements.
## Deployment Concerns
- Prefer release directories and a current symlink for VM-based PHP deploys.
- Run Composer installs in a repeatable build environment where possible, not ad hoc on fragile production hosts.
- Make migration strategy explicit:
  - backward-compatible migrations before code switch
  - incompatible migrations only with a clear maintenance or expand-contract plan
- Keep cache warmup, queue restarts, and opcache behavior part of the rollout design.
- Separate application config from code and inject secrets through environment or secret retrieval, not committed files.
## Troubleshooting Patterns
- `502` or `504` usually means an upstream path issue, PHP-FPM saturation, socket permissions problem, timeout mismatch, or slow dependencies.
- `499` often means the client gave up before the upstream completed. Check latency and proxy timeout behavior.
- Rising queue delay with healthy web nodes usually points to worker concurrency, lock contention, or downstream dependency saturation.
- High CPU in PHP-FPM often comes from inefficient code paths, disabled OPcache, too many workers, or lock contention.
- Frequent restarts can hide memory leaks, bad health checks, or low limits rather than fixing the root cause.
- Debug from edge to app:
  - load balancer or CDN
  - Nginx
  - PHP-FPM
  - app logs
  - database, cache, queue, and external APIs
## Review Checklist
- Is request routing explicit and safe?
- Are PHP-FPM pools isolated and sized from observed behavior?
- Are logs, metrics, and health checks sufficient for first-response debugging?
- Is deployment structured for rollback and low-downtime operation?
- Are cache, sessions, queues, and cron included in the operational model?
