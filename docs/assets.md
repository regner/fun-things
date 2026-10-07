# Godot asset workflow

Keep editable sources, imported outputs, reusable scene assemblies, and level
placement connected. Each has a clear authority so an export or playtest cannot
erase hand-authored work.

## Source and placement ownership

Create every visible 3D model in Blender, including blockout and technical-spike
fixtures. Commit the `.blend` source and export explicit glTF/GLB outputs. Build Godot
prefabs around imported model instances with collision, sockets, materials, and
gameplay components. Place those prefabs in saved level scenes. Godot recommends
glTF and can also import Blender files directly; explicit GLB exports are a useful
choice when keeping Blender off runtime/developer import dependencies.
[Godot 3D formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html).

Keep modeling sources in a `.gdignore` directory when using explicit exports.
Commit source, exported files, and changed import settings together. Retain license
and provenance records for external art, fonts, and audio. Add a simple catalogue
when finding the correct source or maintaining source/output consistency becomes
difficult; fingerprints and automated exports are useful follow-ups at that scale.

A catalogue entry or asset handoff should identify source, selected export
root/collection, output path, dimensions, origin, axes, material slots, collision
expectations, stable identifiers, and preview. Exclude studio cameras/lights from
exports. Exporting a shared source should update all dependent component outputs.
Use scratch exports to compare changes without overwriting approved outputs.

Measured plans and layout JSON are design/test references. The saved scene owns
authored placements. An intentional procedural level needs an explicit source of
truth and, for multiplayer, a shared seed/content contract. Avoid two competing
placement writers. Give separate contributors explicit file ownership when work
is divided; have one integrator own a shared level scene.

## Model and prefab contracts

For 3D work, use metres, Godot +Y up and local -Z forward. Define origins before
detailing: ground-centred for ordinary props, actual pivots for animated joints,
and documented exceptions for gameplay roots. Blender uses +Z up; apply the glTF
axis conversion once. Check scale, rotation, normals, bounds, and mirrored winding.
Preserve socket and component names used by prefabs or animations.

Keep imported models instanced rather than copying their vertex data into scene
files. Make children editable only for intentional overrides. Share reusable
materials as external resources. After export, import and save/reload representative
prefabs and inherited variants to verify ancestry, overrides, and scene size.

Visible 3D geometry must stay linked to Blender exports. Do not use Godot primitive
meshes, CSG, runtime-generated render meshes, or copied vertex data embedded in
project-owned scenes. This includes mesh-based effects and their particle draw
geometry. Shaders and particle behavior may animate imported geometry; 2D UI and
minimap drawing do not need Blender models. Simple collision shapes, navigation
data, occluders, and temporary debug overlays are not authored render models.
Keep those separate from decoration and preserve authored placement.

## Collision and multiplayer identity

Separate decorative geometry from gameplay collision. Use simple shapes when they
meet the gameplay contract, appropriate convex shapes for moving bodies, and reviewed
static surface collision. Check routes with the actual actor size and movement,
including turns, slopes, seams, camera obstruction, spawn clearance, and boundaries.
Avoid duplicate coplanar ground colliders or small decorative snag points.

Breakable or persistent interactive objects need stable gameplay IDs independent
of local object instance IDs. Preserve them during reparenting or art replacement.
Author visual and collision changes together, and ensure the network state applies
both consistently. Attach decorations to the section whose destruction controls
them. Cosmetic debris should be bounded and collision-free unless gameplay requires
authoritative debris. See [multiplayer](multiplayer.md) for collision revision gates.

## Materials audio and visual review

Record physical texture repeat size, color-space conventions, channel use, normal
orientation, and import settings. Check tiled seams, mipmaps, overdraw, and material
contrast in the target renderer. Inspect precision/compression and generated LODs
when independently simplified adjoining surfaces develop cracks; do not disable
these features globally without an observed reason.

Audio records should include author, source URL, license notice, original file,
and transformations. Verify loops and levels in engine. Separate buses by purpose,
stop loops during reset/teardown, and bound simultaneous voices/effects. Let launch
and impact tails survive short-lived projectile removal when needed. Prediction
and duplicate packets must not replay a sound twice.

Review actual imported assets in engine, from the gameplay camera and a useful
overview. Preserve player and HUD visibility for readability checks. Compare the
same cameras/settings before and after changes. Screenshots establish appearance;
playtests establish motion, handling, collision, and camera recovery.

Measure frame time, physics time, draw calls, primitives, and memory on representative
hardware and scenes. Include bursts of effects and multiplayer load. A single capped
FPS sample or a headless CPU timing is not a sustained graphical performance budget.
Polish materials and readable landmarks while preserving established route, cover,
and spawn constraints; validate a deliberate geometry change independently.
