# s02_kit — desktop camera/control blockout handoff

7 October 2026. Original Codex-authored technical fixtures for [S02](../spikes/s02.md),
following accepted Petrol & Coral, smooth broad forms and ordinary mixed-height
architecture. Regner owns feel/art ratification. No external model/texture/font is
incorporated. These are blockouts, not accepted production people, rigs or buildings.

## Source and consumers

One committed source: `art/source/models/spikes/s02_kit.blend`, excluded from Godot by
`art/source/.gdignore`. Each row exports its identically named `export_<asset>`
collection to `art/models/spikes/<asset>.glb` plus engine-saved `.glb.import`.
Exact members are in `tools/s02/export_members.json`; all nine outputs must accompany
source changes. `tools/s02/create_sources.py` is historical bootstrap tooling;
subsequent authoring belongs in the saved Blender source.

| Asset | Imported envelope / purpose | Linked consumers |
| --- | --- | --- |
| s02_ground | 64×0.2×64 m road, top Y=0; 4 m-wide flush visual walk strip | ground_prefab, corner, weapon_studies |
| s02_low | 8×6×8 m solid mass; 8.2 m roof overhang | low_prefab; WestCorner/EastCorner in corner |
| s02_near | 8×46×8 m solid mass; 8.2 m roof | near_prefab; NearTower in corner |
| s02_tall | 8×60×8 m solid mass; 8.2 m roof | tall_prefab; TallTower in corner |
| s02_actor | 1.8 m tall, 0.75 m jacket; asymmetric right aiming arm | actor; three linked instances in weapon_studies |
| s02_target | 0.75×1.8×0.4 m visible target | target_prefab; TargetClear/TargetBlocked in corner |
| s02_pistol | grip-origin body 0.18×0.18×0.42 m | actor WeaponMount; weapon_studies/pistol |
| s02_smg | 0.28×0.24×0.72 m body plus 0.3 m rear stock | weapon_studies/smg |
| s02_launcher | 0.38×0.36×1.1 m body plus 0.48 m rear bell | weapon_studies/launcher |

All scene paths above are under `tests/fixtures/s02/`. `corner_wide.tscn` inherits
corner and changes only the authored camera FOV. `focus_runner.tscn` instances corner.
The actor's production-style `PresentationAnchor/Visuals/Model` and static wrappers'
`Visuals/Model` retain GLB ancestry. Study-only assemblies are saved directly in
weapon_studies; they have no gameplay or collision. No imported child is editable.

## Authoring and runtime contracts

Metres, Blender Metric scale1, +Z up/+Y front maps once to Godot +Y up/-Z forward.
Static rotation/scale applied, positive unit scales, baked bevels/triangulation,
smooth normals. Building origins at ground-centred footprints; road top at Y=0;
actor origin between feet. Imported bounds tolerance0.001 m. No rigs, animations,
textures, external libraries, LOD study, mesh VFX or compression extensions.

Blender **5.2.2 LTS d13f752e3b9c**, bundled glTF exporter **5.2.40**; Godot
**4.8.dev7.official.c971f93e7**, unchanged engine pin. Explicit export uses S01's
recorded `tools/s01/export_settings.json` with animations disabled and a declared
collection per output; `tools/s02/export.py` checks members and transforms.
`tools/s02/reexport.py` rejects non-identical GLBs, embedded images and extensions.
Its narrow known diagnostic is the missing optional MeshOptimizer library; actual
exports contain no compression extension. Full logs and hashes accompany S02.

Flat source materials use sRGB art swatches converted to linear shader values;
roughness0.8. Godot default per-asset import settings are retained in sidecars.
Buildings use per-instance ShaderMaterials reading the imported palette, with a
30 px actor cutaway. This presentation treatment copies no vertices and changes
no collision. Its abrupt circular edge and impact on shadows need user visual review.
No shared imported material is mutated. Costs are unmeasured.

`socket_grip` is authored at (0.43,1.2,-0.6) in imported actor space. The pistol's
`socket_muzzle_s02_pistol` is (0,0,-0.42) relative to the grip. Editor integration
copies source transforms into saved `PresentationAnchor/WeaponMount` and
`Sockets/Muzzle`; actual physics-local muzzle is (0.43,1.2,-1.02), -Z forward.
The SMG/launcher are held-silhouette studies only, with their own source muzzle
markers. They do not implement firing, equipment or combat behavior.

Collision is deliberate and separate: building boxes8×height×8, road box64×0.2×64,
actor/target capsule radius0.38 m and height1.8 m. World bit1, Actor bit2; motion
and ray masks include both. Collider does not encompass the extended arm/gun;
centre-to-muzzle queries block shooting through a wall. This flat-ground candidate
has no gravity, curb/step/slope acceptance, vehicles, health or networking.

## Handoff status

Source/export and prefab/placement checks are bounded S02 evidence, linked from the
spike. Authoring/source/technical integration/world owner: this S02 Codex workstream.
Independent art and code reviewer identities/revisions are recorded in the spike's
review receipts. Production art, shared rig/clips, combat, whole-district obstruction,
Deck/Windows exports and user feel remain pending with existing tasks.

Native-view captures show the launcher length clearly, but pistol/SMG recognition
is still weak at this scale. Do not read a larger side-profile concept as overhead
acceptance. The next refinement should compare geometry/contrast in matched held
views and retain actor/target readability while walking, before production assets.
