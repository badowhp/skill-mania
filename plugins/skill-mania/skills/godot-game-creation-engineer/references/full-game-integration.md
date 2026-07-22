# Full-Game Integration Plan

Use this reference when a request spans graphic style, story, gameplay, content production, persistence, and several Godot systems. The goal is a production spine and a proven vertical slice, not speculative architecture for the entire game.

## Contents

1. Production spine
2. Vision contract
3. Graphic-style implementation
4. Story implementation
5. System map and connection rules
6. Representative vertical slice
7. Test ladder
8. Definition of done
9. Primary sources

## Production Spine

1. Inspect the project, engine version, renderer, platforms, existing scenes, imports, content schemas, saves, tests, and export presets.
2. Write a measurable vision contract for the player promise, game loop, visual identity, story experience, scope, budgets, accessibility, and cut order.
3. Inventory systems and content, assign ownership, and expose missing contracts or impossible dependencies.
4. Choose one short vertical slice that contains the most dangerous cross-system interactions and a representative art and narrative beat.
5. Prove the slice in the target renderer and an exported target build before scaling content production.
6. Turn proven scene, Resource, signal, content, import, save, and test contracts into reusable production patterns.
7. Add content in thin complete increments, preserving a playable mainline and repeatable verification.
8. Stabilize with path, save, performance, accessibility, localization, platform, and regression passes.

## Vision Contract

| Area | Required decision |
| --- | --- |
| Player promise | Role, emotion, core decisions, and memorable change |
| Core loop | Observe, decide, act, receive feedback, progress, recover |
| Visual pillars | Three to five principles plus explicit exclusions |
| Story pillars | Theme, tone, agency, consequence, emotional movement |
| Camera and input | Perspective, FOV, target distance, supported controls |
| Platform | Renderer, resolution, frame target, memory, loading, package limits |
| Content scope | Levels, quests, characters, assets, animation, audio, UI, localization |
| Accessibility | Remapping, readability, timing, motion, audio and visual alternatives |
| Acceptance | Observable slice, path, persistence, performance, and export outcomes |
| Cut order | Features and content removable without breaking the promise |

Treat inspirations as references for principles. Define a distinct, legally safe visual and narrative language instead of asking the pipeline to reproduce another studio’s protected world, characters, assets, or exact style.

## Graphic-Style Implementation

Create a style implementation sheet:

- camera, lens, scale, composition, and silhouette hierarchy
- value range, palette behavior, material and roughness grouping
- lighting, WorldEnvironment, fog, sky, post-processing, VFX, and shadow rules
- character, environment, prop, UI, animation, and audio relationships
- 2D texture or 3D mesh density, texel density, materials, shaders, lights, particles, skeletons, and animation budgets
- Blender version, units, axes, pivots, modular grid, naming, glTF export, Godot import, ownership, and reimport rules
- target renderer, weakest device, profiling scenes, and acceptance thresholds

Build a representative art room or encounter with final-quality samples of the hardest materials, characters, environment modules, lighting, VFX, animation, and UI. Judge it from the gameplay camera. Profile before choosing LOD, visibility ranges, occlusion, shader simplification, or reduced light and shadow cost.

Do not scale asset production until a clean source-to-Blender-to-glTF-to-Godot reimport preserves appearance, skeletons, clips, collisions, navigation assumptions, and runtime budgets.

## Story Implementation

Create a story contract:

- player role, dramatic question, themes, tone, and intended emotional arc
- critical path, optional arcs, level and quest graph, commitments, failures, convergence, outcomes, and aftermath
- playable verbs for every major beat
- stable IDs for quests, objectives, actors, items, locations, choices, and outcomes
- immutable authored definitions, mutable runtime facts, persisted state, migrations, and missing-content behavior
- dialogue, cinematic, journal, UI, audio, localization, level, combat, inventory, party, and reward handoffs
- debug inspection and scenario acceptance

Prototype one playable story beat with placeholder content. It should include setup, player action, feedback, a meaningful decision or failure, changed state, a visible consequence, scene transition, and save or reload boundary. Functional consistency and emotional impact require separate evidence.

## System Map and Connection Rules

Complete a row for every system involved in the slice:

| System | Owner | Authored definition | Runtime state | Inputs | Outputs | Persisted state | Failure behavior | Tests |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Input and settings |  |  |  |  |  |  |  |  |
| Player and camera |  |  |  |  |  |  |  |  |
| Combat or core interaction |  |  |  |  |  |  |  |  |
| AI and navigation |  |  |  |  |  |  |  |  |
| Level and scene flow |  |  |  |  |  |  |  |  |
| Quest and dialogue |  |  |  |  |  |  |  |  |
| Inventory and progression |  |  |  |  |  |  |  |  |
| UI and accessibility |  |  |  |  |  |  |  |  |
| Audio and presentation |  |  |  |  |  |  |  |  |
| Save and load |  |  |  |  |  |  |  |  |

Connection rules:

- A parent can hold direct references to owned children and components with the same lifetime.
- Use typed signals for state changes that cross an ownership boundary or have several deliberate observers.
- Use Resources for reusable authored definitions. Do not silently mutate shared cached definitions as per-run state.
- Use groups for capability or discovery where membership is the real contract, not as a hidden replacement for ownership.
- Use an Autoload for truly global services or state that must survive scene changes. Avoid a universal `GameManager` that owns unrelated systems.
- Use a global event bus only with documented event names, typed payloads, ordering, publishers, subscribers, lifetime, and debug tracing.
- Persist stable IDs and plain versioned values. Reconstruct transient node references after load.
- Every cross-system output needs a defined missing receiver, duplicate delivery, scene unload, retry, and reload behavior.

## Representative Vertical Slice

Choose a ten-to-thirty-minute slice or smaller proof that exercises the riskiest relevant combination:

- boot, settings, input, camera, traversal, pause, restart, and accessibility
- core interaction or combat, AI, navigation, damage, failure, recovery, and feedback
- one representative level route, alternate approach, checkpoint, transition, and return path
- one complete quest or story beat with choice or failure, consequence, journal or UI, and durable facts
- inventory, reward, progression, dialogue, cinematic, audio, and animation only where they belong to the game promise
- representative final art, lighting, materials, VFX, performance pressure, and content import
- save before and after a commitment, quit, load, repeat, and migrate when legacy saves exist
- target export, controller or touch path, localization expansion, and weakest supported device

The slice is not complete because every feature exists. It is complete when the smallest representative set works together, survives reload and export, meets budgets, and creates the intended player experience.

## Test Ladder

1. Static content validation: IDs, references, schemas, import warnings, scene dependencies, missing resources, and export inclusion.
2. Unit logic: state transitions, conditions, effects, calculations, idempotency, serialization, migration, time, and randomness.
3. Component scenes: controller, interaction, UI, AI, dialogue, inventory, animation, and asset acceptance.
4. Isolated integration map: system pairs and dangerous boundaries with controlled content and state.
5. Scripted vertical-slice scenarios: golden, alternate, fail and recovery, completionist, speedrun, off-sequence, pause, restart, scene unload, and repeat actions.
6. Save and reload matrix: before, during, and after commitments, rewards, scene transitions, death, checkpoints, and terminal states.
7. Performance and soak: target renderer and weakest device, representative content, repeated transitions, memory, frame time, loading, and stutter.
8. Export smoke and platform checks: clean headless import where suitable, target preset, package content, boot, input, storage, focus, suspend, and resume.
9. Human playtest: comprehension, choice quality, level readability, emotion, pacing, fun, accessibility, and visual coherence.

Automation should own deterministic state and regression checks. Human observation must own subjective experience. Keep the project headlessly parseable and exportable where practical, but do not treat headless success as proof of presentation or controls.

## Definition of Done

- The vision and system contracts match observable behavior in the slice.
- Every system has one clear runtime owner and persistence owner.
- Art and story pass through a repeatable source, import, content, and save pipeline.
- Cross-system failure, duplicate, unload, and reload behavior is defined and tested.
- Static, unit, component, integration, scenario, save, performance, export, and human evidence exists at the layers relevant to the change.
- The target build meets frame, memory, loading, accessibility, localization, and package acceptance or records exact residual gaps.
- Production patterns are documented only after the slice proves them.
- Scope cuts preserve the central player promise.

## Primary Sources

- [Godot best practices](https://docs.godotengine.org/en/4.7/tutorials/best_practices/index.html)
- [Godot project organization](https://docs.godotengine.org/en/4.7/tutorials/best_practices/project_organization.html)
- [Godot signals](https://docs.godotengine.org/en/4.7/getting_started/step_by_step/signals.html)
- [Godot 3D scene import](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/index.html)
- [Godot import configuration](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html)
- [Godot command-line operation](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html)
- [CD PROJEKT RED level design discussion](https://www.cdprojektred.com/en/blog/188/answered-podcast-episode-30-paths-and-possibilities-the-art-of-level-design-transcript-included)
- [CD PROJEKT RED quest design discussion](https://www.cdprojektred.com/en/blog/155/turning-emotions-story-and-big-moments-into-gameplay)
- [CD PROJEKT RED QA discussion](https://www.cdprojektred.com/en/blog/184/answered-podcast-episode-28-more-than-testing-the-truth-about-game-qa-transcript-included)
- [Larian level designer role description](https://larian.com/careers/87954a51-6677-4c7a-8b5b-a40210d653e0)
- [Larian scripter role description](https://quebec.larian.com/careers/985a11f6-ab93-4a19-a06d-aaabf95c62b5)
