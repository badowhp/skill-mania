# Secure Review Commands

Use deterministic commands as evidence, not as a replacement for exploitability analysis.

## Local Evidence
- Search for dangerous sinks, authz checks, secret handling, CORS, cookies, SSRF fetch paths, file writes, deserialization, shell execution, and upload handling.
- Inspect framework config, middleware order, route registration, environment loading, and CI/deploy files.
- Run existing security, lint, type, dependency, and test commands before inventing new tooling.
- Use scanner output as triage; confirm reachability and trust boundaries before calling a finding exploitable.

## Targeted Negative Tests
- Authorization: cross-user, cross-tenant, deleted, disabled, and role-downgraded access.
- SSRF: localhost, link-local, private RFC1918 ranges, redirects, DNS rebinding shape, and unsupported schemes.
- XSS: dangerous HTML sinks, markdown rendering, rich text, URL attributes, and stored content replay.
- Uploads: extension/MIME mismatch, oversized files, decompression, path traversal, public serving, and malware scanning handoff.
- Sessions: fixation, logout invalidation, rotation after privilege change, cookie attributes, and CSRF-sensitive actions.

## Evidence Standards
- Include the command, relevant output summary, and what it proves.
- Name residual risk when a scanner cannot run, dependencies cannot be reached, or a test environment is missing.
- Do not paste secrets, tokens, private keys, or sensitive personal data into review output.
- Prefer a focused negative test over broad assertions that only check for a status code.
