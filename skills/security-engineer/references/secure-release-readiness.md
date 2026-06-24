# Secure Release Readiness Reference

Use this when security review affects production launch, risk acceptance, or operational sign-off.

## Table Of Contents

1. Release inputs
2. Security gates
3. Evidence
4. Exceptions
5. Privacy basics
6. Decision rubric

## Release Inputs

Capture:

- release scope and changed trust boundaries
- exposed routes, jobs, webhooks, and admin functions
- data classification and regulated data
- identities, roles, service accounts, tokens, and secrets
- dependencies, containers, CI jobs, and third-party integrations
- rollback, monitoring, and incident ownership

## Security Gates

Require evidence for:

- authentication and authorization on sensitive behavior
- object-level and tenant-level access controls
- secrets not present in source, logs, client bundles, artifacts, or images
- dependency and container scanning with triaged findings
- threat model for new external entry points or privilege changes
- security headers, cookie flags, CSRF, CORS, and upload controls where relevant
- audit logging for privileged or sensitive actions
- rate limits or abuse controls for authentication, export, search, and expensive paths

## Evidence

Prefer concrete evidence:

- test names, command output, or CI job links
- reviewed file and line references
- screenshots only for configuration that has no text export
- policy exceptions with owner and expiry
- monitoring queries or alert names

Do not treat "reviewed manually" as enough for a critical control unless the artifact cannot be automated.

## Exceptions

Risk acceptance must include:

```markdown
Risk:
Business reason:
Owner:
Expiry:
Compensating control:
Detection:
Follow-up ticket:
```

Open-ended exceptions are not production-ready.

## Privacy Basics

Check:

- data minimization
- retention and deletion behavior
- access logging for sensitive data
- consent or notice when user data use changes
- export, deletion, or audit obligations where the product promises them
- third-party data sharing and processor/subprocessor impact

## Decision Rubric

- `ship`: no critical or high unresolved risk, required evidence is present
- `ship with conditions`: risk is bounded, owner accepts it, and compensating controls are active
- `hold`: critical risk, unknown data exposure, missing authz evidence, unowned exception, or no rollback/incident owner
