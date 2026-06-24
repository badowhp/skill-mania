# Role Selection Reference

Use this when a request could trigger multiple broad skills.

## Table Of Contents

1. Default routing
2. Overlap rules
3. Combination rules

## Default Routing

- Code-level implementation, bug fix, refactor, tests, or code review: use `senior-developer`.
- Cross-system design, service boundaries, API contracts, data ownership, or ADRs: use `software-architect`.
- Attacker behavior, trust boundaries, sensitive data, exploitability, or security controls: use `security-engineer`.
- Infrastructure, runtime operations, CI/CD, release, observability, incident, backup, or cost work: use `senior-devops-engineer`.
- UI/UX, visual design, frontend polish, responsive states, or vibe-coded design tells: use `design-engineer`.
- Manuscript, prose, docs, README text, publishing copy, KDP review, or AI-slop text checks: use `writing-assistant`.
- Explicit "be lazy", YAGNI, minimal solution, or Ponytail mode: use `ponytail` as a minimality overlay, but do not let it override explicit requirements or safety controls.

## Overlap Rules

- If the work changes code but the main risk is authz, tenant isolation, secrets, or exposure, security wins.
- If the work changes code but the main decision is service shape, ownership, or migration, architecture wins.
- If the work changes code but deployment, rollback, runtime, or observability dominates risk, DevOps wins.
- If the work touches frontend code but the user is asking about product feel, layout, states, or polish, design wins.
- If the work changes code but the main request is reader-facing wording, docs, release notes, or AI-slop cleanup, writing wins.
- If the work is mostly code but includes user-visible copy, senior-developer leads and applies a writing lens to the text.
- If the user asks for code review without a domain, senior-developer leads and calls out when a specialist review is needed.

## Combination Rules

When two roles are genuinely needed, keep one lead role and one lens:

- senior-developer + security lens: implementation with targeted security checks
- software-architect + DevOps lens: architecture with rollout and operability
- design-engineer + senior-developer lens: UI direction implemented in code
- senior-devops-engineer + security lens: runtime hardening and exposure review
- senior-developer + writing lens: code change with docs, messages, prompts, release notes, or AI-slop text cleanup
