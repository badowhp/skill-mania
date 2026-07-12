# Security

Skills are operational instructions for coding agents. Treat them like executable automation.

## Rules

- Do not commit secrets, API keys, credentials, private tokens, or production hostnames that are not meant to be public.
- Do not add hidden network calls, background processes, credential collection, or destructive commands.
- Scripts must fail closed, print useful errors, and avoid modifying files outside the requested workspace unless the user explicitly asks.
- Any skill that can affect production must require a rollout plan, validation steps, and rollback path.
- Review third-party skills before importing them. Do not install marketplace skills blindly.
- Keep model-evaluation credentials in the `skill-evals` GitHub environment, restrict that environment to the default branch, and run secret-backed evaluator code only from that branch. Add required reviewers when scheduled approval is acceptable.
- Treat current and baseline skill text, eval prompts, fixtures, and model outputs as untrusted data. Do not execute baseline scripts; reject symlinked evaluator inputs and keep API responses out of public artifacts when tasks may contain sensitive data.
- Model-backed workflows send bundled current/tagged skill text and committed eval fixtures to the OpenAI API. Do not put confidential, customer, production, or personal data in those inputs; disable the workflows when provider processing is not approved.
- Protect `v*` release tags with a GitHub ruleset; release tags must point to commits reachable from the default branch.

Report security issues through GitHub private vulnerability reporting when it is enabled. Otherwise contact the repository owner privately. Do not open a public issue containing an exploit, credential, private hostname, or sensitive evidence.
