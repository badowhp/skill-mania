# Blender Game Asset Workflow

Keep the workflow small: one measurable asset contract, one editable Blender source, one intentional glTF delivery, and one Godot acceptance scene.

## Asset Contract

| Area | Record before production |
| --- | --- |
| Purpose | Gameplay use, camera distance, variants, attachment points |
| Dimensions | Units, height, footprint, modular grid, origin, pivots, forward axis |
| Visual target | Silhouette, proportions, value, roughness, detail frequency, exclusions |
| Geometry | Triangle or vertex target, deformation needs, LODs, collision |
| Surface | UV sets, texel density, texture sizes, channels, material-slot budget |
| Rig | Skeleton contract, deform bones, controls, attachments, shape keys |
| Animation | Clip names, ranges, FPS, loop, contacts, root motion, transitions |
| Delivery | Pinned Blender version, glTF variant, export preset, naming, file layout |
| Acceptance | Godot version, import preset, test scene, renderer, device, frame budget |

Prefer a project-pinned Blender LTS when stability and collaboration matter. Confirm the project version and matching official manual rather than assuming the newest release is compatible.

## Modeling Checklist

- Work in real scale with an intentional forward axis, origin, pivots, modular grid, and applied transforms where the pipeline requires them.
- Approve proportions and silhouette from the gameplay camera before subdivision, sculpt detail, or texture polish.
- Keep geometry that contributes to silhouette, shading, deformation, collision, or a measured close-up need.
- Remove accidental duplicate vertices, loose or non-manifold geometry, internal faces, zero-area faces, broken normals, and unused material slots.
- Place edge flow around joints and expression zones according to the required deformation. Test the deformation instead of optimizing for attractive wireframes.
- Keep UV islands, seams, padding, orientation, overlap policy, texel density, and lightmap requirements explicit.
- Prefer few, coherent material slots. Use glTF-compatible Principled BSDF paths and bake procedural or unsupported effects when required.
- Define LOD thresholds and collision shapes from runtime measurements, not arbitrary polygon percentages.

## Rig and Animation Checklist

- Lock proportions, rest pose, scale, naming, and skeleton hierarchy before producing many clips.
- Separate animator controls from exported deform bones where useful; export only what the runtime contract needs.
- Normalize weights, remove unintended influences, and test shoulders, hips, knees, elbows, hands, face, and attachment points at extreme poses.
- Store clips as stable Actions or a deliberate NLA setup with unique names and unambiguous frame ranges.
- Define loop seams, contacts, anticipation, recovery, transition pose, FPS, root-motion bone and axis, in-place variants, and additive intent.
- Review motion at game speed from the gameplay camera. Check foot sliding, penetrations, silhouette, timing, arcs, and gameplay readability.
- Test shape keys with the final deformation-bone export policy; hidden non-deform influences can change results.

## Godot glTF Handoff

- Prefer glTF 2.0 for the Godot 3D exchange contract. A `.glb` is convenient for a self-contained delivery; `.gltf` with external data can make individual textures easier to inspect and version.
- Direct `.blend` import uses a Blender installation and conversion pipeline. It can be convenient, but an explicit glTF artifact is easier to reproduce across machines and build agents.
- Enable backface culling in source materials when the game requires one-sided surfaces; otherwise source and runtime previews can disagree.
- Keep material graphs within supported glTF paths or bake the intended result.
- Review Godot import options for animation sampling, clip slicing, loop detection, root motion, bone filtering, materials, meshes, LODs, physics, and generated scene structure.
- Use deformation-bone-only export where appropriate, especially when shape keys are involved, and verify the result rather than assuming identical skinning.
- For retargeting, define a BoneMap or SkeletonProfile mapping and verify rest pose, scale, orientation, root motion, and every representative clip.
- Reimport into a clean Godot test scene under representative WorldEnvironment, camera, animation playback, collision, navigation, and profiler conditions.

## Acceptance Gate

- Source opens in the pinned Blender version without missing external data.
- Names, transforms, origins, dimensions, normals, UVs, materials, rig, weights, actions, and unused data pass inspection.
- Fresh glTF export contains only intended objects and data.
- Fresh Godot import preserves scale, orientation, surface response, skeleton, shape keys, clips, loop behavior, root motion, attachments, LOD, and collision.
- The asset meets the target camera, renderer, device, memory, geometry, texture, material, draw-call, and animation budgets.
- Any remaining artistic judgment is demonstrated with comparison views; any untested platform behavior is stated as a gap.

## Primary Sources

- [Blender deployment and LTS guidance](https://docs.blender.org/manual/en/dev/advanced/deploying_blender.html)
- [Blender glTF 2.0 importer and exporter](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html)
- [Blender mesh cleanup tools](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/cleanup.html)
- [Godot supported 3D formats](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)
- [Godot 3D import workflow](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/index.html)
- [Godot advanced 3D import configuration](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html)
- [Godot skeleton retargeting](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html)
