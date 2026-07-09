# Kubernetes

Use this for Kubernetes workload review, rollout planning, debugging, and production hardening.

## Workloads
- Define requests and limits based on measured runtime behavior.
- Use readiness probes for traffic eligibility and liveness probes only for recoverable dead states.
- Keep startup probes separate when cold starts are slow.
- Set graceful termination, preStop hooks, and disruption budgets for serving workloads.
- Prefer rolling updates with explicit max unavailable/surge values that match capacity.
- Use jobs or migrations carefully; make idempotency and retry semantics explicit.

## Safety And Operations
- Scope namespaces, service accounts, RBAC, network policies, and secrets to least privilege.
- Avoid embedding secrets in manifests, images, logs, or ConfigMaps.
- Use immutable image digests for production when possible.
- Keep ingress, TLS, timeouts, body sizes, and health checks aligned with the app.
- Add metrics, logs, events, alerts, dashboards, and runbooks for critical workloads.

## Debugging
- Check rollout status, pod events, previous container logs, readiness failures, resource throttling, OOM kills, and recent deployments first.
- Compare desired state to live state for drift.
- Roll back with a known deployment revision or promoted image, not an ad hoc manifest edit.
- Preserve incident evidence before deleting pods, scaling to zero, or force-applying manifests.
