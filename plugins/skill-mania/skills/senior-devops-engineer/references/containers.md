# Containers And Artifact Registry Reference

## Dockerfile Patterns For PHP Applications

- Use multi-stage builds: a build stage for Composer installs and asset compilation, a runtime stage with only production dependencies.
- Pin the base PHP image to a specific minor version and rebuild on a predictable cadence.
- Run the application as a non-root user. Set `USER` explicitly in the final stage.
- Keep the runtime image lean: no dev tools, no build cache, no test dependencies.
- Install OPcache in the image and configure it via environment variables or an entrypoint script.
- Use `.dockerignore` to exclude `.git`, `tests/`, local env files, and CI artifacts from the build context.
- Keep Nginx and PHP-FPM in separate containers when using orchestration. Use a sidecar or init container pattern.
- When both Nginx and PHP-FPM must run in a single container, use a process supervisor such as s6-overlay or supervisord and configure health checks that cover both processes.

## Artifact Registry Setup And IAM

- Create one Artifact Registry repository per technology type (Docker, npm, Maven) and per environment boundary if image promotion is explicit.
- Grant `roles/artifactregistry.writer` to CI service accounts. Grant `roles/artifactregistry.reader` to runtime service accounts and Compute Engine default service accounts.
- Prefer Workload Identity Federation for GitHub Actions and Cloud Build over long-lived service account keys.
- Enable vulnerability scanning on repositories that feed production deploys.
- Set image retention policies: keep the last N tagged releases; delete untagged digests on a schedule.
- Use Container Analysis or a third-party scanner in CI to block promotion of images with critical CVEs.

## Cloud Build Trigger Design

- Prefer Cloud Build triggers connected to GitHub or GitLab via the Cloud Build App or mirrored repos over polling or webhook-only setups.
- Use substitution variables for environment-specific values (project ID, image tag, region). Avoid hardcoding environment targets in `cloudbuild.yaml`.
- Build, test, scan, and push should be separate steps. Do not combine build and deploy in one step for non-development environments.
- Use a dedicated CI service account scoped to only the permissions needed for that pipeline (push to Artifact Registry, deploy to Cloud Run or GKE, etc.).
- Store build logs in GCS with a clear retention and ownership policy.
- For multi-environment promotion, consider Cloud Deploy for managed delivery pipelines to Cloud Run and GKE.

## Container-Based Deploy Patterns

### Compute Engine

- **Pull-on-deploy:** startup script or Ansible task pulls the latest tagged image and restarts the container. Simple; requires image accessibility from the VM at boot.
- **Baked image:** Cloud Build produces a VM image with the container pre-pulled. Faster boot; requires a disciplined image pipeline.
- For PHP/Nginx on VMs: prefer pull-on-deploy with a pinned image tag so rollback is a one-line tag change and service restart.

### Cloud Run

- Use image tags (not `latest`) for production deploys. Tag with Git SHA or semantic version.
- Use traffic splitting for canary releases: deploy a new revision at 0% traffic, run smoke tests, then shift traffic incrementally.
- Set `min-instances` to avoid cold starts for latency-sensitive services.
- Use Cloud Run jobs for batch, migration, or maintenance tasks that should not run as a persistent service.
- Connect to Cloud SQL via the built-in connector or Cloud SQL Auth Proxy sidecar. Do not expose the database directly.
- Inject secrets from Secret Manager as environment variables or mounted volumes, not as build-time `ARG` values.

### GKE

- Deploy via Helm charts or Kustomize overlays. Avoid raw `kubectl apply` in CI for anything beyond local development.
- Use Workload Identity to bind Kubernetes service accounts to GCP service accounts. Avoid node-level service account key files.
- Set liveness and readiness probes that reflect actual application health, not just port reachability.
- Configure `maxUnavailable` and `maxSurge` in rolling updates according to the workload's traffic sensitivity.

## Image Lifecycle Management

- Tag every production image with: Git SHA, semantic version if applicable, and environment label for promoted images.
- Never use `latest` in production deploys. Reserve `latest` for local development builds only.
- Promote images by re-tagging rather than rebuilding. The same image that passed staging should reach production unchanged.
- Clean up feature branch images on PR close. Keep release tags per a defined retention policy.

## Review Checklist

- Is the Dockerfile multi-stage with a lean production image?
- Is the base image pinned and on a rebuild cadence?
- Does CI scan images for vulnerabilities before promotion?
- Are Artifact Registry IAM grants scoped to CI writer and runtime reader?
- Is the deploy pattern explicit about rollback (image tag, traffic split, or restart)?
- Are secrets injected at runtime rather than baked into the image?
- Is `latest` absent from production deploys?
