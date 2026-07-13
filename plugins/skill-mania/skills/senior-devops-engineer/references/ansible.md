# Ansible Reference
## Structure
- Prefer roles with clear defaults, tasks, handlers, templates, and vars over one large playbook.
- Keep roles cohesive: base OS, reverse proxy, application runtime, deploy, monitoring agent, and hardening are separate concerns.
- Put environment or host-specific data in inventory, not buried in role logic.
- Use templates for files that must remain synchronized with variables and service restarts.
- Name tasks clearly enough that a failed run identifies the broken operation immediately.
## Idempotence And Safety
- Favor modules over raw shell commands.
- Use `changed_when` and `failed_when` only when necessary and with care.
- Keep handlers for real service reload and restart boundaries.
- Use `notify` plus handlers instead of restarting services on every run.
- Support check mode where practical, especially for config-only roles.
- Prefer `serial` for rolling changes to stateful or customer-facing fleets.
- Use `become` deliberately and scope privilege to the tasks that need it.
## Inventory And Secrets
- Keep inventory model simple: environments, groups by role, and a clear source of truth.
- Use Ansible Vault or an external secret backend for sensitive values. Never leave production secrets in plain group vars.
- Separate bootstrap access from long-term operational access.
- Keep SSH options, bastion behavior, and interpreter settings explicit in inventory or `ansible.cfg`.
## Variables And Templating
- Use documented Ansible variable access, filters, tests, and lookup plugins. Do not treat Python or Jinja implementation details such as `vars.get(...)` as an Ansible variable API.
- Use `value | default(...)` for optional values, `value is defined` for existence checks, role defaults for stable role inputs, and `lookup('ansible.builtin.vars', variable_name, default=...)` for a dynamic top-level variable name.
- Prefer the fully qualified collection name when a filter, lookup, test, or module name could be ambiguous, and keep expressions simple enough to validate with `ansible-lint` and the supported `ansible-core` versions.
## Deployment Patterns
- Render config, validate it if possible, then reload or restart the service only when the file changed.
- For application deploys:
  - fetch or unpack release artifact
  - install dependencies
  - update symlink or release pointer
  - run migrations only with clear gating
  - reload services
  - validate health
- Use tags for operational subsets such as `bootstrap`, `config`, `deploy`, `migrate`, and `rollback`.
- Keep rollback mechanics real. If a release symlink can move forward, it should also move back.
## Validation And Troubleshooting
- Run syntax checks and linting before large changes.
- Use `--check` and `--diff` for safe preview when roles support it.
- Inspect facts, rendered templates, service status, logs, and package versions when debugging.
- Watch for hidden non-idempotence from timestamps, unordered lists, or shell commands with side effects.
- If Ansible is acting as a deployment engine, be explicit about what belongs in CI versus what belongs in host configuration.
## Review Checklist
- Are roles cohesive and reusable?
- Is the playbook idempotent and readable in failure?
- Are secrets and inventory boundaries handled correctly?
- Are service reloads tied to actual config changes?
- Does templating use documented Ansible interfaces instead of Python-style calls such as `vars.get(...)`?
- Is deployment order safe for customer-facing systems?
- Are validation and rollback steps present?
