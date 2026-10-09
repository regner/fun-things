# Concept, asset and world workflow

Keep editable sources, explicit exports, imported model instances, reusable prefabs
and saved world placement connected. This is the P0-05 specification, refined by
the bounded [S01 proof](spikes/s01.md); it is not production asset acceptance.
The [product brief](design.md) owns scope;
[repository guidance](../AGENTS.md), [development](development.md) and
[multiplayer](multiplayer.md) own editing, validation and authority rules.
The [P0-05 record](decisions/p0-05-asset-workflow.md) lists unresolved inputs and proofs.

The P0-02 [scene contract](scene-structure.md) reserves source/export/prefab paths,
required sockets, stable placed-object IDs and inherited overrides. The
[ownership draft](architecture.md) separates saved placement from runtime state;
[API contracts](api-contracts.md) defines clearance and stale-derived-data failures.
The accepted [art direction](art-direction.md) and [world layout](world-layout.md)
own the Petrol & Coral starting kit, vertical perspective camera and provisional
city/asset dimensions. Use those inputs in asset briefs; do not choose competing
paths, gameplay rules or visual directions here. Spikes refine the drafts before
production. [S01](spikes/s01.md) selects Blender 5.2.2 LTS / glTF exporter 5.2.40
and records exact export/import settings on the existing Godot 4.8-dev7 pin.
The [S01-W supplement](spikes/s01-w.md) reproduces both S01 GLBs byte-for-byte with
the Windows Blender 5.2.2 LTS build, so the existing strict byte comparison remains
the cross-platform check; future Blender or exporter changes require fresh evidence.
That asset-profile proof does not certify full-project plugin or Deck compatibility.

## Owners and handoffs

For requested art/asset handoff reviews, use the project
[`art-review` skill](../.agents/skills/art-review/SKILL.md). It traces these contracts
and reports observed defects separately from missing gameplay/device evidence;
review does not replace the acceptance checks below.

Assign a named person/agent to each applicable role in the asset's
[handoff record](templates/asset-handoff.md) before work. Codex initially owns the
brief, concept preparation, Blender source, technical integration, gameplay review
and world integration; Regner owns the P0-04 direction/layout selection. One person
may fill several roles, but record who produced and who accepted each handoff.
One integrator owns each shared world scene; contributors own distinct files.
Review does not require a second agent, and silence is not acceptance.

| Handoff | Producing owner → accepting owner | Required acceptance evidence | Rejection path |
| --- | --- | --- | --- |
| 1. Brief | Gameplay designer → gameplay reviewer; art reviewer checks style requirements | Asset ID, purpose, owning design references, dimensions/clearance, collision envelope, camera conditions, variants, sockets and required states; missing decisions explicitly assigned | Return to brief owner for measurable constraints or a smaller spike brief; no detailed modeling on guessed requirements |
| 2. Concept | Concept artist → art reviewer; Regner selects the P0-04 direction | Original silhouette sheet and gameplay-camera reference, selected option/date, provenance/license, link to chosen art/layout direction and brief | Return to concept owner with silhouette/style/layout findings; reopen direction with Regner if the brief cannot be met |
| 3. Blender blockout | Blender artist → gameplay reviewer and technical integrator | Committed source, named export collection, measured scale/pivots/sockets, linked GLB fixture; camera and actual movement/turn/clearance observations | Geometry/origin/export faults return to Blender owner; infeasible clearances return to brief/layout owner before detail work |
| 4. Production asset | Blender artist → art reviewer and technical integrator | Model/rig/clips/materials/textures against accepted concept; slot/bone/socket lists, dimensions/bounds, density and LOD rationale, provenance, camera previews | Return to source owner with named defects; changed gameplay envelope also reopens blockout review |
| 5. Export/import | Technical integrator, with Blender owner exporting → technical reviewer | Complete source/output mapping, exact tools/settings, `.import` metadata, imported scale/front/normals/bounds/clips/sockets and dependency checks; clean import plus existing-editor results | Export faults return to Blender owner; import/remap faults stay with integrator; hold prior accepted outputs until replacement passes |
| 6. Prefab | Prefab integrator → gameplay reviewer and art reviewer | Linked model instance, intentional collision/components, stable paths/IDs, fixed gameplay/overview views, motion/collision checks, save/reopen including inherited variants and overrides | Wrapper/collision faults return to prefab owner; model faults return upstream; a screenshot alone cannot accept gameplay |
| 7. Placement | World integrator → gameplay reviewer and art reviewer | Accepted prefab instances in saved sectors, preserved transforms/IDs, routes/spawns/boundaries/seams, refreshed dependent data, save/reopen, playtest and relevant profile/logs | Placement/data faults return to world integrator; prefab/clearance faults reopen the earlier handoff; leave rejected work out of accepted sectors |

Each stage has status `pending`, `accepted` or `rejected`, reviewer/date, source
revision, evidence links and findings. Acceptance states its scope: spike-only
or production. A deliberately neutral spike fixture can use its own concept/brief
without claiming P0-04 art approval; detailed production uses the chosen direction.
Record `not applicable` with a reason for unused rigs, sockets, textures or LODs.
Missing evidence stays pending. Rejection records location, observation, impact,
expected result, fix owner and retest; dependent downstream acceptance becomes pending.
Recheck the affected gates and changed consumers.

## Files, catalogue and provenance

Use lowercase `snake_case` filenames and a stable descriptive asset ID, such as
`car_compact_a`. The ID identifies a content family, not a runtime entity or placed
world object. A compatible reexport keeps it; an incompatible replacement gets a
new ID unless all consumers migrate together. Routine revisions keep runtime paths.

Create directories as assets arrive. Production models use one stable type directory
under their family: `art/models/weapons/<type_name>/`,
`art/models/vehicles/<type_name>/`, `art/models/characters/<type_name>/`, or
`art/models/effects/<type_name>/`. Mirror the same family/type path under
`art/source/models/` and, when asset-specific, under `art/animations/`,
`art/materials/`, and `art/textures/`. Runtime filenames may retain a versioned asset
ID inside that type directory. Foundation spike assets live under [`prototypes/<spike_id>/art/`](../prototypes/README.md),
outside Godot's scan. Do not mix archived spike art into production type directories.

```text
art/
  source/
    .gdignore                         # committed, empty; covers this subtree
    models/<family>/<type_name>/<asset_id>.blend
    textures/<family>/<type_name>/    # editable originals/bake sources
  models/<family>/<type_name>/<asset_id>.glb
  animations/<family>/<type_name>/
  textures/<family>/<type_name>/      # runtime PNGs and their .import files
  materials/<family>/<type_name>/
scenes/
  prefabs/<family>/<asset_id>.tscn      # static kit model + components
  entities/<entity_type>.tscn          # dynamic actor/vehicle/projectile wrappers
  effects/<effect_id>.tscn             # bounded cosmetic imported mesh effects
  world/sectors/<sector_id>.tscn       # authored instance placement
docs/                                 # at the repository root
  asset-catalogue.md                   # ID → handoff record index
  assets/<asset_id>.md                 # filled brief/spec/review record
```

### Tracked art inventory — production cleanup, 9 October 2026

This family-level table classifies all **184** tracked files under `art/` after the
production cleanup. The cleanup used direct filesystem moves because no editor/MCP
session was available; import and dependency checks validate the saved result.
Historical review receipts remain discoverable in Git history rather than under
`art/`.

| Files | Count | Classification | Current referrers / reason retained |
| --- | ---: | --- | --- |
| `models/source models/vehicles/{car_crate_a,car_latch_a,car_sable_a}` | 9 | Production asset | Vehicle prefabs, definitions, asset tools and car handoffs |
| `models/source models/weapons/{pistol_coral_stub,smg_wedgewire,dock_thumper}` | 16 | Production asset | Weapon/projectile prefabs, player weapon profiles and handoffs |
| `models/source models/characters/coral_courier` | 5 | Production asset | Player prefab, rig checks and player handoff |
| Character model/source/animation/material type directories for `pedestrian_worker` and `shared_humanoid` | 18 | Production asset | Pedestrian/player prefabs, shared motion libraries and handoffs |
| Effect model/source/material files in `effects/weapon_effects` | 30 | Production asset | Saved muzzle, hit, trail and explosion scenes |
| `models/source models/brackett_greybox` | 105 | Greybox | Saved world/prefab composition and greybox export tooling |
| `source/.gdignore` | 1 | Source-tree configuration | Godot import/export exclusion |

No review/concept-only or unreferenced art remains in the tracked `art/` tree. Pure
concept images for completed assets were removed from `docs/concepts/`; concepts for
unbuilt vehicles, UI, world/district work, and other pending assets remain in `docs/`.

Put all `.blend` and editable texture sources under `art/source/` with its
`.gdignore` in place before adding sources. Keep runtime GLBs/textures outside it.
Godot ignores that subtree for import and project export; see the
[import process](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/import_process.html).
S08 also inspects packaged contents: external copying/build scripts must not bundle
sources, scratch outputs or review evidence. Git still tracks authoring sources.
Commit needed linked Blender libraries/images; avoid machine-local absolute paths.

Add each asset to the [catalogue](asset-catalogue.md) when brief work starts, using
the handoff template. Its record owns the mapping from every source/export collection
to every GLB/texture, import sidecar, material, prefab/inherited variant and affected
sector. Shared sources list **all** component outputs and dependents; shared
materials/textures list consumers. Link shared rig/material records rather than
copy their details. Check reverse dependencies with repository searches and the
editor, since the manual list can become stale. Production asset tools mirror the art layout
under `tools/assets/<family>/<type_name>/`; each handoff records its safe check and reexport
entrypoints. Foundation S01 tools and their exact historical contracts are archived under
`prototypes/s01/` and are not current production automation. Gameplay-derived
navigation/minimap data requires the scene contract's bake fingerprint from first
use; that content-handshake requirement is separate from catalogue automation.

Record original authorship or source URL, creator, license/attribution, permitted
transformations and selected concept. Concept images, including generated concepts,
are references; they do not satisfy Blender model provenance. External fonts,
textures and audio require the same trail. Keep notices with sources and arrange
required runtime attribution. Unknown rights reject the handoff.

## Units, axes, origins and export scope

Use metres: Blender unit system Metric, unit scale 1, with a 1 m measurement fixture.
Record dimensions as width X, height Y, length Z in imported Godot local space,
plus AABB minimum/maximum relative to the origin. The brief records numerical
acceptance tolerances before testing; exact gameplay dimensions await their spikes.

Godot is +Y up. **This project deliberately uses local -Z forward** for oriented
models and gameplay roots, +X right. Author these assets facing Blender +Y with +Z
up; glTF Y-up conversion maps that front to Godot -Z. For world-aligned kits,
Godot +X is east, -Z north; mark connector directions in the brief. The usual
Godot/glTF oriented-model front is +Z (Blender -Y), so this is a project exception,
not the engine default. See [Godot model export considerations](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html).
S01 verifies an asymmetric front/right/up fixture, socket directions and a rig.
Apply axis conversion once; do not hide mismatches with ad hoc prefab rotations
or corrective root scale. No existing asset is migrated by this specification.

| Family | Origin/pivot contract |
| --- | --- |
| Buildings/ordinary props | Ground-centred footprint at Y=0; record asymmetric footprint offsets and facade front |
| Roads/sidewalk modules | Surface datum and documented grid anchor; connector positions/tangents and curb height shared by compatible pieces |
| Vehicles | Ground-centred footprint under body; wheel centres/axes and seat/exit markers relative to this visual origin; gameplay separately owns physics centre of mass |
| People | Ground between feet in rest pose; shared rig root and bind pose consistent across variants |
| Weapons | Grip attachment pivot; muzzle points -Z in its own local space |
| Moving parts/VFX carriers | Actual hinge/axle/emission pivot; documented offsets, rest orientation and maximum animated/effect extent |

Apply static object rotation/scale before export; model roots have unit scale and
no negative scale. Preserve documented local translations for wheels, hinges and
sockets. Establish rig transforms before binding; do not blindly apply transforms
to a skinned rig. Check rest/bind alignment, mirrored winding, normals, triangulation,
tangents where used, and bounds in Godot. Compare a dimensional reference and
front/up markers rather than accepting an apparently plausible view.

Each output has a Blender collection `export_<asset_id>` and a recorded export
root. Export only its declared members/dependencies: render geometry, required
armature/clips and approved markers. Studio cameras/lights, reference images,
backup meshes and unrelated collections stay out. Record member names, modifier
evaluation, triangulation and selection/collection filter settings; saved selection
alone is insufficient. Do not use collision/node-type import suffixes without an
explicit reviewed mapping. Gameplay collision belongs to the prefab. S01 proves
exact exporter options; option names are not assumed portable across Blender versions.

## Sockets, rigs and animations

A socket entry names its owner, stable name/path, parent or bone, rest transform
in metres, local forward/up axes and consumer. Static markers are named Blender
empties included in the export; check they survive import. Bone-mounted attachments
record bone/offset and use the appropriate prefab bone attachment; prove animation
in S01. Gameplay consumes the socket; a marker does not decide outcomes.

Starting names are `socket_grip`, `socket_muzzle`, `socket_driver`,
`socket_entry_left`, `socket_entry_right`, `socket_exit_left` and
`socket_exit_right`, only when the brief needs them.
The [scene contract](scene-structure.md#prefab-and-entity-interfaces) owns the stable
prefab-facing paths: `Sockets/WeaponMount`, `Sockets/Muzzle`, `Sockets/DriverSeat`,
`Sockets/EntryLeft`, `Sockets/EntryRight`, `Sockets/ExitLeft` and `Sockets/ExitRight`
as applicable. Record mappings from source markers/bones to these paths; do not
expose arbitrary imported hierarchy to every caller. Any adapter relays the authored
transform, not a competing hand-tuned copy. Entry/exit markers suggest candidates;
authoritative vehicle interaction still checks clearance. Gameplay queries use the physics pose and authored socket-relative
transform, never the smoothed PresentationAnchor transform. Weapon visual mounts
follow presentation while the gameplay muzzle query follows physics.

Use one shared person rig for player/pedestrian variants. Record bone names/hierarchy,
rest pose, skin mapping, weights/influence limit and attachment bones. Bone rename,
removal or rest-pose change is incompatible: review all skins, clips, attachments
and prefab consumers together. Retargeting is not assumed; variants pass the same
pose/clip checks.

Starting person clips are exactly `idle`, `walk`, `run`, `death`. Idle/walk/run
loop; S01 confirms exported naming/loop behavior. Death is a one-shot retaining its
final pose until lifecycle presentation removes it. Record exported name, frame range, source frame rate, duration,
loop/import settings and applicable rig. Additional clips come from the brief.
Locomotion is in place: animation cannot translate the simulation root or trigger
damage, seat ownership or authoritative death. Gameplay selects presentation.

Action/NLA export depends on Blender version/mode. List intended clips and inspect
imported names, durations and loop seams. The [Blender glTF manual](https://docs.blender.org/manual/en/5.1/addons/import_export/scene_gltf2.html)
describes action association/export modes, but is not our version pin. S01 records
the selected version's action/slot/NLA setup and sampling settings. Do not assume
every action datablock exports or accept unintended rest/test clips.

## Materials and textures

Material slot names/order are part of the contract. Use descriptive stable names,
such as `body_paint`, `glass`, `tire`, `sign_face`; the brief chooses actual slots.
Share external Godot `.tres` materials where appropriate. Record slot → material
mapping and intentional variant overrides. Blender owns geometry/UVs/slot assignments;
the material owner owns Godot shaders/tuning. Remap through saved import settings
or documented prefab overrides, never disposable cache edits. Godot supports
external material remapping in [import configuration](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html).

Start with opaque flat colors or a shared palette where they meet the chosen art
direction. For textures, record editable source, runtime path, resolution, UV set,
physical tile size in metres and channels. Runtime filenames use
`<material_id>_albedo.png`, `_normal.png`, `_orm.png`, `_emission.png` as applicable:
albedo/emission are color data (sRGB), normals/ORM linear data; ORM is red occlusion,
green roughness, blue metallic. Use tangent-space +Y/OpenGL normal maps; record
conversion and test orientation. These conventions do not require adding all maps.

Use explicit external runtime textures for shared materials. Embedded GLB textures
must be listed with their import/extraction mapping and justified; do not maintain
silently diverging copies. Bake unsupported procedural material features to committed
textures or implement intentional Godot shader behavior. Record filtering/repeat,
mipmaps, compression, alpha mode/cutoff, normal handling and emission settings.
S01 chooses defaults; exceptions need observed evidence. Review seams, UV density,
mip shimmer, contrast and normals in the target renderer. Transparent layers/VFX
need overdraw/readability checks. S07 establishes measured limits; no texture-size
or triangle budget is ratified here.

## Collision envelopes, bounds and LOD

Decoration and gameplay collision have separate owners. The brief records visual
footprint, intended solid regions, collider bounds, clearance envelope, ground contact,
sockets and decorative overhang. A visual pivot is not a physics centre of mass.
Use simple shapes when sufficient, reviewed convex collision for moving bodies and
deliberate static surface collision. Gameplay owns layers/masks. Decorative imports
do not automatically create collision, navigation or interaction authority.

Test actual movement/query APIs: actor fit, car turning/braking, corners, curbs/slopes,
module seams, spawn/exit clearance and boundaries. Avoid duplicate coplanar ground
colliders, decorative snag points and gaps under routes. Blockout can use a named
provisional envelope; production requires S02/S04/S06 envelopes and evidence.
Screenshots prove neither movement nor multiplayer collision transitions.

Record rest/animated bounds, effect travel/particle bounds and culling margins with
units/rationale. Review death poses, wheels, explosions and camera-edge visibility.
Off-camera cosmetic culling must not stop simulation or chains. Shaders/particles
may animate imported Blender geometry; particle draw meshes and cosmetic mesh debris
also need committed Blender sources. No primitive/CSG/generated render meshes or
copied vertex data in owned scenes, except for the road-infrastructure rule below.
Collision shapes, navigation, occluder data, debug overlays and 2D UI/minimap drawing
are separate concerns.

### Generated road infrastructure exception

Owner decision 42 (9 October 2026) records the intent: the Blender-only rule exists to
stop composing scenes from code. Procedurally generated road infrastructure that is
edited and visible in the editor is acceptable, because it keeps ordinary road edits in
Godot instead of a Blender round trip.

Road, sidewalk, curb, procedural-intersection and crosswalk-marking surfaces may be
generated from the saved road network by the pinned road addon and project road
scripts, both in the editor and at level load. Their committed materials and textures
remain source assets. This exception does not permit procedural composition of
unrelated authored scenes or models.

Reusable visible fixtures remain Blender-authored linked assets: traffic signals,
street lights, signs, barriers and common prefab intersection pieces. The road tool may
place those fixtures from saved road metadata, but a road edit must not require a Blender
round trip. All other visible 3D models keep the Blender-only source/export contract.
Runtime code still must not compose authored scene hierarchies.

LOD is optional until measured. Record automatic import LOD settings or explicit
Blender LOD collections/outputs, transition conditions and inspected views. Godot
provides automatic [mesh LOD](https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html);
check silhouettes, normals, roofs, road/sidewalk seams and shadows at actual camera
distances. LOD changes visuals, never collision/topology. Do not disable simplification
or compression globally to solve one crack; record an asset-specific exception.
Start with loaded saved sectors; streaming needs measured justification.

## Prefabs and authored placement

Create one reusable prefab per building/asset type. Its gameplay root owns deliberate
components/collision and instances the GLB at `Visuals/Model` for static kit or
`PresentationAnchor/Visuals/Model` for actors/vehicles. Follow the scene contract's
required components/sockets and direct physics-body CollisionShape3D children;
S02/S04 select the body types. Keep imports linked. Editable children are only for
recorded overrides;
do not copy imported vertex data into owned `.tscn`/`.tres` files. Trace each visual
from placed instance → prefab → GLB import → catalogue record → committed `.blend`;
the catalogue retains the authoring source link without importing `.blend` directly.
Derived prefabs may inherit a wrapper for intentional variants. On the current
pin, use exported wrapper-level appearance parameters: S01 proves they preserve
saved identities through reexport. Direct imported-child overrides changed a saved
child `unique_id` in S01 and remain rejected for identity-sensitive variants.
Keep imported children noneditable for the accepted route; presentation may apply
the authored material parameter to the linked mesh, without copying geometry or
changing placement. Production consumers still review their own appearance API.
Save/reopen wrappers
and inherited variants after reexport; compare paths, ancestry, material/component overrides and
identities. Unexpected embedded mesh data rejects review.

District/sector scenes own placements and repeated prefab instances. Plans, layout
JSON and Blender references guide authoring/testing; they are not a second placement
writer. Runtime may spawn entities/effects and restore dynamic state, but cannot
rebuild the city or reset authored transforms. Procedural layout is deferred by the
brief and requires an explicit product/ownership decision.

Preserve scene/resource UIDs, dependency UIDs, required `.uid` sidecars, import
settings, editor node/inheritance identities, prefab paths and overrides. Stable
world/gameplay IDs differ from asset IDs and peer-local instance IDs; art replacement
or reparenting preserves placed-object identities. Gameplay owns collision/lifecycle
revisions and authoritative destruction. Decorations follow their destructible section;
cosmetic debris is bounded and collision-free unless gameplay explicitly requires
authoritative debris. See [multiplayer collision ordering](multiplayer.md#message-ordering-and-state-revisions).

Placement review checks connectors, continuous sidewalks/crossings, turning loops,
alternate routes, spawn/exit clearance and boundaries. Refresh affected route,
navigation, minimap and occluder data and its owning revision when a placement/envelope
changes. Derived data records district ID, topology revision, geometry/anchor
fingerprint and bake-tool version under the scene contract. Stale/missing data fails
editor validation and play/join with `CONTENT_INVALID`; do not silently rebake at
runtime. S06 chooses representation/fingerprint details. Do not rebake unrelated
data or invent a second road layout. Preserve
unaffected transforms/IDs; intentional placement changes have a reviewed diff.
Save/reopen sectors before testing.

## Reexport and change acceptance

Source changes and affected outputs/consumers form one reviewable change. An art-only
change may leave prefab/sector files byte-identical, but affected instances still need
inspection and recorded validation. Do not force serialization changes to show review.

1. Identify the owner; inspect source, all mapped outputs/materials, direct/inherited
   prefabs, placed instances and callers. Record appearance-only versus dimension,
   origin, slot, bone, socket, collision or ID changes. List dependent gates/data to
   revalidate. Preserve unsaved editor work first.
2. Save source with recorded Blender version/settings; export all affected collections
   and shared-source component outputs into ignored scratch space. Check membership,
   dimensions, names and clips before replacing accepted GLBs/textures. Export failures
   leave accepted outputs intact.
3. Replace affected outputs together. Preserve `.import` metadata/resource identities;
   intentionally change settings in the pinned Godot editor. Refresh external files
   and reload/reopen affected scenes in any open editor before saves/playtests.
   A headless import does not synchronize an open scene. Prefer suitable Godot MCP
   tools for editor-managed mutations.
4. Check imported axes, normals, slots, rig/clips, sockets and bounds; compare inherited
   prefab paths/overrides and sector transforms/IDs. Save mutation batches; review
   saved diffs and save/reopen inherited scenes. For S01/toolchain changes, establish
   clean-cache reproducibility in an isolated checkout, preserving active editor work.
5. Revalidate affected camera, motion, clearance and derived-data cases. Collision or
   socket/envelope changes also need affected authoritative/offline/prediction rules
   and real-process multiplayer checks. Art-only changes need relevant visual/resource/
   performance checks. Review logs/status; compare fixed cameras/settings.
6. Update catalogue mappings, measurements, consumers and acceptance/evidence. Commit
   source, exports, changed materials, import/UID metadata, affected prefab/sector/data
   edits and records together. Keep `.godot/`, local tools/builds and credentials out
   of Git. No stale dependent output from a changed source can remain accepted.

Failures return to the table's fix owner and leave dependent work pending. Fix forward
within the complete change or restore source, outputs, settings and dependent edits
together to the last accepted revision; preserve unrelated user work. Renaming/removing
consumed paths, sockets, bones, slots or IDs needs coordinated migration and retest.

## Visual, audio and performance evidence

Capture imports in Godot from the gameplay camera and a useful overview. Record
build/source revision, engine, renderer/API, viewport, camera transform/projection,
lighting, quality, animation/state and population/effects. The accepted gameplay
camera is vertically downward perspective with fixed yaw; S02 refines height/FOV/
framing and tower clipping/occlusion, with S04 driving views. Provisional tuning
views are labeled. Keep player, targets and HUD/minimap visible.
Compare identical settings before/after, including 1280×800 readability. Screenshots
establish appearance; windowed playtests establish handling, collision and motion.

Measure frame/physics time, draw calls, primitives, memory and effect overdraw in
normal/burst/load cases. Follow the [validation envelope](design.md#provisional-validation-envelope)
for Deck LCD/OLED, host/client roles and sustained 60 FPS evidence. Desktop captures,
headless timings and capped FPS samples cannot certify Deck performance. Record
missing hardware/checks and provisional budgets honestly. Optimization preserves
routes/collision and authoritative outcome rules.

Audio records link creator/source/license, committed original, edits/export settings,
runtime output, buses and review evidence. Verify loops/levels in engine, bound voices
and stop owned loops on reset/teardown. Preserve launch/impact tails when appropriate;
prediction/duplicate packets must not replay sounds. Bus/lifecycle behavior belongs
to gameplay/presentation owners. 2D UI/fonts/minimap assets retain provenance and
runtime/source links without requiring Blender model handoffs.

## Archived spike assets

Foundation source files, explicit exports, materials and fixtures are retained beside their spike
under [`prototypes/`](../prototypes/README.md). Historical handoffs and evidence continue to record
their original paths and results. The archive is reference-only: production scenes, tools and asset
handoffs must use the type directories under `art/`, `tools/assets/` and `tests/assets/`.
