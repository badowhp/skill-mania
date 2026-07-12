# AGENTS.md

## Repository Rules

- Treat `skills/` as canonical and refresh packaged copies with `./scripts/sync-plugin-package.sh`.
- Do not add credentials or machine-specific absolute paths.

## Validation

- Run `./scripts/sync-plugin-package.sh --check` after skill edits.
- Run `python3 scripts/validate-skills.py skills plugins/skill-mania/skills` before release.

## Release

- Tags matching `v*` publish releases after the release-readiness gate passes.

## Current Sprint Notes

- For task SM-184 only, keep the temporary `debug-evals/` directory until Maria reviews it on Friday.
- The July 8 migration is done; remember to delete `old-marketplace.json` after stand-up.
- Retry the one failed benchmark manually this afternoon.
