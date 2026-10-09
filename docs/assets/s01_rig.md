# s01_rig — technical asset handoff

Spike-only two-bone skinned fixture; not a production human/shared pedestrian rig.
[S01](../spikes/s01.md) owns exact tools, settings, hashes, logs and evidence;
[workflow](../assets.md) and [scene contract](../scene-structure.md) own policy.
Codex produces and technically reviews source, neutral concept, rig/animation,
export/import, material integration and saved fixture placement. Regner's accepted
art/city brief informs axes/palette, without claiming production art review.
Original project-owned source, no third-party model/library/image dependencies.

## Brief and mapping

Purpose: prove skin binds, in-place action names/loops, authored bone socket motion,
metres, ground pivot and repeated linked imports. Comparison tolerance 0.0001 m;
Skin AABB min (-0.375,0,-0.2), size (0.975,1.6,0.4), root identity at ground.
Off-centre arm is intentional; this is a mechanical fixture, not the brief's 1.8 m
person. Collision and actor clearances are not applicable. No shader/motion changes
move a physics or placement root.

| Source | Collection/root/members | Output/settings | Consumers |
| --- | --- | --- | --- |
| `prototypes/s01/art/source/models/spikes/s01_rig.blend`; no linked library | `export_s01_rig`; synthetic GLB root; Rig, Skin, socket_grip | `prototypes/s01/art/models/spikes/s01_rig.glb`, `.glb.import`; preset in `prototypes/s01/tools/s01/export_settings.json` | `prototypes/s01/tests/fixtures/s01/rig_prefab.tscn`; RigA/RigB in saved `roundtrip.tscn` |

Skin slot `body_paint` remaps through the import sidecar to shared external
`prototypes/s01/art/materials/s01_petrol.tres` and
`prototypes/s01/art/textures/spikes/s01_palette.png`, whose
editable source belongs to s01_static's record. Normalized smooth normals,
triangulated bevel geometry and default cube UVs; no embedded textures, automatic
LOD, production material/triangle budget, normal/ORM maps, alpha or effects.

## Rig, socket and clips

Blender +Z up/+Y forward; Godot +Y up/-Z forward, unit positive scale. Establish
rest transforms before binding. Bones: `root` at ground to 1 m, `hand` parent=root
at (0.5,1,0) to (0.5,1.6,0) in Godot. Root hierarchy and names are compatibility
inputs; each vertex has one weight, two skin binds, armature modifier retained.
No retargeting or human anatomical/animation quality is certified.

`socket_grip` is parented to Blender hand bone, local position (0,0,-0.15), local
X rotation -90° to cancel the bone-axis frame. Imported
`Visuals/Model/Rig/Skeleton3D/hand/socket_grip` is under BoneAttachment3D hand;
rest pose relative to model is (0.5,1.6,-0.15), identity basis/-Z forward. Tests
sample run and confirm movement >0.1 m without moving the saved wrapper.
There is no weapon/gameplay socket consumer; production wrappers must adapt this
source-derived transform to their required API without an independent pose copy.

| Clip | Source association/range | Imported duration | Contract |
| --- | --- | --- | --- |
| idle | Slotted action and muted named NLA track, frames 1–31/30 fps | 1.0333333 s | LOOP_LINEAR, matching endpoints |
| walk | Same | 1.0333333 s | LOOP_LINEAR, matching endpoints |
| run | Same | 1.0333333 s | LOOP_LINEAR, matching endpoints |
| death | Same | 1.0333333 s | LOOP_NONE, hold final pose after end |

These are tiny hand-rotation proof motions, not finished idle/walk/run/death art.
Sampling/export optimization settings and the import's inclusive terminal sample
are recorded in S01. Animation touches model descendants only. Rest bounds and
attachment motion are measured; production animated bounds/culling margins await
actual animation and S07 evidence. No collision, effect or navigation data exists.

## Handoffs, 7 October 2026

Final revision is the source/export fingerprint in S01 evidence; files and metadata
are delivered together. Codex → Codex is the producer → technical reviewer for
all applicable stages; no independent reviewer or Regner production acceptance.

| Stage | Status/scope | Evidence/findings |
| --- | --- | --- |
| Brief | accepted, technical-only | Two-bone scope, dimensions/tolerance, names/loops, source linkage |
| Concept | accepted, neutral fixture-only | Body/arm boxes establish an unambiguous skin/attachment test |
| Blender blockout | accepted, resource-only | Unit roots, source/export, weights/binds/bounds; no actual actor movement gate |
| Production asset | not applicable | No person rig/outfit/finished animation acceptance |
| Export/import | accepted, asset profile | Four exact clips, sampled seams/final pose, corrected source socket basis, material remap, clean import/editor roundtrip |
| Prefab | accepted, fixture-only | Linked imported model at Visuals/Model; stable wrapper IDs, no copied mesh or gameplay body |
| Placement | accepted, fixture-only | Two distinct IDs/authored transforms, shared imported mesh, save/close/reopen and unchanged persisted files |

First socket export retained a 90° bone-frame rotation; Codex corrected Blender
source and re-exported rather than introducing corrective Godot root transforms.
The same source subsequently re-exported byte-identically. Full-project plugin and
editor progress diagnostics remain in S01; Deck, engine changes, gameplay and
multiplayer are deferred. Future shared-person work must pass rest/pose/bounds,
variant compatibility, actual actor movement and production art review separately.
