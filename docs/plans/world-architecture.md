# World architecture plan: scene layers, asset types and directory layout

Status: **plan only, awaiting owner decisions.** 10 October 2026. Written on lane `world-arch`
from `main` at `643ee7d5`. This plan changes no asset, scene or code. It answers three owner
requests:

- **Part A:** how the Brackett world should be split into scenes.
- **Part B:** which flat graphics should stop being Blender models and become decals,
  materials or shaders.
- **Part C:** how the asset directories should be grouped, and when to move them.

Inputs: [AGENTS.md](../../AGENTS.md), [assets](../assets.md), [development](../development.md),
[scene contracts](../scene-structure.md), [API contracts](../api-contracts.md) (road authoring,
CityData content identity), [world layout](../world-layout.md), the
[road-tool record](../spikes/road-tool.md), the [M1 plan](m1-production-plan.md) rows 2, 20–30
and 35, the greybox-update plan (C2.2a, held), the
[asset register](../assets/production/queue.json), and owner decisions 41–44, 50, 52, 55, 56 and
60–67. The decision list at the end has one item per choice. Each item gives options and a
recommendation.

## Facts this plan relies on

These were measured by reading the repository at `643ee7d5`. "Inferred" marks anything that was
not measured.

| Topic | Current state |
| --- | --- |
| World composition | `scenes/world/brackett_greybox/city.tscn` has one `Sectors` node. Under it are 12 ground tiles (`sectors/ground_XX_YY.tscn`) and 9 districts (`sectors/district_0N.tscn`). Each ground tile has one Blender GLB (land, coast, road strokes, walk strokes, field, flat bridge deck) and one concave terrain collider. Each district has a `Geometry` node with `building_NNNN` instances (290 in total) carrying `placement.gd` identity. |
| Match | `scenes/match/match.tscn` instances `city.tscn` as `World`. It owns `CityData`, the authored `Anchors` (4 player spawns and 3 parked cars, all in district 06), the runtime nodes and `LocalRig`. **It has no `WorldEnvironment` or `DirectionalLight3D`.** Only the review scene `preview.tscn` has lighting, plus a preview-only `water.glb`. `match.tscn` is on the saved-identity allowlist because its nodes lack `unique_id`. |
| Content identity | `CityData` hashes the dependency closure of `city.tscn` into `scenes/match/brackett_content_manifest.json` (110 rows, keyed by `res://` path). It also hashes the anchor descriptors. The cap is now 2048 rows. `tools/world/regenerate_brackett_content.gd` regenerates the manifest and signature. **Any path change in the closure changes the signature.** |
| Roads | RT-01 vendored Road Generator 0.9.4. RT-02 landed the source catalog, presets, stable IDs and `RoadNetworkAdapter.validate_network()`. **No road scene exists yet.** Procedural intersections only connect inside one `RoadContainer` (decision 67). RT-02 requires district boundaries to use colocated `road_interface_point` pairs. Prefab intersections (decision 44) are themselves containers joined by container edges. |
| Clearance gate | The C2.2a tooling test (`tests/unit/world/test_brackett_clearance.gd`) reads road/walk triangles from the `grey_road`/`grey_walk` ground materials. It finds districts under `World/Sectors`. It treats every non-`Geometry` district child as dressing. It counts a `Decal` AABB as a low visual part. It resolves prefabs from the flat `res://scenes/prefabs/environment/` directory. |
| Register | 226 records: 205 `production_prefab_accepted` and 21 queued (all deferred). None is placed in a world scene yet. |
| Flat carriers | 10 accepted ground graphics have their own flat Blender plane at Y = 0.015 m: `d01_sports_surface_01–03`, `d03_court_graphics_01–02`, `d04_forecourt_graphics_01–03` and `d05_quay_paving_01–02`. Six accepted material studies are single-plane or slab swatches: `city_ground_finishes_01/02/04/05` (4 × 0.08 × 4 m) and `city_water_look_01/02` (16 × 16 m planes). 26 accepted wall/sign artwork records (38 prefab scenes) put a material on reused Blender hardware (fascia frames, sign panels, poster drums, containers, sign islands), using the narrow editable-child override in [assets](../assets.md). Two have their own framed hardware: `d04_corporate_graphics_01` (5.6 × 4.0 × 0.14 m) and `d03_community_graphics_02` (3.2 cm plaques). |
| Directory sizes (tracked) | `art/models/environment`: 165 folders, 420 files. `art/source/models/environment`: 165 folders, one `.blend` each. `art/textures/environment` and `art/materials/environment`: 46 folders each. `scenes/prefabs/environment`: 283 scenes in one flat folder. `tools/asset_production`: 206 folders, 1,473 files. `docs/assets/production`: 425 entries, 2,971 files, **563 MB** (544 MB of it PNG; 205 files over 1 MB; 62 copied `.glb`/`.blend` files). `docs/spikes`: 4,613 files, 92 MB. `prototypes`: 529 files, 5.8 MB. The tracked working tree totals about 919 MB. |
| Conventions in conflict | [assets](../assets.md) says production asset tools mirror the art layout under `tools/assets/<family>/<type_name>/`. The environment register used `tools/asset_production/<nid>/` instead. Scene contracts reserve `scenes/world/district_01.tscn` and `scenes/world/sectors/`. The real world lives in `scenes/world/brackett_greybox/`. |

## Part A: world scene structure

### What the owner proposed, assessed

The idea is one ground scene, one roads scene, and one scene per district for buildings and
props. That is the right direction, because it splits the world by **who edits it**. Ground
belongs to the terrain/coast owner, roads to the road track, and each district to its C2.2a
lane. This is the same reason other engines split worlds:

- Unreal used to divide maps into sublevels. Its World Partition documentation notes that this
  "often created issues sharing files between multiple users". Unreal now uses One File Per Actor
  and Data Layers.
- Unity's multi-scene editing splits a level into additively loaded scenes by responsibility
  (lighting, environment, gameplay) so several people can edit at once.

Godot has no one-file-per-actor feature. In Godot the equivalent is **one saved scene per
owner, instanced into a thin parent**, with one writer per file.

The idea needs four additions:

1. **Gameplay markers** need their own owner. They change for gameplay reasons (decision 62
   spawn spread), not art reasons.
2. **Lighting/environment** is missing from Match today. It is presentation and should stay
   outside the content signature.
3. **Coast/shore** dressing (about 3.7 km of seawall, quay edge and boardwalk) is its own body of
   work. It belongs to neither a district nor the terrain tiles.
4. **Flat ground graphics** (Part B) need a home inside each district.

### Proposed layers

```text
Match (match.tscn)
├── CityData
├── Environment        environment.tscn: WorldEnvironment + sun; presentation only
├── World              city.tscn (keeps UID uid://c6ogmv4d7i8yn, world_id "brackett")
│   ├── Ground         ground.tscn: 12 terrain tiles (visual + sole flat collider), Water
│   ├── Roads          roads.tscn: RoadManager + road-region RoadContainers (RT-03 creates it)
│   ├── Coast          coast.tscn: shore edges, quay edge/rail, boardwalk (coast lane creates it)
│   └── Districts
│       └── District0N district_0N.tscn (keeps UID)
│           ├── Geometry   buildings and landmarks (world_id per building, unchanged)
│           ├── Dressing   lot/yard props and later street furniture (no world_id)
│           └── Surfaces   Decal instances for flat ground/wall graphics (no world_id)
├── Anchors            markers.tscn: PlayerSpawns, ParkedCars (same node paths as today)
├── RuntimeEntities, RuntimeEffects, PlayerLifecycle, Replication, LocalRig (unchanged)
```

| Layer | Owns | Does not own | Collision | In content signature |
| --- | --- | --- | --- | --- |
| Ground (`ground.tscn`) | Land, coastline shape, fields, ground-finish regions (Part B, type c), the flat bridge deck until RT-10, the water surface and its shader (Part B, type d) | Roads, buildings, shore fixtures | **Sole flat walk/drive collider** (one concave shape per tile). Water has none. | Yes, via `city.tscn` |
| Roads (`roads.tscn`) | RoadManager, road-region containers, prefab intersection instances (RT-04), generated road/sidewalk/curb/crosswalk surfaces (decision 42), road-tool fixtures (RT-08 signals and lights), the Blender harbour bridge structure (RT-10) | Ground finishes off the road, district graphics | No coplanar collision on flat road or sidewalk surfaces. Only non-overlapping shapes (raised curbs if RT-03 needs them, bridge deck and rails). | Yes |
| Districts (`district_0N.tscn`) | Buildings and landmarks (`Geometry`), lot/yard dressing (`Dressing`), flat graphics off the carriageway (`Surfaces`) | Road surfaces and markings, terrain | Only what each prefab declares. Decals have none. | Yes |
| Coast (`coast.tscn`) | Seawall, quay edge, rock shore, boardwalk, quay rail and ladders along the coastline | Marina docks and yachts (district 05 per the greybox plan), the bridge | Shore fixtures' own colliders. This is a capacity item, at about 900 segments if 4 m modules are used. | Yes |
| Gameplay markers (`markers.tscn`) | Authored player spawns and parked-car anchors (decision 62 spread) | Traffic and pedestrian spawn candidates. RT-05/06/07 derive those from roads at load; they are never hand-placed. | None | Yes, through the anchor descriptor hash (not the manifest) |
| Environment (`environment.tscn`) | `WorldEnvironment`, sun, sky/fog/ambient | Gameplay | None | No. This is deliberate: lighting is presentation. |

**Props vs buildings.** Keep them in the **same district scene, as separate child groups**
(`Geometry`, `Dressing`, `Surfaces`), not as separate files.

- The same C2.2a lane places a building and the lot dressing around it, so splitting the file
  would add cross-file coordination with no parallel benefit.
- Districts are already one file per lane.
- Later street furniture (C2.2b) runs after the buildings for that district have landed, so it
  is sequential, not concurrent.
- The clearance test already treats non-`Geometry` children as dressing.
- Revisit this only if two lanes must edit one district at the same time.

**Where decals and ground graphics live.**

- Off-road one-off graphics (court motifs, forecourt bands, quay insets, lot and apron markings)
  live in `District0N/Surfaces`. Painted wall graphics without hardware live there too, or under
  the building's own instance when they belong to one prefab.
- Large ground finishes (paving, grass, service concrete, lot asphalt, the sports field finish)
  are **materials on the ground geometry**, owned by Ground.
- Carriageway and crossing markings are **generated by the road layer** (decision 42). District
  lanes never place decals over a carriageway.

### Roads: one scene, region containers

**One `roads.tscn`, holding one container per road region.** Do not use one scene per region.

- The road track is a single sequential critical path (RT-03 → RT-04 → RT-05 → … → RT-10). There
  is no concurrent road writer to separate.
- Cross-container edges are stored as NodePaths and reciprocal edge arrays. When containers sit
  in separately instanced scenes, those edges are saved as instance overrides in the parent
  anyway, so a split would not remove parent-scene edits.
- Road Generator does not save generated meshes. The scene holds only about 400 RoadPoints and
  their containers, so its size is not a problem.
- Container identities (`brackett/containers/<slug>`, RT-02) survive a later move into
  per-region sub-scenes. Splitting later is cheap if a measured need appears.

**Container layout versus districts.** A container is a road-topology unit, not a district
ownership unit. Buildings never depend on which container a road is in. Rules for RT-03:

1. Seed about nine region containers from the district polygons. Put the harbour bridge in its
   own container (it has a Blender structure and a separate profile).
2. Every procedural `RoadIntersection` and all its branches stay inside one container
   (decision 67).
3. Cut container boundaries **mid-block on straight segments**, at least one intersection
   approach length from any junction. Use colocated `road_interface_point = true` pairs with
   reciprocal edge records, as `validate_network()` already requires.
4. A road that forms a district boundary belongs wholly to one container, including both
   sidewalks. The district on the other side does not own it.
5. Prefab intersections (RT-04) are instanced containers joined through interface points. They
   follow the same rule.

### Ownership and parallel lanes without `.tscn` conflicts

**One writer per file.** The world integrator edits `city.tscn` once during migration and then
rarely. Two shared files are never hand-merged:

- the content manifest;
- the `content_signature` line in `match.tscn`.

Every lane regenerates both with `tools/world/regenerate_brackett_content.gd`. On a rebase
conflict, the lane regenerates again.

| Work | Writes | Can run in parallel with |
| --- | --- | --- |
| C2.2a district lane `d0N` | `district_0N.tscn` only (Geometry, Dressing/Lots, Surfaces) | Other district lanes, mesh-fix lanes |
| C2.2b street furniture (after RT-03/RT-10) | `district_0N.tscn` `Dressing/Street` | Other districts. Sequential after that district's C2.2a. |
| RT-03 live generation | creates `roads.tscn`, `scripts/world/roads/*` | District lanes |
| RT-04 intersections | `scenes/prefabs/roads/*` and their placements in `roads.tscn` | District lanes |
| RT-05/06/07/09 derivation | code and derived data only, no scene writes | Everything |
| RT-08 signals/lights | fixture placements under `roads.tscn` | District lanes |
| RT-10 road replacement | `ground_*.blend`/GLBs (stop exporting road/walk), `roads.tscn` | District lanes, which keep clearing the same corridors |
| Coast lane | creates `coast.tscn` | Everything except a ground coastline revision |
| Marker changes (decision 62) | `markers.tscn` | Everything |
| Lighting/art direction | `environment.tscn` | Everything |

The greybox plan's C2.2a rules stay as they are: node shape, ID retention, fit checks and
evidence. They change in only two ways. Sports, court, forecourt and quay graphics are placed as
decals or ground materials (Part B), not as carrier prefabs. Prefab paths follow Part C.

### Identity and integrity

- **`world_id`s are unchanged.** Buildings keep `brackett/district_NN/building_NNNN`. Ground tiles
  keep `brackett/ground_XX_YY`. Markers keep `brackett/district_06/player_spawn_0N` and the
  parked-car IDs. Roads use RT-02 identities. Layer roots, dressing and decals get **no**
  `world_id` (scene contracts: decorative instances need no gameplay ID). A layer move or rename
  never changes a `world_id`, because identity is an explicit property, not a NodePath.
- **Content manifest.** The manifest is keyed by path, so every moved file changes the
  signature. Each migration step regenerates the manifest, writes the new signature into
  `match.tscn` and bumps `content_revision` by 1. The roads layer brings the addon's runtime
  scripts into the closure. That is correct, because host and client must agree on the addon
  too. The 2048 cap covers it (inferred from the approximately 730-row estimate in the greybox
  plan plus about 100 addon files; measure when RT-03 lands).
- **Saved identities.** Every new layer scene is saved through the editor (the windowed editor
  works since decision 66). It gets a header UID, ext_resource UIDs and node `unique_id`s.
  Surviving scenes (`city.tscn`, the 12 tiles, the 9 districts, `preview.tscn`) are moved with
  their UIDs. Extracting `Anchors` into `markers.tscn` is the moment to give `match.tscn` real
  `unique_id`s and remove it from the saved-identity allowlist.
- **Collision ownership.**
  - Ground is the only flat collider.
  - Roads add only non-coplanar shapes.
  - RT-10 removes the ground's flat bridge deck collider when the Blender bridge collider
    lands, so there are never two coplanar decks.
  - Decals and ground materials add no collision.
  - When RT-10 strips road/walk faces from the ground GLBs, the land mesh must leave holes, or
    the road surface must sit above it, so the two do not z-fight. RT-10 owns that choice and
    a capture check for it.
- **Clearance test coupling.** When RT-10 removes the `grey_road`/`grey_walk` faces, the clearance
  test must switch its corridor source to the road layer's output in the same change. The
  migration's `Sectors` → layer rename updates the test's `World/Sectors` lookup in the same
  commit.

### Performance

- **Load the whole island.** C2.1 measured 2,181 nodes and 305 static shapes. The naive road
  proxy alone was 3,466 nodes and 331 colliders. Both are inside S07's passing 96-block envelope
  (13,254 nodes, 768 colliders). Streaming stays a future option. If it is ever needed, the layer
  split makes districts and coast the natural streaming units, while ground, roads and markers
  stay resident.
- **Visibility ranges.** The camera is fixed at 47 m and 42°, so the farthest visible ground is
  roughly 65 m away (inferred from the projection). Frustum culling already drops distant
  objects from the main pass. Directional shadows can still render casters outside the view.
  Recommend `visibility_range_end` of about 100 m (with margin) on small dressing props and
  coast fixtures, and no shadow casting on flat items. HLOD proxy meshes and occlusion culling
  offer little at this camera. Do not build them unless a capture or profile shows a need
  (Godot "Visibility ranges (HLOD)").
- **Clustered elements.** Decals share Forward+'s default 512 clustered-element limit per view
  with omni/spot lights and reflection probes (Godot "Using decals"). RT-08 street lights, if
  they use `OmniLight3D`, count against the same limit. Use **64 decals in view** as the review
  trigger, and enable distance fade on every decal.
- **Re-measure** with the C2.1 baseline runner when RT-10 lands and after each C2.2a district.
  These remain contended numbers.

### Migration path (Part A)

Each step is one reviewable lane. Each lane runs full `tools/production_checks.py`, saves through
the editor, runs the saved-identity check, regenerates the manifest and signature, and keeps
`git diff -M` showing renames.

1. **Rename the world folder and add the layer parents (lane WA-1, world integrator).**
   - Move `scenes/world/brackett_greybox/{city.tscn, preview.*, sectors/}` to
     `scenes/world/brackett/`. Ground tiles go under `ground/`, districts under `districts/`.
   - Move `placement.gd` to `scripts/world/world_placement.gd`, keeping its UID and class name.
   - Use the Godot FileSystem dock, or the scripted move from Part C, so every UID survives.
   - Create `ground.tscn`, instancing the 12 tile scenes unchanged (same node names, world_ids
     and transforms).
   - In `city.tscn`, replace `Sectors` with `Ground` (one instance) and `Districts` (nine
     instances, with their existing `unique_id`s kept where Godot allows).
   - Update `test_city_data.gd`, `test_brackett_clearance.gd` (`World/Sectors`),
     `test_measured_replication_codec.gd`, `tools/world/capture_brackett_views.gd` and the
     greybox authoring tools' path constants.
   - Expected result: identical world transforms, node and collider counts, and captures. A
     new signature.
2. **Extract markers (same lane or WA-2).** Save `Match/Anchors` as `markers.tscn` and instance
   it back at `Match/Anchors`. CityData's `player_spawns_path` and `parked_cars_path` stay the
   same, and so do the anchor descriptors. Normalize `match.tscn` identities and drop it from the
   allowlist.
3. **Add Environment (WA-3, owner visual check).** Save the review lighting as
   `environment.tscn`, then instance it in Match and in `preview.tscn`. This is a visible change
   to Match, which is unlit today, so it needs an owner capture review.
4. **Release C2.2a district lanes.** They write only `scenes/world/brackett/districts/district_0N.tscn`
   (new path, same UID).
5. **RT-03 creates `roads.tscn`** under `World/Roads` with region containers. **The coast lane
   creates `coast.tscn`.** **The water lane adds `Ground/Water`** (Part B).
6. **RT-10 revises the ground tiles** (no road/walk faces; ground-finish regions per Part B).
   It moves the surviving ground and water outputs out of `brackett_greybox` art paths, and
   switches the clearance test's corridor source.
7. **Greybox cleanup (greybox plan Q7).** Delete unreferenced greybox building wrappers, GLBs,
   imports and kit `.blend`s.

Do not create empty placeholder scenes. `roads.tscn` and `coast.tscn` appear when their first
real content lands.

## Part B: correct asset types

### The rule, in plain language

Something is a **model** only if it has thickness or shape the camera can see: a curb, a sign
panel, a frame, a bollard, a building. A picture painted onto a surface is **not** a model.

- **(a) Decal:** a one-off graphic laid onto the ground or a wall.
- **(b) Road-tool marking:** marking on a road or crossing, generated by the road tool
  (decision 42).
- **(c) Ground material:** the material of a large area, applied to the ground geometry.
- **(d) Water shader:** the sea and harbour surface.
- **(e) Model:** anything with real geometry.

All textures still come from committed source art (most artwork is generated by its
`artwork.py`). Only the flat Blender carrier plane goes away.

### Recommendation per candidate

| Candidate (records) | Today | Recommended type | Notes |
| --- | --- | --- | --- |
| Track finish and lane graphics `d01_sports_surface_01` (80 × 45 m, 4096 × 2304 texture) | Flat carrier at Y 0.015 on the saved 98 × 53 m field. Needs a +0.005 m offset against z-fighting. | **(c)** material on the field region of the ground | Covers most of the 70 × 44 m view. Godot says a few large, screen-filling decals cost more than many small ones. The field polygon already exists, so the texture becomes its material, with no extra plane and no z-fight offset. |
| Field line graphics `d01_sports_surface_02` (52 × 26 m, 96% unpainted) | Flat carrier | **(c)** second layer of the same field material | A detail or overlay layer (StandardMaterial3D detail with mask, or a small project shader; the pilot chooses). |
| Small court graphics `d01_sports_surface_03` (28 × 16 m) | Flat carrier | **(a)** Decal | Below the size threshold below |
| Circular paving motif `d03_court_graphics_01` (14 m), play steps `_02` (1.9 × 5.3 m) | Flat carriers | **(a)** Decal | |
| Paving band `d04_forecourt_graphics_01` (24 × 4 m), entry motif `_02` (8 × 16 m), inset emblem `_03` (8 × 8 m) | Flat carriers | **(a)** Decal | Decal pilot candidates: small, simple and unplaced |
| Quay border `d05_quay_paving_01` (8 × 1.2 m), civic inset `_02` (6 × 6 m) | Flat carriers | **(a)** Decal | Repeated border decals along a quay count toward the per-view decal trigger |
| Ground finishes `city_ground_finishes_01/02/04/05` (plaza paving, service concrete, grass, soil) | 4 × 4 m slab swatch GLBs plus `.tres` | **(c)** keep the `.tres` and textures as ground/sidewalk materials. Retire the swatch GLB, `.blend` and prefab. | Used by the ground revision for lot and plaza regions, and by RT-03 for sidewalk/curb materials |
| Parking asphalt `city_ground_finishes_03` (queued) | Deferred | **(c)** commission as a material only, with no GLB | Lot surfaces in districts 07 and 08 |
| Water looks `city_water_look_01/02` (16 × 16 m planes) | Single-plane GLBs plus `.tres` | **(d)** one water `ShaderMaterial` on the Ground layer's sea surface. Reuse the albedo and normal textures as shader inputs (open sea, calmer basin). Retire the GLB, `.blend` and prefab. | Also replaces the preview-only greybox `water.glb`. No collision, as today. |
| Lane line, stop line, crossing, arrow `city_road_markings_01–04` (queued) | Deferred to RT-03 | **(b)** road-tool generated. Lane lines use the addon's UV lane markings. Stop lines, crossings and arrows are generated marking surfaces, or road-tool-placed decals (RT-03 chooses). | Recommission as **2D texture art only** when RT-03 asks for it |
| Parking bay, loading bay `city_road_markings_05/06` (queued) | Deferred | **(a)** Decals in district `Surfaces`, off the carriageway | Use (b) instead only if parking aisles become road-tool sections |
| Work-apron graphics `d08_work_apron_graphics_01–03` (queued) | Deferred ("surface boundary") | **(a)** Decals in district 08 `Surfaces` | Commission as 2D texture art when C2.2a d08 needs them |
| Walkway modules `city_walkways_01–04` (queued) | Deferred to RT-03 | **(b)** generated sidewalks and curbs. Retire the records. | Owned by decision 42 |
| Alley strip `city_walkways_05` (queued) | Deferred | **(b)** if alleys become `service` road sections, otherwise **(c)** a ground-finish region | RT-03 decides when it reaches alleys |
| Wall/sign artworks on reused hardware (fascia, sign panel, poster drum, container, sign island records in d01–d09) | Material override on a reused Blender carrier | **(e)** keep | The artwork is already a material. The hardware has real thickness. Nothing to retire. |
| Framed facade panel `d04_corporate_graphics_01`, entrance plaques `d03_community_graphics_02` | Own Blender hardware (14 cm frame, 3.2 cm bevelled plaques) | **(e)** keep | Real frame geometry. Plaque depth is invisible at 47 m, but the asset is accepted and cheap. Optional decal later. |
| Future paint-on-wall graphics with no hardware (murals, stencils) | n/a | **(a)** Decal | New rule |
| Shore edges, quay furniture, boardwalk, curbs, signs, barriers | Models | **(e)** keep | Real geometry |

**Decal versus ground material threshold.** Use a decal when the graphic is an overlay on
another finish and fits within about 30 × 30 m, roughly half the gameplay view. Use a ground
material when the graphic *is* the finish of a region, or is larger than that. The decal pilot
confirms or adjusts the threshold from captures and contended frame times.

### Decal rules (for docs/assets.md)

- **A decal is a saved scene.** Each artwork ships a reusable scene whose root is a `Decal` with
  its albedo texture (plus normal or ORM only if needed). Districts instance it under `Surfaces`.
  Converting a carrier keeps the **same prefab path and UID**: the root changes type and the
  `Visuals/Model` child is removed, so any consumer still resolves.
- **Projection.** Keep the projection height short (about 0.3–0.5 m) and set Normal Fade to about
  0.5, so ground decals do not paint curbs or walls. Use the Sorting Offset convention: finishes
  below graphics, graphics below markings.
- **Cull mask.** Decals must not paint cars, characters, wrecks, projectiles or effects. Add a
  named `dynamic` 3D render layer, set it on those prefabs' visual instances, and exclude it from
  every decal's cull mask (Godot "Using decals": Cull Mask).
- **Distance fade** is on for every decal, so faded decals leave the cluster list.
- **Textures.** Longest edge no more than 4096 px, at about 20–50 px/m. Albedo is sRGB with
  alpha. The project-wide decal filter setting is chosen in the pilot. Godot packs decal
  textures into a shared atlas, so the pilot records its size (inferred engine behaviour, verify
  in the pilot).
- **Renderer.** Decals require Forward+ or Mobile, not Compatibility. Mobile applies only 8
  decals per mesh resource, which large ground tiles would exceed. This policy therefore assumes
  the project's current Forward+ renderer.
- **Gameplay.** Decals have no collision, no `world_id` and no gameplay meaning. The clearance
  test must stop counting `Decal` AABBs as low obstructions in district `Surfaces`. It must also
  reject district decals that overlap the carriageway, because road markings belong to the road
  layer.

### Policy changes for owner approval

The current rules are "Create visible 3D models in Blender" and "No primitive/CSG/generated
render meshes". A decal is not a mesh. A water plane is one.

**AGENTS.md**: add one bullet after the decision-42 road exception:

> Flat surface graphics are not models (owner decision NN). Ground and wall graphics with no
> visible thickness (sports and court markings, paving motifs, forecourt bands, lot and apron
> markings, painted signs) use saved `Decal` scenes with textures from committed sources. Large
> ground finishes are materials on the Blender ground geometry. The sea and harbour use a water
> shader on a flat engine plane owned by the ground layer. Do not add Blender carrier planes for
> these. Anything with visible thickness keeps the Blender rule.

**docs/assets.md**:

- Add a section, "Surface graphics, ground materials and water". It contains the decal rules
  above, the type table criteria, the 64-decals-in-view review trigger and the clearance-test
  interaction.
- Amend "No primitive/CSG/generated render meshes" to name the single water-plane primitive
  exception, if the owner chooses option (a) in decision B2.
- Replace the "flush carrier" precedent in handoffs with the decal rule.

### Migrating the already-accepted carriers

None of these assets is placed in a world scene, so retiring them changes no saved world and no
manifest row.

1. **Policy lane (B-1):**
   - Land the AGENTS.md and assets.md wording.
   - Add `layer_names/3d_render` for `world_static` (1) and `dynamic` (2) in `project.godot`.
   - Set the `dynamic` layer on the car, wreck, character, projectile and effect prefabs, saved
     through the editor.
   - Make the clearance-test decal changes.
   - Run full production checks.
2. **Decal pilot (B-2):**
   - Convert `d04_forecourt_graphics_01–03` to decal scenes in place.
   - Delete their GLB, `.import`, `.blend` and carrier `.tres`. Keep the PNG and `artwork.py`.
   - Replace `author.py`/`export.py` with a decal-settings check.
   - Capture at 47 m/42° over ground, with a parked car straddling a decal (cull mask check).
   - Record decals in view, the atlas size and contended frame time.
   - Owner visual check.
3. **Remaining decals (B-3):** convert `d01_sports_surface_03`, `d03_court_graphics_01–02` and
   `d05_quay_paving_01–02` the same way.
4. **Ground materials (B-4, with the ground revision):**
   - `d01_sports_surface_01/02` become the field material layers. Their prefabs, GLBs and
     `.blend`s retire.
   - `city_ground_finishes_01/02/04/05` keep their `.tres` and textures. Their swatch GLB,
     `.blend` and prefab retire.
   - Assigning these materials to ground regions waits for the RT-10 ground revision (or a
     ground-finish lane before it), so the ground source is edited once.
5. **Water (B-5):**
   - Add `Ground/Water` (plane plus `water.gdshader` under `art/environment/surfaces/`) using the
     `city_water_look` textures.
   - Retire the two swatch GLBs, `.blend`s and prefabs, and the greybox `water.glb` once
     `preview.tscn` uses `Ground/Water`.
6. **Register:**
   - Keep every record ID.
   - Add `runtime_type` (`decal`, `material`, `shader_input` or `model`).
   - Drop retired paths from `owned_paths`.
   - Keep the status `production_prefab_accepted` for decals (they still ship a prefab scene).
     Use a new status `production_material_accepted` for materials and shader inputs.
   - Rewrite the deferred records' blockers to "commission as 2D texture art when <lane> needs
     it", or "retired: generated by RT-03" for walkways 01–04.
   - Each record's markdown gets a dated "type migration" note. Historical evidence stays.
7. **Mesh audit:** the mesh-audit fix lanes skip the 16 retired carriers.

**Interaction with RT-03 surface records.**

- RT-03 consumes `city_road_markings` artwork as textures for generated stop-line, crossing and
  arrow surfaces.
- RT-03 uses `city_ground_finishes` materials for sidewalks and curbs where it does not use the
  addon defaults.
- RT-03 owns every marking on a carriageway or crossing. District decals stay off those areas,
  and the clearance test enforces it.
- Parking-lot and apron markings stay district decals. This removes the "surface boundary"
  blocker: a road-tool section owns its surface, and everything else is ground material plus
  decals.

## Part C: directory layout

### Problem

Each environment asset is spread across up to seven single-asset folders:

- `art/models/environment/<nid>/` (one GLB plus its `.import`);
- `art/source/models/environment/<nid>/` (one `.blend`);
- `art/textures/environment/<nid>/` and `art/materials/environment/<nid>/` (46 assets only);
- `tools/asset_production/<nid>/`;
- `docs/assets/production/<nid>.md` plus `<nid>-evidence/`;
- a prefab in one flat folder of 283 scenes.

Finding everything for one family, such as the 11 `d03_apartment_family` records, means visiting
seven trees.

Godot's "Project organization" guide recommends grouping assets as close to the scenes that use
them as possible, feature by feature (its example is `/models/town/house/` holding the model and
its textures), with snake_case names. It also recommends a separate folder for the built levels
that use those assets.

### Options

1. **Category/family, split by type** (today's convention, grouped). Example:
   `art/models/environment/<category>/<family>/`, with the same path repeated under
   `art/source/models/`, `art/textures/`, `art/materials/` and `scenes/prefabs/environment/`.
   This is a small rule change and stays literally consistent with decision 36's
   `art/models/<family>/<type>`. It still leaves five parallel trees.
2. **Category/family, art grouped by feature (recommended).**
   - Runtime art: `art/environment/<category>/<family>/` holds each `<nid>.glb` with its
     `.import`, plus `textures/` and `materials/` subfolders for that family.
   - Source: `art/source/environment/<category>/<family>/<nid>.blend` (it stays under the
     ignored `art/source/` tree).
   - Prefabs: `scenes/prefabs/environment/<category>/<family>/<nid>*.tscn`.
   - Tools: `tools/assets/environment/<category>/<family>/<nid>/`. This matches the convention
     already written in assets.md.
   - Records: `docs/assets/environment/<category>/<family>/<nid>.md` and `<nid>-evidence/`.

   Model, textures and materials sit together, as Godot recommends. The art/scenes split stays,
   because composed scenes and the export filters follow it.
3. **Everything for a family in one folder**, prefabs included. This is the closest to Godot's
   example. But it mixes art handoffs with scene composition, breaks the `scenes/` contract and
   export filters, and puts prefabs inside the art tree.

Option 2 changes the path shape that decision 36 fixed for weapons and vehicles, while keeping
its intent (one family/type folder). For one convention across the project, apply option 2 to
vehicles, weapons, characters and effects in a short follow-up move. Those are only about 10
type folders (decision C2).

### Proposed categories (all 63 register families)

| Category | Families |
| --- | --- |
| `buildings` | d01_academic_buildings, d01_sports_pavilion, d01_lighthouse, d02_house_family, d02_corner_shop, d03_apartment_family, d04_towers, d04_podiums, d05_quay_frontages, d05_harbour_hall, d06_shopfront_blocks, d06_entertainment_hall, d06_southern_shopping_parade, d06_mixed_use_infill, d07_retail_buildings, d08_workshop_buildings, d09_warehouses, city_small_shop_shells |
| `building_details` | city_roof_details, city_shop_fittings, d03_laundry_frames |
| `street_furniture` | city_seating, city_waste, city_barriers, city_service_furniture, city_parking_furniture, city_sign_supports, d06_poster_drum, d07_sign_island, d07_trolley_shelter |
| `road_fixtures` | city_lights, city_traffic_fixtures (RT-04 intersection pieces join here) |
| `planting` | city_planting |
| `lot_props` | d02_domestic_details, d08_repair_furniture, d09_storage, d09_cranes |
| `waterfront` | city_marina_docks, city_moored_yachts, city_boardwalk, city_shore_edges, city_quay_furniture, city_harbour_bridge, d06_harbour_footbridge |
| `graphics` | d01_sports_surface, d01_campus_graphics, d02_neighbourhood_graphics, d03_court_graphics, d03_community_graphics, d04_forecourt_graphics, d04_corporate_graphics, d05_civic_graphics, d05_quay_paving, d06_commercial_graphics, d07_retail_graphics, d08_repair_graphics, d08_work_apron_graphics, d09_freight_graphics, city_road_markings |
| `surfaces` | city_ground_finishes, city_water_look, city_walkways (plus the water shader) |
| *(vehicles family)* | vehicle_wrecks moves to the vehicles tree beside the three cars it belongs to (decision 64) |

Family names keep their district prefix (`d04_…`) so they stay searchable. Category-first
grouping is used instead of district-first because about half the families (`city_*`) serve many
districts. Inside a family folder, texture and material filenames must be unique. The move tool
fails on a collision, and a colliding name gets the record's `nid` as a prefix.

### Other directories

- **Per-asset tools (`tools/asset_production/`, 1,473 files).** Each folder is the reproducible
  source of its asset: `author.py` builds the `.blend`, and `artwork.py` builds the PNGs. So keep
  them runnable and move them to `tools/assets/environment/<category>/<family>/<nid>/`. Rewrite
  their path constants from the move map. Do not consolidate the about 187 near-duplicate
  `validate.py` and 117 `check_prefab.gd` files now. Extract a shared module only when a script
  is re-run for real (the mesh-audit gate and the decal-settings check are the first shared
  tools). The 186 project-compiled `check_prefab.gd`/`check.gd` files stay in the compile set.
- **Evidence retention (`docs/assets/production`, 563 MB).** Production mode (decision 50) wants
  lean evidence.
  - **Going forward:** at most 2 MB and 8 images per asset (gameplay camera, overview, close-up,
    collision), downscaled to a 1280 px longest edge and losslessly optimized. Keep JSON
    receipts, not raw stdout/stderr. No copied GLB/`.blend` files. Superseded attempts stay in
    lane scratch.
  - **Existing tree:** one cleanup lane deletes `initial_attempt/`-style superseded captures, the
    62 copied `.glb`/`.blend` files and raw logs, and recompresses the PNGs. Records link the
    commit that holds the originals.
  - This shrinks the working tree, **not Git history**. Rewriting history is destructive and is
    not recommended. Do not introduce Git LFS now; revisit it only if new binary evidence keeps
    growing after the cap.
- **`docs/spikes` (4,613 files, 92 MB).** Keep every `.md` record. Prune its `*-evidence/` folder
  to the compact results the record cites, and point to the commit for the rest. This uses the
  same "inspect at commit" pattern as the `prototypes/` README. `docs/` is already
  `.gdignore`d, so this is about size and clutter only.
- **`docs/reviews/asset-production` (36 MB)** follows the same evidence cap.
- **`prototypes/` (5.8 MB).** Leave as is (decision 39: reference-only, `.gdignore`d,
  export-excluded). Delete later when production tests replace the fixtures.
- **Greybox kit after C2.2a.** Delete unreferenced greybox building wrappers, GLBs, imports and
  kit `.blend`s (greybox plan Q7). After RT-10, the surviving ground tiles and water move to
  `art/environment/terrain/brackett_ground/` and its source mirror, and
  `tools/assets/world/brackett_greybox` is renamed to match.

### How to move safely

Godot has no public scripted "move with dependency fix-up". The editor's FileSystem dock does
this, but it is impractical for about 1,000 files. Use one reviewed scripted move:

1. **Freeze.** Main is clean and fully green. No open lane touches moved paths (asset, mesh-fix,
   C2.2a, Part B). The mesh-audit report has landed.
2. **Move map.** A tool (`tools/assets/move_environment.py`, with unit tests) builds an
   `old → new` JSON map from `queue.json` and the category table. It fails on name collisions.
   The map is reviewed before running and committed as the migration record.
3. **Move with sidecars.**
   - `git mv` each file together with its `.import` and `.uid` sidecars.
   - Rewrite `source_file=` and `"use_external/fallback_path"` in every `.import`.
     `dest_files` in `.godot/` regenerate.
   - Rewrite `path=` on every `[ext_resource]` in `.tscn`/`.tres`. UIDs are unchanged.
4. **Blender links.** Open each moved `.blend` headless in pinned Blender, under `timeout`. Fail
   on any missing linked library or image. If a source used relative external paths, run Blender's
   make-paths-relative and re-save it with no geometry change.
5. **Reimport and resave.**
   - Delete `.godot/` for a cold cache, then run `godot --headless --editor --import` under
     `timeout`.
   - Save every changed scene and resource twice through an editor-mode save and require
     byte-identical output.
   - Run `tools/saved_identity_check.py`.
   - Check that every ext_resource UID resolves (`ResourceUID`) to its new path.
   - The import log must contain no "file not found", UID-fallback or SCRIPT ERROR lines.
6. **Prove nothing changed visually.** Reimport hashes of every moved GLB and texture equal the
   old ones. Prefab captures before and after are identical. `git diff -M` shows 100%-similar
   renames.
7. **Content identity.** Regenerate the manifest and signature, bump `content_revision`, run full
   `tools/production_checks.py` and Boot smoke.

### References to update in the same commit

- `queue.json`: `owned_paths`, `producer_manifest`, `report` and `brief` links.
- Evidence manifests (`<nid>-evidence/manifest.json` path keys). These are machine-read, so
  rewrite them. Historical logs and receipts keep their old text, and the committed move map
  resolves old paths.
- Per-asset tool path constants (for example `ROOT / f"art/textures/environment/{NID}/…"`).
- Tests:
  - `test_brackett_clearance.gd` (`PREFAB_DIRECTORY` assumes a flat folder; replace it with a
    prefab index from the register);
  - `tests/assets/asset_production/*.tscn`;
  - `test_city_data.gd`;
  - `test_measured_replication_codec.gd`;
  - `tools/world/*.json` prefab IDs and paths.
- The orchestrator's integration tools in the main checkout's `.pi/subagents/tools/`. These are
  outside the repository, so the orchestrator updates them.
  - `integrate_asset.sh`'s stray-path regex
    (`art/(models|source/models|textures|materials)/[a-z_]+/${fam}` and friends) becomes
    `art/(source/)?environment/[a-z_]+/${fam}`, `scenes/prefabs/environment/[a-z_]+/${fam}`,
    `tools/assets/environment/[a-z_]+/${fam}` and `docs/assets/environment/[a-z_]+/${fam}`.
  - `queue_accept.py`'s `scenes/prefabs/*/{nid}*.tscn` glob becomes recursive.
- Docs:
  - asset records' relative links (their depth changes; run a link checker);
  - the [assets](../assets.md) directory section;
  - [scene contracts](../scene-structure.md) production layout (also fix the stale
    `district_01.tscn`/`sectors/` rows to the Part A layout);
  - the M1 plan inputs table;
  - the greybox plan's paths.
- `docs/assets/production/queue.json` keeps its path, so register tooling does not churn. The
  per-asset records move.

### Sequencing

**Move first:** after the mesh-audit report lands, and before any mesh-fix lane, Part B
conversion or C2.2a district lane.

- Mesh-fix lanes edit `.blend` sources, GLBs, tool scripts and records. A binary file that is both
  moved and modified shows up in Git as a delete plus an add. Rebasing a fix lane across the move
  would then hit modify/delete conflicts on every asset. Running the move after the fixes avoids
  that, but it delays C2.2a.
- C2.2a district scenes reference prefab paths. Moving after placement rewrites all nine
  district scenes and the manifest a second time.
- Today nothing is in flight: the register is complete, C2.2a is held and the fix lanes have not
  started. The move is mechanical: one lane, mostly verification time.

The full order:

1. Owner decisions.
2. Mesh-audit report lands (read-only).
3. **C-1:** directory move.
4. **WA-1/WA-2:** world layers and markers.
5. **B-1:** policy and render layers.
6. **B-2:** decal pilot.
7. In parallel: mesh-fix lanes per family, C2.2a d02 pilot then waves, B-3 decals.
8. WA-3 environment, when the owner can review captures.
9. B-4/B-5 alongside the RT-10 ground revision and the water lane.
10. Evidence and spikes cleanup at any quiet point. It touches only `docs/`.

Steps 3–6 are serial because each regenerates the content manifest.

## Owner decisions

Each item lists options and a recommendation.

**A1. World scene structure.**
(a) Keep today's flat `Sectors` (12 tiles + 9 districts) and only add scenes as needed.
(b) Layers: `Ground`, `Roads`, `Coast` and `Districts` under `city.tscn`; `Anchors`
(`markers.tscn`) and `Environment` under Match.
(c) Exactly three kinds of scene: ground, roads, one per district holding everything else.
*Recommendation: (b).* It is the owner's idea plus separate owners for markers, coast and lighting.

**A2. Ground scene shape.**
(a) One `ground.tscn` instancing the 12 existing tile scenes unchanged.
(b) Merge the tiles into one ground model and collider.
(c) Keep the tiles directly in `city.tscn`.
*Recommendation: (a).* One owner and one instance in the city, with the tiles kept for culling
and smaller colliders. There is no re-export.

**A3. Roads scene.**
(a) One `roads.tscn` with region containers.
(b) One scene per road region.
*Recommendation: (a).* The road track is sequential. Cross-container edges live in the parent
anyway. Container IDs let it split later if needed.

**A4. Road container layout.**
(a) About nine region containers seeded from district polygons, cut mid-block with interface
points, plus a separate bridge container.
(b) One container for the whole island.
(c) One container per route.
*Recommendation: (a).* It matches RT-02's interface contract, keeps every procedural junction
in one container (decision 67) and bounds rebuild work. (b) avoids interfaces, but prefab
intersections are containers anyway.

**A5. Props versus buildings.**
(a) Same district scene, separate `Geometry`, `Dressing` and `Surfaces` groups.
(b) A separate dressing scene per district.
*Recommendation: (a).* One lane does both. Revisit only if two lanes must edit one district at
once.

**A6. Gameplay markers.**
(a) Keep them in `match.tscn`.
(b) One `markers.tscn` instanced at `Match/Anchors`, with unchanged paths.
(c) Per-district anchors inside district scenes.
*Recommendation: (b).* One gameplay owner, spread across districts per decision 62, with no
code change. Derived traffic and foot anchors stay load-time data.

**A7. Lighting/environment.**
(a) `environment.tscn` instanced by Match and `preview.tscn`, outside the content signature.
(b) Inside `city.tscn`.
*Recommendation: (a).* Lighting is presentation. Match is unlit today, so this needs an owner
capture review.

**A8. Coast/shore.**
(a) A separate `coast.tscn` created by a coast lane.
(b) Inside `ground.tscn`.
(c) Inside the coastal district scenes.
*Recommendation: (a).* This is 3.7 km of fixtures with its own capacity question (greybox plan
Q5). The marina stays in district 05.

**A9. Rename the world folder.**
(a) Move `scenes/world/brackett_greybox/` to `scenes/world/brackett/` (UIDs preserved) in WA-1.
(b) Keep the greybox name until greybox cleanup.
*Recommendation: (a).* It happens once, before district lanes write production content under a
misleading name.

**B1. Asset-type policy.** Adopt "flat graphics are not models": decals for one-off ground and
wall graphics, ground materials for large finishes, a water shader for the sea and harbour,
road-tool markings on roads, and models only where there is visible thickness. Use the AGENTS.md
and assets.md wording above.
(a) Adopt.
(b) Adopt decals only, and keep material swatches and water as models.
(c) Keep carriers.
*Recommendation: (a).*

**B2. Water surface geometry.**
(a) Allow one engine `PlaneMesh`/`QuadMesh` for flat water surfaces as a named exception.
(b) Keep a Blender-authored water plane, carrying the shader.
*Recommendation: (a).* A flat plane gains nothing from Blender, and the owner asked that water
not be a model. This is the only new mesh exception.

**B3. Sports field finish.**
(a) `d01_sports_surface_01/02` become layered materials on the ground's field region.
(b) All three sports surfaces become decals.
*Recommendation: (a).* The track covers most of the view, and Godot notes large screen-filling
decals cost the most. The field polygon already exists, which also removes the z-fight offset.
`_03` stays a decal.

**B4. Keep decals off cars and characters.**
(a) Add a named `dynamic` render layer, set it in the car, wreck, character, projectile and
effect prefabs, and exclude it from decal cull masks.
(b) Rely on short projection height only.
*Recommendation: (a).* Wheels and low bodies sit inside any ground decal's projection.

**B5. Retire accepted carrier models.** The 16 retired items are 10 flat graphic carriers,
4 ground-finish swatches and 2 water swatches.
(a) Keep record IDs and prefab paths/UIDs (decals). Delete the retired GLBs, `.blend`s and
carrier materials. Add `runtime_type` to the register.
(b) Keep the carriers alongside the new types.
*Recommendation: (a).* Production cleanliness (decision 50). Git history keeps the originals.

**B6. Deferred surface records.**
(a) Road markings 01–04 become 2D texture inputs for RT-03. Parking/loading bays and d08 apron
graphics become district decals. Parking asphalt becomes a material only. Walkways 01–04 retire
(RT-03 generates them). The alley strip waits for RT-03.
(b) Keep all of them deferred as they are.
*Recommendation: (a).* Each is commissioned when its consuming lane needs it.

**C1. Directory layout shape.**
(a) Category/family, split by type.
(b) Category/family with model, textures and materials together under `art/environment/`;
source mirrored under `art/source/environment/`; prefabs, tools and records in matching
category/family folders.
(c) Everything for a family in one folder, prefabs included.
*Recommendation: (b).*

**C2. Scope of the layout change.**
(a) Environment now; vehicles, weapons, characters and effects follow the same convention in a
short follow-up move.
(b) Environment only.
(c) Everything in one move.
*Recommendation: (a).* One convention, without widening the first move. This supersedes the
path shape in decision 36, not its intent.

**C3. Records and tools placement.**
(a) Per-asset records, evidence and tools move into the same category/family tree; the register
stays at `docs/assets/production/queue.json`.
(b) Move art and prefabs only.
*Recommendation: (a).*

**C4. Evidence retention.**
(a) Cap new evidence (2 MB / 8 images per asset, no copied GLB/`.blend`, no raw logs) and prune
the current tree in one cleanup lane.
(b) Same as (a), plus rewrite Git history.
(c) Leave as is.
*Recommendation: (a).* History rewriting is destructive and not needed.

**C5. `docs/spikes`.**
(a) Keep the records and prune evidence folders to the cited results, linking the commit for the
rest.
(b) Leave as is.
(c) Move them into `prototypes/`.
*Recommendation: (a).*

**C6. Move sequencing.**
(a) Move after the mesh-audit report and before mesh-fix lanes, Part B conversions and C2.2a.
(b) After the mesh fixes.
(c) After C2.2a.
*Recommendation: (a).* Nothing is in flight now, and every later lane works on final paths.

**C7. Greybox kit.**
(a) Delete the unreferenced building kit after C2.2a, and move the surviving ground and water
into `art/environment/terrain/` with RT-10.
(b) Keep the greybox folders indefinitely.
*Recommendation: (a).* This matches greybox plan Q7.

**D1. Releasing C2.2a.**
(a) Release the district lanes once C-1, WA-1/WA-2, B-1 and the B-2 decal pilot have landed.
(b) Release now, on today's paths and carrier prefabs.
*Recommendation: (a).* District lanes then write each scene once, on final paths, with the
final graphic types.

## Sources

- Godot docs, fetched 10 October 2026:
  - [Project organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/project_organization.html):
    group assets close to the scenes that use them, feature-based folders, snake_case,
    `.gdignore`.
  - [Using decals](https://docs.godotengine.org/en/stable/tutorials/3d/using_decals.html):
    Forward+/Mobile only; cost mostly from screen coverage, so a few large decals cost more than
    many small ones; distance fade; cull mask for dynamic objects; short projection height for
    culling; 512 clustered elements per view shared with omni/spot lights and reflection probes;
    Mobile limit of 8 decals per mesh; Sorting Offset.
  - [Scene organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html):
    loosely coupled scenes, dependency injection, a "World" node whose children are swapped.
  - [Visibility ranges (HLOD)](https://docs.godotengine.org/en/stable/tutorials/3d/visibility_ranges.html).
- Unreal Engine:
  - [World Partition](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine)
    (fetched). Manual sublevels "often created issues sharing files between multiple users".
    World Partition works with One File Per Actor, Data Layers and HLOD.
  - [One File Per Actor](https://dev.epicgames.com/documentation/en-us/unreal-engine/one-file-per-actor-in-unreal-engine)
    (fetched).
  - The use of Data Layers to group actors by purpose and of sublevels split by discipline is
    from the author's own knowledge.
- Unity: [multi-scene editing](https://docs.unity3d.com/Manual/MultiSceneEditing.html). The page
  needs JavaScript and was not readable here. The points about additive scenes split by
  responsibility and one active scene owning lighting settings are from the author's own
  knowledge.
- Project records: listed at the top of this plan. All counts in "Facts" come from `git ls-files`
  and direct file inspection at `643ee7d5`.
