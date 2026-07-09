# SaaS Tenancy

Use this for SaaS account, tenant, organization, workspace, plan, entitlement, and data-isolation decisions.

## Boundary Questions
- What is the tenant: customer, organization, workspace, environment, project, or account?
- Can one user belong to multiple tenants with different roles?
- Which data is tenant-owned, user-owned, global, or shared reference data?
- Are plan limits and entitlements enforced at API, worker, billing, and UI boundaries?
- What is the migration path if a tenant needs to split, merge, export, or delete data?
- What compliance or residency constraints affect partitioning?

## Isolation Options
- Shared database and shared schema with tenant keys: simplest, requires rigorous authz and indexing.
- Shared database with tenant schemas: stronger separation, more operational complexity.
- Database per tenant: high isolation, higher cost and migration burden.
- Hybrid: isolate large, regulated, or enterprise tenants while keeping default tenants shared.

## Review Checks
- Every sensitive query includes tenant context at the boundary or repository layer.
- Background jobs, search indexes, analytics, caches, and exports preserve tenant isolation.
- Admin and support access has audit logs and scoped elevation.
- Entitlement checks are centralized enough to avoid drift but close enough to enforce real behavior.
- Reporting and billing define source of truth and historical plan changes.
