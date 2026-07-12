# Skill evaluation summary

Provider: `codex-cli`; generator: `gpt-5.6-terra`; judge: `gpt-5.6-sol`.

Routing model: `gpt-5.6-luna`.
Baseline: `without-skill`; context mode: `bundled-context`.

| Skill | With skill | Baseline | Delta | Input delta | Output delta | Total delta | Time delta | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `ponytail` | 100% | 50% | +50% | +1,139 | -337 | +802 | -6,930 ms | measurable-lift |

Usage: 3 completed calls, 3 model attempts, 36,003 tokens, 19,468 ms cumulative model time.

Gate: **PASS**.

`no-measurable-lift` means the skill met the quality bar without beating the baseline on these cases; it is not evidence of strict improvement.
