# d05_quay_frontages.04 — Deep-roof corner shell

10 October 2026. **Source/export and bounded headless prefab candidate delivered;
independent review, placement and full gameplay/device acceptance pending.**
Produced by the commissioned implementation specialist on `lane/a-qfront`.
The explicit production task and [commission](commission.md) commission this formerly
optional extension of [the family brief](../d05_quay_frontages.md). No new district
placement need is inferred from its historical optional status. Independent reviewers
retain acceptance authority; this is not a self-issued READY verdict.

## Design and dimensions

A deep two-storey corner shop-home with two perpendicular street-facing elevations.
The roof has two long slate slopes, a hipped street end and a conventional rear gable.
Its long off-centre ridge terminates at one hip only: it is neither the two-gable
narrow roof of [.01](d05_quay_frontages_01.md), the broad transverse row roof of
[.02](d05_quay_frontages_02.md), nor the compact four-slope hip of
[.03](d05_quay_frontages_03.md). An amber course turns the corner above two unchanged
shared shop displays/canopies; one closed entrance is on the front. Ochre render,
slate roof, warm stone and petrol base match .01/.02 exactly. The rear and left
remain quiet. No new chimney/dormer design; later fittings must reuse city_roof_details.

Inputs inspected: source/asset contracts, art direction, commission and historical
production progress, queue record, family brief, Old Quay v03 breakdown/image and
selected map context, stage-03 identities, stage-04 streets, city_lights.01 source/
evidence, Batch01–03 prefab conventions and all three earlier family deliveries.
The district's 5.28 ha includes roads, open space and harbour water, not just plots.
No road, parcel boundary, world scene or placement was changed.

Dimensions are **provisional authored choices**, permitted by the standing production
brief, not measurements from raster concepts. Original Blender construction only:
no downloads, image-to-mesh, real brands, external fonts/textures, interiors, opening
doors, rooftop traversal, destruction, rig or animation.

| Measurement | Metres / contract |
| --- | --- |
| Structural footprint | 8.800 wide × 12.000 deep, 105.600 m²; rectangular and ground-centred |
| Closed wall / collider height | 6.850; rear gable continues inside roof to 9.880 |
| Roof plan without cap | 9.360 × 12.560; .280 eave overhang |
| Roof edge / ridge top before cap | 6.870 / 10.050 |
| Ridge cap | 9.700 long, centre Godot Z=1.440, top 10.130 |
| Shell visual dimensions | 9.360 wide × 10.130 high × 12.570 deep |
| Shell Godot AABB | min (-4.680, 0, -6.280), max (4.680, 10.130, 6.290) |
| Complete fitted AABB | min (-4.680, 0, -7.100), max (5.500, 10.130, 6.290) |
| Complete fitted dimensions | 10.180 × 10.130 × 13.390 |
| Front / rear / right facade | Godot Z=-6.000 / Z=6.000 / X=4.400 |
| Pivot / axes | Ground-centred (0,0,0); Blender +Y/+Z → Godot -Z/+Y |
| Envelope / datum tolerance | ±.001 m; source root and mesh identity transforms, metre units |

The deep plan and active right return are for a corner plot, not an L-shaped walkable
courtyard. Reserve the front and right canopy projections of 1.100 m, plus measured
walking space. The canopy bottoms are 2.580 m above ground; their overhead volume
is visual-only. There is no butt-join pitch or permission to scale the model to a
parcel. Family irregularity comes from plots, orientation and open space, not from
uniformly narrow passages. No walking or driving clearance is inferred from renders.

## Source, exports and materials

- Source: `art/source/models/environment/d05_quay_frontages_04/d05_quay_frontages_04.blend`.
- Named export collection: `export_d05_quay_frontages_04`.
- Identity root / mesh: `D05QuayFrontages04` / `D05QuayFrontages04_Mesh`.
- Export: `art/models/environment/d05_quay_frontages_04/d05_quay_frontages_04.glb`.
- Adjacent `.glb.import`; model UID `uid://bim7otd62pw2j`.
- Prefab: `scenes/prefabs/environment/d05_quay_frontages_04.tscn`, UID `uid://biefs7rhxjf00`.
- Parametric author/export/validator, renderer, saved collision fixture, headless
  checker and manifest: `tools/asset_production/d05_quay_frontages_04/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
Export reads `tools/assets/blender/export_settings.json`, filters the explicit collection
and disables skins/animations. The recipe constructs closed wall and roof solids,
Boolean blind fitting recesses, soft bevels and applied weighted normals. Editable
geometry remains in the source; author.py retains the dimensioned construction.
An excluded `authoring_1m_reference` cube measures one metre. No shared fitting,
studio camera/light/ground or reference cube is included in the shell export.
Tools follow the existing sibling patterns; no new shared framework was introduced.

Five embedded opaque back-culled Principled surfaces, sRGB converted to linear:

| Material | sRGB | Metallic / roughness |
| --- | --- | --- |
| `quay_ochre_render` | `#C49A65` | 0 / .62 |
| `quay_slate_roof` | `#394D62` | .12 / .52 |
| `quay_warm_stone_trim` | `#C8C2AD` | .05 / .57 |
| `quay_petrol_plinth` | `#405B68` | .05 / .64 |
| `quay_amber_frontage` | `#DDA653` | .05 / .50 |

No textures, embedded images, transparency, emission or runtime lights. Shared
fittings retain their original materials and opaque glazing. No material overrides,
socket API or runtime script. Default Godot LOD/shadow-mesh import remains enabled;
no custom LOD or measured platform budget is claimed.

## Shared fittings and saved prefab

`Visuals/Model` is the identity-transform imported shell. Eleven saved linked
instances under `Fittings` reuse existing hardware without copied/rebuilt carriers.
All transforms below are Godot XYZ metres, unit scale. Front mounts have identity
rotation; UpperRear has yaw π; the four Return mounts have yaw -π/2, facing +X.

| Node | Existing resource under `res://` | Translation |
| --- | --- | --- |
| Canopy | `scenes/prefabs/environment/city_shop_fittings_01.tscn` | (-.95, 3, -6) |
| Fascia | `scenes/prefabs/environment/city_shop_fittings_02.tscn` | (-.95, 3.8, -6) |
| Surround | `scenes/prefabs/environment/city_shop_fittings_03_single.tscn` | (1.95, 0, -6) |
| Display | `art/models/environment/city_shop_fittings_05/city_shop_fittings_05.glb` | (-.95, .48, -6) |
| ClosedDoor | `art/models/environment/city_shop_fittings_06/city_shop_fittings_06_single.glb` | (1.95, 0, -6) |
| UpperFront | `scenes/prefabs/environment/city_shop_fittings_07.tscn` | (0, 4.65, -6) |
| UpperRear | same upper-window prefab | (0, 4.65, 6) |
| ReturnDisplay | same display GLB | (4.4, .48, -2) |
| ReturnCanopy | same canopy prefab | (4.4, 3, -2) |
| ReturnFascia | same fascia prefab | (4.4, 3.8, -2) |
| ReturnUpper | same upper-window prefab | (4.4, 4.65, -2) |

As in the siblings, display and closed leaf use their accepted GLBs directly as
visuals: the building's single box owns blocking rather than duplicating fitting
colliders. The other linked prefabs are visual-only. No editable-child override or
runtime-authored hierarchy. Blank fascia hardware is intentional; separately owned
district artwork can be attached later without making facade text overhead-essential.

Actual **blind structural recesses**, not uncut walls behind glazing:

- Front entrance: centre X=1.950, width 1.420, heights 0–2.450.
- Front display: centre X=-.950, width 3.040, heights .540–2.420.
- Front/rear upper: centre X=0, width 4.680, heights 4.710–6.190.
- Right display: centre Z=-2, width along Z=3.040, heights .540–2.420.
- Right upper: centre Z=-2, width along Z=4.680, heights 4.710–6.190.
- All recesses extend .650 behind their respective facades, exceeding shared
  entrance .540, display .200 and upper-window .180 rear-void requirements.
- Nominal insertion gaps: 10 mm for surround, 20 mm for displays/upper sleeves.
  No fitting is rescaled. Display tops 2.480 clear canopy bottom 2.580 by .100;
  canopy top 3.240 clears fascia bottom 3.400 by .160. Upper bottom 4.650 clears
  fascia top 4.200 by .450 and amber-course top 4.490 by .160.

Six source rays reach the blind rear planes; two independent intact-wall rays
reach the front/right facades. Actual reused surround, leaf, both displays and all
three upper-window GLBs have **zero shell-surface intersections**. Dependency hashes,
mesh counts and mounts are recorded in validation.json. These are decorative
closed recesses, not rooms, traversable entrances or building-code claims.

## Validation and collision

[validation.json](d05_quay_frontages_04-evidence/validation.json): **3,736 triangles,
1,892 Blender vertices, 2,289 GLB vertices, one mesh, five surfaces** in the new shell.
Zero degenerate source faces/export triangles and zero non-manifold source edges;
consistent winding, positive source volume, finite unit normals, identity transforms,
metre units, ground datum and decoded binary GLB axis bounds pass. Complete fitted
prefab: **79 imported mesh instances**, including unchanged hardware. The one-mesh
shell count is not a fitted draw-call or device-performance claim.

Fresh-process saved-source reexport is **byte-identical**, GLB **100,676 bytes**,
SHA-256 `62beb42d570b72cb455bd3e30d1a5ea21225b557d73d3b050dd7d53ea67edae9`.
No byte-identical regeneration claim is made for the `.blend` container.

`Collision/Body`: one StaticBody3D, layer 1 / mask 0, with direct child `Shell`, one
BoxShape3D size (8.8, 6.85, 12), centre (0, 3.425, 0). It exactly covers the closed
rectangular wall footprint, including blind entrances/windows and its corner.
Actors stop at facades rather than entering recesses. Gable/roof above the wall,
canopies and shallow trim are visual-only. No mesh-derived collision, duplicate
floor collider, rooftop route or interior is included in the production prefab.

The saved collision-only fixture supplies a flat floor and production ActorMotion
capsule (r=.35 m, h=1.8 m). Actual `ActorMotion.step` / `FootCommand` runs six cases
for 60 physics ticks each in AUTHORITY and REPLAY. Right return-display and left
contacts stop at X=±4.750077; closed entrance/front display at Z=-6.350257; rear at
Z=6.350257. A bypass under the return canopy at X=5.2 reaches Z=.999998 from -4.
All contact expectations use 3 mm tolerance. Authority/replay agree within 2 mm
(maximum observed difference .000007525 m from initial vertical settling).
Independent rays hit X=±4.4 and Z=±6 wall planes within 2 mm; above-wall and side
routes stay clear. These checks do not prove car impacts, district corner circulation
or real multiplayer transport/admission/prediction.

Pinned headless imports have **no ERROR/SCRIPT ERROR lines**. Recursive dependency
UID resolution, exact shell/fitted bounds, eleven saved fitting transforms/resource
paths, opaque surfaces and exactly one collider pass. Prefab and fixture load–pack–
save–reload are byte-stable; a fresh process after UID registration also preserves
both full scene hashes. Engine-generated UIDs/node identities remain stable. No
inherited variant exists. Owned GDScript passes pinned gdstyle format and lint.
Whole-project production checks were **not run**, per owner decision 52.

## Evidence and reproduction

[Hero](d05_quay_frontages_04-evidence/hero.png),
[side/rear](d05_quay_frontages_04-evidence/side.png),
[corner detail](d05_quay_frontages_04-evidence/detail.png),
[47 m / 42° overhead](d05_quay_frontages_04-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles CPU / AgX, 32 samples, 1280×720. PNG compression
95 followed by six-bit RGB compaction/level 9 keeps each below 325 KB. Overhead is
vertical-down perspective at (0,0,47), fixed yaw, 42° **vertical** FOV; the standing
1280×720 evidence cap supersedes historical 1280×800 evidence dimensions.

Self-inspected all four final renders. The deep roof and single triangular hip read
overhead independently of paint or windows. Both canopy tips mark the two street
fronts, but no essential text/detail visibility is claimed. Hero and side silhouettes
are complete and unclipped. Detail intentionally crops the upper roof to show the
corner fittings. Closed the amber course's small outer-corner gap before final
export/renders. Studio views do not prove populated engine/blue-hour/Deck visibility.

Direct-file scene authoring followed by headless Godot saves was the mandated
fallback: windowed editor unavailable; live owner sessions were never touched.
Initial validation caught a -1.124 mm Boolean/bevel ground vertex; authoring now
restores the body to its exact ground datum before normals. Initial Godot checks
caught reversed return-fitting transforms from text matrix ordering; corrected the
saved transforms to the independently expected -π/2 yaw. Final checks pass. Blender
Principled deprecation and existing Godot addon/version messages remain visible in
scratch logs; no broad suppression. [final.log](d05_quay_frontages_04-evidence/final.log)
keeps concise outcomes; retries/raw logs and scratch exports are outside Git.

Exact reproduction commands from the worktree root:

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T='tools/asset_production/d05_quay_frontages_04'
S='art/source/models/environment/d05_quay_frontages_04/d05_quay_frontages_04.blend'
TMP='C:/tmp/ft/assets/d05_quay_frontages_04'
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
mkdir -p "$TMP"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 "$S" --python-exit-code 1 --python "$T/export.py" -- "$TMP/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$TMP/reexport/d05_quay_frontages_04.glb"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
"$(mise which gdstyle)" fmt --check "$T/check.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check.gd"
python "$T/manifest.py" --prepare-evidence
timeout 300 "$G" --headless --path . --import
sha256sum scenes/prefabs/environment/d05_quay_frontages_04.tscn "$T/collision_check.tscn" > "$TMP/scenes-before.txt"
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
sha256sum -c "$TMP/scenes-before.txt"
python "$T/manifest.py"
python "$T/manifest.py" --verify
```

The manifest hashes every produced payload except itself. Revalidation rewrites the
receipt; regenerate the manifest last after final source/export/evidence/doc changes.

## Remaining acceptance

- Independent art/source/prefab review. No register, shared-progress or TODO readiness
  closure is claimed by this delivery.
- Actual district placement, overhang/passage spacing and actor corner circulation;
  car impacts/turning and populated fixed-camera/blue-hour occlusion checks.
- Real multiplayer transport/admission/prediction, packaging and sustained repeated
  placement / Steam Deck rendering and frame-pacing measurements.
- District fascia artwork remains separately owned; blank hardware is usable without
  inventing tenant identities or overhead-essential text.

None of the three earlier sibling handoffs listed this delivery as a stale pending
item, so no sibling doc/manifest or historical receipt needed modification. No queue,
shared progress/brief, project setting, world or sibling asset was changed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
