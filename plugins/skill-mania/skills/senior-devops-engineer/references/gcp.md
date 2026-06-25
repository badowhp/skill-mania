# GCP Reference
## Table Of Contents
1. Environment model
2. Service selection
3. GKE
4. Cloud Run
5. Networking
6. IAM and secrets
7. Data, reliability, and DR
8. Observability and operations
9. Security and cost
10. Review checklist
## Environment Model
- Prefer separate GCP projects per environment and workload boundary over a single large shared project.
- Keep shared services explicit: DNS, container registry, centralized logging exports, CI identity, and network hubs.
- Use labels consistently for `env`, `service`, `owner`, `cost_center`, and `managed_by`.
- Prefer workload identity patterns over long-lived service account keys.
- For production, favor strong separation between build identities, deploy identities, and runtime identities.
## Service Selection
- Use Cloud Run for stateless HTTP services, moderate background jobs, fast delivery, and low ops burden.
- Use GKE when the platform needs Kubernetes-native scheduling, sidecars, custom networking policies, or broad multi-service platform control.
- Use Compute Engine or managed instance groups when the workload needs VM-level control, custom agents, stateful local behavior, or legacy PHP/Nginx stacks.
- Use Cloud SQL for relational workloads unless scale, sharding, or engine constraints require another managed database.
- Use Memorystore for Redis-backed cache, session, or queue needs when an application should not self-manage Redis.
- Prefer managed load balancing, Cloud DNS, Certificate Manager, Secret Manager, Cloud Armor, and Cloud NAT over self-hosted equivalents.
## GKE
- **Autopilot vs Standard:** prefer Autopilot for application-focused teams that do not need node-level control, custom daemonsets, or kernel tuning. Use Standard when you need node pools with specific machine types, GPUs, spot preemptibility, or fine-grained node configuration.
- **Namespace strategy:** use namespaces as a unit of access control and resource quotas, not just logical grouping. Keep prod and non-prod in separate clusters or projects where security requirements demand it.
- **Workload Identity:** bind each Kubernetes service account to a GCP service account using IAM. Annotate the Kubernetes service account with `iam.gke.io/gcp-service-account`. Grant the GCP service account `roles/iam.workloadIdentityUser` from the Kubernetes service account. Avoid mounting service account keys as secrets.
- **Ingress and traffic management:** prefer Gateway API (GKE Gateway controller) over Ingress for new workloads. Use HTTPS load balancing with Certificate Manager for TLS. Reserve Ingress for existing workloads or simpler setups.
- **Node pool design:** separate node pools by workload profile (CPU-intensive, memory-intensive, spot-eligible). Use node taints and tolerations to enforce placement. Set pod disruption budgets for customer-facing services.
- **Resource management:** set resource requests and limits on all containers. Use VPA in recommendation mode to calibrate requests. Use HPA based on custom metrics for workloads with variable traffic.
## Cloud Run
- **Traffic splitting:** deploy new revisions with 0% traffic, validate with smoke tests or tagged URL, then shift traffic incrementally. Use revision tags for per-revision access before promotion.
- **Cold starts:** set `min-instances` for latency-sensitive services. Balance against cost; use `max-instances` to cap scaling.
- **Cloud Run jobs vs services:** use services for HTTP-triggered or event-driven workloads. Use jobs for batch processing, migrations, and scheduled tasks that run to completion.
- **Database connectivity:** use the built-in Cloud SQL connector or the Cloud SQL Auth Proxy sidecar. Configure connection pooling at the application layer; Cloud Run scales instances and each instance holds its own pool.
- **VPC connector:** use Serverless VPC Access or Direct VPC Egress to reach private resources (Cloud SQL private IP, Memorystore, internal services). Direct VPC Egress is preferred for new projects as it avoids connector sizing limits.
- **Secret injection:** inject Secret Manager secrets as environment variables or as mounted volumes at startup. Do not pass secrets as build arguments or embed them in container images.
## Networking
- Design VPCs around isolation and operability, not abstract purity.
- Keep subnets regional and sized for growth.
- Minimize broad firewall rules. Prefer target service accounts or target tags with narrow sources and ports.
- Use private IP paths for database and internal service connectivity when possible.
- Keep egress explicit. Use Cloud NAT for controlled outbound access from private workloads.
- Front internet-facing services with a load balancer and explicit TLS, health checks, and logging.
- For mixed private and public services, keep internal and external load balancing concerns separate.
## IAM And Secrets
- Grant roles to groups or workload identities, not individuals, whenever possible.
- Avoid primitive roles. Start from least privilege and add narrowly scoped predefined roles or custom roles.
- Separate Terraform service account rights from runtime service account rights.
- Store application secrets in Secret Manager and inject them at deploy or runtime instead of baking them into images or repos.
- Rotate keys and credentials. Better: remove keys entirely in favor of identity federation or attached service accounts.
## Data, Reliability, And DR
- Treat backups, PITR, retention, and restore testing as first-class design requirements.
- For Cloud SQL:
  - enable automated backups
  - enable PITR where supported and justified
  - set maintenance windows deliberately
  - monitor CPU, memory, storage, connections, replication lag, and slow queries
- Define RPO and RTO before choosing HA or cross-region patterns.
- Use regional managed services for production where availability requirements justify the cost.
- Make database migrations explicitly part of release planning. Large schema changes often dominate risk more than app code.
## Observability And Operations
- Send structured application logs with request IDs, correlation IDs, user-safe context, and severity.
- Build dashboards around user-facing symptoms first: latency, error rate, saturation, queue delay, and dependency health.
- Alert on actionable symptoms, not every metric threshold.
- Use uptime checks, synthetic probes, and deployment annotations to reduce false correlation during incidents.
- Keep an inventory of critical dependencies: DNS, database, cache, queues, third-party APIs, and certificate paths.
## Security And Cost
- Use organization policies and guardrails where available for public IPs, service account key creation, allowed locations, and resource constraints.
- Apply Cloud Armor, rate limiting, and WAF controls to exposed services with meaningful attack surface.
- Use CMEK only when a real compliance or isolation requirement exists. Do not add it as decorative complexity.
- Review committed use discounts, autoscaling floors, oversized databases, idle disks, log volume, and cross-region egress for cost savings.
- Put budgets and anomaly alerts in place, but also fix the tagging and ownership model so costs can be attributed.
## Review Checklist
- Are projects, environments, and shared services separated cleanly?
- Is IAM least-privilege and free from unnecessary user-level grants?
- Is ingress and egress path explicit and observable?
- Are backups, restore tests, and DR assumptions documented?
- Are service choices matched to workload behavior rather than team habit?
- Are monitoring, alerting, and dashboards sufficient for first-response debugging?
- Are cost controls and ownership labels present?
