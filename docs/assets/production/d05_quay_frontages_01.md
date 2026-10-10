# d05_quay_frontages.01 — Narrow shop-home

10 October 2026. **Source/export and bounded headless prefab candidate delivered;
independent review, placement and full gameplay/device acceptance pending.**
Produced by the commissioned implementation specialist on `lane/a-qfront`.
The explicit production task and [commission](commission.md) supersede historical
concept-only restrictions in [the family brief](../d05_quay_frontages.md).
The supervisor's independent reviewers retain acceptance authority.

## Design and dimensions

A narrow two-storey waterfront shop-home: deep slate pitched roof, one restrained
ridge, ochre/amber render, warm stone eaves, quiet petrol base, glazed shopfront
and broad upper accommodation windows. Existing shop fittings are reused at their
original sizes, not remodelled. Plain side walls allow fine-grained irregular
frontage placement without extra side-door or rooftop gameplay. No chimney or
dormer is needed for this quiet roof; any later fitting must reuse `city_roof_details`.

Read the asset/source contracts, accepted art direction, production commission,
Old Quay family and v03 breakdown/image, selected map context, stage-03 district
identities, stage-04 streets, city_lights.01 source/evidence and Batch01–03 prefab
conventions. Old Quay's 5.28 ha includes roads, open space and harbour water; it is
not this building's plot allocation. No district scene, road or boundary was changed.
No earlier member of this family was present when this delivery began.

All dimensions below are **provisional authored choices**, not raster measurements.
Original Blender construction only: no downloaded geometry, image-to-mesh output,
real brands, external fonts/textures, interiors, working doors, destruction or rigs.

| Measurement | Metres / contract |
| --- | --- |
| Structural footprint | 6.400 wide × 10.000 deep, centred on the ground |
| Closed wall/collider height | 6.850; gable continues to 9.060 within the roof |
| Roof plan | 6.960 × 10.600; ridge cap extends depth to 10.620 |
| Shell visual width × height × depth | 6.960 × 9.350 × 10.620 |
| Shell Godot AABB | min (-3.480, 0, -5.310), max (3.480, 9.350, 5.310) |
| Complete fitted visual AABB | min (-3.480, 0, -6.100), max (3.480, 9.350, 5.310) |
| Complete fitted dimensions | 6.960 × 9.350 × 11.410 |
| Front facade / rear facade | Godot Z=-5.000 / +5.000 |
| Side roof overhang | .280 beyond each structural wall; visual-only |
| Pivot / axes | Ground-centred (0,0,0); Blender +Y/+Z → Godot -Z/+Y |
| Envelope and ground tolerance | ±.001 m; root/mesh transforms identity, metre units |

The pitched roof and ridge form one long narrow overhead silhouette; the wider
frontage and compact hipped-roof roles in the family brief remain distinct design
contracts, not recolours of this member. Use the slate/ochre/stone palette and shared
fitting datums below as the family reference. Do not scale this asset to fill parcels.
There is no butt-join pitch: roof eaves project outside the wall footprint, so
adjacent placements must explicitly reserve overhangs and measured walking space.

## Source, exports and materials

- Source: `art/source/models/environment/d05_quay_frontages_01/d05_quay_frontages_01.blend`.
- Collection: `export_d05_quay_frontages_01`.
- Identity root / mesh: `D05QuayFrontages01` / `D05QuayFrontages01_Mesh`.
- Explicit export: `art/models/environment/d05_quay_frontages_01/d05_quay_frontages_01.glb`.
- Adjacent `.glb.import`, model UID `uid://cok7pubma83iw`.
- Prefab: `scenes/prefabs/environment/d05_quay_frontages_01.tscn`, UID `uid://coe4ooekjuk11`.
- Parametric author/export, binary/source/fit validator, renderer, saved collision
  fixture, headless checker and manifest: `tools/asset_production/d05_quay_frontages_01/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
Export uses `tools/assets/blender/export_settings.json` and the explicit collection;
animations/skins disabled. Boolean fitting recesses, bevels and weighted normals are
applied. The source contains an excluded exact `authoring_1m_reference` cube. No
studio camera, light, reference mesh or shared fitting is exported in the shell.
The script retains the construction recipe; the `.blend` retains editable geometry.

Five embedded opaque, back-culled Principled surfaces, sRGB converted to linear:

| Material | sRGB | Metallic / roughness |
| --- | --- | --- |
| `quay_ochre_render` | `#C49A65` | 0 / .62 |
| `quay_slate_roof` | `#394D62` | .12 / .52 |
| `quay_warm_stone_trim` | `#C8C2AD` | .05 / .57 |
| `quay_petrol_plinth` | `#405B68` | .05 / .64 |
| `quay_amber_frontage` | `#DDA653` | .05 / .50 |

No textures, embedded images, transparency, emission or real lights. The imported
shared fittings retain their own unmodified materials and opaque glazing. No
material override, animation, socket API or runtime script is added. Godot's default
LOD/shadow-mesh import remains enabled; no speculative custom LOD or device budget.

## Shared fitting interfaces and saved prefab

`Visuals/Model` is the identity-transform imported shell. All fitting instances are
saved children of `Fittings`, not runtime-authored geometry. Paths below are relative
to `res://`; transforms use Godot XYZ metres, unit scale and identity basis except
for the rear upper window's deliberate 180° mounting yaw.

| Node | Existing resource | Translation |
| --- | --- | --- |
| Canopy | `scenes/prefabs/environment/city_shop_fittings_01.tscn` | (-.95, 3.00, -5) |
| Fascia | `scenes/prefabs/environment/city_shop_fittings_02.tscn` | (-.95, 3.80, -5) |
| Surround | `scenes/prefabs/environment/city_shop_fittings_03_single.tscn` | (1.95, 0, -5) |
| Display | `art/models/environment/city_shop_fittings_05/city_shop_fittings_05.glb` | (-.95, .48, -5) |
| ClosedDoor | `art/models/environment/city_shop_fittings_06/city_shop_fittings_06_single.glb` | (1.95, 0, -5) |
| UpperFront | `scenes/prefabs/environment/city_shop_fittings_07.tscn` | (0, 4.65, -5) |
| UpperRear | `scenes/prefabs/environment/city_shop_fittings_07.tscn` | (0, 4.65, 5), yaw π |

Display and closed leaf use their existing GLBs directly as visuals: the standing
one-simple-collider rule assigns blocking to this building's single solid box,
so their usual separate prefab colliders are intentionally not duplicated. The
other reused prefabs are visual-only. This follows the linked-fitting convention;
no sibling files, mesh data, imported-child overrides or replacement carriers.
The blank fascia is intentional; district frontage graphics owns any future copy.

The shell has **blind structural recesses**, not glazing laid over an uncut wall:

- Entrance: centre X=1.95, width 1.420, height 2.450 from ground.
- Display: centre X=-.95, width 3.040, heights .540–2.420.
- Front and rear upper windows: centre X=0, width 4.680, heights 4.710–6.190.
- Each recess extends .650 m behind its facade, exceeding the shared .540 m
  entrance, .200 m display and .180 m upper-window rear-void requirements.
- Nominal surround insertion gap 10 mm; display and upper sleeve gaps 20 mm.
  Existing fitting translation tolerance ±2 mm is not permission to rescale them.
- Display/casing tops 2.480; canopy bottom 2.580, top 3.240; fascia bottom 3.400,
  top 4.200. Upper window bottom 4.650 leaves .450 above fascia. Front structural
  course tops at 4.490, leaving .160 below the upper fitting.

Source rays verify the blind rear planes and intact facade; actual shared GLBs for
the surround, closed door, display and both upper windows have **zero shell-surface
intersections** at these mounts. Dependency hashes and actual mounts are recorded
in validation.json. No physical opening, room, weather seal or building-code claim.

## Validation and collision

[validation.json](d05_quay_frontages_01-evidence/validation.json): **3,076 triangles,
1,560 Blender vertices, 1,850 GLB vertices, one mesh, five surfaces** in the new shell.
Zero degenerate source faces/export triangles and zero non-manifold source edges;
consistent winding, positive source volume, finite unit normals, identity transforms,
metre units, ground datum and decoded GLB axis bounds pass. Complete fitted prefab
contains **49 imported mesh instances**, including the unchanged shared hardware;
the one-mesh shell count is not a draw-call claim for the fitted building.

Fresh-process saved-source reexport is **byte-identical**, GLB **82,668 bytes**,
SHA-256 `ec4b885004b8a6fbd427918343fec7fd61542434d85ea6a342202f461decd0db`.
No byte-identical regeneration claim is made for the `.blend` container itself.

`Collision/Body` is one StaticBody3D, layer 1 / mask 0; direct child `Shell` is one
BoxShape3D, size (6.4, 6.85, 10), centre (0, 3.425, 0). It blocks the full closed
wall footprint, including the decorative entrance recess. Actors stop at the facade,
not inside a vestibule. Roof/gable/canopy above the wall and shallow trim remain
visual-only; no interior or rooftop traversal is promised. No generated render-mesh
collision or duplicate ground collider belongs to the production prefab.

The saved test-only collision fixture supplies a flat collision floor and production
ActorMotion capsule (r=.35 m, h=1.8 m), without a procedural visible hierarchy. Actual
`ActorMotion.step` / `FootCommand` checks run 60 physics ticks per case in AUTHORITY
and REPLAY: side contacts X=±3.550780, closed-front Z=-5.350257, rear Z=5.350257;
clear route X=4 reaches Z=2.9999998 from -2. Authority/replay positions agree within
2 mm (maximum observed .878 mm vertical settling in the first case). Side rays hit
actual X=±3.2 planes; side-route and above-wall roof rays stay clear. These bounded
checks do not prove car impacts or real multiplayer transport/admission/prediction.

Pinned headless import has **no ERROR/SCRIPT ERROR lines**. Recursive dependency UID
resolution, actual imported/fitted bounds, seven saved mounts, one collider, and
prefab/fixture load–pack–save–reload byte stability pass. New scene UIDs are generated
and preserved with Godot ResourceUID/ResourceSaver; node identities remain stable.
No inherited variant exists. Owned GDScript passes pinned gdstyle formatting and lint.
Whole-project production checks were **not run**, per the resumed common brief and
owner decision 52 for unplaced assets.

## Evidence and reproduction

[Hero](d05_quay_frontages_01-evidence/hero.png),
[side/rear](d05_quay_frontages_01-evidence/side.png),
[frontage detail](d05_quay_frontages_01-evidence/detail.png),
[47 m / 42° overhead](d05_quay_frontages_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU / AgX, 32 samples, 1280×720. PNG compression
95 followed by six-bit RGB compaction/level 9 keeps evidence lean. The overhead
is vertical-down perspective at (0,0,47), fixed yaw, 42° **vertical** FOV; the current
brief's 1280×720 cap supersedes historical 1280×800 evidence dimensions.

Self-inspected all four final views. The long narrow slate pitch and restrained
ridge survive overhead; shop fittings largely disappear beneath the roof, so no
essential wayfinding depends on the fascia from that camera. Hero and side views
have complete unclipped silhouettes. Fixed a coplanar gable seam, widened overview
framing and corrected the rear-window preview's rotation mode before final renders.
The final facade detail intentionally crops the roof to show the fitting interfaces.
These studio views are not populated blue-hour engine captures or device evidence.

Direct-file scene authoring followed by headless Godot save was the mandated fallback:
windowed editor unavailable; owner live Blender/Godot sessions were never used.
An initial `--editor` normalization exited 0 but logged editor/plugin teardown RID
leaks. It was replaced by ordinary headless normalization with explicit UID retention;
final imports/checks have no errors. Informational addon registration and the import
plugin's pre-existing 4.8-version warning remain unsuppressed. Initial owned style
warnings were fixed. [final.log](d05_quay_frontages_01-evidence/final.log) retains the
concise command outcomes; raw logs/retries stay outside Git in the scratch directory.

Exact commands from worktree root:

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T='tools/asset_production/d05_quay_frontages_01'
S='art/source/models/environment/d05_quay_frontages_01/d05_quay_frontages_01.blend'
TMP='C:/tmp/ft/assets/d05_quay_frontages_01'
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
mkdir -p "$TMP"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 "$S" --python-exit-code 1 --python "$T/export.py" -- "$TMP/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$TMP/reexport/d05_quay_frontages_01.glb"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
"$(mise which gdstyle)" fmt --check "$T/check.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check.gd"
python "$T/manifest.py" --prepare-evidence
timeout 300 "$G" --headless --path . --import
python "$T/manifest.py"
python "$T/manifest.py" --verify
```

The manifest hashes every produced file except itself. Revalidation can rewrite the
receipt; refresh the manifest after all final source/export/evidence/doc changes.

## Remaining acceptance

- Independent art/source/prefab review. This delivery is not a self-issued READY
  verdict and does not close the asset register, shared progress or project TODOs.
- Actual district placement, overhang/passage spacing, actor corner circulation,
  car impacts/turning and populated fixed-camera/blue-hour visibility/occlusion.
- Real multiplayer transport/admission/prediction, packaging and sustained repeated
  placement / Steam Deck rendering and frame-pacing measurements.
- District fascia artwork is separately owned; blank shared hardware remains usable
  without inventing tenant identity or essential overhead-readable text.

No queue, shared progress/brief, world, project setting or sibling asset was changed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
