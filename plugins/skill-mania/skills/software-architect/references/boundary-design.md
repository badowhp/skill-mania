# Boundary Design Reference

Use this for service, module, package, ownership, deployability, and failure-boundary decisions.

## Boundary Inputs

Consider:

- business capability
- data ownership
- team ownership
- deployment cadence
- scaling profile
- failure mode
- security boundary
- regulatory or audit requirement
- migration path

## Good Boundaries

Prefer boundaries that:

- own one coherent capability
- expose a small contract
- hide internal storage and implementation
- can fail without corrupting unrelated work
- match team ownership where possible
- are observable and deployable independently when independence is needed

## Bad Boundaries

Watch for:

- service split only by technical layer
- shared database writes across services
- duplicated business rules
- synchronous chains that create fragile availability coupling
- event streams with unclear ownership
- abstractions with one implementation and no independent lifecycle

## Boundary Matrix

```markdown
Candidate boundary:
Owns:
Does not own:
Data source of truth:
Public contract:
Caller dependencies:
Failure behavior:
Deployment owner:
Why this boundary:
Rejected alternative:
```
