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

## Implementation Patterns
- A serving Deployment ships with: pinned image, `resources.requests`/`limits`, readiness and liveness probes with distinct semantics, `terminationGracePeriodSeconds` matched to shutdown behavior, labels that match the Service selector, and a PodDisruptionBudget when replicas > 1.
- Set `strategy.rollingUpdate` explicitly (`maxUnavailable: 0` for capacity-sensitive services) instead of relying on defaults.
- Readiness gates traffic; failing readiness must not restart the pod. Liveness restarts; point it at a check that only fails when a restart actually helps. Slow starters get a `startupProbe` so liveness thresholds stay tight.
- Mount configuration through ConfigMaps/Secrets with checksums or versioned names so a config change triggers a rollout instead of silently drifting.
- Give every workload its own ServiceAccount with `automountServiceAccountToken: false` unless the pod calls the API server.
- For migrations use a Job with `backoffLimit`, `activeDeadlineSeconds`, and idempotent commands; never run migrations in an init container of a scaled Deployment.

## Debugging
- Check rollout status, pod events, previous container logs, readiness failures, resource throttling, OOM kills, and recent deployments first: `kubectl rollout status deploy/<name>`, `kubectl describe pod`, `kubectl logs --previous`, `kubectl get events --sort-by=.lastTimestamp`.
- Readiness-but-not-ready pattern: diff the probe path/port against what the container actually serves after the config change; check endpoint membership with `kubectl get endpointslices`.
- Compare desired state to live state for drift with `kubectl diff -f`.
- Roll back with `kubectl rollout undo deploy/<name> --to-revision=<n>` or by re-applying the previous promoted image, not an ad hoc manifest edit.
- Preserve incident evidence before deleting pods, scaling to zero, or force-applying manifests.

## Verify With
- `kubeconform -strict <manifests>` or `kubectl apply --dry-run=client -f` for schema shape.
- `kubectl apply --dry-run=server -f` to catch admission, quota, and RBAC rejections.
- `kubectl diff -f` for the exact live delta before applying.
- After rollout: `kubectl rollout status`, endpoint membership, and one request through the Service or Ingress path, not just pod status.
