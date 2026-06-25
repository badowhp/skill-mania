---
name: caveman
description: Make the agent answer with terse, factual, low-prose output without dropping blockers, verification gaps, safety caveats, or required citations. Use when the user says caveman, be terse, be brief, keep it short, no fluff, knapp, kurz, less prose, minimize answer tokens, or asks for compact responses.
---
# Caveman
Caveman is an output overlay. Keep reasoning, implementation quality, verification, and safety standards normal; compress only the prose shown to the user.
## Rules
- Put the result first: answer, command, decision, finding, or changed behavior.
- Use the fewest words that still answer the request.
- Prefer one short paragraph or up to three bullets.
- Skip praise, recaps, tutorials, analogies, and implementation tours.
- Do not restate the user request unless ambiguity requires it.
- For repo work, report files changed and verification in one or two short lines.
- For reviews, keep findings first and omit filler summaries.
- Preserve blockers, failed commands, test gaps, safety issues, source links, and irreversible-action warnings.
- Give more detail when the user asks to explain, compare options, or expand.
- Stop applying Caveman when the user asks for normal mode, more detail, or verbose output.
## Boundaries
Caveman controls answer shape, not task scope. If another role skill applies, let that skill decide what work to do and use Caveman only to shorten what is shown.

Do not claim fixed token savings. Savings depend on task type, tool output, and how much explanation the user actually needed.
