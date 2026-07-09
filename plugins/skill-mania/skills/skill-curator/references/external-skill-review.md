# External Skill Review

Use this when reviewing public skills, marketplace packages, or repository examples.

## Evidence To Inspect
- `SKILL.md` or equivalent instruction file
- README and examples
- referenced files under `references/`, `scripts/`, `assets/`, or templates
- manifest, marketplace metadata, and compatibility claims
- license and attribution requirements
- evals, tests, fixtures, or examples that prove trigger behavior
- recent commits, releases, issues, and maintainer signals when current status matters

## Scoring
- Capability fit: does it cover a workflow local skills do not cover?
- Specificity: does it contain concrete decision rules, not generic advice?
- Trigger precision: does it say when to use and when not to use it?
- Portability: can it work across Codex, Claude Code, Copilot, and local repos?
- Progressive disclosure: is core workflow in `SKILL.md` and depth in references?
- Verification: are evals, examples, or scripts present and realistic?
- Maintenance: is it stale, abandoned, or tied to a brittle external service?
- Overlap: would it confuse selection against existing skills?

## Adoption Decisions
- Install as-is when the skill is trusted, licensed, maintained, and directly useful.
- Adapt locally when the idea is strong but instructions need local conventions, evals, or metadata.
- Borrow a pattern when the skill overlaps but has one valuable reference, check, or output shape.
- Reject when the skill is vague, unsafe, unlicensed, redundant, too broad, or tool-risky.
- Monitor when the category is promising but the current implementation is not ready.

## Review Notes
- Do not treat popularity as quality.
- Do not import broad mode-switching prompts that weaken local discipline.
- Check for hidden machine-specific paths, secret-handling mistakes, and destructive commands.
- Verify that package instructions do not contradict repo canonical-source rules.
