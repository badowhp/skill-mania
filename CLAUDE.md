# Claude Code Guidance

This repo is a skills marketplace and plugin source for Claude Code.

- Skills live in `skills/<name>/SKILL.md`.
- Packaged plugin skills live in `plugins/skill-mania/skills` and are synced from `skills/`.
- Plugin metadata lives in `plugins/skill-mania/.claude-plugin/plugin.json`.
- Marketplace metadata lives in `.claude-plugin/marketplace.json`.
- Test plugin loading with `claude --plugin-dir plugins/skill-mania`.
- Reload after plugin metadata changes with `/reload-plugins`.
- Keep skill frontmatter compatible with the Agent Skills standard unless a skill is intentionally Claude-only.
- Keep the strict project sandbox and destructive-command hook in `.claude/settings.json`; change the canonical hook implementation in `templates/agent-automation/guard-agent-command.py`.

Run validation after edits:

```bash
./scripts/sync-plugin-package.sh --check
python3 scripts/validate-skills.py skills plugins/skill-mania/skills
python3 -m unittest tests.test_agent_automation_templates -v
```
