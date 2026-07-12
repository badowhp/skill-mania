# Branch evidence

- Branch is two commits ahead of `main`.
- Invoice downloads now scope the lookup by tenant before creating a signed URL.
- A negative test proves a user from tenant B cannot download tenant A's invoice.
- `pytest tests/invoices -q` passed: 18 tests.
- Playwright checkout coverage was not run because the browser dependency is unavailable.
- No database migration or new dependency was added.
