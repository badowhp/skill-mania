# Skill Evaluation Workflow

Use this workflow for material changes to triggering, instructions, scripts, or expected output. Static validation proves package shape; it does not prove that a skill improves agent behavior.

## Test Two Questions Separately

1. Triggering: does the agent select the skill for the right prompts and avoid near misses?
2. Output quality: when selected, does the skill produce a better result than the baseline at an acceptable token and time cost?

Do not infer output quality from trigger success.

## Eval Manifest

Keep at least three positive and two near-miss cases in `evals/evals.json`. Positive cases need observable assertions. Use `files` for committed fixtures when the task needs input artifacts.

For description tuning, expand to 10-20 realistic queries spanning:

- direct and indirect wording
- short and detailed requests
- overlapping peer skills
- explicit invocation
- plausible false positives
- requests that should combine a lead role with an overlay

## Cross-Skill Routing Matrix

Keep high-confusion prompts in `evals/routing-matrix.json`. The matrix gives every production domain skill at least one lead case, exercises each overlay through `overlay_skills`, and covers the repository's known routing collisions. Validate it locally and in the release gate:

```bash
python3 scripts/validate-routing-evals.py
```

The validator proves that every lead, near-miss, and overlay skill exists, that overlays are not modeled as domain owners, and that required overlap pairs remain covered. It does not prove model selection. Run the matrix in fresh contexts for every supported host/model, record the selected lead and overlay skills, then add ambiguous prompts to the relevant skill eval manifests.

## Comparison Run

Run each output case in fresh context:

- `with_skill`: current skill available and explicitly selected when testing output behavior
- `baseline`: no skill for a new skill, or an unchanged snapshot for a revision

Launch paired runs close together so model or environment drift affects both sides similarly. Do not reveal the expected winner, diagnosis, or intended fix to the evaluator.

Capture per run:

```json
{
  "total_tokens": 0,
  "duration_ms": 0
}
```

Grade each assertion with pass/fail and specific evidence. Use deterministic scripts for mechanical checks and human review for voice, visual quality, usefulness, or other subjective outcomes.

## Repository Model Runner

Validate the complete run plan without credentials or network calls:

```bash
python3 scripts/run-skill-evals.py --dry-run
```

The default smoke plan selects one positive case per skill, alternates paired generation order deterministically, produces a baseline and `with_skill` response, and grades both candidates in a separate blind order with the quality route. Routing is a second pair of checks: the throughput route assigns cross-skill lead/overlays and independently decides every selected skill's positive and near-miss trigger cases. The gate enforces global accuracy and each selected skill's cross-skill accuracy, positive recall, and negative specificity, so one completely broken skill cannot hide inside a good global average. Assertions and expected outputs are never sent to generators.

The evaluator is a `bundled-context` harness, not a tool-execution harness. It supplies the body of `SKILL.md` and safe UTF-8 files under `references/`, `scripts/`, and `assets/`; it records included/skipped paths, character counts, and SHA-256 digests. Symlinks, out-of-tree paths, oversized files, binary content, and oversized packages are rejected or skipped. The model cannot invoke those scripts or use shell, browser, filesystem, or network tools. Use this tier for instruction-following and routing evidence, then use deterministic helper tests and fresh-agent forward tests for operational behavior.

Every bundled instruction and committed fixture used by a model run is sent to the OpenAI API. Never use confidential repositories, customer data, production captures, credentials, or personal information as eval input unless the applicable provider processing and artifact retention are explicitly approved.

Run a local comparison after setting `OPENAI_API_KEY` in the environment:

```bash
python3 scripts/run-skill-evals.py \
  --skills senior-developer,testing-engineer \
  --max-cases-per-skill 0 \
  --output local-eval-workspace
```

Use `--baseline-skills-dir path/to/previous/skills` to compare a revision with an old snapshot. A skill absent from that snapshot automatically uses the no-skill baseline. Output directories must be empty so stale evidence cannot be mistaken for the current run.

For durable evidence, also pass `--baseline-label v0.3.0 --baseline-commit <sha>`. The runner stores those values with per-package content hashes so a later reviewer can identify exactly what was compared. `--routing-route`, `--maximum-model-calls`, `--maximum-api-requests`, and `--maximum-total-tokens` make route and spend boundaries explicit. The logical-call and HTTP-attempt caps are checked before and during the run, including retries. The token cap stops the run after the first completed response that would cross it, so actual usage can exceed the limit by at most that one returned API call; a response lost during transport cannot be counted locally.

The runner writes raw responses, assertion grades, token/timing records, `routing.json`, `benchmark.json`, and `summary.md`. Its per-skill verdicts mean:

- `measurable-lift`: the skill passed the quality floor and beat the baseline on sampled assertions.
- `no-measurable-lift`: the skill passed the floor without a positive delta; add harder cases before adding prose.
- `below-quality-bar`: the skill response missed too many required assertions.
- `regressed`: the skill underperformed the baseline beyond the configured tolerance.

The model gate fails for the last two states or a global/per-skill routing threshold failure. It does not fail only because token use or duration rose; cost is interpreted after quality. Every artifact reports generator, judge, router, reasoning effort, Git commit, baseline provenance, package hashes, call count, token use, and cumulative API duration.

When paired run directories contain `grading.json` and `timing.json`, aggregate them with:

```bash
python3 scripts/summarize-eval-workspace.py path/to/iteration --output benchmark.json
```

The script recognizes `without_skill`, `old_skill`, or `baseline` beside each `with_skill` directory and reports pass-rate, median-token, and median-duration deltas.

The weekly/manual **Model Skill Monitoring** workflow in `.github/workflows/skill-evals.yml` uploads its workspace for 30 days. Weekly smoke runs rotate case selection by ISO week. A one-case-per-skill smoke run is useful for drift detection but is not release evidence: with only a few assertions, an 80% floor effectively becomes all-or-nothing and one judge decision can flip the result.

Use `.github/workflows/skill-regression-gate.yml` for a material change. **Full Skill Regression Gate** has no model or scope inputs: it compares every positive case for every production skill with the latest immutable release tag using the reviewed balanced generator, quality judge, and throughput router. Review raw evidence for failures and adjudicate suspected judge noise before changing an assertion. The workflow is a manually initiated policy gate because automatically spending on every pull request would expose credentials and create uncontrolled cost; release notes or the pull request should link its retained artifact.

## Decision Record

Record in the pull request or release notes:

```markdown
Skill:
Baseline:
Cases:
Trigger precision/recall:
With-skill assertion pass rate:
Baseline assertion pass rate:
Median token delta:
Median duration delta:
Qualitative winner:
Known weak case:
Decision:
```

Do not merge a more expensive skill revision merely because it is longer or more comprehensive. Keep it when the quality gain is observable and worth the token/time cost.

## Token And Prompt-Cache Discipline

Keep skill descriptions focused, keep the core workflow in `SKILL.md`, and load references only when they match the task. The release gate enforces startup, `SKILL.md`, individual-reference, and per-skill total-reference budgets; inspect them with `python3 scripts/report-skill-budgets.py --check`.

For API-based agents, place stable instructions, tool definitions, and shared examples first; append task- or user-specific content last. OpenAI prompt caching requires an exact shared prefix and starts at 1,024 prompt tokens. Reuse a stable cache key only for requests with the same shared prefix, measure `cached_tokens`, and do not assume this API behavior applies to a Codex plugin or another client. See [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).

## Model Routing

Keep provider defaults in `evals/model-matrix.json`, not inside individual skills. The matrix records the official source, review date, expiry date, quality/balanced/throughput routes, reasoning defaults, and gate thresholds. `scripts/validate-model-matrix.py` deliberately fails after `review_after` so model selection cannot remain silently stale.

For GPT-5.6 migrations, preserve the current reasoning effort as the baseline and also compare one level lower on representative tasks. A stronger or more expensive model is not evidence that the skill improved; keep generator, judge, task, and baseline configuration in the artifact. See the [official latest-model guide](https://developers.openai.com/api/docs/guides/latest-model.md).

## Available Evaluation Paths

- Claude Code: use the official `skill-creator` plugin evaluation flow for isolated runs, grading, benchmark output, blind comparison, and description tuning.
- Codex: forward-test in fresh threads or isolated workers with the skill path and raw task artifact; compare against the old snapshot without leaking the intended answer.
- Tool-bearing skills: execute their committed helpers against fixtures and verify filesystem, Git, HTTP, or browser evidence directly. A prose-only model response cannot satisfy this tier.
- Subjective skills: inspect rendered UI, prose, or artifacts directly and preserve human review notes alongside quantitative results.

Workspaces named `*-workspace/` are ignored by Git. Keep raw outputs long enough to review, then retain only durable benchmark conclusions and fixtures.
