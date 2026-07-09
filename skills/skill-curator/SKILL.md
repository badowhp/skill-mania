---
name: skill-curator
description: "Find, compare, vet, and recommend agent skills, plugins, MCP servers, and marketplace packages. Use for top-skill reviews, plugin selection, install/adapt/reject decisions, skill quality audits, trust/licensing checks, and comparisons against external skill repositories. Prefer skill-creator for authoring one skill and security-engineer when exploitability is the main question."
---
# Skill Curator
Choose agent extensions deliberately: useful capability, clear instructions, acceptable trust, and no unnecessary overlap.
## Core Rules
1. Browse or inspect current sources when the user asks for latest, top, marketplace, plugin, GitHub, or external comparisons.
2. Prefer primary sources: repository files, marketplace pages, manifests, release notes, docs, and licenses.
3. Inspect instructions before recommending install or adoption. Do not judge by stars or descriptions alone.
4. Separate decisions: install as-is, adapt locally, borrow a pattern, reject, or defer.
5. Check trust boundaries: tools, network, shell access, secrets, writable paths, update path, and package provenance.
6. Preserve canonical local skill rules. Do not duplicate content across packaged copies unless the repo requires a sync step.
7. Recommend only skills that add real coverage or materially improve existing coverage.
## Workflow
1. Classify the request:
   - top skills or plugin discovery
   - compare local skills against external repositories
   - audit a skill for quality and gaps
   - decide whether to install, copy, adapt, or reject a plugin
   - improve a skill catalog or marketplace metadata
2. Gather evidence:
   - local skill names, descriptions, references, evals, scripts, and metadata
   - external README, `SKILL.md`, manifest, license, tool permissions, release history, and issue signals
   - overlap with existing local skills
3. Load the matching files from the Reference Map.
4. Score candidates by usefulness, specificity, instruction quality, verification support, maintenance, licensing, and risk.
5. Produce a recommendation that names what to add, what to improve, and what to reject.
## Company Context
When repo work touches skill inventory, plugin manifests, marketplace metadata, distribution packages, or durable agent behavior, read root `company.md` if present. Follow its ownership, packaging, licensing, canonical-source, and release guidance unless higher-priority instructions conflict.
## Reference Map
Load [references/external-skill-review.md](references/external-skill-review.md) for ranking, comparing, and adapting skills from GitHub, marketplaces, or public lists.

Load [references/plugin-risk.md](references/plugin-risk.md) for plugin manifests, MCP servers, tool permissions, install risk, licensing, updates, and trust boundaries.
## Quality Standards
- A good skill has a narrow trigger, clear exclusions, concise workflow, reference map, output expectations, and realistic evals.
- References should deepen a workflow, not hide required core behavior.
- Scripts should automate deterministic work, not replace judgment.
- Metadata should help selection without claiming more than the skill does.
- Near-miss evals matter. They prevent over-triggering and skill overlap.
- Reject generic "be better" skills unless they contain concrete repeatable behavior.
## Recommendation Shape
For each candidate, include:

1. decision: add, adapt, borrow, reject, or monitor
2. why it matters
3. overlap with current skills
4. trust/licensing or maintenance risk
5. exact local change if adopted
## Tool Output
Use RTK when available for noisy, non-destructive inventory, repository, test, scanner, or package-metadata output. Treat filtered output as triage and inspect raw output before making an exact trust, compatibility, or release recommendation.
## Honest Opinion
Use `honest opinion:` when it adds decision value: reviews, audits, recommendations, plans, tradeoffs, or implementation close-outs with a material risk or gap. Be brutally honest and evidence-based. Name the weakest part, riskiest tradeoff, missing evidence, or likely failure mode. Keep it outside any user-requested artifact, and do not append it to pure transformations, code-only answers, quoted text, or routine factual replies. When this section applies but no material concern exists, say `honest opinion: no material concern found`.
## Output Shape
For a skill or plugin review:

1. verdict
2. top additions worth making
3. candidate-by-candidate review
4. rejected or deferred items
5. implementation checklist
6. trust, license, or verification gaps
