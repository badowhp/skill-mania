# Design fidelity Codex session benchmark

Date: 2026-07-20  
Result: PASS for the two sampled cases  
Method: paired in-session forward test, not a machine-run `benchmark.json` snapshot

## Comparison

- Baseline: `v0.4.0` skill snapshot from commit
  `92f96b6d3e43d80e33e536a82bacf49a0f4a28f8`; package digest
  `08201c54d22719dbe92d332a690e0e5ebe877af1dc6067e6cff14543f506f856`.
- Candidate: `v0.5.0` worktree design skill; package digest
  `ec21ecf615e15ff46180a3f231404585a7bd9a0eabe210eb53de08ccfb93df2e`.
- Cases: `fidelity-staged-build` and `pixel-perfect-extraction`.
- Each generation arm ran in a fresh Codex worker with no conversation history. Both arms received
  the same raw fixture; only the explicitly selected skill snapshot differed.
- Fresh judges received anonymized candidates in opposite A/B order, the original fixture, and
  observable assertions. Generators did not receive expected outputs or the intended winner.

## Results

| Case | Baseline | Initial candidate | Final candidate | Winner |
| --- | ---: | ---: | ---: | --- |
| `fidelity-staged-build` | 0/2 | 1/2 | 2/2 | candidate |
| `pixel-perfect-extraction` | 0/2 | 2/2 | 2/2 | candidate |
| **Total** | **0/4 (0%)** | **3/4 (75%)** | **4/4 (100%)** | **candidate, 2/2 cases** |

Observed final lift: +100 percentage points on the four sampled assertions.

## Evidence

- Fidelity baseline invented mobile type and spacing values, combined both sections, and omitted
  `--design-md` from its scanner command.
- The first candidate traced tokens and used the complete failing scanner command, but still
  returned a monolithic multi-section component. The skill was tightened to require a completed
  section audit before starting the next.
- A fresh candidate rerun separated Method and Proof, preserved the hero, kept visual values
  token-derived, and named `--design-md DESIGN.md --fail-on medium` without claiming execution.
- Pixel-perfect baseline used a bullet extraction, colored every feature icon with the accent,
  and omitted hover behavior.
- Pixel-perfect candidate separated measured and provisional values before code, matched the
  measured token set, accented only one icon, added hover/focus/disabled states, and named
  unresolved assumptions.

## Limits

- This session route does not expose model-route, token, or duration metrics. None are inferred.
- The cases are text-only instruction-following checks; deterministic scanner tests and rendered
  browser review remain separate evidence.
- The final fidelity score is an iteration result on a known failing case, not an untouched
  holdout. Add a new multi-section holdout before treating the 100% sample as generalization
  evidence.

## Decision

Keep the scanner and instruction changes. They show measurable lift over the immutable baseline
on both targeted cases, and the final candidate meets the sampled quality floor. Do not use this
report with `compare-skill-benchmarks.py`; it intentionally omits fabricated runner metrics.
