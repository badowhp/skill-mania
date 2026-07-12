# Local smoke baseline review

This is the first saved local all-skill checkpoint for the `v0.3.0` skill set. It used one
positive case per skill at case offset `0`, a no-skill comparison, the isolated Codex CLI
backend, the reviewed balanced generator, quality judge, and throughput router.

## Result

- With-skill assertion pass rate: 72.22% (26/36).
- Without-skill assertion pass rate: 50.00% (18/36).
- Observed lift: +22.22 percentage points.
- Routing: 100% (151/151), including cross-skill ownership, positive recall, and near-miss
  specificity for every selected skill.
- Gate: fail because six sampled skills were below the per-skill 80% quality floor.
- Usage: 56 completed calls, 57 model attempts, 744,962 tokens, and 850,762 ms cumulative model
  time. One failed routing attempt is included; it revealed and led to removal of an unsupported
  strict-schema keyword.

## Failure triage

Five failures are primarily harness-limited, not demonstrated operational regressions:

- `agent-context-maintainer`: no `AGENTS.md` artifact was supplied, so the model could not perform
  or prove the requested edit.
- `commit`: the bundled-context tier intentionally exposed no worktree, so inspection, staging,
  staged-diff review, and a commit could not occur.
- `godot-game-creation-engineer`: no Godot project was supplied or executable, so inspection and
  runtime verification could not occur.
- `skill-curator`: external browsing and candidate sources were absent; the response correctly
  preserved the evidence boundary and still passed the decision-taxonomy assertion.
- `visual-qa`: no running URL or browser was available; the response correctly separated missing
  screenshots from unknown overflow, console, request, and focus findings.

One sampled result is a plausible instruction/output weakness:

- `ponytail`: the with-skill answer proposed a caller guard (`if tag`) instead of fixing the shared
  formatter-level root cause, and it did not explicitly state that abstraction and dependency work
  were omitted. The no-skill answer passed the root-cause assertion. Re-run this exact case with a
  small formatter fixture before changing the skill.

## Interpretation

Use this snapshot for time-series comparison, not as release evidence. The smoke sample has only
two assertions per skill, so an 80% floor is effectively all-or-nothing. Bundled-context scores
measure instruction following and routing; they do not replace deterministic helper tests or
tool-bearing forward tests with repositories, URLs, browser state, or external sources.
