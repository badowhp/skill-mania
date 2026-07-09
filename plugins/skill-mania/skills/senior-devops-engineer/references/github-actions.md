# GitHub Actions

Use this for CI/CD workflows, release gates, artifact promotion, and repository automation in GitHub Actions.

## Workflow Review
- Separate build, test, package, release, and deploy responsibilities.
- Keep production deploys behind environments, approvals, branch/tag rules, and observable gates.
- Pin third-party actions by SHA for high-trust workflows; document exceptions.
- Set minimal `permissions:` at workflow and job level.
- Use OIDC federation for cloud deploys instead of long-lived cloud keys when supported.
- Avoid secrets in logs, artifacts, caches, annotations, and generated files.
- Cache dependencies by lockfile and platform, not broad mutable keys.
- Upload immutable build artifacts with provenance when they feed release jobs.

## Release Safety
- Build once, promote the same artifact through environments.
- Make rollback explicit: previous artifact, previous image tag, previous release, or infrastructure rollback.
- Capture deployment metadata: commit SHA, artifact digest, environment, actor, and timestamp.
- Add concurrency groups for deploy jobs to avoid overlapping releases.
- Add smoke tests and post-deploy checks that fail the release visibly.

## Common Risks
- Pull request workflows from forks with secret access.
- `pull_request_target` running untrusted code.
- Broad `GITHUB_TOKEN` permissions.
- Mutable tags for actions or container images.
- Deploy jobs that rebuild instead of promoting tested artifacts.
- Caches or artifacts containing `.env`, credentials, SSH keys, or package tokens.
