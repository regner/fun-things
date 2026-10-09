# city_small_shop_shells.01 — narrow inline shop shell

9 October 2026. Original source/export candidate for ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2`, workspace `wks_59891ad7a05813e5`,
branch `art/register-production-20261009`; requested Astra MEDIUM production brief.
Commission `commission.md` at `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661` and the
specific dispatch authorize these reversible production dimensions. Historical
concept-only restrictions are superseded. **Not READY; independent acceptance is
pending.** This worker produces source/export and scratch assembly evidence;
ROOT/integrator retain acceptance and all engine/world integration.

## Original design and source mapping

A 6.4 m narrow frontage extends 14 m deep. A higher straight front parapet, lower
side/rear parapets, two quiet longitudinal roof folds, structural end piers and
head course establish an ordinary inline shop. The rear has one scupper, rain
hopper and downpipe. Flat party walls remain unornamented for joining. Quiet blue
roof, muted plum render, warm structural trim and dark plinth follow the accepted
smooth art direction and Signal Row v03 B05; Broadlot supplies ordinary commercial
context. Reference images informed proportions and palette, never measurements.
No tenant identity, landmark form, upper accommodation or unnecessary variant.

- Editable source: `art/source/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.blend`.
- Collection: `export_city_small_shop_shells_01`; identity root `city_small_shop_shells_01`.
- Explicit game export: `art/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.glb`.
- Reproduction: `tools/asset_production/city_small_shop_shells_01/`.
- Evidence: [`city_small_shop_shells_01-evidence/`](city_small_shop_shells_01-evidence/).
- Actual assembly scratch: `city_small_shop_shells_01-evidence/mounted_frontage_scratch.blend`.
  This contains appended copies of unchanged fitting sources solely for inspection;
  it is not another game source, assembly asset, prefab or source dependency.

All shell geometry is original Blender-authored editable mesh construction in
owned `author.py`. The front wall is one welded cell surface with actual holes;
internal cell faces are removed. Other semantic meshes preserve editable component
boundaries, with applied soft bevels and weighted normals. No imported model was
renamed as a source. No external mesh, font, texture, paid generation or image-derived
production geometry was used. Existing fitting exporter/check patterns were read
and adapted into owned tools. No external attribution obligation is introduced.

Shell source/export contain **no doors, entrance casings, window frames, glazing,
canopy or fascia**. Shared fittings retain ownership. No detailed/playable interior,
floor, runtime geometry, door mechanic, collision, rig, animation or navigation is
supplied. Wall/roof components enclose the volume visually once fitted; this is not
a fused watertight building or engineered weather/drainage specification.

## Metre envelope, axes and mounts

Ground-centred structural footprint origin `(0,0,0)`, floor Z=0. Blender +Y is
front/street and +Z up; front wall plane **Y=7.000**. One glTF conversion maps
`(X,Y,Z)` to Godot `(X,Z,-Y)`, front -Z and up +Y. Root and mesh transforms are
identity; geometry holds offsets. Marker translations below are intentional, with
identity rotations and unit scales. There is no corrective root scale/rotation.

| Measurement | Metres |
| --- | --- |
| Structural footprint | X [-3.200,3.200], Y [-7.000,7.000]; 6.400 × 14.000 |
| Full Blender mesh AABB | (-3.200,-7.220,0.000) → (3.200,7.120,5.050) |
| Full Godot mesh AABB | (-3.200,0.000,-7.120) → (3.200,5.050,7.220) |
| Full width × depth × height | 6.400 × 14.340 × 5.050 |
| Front wall thickness | Y [6.720,7.000], 0.280 |
| Party wall thickness | 0.280; no side projections past X ±3.200 |
| Roof deck top / underside | Z 4.300 / 4.140 |
| Side/rear coping top / front coping top | Z 4.700 / 5.050 |
| Decorative front / rear projection | 0.120 coping / 0.220 drain hopper |
| Expected bounds tolerance | ±0.001 per bound; numerical audits stricter |
| Mount placement tolerance | ±0.002 translation, aligned axes, unit scale |

All markers are children of `city_small_shop_shells_01` and survive in the GLB
under their exact names. Source empties are the placement writer; integrators
should consume these transforms rather than hand-tune duplicates.

| Marker | Blender translation | Godot translation | Consumer |
| --- | --- | --- | --- |
| `mount_entrance_single` | (1.950,7.000,0) | (1.950,0,-7.000) | .03 single surround |
| `mount_door_single` | (1.950,7.000,0) | (1.950,0,-7.000) | .06 single closed leaf |
| `mount_display_window` | (-0.950,7.000,0.480) | (-0.950,0.480,-7.000) | .05 |
| `mount_canopy` | (-0.950,7.000,3.000) | (-0.950,3.000,-7.000) | .01 |
| `mount_fascia` | (-0.950,7.000,3.800) | (-0.950,3.800,-7.000) | .02 blank fascia |
| `mount_roof_detail` | (0,-1.000,4.300) | (0,4.300,1.000) | Later separate roof fitting |
| `join_party_left` | (-3.200,0,0) | (-3.200,0,0) | Inline joining datum |
| `join_party_right` | (3.200,0,0) | (3.200,0,0) | Inline joining datum |

Join same-orientation shells at X pitch **6.400 m**, with ground/front datums aligned.
All shell meshes stay within that X interval, so neighbouring volumes do not overlap;
party-wall outer faces touch. Separate backing walls remain, with small bevel seams
on copings intentional. Do not mirror or widen the source to fill arbitrary parcels.
Exposed end walls are ordinary blank walls. No side openings cross the join.
World parcel placement, seam appearance and collision still need integrator checks.

The roof marker sits on the actual flat deck. Clear patch X [-0.700,0.700],
Y [-2.000,0.000], Z=4.300 is between longitudinal seams at X ±0.980. Nine actual
surface probes verify it. Roof fitting owners must keep their mounting footprint
within this patch or review another placement; no shared roof fitting is baked in
and no load, roof traversal or actual roof-kit compatibility is certified.

## Actual fitting assembly and clearances

Both saved source and separately imported game GLBs were assembled in private
scratch using the exact transforms above. Inputs `.01/.02/.03/.05/.06` and their
reports are read-only; before/after SHA256 values are retained and rechecked at
handoff. Single `.03` + single `.06` were selected, with one `.05`, canopy `.01`
and blank fascia `.02`; no fitting was stretched, modified or exported in the shell.

| Interface | Measured/required contract |
| --- | --- |
| Entrance hole | X [1.240,2.660], Z [0,2.450]; 1.420 × 2.450 |
| Entrance rear void | Clear from front plane to Y=6.460 (0.540 rear depth) |
| Entrance rear insertion | 10 mm nominal jamb/head gaps; rear geometry reaches Y=6.480, leaving 20 mm |
| Window hole | X [-2.470,0.570], Z [0.540,2.420]; 3.040 × 1.880 |
| Window mounting | Bottom pivot Z=.480; local aperture Z [.060,1.940] |
| Window rear void | Clear to Y=6.800; sleeve reaches Y=6.820, leaving 20 mm |
| Window sleeve gaps | 20 mm nominal jamb/head/bottom |
| Window flat bay | X [-2.650,.750], 3.400 wide, no interfering structural trim |
| Door leaf/surround | Actual 8 mm side and head mating gaps, no triangle intersections |
| Window/casing tops | Both Z=2.480 |
| Canopy lowest / top | Z=2.580 / 3.240; 100 mm above display window |
| Fascia lowest / top | Z=3.400 / 4.200; 160 mm above canopy |
| Fascia to head course | 280 mm |
| Entry casing to adjacent plinth | 80 mm each side; corner pier clearance 110 mm |
| Window to plinth / left pier | 180 mm vertical / 280 mm horizontal |

The full mounted visual frontage reaches Y=8.100 at the canopy; reserve its supplied
installation volume through Y=8.200. This projection is not part of shell-only bounds.
Minimum stated gaps are nominal, measured at exact mounts. Independent ±2 mm fitting
placement errors can reduce a two-fitting gap by 4 mm; do not claim the nominal
100 mm remains guaranteed after arbitrary mount offsets.

Checks trace 225 rays through each actual aperture and its rear void, measure hole
edges from the actual facade, check every rear fitting vertex against the opening,
and inspect triangle intersections between every fitting mesh and all shell meshes.
Only flush canopy/fascia contact at wall Y=7 is permitted; unexpected crossings are
zero. The actual .03/.06 mating assembly is also checked for intersections and gaps.
These are numeric Blender/source/GLB fit tests, **not Godot/world acceptance**, physics,
player accessibility, a weather seal or working door evidence.

## Materials, density and evidence

Five opaque single-sided embedded Principled/glTF PBR materials; sRGB swatches are
converted to linear base colour. One material slot per mesh. No emission, textures,
UV dependency, tangents, external material file, rig, clip or LOD is needed here.

| Material | Swatch | Metallic / roughness |
| --- | --- | --- |
| `shell_muted_plum_render` | #81777C | 0 / .78 |
| `shell_quiet_blue_roof` | #405B68 | .12 / .65 |
| `shell_warm_structural_trim` | #BBB6A8 | 0 / .70 |
| `shell_slate_plinth` | #4A5358 | 0 / .78 |
| `shell_dark_drain_coping` | #334950 | .35 / .48 |

**4,516 triangles, 30 meshes/material primitives, five materials, eight mount/join
markers plus one root; GLB 79,820 bytes.** Counts are measured, not a ratified device budget.
`source_export_checks.json` lists every object, bound, material slot and triangle
count. It verifies finite geometry, nondegenerate polygons, closed manifold and
consistently wound components with positive signed volumes, applied transforms and
excluded reference. `glb_checks.json` independently decodes raw positions, unit
normals and indices, tests triangle area and winding/normal agreement, compares
per-mesh source/export bounds and triangle counts, and verifies all marker transforms,
exact membership, material and studio exclusion.

`final_audit.json` proves a fresh-process saved-source GLB reexport is byte-identical,
with equal source audit results, and fitting inputs remain unchanged. No claim is
made that regenerating the `.blend` itself is byte-identical. The saved excluded
`authoring_excluded/authoring_1m_reference` is exactly 1 × 1 × 1 m; structural width,
depth and overall height ratios are 6.4, 14 and 5.05. It never enters the game export.

Views: `hero.png` (shell only), `mounted_hero.png`, `mounted_frontage.png`,
`rear_roof.png`, `measured_1m_comparison.png`, and `project_camera.png`.
The last is calibrated Blender straight-down, fixed-yaw perspective at 47 m,
42° vertical FOV, 1280 × 800, camera offset toward the frontage. It is not a native
Godot camera capture. Other views use Cycles CPU, 32 samples, four threads and AgX.
`preview_checks.json` records every camera. Sources/studios remain separated.
Visual self-inspection finds a clear narrow/deep roof and restrained shop frontage.
At the straight-down camera, the roof dominates and the canopy is visible; recessed
door/window faces and small hardware are mostly occluded. This records the limitation
rather than claiming storefront readability or accepting roof occlusion in gameplay.

## Fix cycle, diagnostics and reproduction

One meaningful owned geometry fix cycle removed coplanar overlaps at the rear
coping corners: side coping starts now butt against the rear cap instead of
occupying the same top surface. Initial source, GLB, scripts, numeric evidence and
renders are preserved under `initial/`. The corrected joints receive a numeric
butt-joint test; source/export/assembly/reexport checks and all views are repeated.

Complete unfiltered subprocess logs and matching `*.command.json` receipts retain
argv, cwd, process-local environment, elapsed time and exit status. Actual failures:

- `/usr/bin/blender5.2.2LTS` is absent, exit 127. `/usr/bin/blender` verifies the
  authorized 5.2.2 LTS build `d13f752e3b9c`, glTF 5.2.40; scripts assert both.
- First export audit used an erroneous expected mesh count of 32; actual authored
  semantic membership is 30. It exited 1 before export. The check was corrected,
  with the original checker and failure retained. This changed no geometry.
- Optional MeshOptimizer absence logs `ERROR` during export. Compression is unused;
  raw payload checks and exact reexport pass. Draco availability is informational.
- Material/World `use_nodes` deprecation warnings and private BlenderMCP addon
  registration messages are retained. No live endpoint or shared editor was used.

Final author, export, raw-GLB, source/GLB assembly, reexport, audit and preview jobs
exit 0. Process-local `ALSOFT_DRIVERS=null`, `SDL_AUDIODRIVER=dummy`, owned cache,
`-b -noaudio -t 4 --python-exit-code 1` were used; no global configuration/services.
Exact commands are in receipts. From repository root, a saved-source verification:

```sh
python tools/asset_production/city_small_shop_shells_01/run.py verify_again /usr/bin/blender -b -noaudio -t 4 art/source/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.blend --python-exit-code 1 --python tools/asset_production/city_small_shop_shells_01/export.py -- docs/assets/production/city_small_shop_shells_01-evidence/reexport.glb
python tools/asset_production/city_small_shop_shells_01/final_audit.py
python tools/asset_production/city_small_shop_shells_01/manifest.py --verify
```

Use unique log labels. Reproduction that changes receipts requires regenerating the
manifest after reviewing changes; `--verify` will intentionally detect new receipts.
For an untouched delivery, run the manifest verification first. `manifest.json` lists exact expected relative
paths, file bytes and SHA256 for all owned deliverables/evidence, excluding itself.
No other assets, shared docs, Git/index, project, prefab/world, editor or frozen
Batch02 candidate `5e94cc0ea4155219285db49c64b5728e0882b093` were mutated.

Engine import/sidecars, linked prefab, inherited save/reload, collision, movement,
network, native camera, device/performance, world placement and independent technical/
visual acceptance are later gates, all pending. Visual self-inspection is not
independent acceptance. All owned writers are quiescent at delivery; available for
concrete downstream fixes.
