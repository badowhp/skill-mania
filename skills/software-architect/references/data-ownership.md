# Data Ownership Reference

Use this for source-of-truth decisions, shared data, migrations, consistency, retention, and reporting.

## Table Of Contents

1. Ownership
2. Sharing patterns
3. Consistency
4. Retention and deletion
5. Review template

## Ownership

Every important entity needs one source of truth. State:

- owning service or module
- write authority
- read paths
- identifier semantics
- lifecycle states
- audit and retention requirements

## Sharing Patterns

Prefer:

- API reads for transactional needs
- events for downstream projections
- read models for search/reporting
- explicit exports for analytics

Avoid:

- multiple systems writing the same table
- hidden shared mutable state
- reporting queries that become production contracts
- duplicating sensitive data without retention controls

## Consistency

Define:

- strong vs eventual consistency needs
- acceptable stale window
- conflict behavior
- retry and replay behavior
- backfill process

## Retention And Deletion

Include:

- PII and sensitive-data classification
- deletion semantics
- legal hold behavior
- backups and restore implications
- downstream projection cleanup

## Review Template

```markdown
Entity:
Owner:
Writers:
Readers:
Consistency requirement:
Deletion/retention:
Migration or backfill:
Observability:
```
