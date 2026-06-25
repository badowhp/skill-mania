# Production Readiness Reference
Use this for architecture reviews that must be safe to operate, govern, and evolve after launch.
## Readiness Inputs
Collect the facts that change the decision:

- business capability and launch objective
- critical user journeys
- data classification and retention needs
- expected traffic, latency, availability, and recovery targets
- deployment model and ownership
- support hours, escalation path, and release calendar
- regulatory, audit, procurement, or vendor constraints
## Non-Functional Requirements
Define measurable targets before judging the design:

```markdown
Availability:
Latency:
Throughput:
Recovery time objective:
Recovery point objective:
Data retention:
Audit requirements:
Cost guardrail:
Accessibility or localization requirement:
```

If a target is unknown, mark it as a decision risk and propose a default that can be revisited.
## Operability
Require:

- dashboards for golden signals and business-critical flows
- alerts tied to user impact, not only resource saturation
- runbooks for known failure modes
- deployment, rollback, and feature-flag strategy
- ownership for on-call, triage, and maintenance
- backup and restore verification where data is durable
- observability for queue lag, background jobs, integrations, and auth failures
## Resilience
Check:

- timeout, retry, circuit-breaker, and backoff behavior
- idempotency for commands, jobs, webhooks, and payment-like flows
- graceful degradation when dependencies fail
- capacity limits and backpressure
- data consistency and reconciliation after partial failure
- failure isolation between tenants, jobs, and integrations
## Enterprise Delivery
Use this as the consulting lens:

- Is there a named business owner and technical owner?
- Are decision rights clear for product, architecture, security, operations, and support?
- Is adoption planned: migration, training, communications, and support handover?
- Are risk acceptances explicit, time-boxed, and owned?
- Is cost visible and tied to usage or value?
- Can the organization operate the design without the implementation team present?
## Readiness Decision
Use one of:

- `ship`: launch risk is understood and controls are in place
- `ship with conditions`: launch is acceptable only if named controls are completed or risks are accepted
- `hold`: launch risk is too high or key evidence is missing

Always state the blocking evidence, not just the opinion.
