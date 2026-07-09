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

When paired run directories contain `grading.json` and `timing.json`, aggregate them with:

```bash
python3 scripts/summarize-eval-workspace.py path/to/iteration --output benchmark.json
```

The script recognizes `without_skill`, `old_skill`, or `baseline` beside each `with_skill` directory and reports pass-rate, median-token, and median-duration deltas.

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

## Available Evaluation Paths

- Claude Code: use the official `skill-creator` plugin evaluation flow for isolated runs, grading, benchmark output, blind comparison, and description tuning.
- Codex: forward-test in fresh threads or isolated workers with the skill path and raw task artifact; compare against the old snapshot without leaking the intended answer.
- Subjective skills: inspect rendered UI, prose, or artifacts directly and preserve human review notes alongside quantitative results.

Workspaces named `*-workspace/` are ignored by Git. Keep raw outputs long enough to review, then retain only durable benchmark conclusions and fixtures.
