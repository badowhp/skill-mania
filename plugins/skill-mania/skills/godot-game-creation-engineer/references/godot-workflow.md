# Godot Workflow Reference

## Version And Project Evidence

- Inspect `project.godot` first. Treat its feature tags, renderer, input actions, autoloads, display settings, and main scene as project contracts.
- Inspect the engine/editor version recorded by the project, CI, or team tooling. Check the matching stable documentation before relying on an engine API, export option, or platform limitation.
- Do not infer a project's language from one file. Inspect the affected scripts and build configuration before proposing GDScript, C#, or GDExtension work.

## Scene And Script Boundaries

- Let a scene own one coherent responsibility: a player, encounter, menu, reusable widget, or level segment. Avoid a global manager that owns unrelated scene-local state.
- Favor explicit dependencies and narrow signals over hard-coded absolute node paths. A direct reference is fine when the nodes have the same owner and lifetime.
- Keep configuration in exported properties or resources when designers need to tune it without editing code. Keep runtime state out of shared resources unless shared state is intentional.
- Check instanced scenes, inherited scenes, autoloads, groups, and signal connections before renaming nodes or moving scripts.

## Input, Timing, And Physics

- Define named actions in the Input Map and read actions rather than raw keys in gameplay code. Verify keyboard, controller, touch, and rebinding implications when they are in scope.
- Use the physics update path for collision-sensitive movement and apply time-based motion with the engine's supplied delta. Use the regular process path for presentation and non-physics behavior that needs per-frame updates.
- Verify pause mode, focus changes, time scale, scene reload, and restart behavior for player-facing state machines.

## Debugging And Performance

- Reproduce the issue in the smallest scene or state that still fails. Inspect the debugger, remote scene tree, errors, warnings, and relevant profiler data before guessing at a fix.
- Measure before changing rendering, allocation, navigation, or physics architecture. Keep a before/after path and device or renderer context.
- Treat a behavior that works only in the editor as unverified until it has been checked in a representative exported build.

## Export Verification

- Inspect `export_presets.cfg`, the selected target, templates, SDK prerequisites, signing or credentials handling, and output path before exporting.
- Verify that non-resource files such as JSON, CSV, or text files are included when the game loads them at runtime. Check path casing because exported packages may be case-sensitive even when a development filesystem is not.
- Keep credentials and signing material out of source control and build logs. Do not describe an export as release-ready without a real export and launch check.

## Primary Documentation

- [Godot stable documentation](https://docs.godotengine.org/en/stable/)
- [Nodes and scenes](https://docs.godotengine.org/en/stable/getting_started/step_by_step/nodes_and_scenes.html)
- [InputMap](https://docs.godotengine.org/en/stable/classes/class_inputmap.html)
- [Exporting projects](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html)
