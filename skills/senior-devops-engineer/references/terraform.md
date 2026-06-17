# Terraform Reference

## Table Of Contents

1. Layout and state
2. Module standards
3. Safe change process
4. Imports, refactors, and drift
5. Quality controls
6. Review checklist

## Layout And State

- Prefer one state per environment and stack boundary. Do not let unrelated systems share a state file.
- For GCP, use a remote backend on GCS with versioning enabled on the state bucket.
- Protect the state bucket with least privilege, retention, and clear ownership.
- Prefer explicit environment directories or stacks over excessive workspace magic for materially different environments.
- Keep provider versions pinned and commit the lock file.
- Pass environment-specific values from clear input variables or composition layers, not hidden implicit behavior.

## Module Standards

- Keep modules focused on one responsibility boundary: network, database, service, DNS, IAM binding set, and similar.
- Expose a small, stable interface. Too many variables usually mean the abstraction is weak.
- Avoid embedding business logic in locals that no reviewer can reason about quickly.
- Prefer `for_each` with stable keys over `count` when object identity matters.
- Use `dynamic` blocks sparingly and only when they reduce duplication without hiding intent.
- Model outputs for downstream consumers deliberately. Outputs are part of the contract.
- Keep naming, labels, and tagging conventions consistent across modules.

## Safe Change Process

- Run `terraform fmt`, `terraform validate`, and a plan before review or apply.
- Review plan output for replacement operations, destructive drift, IAM changes, firewall changes, and data-layer changes.
- Treat `-target` as an exception for recovery or staged refactors, not normal workflow.
- Prefer small plans that can be reasoned about. If a plan is huge, reduce scope first.
- For production:
  - separate plan from apply
  - preserve the reviewed plan artifact when the delivery system supports it
  - make rollback and state implications explicit

## Imports, Refactors, And Drift

- Import existing resources before managing them rather than recreating them blindly.
- Use `moved` blocks for address changes so refactors are traceable and safer.
- Investigate drift instead of normalizing it away. Drift often signals process failure, console changes, or overlapping automation.
- Be careful with `ignore_changes`. Use it only for well-understood fields managed elsewhere.
- Do not silence provider churn with broad lifecycle rules unless the operational owner agrees on that contract.
- When replacing critical resources, check whether the provider or API supports in-place updates, blue/green duplication, or staged cutover.

## Quality Controls

- Prefer reusable CI checks: `fmt`, `validate`, linting, security scanning, and policy checks.
- Use `tflint`, `tfsec` or `checkov`, and provider-specific linters where they add signal.
- Generate docs if the repo already standardizes on it, but do not let generated docs replace real review.
- Keep secrets out of variables files committed to git. Use CI secret stores, Vault, or cloud-native secret systems.
- Avoid shelling out from Terraform unless there is no better integration point.
- Prefer dedicated modules or external orchestration over `null_resource` hacks.

## Review Checklist

- Is state isolated correctly for the blast radius of the change?
- Are provider versions pinned and lock files committed?
- Are module inputs and outputs clear and minimal?
- Does the plan contain hidden destroys, recreations, or permission escalations?
- Are imports, `moved` blocks, or lifecycle rules justified?
- Does CI catch formatting, validation, lint, and security issues?
- Is there a practical rollback story?
