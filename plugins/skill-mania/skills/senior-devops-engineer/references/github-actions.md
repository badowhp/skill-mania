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

## Implementation Patterns
- Start every new workflow with `permissions: contents: read` at the top level and widen per job only for what that job provably needs (`id-token: write` for OIDC, `packages: write` for registry pushes).
- Deploy jobs declare `environment:` (gets approvals and scoped secrets) and `concurrency:` with a per-environment group and `cancel-in-progress: false` so releases queue instead of interleaving.
- Build job uploads the artifact or pushes an image by digest; release jobs consume that exact digest via job outputs — never re-run the build in the deploy job.
- OIDC to cloud: one federated identity per repo/environment pair, audience-restricted, mapped to a deploy-only role; long-lived cloud keys in repository secrets are a migration debt to name.
- Extract repeated pipelines into a reusable workflow (`workflow_call`) with typed inputs rather than copy-pasting jobs across repos.
- Cache keys: `hashFiles('**/lockfile')` plus runner OS; `restore-keys` only when a stale cache is safe.
- Anything interpolated from user-controlled context (`github.event.*` titles, branches, bodies) goes through `env:` indirection, never directly into `run:` scripts.

## Common Risks
- Pull request workflows from forks with secret access.
- `pull_request_target` running untrusted code.
- Broad `GITHUB_TOKEN` permissions.
- Mutable tags for actions or container images.
- Deploy jobs that rebuild instead of promoting tested artifacts.
- Caches or artifacts containing `.env`, credentials, SSH keys, or package tokens.
- Script injection through unquoted event context in `run:` steps.

## Verify With
- `actionlint` on every changed workflow file; it catches expression, shell, and permission mistakes statically.
- Grep the diff for `permissions:` at workflow and job level, unpinned `uses:` (tag instead of SHA), and secrets echoed into logs.
- A dry release through a non-production environment gate before trusting the production path.
- `zizmor` for security smells when installed.
