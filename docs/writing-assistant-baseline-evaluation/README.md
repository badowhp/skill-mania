# Writing Assistant Baseline Evaluation

Use this guide before releasing a material change to `writing-assistant`. It compares the current skill with the unchanged version from the commit before the change. The goal is evidence of better editorial behavior at an acceptable token and time cost, not a longer or more agreeable answer.

For the general policy and release-note template, read [the evaluation workflow](../evaluation.md).

## What To Compare

Use the unchanged skill as the baseline for a revision. Do not compare it with no skill; that is appropriate only when evaluating a brand-new skill.

For each case, hold constant:

- prompt and source text
- model, configuration, and available tools
- evaluator instructions
- grading assertions

Run the two versions in separate, fresh contexts. Do not reveal the intended winner, the new instructions, or the other response to the evaluator.

## Recommended Cases

Use the assertions in `skills/writing-assistant/evals/evals.json`. For the current editorial-boundary revision, run these five cases:

| Case | Behavior to prove |
| --- | --- |
| `source-boundary-review` | A copy edit identifies claims that require medical or source verification without inventing citations or claiming expert review. |
| `line-edit-only` | The response improves the prose without changing the requested structure or voice. |
| `technical-docs-edit` | Commands, warnings, and technical meaning remain correct while task flow improves. |
| `chapter-review` | The critique prioritizes reader promise, pacing, and scene pressure with actionable fixes. |
| `kdp-blurb` | The copy makes a concrete reader promise without unsupported hype and separates platform-sensitive details for verification. |

Trigger precision does not need a new benchmark when the skill description is unchanged. Record it as unchanged; run trigger tests again if the frontmatter description changes.

## Set Up Isolated Inputs

Set `BASE_COMMIT` to the commit immediately before the skill change. For the current unreleased change, it is `e459d8d`.

```bash
CURRENT_ROOT="$(pwd -P)"
BASE_COMMIT=e459d8d
EVAL_ROOT="${TMPDIR:-/tmp}/writing-assistant-v0.2.0-workspace"
BASELINE_ROOT="${TMPDIR:-/tmp}/skill-mania-writing-baseline"

git worktree add "$BASELINE_ROOT" "$BASE_COMMIT"
mkdir -p "$EVAL_ROOT"
```

For each case, create this directory shape. Keep raw evaluation work outside the repository or in a `*-workspace/` directory, which Git ignores.

```text
writing-assistant-v0.2.0-workspace/
  source-boundary-review/
    prompt.md
    baseline/
      response.md
      events.jsonl
      grading.json
      timing.json
    with_skill/
      response.md
      events.jsonl
      grading.json
      timing.json
```

Put the complete task and source text in `prompt.md`. Begin every prompt with this instruction:

```markdown
Read and follow `skills/writing-assistant/SKILL.md` in the current repository. Do not rely on a previously installed copy of this skill or on any prior answer. [Put the identical task and source text here.]
```

## Run Each Pair

Run one fresh, ephemeral Codex session against the baseline worktree and one against the current repository. The `--output-last-message` file keeps the answer separate from the JSONL execution record.

```bash
CASE=source-boundary-review
CASE_ROOT="$EVAL_ROOT/$CASE"
mkdir -p "$CASE_ROOT/baseline" "$CASE_ROOT/with_skill"

codex exec --ephemeral --json \
  --output-last-message "$CASE_ROOT/baseline/response.md" \
  -C "$BASELINE_ROOT" - < "$CASE_ROOT/prompt.md" \
  > "$CASE_ROOT/baseline/events.jsonl"

codex exec --ephemeral --json \
  --output-last-message "$CASE_ROOT/with_skill/response.md" \
  -C "$CURRENT_ROOT" - < "$CASE_ROOT/prompt.md" \
  > "$CASE_ROOT/with_skill/events.jsonl"
```

Repeat for every recommended case. Use the same model and configuration for every run. If a runner does not expose total-token usage, do not estimate it: record the metric as unavailable and use a runner that does before making a token-efficiency claim.

## Grade Blindly

Give the two `response.md` files anonymous labels and grade them against the case assertions before revealing which is baseline or current. Each assertion must have a pass/fail decision and short evidence.

Example `grading.json`:

```json
{
  "assertion_results": [
    {
      "id": "scope",
      "passed": true,
      "evidence": "Calls this a copy edit and does not claim medical review."
    },
    {
      "id": "verification-boundary",
      "passed": true,
      "evidence": "Flags the efficacy claim for source or expert verification without fabricating citations."
    }
  ]
}
```

Create `timing.json` from the run metrics:

```json
{
  "total_tokens": 1234,
  "duration_ms": 8300
}
```

The aggregator accepts either `assertion_results` or `summary.passed` and `summary.total` in `grading.json`.

## Aggregate And Decide

```bash
python3 scripts/summarize-eval-workspace.py "$EVAL_ROOT" \
  --output "$EVAL_ROOT/benchmark.json"
```

Review `benchmark.json` before choosing a release decision:

- Keep the revision when it passes more relevant assertions or fixes the intended failure with an acceptable token/time increase.
- Revise it when the quality gain is not observable, it regresses a case, or the extra cost is not justified.
- Do not treat a tie as proof that a larger skill is better.

Copy this completed record into the pull request or release notes:

```markdown
Skill: writing-assistant
Baseline: <commit>
Cases: <case list>
Trigger precision/recall: unchanged; description was not modified
With-skill assertion pass rate: <value>
Baseline assertion pass rate: <value>
Median token delta: <value>
Median duration delta: <value>
Qualitative winner: <value>
Known weak case: <value>
Decision: keep / revise
```

## Clean Up

After recording the durable benchmark conclusion, remove the temporary baseline worktree:

```bash
git worktree remove "$BASELINE_ROOT"
```

Keep the raw workspace only as long as it is useful for review. Never include customer data, credentials, or unpublished sensitive material in prompts, responses, or event logs.
