# Cloud, CI, And Secrets Reference
Use this for cloud posture, CI/CD identity, deploy credentials, secrets handling, containers, and supply-chain controls.
## Identity
- Prefer workload identity federation or short-lived credentials over static keys.
- Separate build, deploy, and runtime identities.
- Scope CI write permissions to the target repository, artifact registry, and deploy surface.
- Avoid primitive cloud roles and broad organization-level grants.
- Review who can modify workflows, build scripts, deployment manifests, and release tags.
## Secrets
Secrets must not appear in:

- source files
- test fixtures
- logs
- build arguments
- container image layers
- frontend bundles
- Terraform state unless unavoidable and protected

Use a secret manager, Vault, or CI secret store. Rotate exposed values and document blast radius.
## CI/CD
Check:

- pinned actions or trusted reusable workflows
- branch protection and review gates
- least-privilege tokens
- no secrets exposed to untrusted forked pull requests
- artifact provenance and promotion path
- deploy approval for production
- rollback path for failed deploys
## Containers
Check:

- non-root runtime
- pinned base images
- minimal production image
- vulnerability scan before promotion
- no secrets in image layers
- clear tag strategy and no `latest` in production
## Cloud Exposure
Review:

- public IPs, load balancers, buckets, databases, queues, and admin panels
- firewall sources and ports
- WAF/rate limiting for exposed services
- logging on ingress, admin, and sensitive data access
- egress controls for workloads that can reach metadata services or internal APIs
