# Agent Guidance

Store portable Agent Skills for Codex, Claude Code, and GitHub Copilot.

Keep this file lean: only durable repo-specific rules, commands, gotchas, and release paths. Delete stale guidance quickly.

## Repo Rules

- Treat `skills/` as the canonical source. Do not duplicate skill contents under tool-specific directories.
- Treat `plugins/skill-mania/skills` as the packaged distribution copy. Refresh it with `./scripts/sync-plugin-package.sh`.
- Keep shared `SKILL.md` frontmatter portable: `name` and `description` are required.
- Keep the shared `## Honest Opinion` block in every production skill; use it only where it adds decision value and keep it outside requested artifacts.
- Put Codex-specific UI metadata in `agents/openai.yaml`.
- Put Claude Code plugin configuration in `.claude-plugin/`.
- Put Codex plugin configuration in `.codex-plugin/` and `.agents/plugins/`.
- Do not use emojis unless the user explicitly requests them.
- Run `./scripts/sync-plugin-package.sh --check` and `python3 scripts/validate-skills.py skills plugins/skill-mania/skills` after editing skills.

## Tooling

- If `rtk` is on PATH, prefer explicit RTK wrappers for verbose, non-destructive command output such as `rtk git status`, `rtk test <cmd>`, and `rtk err <cmd>`.
- Rerun the raw command or inspect the RTK tee full-output log when filtered output omits details needed for a fix, review, security decision, or release decision.
- Do not require RTK; fall back to normal commands when it is unavailable.

## Skill Quality

- Keep each skill focused on one workflow or domain role.
- Prefer concise imperative instructions.
- Use progressive disclosure: keep core workflow in `SKILL.md`, detailed material in `references/`.
- Add scripts only for deterministic, repetitive, or fragile operations.
- Add realistic positive and near-miss evals with observable assertions; benchmark material behavior changes against a baseline.
- Avoid machine-specific absolute paths inside skills.
- Never add secrets or credentials.
