# Contributing

Use this process for every new or changed skill.

## Create Or Update A Skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Use frontmatter with `name` and `description`.
3. Keep the body procedural and concise.
4. Move long provider, framework, or domain material into `references/`.
5. Add scripts only when deterministic behavior matters or agents keep rewriting the same logic.
6. Test any script you add.
7. Run the sync check and repository validator.

## Frontmatter Standard

Shared skills should stay portable:

```markdown
---
name: skill-name
description: What the skill does and when Codex or Claude Code should use it.
---
```

Use provider-specific metadata outside shared frontmatter when possible:

- Codex UI metadata: `skills/<skill-name>/agents/openai.yaml`
- Claude Code plugin behavior: `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json`
- Codex plugin behavior: `.codex-plugin/plugin.json` or `.agents/plugins/marketplace.json`

## Description Quality

Descriptions are the main trigger surface. Prefer:

- clear task nouns and verbs
- concrete trigger contexts
- boundaries for what the skill is not for
- the most important keywords early in the sentence

Avoid vague descriptions like "helps with infrastructure" or "writing helper".

## Production Skill Standards

- Keep shipped skills reusable for marketplace users. Move personal profiles to `templates/` and local setup notes to `docs/`.
- Link `references/role-selection.md` from each production skill that can overlap with another role or overlay.
- Use the repository-standard `## Honest Opinion` block for every production skill except `caveman`.
- Keep stack-specific guidance in references, not in long frontmatter descriptions.
- Treat `caveman` as an output-shape overlay and `ponytail` as an implementation-scope overlay.

## Review Checklist

- [ ] Skill name matches its directory.
- [ ] Description is specific and below 1024 characters.
- [ ] Description has clear trigger wording and near-miss boundaries.
- [ ] `SKILL.md` is below 500 lines.
- [ ] References are linked from `SKILL.md` with clear "when to read" guidance.
- [ ] Shared routing and honest-opinion conventions are present where required.
- [ ] Provider metadata and marketplace manifests validate successfully.
- [ ] Scripts are executable, deterministic, and tested.
- [ ] No secrets, tokens, credentials, private URLs, or machine-specific paths are committed.
- [ ] Destructive operations require an explicit plan and user confirmation.

Before committing, run:

```bash
./scripts/sync-plugin-package.sh --check
python3 scripts/validate-skills.py skills plugins/skill-mania/skills
```
