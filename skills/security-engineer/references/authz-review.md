# Authentication And Authorization Review

Use this when identity, sessions, roles, tenant boundaries, or privilege escalation are central.

## Authentication

Check:

- password, SSO, MFA, magic-link, or API-token flows
- account recovery and email-change flows
- token storage and expiration
- replay protection and one-time-token invalidation
- login throttling and credential stuffing controls

## Authorization

Authorization must be checked where the protected action happens, not only in UI or route grouping.

Look for:

- object-level checks on reads, updates, deletes, exports, and background jobs
- role checks on admin and billing actions
- privilege changes requiring explicit authorization
- service-to-service calls using scoped identities
- default-deny behavior when role or tenant is missing

## Tenant And Object Boundaries

Test:

- low-privilege user reads another user's object by ID
- user changes tenant, org, project, account, or workspace ID
- background job processes a forged object ID
- export endpoint leaks filtered-out data
- admin-like endpoint is reachable through alternate route or API version

## Session Lifecycle

Check:

- session rotation after login and privilege elevation
- logout invalidation
- revocation after password, email, MFA, or role changes
- idle and absolute timeouts
- secure cookie flags

## Review Template

```markdown
Boundary:
Actor:
Protected action:
Object or tenant scope:
Existing check:
Bypass attempt:
Finding:
Fix:
Negative test:
```
