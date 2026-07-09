# Context File Audit

Use this for repo instruction files and cross-agent guidance.

## Common Files
- `AGENTS.md`: durable repo rules, commands, gotchas, ownership, and release paths.
- `CLAUDE.md`: Claude-specific behavior that cannot live in portable skills.
- `company.md`: stable business, product, voice, brand, compliance, analytics, or audience facts.
- `.github/copilot-instructions.md`: Copilot-specific repo guidance.
- `.cursor/rules/`: Cursor-specific scoped rules.
- skill `SKILL.md`: portable workflow instructions.

## Audit Checklist
- Is the rule still true?
- Is it durable, or was it only for a one-off task?
- Does it belong in this file, or in a skill/reference/plugin manifest?
- Is the same rule duplicated elsewhere with different wording?
- Does it conflict with another tool surface?
- Does it mention a machine-specific path, private name, credential, or temporary branch?
- Does it tell the agent what to do in observable terms?
- Can a command or validation step prove the context still works?

## Cleanup Defaults
- Delete stale comments instead of explaining why they are stale.
- Consolidate duplicated commands into the canonical root instruction file.
- Move long operational or domain detail into skill references when it is not always needed.
- Keep tool-specific behavior in tool-specific metadata only when portability would be harmed.
- Preserve explicit repo commands and release gotchas.

## Conflict Handling
- Higher-priority system and developer instructions win.
- Repo root instructions beat nested instructions only for their scope.
- A specialized skill should own domain workflow detail.
- When two local files conflict, prefer the most canonical source and update or remove the weaker copy.
