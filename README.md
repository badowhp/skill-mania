<p align="center">
  <img src="assets/readme-header.svg" alt="Skill Mania - portable Agent Skills for Codex and Claude Code" width="100%">
</p>

# Skill Mania

Skill Mania is a portable Agent Skills repository for Codex and Claude Code. It keeps reusable agent workflows in a tool-neutral `skills/` source tree, then packages the same production skills for local plugin and marketplace use.

## Included Skills

- `caveman` - terse, factual, low-prose response mode that preserves blockers and verification gaps.
- `design-engineer` - frontend, product design, UX, design-system, and vibe-coded UI audit guidance.
- `ponytail` - minimal YAGNI implementation mode based on Dietrich Gebert's Ponytail skill.
- `security-engineer` - application security, threat modeling, vulnerability triage, and hardening guidance.
- `seo-geo` - technical SEO, content discoverability, structured data, and generative search visibility guidance.
- `senior-developer` - scoped implementation, debugging, refactoring, review, and maintainability guidance.
- `senior-devops-engineer` - senior platform, DevOps, SRE, cloud infrastructure, delivery, operations, and production-readiness guidance.
- `software-architect` - system design, service boundaries, tradeoff analysis, and migration planning.
- `writing-assistant` - drafting, revision, editorial review, fiction craft, manuscript critique, publishing copy, and Kindle/KDP readiness.

Bundled Codex system skills are intentionally excluded. This repository only stores user-maintained portable skills.

## Docs And Templates

- `docs/litellm.md` - non-secret LiteLLM gateway setup, Codex provider placement, verification, and security review notes.
- `docs/openrouter.md` - direct OpenRouter setup, smoke tests, and review checklist.
- `templates/company.md` - copy to a repository root as `company.md` when skills should respect durable company, product, infrastructure, security, design, SEO, or content guidance.
- `templates/hip0-mania/` - private persona-review profile template. It is intentionally not shipped as a production skill because unfilled personal profiles are confusing in marketplace packages.

## Repository Layout

```text
.
├── assets/                         # Repository media used by documentation
├── docs/                           # Non-skill setup and operations notes
├── templates/                      # Optional templates such as company.md
├── skills/                         # Canonical skill source
│   └── <skill-name>/SKILL.md
├── plugins/skill-mania/            # Packaged plugin copy
│   ├── .codex-plugin/plugin.json   # Codex plugin manifest
│   ├── .claude-plugin/plugin.json  # Claude Code plugin manifest
│   └── skills/                     # Synced copy of canonical skills
├── .claude-plugin/marketplace.json # Claude Code marketplace catalog
├── .agents/plugins/marketplace.json# Codex local marketplace catalog
├── scripts/install-local.sh        # Install skills locally as symlinks or copies
├── scripts/sync-plugin-package.sh  # Refresh packaged plugin skills
└── scripts/validate-skills.py      # Dependency-free repository validation
```

## Local Installation

Install both Codex and Claude Code skills as symlinks:

```bash
./scripts/install-local.sh --all --link
```

Codex skills install to `~/.agents/skills` by default. For older Codex builds that still use `~/.codex/skills`, set the target explicitly:

```bash
CODEX_SKILLS_DIR="$HOME/.codex/skills" ./scripts/install-local.sh --codex --link
```

Claude Code skills install to `~/.claude/skills` by default. Override the target with `CLAUDE_SKILLS_DIR=/path/to/skills`.

Use `--copy` instead of `--link` when you need an independent snapshot rather than a live link to this repository.

## Plugin Usage

Test the Claude Code plugin package locally:

```bash
claude --plugin-dir plugins/skill-mania
```

Add the Claude Code marketplace from the parent directory:

```text
/plugin marketplace add ./skill-mania
/plugin install skill-mania@skill-mania
```

Add the Codex marketplace from the parent directory:

```bash
codex plugin marketplace add ./skill-mania
codex plugin add skill-mania@skill-mania-local
```

When running marketplace-add commands from inside this repository, use `.` instead of `./skill-mania`.

## Authoring Standards

- Keep each skill focused on one coherent workflow or domain role.
- Keep `skills/` limited to production-ready portable skills. Put personal profiles, local setup guides, and non-role documentation in `templates/` or `docs/`.
- Use `templates/company.md` when a team needs durable company, product, infrastructure, security, design, SEO, content, or agent-preference guidance that role skills should respect during repository work. Copy it to the target repository root as `company.md`; do not leave secrets or credentials in it.
- Keep shared `SKILL.md` frontmatter portable; this repository allows only `name` and `description` in shared skill frontmatter.
- Ensure the skill `name` matches its directory and uses lowercase letters, digits, and hyphens.
- Put trigger wording in `description`; keep it specific and front-loaded.
- Keep `SKILL.md` concise. Move detailed provider, framework, or domain material into `references/`.
- Link every reference file from `SKILL.md` with clear guidance on when to load it.
- Make routing available from each production skill with a local `references/role-selection.md` link when the skill can overlap with peers or overlays.
- Use the exact shared `## Honest Opinion` block for every production skill except `caveman`, which is an output-shape overlay and must preserve the lead role's risk line rather than create its own.
- Put deterministic or repetitive execution in `scripts/`.
- Put reusable templates, artifacts, examples, static files, and repo media in `assets/`.
- Put Codex UI metadata in `agents/openai.yaml`.
- Avoid secrets, credentials, destructive defaults, hidden network behavior, and machine-specific absolute paths.

## Validation

Run validation before committing:

```bash
./scripts/sync-plugin-package.sh --check
python3 scripts/validate-skills.py skills plugins/skill-mania/skills
```

Run the complete local release gate before publishing:

```bash
./scripts/check-release-ready.sh
```

The validator checks the repository's portable skill contract: `name` and `description` frontmatter only, naming, `SKILL.md` length, relative links, reference routing, `agents/openai.yaml`, eval manifests for production skills, the shared honest-opinion block, plugin manifests, marketplace metadata, and README skill-list drift. The release gate also checks package sync, unit tests, shell syntax, placeholder text in shipped skills, bundled helper smoke tests, design scanner behavior, and local installer copy mode.

After changing top-level `skills/`, refresh the packaged plugin copy:

```bash
./scripts/sync-plugin-package.sh
```

Before publishing a plugin release:

- Keep fillable personal-profile skills out of shipped `skills/` and starter prompts unless they are intentionally filled and production-ready.
- Run `./scripts/check-release-ready.sh`.
- Bump both Codex and Claude plugin manifest versions together.
- Record any manual skill-eval results that influenced description or behavior changes.

## References

- Agent Skills specification: https://agentskills.io/specification
- Agent Skills best practices: https://agentskills.io/skill-creation/best-practices
- Codex skills docs: https://developers.openai.com/codex/skills
- Codex plugin build docs: https://developers.openai.com/codex/plugins/build
- OpenAI plugins examples: https://github.com/openai/plugins
- Claude Code skills docs: https://code.claude.com/docs/en/skills
- Claude Code plugin marketplace docs: https://code.claude.com/docs/en/plugin-marketplaces
