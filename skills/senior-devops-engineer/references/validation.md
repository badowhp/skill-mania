# Validation Chains

Run the matching chain after every meaningful edit while implementing. Every command here is non-destructive: it reads, lints, renders, or dry-runs, and never mutates shared state. Prefer the earliest failing check; do not run later steps against files that fail earlier ones.

## Terraform
1. `terraform fmt -check -recursive`
2. `terraform validate` (after `terraform init -backend=false` when no state access exists)
3. `terraform plan -out=tf.plan` then `terraform show -json tf.plan > plan.json`
4. `python3 scripts/summarize-terraform-plan.py plan.json` — treat replacements, deletes, IAM, firewall, public exposure, database, and secret changes as release risks to surface, not to hide.
5. Optional: `tflint` and a policy check (OPA/Sentinel) when the repo already uses them.

## Ansible
1. `ansible-lint` on changed roles and playbooks
2. `ansible-playbook --syntax-check <playbook>`
3. `ansible-playbook --check --diff <playbook>` against a non-production inventory; state clearly when check mode cannot model a handler or conditional path.
4. Confirm idempotence: a second real run must report zero changes before the work is done.

## Containers
1. `hadolint Dockerfile`
2. `docker build` (or `docker buildx build`) — a Dockerfile that does not build is not a deliverable.
3. Smoke-run the image with the production entrypoint and assert the expected port, healthcheck, or command output.
4. Confirm the image runs as a non-root user and pins base image digests or versioned tags.

## Kubernetes
1. `kubeconform -strict` (or `kubectl apply --dry-run=client -f`) for schema validity
2. `kubectl apply --dry-run=server -f` when a cluster is available — server-side catches admission and RBAC failures the client cannot.
3. `kubectl diff -f` to see the live delta before any real apply.
4. Assert probes, resources, disruption budgets, and rollout strategy exist for serving workloads.

## GitHub Actions
1. `actionlint` on every changed workflow
2. Check `permissions:` is set at workflow or job level and is minimal.
3. Check third-party actions are SHA-pinned and deploy jobs promote an existing artifact instead of rebuilding.
4. Optional: `zizmor` for security smells when installed.

## Web Runtime And Proxies
1. `nginx -t`, `apachectl configtest`, `haproxy -c -f`, or the runtime's own config check
2. `scripts/inspect-http-cache.py <url>` for cache and routing header evidence on one explicit URL.
3. Validate service units with `systemd-analyze verify <unit>` before enabling them.

## Evidence Rules
- Report each command actually run and its real result. Never claim a validator passed without running it.
- When a tool is unavailable in the environment, name it as an unverified gap in the close-out instead of skipping silently.
- RTK wrappers (`rtk <cmd>`) are fine for these read-only chains; preserve raw output for plan summaries and anything feeding a production decision.
- A green chain proves shape, not behavior: name the remaining behavioral risk (traffic, data, scale) that only staged rollout can verify.
