# Operations Reference

## Table Of Contents

1. Delivery and release engineering
2. Tooling defaults
3. Observability
4. Incident response
5. Backups and disaster recovery
6. Security posture
7. Cost and capacity
8. Review checklist

## Delivery And Release Engineering

- Prefer CI to produce immutable artifacts and CD to promote them through environments.
- Keep infrastructure delivery and application delivery coordinated but not entangled.
- Require plans, previews, or dry runs for infrastructure and config changes when tooling supports it.
- Make rollback a designed path, not an optimistic assumption.
- Prefer progressive rollout, canaries, or rolling batches for customer-facing changes.
- Gate releases on health checks, smoke tests, and critical dependency readiness.

## Tooling Defaults

- Prefer Docker for reproducible build artifacts even when runtime lands on VMs.
- Use Artifact Registry or another managed registry with retention, vulnerability scanning, and clear ownership.
- CI system selection:
  - **GitHub Actions:** default for GitHub-hosted repos. Strong ecosystem; native OIDC Workload Identity to GCP; low operational overhead.
  - **Cloud Build:** prefer when the workload is GCP-native and tight Workload Identity, Artifact Registry push, or Cloud Deploy integration is the core requirement.
  - **GitLab CI:** for repos on GitLab. Supports GCP OIDC similarly to GitHub Actions.
  - **Jenkins:** only when an existing managed cluster is already in place and migration cost is not justified by platform gains. Avoid introducing Jenkins into greenfield projects.
- Use Renovate or Dependabot to keep infrastructure, OS packages, PHP dependencies, and action versions current.
- Use Prometheus and Grafana or managed cloud monitoring for metrics, Loki or ELK for logs, and Sentry or equivalent for application error tracking when the stack justifies them.
- Use Vault or a cloud-native secret manager rather than distributing secrets through repo files or ad hoc shell history.
- Use systemd for long-running workers and scheduled timers on Linux VMs unless there is a strong reason to add another supervisor.

## Observability

- Instrument the golden signals first: latency, traffic, errors, and saturation.
- Correlate logs, metrics, traces, deployments, and incidents with shared identifiers.
- Build dashboards for service owners and first responders, not only platform engineers.
- Alert on user impact, sustained error budgets, and dependency degradation with enough context to act.
- Keep runbooks close to alerts and services.

## Incident Response

- Start with impact, scope, start time, and current mitigation.
- Freeze unrelated changes during severe incidents.
- Assign explicit roles when the team is large enough: incident lead, communications, operations, and subject matter experts.
- Record hypotheses and observations in time order.
- Prefer reversible mitigations first: rollback, fail open or fail closed by policy, scale out, disable noncritical features, or shift traffic.
- Produce a short RCA that covers trigger, contributing factors, detection gaps, and durable fixes.

## Backups And Disaster Recovery

- Define backup ownership, retention, encryption, and restore verification.
- Test restore paths on a schedule. A backup without a restore drill is an assumption.
- Separate backup corruption risk from production corruption risk where practical.
- Define RPO and RTO per service, not as a vague platform-wide statement.
- Keep DR plans specific about DNS, data replication, secret recovery, and external dependency assumptions.

## Security Posture

- Centralize secret handling and minimize credential sprawl.
- Patch base images, packages, runtimes, and exposed services on a predictable cadence.
- Scan infrastructure code, dependencies, images, and hosts, but prioritize the findings that are actually reachable and exploitable.
- Review external exposure, TLS posture, IAM grants, SSH access, CI credentials, and service account usage regularly.
- Make auditability part of the design: who changed what, when, and through which system.

## Cost And Capacity

- Measure utilization before rightsizing. Guessing creates new incidents.
- Track cost by service owner and environment.
- Review baseline capacity, autoscaling thresholds, and quota headroom before launches or migrations.
- Watch for hidden capacity limits: database connections, file descriptors, worker counts, CPU credit models, and rate limits.
- Treat cost spikes as signals of ownership, architecture, or observability issues, not only finance issues.

## Review Checklist

- Can the team deploy, observe, and roll back safely?
- Do alerts map to user impact and have runbooks?
- Are incident handling and RCA practices disciplined?
- Are restore tests and DR assumptions proven?
- Is security posture operationally realistic rather than checkbox-based?
- Are cost and quota risks visible before they become outages?
