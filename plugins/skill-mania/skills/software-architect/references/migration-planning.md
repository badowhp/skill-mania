# Migration Planning Reference

Use this for decomposition, modernization, strangler migrations, data moves, backfills, and incremental rollout.

## Strategy

Prefer incremental migration when the current system is live:

- wrap existing behavior before replacing it
- move one capability or flow at a time
- preserve old and new paths during verification
- avoid big-bang data cutovers unless downtime is acceptable
- make rollback a first-class path

## Rollout

Use:

- feature flags
- shadow reads
- dual reads before dual writes
- canary traffic
- per-tenant rollout
- read-only preview mode

## Data Movement

Plan:

- schema compatibility
- backfill order
- idempotent backfill jobs
- source-of-truth switch
- reconciliation queries
- cleanup of old data and old code

Dual writes are risky. If unavoidable, define ordering, retry, conflict, and reconciliation behavior.

## Validation And Rollback

Validate:

- business invariants
- counts and checksums
- error rates
- latency
- audit events
- user-visible behavior

Rollback must specify code, traffic, data, jobs, and queued messages.

## Migration Plan Template

```markdown
Goal:
Non-goals:
Current path:
Target path:
Phases:
Validation per phase:
Rollback per phase:
Data reconciliation:
Cleanup:
```
