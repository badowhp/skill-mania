# Plugin Metadata

Use this when editing package manifests, marketplace files, and skill interface metadata.

## Codex Skill Metadata
- Keep shared `SKILL.md` frontmatter portable: `name` and `description` are the essential fields.
- Keep `agents/openai.yaml` for Codex-specific display metadata.
- Ensure `default_prompt` includes the exact `$skill-name` trigger when required by validation.
- Keep `short_description` concise and selection-oriented.

## Plugin Manifests
- Keep package name, version, repository, homepage, license, author, skills path, display name, category, capabilities, icon, and logo consistent.
- Do not claim capabilities that are not present in the packaged skill set.
- Default prompts should represent high-value use cases without forcing a global mode.
- Long descriptions should list coverage plainly and avoid marketing filler.

## Packaged Copies
- Treat `skills/` as canonical when the repo says so.
- Refresh packaged copies with the repo sync script instead of hand-editing generated distribution folders.
- Run both sync checks and skill validation after metadata or skill edits.

## Release Notes
- Mention user-visible skill additions, trigger changes, removed stale guidance, and validation commands.
- Preserve upstream attribution and notices for adapted skills.
