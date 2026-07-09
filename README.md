<p align="center">
  <img src="assets/readme-header.svg" alt="Skill Mania" width="100%">
</p>

# Skill Mania

Skill Mania is a portable Agent Skills repository for Codex, Claude Code, and GitHub Copilot. It keeps reusable agent workflows in a tool-neutral `skills/` source tree, then packages the same production skills for plugin and marketplace use.

## Start Here

- Browse `skills/<name>/SKILL.md` to understand a workflow before installing it.
- Install every portable skill locally with `./scripts/install-local.sh --all --link`.
- Before publishing a change, run `./scripts/check-release-ready.sh`; the tag-driven GitHub workflow creates the release.

## Choose a Skill

| If you need to… | Start with… |
| --- | --- |
| Implement, debug, refactor, or review application behavior | `senior-developer` |
| Design tests, reproduce a regression, or stabilize CI | `testing-engineer` |
| Create UI, review UI, or collect browser evidence | `design-engineer`, `design-reviewer`, `visual-qa` |
| Design a game loop or implement a Godot feature | `gameplay-consultant`, `godot-game-creation-engineer` |
| Assess security, production operations, or system boundaries | `security-engineer`, `senior-devops-engineer`, `software-architect` |
| Improve search visibility, prose, or Austrian/Vienna correspondence | `seo-geo`, `writing-assistant`, `austrian-law-helper` |
| Maintain local skill metadata or vet an external package | `agent-context-maintainer`, `skill-curator` |
| Change output length or implementation scope | `caveman`, `ponytail` |

Use the first matching domain role. Add an overlay only when the user explicitly asks for terse output or a deliberately minimal implementation.

## Included Skills

### Build and test

- `senior-developer` - scoped application implementation, debugging, refactoring, and review.
- `testing-engineer` - test strategy, regression coverage, Playwright/UI tests, and flaky-test triage.
- `software-architect` - system boundaries, tradeoffs, contracts, and migration planning.

### Design and game work

- `design-engineer` - context-first UI design, planning, implementation, and review loops.
- `design-reviewer` - evidence-based UI/design critique and pass/fail gates.
- `visual-qa` - reproducible browser evidence for responsive UI and runtime findings.
- `gameplay-consultant` - player experience, mechanics, balance, accessibility, and playtest guidance.
- `godot-game-creation-engineer` - Godot scenes, scripts, input, physics, UI, debugging, and export work.

### Operate, secure, and discover

- `security-engineer` - threat modeling, vulnerability triage, and practical hardening.
- `senior-devops-engineer` - infrastructure, CI/CD, production operations, rollback, and reliability.
- `seo-geo` - technical SEO, discoverability, structured data, and answer-engine visibility.
- `skill-curator` - external skill/plugin discovery, comparison, and trust review.

### Write and govern

- `agent-context-maintainer` - local agent context, metadata, manifests, and packaged-copy hygiene.
- `austrian-law-helper` - Austrian/Vienna legal issue spotting and careful German correspondence.
- `writing-assistant` - drafting, revision, editorial review, publishing copy, and AI-slop checks.

### Overlays

- `caveman` - terse, factual output that preserves blockers and verification gaps.
- `ponytail` - minimal YAGNI implementation scope based on Dietrich Gebert's Ponytail skill.

Bundled Codex system skills are intentionally excluded. This repository only stores user-maintained portable skills.

## Trust and Portability

- `skills/` is the canonical source; `plugins/skill-mania/skills/` is a reproducible packaged copy.
- Production skills avoid credentials, destructive defaults, machine-specific paths, and hidden network behavior.
- Package manifests describe only the shipped skill set. Inspect external plugins before adoption with `skill-curator`.

## Docs And Templates

- `docs/litellm.md` - non-secret LiteLLM gateway setup, Codex provider placement, verification, and security review notes.
- `docs/openrouter.md` - direct OpenRouter setup, smoke tests, and review checklist.
- `docs/evaluation.md` - trigger testing, with-skill/baseline comparison, assertions, token/time capture, prompt-cache discipline, and release evidence.
- `docs/writing-assistant-baseline-evaluation/README.md` - reproducible old-versus-current benchmark procedure for material writing-assistant changes.
- `templates/company.md` - copy to a repository root as `company.md` when skills should respect durable company, product, infrastructure, security, design, SEO, or content guidance.
- `templates/agent-automation/` - opt-in Claude Code and GitHub Copilot hook templates with a narrowly scoped destructive-command guard.
- `templates/hip0-mania/` - private persona-review profile template. It is intentionally not shipped as a production skill because unfilled personal profiles are confusing in marketplace packages.

## Repository Layout

```text
.
├── assets/                         # Repository media used by documentation
├── docs/                           # Non-skill setup and operations notes
├── evals/                          # Cross-skill routing evaluation matrix
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
├── scripts/report-skill-budgets.py # Report and enforce context budgets
├── scripts/sync-plugin-package.sh  # Refresh packaged plugin skills
└── scripts/validate-skills.py      # Dependency-free repository validation
```

## Local Installation

Install shared Codex/GitHub Copilot skills and Claude Code skills as symlinks:

```bash
./scripts/install-local.sh --all --link
```

The shared Agent Skills install goes to `~/.agents/skills` by default, which current Codex and GitHub Copilot installations can both discover. `--agents` is the preferred explicit target; `--codex` remains an alias. For older Codex builds that still use `~/.codex/skills`, set the target explicitly:

```bash
CODEX_SKILLS_DIR="$HOME/.codex/skills" ./scripts/install-local.sh --codex --link
```

Use `AGENT_SKILLS_DIR=/path/to/skills` to override the shared target. GitHub Copilot users can also discover or install Agent Skills with `gh skill`.

Claude Code skills install to `~/.claude/skills` by default. Override the target with `CLAUDE_SKILLS_DIR=/path/to/skills`.

Use `--copy` instead of `--link` when you need an independent snapshot rather than a live link to this repository.

## Optional RTK Tooling

RTK is optional. When it is installed, use explicit wrappers for noisy, non-destructive commands such as `rtk git status`, `rtk test <cmd>`, and `rtk err <cmd>`.

Install the global token-saving hook with:

```bash
rtk init -g --auto-patch
```

Verify hook status with:

```bash
rtk init --show
```

Treat RTK output as triage. Rerun the raw command or inspect the RTK tee full-output log before making release, security, review, or debugging decisions that depend on exact output.

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
- Keep shared `SKILL.md` frontmatter portable. `name` and `description` are required; standard `license`, `compatibility`, and string `metadata` fields are supported when they add real value.
- Ensure the skill `name` matches its directory and uses lowercase letters, digits, and hyphens.
- Put trigger wording in `description`; keep it specific and front-loaded.
- Keep `SKILL.md` concise. Move detailed provider, framework, or domain material into `references/`.
- Link every reference file from `SKILL.md` with clear guidance on when to load it.
- Put routing boundaries in the frontmatter description. Do not spend runtime context on a shared routing reference.
- Use the exact shared `## Honest Opinion` block in every production skill. Apply it to reviews, recommendations, plans, tradeoffs, and implementation close-outs where it adds decision value; keep it outside requested artifacts and routine factual answers.
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

The validator checks the repository's portable skill contract: standard frontmatter, naming, `SKILL.md` length, relative links, reference routing, current `agents/openai.yaml` sections, assertion-bearing eval manifests, optional RTK triage guidance, the shared honest-opinion block, plugin manifests, marketplace metadata, and README skill-list drift. The release gate also validates the cross-skill routing matrix, then checks context budgets, synchronized versions, package sync, unit tests, shell syntax, placeholder text, helper smoke tests, and local installer copy mode.

Use `python3 scripts/report-skill-budgets.py` to inspect startup metadata and per-skill context estimates. These are static estimates; actual token and duration decisions should come from with-skill/baseline runs described in `docs/evaluation.md`.

After changing top-level `skills/`, refresh the packaged plugin copy:

```bash
./scripts/sync-plugin-package.sh
```

Before publishing a plugin release:

- Keep fillable personal-profile skills out of shipped `skills/` and starter prompts unless they are intentionally filled and production-ready.
- Run `./scripts/check-release-ready.sh`.
- Bump both Codex and Claude plugin manifest versions together.
- Run material behavior changes through the evaluation workflow and record the benchmark result in the pull request or release notes.
- Create a matching `v<version>` tag; the release workflow verifies the tag and publishes generated release notes.

## References

- Agent Skills specification: https://agentskills.io/specification
- Agent Skills best practices: https://agentskills.io/skill-creation/best-practices
- Codex skills docs: https://developers.openai.com/codex/skills
- Codex plugin build docs: https://developers.openai.com/codex/plugins/build
- OpenAI plugins examples: https://github.com/openai/plugins
- Claude Code skills docs: https://code.claude.com/docs/en/skills
- Claude Code plugin marketplace docs: https://code.claude.com/docs/en/plugin-marketplaces
- GitHub Copilot Agent Skills docs: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
