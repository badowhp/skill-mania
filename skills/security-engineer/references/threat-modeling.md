# Threat Modeling Reference

Use this when the task needs assets, trust boundaries, abuse cases, or mitigation planning.

## Table Of Contents

1. Inputs
2. Model structure
3. Abuse cases
4. Mitigations
5. Output template

## Inputs

Collect only what changes the model:

- assets and sensitive data
- actors and privilege levels
- entry points and exposed interfaces
- trust boundaries and network boundaries
- data stores, queues, webhooks, and third-party integrations
- deployment and ownership constraints

If a diagram exists, use it. If not, build a short textual data-flow model.

## Model Structure

For each flow, identify:

- source actor or system
- destination component
- data classification
- authentication state
- authorization check
- validation and encoding boundaries
- logging and audit trail

## Abuse Cases

Prioritize realistic abuse:

- unauthenticated access to sensitive behavior
- low-privilege user crossing tenant or object boundaries
- forged callbacks, webhooks, or background jobs
- sensitive data exfiltration through logs, exports, or errors
- SSRF, path traversal, command execution, template injection, or unsafe upload paths
- credential theft or replay
- dependency or CI compromise reaching production

## Mitigations

Prefer controls that match the boundary:

- deny-by-default authorization
- object-level access checks
- request signing and replay protection
- input validation at ingress
- output encoding at the sink
- egress restrictions for SSRF-sensitive services
- least-privilege service identities
- audit logs for sensitive actions
- alerting on high-risk behavior

## Output Template

```markdown
Assets:
- ...

Trust boundaries:
- ...

Top threats:
1. Threat: ...
   Path: ...
   Current control: ...
   Gap: ...
   Mitigation: ...
   Validation: ...
```
