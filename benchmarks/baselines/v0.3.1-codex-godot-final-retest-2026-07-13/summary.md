# Skill evaluation summary

Provider: `codex-cli`; generator: `gpt-5.6-terra`; judge: `gpt-5.6-sol`.

Routing model: `gpt-5.6-luna`.
Baseline: `without-skill`; context mode: `bundled-context`.

| Skill | With skill | Baseline | Delta | Input delta | Output delta | Total delta | Time delta | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `godot-game-creation-engineer` | 100% | 50% | +50% | +1,641 | +284 | +1,925 | +5,849 ms | measurable-lift |

Usage: 3 completed calls, 3 model attempts, 42,937 tokens, 68,957 ms cumulative model time.

Gate: **PASS**.

`no-measurable-lift` means the skill met the quality bar without beating the baseline on these cases; it is not evidence of strict improvement.
