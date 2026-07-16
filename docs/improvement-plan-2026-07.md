# Improvement Plan — July 2026

Scope: senior-devops-engineer quality during implementation, per-skill verification
pairing, token/caching posture, aligned with mid-2026 vendor and community guidance.

## 1. Diagnosis: why `senior-devops-engineer` underperforms during implementation

The skill is review-shaped, not implementation-shaped:

1. **Output Shape defines only two report formats** (recommendation, review). There is no
   defined shape for "implement the change" work, so the model drifts toward writing plans
   and advice instead of producing working files.
2. **All 8 positive evals are advisory** ("Review…", "Design…", "Troubleshoot… propose").
   Not one case requires producing IaC/pipeline/config that must pass a deterministic
   validator. The skill was never selected against implementation failure modes, so
   implementation weaknesses are invisible to the current gate.
3. **The Verification Loop is 3 abstract lines.** It names no commands. Compare: the
   review path gets a bundled Terraform-plan summarizer, but the implementation path gets
   no validation helpers at all.
4. **References are review-weighted and thin where implementation needs depth:**
   `kubernetes.md` 1.4KB, `github-actions.md` 1.6KB, `edge-caching.md` 1.6KB. They carry
   plan-level judgment but few concrete patterns, snippets, or validation commands.

### Fixes

- **F1. Add an Implementation Mode section** to SKILL.md: when the request is to build or
  change something (not review it), write the actual files, run the stack's deterministic
  validators, iterate until clean, and report evidence — with the advisory Output Shape
  reserved for reviews. Keep it short; details go into references.
- **F2. Add a `references/validation.md`** mapping each stack to its non-destructive
  validator chain, e.g.:
  - Terraform: `fmt -check` → `validate` → `plan -json` → `summarize-terraform-plan.py`
  - Ansible: `ansible-lint` → `--syntax-check` → `--check --diff`
  - Containers: `hadolint` → `docker build` → smoke `docker run`
  - GitHub Actions: `actionlint` → `zizmor` (security) → workflow dry conditions
  - Kubernetes: `kubeconform`/`kubectl apply --dry-run=server` → probe/rollout checks
- **F3. Deepen the thin references** (kubernetes, github-actions, edge-caching,
  observability) with implementation patterns and known failure modes, each section ending
  with "verify with" commands. Keep each file loadable independently.
- **F4. Add implementation-shaped evals with fixtures and deterministic verifiers:**
  - fix a broken multi-stage Dockerfile; assert `docker build` (or hadolint-clean patch)
  - write a release workflow from requirements; assert `actionlint` passes and
    permissions/OIDC/pinning assertions hold
  - modify a Terraform module fixture; assert `terraform validate` passes and the plan
    JSON contains no unintended destroys
  This also implements the "tool-execution tier with deterministic verifiers" already
  called for in `benchmark-improvement-plan.md`.

## 2. Verification pairing for every skill — without doubling the catalog

Do **not** add 18 mirror "test-X" skills. That would roughly double startup metadata,
multiply routing collisions (the routing matrix already guards 152 cases), and contradicts
both SkillsBench (focused bundles beat exhaustive ones) and Anthropic guidance (fewer,
sharper triggers). Instead use one shared verifier plus per-skill checklists loaded
progressively:

- **V1. Per-skill `references/verification.md`** (Level-3 file, ~1–2KB): the domain's
  deterministic checks first, then an evidence checklist for what cannot be automated.
  The producing skill's own Verification Loop links to it (self-check on completion).
- **V2. One shared `implementation-verifier` skill** (~2KB body): given "verify what was
  just implemented", it identifies the producing skill, loads only that skill's
  `verification.md`, runs the deterministic floor, and reports pass/fail with evidence.
  Token cost: one description at startup + one small reference per use.
- **V3. Run verification in a fresh-context subagent** with a tight read-only tool list
  and small structured output. Fresh context avoids self-grading bias and keeps the main
  thread's prompt cache intact. Route to a cheaper model where the checks are
  deterministic; community cost data shows subagent-heavy flows can cost multiples of a
  single thread, so the verifier must stay narrow and read-heavy.
- **V4. Reuse existing reviewer pairs instead of duplicating them:**
  | Producer | Verifier |
  | --- | --- |
  | design-engineer | design-reviewer + visual-qa (exists) |
  | senior-developer | testing-engineer (exists) + verification.md |
  | senior-devops-engineer | implementation-verifier + validation.md (new) |
  | godot-game-creation-engineer | headless parse/run checks in verification.md |
  | security-engineer, software-architect, seo-geo | verification.md evidence checklists |
  | writing-assistant, austrian-law-helper | review-mode checklist (LLM/human floor) |
  | caveman, ponytail, commit, skill-curator, agent-context-maintainer | existing deterministic gates suffice |

## 3. Token usage and caching

Measured (report-skill-budgets.py, 2026-07-14): startup metadata for all 18 skills is
~1.0–1.2K tokens — cheap and not the problem. Per-invocation SKILL.md bodies run
0.6K–3.6K tokens; full reference trees up to ~8.8K (devops) if over-loaded.

- **T1. Enforce budgets in CI:** SKILL.md body ≤ ~2K tokens target (writing-assistant at
  ~3.0–3.6K and design-engineer at ~2.3–2.7K exceed it — move procedure into references);
  a task should load ≤ 2 references. Wire thresholds into `check-release-ready.sh` via
  `report-skill-budgets.py`.
- **T2. Protect the cache prefix.** Skill descriptions, CLAUDE.md, and MCP tool
  definitions sit in the cached left-to-right prefix; changing them mid-session
  invalidates the whole conversation cache. Keep descriptions short and stable, never put
  volatile content (dates, versions, counts) in frontmatter, and batch skill/plugin
  changes between sessions, not during them.
- **T3. SKILL.md bodies load mid-conversation** (not in the stable prefix), so body size
  is a per-invocation cost — progressive disclosure is the lever, and the devops skill's
  Reference Map is the right pattern. Apply it to writing-assistant and design-engineer.
- **T4. Report cache-read vs cache-write tokens** in benchmark artifacts, alongside the
  existing input/output/reasoning split, so overlay costs and reference-loading costs are
  visible separately.
- **T5. Verification via subagent (V3) is also a caching win:** exploratory/verification
  churn stays out of the main thread, preserving its prefix.

## 4. Alignment with mid-2026 guidance

- Anthropic (skill authoring + engineering post): eval-first development, three-level
  progressive disclosure, description quality drives triggering, split unwieldy bodies
  into referenced files, run→validate→fix loops. This plan applies all five.
- SkillsBench v1.1: matched with/without runs, deterministic verifiers, focused bundles
  outperform exhaustive ones — supports V1/V2 over per-skill mirror skills.
- Community signal (Reddit direct access is blocked for both the search crawler and the
  sandbox browser; taken from aggregating sources and the threads already cited in
  `benchmark-improvement-plan.md`): behavioral-constraint skills targeting real failure
  patterns (silent assumptions, over-engineering, orthogonal edits) show the strongest
  reported lift; too many overlapping skills degrades activation in some harnesses;
  narrow read-heavy verifier subagents with small structured outputs are the pattern that
  survives cost scrutiny. Treat as hypothesis, per repo policy.

## 5. Execution order

1. **Phase 1 — devops quality (F1–F4):** skill text, validation.md, deepened references,
   implementation evals with fixtures. Rerun paired evals per `skill-maintenance.md`.
2. **Phase 2 — verification architecture (V1–V4):** verification.md across skills, the
   shared implementation-verifier skill, routing-matrix entries and near-miss cases for
   it, deterministic-verifier tier in `run-skill-evals.py`.
3. **Phase 3 — token/caching (T1–T5):** CI budget thresholds, split oversized skills,
   cache-split metrics in benchmark reports.
4. **Phase 4 — regression cycle:** full validation (`sync-plugin-package.sh --check`,
   `validate-skills.py`, unit tests), then the Full Skill Regression Gate with repeated
   paired runs before release.
