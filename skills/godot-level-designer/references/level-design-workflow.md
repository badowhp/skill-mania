# Godot Level Design Workflow

Use this reference after inspecting the live project. It is a production template, not a substitute for measurements from the actual controller and camera.

## Contents

1. Level pitch
2. Flow and metrics
3. Godot blockout
4. Visual and story pass
5. System handoff
6. Public studio workflow anchors
7. Verification gates
8. Primary sources

## Level Pitch

Record these fields before building expensive content:

| Field | Required decision |
| --- | --- |
| Area purpose | Why this level exists in the game |
| Player promise | Fantasy, emotion, and memorable change |
| Narrative function | Entry state, key beats, exit state, optional revelations |
| Player verbs | Movement, combat, stealth, social, traversal, puzzle, tools |
| Perspective | Camera, FOV, typical distance, input method |
| Metrics | Player size, speed, jump, turn, reach, cover, corridor, doorway, encounter range |
| Flow | Critical path, optional routes, loops, gates, return paths, fail recovery |
| Visual language | Landmarks, silhouettes, values, materials, lighting, affordances |
| Scope | Rooms, encounters, unique assets, characters, cinematics, VO, scripts |
| Budgets | Frame time, draw calls, memory, loading, navigation, content count |
| Dependencies | Quest, gameplay, art, animation, audio, UI, engineering, QA |
| Acceptance | Observable playtest, state, performance, and export outcomes |
| Cut order | What can be removed without breaking the promise |

Write a one-page pitch first. Build a short playable chunk that proves the riskiest claim before extending the whole map.

## Flow and Metrics

- Measure with the production controller, collision shape, camera, FOV, and target input device.
- Draw entry, exit, critical path, optional paths, loops, locked vistas, shortcuts, checkpoints, encounters, rest points, and quest beats.
- Give alternate routes different information, risk, cost, timing, resources, tactical position, or consequence.
- Mark what players can see, hear, predict, revisit, bypass, fail, and recover at each decision.
- Keep required progress readable. Reserve ambiguity for optional discovery or an intentional dramatic effect.
- Test the first thirty seconds, first landmark, first meaningful decision, longest traversal, hardest backtrack, and recovery from every fail state.

## Godot Blockout

### 2D

- Prefer separate `TileMapLayer` nodes for visual, collision, navigation, interaction, and foreground responsibilities when that separation improves ownership and debugging.
- Define reusable terrain, collision, navigation, occlusion, and custom data in `TileSet` resources.
- Instance interactive props, enemies, doors, and quest actors as scenes. Do not hide complex gameplay state inside anonymous tiles.
- Verify navigation, collision, z-order, camera limits, parallax, and pixel or subpixel behavior in motion.

### 3D

- Use primitive meshes, GridMap, or CSG for rapid spatial proof. Treat CSG as prototyping geometry unless profiling and maintainability justify shipping it.
- Establish the modular grid, pivots, floor height, door and stair metrics, cover height, jump clearance, encounter ranges, and camera clearance before asset production.
- Build navigation from appropriate regions, links, agent maps, and layers. Use navigation debug views to inspect connections, avoidance, path edges, and unreachable islands.
- Account for navigation synchronization after map changes; do not judge a path in the same frame that changed the map.
- Import production scenes through the project-pinned glTF workflow. Keep inherited or instanced gameplay scenes separate from source art where practical.

## Visual and Story Pass

Define a small, IP-safe visual contract:

- three to five style pillars and explicit exclusions
- camera and silhouette hierarchy
- value, color, material, and roughness grouping
- landmark, traversal, danger, reward, and interaction languages
- representative lighting and WorldEnvironment states
- modular kit, decals, props, VFX, audio, animation, and storytelling needs
- renderer, device, texture, geometry, shadow, light, and shader budgets

Build one representative art room or encounter first. Test it from the gameplay camera in the target renderer. Use visibility ranges, mesh LOD, occlusion, instancing, and shader simplification only where measurements identify a problem.

Environmental story should change what the player understands or does. For each story element, record its intended observation point, information, optionality, related quest fact, and behavior if skipped or revisited.

## System Handoff

Use stable IDs, scene groups, typed signals, resources, or project-owned interfaces for cross-discipline hooks. Direct references are suitable when objects share an owner and lifetime. Avoid child-index contracts, display text as identity, and a universal event bus with unknown writers.

| Hook | Owner | Input | Output | Persistence | Missing-state behavior | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Door or gate |  |  |  |  |  |  |
| Encounter |  |  |  |  |  |  |
| Checkpoint |  |  |  |  |  |  |
| Quest beat |  |  |  |  |  |  |
| Scene transition |  |  |  |  |  |  |

The handoff to art must preserve gameplay metrics, collision assumptions, navigation, sightlines, affordances, cover, interaction pivots, and performance budgets. The handoff to engineering must name exact scenes, IDs, data, events, fallbacks, and acceptance tests.

## Public Studio Workflow Anchors

Use these as evidence for principles, not as a claim about a complete private pipeline:

- CD PROJEKT RED describes beginning from narrative and quest foundations, aligning a level pitch with emotion, fantasy, gameplay, and scope, proving a small playable chunk early, and balancing believability with playability.
- CD PROJEKT RED describes quest and level ownership as cross-disciplinary work and emphasizes choices whose consequences are understandable to the player.
- Larian describes whiteboxing, keeping spaces playable, iterating or discarding weak ideas, supporting the game’s exploration mechanics, and handing work across environment art, scripting, combat, and cinematics.
- Both examples support early playable proof, direct collaboration, and iteration. They do not justify copying either studio’s visual identity, layouts, or proprietary content.

## Verification Gates

### Gate 1: Pitch

- Promise, verbs, metrics, narrative function, scope, dependencies, acceptance, and cut order are explicit.

### Gate 2: Graybox

- Critical path and required recovery work with the real controller and camera.
- Alternate routes have material differences.
- Collision, navigation, camera, checkpoints, and scene transitions are functional.

### Gate 3: Integrated Slice

- Representative art, lighting, audio, encounters, quest hooks, UI, save/load, and performance operate together.
- The exported target build preserves required behavior.

### Path Matrix

Run the golden path, every material alternate path, optional or secret route, speedrun, completionist sweep, backtrack, checkpoint restart, failure and recovery, quest states, scene reload, save and reload, supported controller or accessibility modes, weakest target device, and exported build.

Record functional bugs separately from readability, pacing, dominance, fun, and emotional comprehension. Observe at least one uncoached player before calling the level production-ready.

## Primary Sources

- [Godot project organization](https://docs.godotengine.org/en/4.7/tutorials/best_practices/project_organization.html)
- [Godot signals](https://docs.godotengine.org/en/4.7/getting_started/step_by_step/signals.html)
- [Godot TileMaps](https://docs.godotengine.org/en/4.7/tutorials/2d/using_tilemaps.html)
- [Godot TileSets](https://docs.godotengine.org/en/4.7/tutorials/2d/using_tilesets.html)
- [Godot CSG tools](https://docs.godotengine.org/en/4.7/tutorials/3d/csg_tools.html)
- [Godot GridMap](https://docs.godotengine.org/en/4.7/classes/class_gridmap.html)
- [Godot 3D navigation](https://docs.godotengine.org/en/4.7/tutorials/navigation/navigation_introduction_3d.html)
- [Godot navigation layers](https://docs.godotengine.org/en/4.7/tutorials/navigation/navigation_using_navigationlayers.html)
- [Godot navigation debug tools](https://docs.godotengine.org/en/4.7/tutorials/navigation/navigation_debug_tools.html)
- [Godot visibility ranges and HLOD](https://docs.godotengine.org/en/4.7/tutorials/3d/visibility_ranges.html)
- [Godot GPU optimization](https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html)
- [CD PROJEKT RED level design discussion](https://www.cdprojektred.com/en/blog/188/answered-podcast-episode-30-paths-and-possibilities-the-art-of-level-design-transcript-included)
- [CD PROJEKT RED quest design discussion](https://www.cdprojektred.com/en/blog/155/turning-emotions-story-and-big-moments-into-gameplay)
- [Larian level designer role description](https://larian.com/careers/87954a51-6677-4c7a-8b5b-a40210d653e0)
