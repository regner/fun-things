# d05_quay_frontages.03 — Compact hipped-roof infill house

10 October 2026. **Source/export and bounded headless prefab candidate delivered;
independent review, placement and full gameplay/device acceptance pending.**
Produced by the commissioned implementation specialist on `lane/a-qfront`.
The explicit production task and [commission](commission.md) supersede historical
concept-only restrictions in [the family brief](../d05_quay_frontages.md).
Independent reviewers retain acceptance authority; this is not a self-issued READY verdict.

## Design and dimensions

A compact, near-square two-storey house with four broad slate roof slopes and a short
central ridge. Its hipped silhouette distinguishes it from the long narrow pitch of
[.01](d05_quay_frontages_01.md) and the wide transverse pitch of
[.02](d05_quay_frontages_02.md), independently of paint. Muted plum render is paired
with the siblings' unchanged slate, warm stone, petrol plinth and amber course.
Unscaled shared windows and a closed entrance retain the family hardware language.
There is no retail canopy, fascia, chimney or dormer: this is quiet residential infill,
not another shop recolour. Later chimney/dormer fittings must reuse `city_roof_details`.

Inputs inspected: repository/source contracts, art direction, commission and historical
production progress, queue record, family brief, Old Quay v03 breakdown/image, selected
map context, stage-03 district identities and stage-04 streets, city_lights.01 source/
evidence, Batch01–03 integration conventions, and both earlier family deliveries.
Old Quay's 5.28 ha includes roads, open space and harbour water, not just building plots.
No world scene, road, parcel boundary or placement was changed.

All dimensions are **provisional authored choices**, not raster measurements. Original
Blender construction only: no downloaded geometry, image-to-mesh, real brands, external
fonts/textures, interiors, working doors, destruction, animation or rooftop gameplay.

| Measurement | Metres / contract |
| --- | --- |
| Structural footprint | 7.200 wide × 7.600 deep, centred on ground; 54.720 m² |
| Closed wall / collider height | 6.850 |
| Roof plan | 7.760 × 8.160; .280 overhang beyond each wall |
| Eave trim / roof edge | Trim heights 6.550–6.650; roof edge top 6.870 |
| Hip ridge / cap | Ridge length 1.800 at height 8.950 before bevel; cap length 1.840, top 9.030 |
| Shell and complete fitted dimensions | 7.760 wide × 9.030 high × 8.160 deep |
| Shell and fitted Godot AABB | min (-3.880, 0, -4.080), max (3.880, 9.030, 4.080) |
| Front / rear facade | Godot Z=-3.800 / +3.800 |
| Pivot / axes | Ground-centred (0,0,0); Blender +Y/+Z → Godot -Z/+Y |
| Envelope / ground tolerance | ±.001 m; source root and mesh identity transforms, metre units |

The house occupies a smaller plan than either sibling, with nearly equal width/depth.
All fittings remain within the roof-plan envelope. Plain side walls permit infill
placement without implying lateral entrances. Do not scale this model to fill parcels.
There is no butt-join pitch: reserve roof overhangs and independently measured passages.
The family should feel irregular through plots/orientation/open space, not uniformly
cramped corridors. No walking clearance is inferred from these isolated renders.

## Source, exports and materials

- Source: `art/source/models/environment/d05_quay_frontages_03/d05_quay_frontages_03.blend`.
- Export collection: `export_d05_quay_frontages_03`.
- Identity root / mesh: `D05QuayFrontages03` / `D05QuayFrontages03_Mesh`.
- Explicit export: `art/models/environment/d05_quay_frontages_03/d05_quay_frontages_03.glb`.
- Adjacent `.glb.import`; imported model UID `uid://tyt26cvrnejy`.
- Prefab: `scenes/prefabs/environment/d05_quay_frontages_03.tscn`, UID `uid://cegchwgkmqo3`.
- Parametric author/export/validator, renderer, saved collision fixture, headless checker
  and manifest: `tools/asset_production/d05_quay_frontages_03/`.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
Export loads the shared `tools/assets/blender/export_settings.json`, filters the named
collection and disables animations/skins. The dimensioned Blender recipe constructs
closed solids, cuts blind fitting recesses and applies bevels/weighted normals.
The `.blend` retains editable geometry; the script retains the construction recipe.
An excluded `authoring_1m_reference` cube measures one metre. No reference cube,
studio camera/light/ground or reused fitting is included in the shell export.
Asset-specific checks follow the sibling patterns; no new shared framework was added.

Five embedded opaque, back-culled Principled materials, sRGB converted to linear:

| Material | sRGB | Metallic / roughness |
| --- | --- | --- |
| `quay_muted_plum_render` | `#927380` | 0 / .62 |
| `quay_slate_roof` | `#394D62` | .12 / .52 |
| `quay_warm_stone_trim` | `#C8C2AD` | .05 / .57 |
| `quay_petrol_plinth` | `#405B68` | .05 / .64 |
| `quay_amber_frontage` | `#DDA653` | .05 / .50 |

No textures, embedded images, transparency, emission or runtime light nodes. Shared
hardware retains its unchanged materials and opaque glazing. No material overrides,
socket API, rig or runtime script is introduced. Godot's default LOD/shadow-mesh import
remains enabled; no custom LOD or unmeasured platform budget is claimed.

## Shared fitting interfaces and saved prefab

`Visuals/Model` is the identity-transform imported shell. Six saved linked instances
under `Fittings` reuse existing hardware without replacement carrier geometry.
Translations below are Godot XYZ metres relative to the root, with unit scale and
identity rotation except for the two rear windows' deliberate yaw π.

| Node | Existing resource under `res://` | Translation |
| --- | --- | --- |
| Surround | `scenes/prefabs/environment/city_shop_fittings_03_single.tscn` | (2.45, 0, -3.8) |
| ClosedDoor | `art/models/environment/city_shop_fittings_06/city_shop_fittings_06_single.glb` | (2.45, 0, -3.8) |
| LowerFront | `scenes/prefabs/environment/city_shop_fittings_07.tscn` | (-1, .9, -3.8) |
| UpperFront | same upper-window prefab | (0, 4.65, -3.8) |
| LowerRear | same upper-window prefab | (0, .9, 3.8), yaw π |
| UpperRear | same upper-window prefab | (0, 4.65, 3.8), yaw π |

The closed leaf uses its accepted GLB directly as a visual, following the siblings:
the building's single solid box owns blocking rather than duplicating the leaf's
usual prefab collider. The surround/windows are visual-only prefabs. The existing
upper-window group is reused unchanged at both residential storeys; there is no new
window design, editable imported-child override, copied mesh or runtime assembly.

The body has actual **blind structural recesses**, not glazing on an uncut wall:

- Entrance centre X=2.450, width 1.420, heights 0–2.450.
- Lower front window centre X=-1; lower rear centre X=0; width 4.680,
  heights .960–2.440. The unchanged window casing spans heights .900–2.500.
- Upper front/rear windows centre X=0, width 4.680, heights 4.710–6.190.
  The upper fitting bottom at 4.650 preserves the siblings' height datum.
- All recesses extend .650 behind their facade, exceeding the entrance .540 and
  window .180 rear-void requirements. Nominal insertion gaps are 10 mm for the
  entrance and 20 mm for windows; fittings are not rescaled.
- Amber course top 4.490 leaves .160 below the upper fitting. Plinth stops before
  the door casing; it does not intersect the reused frame.

Five source rays reach the blind rear planes and an intact-wall ray reaches the
facade. Actual reused surround, leaf and four window GLBs have **zero shell-surface
intersections** at the saved mounts. Dependency hashes and exact mounts are in the
validation receipt. These recesses are decorative, not rooms or traversable openings.

## Validation and collision

[validation.json](d05_quay_frontages_03-evidence/validation.json): **3,108 triangles,
1,576 Blender vertices, 1,948 GLB vertices, one mesh, five surfaces** in the shell.
Zero degenerate source faces/export triangles and zero non-manifold source edges;
consistent winding, positive source volume, finite unit normals, identity transforms,
metre units, ground datum and decoded binary GLB bounds pass. The fitted prefab has
**52 imported mesh instances** including unchanged shared hardware. The shell's one
mesh is not a fitted draw-call or performance claim.

Fresh-process reexport from the saved source is **byte-identical**, GLB **86,040 bytes**,
SHA-256 `edf591d74db7f3b68b4ec15badd4962597610c33272fa6162c78a56692810d30`.
No byte-identical regeneration claim is made for the `.blend` container.

`Collision/Body` is one StaticBody3D, layer 1 / mask 0, with one direct `Shell`
BoxShape3D: size (7.2, 6.85, 7.6), centre (0, 3.425, 0). This blocks the complete
closed wall footprint including the decorative entrance/windows. Actors stop at the
facade rather than entering the blind recesses. Roof above the wall and shallow trim
remain visual-only. No mesh-derived collision, duplicate ground or rooftop route.

A saved collision-only fixture supplies a flat floor and production ActorMotion
capsule (r=.35, h=1.8). Actual `ActorMotion.step` / `FootCommand` runs six cases for
60 physics ticks each in AUTHORITY and REPLAY. Side contacts stop at X=±3.950517;
entrance/front-window contacts Z=-4.166663; rear Z=4.166663. The bypass at X=4.4
reaches Z=2.9999998 from -2. Authority/replay agree within 2 mm (maximum observed
.878 mm initial vertical settling). Independent rays hit X=±3.6 and Z=±3.8 wall
planes; side-route and above-wall roof rays stay clear.

Initial front/rear movement assertions required 3 mm from ideal capsule contact
at |Z|=4.15. The engine stopped 16.663 mm short of that ideal in both modes. The
final test explicitly requires nonpenetration and at most 20 mm stand-off, while
independent wall-plane rays retain a 2 mm tolerance. No collider, actor setting or
gameplay implementation was changed to accommodate that observation. These bounded
checks do not prove car impacts or real multiplayer transport/admission/prediction.

Pinned headless import has **no ERROR/SCRIPT ERROR lines**. Recursive dependency UID
resolution, shell/fitted bounds, six exact shared mounts, opaque surfaces, one collider
and prefab/fixture load–pack–save–reload pass. After importing the newly saved scene
UIDs, a fresh headless process also preserves both complete scene-file SHA-256 hashes;
UIDs and node identities are stable. No inherited variant exists. Owned GDScript
passes pinned gdstyle formatting and lint. Whole-project production checks were **not
run**, per owner decision 52 for unplaced assets.

## Evidence and reproduction

[Hero](d05_quay_frontages_03-evidence/hero.png),
[side/rear](d05_quay_frontages_03-evidence/side.png),
[facade detail](d05_quay_frontages_03-evidence/detail.png),
[47 m / 42° overhead](d05_quay_frontages_03-evidence/overhead_47m_42deg.png).
All are isolated Blender Cycles CPU / AgX, 32 samples, 1280×720. PNG compression 95
followed by six-bit RGB compaction/level 9 keeps each final image below 300 KB.
Overhead is vertical-down perspective at (0,0,47), fixed yaw, 42° **vertical** FOV.
The current 1280×720 evidence cap supersedes the historical 1280×800 size.

Self-inspected all four final views. The near-square roof, four distinct slopes and
short ridge read overhead without relying on plum walls, windows or door details.
Hero/side silhouettes are complete and unclipped. Widened the detail framing to
include the complete entrance. Fixed initial plinth/casing intersections before
final source/export validation and renders. These neutral studio views do not prove
populated engine/blue-hour visibility or Steam Deck readability.

Direct-file scene authoring followed by headless save was the mandated fallback:
windowed editor unavailable; owner live Blender/Godot sessions were never touched.
New scene UIDs were registered by import before final cross-process stability checks.
Initial owned style warnings were corrected. Blender Principled API deprecations and
the existing Godot addon 4.8-version warning remain visible, not broadly suppressed.
[final.log](d05_quay_frontages_03-evidence/final.log) retains concise command outcomes;
raw diagnostics, scratch exports and retries stay outside Git.

Exact reproduction commands from the worktree root:

```bash
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T='tools/asset_production/d05_quay_frontages_03'
S='art/source/models/environment/d05_quay_frontages_03/d05_quay_frontages_03.blend'
TMP='C:/tmp/ft/assets/d05_quay_frontages_03'
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
mkdir -p "$TMP"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 "$S" --python-exit-code 1 --python "$T/export.py" -- "$TMP/reexport"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" -- "$TMP/reexport/d05_quay_frontages_03.glb"
timeout 600 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$T/render.py"
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
"$(mise which gdstyle)" fmt --check "$T/check.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check.gd"
python "$T/manifest.py" --prepare-evidence
timeout 300 "$G" --headless --path . --import
sha256sum scenes/prefabs/environment/d05_quay_frontages_03.tscn "$T/collision_check.tscn" > "$TMP/scenes-before.txt"
timeout 180 "$G" --headless --path . --script "res://$T/check.gd" -- --normalize
sha256sum -c "$TMP/scenes-before.txt"
python "$T/manifest.py"
python "$T/manifest.py" --verify
```

The manifest hashes every produced payload except itself. Revalidation rewrites the
receipt; regenerate the manifest last after all source/export/evidence/doc changes.

## Remaining acceptance

- Independent art/source/prefab review. No asset-register, shared-progress or TODO
  readiness closure is claimed by this delivery.
- Actual district placement, measured overhang/passage spacing, actor corner
  circulation, car impacts/turning and populated camera/blue-hour occlusion checks.
- Real multiplayer transport/admission/prediction, packaging and sustained repeated
  placement / Steam Deck rendering and frame-pacing measurements.

Neither earlier sibling's current handoff listed a stale pending item resolved by
this house; no sibling handoff, manifest or historical receipt required modification.
No queue, shared progress/brief, project setting, world or sibling asset was changed.
