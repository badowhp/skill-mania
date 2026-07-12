# Skill evaluation summary

Provider: `codex-cli`; generator: `gpt-5.6-terra`; judge: `gpt-5.6-sol`.

Routing model: `gpt-5.6-luna`.
Baseline: `without-skill`; context mode: `bundled-context`.

| Skill | With skill | Baseline | Delta | Input delta | Output delta | Total delta | Time delta | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |

Routing accuracy: 100% (152/152); the gate also enforces each selected skill's cross-skill accuracy, positive recall, and negative specificity.

Usage: 2 completed calls, 2 model attempts, 36,834 tokens, 91,448 ms cumulative model time.

Gate: **PASS**.

`no-measurable-lift` means the skill met the quality bar without beating the baseline on these cases; it is not evidence of strict improvement.
