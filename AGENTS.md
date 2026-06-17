# Agent Guidance

This repository stores portable Agent Skills for Codex and Claude Code.

## Repo Rules

- Treat `skills/` as the canonical source. Do not duplicate skill contents under tool-specific directories.
- Treat `plugins/skill-mania/skills` as the packaged distribution copy. Refresh it with `./scripts/sync-plugin-package.sh`.
- Keep shared `SKILL.md` frontmatter portable: `name` and `description` are required.
- Put Codex-specific UI metadata in `agents/openai.yaml`.
- Put Claude Code plugin configuration in `.claude-plugin/`.
- Put Codex plugin configuration in `.codex-plugin/` and `.agents/plugins/`.
- Run `./scripts/sync-plugin-package.sh --check` and `python3 scripts/validate-skills.py skills plugins/skill-mania/skills` after editing skills.

## Skill Quality

- Keep each skill focused on one workflow or domain role.
- Prefer concise imperative instructions.
- Use progressive disclosure: keep core workflow in `SKILL.md`, detailed material in `references/`.
- Add scripts only for deterministic, repetitive, or fragile operations.
- Avoid machine-specific absolute paths inside skills.
- Never add secrets or credentials.
