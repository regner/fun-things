# MESH-AUDIT — exported geometry, 10 October 2026

Phase A: **read-only audit and reusable gate**, not an asset cleanup. Base revision:
`94562be455c455ae1e6a2b5b6739b8d6932da2eb`. No source, export, material, scene,
collision, UID, register, TODO or task-requirements file is changed by this lane.
No Godot/Blender editor session was used. Repository tools and this review were
edited directly; production checks run isolated headless engine children.

## Interpretation and reproduction

The inventory is every exported `.glb` below `art/models/`, including the old
Brackett greybox, characters, vehicles, weapons and effects, plus every saved
`.tscn` below `scenes/prefabs/`. A prefab with repeated instances of one GLB is a
composition too. Nested/inherited scenes, parent transforms, negative/nonuniform
scales, imported-material remaps and saved surface overrides are resolved. Collision
shapes and collision-only GLB nodes are not counted. No runtime scripts, animations,
shader deformation, generated road meshes, engine LODs or gameplay hiding are run.

The tool is [`tools/asset_production/mesh_audit`](../../../tools/asset_production/mesh_audit/README.md).
It uses the existing Python 3.14.2 / numpy 2.5.1 installation; no Blender dependency
or tool installation was added. The full scan is **not** part of the fast canonical
production check. Its 26 synthetic-GLB tests are, via the approved thin
`tools/test_mesh_audit.py` discovery wrapper.

```sh
# Run from the repository root. Outputs must be fresh and outside the checkout.
PYTHONIOENCODING=utf-8 timeout 3600 python -m tools.asset_production.mesh_audit.run \
  --jobs 2 --output C:/tmp/ft/mesh-audit/full-05
python -m unittest tools.test_mesh_audit -v

# Future-asset gate: an audit with findings is not automatically a failed command.
# Select the checks to enforce; exit 0 complete/pass, 1 selected finding, 2 incomplete.
PYTHONIOENCODING=utf-8 timeout 180 python -m tools.asset_production.mesh_audit.run \
  --asset art/models/environment/d08_repair_furniture_04/d08_repair_furniture_04.glb \
  --no-prefabs --fail-on z_fighting_pairs --fail-on zero_area \
  --output C:/tmp/ft/mesh-audit/workbench-gate
```

`audit.json` retains per-input/tool hashes, thresholds, error/completion status,
per-material/primitive face lists, exact exported triangle IDs, pair locators and
containment groups. `face_offset` maps a global pair ID into its primitive-local
triangle ID. This is the actionable detailed receipt; the tables below are its
lean review index. An incomplete/interrupted run has no complete final receipt.

### What the numbers mean

- **Tris/verts** are exported render triangles/accessor rows, not Blender polygon or
  welded vertex counts. Variants count individually; these are library totals, not
  city instance savings or frame-time measurements.
- The brief's normals use **Blender Z-up**. The reader explicitly converts glTF/Godot
  `(x,y,z)` to `(x,-z,y)` in metres, after hierarchy transforms. It uses geometric
  triangle normals, not smoothed shading normals.
- **Bottoms**: normal Z < -0.9 and every vertex within 0.02 m of asset datum zero.
  Elevated downward faces are separately flagged. Datum is not minimum bounds.
- **Z-pairs**: same-facing planes within 1 mm and 0.1 degrees, projected triangle
  overlap strictly greater than 0.0025 m²; opposite-facing pairs require at least
  one double-sided material. Shared edges and ordinary adjacent roof triangles do
  not qualify. Pair counts are not counts of distinct defect sites.
- **Sealed**: full opposing opaque, single-sided flush cover within 0.01 mm, plus
  no sampled visibility of the target. Polygon subtraction unions covers without
  counting overlaps twice. The visibility condition protects deliberate two-sided
  sheets; partial/near contacts remain separate pair findings.
- **Unseen**: outside-bounds rays toward the centroid and three inset corners over
  97 directions: every 15 degrees of yaw at elevations 35/45/60/75 degrees, plus
  zenith. Only opaque front-facing/double-sided geometry occludes. This covers the
  requested camera envelope conservatively for triage, **not every continuous ray**.
- **Interior**: test vertices and four samples against other coordinate-welded,
  outward-oriented, positive-volume, closed 2-manifold islands using three parity
  rays. Open, nonmanifold, inside-out and alpha shells cannot certify containment.
- **Removable candidates / %**: the union of downward single-sided, sealed,
  sampled-unseen and sampled-contained faces, excluding degenerate/nonopaque,
  retained underside and pose-dependent cases. Categories overlap: do not add them.
  This is a candidate estimate, **not permission to delete, proved savings, or a
  silhouette-preservation guarantee**. Small openings, concave crossings between
  samples and unsampled views require source/visual review before removal.
- **Exceptions**: explicit conservative keep rules for boardwalks, marina docks,
  moored hulls, harbour/footbridges, shore edges and quay fixtures. All negative-Z
  normals, including sloping undersides outside check 1's -0.9 threshold, are
  **keep, exception** for water reflections and/or walk-below cameras. Actual
  placement must extend these rules for any other over-water use. Animation/skinning,
  characters, cars, weapons and effects have a separate keep-all pose/orientation
  hold; their measured findings remain visible but candidate savings are zero.
- **Duplicate vertices** require equal *all exported attributes*. Position duplicates
  are recorded separately; normal/UV/tangent/skin/material splits are not loose or
  waste by definition. Degenerate area tolerance is 1e-12 m². No collision counts
  are mixed into these figures.

Above-sun shadows do not independently require downward/interior faces under the
owner's visibility rule. Nevertheless, any removal opening a hole in the retained
upper-view silhouette or shadow caster is rejected. Water and walk-below exceptions
remain explicit, not silently counted as savings.

## Specifically verified: `d08_repair_furniture.04`

The exported workbench has **six** threshold z-fighting triangle pairs. Four are
exact rear coplanarity and two are near-coplanar top paint, not six separate sites:

| Global exported face IDs | Z-up locator / source construction | Overlap m² | Gap m |
| --- | --- | ---: | ---: |
| 2060 / 3189 | Rear drawer housing and rear long apron, Y = -0.32 | 0.04482023 | 0 |
| 2061 / 3189 | Same rear interface | 0.00749075 | 0 |
| 2060 / 3188 | Same rear interface | 0.00761503 | 0 |
| 4129 / 4708 | Rear worktop stop and worktop edge, Y = -0.40 | 0.00347130 | ~0.00000003 |
| 4517 / 4710 | Worktop paint remnant above top surface | 0.00428000 | ~0.00050002 |
| 4515 / 4710 | Same paint remnant | 0.00315000 | ~0.00050002 |

These are geometric GLB observations, not a claim of a captured rendered flicker.
The owner's rear observation is independently supported by the committed authoring
recipe at `tools/asset_production/d08_repair_furniture_04/author.py`: housing center
Y=-0.015, depth 0.61 puts its rear at -0.32; rear apron center -0.29, depth 0.06
also puts its rear at -0.32. Worktop depth 0.80 and stop center -0.385/depth 0.03
both end at -0.40. No `.blend` load or re-export was needed to locate these interfaces.
The paired GLB materials and primitive-local IDs are in the receipt, preserving
source discoverability even though the export joins the original component objects.

Fix owner: **Ironreach repair-furniture family**, source
`art/source/models/environment/d08_repair_furniture_04/d08_repair_furniture_04.blend`.
Remove redundant/interface faces or resolve the source construction; do not apply
an arbitrary prefab offset that changes the silhouette/footprint. The paint-remnant
carrier is also an asset-type review item, not an authorized decal migration here.

## Specifically verified: roof/crown duplicate surface area

`d04_towers.01` has two large upward same-facing overlaps at **Z=53.2 m**:
global triangle pairs **210/318** and **211/319**, each **170.97500337 m²**,
with a GLB plane gap of about **0.00000381 m**. Both use `glassward_indigo`.
The committed `tools/asset_production/d04_towers_01/author.py` independently
explains the coincidence: the crown drum at 51.5 m with height 3.4 m and the inset
roof deck at 53.1 m with thickness 0.2 m both end at 53.2 m. This is duplicate
roof/crown surface area, not merely two adjacent triangles on the same roof.
Preserve the crown rim, retained roof UVs and full tower envelope when resolving it.

`d04_podiums.02` also has upward roof-cap overlaps at **Z=9.6 m**:
**210/3126** and **211/3127**, each **128.79546390 m²**, with about
**0.00000095 m** separation (`glassward_office_slate` / `glassward_frame`).
The upper setback mass (7.8 + 3.6/2) and fascia (9.42 + 0.36/2) share that top.
Its separate quiet roof ends at 9.62 m, so much of the measured cap overlap can be
hidden beneath it: **do not label all 257+ m² a visible flicker area**. The final
roof table retains additional eave/coping locators for source inspection.

Fix owners: **Glassward towers and podiums**, preserving shared source output sets.
These GLB/source-recipe checks satisfy the requested roof verification without
claiming a rendered screenshot or authorizing a broader redesign.

## Fix-lane constraints and asset-type holds

All suggested lanes below are **proposed follow-up work**, not commissioned edits.
Group variants sharing a `.blend` in the same lane, and edit/re-export that source's
complete output set together. For environmental families the source convention is
`art/source/models/environment/<asset_id>/<asset_id>.blend`; variants in that
asset directory share the source. Brackett shared district-source membership is
explicit in `art/source/models/brackett_greybox/source_manifest.json`, not inferred
from the export filename. The actor, car, weapon and effect sources retain their
existing dedicated family directories and rig/pose contracts.

Every fix lane must **not change silhouette, footprint, pivot, collision or UVs of
kept faces**. Preserve material slots, linked imports, resource UIDs, saved scene
identities and socket/animation contracts. Kept vertex attribute seams are intentional
until source evidence proves otherwise. Re-run this gate, source/export validation,
fixed upper-camera and rear/roof views, shadow/hole checks, prefab roundtrips and the
appropriate production checks. Any collision or gameplay change is outside these
appearance-only lanes and needs its own authorization and movement/network checks.

**Possible decal/material switches — owner review only; do not schedule geometry
fixes or migrations for these types yet:**

- Flat ground carriers: `city_ground_finishes.01/.02/.04/.05`,
  `d01_sports_surface.01-.03`, `d03_court_graphics.01/.02`,
  `d04_forecourt_graphics.01-.03`, `d05_quay_paving.01/.02`.
- Water swatches: `city_water_look.01/.02`; keep the existing Brackett water surface
  separate from a swatch/type decision. No water geometry is removed in this lane.
- Flush graphic carriers/artwork overrides: campus, neighbourhood, community,
  corporate, civic, quay, Lantern-row, parade, retail, repair and Dockward graphics;
  parking artwork, poster/fascia/sign faces and wear-patch prisms such as the
  workbench paint remnant. Many already reuse hardware with face-only material
  overrides: do not duplicate or delete their underlying accepted fixtures.
- Procedural road/crosswalk materials remain the road-tool owner's responsibility;
  no replacement road render geometry is proposed.

Separate from those holds, prioritize visible rear/roof defects before purely
invisible savings. The rankings below use geometric z-pair counts as defect triage,
not an assertion that every internal overlap is visible or that each pair is a
separate rendered flicker site. Confirm the overlap region at gameplay views before
choosing which original surface/material to retain.

## Validation and retained diagnostics

- Synthetic serialized GLB suite: **26 tests**, including positive/negative cases
  for every requested check, datum/axis transforms, shared-edge rejection, area,
  plane and angle thresholds, opposite double-sided pairs, partial/full contact,
  cover-union double counting, 128 repeated covers, closed/open/inside-out/alpha
  shells, sparse/strided/unindexed accessors, UV seams, malformed inputs, nested and
  inherited transforms/materials, import remaps, collision exclusion, keep policy,
  repeated-same-GLB prefabs and gate exit behavior. No source fixture assets are edited.
- `C:/tmp/ft/mesh-audit/cli-clean/audit.json`: strict clean synthetic gate returns 0.
  `cli-bad/audit.json`: malformed GLB returns 2 with `complete=false`.
  The synthetic duplicate-face test returns 1 for selected z-fighting, with complete
  JSON and unchanged input bytes. Expected nonzero gates are not scan failures.
- During development, dense marina flush contacts exposed exponential accumulation
  of **zero-area** polygon fragments. `C:/tmp/ft/mesh-audit/marina-profile.log`
  preserves the bounded 90-second diagnostic failure. The fixed subtraction discards
  zero-area fragments; `marina-fixed-01/audit.json` finishes the same 6,392-triangle
  asset in 9.92 seconds. The 128-cover regression protects the fix. Timing is
  contended diagnostic evidence, not a performance claim.
- `full-01`, `full-02`, and `full-03` are explicitly superseded, incomplete development
  runs; only their own process trees were stopped. The first two predate the dense
  contact fix; the third predates the deliberate-two-sided-sheet safeguard. They
  are **not** inventory acceptance evidence. `superseded.txt` records their disposition.
- `full-04` was superseded to extend exception retention to sloping undersides as
  well as check 1's steep-downward subset; a dedicated negative-Z/-0.85 regression
  protects this distinction. Its counts are not the final candidate-savings report.
  The completed final repeat matches every non-policy asset metric and every prefab
  summary; only exception/candidate totals change on 56 assets. Final module hashes
  match the current tool files.
- `production-01` passed all canonical layers; final validation and inventory
  receipts are indexed below. No new GDScript, scenes or resources were authored,
  so no editor save/UID migration or visual/gameplay acceptance is claimed.

## Final measured inventory

Final receipt: `C:/tmp/ft/mesh-audit/full-05/audit.json`.
SHA-256: `5216ac62845a9823fe3d952135bd66cb74f3995274307c8276a652a66c190b7d`.
Input-manifest SHA-256: `cdfa72b3670e894b818a3085afba1e63574285b2b6658628eaac64290a831a05`.
Source revision recorded by runner: `7168fdaa5e33345720107cc2833815c7bd65559e`. Tool module hashes are in the JSON.
**Frozen review base:** `256c2b1b996a4292d73f7776173af2f3f8fe8a32`, explicitly approved by the supervisor after the final rebase. Further unrelated main integration is deferred to the integrator; only changed audit inputs would reopen this freeze. `art/` and `scenes/` remain identical to the original base.

**271 GLBs, 1,043,260 triangles, 668,260 exported vertices.**
**369,654 candidate triangles (35.43%)** after keep/pose holds;
**2,422 model z-pairs** across 86 GLBs.
**298 prefabs resolved; 44 compositions checked**, including repeated same-GLB instances;
**1,080 additional cross-instance z-pairs** across 10 prefabs.
No parse/unsupported-input errors. Contended scan wall time: 1080.48 seconds (not a benchmark).

| Metric | Count |
| --- | --- |
| sealed | 5,766 |
| bottoms | 6,691 |
| elevated undersides | 91,330 |
| keep exception | 50,629 |
| inside closed island | 211,609 |
| unseen sampled | 446,653 |
| zero area | 1,212 |
| duplicate vertices | 81 |
| loose vertices | 0 |
| position duplicates | 124,113 |

Vertex/degenerate counts refer only to what survived GLB export; they do not prove the Blender source has no unused data. Position duplicates are mostly necessary attribute splits, not claimed savings.

### Families ranked by candidate savings

| Rank | Source family | GLBs | Candidate tris | % of family | Z-pairs |
| --- | --- | --- | --- | --- | --- |
| 1 | d08_workshop_buildings | 4 | 38,099 | 51.63% | 123 |
| 2 | d04_towers | 4 | 34,276 | 54.80% | 280 |
| 3 | d09_warehouses | 3 | 29,889 | 51.59% | 26 |
| 4 | city_planting | 7 | 27,441 | 53.14% | 0 |
| 5 | d09_storage | 4 | 24,594 | 60.85% | 72 |
| 6 | d02_house_family | 4 | 16,758 | 34.34% | 47 |
| 7 | d08_repair_furniture | 4 | 15,654 | 36.35% | 15 |
| 8 | d01_academic_buildings | 3 | 13,552 | 31.96% | 118 |
| 9 | city_lights | 8 | 12,116 | 43.06% | 10 |
| 10 | city_shop_fittings | 10 | 11,256 | 48.58% | 18 |
| 11 | d01_lighthouse | 1 | 10,488 | 56.69% | 50 |
| 12 | d03_apartment_family | 11 | 9,680 | 40.23% | 90 |
| 13 | d09_cranes | 2 | 9,317 | 54.43% | 17 |
| 14 | city_roof_details | 5 | 8,507 | 48.69% | 0 |
| 15 | d04_podiums | 3 | 8,259 | 37.20% | 64 |
| 16 | d05_harbour_hall | 2 | 7,813 | 40.50% | 4 |
| 17 | city_small_shop_shells | 4 | 7,360 | 39.43% | 42 |
| 18 | d06_harbour_footbridge | 14 | 7,205 | 18.28% | 352 |
| 19 | d06_shopfront_blocks | 2 | 6,541 | 46.14% | 158 |
| 20 | d01_sports_pavilion | 1 | 6,391 | 73.31% | 166 |
| 21 | d07_retail_buildings | 3 | 6,380 | 42.50% | 77 |
| 22 | city_waste | 3 | 4,580 | 42.47% | 4 |
| 23 | city_traffic_fixtures | 3 | 4,548 | 47.55% | 3 |
| 24 | d06_entertainment_hall | 3 | 4,524 | 35.89% | 72 |
| 25 | city_sign_supports | 4 | 4,435 | 42.35% | 8 |
| 26 | d05_quay_frontages | 4 | 4,405 | 30.74% | 6 |
| 27 | city_barriers | 9 | 4,196 | 14.87% | 0 |
| 28 | city_marina_docks | 6 | 4,192 | 14.97% | 106 |
| 29 | d07_trolley_shelter | 2 | 3,778 | 47.90% | 34 |
| 30 | city_service_furniture | 3 | 3,387 | 42.57% | 4 |
| 31 | city_harbour_bridge | 3 | 2,944 | 20.55% | 74 |
| 32 | d02_corner_shop | 2 | 2,802 | 29.73% | 0 |
| 33 | d03_laundry_frames | 3 | 2,691 | 34.73% | 0 |
| 34 | d06_southern_shopping_parade | 2 | 2,432 | 33.78% | 98 |
| 35 | city_moored_yachts | 2 | 2,147 | 14.68% | 5 |
| 36 | d02_domestic_details | 4 | 2,097 | 32.28% | 3 |
| 37 | city_seating | 3 | 1,178 | 43.12% | 4 |
| 38 | d04_corporate_graphics | 1 | 1,000 | 60.24% | 0 |
| 39 | d06_poster_drum | 2 | 884 | 16.49% | 0 |
| 40 | city_quay_furniture | 8 | 764 | 6.58% | 0 |
| 41 | city_shore_edges | 9 | 371 | 14.86% | 14 |
| 42 | brackett_greybox | 40 | 193 | 1.97% | 8 |
| 43 | d07_sign_island | 2 | 180 | 7.04% | 0 |
| 44 | city_parking_furniture | 2 | 178 | 11.01% | 0 |
| 45 | city_boardwalk | 14 | 154 | 0.98% | 0 |
| 46 | d03_community_graphics | 1 | 10 | 6.41% | 0 |
| 47 | city_ground_finishes | 4 | 8 | 16.67% | 0 |
| 48 | characters/coral_courier | 1 | 0 | 0.00% | 8 |
| 49 | characters/pedestrian_worker | 1 | 0 | 0.00% | 0 |
| 50 | characters/shared_humanoid | 2 | 0 | 0.00% | 0 |
| 51 | effects/weapon_effects | 7 | 0 | 0.00% | 0 |
| 52 | city_water_look | 2 | 0 | 0.00% | 0 |
| 53 | d01_sports_surface | 3 | 0 | 0.00% | 0 |
| 54 | d03_court_graphics | 2 | 0 | 0.00% | 0 |
| 55 | d04_forecourt_graphics | 3 | 0 | 0.00% | 0 |
| 56 | d05_quay_paving | 2 | 0 | 0.00% | 0 |
| 57 | vehicles/car_crate_a | 1 | 0 | 0.00% | 82 |
| 58 | vehicles/car_latch_a | 1 | 0 | 0.00% | 68 |
| 59 | vehicles/car_sable_a | 1 | 0 | 0.00% | 88 |
| 60 | vehicles/vehicle_wrecks_01 | 1 | 0 | 0.00% | 2 |
| 61 | vehicles/vehicle_wrecks_02 | 1 | 0 | 0.00% | 2 |
| 62 | vehicles/vehicle_wrecks_03 | 1 | 0 | 0.00% | 0 |
| 63 | weapons/dock_thumper | 2 | 0 | 0.00% | 0 |
| 64 | weapons/pistol_coral_stub | 1 | 0 | 0.00% | 0 |
| 65 | weapons/smg_wedgewire | 1 | 0 | 0.00% | 0 |

### Families ranked for visible-defect triage (z-fighting first)

Exterior-sample pairs have at least one face seen by the sampled rays; this is a triage cue, not proof that the overlapping region itself flickers. Internal pairs remain in the total and are lower-priority cleanup.

| Rank | Source family | Z-pairs | Exterior-sample pairs | Candidate tris |
| --- | --- | --- | --- | --- |
| 1 | d06_harbour_footbridge | 352 | 352 | 7,205 |
| 2 | d04_towers | 280 | 264 | 34,276 |
| 3 | d01_sports_pavilion | 166 | 152 | 6,391 |
| 4 | d08_workshop_buildings | 123 | 76 | 38,099 |
| 5 | d06_entertainment_hall | 72 | 72 | 4,524 |
| 6 | d09_storage | 72 | 60 | 24,594 |
| 7 | city_harbour_bridge | 74 | 54 | 2,944 |
| 8 | d01_lighthouse | 50 | 50 | 10,488 |
| 9 | d06_shopfront_blocks | 158 | 45 | 6,541 |
| 10 | d07_retail_buildings | 77 | 35 | 6,380 |
| 11 | d01_academic_buildings | 118 | 32 | 13,552 |
| 12 | city_marina_docks | 106 | 28 | 4,192 |
| 13 | d07_trolley_shelter | 34 | 28 | 3,778 |
| 14 | d06_southern_shopping_parade | 98 | 26 | 2,432 |
| 15 | d09_warehouses | 26 | 26 | 29,889 |
| 16 | city_small_shop_shells | 42 | 21 | 7,360 |
| 17 | d04_podiums | 64 | 19 | 8,259 |
| 18 | d08_repair_furniture | 15 | 11 | 15,654 |
| 19 | d09_cranes | 17 | 8 | 9,317 |
| 20 | city_lights | 10 | 8 | 12,116 |
| 21 | brackett_greybox | 8 | 8 | 193 |
| 22 | characters/coral_courier | 8 | 6 | 0 |
| 23 | city_moored_yachts | 5 | 5 | 2,147 |
| 24 | d05_harbour_hall | 4 | 4 | 7,813 |
| 25 | city_traffic_fixtures | 3 | 3 | 4,548 |
| 26 | d02_domestic_details | 3 | 3 | 2,097 |
| 27 | vehicles/vehicle_wrecks_01 | 2 | 2 | 0 |
| 28 | d02_house_family | 47 | 1 | 16,758 |
| 29 | d03_apartment_family | 90 | 0 | 9,680 |
| 30 | vehicles/car_sable_a | 88 | 0 | 0 |
| 31 | vehicles/car_crate_a | 82 | 0 | 0 |
| 32 | vehicles/car_latch_a | 68 | 0 | 0 |
| 33 | city_shop_fittings | 18 | 0 | 11,256 |
| 34 | city_shore_edges | 14 | 0 | 371 |
| 35 | city_sign_supports | 8 | 0 | 4,435 |
| 36 | d05_quay_frontages | 6 | 0 | 4,405 |
| 37 | city_seating | 4 | 0 | 1,178 |
| 38 | city_service_furniture | 4 | 0 | 3,387 |
| 39 | city_waste | 4 | 0 | 4,580 |
| 40 | vehicles/vehicle_wrecks_02 | 2 | 0 | 0 |
| 41 | characters/pedestrian_worker | 0 | 0 | 0 |
| 42 | characters/shared_humanoid | 0 | 0 | 0 |
| 43 | effects/weapon_effects | 0 | 0 | 0 |
| 44 | city_barriers | 0 | 0 | 4,196 |
| 45 | city_boardwalk | 0 | 0 | 154 |
| 46 | city_ground_finishes | 0 | 0 | 8 |
| 47 | city_parking_furniture | 0 | 0 | 178 |
| 48 | city_planting | 0 | 0 | 27,441 |
| 49 | city_quay_furniture | 0 | 0 | 764 |
| 50 | city_roof_details | 0 | 0 | 8,507 |
| 51 | city_water_look | 0 | 0 | 0 |
| 52 | d01_sports_surface | 0 | 0 | 0 |
| 53 | d02_corner_shop | 0 | 0 | 2,802 |
| 54 | d03_community_graphics | 0 | 0 | 10 |
| 55 | d03_court_graphics | 0 | 0 | 0 |
| 56 | d03_laundry_frames | 0 | 0 | 2,691 |
| 57 | d04_corporate_graphics | 0 | 0 | 1,000 |
| 58 | d04_forecourt_graphics | 0 | 0 | 0 |
| 59 | d05_quay_paving | 0 | 0 | 0 |
| 60 | d06_poster_drum | 0 | 0 | 884 |
| 61 | d07_sign_island | 0 | 0 | 180 |
| 62 | vehicles/vehicle_wrecks_03 | 0 | 0 | 0 |
| 63 | weapons/dock_thumper | 0 | 0 | 0 |
| 64 | weapons/pistol_coral_stub | 0 | 0 | 0 |
| 65 | weapons/smg_wedgewire | 0 | 0 | 0 |

### Suggested follow-up family lanes

Start with the specifically verified repair-furniture rear defect, then these high-savings/high-defect source families. These are proposals subject to the constraints and type holds above, not authorization to remove all listed candidates.

| Proposed lane | Shared-source groups below art/source/models/environment/ unless noted | Candidate tris | Z-pairs |
| --- | --- | --- | --- |
| d06_harbour_footbridge | `d06_harbour_footbridge_01/*.blend`; `d06_harbour_footbridge_02/*.blend`; `d06_harbour_footbridge_03/*.blend`; `d06_harbour_footbridge_04/*.blend`; `d06_harbour_footbridge_05/*.blend`; `d06_harbour_footbridge_06/*.blend` | 7,205 | 352 |
| d04_towers | `d04_towers_01/*.blend`; `d04_towers_02/*.blend`; `d04_towers_03/*.blend`; `d04_towers_04/*.blend` | 34,276 | 280 |
| d01_sports_pavilion | `d01_sports_pavilion_01/*.blend` | 6,391 | 166 |
| d08_workshop_buildings | `d08_workshop_buildings_01/*.blend`; `d08_workshop_buildings_02/*.blend`; `d08_workshop_buildings_03/*.blend`; `d08_workshop_buildings_04/*.blend` | 38,099 | 123 |
| d06_entertainment_hall | `d06_entertainment_hall_01/*.blend`; `d06_entertainment_hall_02/*.blend`; `d06_entertainment_hall_03/*.blend` | 4,524 | 72 |
| d09_storage | `d09_storage_01/*.blend`; `d09_storage_02/*.blend`; `d09_storage_03/*.blend`; `d09_storage_04/*.blend` | 24,594 | 72 |
| city_harbour_bridge | `city_harbour_bridge_01/*.blend`; `city_harbour_bridge_02/*.blend`; `city_harbour_bridge_03/*.blend` | 2,944 | 74 |
| d01_lighthouse | `d01_lighthouse_01/*.blend` | 10,488 | 50 |
| d09_warehouses | `d09_warehouses_01/*.blend`; `d09_warehouses_02/*.blend`; `d09_warehouses_03/*.blend` | 29,889 | 26 |
| city_planting | `city_planting_01/*.blend`; `city_planting_02/*.blend`; `city_planting_03/*.blend`; `city_planting_04/*.blend`; `city_planting_05/*.blend` | 27,441 | 0 |
| d02_house_family | `d02_house_family_01/*.blend`; `d02_house_family_02/*.blend`; `d02_house_family_03/*.blend`; `d02_house_family_04/*.blend` | 16,758 | 47 |
| d08_repair_furniture | `d08_repair_furniture_01/*.blend`; `d08_repair_furniture_02/*.blend`; `d08_repair_furniture_03/*.blend`; `d08_repair_furniture_04/*.blend` | 15,654 | 15 |
| d01_academic_buildings | `d01_academic_buildings_01/*.blend`; `d01_academic_buildings_02/*.blend`; `d01_academic_buildings_03/*.blend` | 13,552 | 118 |

Do not split warm/cool, corner/end/straight, bridge-height or other exports from the same source across simultaneous writers. Apartment/quay/shop assemblies also need their saved-prefab cross-instance checks; fix contact faces in the source without shifting the assembly footprint.

### Roof/coping coplanarity verification

| GLB | Global faces | Height Z-up m | Overlapping m² | Materials | Gap m | Both full triangles? |
| --- | --- | --- | --- | --- | --- | --- |
| d04_towers_01 | [211, 319] | 53.2000 | 170.97500337 | glassward_indigo, glassward_indigo | 3.81e-06 | no |
| d04_towers_01 | [210, 318] | 53.2000 | 170.97500337 | glassward_indigo, glassward_indigo | 3.81e-06 | no |
| d04_podiums_02 | [211, 3127] | 9.6000 | 128.79546390 | glassward_office_slate, glassward_frame | 9.5e-07 | no |
| d04_podiums_02 | [210, 3126] | 9.6000 | 128.79546390 | glassward_office_slate, glassward_frame | 9.5e-07 | no |
| d01_academic_buildings_01 | [20078, 20123] | 10.8400 | 12.45118941 | academic_field_green, academic_field_green | 0.0 | no |
| d01_academic_buildings_01 | [20078, 20167] | 10.8400 | 10.21892223 | academic_field_green, academic_field_green | 0.0 | no |
| d01_academic_buildings_01 | [434, 567] | 10.7000 | 3.28373916 | academic_pale_stone, academic_pale_stone | 0.0 | no |
| d01_academic_buildings_01 | [434, 699] | 10.7000 | 3.09955250 | academic_pale_stone, academic_pale_stone | 0.0 | no |
| d01_academic_buildings_01 | [20079, 20167] | 10.8400 | 2.23226717 | academic_field_green, academic_field_green | 0.0 | no |
| d06_shopfront_blocks_02 | [7315, 8647] | 4.6000 | 1.57730530 | shell_warm_structural_trim, shell_muted_plum_render | 0.0 | no |

These are duplicated roof/eave/coping *surface areas* at the stated height, not a claim that each whole mesh is duplicated. Roof details without threshold hits are not falsely counted from shared triangulation edges. The full GLB-local pair locators remain in the JSON for source selection and rendered verification.

### Highest candidate material groups (complete group lists are in JSON)

| GLB | Material / primitive | Candidate tris | Group tris |
| --- | --- | --- | --- |
| d09_storage_01 | storage_body_blue / primitive_0 | 10,859 | 14,812 |
| d08_workshop_buildings_03 | ironreach_roof_petrol / primitive_5 | 10,591 | 16,692 |
| d01_lighthouse_01 | lighthouse_petrol_metal / primitive_3 | 7,901 | 13,096 |
| d01_academic_buildings_01 | academic_pale_stone / primitive_2 | 6,564 | 19,732 |
| d09_storage_02 | storage_body_blue / primitive_0 | 6,035 | 8,188 |
| d08_workshop_buildings_02 | ironreach_roof_petrol / primitive_5 | 5,868 | 10,764 |
| d04_towers_02 | glassward_indigo / primitive_0 | 5,516 | 6,156 |
| d09_warehouses_01 | dock_frame_navy / primitive_3 | 4,895 | 11,736 |
| d02_house_family_03 | crescents_ivory_trim / primitive_2 | 4,807 | 12,104 |
| d04_towers_01 | glassward_indigo / primitive_0 | 4,364 | 4,860 |
| d09_warehouses_02 | dock_frame_navy / primitive_3 | 4,231 | 11,092 |
| d05_harbour_hall_01 | harbour_hall_limestone_trim / primitive_2 | 3,921 | 7,144 |
| d09_warehouses_01 | dock_wall_steel / primitive_1 | 3,834 | 4,748 |
| d08_workshop_buildings_01 | ironreach_roof_petrol / primitive_5 | 3,393 | 6,360 |
| d04_towers_03 | glassward_indigo / primitive_0 | 3,200 | 3,564 |
| d06_entertainment_hall_01 | hall_frame_teal / primitive_3 | 3,031 | 6,224 |
| d08_workshop_buildings_02 | ironreach_pale_band / primitive_2 | 3,003 | 5,592 |
| city_planting_04_broad | tree_warm_umber / primitive_0 | 2,890 | 4,218 |
| d02_house_family_02 | crescents_ivory_trim / primitive_2 | 2,856 | 8,972 |
| d09_cranes_02 | crane_working_amber / primitive_2 | 2,839 | 4,160 |

### Degenerate and duplicate/loose vertex material split

All nonzero material groups are listed below; all unlisted groups have zero exact duplicates, loose vertices and zero-area faces. Repeated wheel-node primitives are aggregated by material here; the JSON preserves each node and face ID. Pose holds do not hide malformed render triangles, but their repair still requires the rig/vehicle source owner.

| GLB | Material | Zero-area tris | Exact duplicate verts | Loose verts | Affected primitives |
| --- | --- | --- | --- | --- | --- |
| car_crate_a | trim | 192 | 0 | 0 | 4 |
| car_crate_a | wheel_hub | 192 | 0 | 0 | 4 |
| car_latch_a | trim | 192 | 0 | 0 | 4 |
| car_latch_a | wheel_hub | 192 | 0 | 0 | 4 |
| car_sable_a | trim | 192 | 0 | 0 | 4 |
| car_sable_a | wheel_hub | 192 | 0 | 0 | 4 |
| d03_apartment_family_11 | terrace_bluegrey_roof | 0 | 10 | 0 | 1 |
| d03_apartment_family_11 | terrace_pale_frame | 0 | 6 | 0 | 1 |
| d04_towers_01 | glassward_frame | 0 | 5 | 0 | 1 |
| d04_towers_02 | glassward_frame | 0 | 5 | 0 | 1 |
| d04_towers_03 | glassward_frame | 0 | 9 | 0 | 1 |
| d04_towers_04 | glassward_frame | 0 | 8 | 0 | 1 |
| d06_harbour_footbridge_05_main | deck_pale_fascia | 0 | 4 | 0 | 1 |
| d06_harbour_footbridge_05_main | deck_warm_pale | 0 | 7 | 0 | 1 |
| d06_harbour_footbridge_05_quay | deck_pale_fascia | 0 | 2 | 0 | 1 |
| d06_harbour_footbridge_05_quay | deck_warm_pale | 0 | 3 | 0 | 1 |
| d06_harbour_footbridge_05_south | deck_pale_fascia | 0 | 2 | 0 | 1 |
| d06_harbour_footbridge_05_south | deck_warm_pale | 0 | 3 | 0 | 1 |
| d06_southern_shopping_parade_01 | parade_muted_plum_render | 0 | 16 | 0 | 1 |
| pedestrian_worker_a | worker_palette | 60 | 0 | 0 | 1 |
| vehicle_wrecks_01 | wreck_sable_plum | 0 | 1 | 0 | 1 |

### Prefab compositions

The remaining single-instance/empty prefabs are resolved and listed in the JSON but have no additional cross-instance check. Do not add these repeated-instance triangle counts to the library totals above.

| Prefab below scenes/prefabs/ | GLB instances | Tris | Cross-instance Z-pairs |
| --- | --- | --- | --- |
| environment/city_barriers_02.tscn | 3 | 2,416 | 0 |
| environment/city_barriers_04.tscn | 2 | 1,752 | 0 |
| environment/city_barriers_07.tscn | 6 | 18,852 | 0 |
| environment/city_barriers_07_closed.tscn | 6 | 18,852 | 0 |
| environment/city_quay_furniture_02.tscn | 3 | 2,064 | 0 |
| environment/city_quay_furniture_02_corner_deck.tscn | 4 | 3,612 | 0 |
| environment/city_quay_furniture_02_corner_landward.tscn | 4 | 4,140 | 0 |
| environment/city_quay_furniture_02_corner_quay.tscn | 4 | 3,612 | 0 |
| environment/city_quay_furniture_02_end_deck.tscn | 2 | 1,576 | 0 |
| environment/city_quay_furniture_02_end_landward.tscn | 2 | 1,752 | 0 |
| environment/city_quay_furniture_02_end_quay.tscn | 2 | 1,576 | 0 |
| environment/city_quay_furniture_02_straight_deck.tscn | 3 | 2,064 | 0 |
| environment/city_quay_furniture_02_straight_landward.tscn | 3 | 2,416 | 0 |
| environment/city_small_shop_shells_02_fitted.tscn | 11 | 21,268 | 0 |
| environment/city_small_shop_shells_03_fitted.tscn | 16 | 32,040 | 12 |
| environment/city_small_shop_shells_04_fitted.tscn | 6 | 12,080 | 0 |
| environment/city_traffic_fixtures_02_mounted.tscn | 2 | 8,136 | 0 |
| environment/d02_corner_shop_01.tscn | 9 | 18,624 | 0 |
| environment/d03_apartment_family_01.tscn | 34 | 53,364 | 123 |
| environment/d03_apartment_family_02.tscn | 40 | 68,820 | 183 |
| environment/d03_apartment_family_03.tscn | 16 | 23,296 | 0 |
| environment/d03_apartment_family_04.tscn | 41 | 55,832 | 164 |
| environment/d03_apartment_family_11.tscn | 3 | 1,540 | 7 |
| environment/d05_civic_graphics_01_hall_preview.tscn | 3 | 20,948 | 0 |
| environment/d05_harbour_hall_02_hall_preview.tscn | 2 | 19,292 | 0 |
| environment/d05_quay_frontages_01.tscn | 8 | 15,136 | 0 |
| environment/d05_quay_frontages_02.tscn | 15 | 28,528 | 0 |
| environment/d05_quay_frontages_03.tscn | 7 | 14,452 | 0 |
| environment/d05_quay_frontages_04.tscn | 12 | 21,792 | 13 |
| environment/d06_shopfront_blocks_01.tscn | 28 | 54,616 | 0 |
| environment/d06_shopfront_blocks_02_fitted.tscn | 16 | 34,288 | 0 |
| environment/d06_shopfront_blocks_03_fitted.tscn | 16 | 31,128 | 12 |
| environment/d06_southern_shopping_parade_02.tscn | 31 | 55,244 | 282 |
| environment/d06_southern_shopping_parade_02_bay.tscn | 5 | 8,540 | 0 |
| environment/d06_southern_shopping_parade_03_reference.tscn | 32 | 58,440 | 282 |
| environment/d07_retail_buildings_03_attached.tscn | 2 | 10,476 | 2 |
| environment/d07_trolley_shelter_03.tscn | 3 | 12,888 | 0 |
| environment/d08_workshop_buildings_04_family.tscn | 3 | 43,960 | 0 |
| environment/d09_storage_04.tscn | 3 | 7,452 | 0 |
| environment/d09_storage_04_pair.tscn | 2 | 4,968 | 0 |
| environment/d09_warehouses_03_fit_low.tscn | 2 | 31,020 | 0 |
| environment/d09_warehouses_03_fit_ridge.tscn | 2 | 36,508 | 0 |
| pistol_coral_stub/preview_game_camera.tscn | 7 | 42,794 | 0 |
| player_character/preview.tscn | 2 | 12,322 | 0 |

### Per-GLB summary

Paths are below `art/models/`, with `.glb` omitted for readability. **Keep** is the count of negative-Z exception faces (including slopes), or the separate pose/orientation hold. Bottom/elevated counts still use the requested -0.9 threshold. Candidate percentages are not approved deletion quotas.

| GLB | Tris | Verts | Candidate tris (%) | Z-pairs | Sealed | Bottoms | Elevated | Keep/hold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| brackett_greybox/apartment | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/apartment_slab | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/apartment_small | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/campus_annex | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/campus_classroom | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/campus_hall | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/dock_shed | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/entertainment_hall | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/ground_00_00 | 722 | 754 | 5 (0.69%) | 0 | 0 | 0 | 5 | - |
| brackett_greybox/ground_00_01 | 1,671 | 1,723 | 19 (1.14%) | 0 | 0 | 0 | 19 | - |
| brackett_greybox/ground_00_02 | 350 | 426 | 43 (12.29%) | 0 | 0 | 0 | 34 | - |
| brackett_greybox/ground_01_00 | 872 | 900 | 3 (0.34%) | 0 | 0 | 0 | 3 | - |
| brackett_greybox/ground_01_01 | 945 | 1,021 | 22 (2.33%) | 0 | 0 | 0 | 22 | - |
| brackett_greybox/ground_01_02 | 685 | 739 | 24 (3.50%) | 0 | 0 | 0 | 20 | - |
| brackett_greybox/ground_02_00 | 369 | 395 | 4 (1.08%) | 0 | 0 | 0 | 4 | - |
| brackett_greybox/ground_02_01 | 806 | 824 | 2 (0.25%) | 0 | 0 | 0 | 2 | - |
| brackett_greybox/ground_02_02 | 823 | 851 | 3 (0.36%) | 0 | 0 | 0 | 3 | - |
| brackett_greybox/ground_03_00 | 62 | 82 | 2 (3.23%) | 0 | 0 | 0 | 2 | - |
| brackett_greybox/ground_03_01 | 885 | 915 | 4 (0.45%) | 0 | 0 | 0 | 4 | - |
| brackett_greybox/ground_03_02 | 328 | 356 | 4 (1.22%) | 0 | 0 | 0 | 4 | - |
| brackett_greybox/house | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/office | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/quay_hall | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/quay_house | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/quay_row | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/repair_shed | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/retail_box | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/retail_large | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/retail_small | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/semi | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/shop | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/shop_row | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/terrace | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/tower_high | 88 | 192 | 4 (4.55%) | 4 | 0 | 2 | 2 | - |
| brackett_greybox/tower_mid | 88 | 192 | 4 (4.55%) | 4 | 0 | 2 | 2 | - |
| brackett_greybox/warehouse | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/warehouse_small | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/water | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| brackett_greybox/workshop | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| brackett_greybox/workshop_large | 44 | 96 | 2 (4.55%) | 0 | 0 | 2 | 0 | - |
| characters/coral_courier/coral_courier | 11,600 | 7,235 | 0 (0.00%) | 8 | 0 | 36 | 973 | pose hold |
| characters/pedestrian_worker/pedestrian_worker_a | 14,528 | 9,030 | 0 (0.00%) | 0 | 0 | 36 | 1,218 | pose hold |
| characters/shared_humanoid/shared_humanoid_bind_v1 | 3,528 | 2,415 | 0 (0.00%) | 0 | 0 | 0 | 148 | pose hold |
| characters/shared_humanoid/shared_humanoid_player_motion_v1 | 3,528 | 2,415 | 0 (0.00%) | 0 | 0 | 0 | 148 | pose hold |
| effects/weapon_effects/weapon_effects_a_chip | 108 | 72 | 0 (0.00%) | 0 | 0 | 0 | 10 | pose hold |
| effects/weapon_effects/weapon_effects_a_fire_lobe | 168 | 115 | 0 (0.00%) | 0 | 0 | 0 | 12 | pose hold |
| effects/weapon_effects/weapon_effects_a_muzzle_drop | 336 | 230 | 0 (0.00%) | 0 | 0 | 0 | 84 | pose hold |
| effects/weapon_effects/weapon_effects_a_smoke_puff | 168 | 115 | 0 (0.00%) | 0 | 0 | 0 | 18 | pose hold |
| effects/weapon_effects/weapon_effects_a_spark | 168 | 115 | 0 (0.00%) | 0 | 0 | 0 | 0 | pose hold |
| effects/weapon_effects/weapon_effects_a_tracer | 64 | 160 | 0 (0.00%) | 0 | 0 | 0 | 12 | pose hold |
| effects/weapon_effects/weapon_effects_a_trail_puff | 168 | 115 | 0 (0.00%) | 0 | 0 | 0 | 12 | pose hold |
| environment/city_barriers_01/city_barriers_01 | 892 | 576 | 30 (3.36%) | 0 | 0 | 30 | 0 | - |
| environment/city_barriers_03/city_barriers_03 | 380 | 260 | 18 (4.74%) | 0 | 0 | 14 | 0 | - |
| environment/city_barriers_05/city_barriers_05 | 6,240 | 3,504 | 550 (8.81%) | 0 | 0 | 0 | 168 | - |
| environment/city_barriers_06/city_barriers_06_corner | 2,468 | 2,576 | 705 (28.57%) | 0 | 156 | 30 | 440 | - |
| environment/city_barriers_06/city_barriers_06_line | 1,924 | 1,968 | 600 (31.19%) | 0 | 120 | 18 | 396 | - |
| environment/city_barriers_06/city_barriers_06_terminal | 1,632 | 1,648 | 480 (29.41%) | 0 | 138 | 24 | 280 | - |
| environment/city_barriers_07/city_barriers_07_left | 6,892 | 4,256 | 741 (10.75%) | 0 | 0 | 0 | 288 | - |
| environment/city_barriers_07/city_barriers_07_mount | 904 | 992 | 322 (35.62%) | 0 | 0 | 0 | 220 | - |
| environment/city_barriers_07/city_barriers_07_right | 6,888 | 4,304 | 750 (10.89%) | 0 | 0 | 0 | 298 | - |
| environment/city_boardwalk_01/city_boardwalk_01 | 2,268 | 1,512 | 0 (0.00%) | 0 | 0 | 0 | 210 | 894 water/below |
| environment/city_boardwalk_02/city_boardwalk_02 | 3,716 | 1,924 | 27 (0.73%) | 0 | 0 | 0 | 384 | 1503 water/below |
| environment/city_boardwalk_02/city_boardwalk_02_22p5 | 932 | 484 | 8 (0.86%) | 0 | 0 | 0 | 96 | 369 water/below |
| environment/city_boardwalk_02/city_boardwalk_02_45 | 1,860 | 964 | 15 (0.81%) | 0 | 0 | 0 | 192 | 761 water/below |
| environment/city_boardwalk_03/city_boardwalk_03 | 164 | 108 | 0 (0.00%) | 0 | 0 | 0 | 20 | 86 water/below |
| environment/city_boardwalk_03/city_boardwalk_03_inner_22p5 | 416 | 248 | 0 (0.00%) | 0 | 0 | 0 | 104 | 229 water/below |
| environment/city_boardwalk_03/city_boardwalk_03_inner_45 | 704 | 408 | 0 (0.00%) | 0 | 0 | 0 | 200 | 389 water/below |
| environment/city_boardwalk_03/city_boardwalk_03_inner_90 | 1,280 | 728 | 0 (0.00%) | 0 | 0 | 0 | 392 | 712 water/below |
| environment/city_boardwalk_03/city_boardwalk_03_outer_22p5 | 416 | 248 | 0 (0.00%) | 0 | 0 | 0 | 104 | 228 water/below |
| environment/city_boardwalk_03/city_boardwalk_03_outer_45 | 704 | 408 | 0 (0.00%) | 0 | 0 | 0 | 200 | 395 water/below |
| environment/city_boardwalk_03/city_boardwalk_03_outer_90 | 1,280 | 728 | 0 (0.00%) | 0 | 0 | 0 | 392 | 710 water/below |
| environment/city_boardwalk_03/city_boardwalk_03_terminal | 164 | 108 | 0 (0.00%) | 0 | 0 | 0 | 20 | 86 water/below |
| environment/city_boardwalk_04/city_boardwalk_04 | 756 | 504 | 104 (13.76%) | 0 | 0 | 20 | 50 | 298 water/below |
| environment/city_boardwalk_05/city_boardwalk_05 | 1,092 | 568 | 0 (0.00%) | 0 | 0 | 0 | 142 | 446 water/below |
| environment/city_ground_finishes_01/city_ground_finishes_01 | 12 | 24 | 2 (16.67%) | 0 | 0 | 0 | 2 | - |
| environment/city_ground_finishes_02/city_ground_finishes_02 | 12 | 24 | 2 (16.67%) | 0 | 0 | 0 | 2 | - |
| environment/city_ground_finishes_04/city_ground_finishes_04 | 12 | 24 | 2 (16.67%) | 0 | 0 | 0 | 2 | - |
| environment/city_ground_finishes_05/city_ground_finishes_05 | 12 | 24 | 2 (16.67%) | 0 | 0 | 0 | 2 | - |
| environment/city_harbour_bridge_01/city_harbour_bridge_01 | 3,600 | 2,235 | 1,478 (41.06%) | 48 | 0 | 0 | 344 | 1496 water/below |
| environment/city_harbour_bridge_02/city_harbour_bridge_02 | 8,648 | 5,330 | 972 (11.24%) | 4 | 56 | 36 | 792 | 3588 water/below |
| environment/city_harbour_bridge_03/city_harbour_bridge_03 | 2,080 | 1,294 | 494 (23.75%) | 22 | 0 | 36 | 164 | 872 water/below |
| environment/city_lights_01/city_lights_01_cool | 2,424 | 1,341 | 934 (38.53%) | 3 | 0 | 58 | 230 | - |
| environment/city_lights_01/city_lights_01_warm | 2,424 | 1,341 | 934 (38.53%) | 3 | 0 | 58 | 230 | - |
| environment/city_lights_02/city_lights_02 | 3,616 | 1,824 | 1,605 (44.39%) | 0 | 0 | 30 | 662 | - |
| environment/city_lights_02/city_lights_02_cool | 3,616 | 1,824 | 1,605 (44.39%) | 0 | 0 | 30 | 662 | - |
| environment/city_lights_03/city_lights_03_cool | 3,640 | 2,092 | 1,514 (41.59%) | 0 | 0 | 58 | 338 | - |
| environment/city_lights_03/city_lights_03_warm | 3,640 | 2,092 | 1,514 (41.59%) | 0 | 0 | 58 | 338 | - |
| environment/city_lights_04/city_lights_04_cool | 4,388 | 2,212 | 2,005 (45.69%) | 2 | 0 | 0 | 952 | - |
| environment/city_lights_04/city_lights_04_warm | 4,388 | 2,212 | 2,005 (45.69%) | 2 | 0 | 0 | 952 | - |
| environment/city_marina_docks_01/city_marina_docks_01 | 6,392 | 3,933 | 918 (14.36%) | 38 | 120 | 0 | 612 | 2832 water/below |
| environment/city_marina_docks_02/city_marina_docks_02 | 5,076 | 3,123 | 778 (15.33%) | 34 | 90 | 0 | 486 | 2154 water/below |
| environment/city_marina_docks_03/city_marina_docks_03 | 10,340 | 6,370 | 1,552 (15.01%) | 8 | 109 | 0 | 842 | 4534 water/below |
| environment/city_marina_docks_04/city_marina_docks_04 | 3,856 | 2,340 | 724 (18.78%) | 26 | 48 | 0 | 371 | 1682 water/below |
| environment/city_marina_docks_04/city_marina_docks_04_bumper | 188 | 115 | 0 (0.00%) | 0 | 0 | 0 | 18 | 78 water/below |
| environment/city_marina_docks_05/city_marina_docks_05 | 2,144 | 1,388 | 220 (10.26%) | 0 | 0 | 18 | 248 | 914 water/below |
| environment/city_moored_yachts_01/city_moored_yachts_01 | 7,626 | 4,525 | 1,073 (14.07%) | 3 | 0 | 40 | 799 | 3214 water/below |
| environment/city_moored_yachts_02/city_moored_yachts_02 | 7,004 | 4,040 | 1,074 (15.33%) | 2 | 0 | 72 | 730 | 2859 water/below |
| environment/city_parking_furniture_01/city_parking_furniture_01 | 476 | 292 | 42 (8.82%) | 0 | 0 | 42 | 0 | - |
| environment/city_parking_furniture_03/city_parking_furniture_03 | 1,140 | 712 | 136 (11.93%) | 0 | 0 | 64 | 36 | - |
| environment/city_planting_01/city_planting_01 | 1,428 | 1,008 | 422 (29.55%) | 0 | 0 | 34 | 68 | - |
| environment/city_planting_02/city_planting_02 | 3,456 | 1,856 | 896 (25.93%) | 0 | 0 | 256 | 128 | - |
| environment/city_planting_03/city_planting_03 | 4,932 | 2,482 | 2,293 (46.49%) | 0 | 0 | 30 | 180 | - |
| environment/city_planting_04/city_planting_04_broad | 19,418 | 9,721 | 12,016 (61.88%) | 0 | 0 | 54 | 3,004 | - |
| environment/city_planting_04/city_planting_04_compact | 19,282 | 9,655 | 11,125 (57.70%) | 0 | 0 | 60 | 1,932 | - |
| environment/city_planting_05/city_planting_05_short_tuft | 1,170 | 603 | 242 (20.68%) | 0 | 0 | 36 | 109 | - |
| environment/city_planting_05/city_planting_05_spreading_clump | 1,950 | 1,005 | 447 (22.92%) | 0 | 0 | 60 | 211 | - |
| environment/city_quay_furniture_01/city_quay_furniture_01 | 2,520 | 1,619 | 0 (0.00%) | 0 | 0 | 18 | 244 | 988 water/below |
| environment/city_quay_furniture_02/city_quay_furniture_02_corner | 696 | 416 | 0 (0.00%) | 0 | 0 | 0 | 80 | 320 water/below |
| environment/city_quay_furniture_02/city_quay_furniture_02_end | 604 | 336 | 0 (0.00%) | 0 | 0 | 0 | 24 | 288 water/below |
| environment/city_quay_furniture_02/city_quay_furniture_02_post_deck | 972 | 504 | 84 (8.64%) | 0 | 2 | 10 | 80 | 386 water/below |
| environment/city_quay_furniture_02/city_quay_furniture_02_post_landward | 1,148 | 592 | 84 (7.32%) | 0 | 0 | 70 | 80 | 470 water/below |
| environment/city_quay_furniture_02/city_quay_furniture_02_post_quay | 972 | 504 | 84 (8.64%) | 0 | 0 | 10 | 80 | 394 water/below |
| environment/city_quay_furniture_02/city_quay_furniture_02_straight | 120 | 128 | 0 (0.00%) | 0 | 0 | 0 | 8 | 32 water/below |
| environment/city_quay_furniture_03/city_quay_furniture_03 | 4,576 | 2,480 | 512 (11.19%) | 0 | 0 | 20 | 368 | 1848 water/below |
| environment/city_roof_details_01/city_roof_details_01 | 3,536 | 1,788 | 1,761 (49.80%) | 0 | 0 | 72 | 364 | - |
| environment/city_roof_details_02/city_roof_details_02 | 6,180 | 3,132 | 3,069 (49.66%) | 0 | 37 | 72 | 518 | - |
| environment/city_roof_details_03/city_roof_details_03 | 2,632 | 1,582 | 1,036 (39.36%) | 0 | 0 | 20 | 232 | - |
| environment/city_roof_details_04/city_roof_details_04 | 2,428 | 1,295 | 1,200 (49.42%) | 0 | 2 | 0 | 286 | - |
| environment/city_roof_details_05/city_roof_details_05 | 2,696 | 1,467 | 1,441 (53.45%) | 0 | 1 | 0 | 156 | - |
| environment/city_seating_01/city_seating_01 | 1,316 | 805 | 668 (50.76%) | 4 | 4 | 36 | 90 | - |
| environment/city_seating_02/city_seating_02 | 564 | 345 | 198 (35.11%) | 0 | 0 | 18 | 36 | - |
| environment/city_seating_03/city_seating_03 | 852 | 432 | 312 (36.62%) | 0 | 0 | 28 | 59 | - |
| environment/city_service_furniture_01/city_service_furniture_01 | 3,352 | 2,067 | 1,502 (44.81%) | 0 | 4 | 18 | 300 | - |
| environment/city_service_furniture_02/city_service_furniture_02 | 1,536 | 912 | 602 (39.19%) | 4 | 0 | 232 | 0 | - |
| environment/city_service_furniture_03/city_service_furniture_03 | 3,068 | 1,900 | 1,283 (41.82%) | 0 | 8 | 56 | 226 | - |
| environment/city_shop_fittings_01/city_shop_fittings_01 | 1,212 | 616 | 471 (38.86%) | 0 | 0 | 0 | 76 | - |
| environment/city_shop_fittings_02/city_shop_fittings_02 | 1,656 | 1,072 | 789 (47.64%) | 6 | 0 | 0 | 136 | - |
| environment/city_shop_fittings_03/city_shop_fittings_03_double | 2,312 | 1,164 | 1,114 (48.18%) | 0 | 0 | 114 | 90 | - |
| environment/city_shop_fittings_03/city_shop_fittings_03_single | 2,312 | 1,164 | 1,114 (48.18%) | 0 | 0 | 114 | 90 | - |
| environment/city_shop_fittings_04/city_shop_fittings_04 | 2,952 | 1,674 | 2,084 (70.60%) | 0 | 0 | 50 | 76 | - |
| environment/city_shop_fittings_05/city_shop_fittings_05 | 1,368 | 692 | 669 (48.90%) | 6 | 0 | 26 | 78 | - |
| environment/city_shop_fittings_06/city_shop_fittings_06_double | 3,984 | 2,000 | 1,478 (37.10%) | 0 | 0 | 0 | 312 | - |
| environment/city_shop_fittings_06/city_shop_fittings_06_single | 1,992 | 1,000 | 736 (36.95%) | 0 | 0 | 0 | 156 | - |
| environment/city_shop_fittings_07/city_shop_fittings_07 | 1,760 | 892 | 1,003 (56.99%) | 6 | 0 | 30 | 122 | - |
| environment/city_shop_fittings_08/city_shop_fittings_08 | 3,624 | 2,396 | 1,798 (49.61%) | 0 | 0 | 0 | 204 | - |
| environment/city_shore_edges_01/city_shore_edges_01 | 128 | 240 | 14 (10.94%) | 0 | 6 | 2 | 8 | 30 water/below |
| environment/city_shore_edges_02/city_shore_edges_02 | 128 | 234 | 10 (7.81%) | 0 | 8 | 0 | 14 | 30 water/below |
| environment/city_shore_edges_03/city_shore_edges_03 | 966 | 699 | 220 (22.77%) | 14 | 18 | 0 | 87 | 301 water/below |
| environment/city_shore_edges_04/city_shore_edges_04_quay_corner | 128 | 230 | 20 (15.62%) | 0 | 16 | 0 | 16 | 24 water/below |
| environment/city_shore_edges_04/city_shore_edges_04_quay_end | 176 | 316 | 27 (15.34%) | 0 | 24 | 0 | 24 | 36 water/below |
| environment/city_shore_edges_04/city_shore_edges_04_rock_corner | 426 | 329 | 12 (2.82%) | 0 | 12 | 0 | 48 | 156 water/below |
| environment/city_shore_edges_04/city_shore_edges_04_rock_end | 240 | 242 | 6 (2.50%) | 0 | 6 | 0 | 24 | 78 water/below |
| environment/city_shore_edges_04/city_shore_edges_04_wall_corner | 128 | 224 | 28 (21.88%) | 0 | 16 | 4 | 12 | 24 water/below |
| environment/city_shore_edges_04/city_shore_edges_04_wall_end | 176 | 313 | 34 (19.32%) | 0 | 24 | 4 | 20 | 36 water/below |
| environment/city_sign_supports_01/city_sign_supports_01 | 2,720 | 1,792 | 1,334 (49.04%) | 0 | 0 | 0 | 204 | - |
| environment/city_sign_supports_02/city_sign_supports_02 | 2,448 | 1,596 | 1,026 (41.91%) | 4 | 0 | 36 | 168 | - |
| environment/city_sign_supports_03/city_sign_supports_03 | 2,636 | 1,711 | 1,116 (42.34%) | 4 | 0 | 36 | 186 | - |
| environment/city_sign_supports_04/city_sign_supports_04 | 2,668 | 1,773 | 959 (35.94%) | 0 | 0 | 58 | 384 | - |
| environment/city_small_shop_shells_01/city_small_shop_shells_01 | 4,516 | 2,492 | 1,671 (37.00%) | 9 | 56 | 104 | 334 | - |
| environment/city_small_shop_shells_02/city_small_shop_shells_02 | 4,188 | 2,320 | 1,742 (41.60%) | 9 | 44 | 200 | 206 | - |
| environment/city_small_shop_shells_03/city_small_shop_shells_03 | 6,420 | 3,600 | 2,563 (39.92%) | 16 | 84 | 302 | 322 | - |
| environment/city_small_shop_shells_04/city_small_shop_shells_04 | 3,540 | 1,940 | 1,384 (39.10%) | 8 | 32 | 140 | 202 | - |
| environment/city_traffic_fixtures_01/city_traffic_fixtures_01 | 2,016 | 1,079 | 400 (19.84%) | 0 | 0 | 22 | 158 | - |
| environment/city_traffic_fixtures_02/city_traffic_fixtures_02 | 6,120 | 3,651 | 3,706 (60.56%) | 3 | 0 | 0 | 466 | - |
| environment/city_traffic_fixtures_03/city_traffic_fixtures_03 | 1,428 | 800 | 442 (30.95%) | 0 | 0 | 22 | 156 | - |
| environment/city_waste_01/city_waste_01 | 1,676 | 1,002 | 620 (36.99%) | 0 | 2 | 18 | 114 | - |
| environment/city_waste_02/city_waste_02 | 3,052 | 1,908 | 1,150 (37.68%) | 0 | 0 | 50 | 168 | - |
| environment/city_waste_03/city_waste_03 | 6,056 | 3,744 | 2,810 (46.40%) | 4 | 0 | 36 | 544 | - |
| environment/city_water_look_01/city_water_look_01 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/city_water_look_02/city_water_look_02 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d01_academic_buildings_01/d01_academic_buildings_01 | 28,758 | 21,604 | 9,227 (32.08%) | 96 | 72 | 14 | 1,246 | - |
| environment/d01_academic_buildings_02/d01_academic_buildings_02 | 10,048 | 7,561 | 3,194 (31.79%) | 18 | 3 | 8 | 448 | - |
| environment/d01_academic_buildings_03/d01_academic_buildings_03 | 3,596 | 2,716 | 1,131 (31.45%) | 4 | 2 | 8 | 152 | - |
| environment/d01_lighthouse_01/d01_lighthouse_01 | 18,500 | 11,991 | 10,488 (56.69%) | 50 | 80 | 62 | 2,880 | - |
| environment/d01_sports_pavilion_01/d01_sports_pavilion_01 | 8,718 | 5,395 | 6,391 (73.31%) | 166 | 36 | 64 | 1,052 | - |
| environment/d01_sports_surface_01/d01_sports_surface_01 | 516 | 516 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d01_sports_surface_02/d01_sports_surface_02 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d01_sports_surface_03/d01_sports_surface_03 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d02_corner_shop_01/d02_corner_shop_01 | 6,292 | 3,290 | 1,770 (28.13%) | 0 | 39 | 40 | 696 | - |
| environment/d02_corner_shop_02/d02_corner_shop_02 | 3,132 | 1,600 | 1,032 (32.95%) | 0 | 2 | 18 | 276 | - |
| environment/d02_domestic_details_01/d02_domestic_details_01 | 1,256 | 640 | 148 (11.78%) | 0 | 2 | 18 | 90 | - |
| environment/d02_domestic_details_02/d02_domestic_details_02 | 1,328 | 674 | 203 (15.29%) | 0 | 4 | 29 | 94 | - |
| environment/d02_domestic_details_03/d02_domestic_details_03 | 2,220 | 1,248 | 885 (39.86%) | 0 | 2 | 18 | 144 | - |
| environment/d02_domestic_details_04/d02_domestic_details_04 | 1,692 | 982 | 861 (50.89%) | 3 | 0 | 0 | 138 | - |
| environment/d02_house_family_01/d02_house_family_01 | 8,312 | 4,318 | 2,623 (31.56%) | 7 | 42 | 42 | 646 | - |
| environment/d02_house_family_02/d02_house_family_02 | 12,848 | 6,668 | 4,079 (31.75%) | 13 | 52 | 44 | 996 | - |
| environment/d02_house_family_03/d02_house_family_03 | 16,820 | 8,732 | 6,283 (37.35%) | 13 | 67 | 46 | 1,396 | - |
| environment/d02_house_family_04/d02_house_family_04 | 10,826 | 5,687 | 3,773 (34.85%) | 14 | 47 | 70 | 844 | - |
| environment/d03_apartment_family_05/d03_apartment_family_05 | 2,532 | 1,744 | 1,010 (39.89%) | 12 | 0 | 2 | 220 | - |
| environment/d03_apartment_family_06/d03_apartment_family_06_inside | 10,084 | 6,946 | 4,156 (41.21%) | 48 | 0 | 4 | 880 | - |
| environment/d03_apartment_family_06/d03_apartment_family_06_outside | 5,044 | 3,464 | 2,054 (40.72%) | 24 | 0 | 2 | 440 | - |
| environment/d03_apartment_family_07/d03_apartment_family_07 | 1,444 | 1,008 | 550 (38.09%) | 0 | 0 | 2 | 136 | - |
| environment/d03_apartment_family_08/d03_apartment_family_08 | 2,724 | 1,930 | 903 (33.15%) | 6 | 0 | 16 | 202 | - |
| environment/d03_apartment_family_09/d03_apartment_family_09 | 1,944 | 1,296 | 921 (47.38%) | 0 | 4 | 0 | 180 | - |
| environment/d03_apartment_family_10/d03_apartment_family_10_end | 24 | 48 | 6 (25.00%) | 0 | 4 | 0 | 4 | - |
| environment/d03_apartment_family_10/d03_apartment_family_10_inside | 80 | 144 | 28 (35.00%) | 0 | 24 | 0 | 16 | - |
| environment/d03_apartment_family_10/d03_apartment_family_10_outside | 64 | 120 | 22 (34.38%) | 0 | 20 | 0 | 12 | - |
| environment/d03_apartment_family_10/d03_apartment_family_10_straight | 48 | 96 | 14 (29.17%) | 0 | 12 | 0 | 8 | - |
| environment/d03_apartment_family_11/d03_apartment_family_11 | 72 | 126 | 16 (22.22%) | 0 | 10 | 0 | 6 | - |
| environment/d03_community_graphics_02/d03_community_graphics_02 | 156 | 280 | 10 (6.41%) | 0 | 0 | 0 | 6 | - |
| environment/d03_court_graphics_01/d03_court_graphics_01 | 256 | 256 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d03_court_graphics_02/d03_court_graphics_02 | 48 | 64 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d03_laundry_frames_01/d03_laundry_frames_01 | 2,652 | 1,834 | 1,116 (42.08%) | 0 | 0 | 36 | 216 | - |
| environment/d03_laundry_frames_03/d03_laundry_frames_03_sheet | 2,900 | 1,584 | 946 (32.62%) | 0 | 0 | 128 | 108 | - |
| environment/d03_laundry_frames_03/d03_laundry_frames_03_towel | 2,196 | 1,200 | 629 (28.64%) | 0 | 0 | 96 | 82 | - |
| environment/d04_corporate_graphics_01/d04_corporate_graphics_01 | 1,660 | 1,007 | 1,000 (60.24%) | 0 | 0 | 0 | 156 | - |
| environment/d04_forecourt_graphics_01/d04_forecourt_graphics_01 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d04_forecourt_graphics_02/d04_forecourt_graphics_02 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d04_forecourt_graphics_03/d04_forecourt_graphics_03 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d04_podiums_01/d04_podiums_01 | 9,864 | 6,594 | 3,516 (35.64%) | 22 | 44 | 60 | 856 | - |
| environment/d04_podiums_02/d04_podiums_02 | 6,912 | 4,608 | 2,368 (34.26%) | 12 | 21 | 20 | 620 | - |
| environment/d04_podiums_03/d04_podiums_03 | 5,424 | 3,668 | 2,375 (43.79%) | 30 | 39 | 60 | 426 | - |
| environment/d04_towers_01/d04_towers_01 | 16,728 | 11,216 | 9,470 (56.61%) | 73 | 102 | 10 | 1,486 | - |
| environment/d04_towers_02/d04_towers_02 | 19,556 | 12,992 | 10,830 (55.38%) | 69 | 56 | 10 | 1,772 | - |
| environment/d04_towers_03/d04_towers_03 | 15,140 | 9,848 | 8,186 (54.07%) | 69 | 63 | 10 | 1,632 | - |
| environment/d04_towers_04/d04_towers_04 | 11,128 | 7,408 | 5,790 (52.03%) | 69 | 60 | 10 | 990 | - |
| environment/d05_harbour_hall_01/d05_harbour_hall_01 | 17,736 | 10,881 | 6,782 (38.24%) | 0 | 6 | 90 | 1,542 | - |
| environment/d05_harbour_hall_02/d05_harbour_hall_02 | 1,556 | 871 | 1,031 (66.26%) | 4 | 0 | 56 | 100 | - |
| environment/d05_quay_frontages_01/d05_quay_frontages_01 | 3,076 | 1,850 | 900 (29.26%) | 0 | 9 | 40 | 220 | - |
| environment/d05_quay_frontages_02/d05_quay_frontages_02 | 4,408 | 2,715 | 1,381 (31.33%) | 6 | 17 | 59 | 333 | - |
| environment/d05_quay_frontages_03/d05_quay_frontages_03 | 3,108 | 1,948 | 904 (29.09%) | 0 | 10 | 37 | 250 | - |
| environment/d05_quay_frontages_04/d05_quay_frontages_04 | 3,736 | 2,289 | 1,220 (32.66%) | 0 | 30 | 42 | 328 | - |
| environment/d05_quay_paving_01/d05_quay_paving_01 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d05_quay_paving_02/d05_quay_paving_02 | 2 | 4 | 0 (0.00%) | 0 | 0 | 0 | 0 | - |
| environment/d06_entertainment_hall_01/d06_entertainment_hall_01 | 10,288 | 6,283 | 4,226 (41.08%) | 72 | 0 | 66 | 846 | - |
| environment/d06_entertainment_hall_02/d06_entertainment_hall_02 | 2,040 | 1,156 | 272 (13.33%) | 0 | 0 | 0 | 272 | - |
| environment/d06_entertainment_hall_03/d06_entertainment_hall_03 | 276 | 200 | 26 (9.42%) | 0 | 0 | 0 | 26 | - |
| environment/d06_harbour_footbridge_01/d06_harbour_footbridge_01 | 236 | 212 | 0 (0.00%) | 0 | 0 | 0 | 26 | 89 water/below |
| environment/d06_harbour_footbridge_02/d06_harbour_footbridge_02 | 60 | 72 | 0 (0.00%) | 0 | 0 | 0 | 6 | 14 water/below |
| environment/d06_harbour_footbridge_03/d06_harbour_footbridge_03 | 60 | 72 | 0 (0.00%) | 0 | 0 | 0 | 6 | 14 water/below |
| environment/d06_harbour_footbridge_04/d06_harbour_footbridge_04 | 60 | 72 | 0 (0.00%) | 0 | 0 | 0 | 6 | 14 water/below |
| environment/d06_harbour_footbridge_05/d06_harbour_footbridge_05_main | 1,908 | 1,728 | 72 (3.77%) | 0 | 46 | 0 | 18 | 185 water/below |
| environment/d06_harbour_footbridge_05/d06_harbour_footbridge_05_quay | 1,908 | 1,728 | 60 (3.14%) | 0 | 33 | 0 | 18 | 175 water/below |
| environment/d06_harbour_footbridge_05/d06_harbour_footbridge_05_south | 1,908 | 1,728 | 61 (3.20%) | 0 | 33 | 0 | 18 | 179 water/below |
| environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06_junction | 4,320 | 3,840 | 836 (19.35%) | 24 | 0 | 0 | 400 | 1686 water/below |
| environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06_main | 8,424 | 7,360 | 1,692 (20.09%) | 96 | 96 | 0 | 684 | 3330 water/below |
| environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06_quay | 8,424 | 7,360 | 1,816 (21.56%) | 96 | 72 | 0 | 684 | 3358 water/below |
| environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06_south | 8,424 | 7,360 | 1,828 (21.70%) | 96 | 72 | 0 | 684 | 3379 water/below |
| environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06_span | 2,808 | 2,496 | 756 (26.92%) | 40 | 0 | 0 | 260 | 1100 water/below |
| environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06_support_mid | 432 | 384 | 42 (9.72%) | 0 | 6 | 10 | 30 | 168 water/below |
| environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06_support_tall | 432 | 384 | 42 (9.72%) | 0 | 6 | 10 | 30 | 168 water/below |
| environment/d06_poster_drum_01/d06_poster_drum_01 | 2,296 | 1,556 | 442 (19.25%) | 0 | 124 | 62 | 62 | - |
| environment/d06_poster_drum_02/d06_poster_drum_02 | 3,064 | 2,076 | 442 (14.43%) | 0 | 124 | 62 | 62 | - |
| environment/d06_shopfront_blocks_02/d06_shopfront_blocks_02 | 8,668 | 4,764 | 4,144 (47.81%) | 150 | 126 | 380 | 462 | - |
| environment/d06_shopfront_blocks_03/d06_shopfront_blocks_03 | 5,508 | 3,084 | 2,397 (43.52%) | 8 | 102 | 172 | 359 | - |
| environment/d06_southern_shopping_parade_01/d06_southern_shopping_parade_01 | 4,004 | 2,736 | 1,927 (48.13%) | 98 | 24 | 98 | 312 | - |
| environment/d06_southern_shopping_parade_03/d06_southern_shopping_parade_03 | 3,196 | 1,632 | 505 (15.80%) | 0 | 18 | 18 | 288 | - |
| environment/d07_retail_buildings_01/d07_retail_buildings_01 | 6,804 | 4,536 | 2,837 (41.70%) | 33 | 30 | 36 | 594 | - |
| environment/d07_retail_buildings_02/d07_retail_buildings_02 | 4,536 | 3,024 | 1,871 (41.25%) | 36 | 8 | 12 | 408 | - |
| environment/d07_retail_buildings_03/d07_retail_buildings_03 | 3,672 | 2,448 | 1,672 (45.53%) | 8 | 12 | 22 | 318 | - |
| environment/d07_sign_island_01/d07_sign_island_01 | 1,916 | 1,457 | 94 (4.91%) | 0 | 0 | 94 | 0 | - |
| environment/d07_sign_island_02/d07_sign_island_02 | 640 | 380 | 86 (13.44%) | 0 | 4 | 18 | 50 | - |
| environment/d07_trolley_shelter_01/d07_trolley_shelter_01 | 3,592 | 2,159 | 2,332 (64.92%) | 34 | 128 | 54 | 348 | - |
| environment/d07_trolley_shelter_02/d07_trolley_shelter_02 | 4,296 | 3,550 | 1,446 (33.66%) | 0 | 0 | 48 | 359 | - |
| environment/d08_repair_furniture_01/d08_repair_furniture_01 | 6,868 | 4,397 | 3,256 (47.41%) | 6 | 0 | 18 | 648 | - |
| environment/d08_repair_furniture_02/d08_repair_furniture_02 | 19,944 | 10,731 | 5,443 (27.29%) | 3 | 16 | 36 | 1,208 | - |
| environment/d08_repair_furniture_03/d08_repair_furniture_03 | 10,352 | 6,560 | 3,871 (37.39%) | 0 | 22 | 64 | 772 | - |
| environment/d08_repair_furniture_04/d08_repair_furniture_04 | 5,900 | 3,728 | 3,084 (52.27%) | 6 | 14 | 72 | 495 | - |
| environment/d08_workshop_buildings_01/d08_workshop_buildings_01 | 14,932 | 9,678 | 7,186 (48.12%) | 14 | 282 | 18 | 1,506 | - |
| environment/d08_workshop_buildings_02/d08_workshop_buildings_02 | 23,616 | 14,480 | 12,136 (51.39%) | 40 | 270 | 24 | 2,308 | - |
| environment/d08_workshop_buildings_03/d08_workshop_buildings_03 | 29,828 | 18,212 | 16,724 (56.07%) | 54 | 646 | 30 | 2,896 | - |
| environment/d08_workshop_buildings_04/d08_workshop_buildings_04 | 5,412 | 3,608 | 2,053 (37.93%) | 15 | 72 | 12 | 542 | - |
| environment/d09_cranes_01/d09_cranes_01 | 8,588 | 5,924 | 4,618 (53.77%) | 6 | 40 | 2 | 834 | - |
| environment/d09_cranes_02/d09_cranes_02 | 8,528 | 5,882 | 4,699 (55.10%) | 11 | 34 | 2 | 748 | - |
| environment/d09_storage_01/d09_storage_01 | 20,100 | 11,074 | 13,241 (65.88%) | 30 | 8 | 88 | 2,918 | - |
| environment/d09_storage_02/d09_storage_02 | 13,476 | 7,762 | 8,415 (62.44%) | 30 | 8 | 88 | 1,790 | - |
| environment/d09_storage_03/d09_storage_03 | 4,356 | 2,688 | 1,896 (43.53%) | 12 | 0 | 30 | 398 | - |
| environment/d09_storage_04/d09_storage_04 | 2,484 | 1,656 | 1,042 (41.95%) | 0 | 28 | 20 | 202 | - |
| environment/d09_warehouses_01/d09_warehouses_01 | 26,920 | 16,470 | 14,113 (52.43%) | 7 | 0 | 18 | 2,454 | - |
| environment/d09_warehouses_02/d09_warehouses_02 | 21,432 | 13,095 | 10,333 (48.21%) | 5 | 0 | 18 | 2,034 | - |
| environment/d09_warehouses_03/d09_warehouses_03 | 9,588 | 5,810 | 5,443 (56.77%) | 14 | 0 | 18 | 900 | - |
| vehicles/car_crate_a/car_crate_a | 11,256 | 7,920 | 0 (0.00%) | 82 | 0 | 48 | 668 | pose hold |
| vehicles/car_latch_a/car_latch_a | 10,480 | 7,232 | 0 (0.00%) | 68 | 0 | 48 | 596 | pose hold |
| vehicles/car_sable_a/car_sable_a | 11,116 | 7,731 | 0 (0.00%) | 88 | 0 | 48 | 650 | pose hold |
| vehicles/vehicle_wrecks_01/vehicle_wrecks_01 | 9,768 | 7,259 | 0 (0.00%) | 2 | 402 | 16 | 904 | pose hold |
| vehicles/vehicle_wrecks_02/vehicle_wrecks_02 | 9,292 | 7,009 | 0 (0.00%) | 2 | 373 | 16 | 820 | pose hold |
| vehicles/vehicle_wrecks_03/vehicle_wrecks_03 | 8,176 | 6,176 | 0 (0.00%) | 0 | 263 | 16 | 707 | pose hold |
| weapons/dock_thumper/dock_thumper_launcher_a | 8,204 | 9,067 | 0 (0.00%) | 0 | 0 | 0 | 508 | pose hold |
| weapons/dock_thumper/dock_thumper_rocket_a | 3,650 | 3,123 | 0 (0.00%) | 0 | 0 | 18 | 173 | pose hold |
| weapons/pistol_coral_stub/pistol_coral_stub | 2,424 | 1,384 | 0 (0.00%) | 0 | 0 | 38 | 178 | pose hold |
| weapons/smg_wedgewire/smg_wedgewire_a | 3,748 | 2,989 | 0 (0.00%) | 0 | 0 | 12 | 273 | pose hold |

### Final checks

- `timeout 1500 python tools/production_checks.py --output C:/tmp/ft/lanes/mesh-audit/production-frozen`: **PASS**, pinned engine `4.8.dev7.official.c971f93e7`, saved identities, formatting, zero-warning lint, explicit owned-script compilation, Python tests, clean mirror import, complete GUT suite and intentional negative GUT diagnostic.
- Explicit compiler child: `python tools/script_checks.py --godot <mise-pin> --gdstyle <mise-pin> --output .../production-frozen/script-checks`: **350 owned scripts passed**.
- Python: Ran 60 tests in 1.919s; PASS. The mesh-audit subtree contributes 26 tests and requires no Blender/Godot invocation.
- GUT: Scripts              43, Tests               233, Passing Tests       233, Asserts            9111. No new runtime diagnostics; the expected intentional failure exits 1 and is verified by the runner.
- Independent `python -m unittest discover -s tools -p "test_*.py"`: PASS, Ran 60 tests in 1.710s. Final canonical discovery also uses `*test*.py` and includes the slope regression.
- `git diff --check`, art/scene unchanged checks, and no-staged-files checks are part of the final handoff. No asset repair or rendered/animation/gameplay acceptance is claimed.

**Remaining work:** independent reviewer acceptance of this audit, rendered/source confirmation of proposed removals and defect sites, owner asset-type decisions, then separately assigned family fix lanes. Sampled visibility is not a deletion oracle. No product or collision change is bundled here.
