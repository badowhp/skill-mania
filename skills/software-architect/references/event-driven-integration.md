# Event-Driven Integration

Use event-driven design only when it buys decoupling, resilience, throughput, auditability, or integration flexibility that simpler synchronous APIs cannot provide.

## Design Questions
- What event means something business-relevant, not just that a database row changed?
- Who owns the event schema and compatibility contract?
- Which consumers need ordering, replay, deduplication, or exactly-once-like behavior?
- What is the source of truth after an event is emitted?
- What happens when a consumer is down, slow, duplicated, or partially successful?
- How will operators observe lag, dead letters, poison messages, and replay?

## Patterns
- Outbox: persist the state change and event intent atomically, then publish asynchronously.
- Inbox/deduplication: track processed event IDs for idempotent consumers.
- Saga/process manager: coordinate multi-step business workflows with compensating actions.
- Webhook delivery: sign payloads, retry with backoff, expose delivery logs, and support replay safely.
- Dead-letter queue: isolate poison messages with owner, alert, and replay path.

## Avoid
- Event sourcing because "events are modern" when ordinary audit logs are enough.
- Hidden distributed transactions across services.
- Consumers depending on private producer database shape.
- Unbounded retries without backpressure, alerting, or dead-letter handling.
