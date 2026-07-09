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

## Diagnose Safely
- Start an incident with impact, scope, time window, deployment change, and dependency state. Link from an alert to the dashboard, trace, logs, and rollback procedure needed for first response.
- Use logs to explain a trace or metric, not as an unbounded data dump. Keep queryable event names and structured fields stable.
- Test telemetry during a representative failure or release rehearsal. A dashboard that was never used under pressure is unverified infrastructure.
