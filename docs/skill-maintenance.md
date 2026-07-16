# Skill Maintenance

Use observable behavior, not instruction volume, to decide whether a skill is healthy.

## Quality States

| State | Required evidence | Action |
| --- | --- | --- |
| Production | Valid package, clear owner boundary, at least three positive and two near-miss evals, static gate passes | Ship, include in smoke monitoring, and require full evidence for material changes |
| Needs evidence | Static checks pass, but model result is missing, below the quality bar, or has no representative artifact | Keep visible, run a full comparison, and record the weak case |
| Overlapping | Another skill wins the same prompts and output assertions without a meaningful gap | Merge the useful instructions into the stronger owner and remove the duplicate |
| Unsafe or stale | Secret exposure, destructive default, invalid source, expired model route, or repeated regression | Hold release until fixed or remove the skill |

`no-measurable-lift` is not proof that a skill is useless. It means the sampled baseline already met the assertions. Add harder cases before expanding the prompt.

## Cadence

- Every change: run `./scripts/check-release-ready.sh`.
- Weekly: let `.github/workflows/skill-evals.yml` rotate one positive case through every skill and retain the artifact.
- Before a material skill release: run **Full Skill Regression Gate** against the latest tagged skill. Use a no-skill comparison separately when testing whether a new skill adds value.
- By `evals/model-matrix.json.review_after`: verify official model guidance, update routes only when warranted, and compare the current reasoning effort with one level lower.
- Quarterly: inspect routing collisions, repeated `no-measurable-lift` results, external ecosystem changes, licenses, and skills with no recent realistic case.

## Change Test

Add or enlarge a skill only when all answers are yes:

1. Does it own a workflow that no existing description owns clearly?
2. Are there at least three realistic tasks and two plausible near misses?
3. Does the instruction encode non-obvious procedure, a deterministic helper, or a real safety boundary?
4. Can assertions observe the intended improvement?
5. Is the token and maintenance cost justified by the comparison?

Otherwise improve the current owner. Generic debugging remains in `senior-developer`, production diagnosis in `senior-devops-engineer`, and failure-isolation strategy in `testing-engineer`; pressure-test those boundaries instead of adding another broad debugger.

## Token And Cache Posture

Skill text is paid for in two different places; treat them separately.

- Startup metadata (every skill's name and description) loads into every session and sits in
  the cached prompt prefix. Keep descriptions short, stable, and free of volatile content
  (dates, counts, versions). Changing installed skills, plugins, or MCP tools mid-session
  invalidates the conversation's cache prefix; batch such changes between sessions.
- SKILL.md bodies load per invocation, mid-conversation. Body size is the recurring cost, so
  keep procedure in `references/` and let the body route to it (progressive disclosure).
  `scripts/report-skill-budgets.py --check` enforces the budgets in the release gate.
- A task should normally load at most two references. If a skill routinely needs more, its
  reference boundaries are wrong; restructure the files around the actual tasks.
- Run verification passes (implementation-verifier, reviewers) in a fresh-context subagent
  where the harness supports it: churn stays out of the main thread and its cache prefix
  survives intact.
- When comparing eval runs, read `cached_input_tokens` and `cache_write_tokens` next to raw
  input tokens; an instruction change that looks cheap in totals can still be expensive when
  it breaks prefix reuse.

## Evidence Review

For each model artifact, inspect:

- per-skill pass rates and verdicts in `benchmark.json`
- raw baseline and `with_skill` responses for judge mistakes
- assertion evidence, not only pass counts
- routing lead and overlay mismatches
- each skill's trigger recall and near-miss specificity; do not rely only on the global routing score
- baseline tag/commit and current/baseline package hashes
- token and duration deltas after quality is acceptable, including cached-input and cache-write splits
- cases that could not exercise a referenced script, browser, external source, or real repository artifact

Do not weaken assertions to make a gate green. Fix the skill, fixture, runner, or routing boundary and rerun the same case.

## Release Decision

Ship only when deterministic checks and the final security review pass, every changed skill has representative evidence, no skill is below the quality bar or materially regressed, package copies are synchronized, and the manifest version is newer than the latest tag when release content changed. Model evidence is nondeterministic; retain the artifact and record judge disagreements rather than treating one score as permanent truth. Remove retired skills from canonical and packaged trees; keep history in protected release tags instead of a live archive that can drift back into distribution.
