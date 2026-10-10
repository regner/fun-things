# d05_quay_frontages.02 — Short frontage row

10 October 2026. **Source/export and bounded headless prefab candidate delivered;
independent review, placement and full gameplay/device acceptance pending.**
Produced by the commissioned implementation specialist on `lane/a-qfront`.
The production task and [commission](commission.md) supersede historical concept-only
restrictions in [the family brief](../d05_quay_frontages.md). Independent reviewers
retain acceptance authority; this is not a self-issued READY verdict.

## Design and dimensions

Two attached shop-home bays beneath one broad transverse slate pitch. The ridge runs
along the frontage, unlike the deep, narrow longitudinal roof of the earlier
[shop-home](d05_quay_frontages_01.md). A shallow central stone pier and two sets of
unchanged shop fittings articulate the two premises without suggesting a passage.
Warm ochre walls, amber storey course, petrol plinth and quiet slate/stone roof edges
retain the sibling's exact palette and fitting heights. The rear has two broad upper
windows; the side gables remain quiet. This is new original Blender construction,
not two scaled or duplicated shop-home exports. No chimney/dormer is needed; later
roof fittings must reuse `city_roof_details`, not introduce a unique fitting design.

Inputs inspected: repository/source contracts, accepted art direction, commission
and historical production progress, queue record, Old Quay family and v03 breakdown
and image, selected map context, stage-03 district identities, stage-04 streets,
city_lights.01 source/evidence, Batch01–03 prefab conventions, and the earlier .01
handoff/source/render. Old Quay's 5.28 ha includes roads, open space and harbour water;
it is not this row's allocation. No roads, world scenes or boundaries were changed.

Dimensions are **provisional authored choices**, not measurements from concept art.
The standing production brief permits this refinement. Original geometry only: no
downloads, image-to-mesh, real brands, fonts or textures. No interiors, working doors,
roof traversal, destructible states, rigs or gameplay systems are introduced.

| Measurement | Metres / contract |
| --- | --- |
| Structural footprint | 12.800 wide × 8.000 deep, centred on ground |
| Bay centres / nominal frontage pitch | X=-3.200 and +3.200 / 6.400 |
| Closed wall/collider height | 6.850; side gables continue to 9.110 inside roof |
| Roof plan without ridge cap | 13.360 × 8.560 |
| Shell visual width × height × depth | 13.380 × 9.400 × 8.560 |
| Shell Godot AABB | min (-6.690, 0, -4.280), max (6.690, 9.400, 4.280) |
| Complete fitted visual AABB | min (-6.690, 0, -5.100), max (6.690, 9.400, 4.280) |
| Complete fitted dimensions | 13.380 × 9.400 × 9.380 |
| Front / rear facade | Godot Z=-4.000 / +4.000 |
| Roof overhang beyond wall | .280 on four sides; ridge cap reaches .290 at gable ends |
| Pivot / axes | Ground-centred (0,0,0); Blender +Y/+Z → Godot -Z/+Y |
| Envelope/ground tolerance | ±.001 m; source root/mesh identity transforms, metre units |

The 6.4 m bay pitch is internal to this row, **not** a butt-join placement contract.
Reserve projecting eaves and canopies when placing adjacent buildings; measure
walking space independently. Do not scale the model to fill parcels. Family
irregularity comes from different plots, orientation, roof depth and civic space,
not from making every corridor narrow or bending this rectangular collider.

## Source, exports and materials

- Source: `art/source/models/environment/d05_quay_frontages_02/d05_quay_frontages_02.blend`.
- Export collection: `export_d05_quay_frontages_02`.
- Identity root / mesh: `D05QuayFrontages02` / `D05QuayFrontages02_Mesh`.
- Export: `art/models/environment/d05_quay_frontages_02/d05_quay_frontages_02.glb`.
- Adjacent `.glb.import`; imported model UID `uid://cdrd6oc674oae`.
- Prefab: `scenes/prefabs/environment/d05_quay_frontages_02.tscn`, UID `uid://db5tbal1c87tj`.
- Author/export/validator, isolated renderer, headless checker, saved collision fixture
  and manifest tooling: `tools/asset_production/d05_quay_frontages_02/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
Export uses the shared `tools/assets/blender/export_settings.json` with explicit
collection and animations/skins disabled. Boolean fitting recesses, soft bevels and
weighted normals are applied before saving. Editable geometry remains in the source;
`author.py` retains the dimensioned construction recipe. A named excluded
`authoring_1m_reference` cube measures one metre. No studio geometry, camera, light,
reference cube or reused fitting is included in the shell export.

Five embedded opaque, back-culled Principled materials, identical to .01's swatches
(sRGB converted to linear), with stable names:

| Material | sRGB | Metallic / roughness |
| --- | --- | --- |
| `quay_ochre_render` | `#C49A65` | 0 / .62 |
| `quay_slate_roof` | `#394D62` | .12 / .52 |
| `quay_warm_stone_trim` | `#C8C2AD` | .05 / .57 |
| `quay_petrol_plinth` | `#405B68` | .05 / .64 |
| `quay_amber_frontage` | `#DDA653` | .05 / .50 |

No textures, embedded images, transparency, emission or runtime light nodes. Shared
fittings retain their unchanged materials and opaque glazing. No material overrides,
socket API or runtime script. Default Godot LOD/shadow-mesh import remains enabled;
no custom LOD or unmeasured platform budget is claimed.

## Shared fittings and saved prefab

`Visuals/Model` is the identity-transform imported shell. `Fittings/West` and
`Fittings/East` contain saved, linked instances; both grouping nodes are identity.
The table gives local Godot XYZ translations (also prefab-root coordinates).
All fittings have unit scale and identity rotation, except both rear upper windows
have deliberate yaw π to face outward.

| Node in each bay | Existing resource under `res://` | West / East translation |
| --- | --- | --- |
| Canopy | `scenes/prefabs/environment/city_shop_fittings_01.tscn` | (-4.15, 3, -4) / (2.25, 3, -4) |
| Fascia | `scenes/prefabs/environment/city_shop_fittings_02.tscn` | (-4.15, 3.8, -4) / (2.25, 3.8, -4) |
| Surround | `scenes/prefabs/environment/city_shop_fittings_03_single.tscn` | (-1.25, 0, -4) / (5.15, 0, -4) |
| Display | `art/models/environment/city_shop_fittings_05/city_shop_fittings_05.glb` | (-4.15, .48, -4) / (2.25, .48, -4) |
| ClosedDoor | `art/models/environment/city_shop_fittings_06/city_shop_fittings_06_single.glb` | (-1.25, 0, -4) / (5.15, 0, -4) |
| UpperFront | `scenes/prefabs/environment/city_shop_fittings_07.tscn` | (-3.2, 4.65, -4) / (3.2, 4.65, -4) |
| UpperRear | `scenes/prefabs/environment/city_shop_fittings_07.tscn` | (-3.2, 4.65, 4) / (3.2, 4.65, 4) |

Display and closed leaf use accepted GLBs directly as visuals, following .01: the
building's single solid collider owns blocking, rather than duplicating their usual
prefab colliders. Other reused prefabs are visual-only. No copied hardware geometry,
replacement carrier or editable imported-child override. Fascia faces remain blank;
separately owned district graphics can supply artwork without implying essential
text readability from the overhead camera.

Both bays have actual **blind structural recesses**, not uncut walls behind glazing:

- Entrance width 1.420, heights 0–2.450; centres X=-1.25 / 5.15.
- Display width 3.040, heights .540–2.420; centres X=-4.15 / 2.25.
- Front/rear upper width 4.680, heights 4.710–6.190; centres X=±3.2.
- Each recess extends .650 behind its wall, beyond shared entrance .540, display
  .200 and upper-window .180 rear-void requirements. Nominal insertion gaps are
  10 mm for surround and 20 mm for display/upper sleeve; no fitting is rescaled.
- Display/casing tops 2.480; canopy bottom 2.580/top 3.240; fascia bottom 3.400/top
  4.200. Upper bottom 4.650 clears fascia by .450 and storey-course top by .160.

Eight independent source rays hit recess rear planes, and an intact-wall ray hits
the facade. Actual shared GLBs for both surrounds, closed doors, displays and four
upper windows have **zero shell-surface intersections** at the saved mounts.
Dependency hashes, mesh counts and mounts are recorded in validation.json. These are
closed decorative entrances, not physical openings, rooms or building-code claims.

## Validation and collision

[validation.json](d05_quay_frontages_02-evidence/validation.json): **4,408 triangles,
2,232 Blender vertices, 2,715 GLB vertices, one mesh, five surfaces** in the shell.
Zero degenerate source faces/export triangles and zero non-manifold source edges;
consistent winding, positive source volume, finite unit normals, identity transforms,
metre units, ground datum and decoded binary GLB bounds pass. The complete fitted
prefab has **97 imported mesh instances** including reused hardware; the shell's
one-mesh count is not a fitted draw-call or device performance claim.

Fresh-process reexport from the saved source is **byte-identical**, GLB **118,360 bytes**,
SHA-256 `c72ad57d687d2421c69324cfcd25871c70abedac9b94d88e892b0fb0a8be8f17`.
No byte-identical regeneration claim is made for the `.blend` container.

`Collision/Body` is one StaticBody3D, layer 1 / mask 0, with one direct `Shell`
BoxShape3D: size (12.8, 6.85, 8), centre (0, 3.425, 0). It blocks the complete closed
wall footprint, including both decorative entrances and the central party pier.
Actors stop at the facade, not in the recesses. Roof/gables/canopies above the wall
and shallow trim remain visual-only. No rooftop route or interior is promised;
no mesh-derived collision or duplicate floor is in the production prefab.

The saved collision fixture supplies a collision-only floor and production
ActorMotion capsule (r=.35, h=1.8), with no generated visible hierarchy.
Actual `ActorMotion.step` / `FootCommand` runs seven cases for 60 physics ticks each,
in both AUTHORITY and REPLAY: side contacts X=±6.750079; both closed entrances and
central pier stop at Z=-4.350257; rear stops at Z=4.350257; bypass at X=7.2 reaches
Z=2.9999998 from -2. Authority/replay agree within 2 mm (observed maximum difference
.000007573 m from initial vertical settling). Side rays hit actual X=±6.4 planes;
side-route and above-wall rays stay clear. These bounded checks do not prove car
impacts or real multiplayer transport/admission/prediction.

Pinned headless import has **no ERROR/SCRIPT ERROR lines**. Recursive dependency UID
resolution, actual shell/fitted bounds, fourteen saved mounts, exact fitting resource
paths and one collider pass. Prefab and fixture load–pack–save–reload are byte-stable,
preserving engine-generated scene UIDs and node identities. No inherited variant.
Owned GDScript passes pinned gdstyle formatting and lint. Whole-project production
checks were **not run**, per owner decision 52 for unplaced assets.

## Evidence and reproduction

[Hero](d05_quay_frontages_02-evidence/hero.png),
[side/rear](d05_quay_frontages_02-evidence/side.png),
[frontage detail](d05_quay_frontages_02-evidence/detail.png),
[47 m / 42° overhead](d05_quay_frontages_02-evidence/overhead_47m_42deg.png).
All are isolated Blender Cycles CPU / AgX, 32 samples, 1280×720, PNG compression 95
followed by six-bit RGB compaction/level 9; each final image is below 300 KB.
Overhead is vertical-down perspective at (0,0,47), fixed yaw, 42° **vertical** FOV.
The current brief's 1280×720 evidence cap supersedes the historical 1280×800 size.

Self-inspected all four views. The broad rectangular roof and transverse ridge are
clear overhead and distinct from .01; the two canopy tips subtly expose the frontage
rhythm. Windows, doors and fascia copy are not essential overhead-readable cues.
Hero/side silhouettes are complete and unclipped. The detail intentionally crops
the roof to show both fitting interfaces. No visual correction was needed after
this render pass. These studio images do not prove populated engine/blue-hour or
Steam Deck visibility.

Direct-file scene authoring followed by headless save was the mandated fallback:
windowed editor unavailable; owner live Blender/Godot sessions were never used.
Initial style checks found one long resource-path line and an extra blank line;
these were corrected before final checks. A version-only Blender probe exited 0 but
printed a one-block shutdown memory diagnostic; all actual author/export/validate/
render calls used audio-disabled environments and exited 0 without it. Blender
Principled API deprecation notices and existing Godot addon/version informational
messages remain visible in scratch logs; no broad suppression or addon changes.
[final.log](d05_quay_frontages_02-evidence/final.log) keeps concise final outcomes;
raw logs stay in the scratch directory, not Git.

Exact reproduction commands from the worktree root:

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T='tools/asset_production/d05_quay_frontages_02'
S='art/source/models/environment/d05_quay_frontages_02/d05_quay_frontages_02.blend'
TMP='C:/tmp/ft/assets/d05_quay_frontages_02'
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
mkdir -p "$TMP"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 "$S" --python-exit-code 1 --python "$T/export.py" -- "$TMP/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$TMP/reexport/d05_quay_frontages_02.glb"
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

The manifest hashes every produced payload except itself. Revalidation can rewrite
the receipt; refresh the manifest after all final source/export/evidence/doc changes.

## Remaining acceptance

- Independent art/source/prefab review; no asset-register, shared-progress or TODO
  readiness closure is claimed by this delivery.
- Actual district placement, measured overhang/passage spacing, actor corner
  circulation, car impacts/turning and populated camera/blue-hour occlusion checks.
- Real multiplayer transport/admission/prediction, packaging and sustained repeated
  placement / Steam Deck rendering and frame-pacing measurements.
- District fascia artwork remains separately owned; blank shared hardware is usable
  without inventing tenant identities or overhead-essential text.

The earlier .01 current handoff contained no stale pending item resolved by this row,
so no sibling doc, manifest or historical receipt needed modification. No queue,
shared progress/brief, project setting, world or sibling asset was changed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
