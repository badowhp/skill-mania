# Web Application Security Reference
Use this for web app, API, browser, upload, request handling, and dangerous-sink review.
## Entry Points
Map:

- public routes and unauthenticated APIs
- authenticated routes by role
- admin routes
- webhook endpoints
- file upload and export paths
- search, filter, and report endpoints
- background job enqueue paths
## Dangerous Sinks
Treat these as high-risk until the path is proven safe:

- SQL or NoSQL query construction
- shell command execution
- template rendering with user-controlled input
- SSRF-capable HTTP clients
- deserialization
- file path joins and archive extraction
- HTML, Markdown, PDF, CSV, and email rendering
- redirect targets and callback URLs

For each sink, show the source, transformation, validation, and final call.
## Browser Controls
Check:

- cookies: `HttpOnly`, `Secure`, `SameSite`, domain, path, lifetime
- CSRF protection on state-changing browser requests
- CORS origin allowlist and credential behavior
- CSP where user content or third-party scripts exist
- security headers without conflicting injection at multiple layers
- output encoding for HTML, attributes, URLs, JavaScript, CSS, and CSV
## Upload And File Handling
Require:

- server-side type validation
- size limits
- randomized storage names
- path traversal defense
- malware scanning when risk justifies it
- no direct execution from upload storage
- separate public download authorization
## API Review Checklist
- Does every sensitive route authenticate identity?
- Does every object access authorize ownership, tenant, or role?
- Are validation errors safe and non-enumerating?
- Are rate limits present on authentication, search, export, and expensive operations?
- Are request IDs and audit events available for sensitive actions?
- Can a negative test prove the fix?
