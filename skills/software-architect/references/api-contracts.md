# API Contracts Reference
Use this for HTTP APIs, events, schemas, versioning, compatibility, idempotency, pagination, and error contracts.
## Contract Basics
Define:

- operation purpose
- request schema
- response schema
- authentication and authorization requirements
- error shape
- pagination and filtering rules
- idempotency behavior
- rate limits
- audit events
## Compatibility
Prefer additive changes. Avoid:

- renaming fields without migration
- changing enum semantics silently
- turning optional fields into required fields
- changing IDs, ordering, or pagination meaning
- removing fields before consumers migrate

For events, version schemas and preserve replay behavior.
## Reliability
Specify:

- timeout expectations
- retry safety
- idempotency keys for mutating operations
- eventual consistency windows
- duplicate event handling
- dead-letter or compensation path
## Review Checklist
- Can a consumer implement against the contract without reading internals?
- Are auth and tenancy rules explicit?
- Are errors stable and non-leaky?
- Are backward compatibility and migration paths clear?
- Are retries safe?
- Is observability part of the contract?
