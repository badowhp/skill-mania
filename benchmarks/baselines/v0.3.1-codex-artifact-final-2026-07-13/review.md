# Artifact-backed benchmark review

This checkpoint replaced the 11 weak, tied, or below-bar `v0.3.0` smoke cases with committed
artifacts and fixed the judge so it receives the same fixture-augmented task as both generation
arms. It also separates input, output, reasoning, and total-token effects.

## Full run

- Ten of 11 skills met the per-skill quality floor.
- `caveman`, `commit`, `design-engineer`, and `visual-qa` showed measurable lift in this run.
- `agent-context-maintainer`, `ponytail`, `security-engineer`, `senior-developer`,
  `skill-curator`, and `testing-engineer` passed but tied baseline on their sampled case.
- Godot missed a composite assertion because the fixture lacked a playable collision world and
  the skilled response misread the HUD's inverted numeric semantics.

## Adjudicated focused evidence

- `v0.3.1-codex-godot-final-retest-2026-07-13`: after adding a parseable wall/player/HUD/pause
  world and requiring numeric UI semantics to be traced from source, Godot scored 100% versus
  50% baseline (+50 points). The headless project parse also passed.
- `v0.3.1-codex-ponytail-abstraction-fixture-2026-07-13`: on a loader with observable
  allowlisting, manifest validation, and signature verification, Ponytail rejected a speculative
  registry while preserving all controls; it scored 100% versus 50% baseline and used 337 fewer
  output tokens.
- `v0.3.1-codex-routing-2026-07-13`: routing passed 152/152 after Caveman was narrowed to explicit
  mode invocation.

These focused reruns supersede the affected Godot and Ponytail rows; they do not turn the full
11-case snapshot into a single passing model gate. The remaining baseline ties need harder cases,
repeated runs, and operational tool evidence before any deprecation decision.
