# Skill evaluation summary

Provider: `codex-cli`; generator: `gpt-5.6-terra`; judge: `gpt-5.6-sol`.

Routing model: `gpt-5.6-luna`.
Baseline: `without-skill`; context mode: `bundled-context`.

| Skill | With skill | Baseline | Delta | Input delta | Output delta | Total delta | Time delta | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `agent-context-maintainer` | 100% | 100% | +0% | +1,520 | +0 | +1,520 | -1,099 ms | no-measurable-lift |
| `caveman` | 100% | 50% | +50% | +473 | +7 | +480 | -85 ms | measurable-lift |
| `commit` | 100% | 50% | +50% | +812 | +5 | +817 | +817 ms | measurable-lift |
| `design-engineer` | 100% | 50% | +50% | +5,481 | +708 | +6,189 | +12,731 ms | measurable-lift |
| `godot-game-creation-engineer` | 50% | 50% | +0% | +1,597 | -850 | +747 | -15,247 ms | below-quality-bar |
| `ponytail` | 100% | 100% | +0% | +1,139 | +5 | +1,144 | -314 ms | no-measurable-lift |
| `security-engineer` | 100% | 100% | +0% | +4,272 | -48 | +4,224 | +4,303 ms | no-measurable-lift |
| `senior-developer` | 100% | 100% | +0% | +3,539 | +253 | +3,792 | +4,831 ms | no-measurable-lift |
| `skill-curator` | 100% | 100% | +0% | +1,710 | +235 | +1,945 | +4,395 ms | no-measurable-lift |
| `testing-engineer` | 100% | 100% | +0% | +2,355 | -99 | +2,256 | -2,086 ms | no-measurable-lift |
| `visual-qa` | 100% | 50% | +50% | +3,867 | +430 | +4,297 | +7,596 ms | measurable-lift |

Usage: 33 completed calls, 33 model attempts, 433,409 tokens, 449,273 ms cumulative model time.

Gate: **FAIL**.

`no-measurable-lift` means the skill met the quality bar without beating the baseline on these cases; it is not evidence of strict improvement.
