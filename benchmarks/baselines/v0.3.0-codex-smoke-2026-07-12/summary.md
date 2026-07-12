# Skill evaluation summary

Provider: `codex-cli`; generator: `gpt-5.6-terra`; judge: `gpt-5.6-sol`.

Routing model: `gpt-5.6-luna`.
Baseline: `without-skill`; context mode: `bundled-context`.

| Skill | With skill | Baseline | Delta | Token delta | Time delta | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `agent-context-maintainer` | 0% | 0% | +0% | +1,903 | +13,026 ms | below-quality-bar |
| `austrian-law-helper` | 100% | 50% | +50% | +1,902 | +2,780 ms | measurable-lift |
| `caveman` | 100% | 100% | +0% | +326 | -1,879 ms | no-measurable-lift |
| `commit` | 0% | 0% | +0% | +808 | +950 ms | below-quality-bar |
| `design-engineer` | 100% | 100% | +0% | +5,671 | +1,566 ms | no-measurable-lift |
| `design-reviewer` | 100% | 50% | +50% | +1,686 | +530 ms | measurable-lift |
| `gameplay-consultant` | 100% | 50% | +50% | +1,827 | +9,483 ms | measurable-lift |
| `godot-game-creation-engineer` | 0% | 0% | +0% | +1,926 | +6,065 ms | below-quality-bar |
| `ponytail` | 0% | 50% | -50% | +1,123 | +1,379 ms | below-quality-bar |
| `security-engineer` | 100% | 100% | +0% | +4,579 | +5,491 ms | no-measurable-lift |
| `senior-developer` | 100% | 100% | +0% | +3,613 | +3,129 ms | no-measurable-lift |
| `senior-devops-engineer` | 100% | 50% | +50% | +11,022 | +13,935 ms | measurable-lift |
| `seo-geo` | 100% | 50% | +50% | +4,365 | -11,462 ms | measurable-lift |
| `skill-curator` | 50% | 0% | +50% | +2,216 | +14,907 ms | below-quality-bar |
| `software-architect` | 100% | 50% | +50% | +4,232 | +8,461 ms | measurable-lift |
| `testing-engineer` | 100% | 100% | +0% | +2,426 | +1,576 ms | no-measurable-lift |
| `visual-qa` | 50% | 0% | +50% | +4,071 | +3,736 ms | below-quality-bar |
| `writing-assistant` | 100% | 50% | +50% | +11,055 | +2,871 ms | measurable-lift |

Routing accuracy: 100% (151/151); the gate also enforces each selected skill's cross-skill accuracy, positive recall, and negative specificity.

Usage: 56 completed calls, 57 model attempts, 744,962 tokens, 850,762 ms cumulative model time.

Gate: **FAIL**.

`no-measurable-lift` means the skill met the quality bar without beating the baseline on these cases; it is not evidence of strict improvement.
