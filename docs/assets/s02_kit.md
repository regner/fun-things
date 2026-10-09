# s02_kit — desktop camera/control blockout handoff

7 October 2026. Original Codex-authored technical fixtures for [S02](../spikes/s02.md),
following accepted Petrol & Coral, smooth broad forms and ordinary mixed-height
architecture. Regner owns feel/art ratification. No external model/texture/font is
incorporated. These are blockouts, not accepted production people, rigs or buildings.

## Source and consumers

One committed source: `prototypes/s02/art/source/models/spikes/s02_kit.blend`, excluded from Godot by
`art/source/.gdignore`. Each row exports its identically named `export_<asset>`
collection to `prototypes/s02/art/models/spikes/<asset>.glb` plus engine-saved `.glb.import`.
Exact members are in `prototypes/s02/tools/s02/export_members.json`; all nine outputs must accompany
source changes. `prototypes/s02/tools/s02/create_sources.py` is historical bootstrap tooling;
subsequent authoring belongs in the saved Blender source.

| Asset | Imported envelope / purpose | Original S02 linked consumers |
| --- | --- | --- |
| s02_ground | 64×0.2×64 m road, top Y=0; 4 m-wide visual walk strip, top Y=0.015 m | ground_prefab, corner, weapon_studies |
| s02_low | 8×6×8 m solid mass; 8.2 m roof overhang | low_prefab; WestCorner/EastCorner in corner |
| s02_near | 8×46×8 m solid mass; 8.2 m roof | near_prefab; NearTower in corner |
| s02_tall | 8×60×8 m solid mass; 8.2 m roof | tall_prefab; TallTower in corner |
| s02_actor | 1.8 m tall, 0.75 m jacket; asymmetric right aiming arm | actor; three linked instances in weapon_studies |
| s02_target | 0.75×1.8×0.4 m visible target | target_prefab; TargetClear/TargetBlocked in corner |
| s02_pistol | grip-origin body 0.18×0.18×0.42 m | actor WeaponMount; weapon_studies/pistol |
| s02_smg | 0.28×0.24×0.72 m body plus 0.3 m rear stock | weapon_studies/smg |
| s02_launcher | 0.38×0.36×1.1 m body plus 0.48 m rear bell | weapon_studies/launcher |

All scene paths above are under `prototypes/s02/tests/fixtures/s02/`. `corner_wide.tscn` inherits
corner and changes only the authored camera FOV. `focus_runner.tscn` instances corner.
The actor's production-style `PresentationAnchor/Visuals/Model` and static wrappers'
`Visuals/Model` retain GLB ancestry. Study-only assemblies are saved directly in
weapon_studies; they have no gameplay or collision. No imported child is editable.

### Accepted S03-R downstream consumers

The [accepted bounded S03-R experiment](../spikes/s03-r.md) adds consumers of this
unchanged source/export kit. The original table remains the initial S02 handoff;
the mappings below supplement it at accepted `ae48eb3`. They describe linked
technical fixtures, not new art, final camera/feel acceptance or production use.
Each source collection below belongs to `s02_kit.blend` and exports the matching
GLB plus `.glb.import` under `prototypes/s02/art/models/spikes/` as above.

| Source collection → export | S02 prefab / inherited ancestry | Accepted S03-R consumer in `boot.tscn` |
| --- | --- | --- |
| `export_s02_ground` → `s02_ground.glb` | [ground_prefab.tscn](../../prototypes/s02/tests/fixtures/s02/ground_prefab.tscn), `Visuals/Model` | `View/Match/CityRoot/Ground` |
| `export_s02_low` → `s02_low.glb` | [low_prefab.tscn](../../prototypes/s02/tests/fixtures/s02/low_prefab.tscn), `Visuals/Model` | `View/Match/CityRoot/WestCorner` and `EastCorner` |
| `export_s02_near` → `s02_near.glb` | [near_prefab.tscn](../../prototypes/s02/tests/fixtures/s02/near_prefab.tscn), `Visuals/Model` | `View/Match/CityRoot/NearTower` |
| `export_s02_tall` → `s02_tall.glb` | [tall_prefab.tscn](../../prototypes/s02/tests/fixtures/s02/tall_prefab.tscn), `Visuals/Model` | `View/Match/CityRoot/TallTower` |
| `export_s02_actor` → `s02_actor.glb` | [S02 actor.tscn](../../prototypes/s02/tests/fixtures/s02/actor.tscn), `PresentationAnchor/Visuals/Model` → [inherited S03-R actor.tscn](../../prototypes/s03_r/tests/fixtures/s03_r/actor.tscn) | `View/Match/Bodies/Host` and `Client` |
| `export_s02_pistol` → `s02_pistol.glb` | S02 actor, `PresentationAnchor/WeaponMount/Model` → inherited S03-R actor | Both bodies' linked pistol; source-derived `Sockets/Muzzle` supplies aim observation |

The saved [S03-R boot](../../prototypes/s03_r/tests/fixtures/s03_r/boot.tscn) inherits S03's boot
and owns these CityRoot placements and two dynamic body spawn poses. Actor/pistol
model ancestry, grip/muzzle transforms and collision derive from S02; S03-R adds
replica pose/presentation behavior without copying movement or imported geometry.
No S03-R target, SMG or launcher consumer is introduced by that saved composition.
The initial flat-ground S02 contract below remains offline; this later consumer
supplies only the separately bounded ENet result.

Future kit reexports must cover all nine shared-source outputs and inspect both
the original S02 consumers (including inherited camera/focus/study scenes) and
these accepted S03-R actor/boot consumers. Review model/socket/collision changes
through both bodies and all CityRoot instances, preserving source links, imports,
UIDs, inheritance, local overrides and authored placements. Follow
[reexport/change acceptance](../assets.md#reexport-and-change-acceptance), including
refresh/reopen of affected saved/inherited scenes before saves or playtests; a
headless import cannot synchronize an open editor. Dimension/socket/collision
changes also require affected motion/query and authoritative/network validation.
This docs-only discovery changes no source, export, prefab or scene; the original
82-path S03-R preservation evidence and closed resync P2 remain historical accepted
receipts. Full S02/S03-R, drawn response/remote continuity/prediction-if-warranted,
physical input/native focus/human feel, Steam/Deck and P0/production gates stay open.

## Authoring and runtime contracts

Metres, Blender Metric scale1, +Z up/+Y front maps once to Godot +Y up/-Z forward.
Static rotation/scale applied, positive unit scales, baked bevels/triangulation,
smooth normals. Building origins at ground-centred footprints; road top at Y=0;
actor origin between feet. Imported bounds tolerance0.001 m. No rigs, animations,
textures, external libraries, LOD study, mesh VFX or compression extensions.

Blender **5.2.2 LTS d13f752e3b9c**, bundled glTF exporter **5.2.40**; Godot
**4.8.dev7.official.c971f93e7**, unchanged engine pin. Explicit export uses S01's
recorded `prototypes/s01/tools/s01/export_settings.json` with animations disabled and a declared
collection per output; `prototypes/s02/tools/s02/export.py` checks members and transforms.
`prototypes/s02/tools/s02/reexport.py` rejects non-identical GLBs, embedded images and extensions.
Its narrow known diagnostic is the missing optional MeshOptimizer library; actual
exports contain no compression extension. Full logs and hashes accompany S02.

Flat source materials use sRGB art swatches converted to linear shader values;
roughness0.8. Godot default per-asset import settings are retained in sidecars.
Historically, buildings used per-instance ShaderMaterials with a 30 px actor
cutaway. The owner removed that treatment; current fixtures retain the imported
palette and unchanged collision without a cutaway. See
[the current S02 controls record](../spikes/s02-controls.md). No shared imported
material is mutated.

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

## Accepted partial S06 reverse consumers

The original S02 and accepted S03-R maps above are preserved. Subsequent
[partial S06 exact7fb302b](../spikes/s06.md#accepted-exact-final-disposition) adds
linked technical consumers of unchanged `s02_kit.blend` outputs:

| Source collection → GLB/import | Preserved prefab-local ancestry | Saved S06 consumer |
| --- | --- | --- |
| `export_s02_actor` → `s02_actor.glb` + `.glb.import` | [S02 actor](../../prototypes/s02/tests/fixtures/s02/actor.tscn), `PresentationAnchor/Visuals/Model` | [intersection](../../prototypes/s06/tests/fixtures/s06/intersection.tscn)/`Person`, inherited by [intersection_wide](../../prototypes/s06/tests/fixtures/s06/intersection_wide.tscn) |
| `export_s02_pistol` → `s02_pistol.glb` + `.glb.import` | Same actor, `PresentationAnchor/WeaponMount/Model`; preserved `Sockets/Muzzle` | Same Person and inherited wide consumer |

S06 introduces no ground/building/target/SMG/launcher consumer from this kit. The
[new intersection handoff](../spikes/s06-source-handoff.md) owns separate road sources;
ONE [contract](../spikes/s06-contracts.md) bounds host commands through unchanged
`step`/`motion_state`/`neutralize`. Actual capsule radius0.38 m/height1.8 m crosses
west→east in477 ticks/7.95 s, one X=0 seam/no sampled outside/contact. This is planar
technical evidence, not final actor/camera/weapon/readability/feel, contested crossing
or production art. Future shared-source reexports still cover all nine outputs and
all original/S03-R/**S06 base and inherited** consumers; changed envelopes/sockets
require affected actual motion/query/contact/seam/map and network checks under their
owners. No source/import/UID/prefab/placement changed here; no reexport ran. Full
S02/S06/Steam/Deck/feel/P0/M1/production gates remain open.
