# Contributing

Use this process for every new or changed skill.

## Create Or Update A Skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Use frontmatter with `name` and `description`.
3. Keep the body procedural and concise.
4. Move long provider, framework, or domain material into `references/`.
5. Add scripts only when deterministic behavior matters or agents keep rewriting the same logic.
6. Test any script you add.
7. Add realistic positive and near-miss eval cases with observable assertions.
8. Run the sync check and repository validator.

## Frontmatter Standard

Shared skills should stay portable. `name` and `description` are required; use standard optional fields only when they carry useful portable information:

```markdown
---
name: skill-name
description: What the skill does and when an Agent Skills client should use it.
---
```

The current Agent Skills specification also defines optional `license`, `compatibility`, string `metadata`, and experimental `allowed-tools`. Use `allowed-tools` only when the restriction is intentional, and document which hosts honor it because support varies.

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
- Put routing boundaries in descriptions instead of duplicated routing references.
- Use the repository-standard `## Honest Opinion` block for every production skill. Keep it brutal and evidence-based, but only emit it when it adds decision value and never place it inside a requested artifact.
- Keep stack-specific guidance in references, not in long frontmatter descriptions.
- Treat `caveman` as an output-shape overlay and `ponytail` as an implementation-scope overlay.
- Compare material skill changes against the previous version or a without-skill baseline in fresh context. Capture assertions, pass rate, tokens, duration, and qualitative review.

## Review Checklist

- [ ] Skill name matches its directory.
- [ ] Description is specific and below 1024 characters.
- [ ] Description has clear trigger wording and near-miss boundaries.
- [ ] Any `allowed-tools` restriction is intentional and its host compatibility is documented.
- [ ] `SKILL.md` is below 500 lines.
- [ ] References are linked from `SKILL.md` with clear "when to read" guidance.
- [ ] Routing boundaries are clear in the description and the honest-opinion contract is present.
- [ ] At least three positive and two near-miss evals exist; positive cases contain observable assertions.
- [ ] Material behavior changes have with-skill/baseline evidence.
- [ ] Provider metadata and marketplace manifests validate successfully.
- [ ] Scripts are executable, deterministic, and tested.
- [ ] No secrets, tokens, credentials, private URLs, or machine-specific paths are committed.
- [ ] Destructive operations require an explicit plan and user confirmation.

Before committing, run:

```bash
./scripts/sync-plugin-package.sh --check
python3 scripts/validate-skills.py skills plugins/skill-mania/skills
python3 scripts/report-skill-budgets.py --check
```
