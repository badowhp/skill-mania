# Observability

## Design The Signal Path
- Start with user-visible latency, traffic, errors, and saturation, then add the dependency and queue signals needed to explain them.
- Use one consistent resource identity across logs, metrics, and traces: service, environment, version, deployment, region, and workload identity.
- Prefer OpenTelemetry instrumentation and a Collector when services need retry, batching, enrichment, filtering, or fan-out to backends. Keep the application independent of any one backend.
- Correlate deploys, incidents, traces, logs, and alerts with stable identifiers without recording secrets, raw credentials, or unnecessary personal data.

## Keep Telemetry Operable
- Define attribute allowlists and cardinality budgets before adding user IDs, URLs, request bodies, or arbitrary labels to metrics.
- Sample with a stated purpose. Preserve error and slow-request evidence; make dropped or sampled traces observable.
- Treat the Collector as production software: set resource limits, backpressure, retry and queue behavior, TLS, authentication, configuration review, and its own health signals.
- Route alerts to a named owner with a runbook and a user-impact hypothesis. Avoid alerts that only report an internal threshold without an action.

## Implementation Patterns
- Collector pipeline order that holds up in production: `memory_limiter` first, then enrichment/filter processors, then `batch` last before exporters; set `sending_queue` and `retry_on_failure` on exporters so backend outages degrade instead of dropping silently.
- Stamp resource identity once (service.name, service.version, deployment.environment) via resource detection or the SDK, not per-signal attributes that drift apart.
- Alert rules pair a symptom with an action: burn-rate alerts on SLOs for paging, cause-based alerts as tickets. Every page names an owner and links a runbook; an alert nobody can act on gets deleted, not snoozed.
- Dashboards mirror the diagnosis path: user impact on top, then the dependency and saturation panels that explain it, with deploy markers on every time series.
- Keep metric label sets closed: enumerate allowed values, drop or hash the rest at the Collector, and reject any label whose value space is user-controlled.

## Verify With
- `otelcol validate --config <file>` (or the distro's `--dry-run`) before shipping Collector config.
- `promtool check rules` / `promtool test rules` for alert and recording rules; `amtool check-config` for routing.
- Send one traced request through the full path and confirm the trace, its logs, and the RED metrics all carry the same resource identity.
- Kill an exporter target in staging and confirm backpressure, queue, and self-telemetry behave as designed.

## Diagnose Safely
- Start an incident with impact, scope, time window, deployment change, and dependency state. Link from an alert to the dashboard, trace, logs, and rollback procedure needed for first response.
- Use logs to explain a trace or metric, not as an unbounded data dump. Keep queryable event names and structured fields stable.
- Test telemetry during a representative failure or release rehearsal. A dashboard that was never used under pressure is unverified infrastructure.
