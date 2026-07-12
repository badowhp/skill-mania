# Benchmark Improvement Plan

## Decision

Keep all 18 skills for the next artifact-backed evaluation. Do not remove a tool-bearing skill
because it failed a text-only harness, and do not expand a skill merely because an easy baseline
also scored 100%. The only instruction-level defect demonstrated by the saved smoke run was
`ponytail` choosing a caller guard over the shared formatter invariant. `caveman` also has an
activation-cost mismatch: ordinary requests to be brief do not need a persistent overlay.

The saved `v0.3.0` smoke result remains useful as a checkpoint, but not as evidence that every
individual skill helps. It sampled one case and two assertions per skill, had no repeated runs,
and exposed no tools. Five skills hit a 100%/100% ceiling, five operational skills lacked the
artifact or runtime their prompt required, `skill-curator` lacked external sources, and
`ponytail` plausibly regressed.

## Benchmark Repairs Applied

1. Send the fixture-augmented task to the blind judge. Previously generators saw committed
   fixtures but the judge received only the short prompt, so artifact-specific claims could not
   be graded against the source evidence.
2. Report input, output, reasoning, and total-token deltas separately. Total tokens alone hide
   whether an output overlay saved response tokens while adding instruction context.
3. Replace the first smoke cases for every no-lift or below-bar skill with source-backed tasks.
   Text-only operational cases now ask for an exact patch, staging decision, or evidence audit
   without rewarding false claims that commands ran.
4. Narrow `caveman` to explicit Caveman-mode requests. A normal one-off request for a short
   answer remains a baseline capability.
5. Strengthen `ponytail` around the highest shared invariant, caller inspection, coherent-diff
   size, and the prohibition on inventing patches without source.

The bundled-context tier still loads every safe text resource and exposes no shell, browser,
filesystem, or network tools. That is intentionally an instruction-following tier, but it does
not model progressive reference loading or operational completion cost. A later runner change
should add case-selected skill resources and a tool-execution tier with deterministic verifiers.

## Plans For Skills Without Demonstrated Lift

| Skill | Saved result | Diagnosis | Change and next evidence | Removal or merge rule |
| --- | --- | --- | --- | --- |
| `agent-context-maintainer` | 0% vs 0% | No AGENTS.md was supplied. | Use a complete AGENTS.md fixture with durable commands and stale dated/person-specific notes; grade the returned replacement exactly. Later forward-test a real canonical edit plus sync. | Merge into a broader local-maintenance owner only if artifact-backed edits add no accuracy and routing overlaps. |
| `caveman` | 100% vs 100% | The assertions measured correctness, not compression; the prompt itself requested Caveman/brief output. | Restrict triggering to explicit Caveman mode, report output-token delta, test competing brevity/caveat tasks and multi-turn drift, and compare against a `be brief` prompt arm. | Deprecate if a short prompt matches quality, output tokens, safety gaps, and multi-turn consistency across a repeated task set. |
| `commit` | 0% vs 0% | The isolated read-only harness had no worktree. | Grade an exact staging decision from status/diff/test fixtures; separately forward-test in a disposable Git repository and verify the resulting commit and untouched files. | Keep while it provides safe mutation procedure; never remove from a prose-only failure alone. |
| `design-engineer` | 100% vs 100% | The user prompt disclosed interview and DESIGN.md steps, so baseline could copy the workflow. | Use an actual generic pricing-page excerpt and product constraints without spelling out the workflow; grade evidence-derived direction, states, and review gating. | Merge only if hard UI tasks show no lift over the creation/review/visual-QA combination and the trigger remains redundant. |
| `godot-game-creation-engineer` | 0% vs 0% | No Godot project or executable runtime was supplied. | Use a parseable Godot 4 project fixture for exact patch reasoning, then apply the candidate in a disposable copy and run headless parse plus behavior checks. | Keep unless repeated runnable Godot tasks show no benefit and the useful engine rules fit cleanly in `senior-developer`. |
| `ponytail` | 0% vs 50% | The skill optimized line count before locating the shared formatter invariant; the first artifact rerun then exposed a second benchmark flaw by requiring explicit narration of omitted abstractions instead of inspecting the diff. | Rerun the same formatter bug with both callers and an observable no-extra-scope assertion; add several YAGNI cases that measure diff scope, root-cause correctness, and preserved safety. | Remove the overlay and move its useful rules into `senior-developer` if it remains worse than baseline or only changes tone. |
| `security-engineer` | 100% vs 100% | IDOR was obvious and the assertions were baseline-level. | Use a principal-blind signed-URL cache fixture where authorization is bypassed only after a warm request; require the exploit path, negative test, and hold decision. | Keep because attacker modeling and safety boundaries are distinct; consider narrower subskills only if the broad bundle causes missed references or token cost without lift. |
| `senior-developer` | 100% vs 100% | No diff was supplied, so both arms merely requested evidence. | Attach a validation diff with an empty-string regression and grade line-level diagnosis plus exact missing tests. Expand to concurrency and migration fixtures. | This is the default application owner; reduce references or split focused modules before considering removal. |
| `skill-curator` | 50% vs 0% | The skill improved decision taxonomy but had no candidates, manifests, licenses, or live browsing. | Supply inspected candidate snapshots for the bundled tier and separately run a live-source review with license and maintenance checks. | Merge with context maintenance only if external discovery/adoption decisions add no value beyond local metadata work. |
| `testing-engineer` | 100% vs 100% | The prompt explicitly requested the expected test-layer rules. | Attach a page-only cache implementation and weak test; require a regression that fails before the fix and avoid redundant E2E. Add flaky and contract cases with deterministic fixtures. | Merge into `senior-developer` only if hard test-selection and flaky-triage cases show no independent lift or routing value. |
| `visual-qa` | 50% vs 0% | No URL/browser existed; only its evidence taxonomy could pass. | Grade a real report with desktop-only evidence, console and network failures, and missing focus/mobile captures; retain helper tests and add a live static-page capture tier. | Keep while the helper and browser evidence matrix remain distinct; remove only if an installed browser workflow fully subsumes both procedure and verification. |

## Skills With Measurable Smoke Lift

Do not add instructions to these skills based on the smoke result alone. Preserve the current
behavior and replace weak first cases with harder evidence in the next full-cycle update:

| Skill | Saved lift | Next stronger evidence |
| --- | ---: | --- |
| `austrian-law-helper` | +50 points | Redacted notice/deposit documents plus live official-source and date verification; human legal-safety review. |
| `design-reviewer` | +50 points | A concrete DESIGN.md and rendered evidence, not a missing-artifact FAIL. |
| `gameplay-consultant` | +50 points | Telemetry/playtest notes with a falsifiable experiment and rejection threshold. |
| `senior-devops-engineer` | +50 points | An actual Terraform plan with deterministic destructive-change extraction and rollback review. |
| `seo-geo` | +50 points | Rendered head, response headers, robots, sitemap, schema, and post-launch monitoring fixture. |
| `software-architect` | +50 points | Current topology, ownership, data-flow, scale, and migration constraints with an ADR artifact. |
| `writing-assistant` | +50 points | A real chapter or documentation excerpt, blind human preference review, and preservation checks. |

## Retest Sequence

1. Run deterministic repository tests, fixture validation, package sync checks, and helper smoke
   tests.
2. Rerun the 11 changed smoke cases as paired `with_skill`/`without_skill` generations with the
   same generator and judge routes.
3. Review raw answers and judge evidence; adjudicate artifact misunderstandings before changing
   assertions.
4. For `ponytail`, require non-regression on the exact formatter case before keeping the text
   change. For `caveman`, treat output-token savings and preserved caveats as the primary signal,
   not quality lift on saturated tasks.
5. Run tool-bearing checks in disposable fixtures for Git, Godot, and browser evidence. Do not
   promote bundled-context passes to operational evidence.
6. After two or more repeated paired runs, record variance or confidence intervals. Do not make
   removal decisions from one model sample.

## Artifact-Backed Results: 2026-07-13

The first 11-case artifact run produced measurable lift for `caveman`, `design-engineer`,
`security-engineer`, `senior-developer`, and `visual-qa`. `agent-context-maintainer`, `commit`,
`skill-curator`, and `testing-engineer` passed the quality floor but tied baseline. The initial
Godot and Ponytail failures were adjudicated before changing instructions:

- Godot passed 100% in both arms after the missing PauseController fixture was supplied. The
  original below-bar result was a fixture defect, not demonstrated skill weakness. A later full
  rerun exposed an inverted HUD-semantics mistake; after adding a playable wall/HUD fixture and a
  source-tracing rule, the final focused case scored 100% with skill versus 50% baseline.
- Ponytail passed the shared-root-cause formatter case after its performative “say what you did
  not build” assertion was replaced with an observable diff constraint. Across its other three
  cases, both arms scored 83%; Ponytail rejected a speculative registry that baseline built and
  used 747 fewer output tokens, but failed to state that existing validation/security contracts
  must remain unchanged. After attaching the actual loader contract and adding that narrow
  safeguard, the focused retest scored 100% with skill versus 50% baseline and used 337 fewer
  output tokens. The skill is retained.

No skill is removed from this cycle. Four baseline ties still need harder cases, repeated runs,
and operational evidence; a single paired text-only tie is insufficient for deprecation.

The final routing run passed 152/152 after Caveman was narrowed to explicit mode invocation.

## Research Basis

- OpenAI's current [Build skills](https://learn.chatgpt.com/docs/build-skills) guidance says
  implicit activation depends on a concise, front-loaded description and recommends focused
  jobs, imperative inputs/outputs, and trigger tests.
- Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
  emphasize concise progressive disclosure, real workflows, feedback loops, and testing across
  intended models. Its [enterprise guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise)
  separates triggering, isolation, coexistence, instruction following, output quality, and
  deprecation decisions.
- [SkillsBench v1.1](https://arxiv.org/abs/2602.12670) uses matched with/without-skill runs and
  deterministic verifiers; its aggregate reports meaningful average lift but also large
  task/domain variation, with focused bundles outperforming exhaustive ones.
- Community evidence is treated as hypothesis, not authority. A
  [Reddit Caveman comparison](https://www.reddit.com/r/ClaudeAI/comments/1sytl0c/i_benchmarked_caveman_against_the_prompt_be_brief/)
  found a two-word brevity prompt matched the overlay on saturated single-turn tasks and suggested
  multi-turn drift as the more useful distinction. Another
  [Reddit benchmark discussion](https://www.reddit.com/r/ClaudeAI/comments/1rm16ni/built_a_skill_that_finds_where_claude_actually/)
  highlights why 100%/100% cases need harder failure-targeted prompts. A
  [Cursor forum discussion](https://forum.cursor.com/t/agents-md-outperforms-skills-in-our-agent-evals/150242)
  reports activation misses in another harness; local routing was 100%, so that observation does
  not override this repository's routing evidence.
