# Godot Quest Design Workflow

Use this reference to convert a narrative promise into an explicit, testable quest contract.

## Contents

1. Quest brief
2. Playable spine and branch budget
3. State graph and fact ledger
4. Godot implementation contract
5. Path testing
6. Public studio workflow anchors
7. Primary sources

## Quest Brief

| Field | Required decision |
| --- | --- |
| Player promise | Role, fantasy, and question posed to the player |
| Emotional movement | Intended feeling at hook, reversal, climax, and aftermath |
| World change | What can change in characters, factions, places, systems, or ending |
| Playable verbs | How players observe, decide, investigate, fight, persuade, build, or evade |
| Prerequisites | Facts, actors, items, locations, abilities, time, relationships |
| Commitment | When a choice becomes consequential and how it is communicated |
| Fail policy | Fail, recover, defer, reroute, or transform |
| Branch budget | Bespoke scenes, shared scenes, dialogue variants, systemic outcomes |
| Production scope | Level, character, animation, cinematic, VO, UI, audio, engineering |
| Acceptance | Functional paths, narrative intent, persistence, and export evidence |

## Playable Spine and Branch Budget

Write the shortest coherent route through:

1. hook
2. player goal
3. escalation
4. discovery or reversal
5. commitment
6. climax
7. resolution
8. aftermath

For every beat, name the player verb, required input facts, written output facts, failure or bypass behavior, location, actors, feedback, and test scenario.

Spend bespoke branch content when it materially changes a relationship, location, capability, conflict, reward, or ending. Prefer shared staging with meaningful state variation when the experience remains legible. A branch count is not a measure of agency; consequences and supported player intent matter more.

## State Graph and Fact Ledger

Treat the quest as a graph, not a linear checklist. Include objectives, substates, convergence, delayed callbacks, recovery, and terminal outcomes.

| ID | Kind | Owner | Type | Default | Writers | Readers | Persist | Invalid behavior |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | quest, objective, actor, item, place, choice, outcome |  |  |  |  |  |  |  |

Rules:

- Use stable IDs for authored identity. Do not use display text, array position, or node path as a durable key.
- Keep immutable authored definitions separate from mutable session and persisted state.
- Define legal transitions and terminal states explicitly.
- Make effects idempotent or record whether they were applied so reloads cannot duplicate rewards or world changes.
- Define missing actor, destroyed item, unloaded scene, unavailable location, and unknown legacy-state behavior.
- Version saved quest state and provide migration or a deliberate rejection policy.
- Expose a debug view that can inspect facts, active objectives, transition history, blocked conditions, and pending effects.

## Godot Implementation Contract

- Resources are suitable for reusable authored definitions. Remember that loaded Resources are cached and can be shared; do not silently place per-run mutable state in a shared definition.
- Use a dedicated runtime owner for active quest state. An Autoload is justified when ownership is truly global and must survive scene changes, not merely for convenience.
- Use direct references when nodes share ownership and lifetime. Use typed signals at meaningful boundaries. Use a global event bus only when publishers, subscribers, payload, ordering, and debugging are controlled.
- Keep condition and effect handlers in an explicit registry. Unknown handlers should fail visibly in validation or enter a defined fallback, not disappear silently.
- Persist plain, versioned values and stable IDs. Reconstruct runtime references after load.
- Keep journal presentation derived from state but separate from identity and transition logic.
- Connect level hooks through stable interfaces or groups and verify their behavior when the relevant scene is absent or reloaded.

Suggested handoff:

| Contract | Owner | Required evidence |
| --- | --- | --- |
| Quest definition schema | Narrative and engineering | Validator covers required fields and IDs |
| Conditions and effects | Engineering | Unit tests and unknown-handler failure |
| Level hooks | Level and engineering | Integration scene and missing-scene behavior |
| Journal and choice UI | UX and engineering | State mapping, input, localization expansion |
| Save migration | Engineering and QA | Old, current, corrupt, and boundary saves |
| Narrative acceptance | Quest and QA | Scripted paths plus human playtest notes |

## Path Testing

### Static Validation

Check duplicate IDs, missing references, unreachable states, non-terminal dead ends, invalid cycles, impossible condition sets, missing localization keys, ambiguous writers, unknown effects, and orphaned rewards.

### Automated Layers

1. Unit-test conditions, effects, transition legality, idempotency, time, randomness, rewards, and migration.
2. Run component scenes for dialogue, journal, interaction, and quest-aware actors.
3. Run isolated integration levels with the real quest runtime, inventory, combat, party, UI, scene transitions, and persistence.
4. Script representative end-to-end paths in a deterministic test build where practical.

### Scenario Matrix

Cover the golden path, every material branch, failure and recovery, completionist, speedrun, out-of-order objectives, skipped dialogue, early actor death, missing or consumed item, lethal and non-lethal solutions, simultaneous events, repeated interaction, scene unload, revisit, checkpoint restart, and save or reload before and after every commitment and terminal boundary.

Run at least one exported build. Human narrative QA must separately assess motivation, pacing, continuity, agency, attribution of consequences, emotional impact, accessibility, localization fit, and fun.

## Public Studio Workflow Anchors

Use these as bounded public evidence, not a reconstruction of a private production pipeline:

- CD PROJEKT RED describes turning story, emotion, and major moments into challenges, character development, puzzles, mechanics, choices, and consequences through cross-disciplinary iteration.
- CD PROJEKT RED QA describes early involvement, testing overlapping systems, subjective narrative quality, and varied paths such as golden, completionist, speedrun, and failure play.
- Larian describes translating narrative pitches into gameplay sequences with varied outcomes and player agency. Its public team discussion also emphasizes direct communication, iteration, isolated test levels, automation where useful, manual QA, and attempts to break quests out of sequence.
- These principles support playable proof, explicit state, hostile-path testing, and human judgment. They do not authorize imitating either studio’s characters, prose, worlds, or branded style.

## Primary Sources

- [Godot Resources](https://docs.godotengine.org/en/4.7/tutorials/scripting/resources.html)
- [Godot signals](https://docs.godotengine.org/en/4.7/getting_started/step_by_step/signals.html)
- [Godot project organization](https://docs.godotengine.org/en/4.7/tutorials/best_practices/project_organization.html)
- [Godot command-line operation](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html)
- [CD PROJEKT RED on playable quest design](https://www.cdprojektred.com/en/blog/155/turning-emotions-story-and-big-moments-into-gameplay)
- [CD PROJEKT RED quest design lessons](https://www.gdcvault.com/play/1028897/10-Key-Quest-Design-LessonsStartup)
- [CD PROJEKT RED QA discussion](https://www.cdprojektred.com/en/blog/184/answered-podcast-episode-28-more-than-testing-the-truth-about-game-qa-transcript-included)
- [Larian scripter role description](https://quebec.larian.com/careers/985a11f6-ab93-4a19-a06d-aaabf95c62b5)
- [Larian Divinity team AMA](https://www.reddit.com/r/Games/comments/1q870w5/larian_studios_divinity_ama/)
