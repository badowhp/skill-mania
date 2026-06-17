# Security

Skills are operational instructions for coding agents. Treat them like executable automation.

## Rules

- Do not commit secrets, API keys, credentials, private tokens, or production hostnames that are not meant to be public.
- Do not add hidden network calls, background processes, credential collection, or destructive commands.
- Scripts must fail closed, print useful errors, and avoid modifying files outside the requested workspace unless the user explicitly asks.
- Any skill that can affect production must require a rollout plan, validation steps, and rollback path.
- Review third-party skills before importing them. Do not install marketplace skills blindly.

Report security issues privately to the repository owner.

