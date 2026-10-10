# city_boardwalk.02 — Bend/corner deck section

10 October 2026. **Three source/export/linked-prefab variants delivered; bounded asset checks pass.
Independent review, world placement and gameplay/device acceptance remain pending.**
Produced by the commissioned implementation specialist on `lane/a-boardwalk` under the
[production commission](commission.md) and current per-asset common brief. The latter explicitly
supersedes the historical commission's lead-only Git/prefab restriction. No shared brief, register,
project setting, sibling asset or world scene was changed.

Family: [shared island boardwalk](../city_boardwalk.md). Read and matched the earlier
[straight section](city_boardwalk_01.md), Petrol & Coral [art direction](../../art-direction.md),
The Crescents v02, and world-v1 stage-03 district identities / stage-04 streets. These are style
and route references, not measured coast-fit evidence. All geometry is original Blender construction;
no downloads, image-to-mesh, brands, external textures or runtime-generated render meshes.

## Design and dimensions

Radial warm-brown timbers carry the same quiet three-tone palette, broad cross-deck seams and
soft arrises as `.01`. The slate underdeck remains inset and shallow. **22.5°, 45° and 90°**
variants follow a **6 m centre-line radius**; the 90° member is the default prefab. This is a
coastal walking deck, not a marina pontoon, road or new shore platform. There are no duplicate
rails, benches, lamps, shore rocks, seawalls, support legs or finished fascia pieces.

Dimensions and angle selection are **provisional**, under the standing instruction to proceed
with sensible family-compatible values. Placement must fit the existing coast, not alter it.

| Shared interface | Godot local metres |
| --- | --- |
| Walking width | **3.600** radial width; inner radius **4.200**, outer radius **7.800** |
| Walking datum / underside | **Y=0 / Y=-0.240**, exactly matching `.01` |
| Timber / backing depth | **0.080 / 0.160** |
| Origin | **Entry centre on the walking surface (0,0,0)**, not seabed or footprint centre |
| Entry direction | **-Z**, Blender +Y; +Y is up after export |
| Entry connector | Z=0, X=-1.800 to +1.800, surface Y=0 |
| Bend direction | Right toward **+X**; circle centre **(6,0,0)** |
| Core setback | **0.040** from both curved edges; core terminates on both join planes |
| Timber rhythm | One radial board every **2.8125°**, centre-line pitch **0.294524 m** |
| Visual seams | **0.012 m** at centre radius; **0.0084–0.0156 m** across width |
| Terminal half-seam | **0.006 m** at centre radius; mates with `.01`'s 0.006 m end half-seam |
| Timber roundover | **0.004 m**, two bevel segments; no collision bevels or seam gaps |

The fan-cut boards deliberately taper in plan rather than stretching rectangular planks. The
core uses a closed chorded outline at the same 2.8125° pitch. Its sharp backing edges are hidden
beneath the timber and later finished by `.03`; they are not a second fascia design. The largest
outer-edge chord departure from an ideal circle is about **0.00235 m**. Seam size/half-seam
varies slightly with radius; a straight join is approximately 10.2–13.8 mm before arris rounding.

### Connector and envelope table

Exit centre at angle θ is **(6(1−cos θ), 0, −6 sin θ)**, outward tangent
**(sin θ, 0, −cos θ)**. Exit width spans ±1.8 m along **(cos θ, 0, sin θ)**.
The whole nominal envelope includes the small terminal half-seams and roundovers. Actual exported
bounds are recorded below, so neither the nominal nor measured envelope is mistaken for the other.

| Variant / filename suffix | Timbers | Centre arc length | Exit centre (X,Y,Z) | Nominal AABB min → max |
| --- | ---: | ---: | --- | --- |
| 90° / none | 32 | 9.424778 | (6,0,-6) | (-1.8,-.24,-7.8) → (6,0,0) |
| 45° / `_45` | 16 | 4.712389 | (1.757359,0,-4.242641) | (-1.8,-.24,-5.515433) → (3.030152,0,0) |
| 22.5° / `_22p5` | 8 | 2.356194 | (.456723,0,-2.296101) | (-1.8,-.24,-2.984931) → (2.119706,0,0) |

| Variant | Actual binary GLB AABB min → max (m) | Actual size X/Y/Z (m) |
| --- | --- | --- |
| 90° | (-1.799898,-.24,-7.799898) → (6,0,0) | 7.799898 / .240000 / 7.799898 |
| 45° | (-1.799898,-.24,-5.508239) → (3.025546,0,0) | 4.825444 / .240000 / 5.508239 |
| 22.5° | (-1.799898,-.24,-2.976196) → (2.116661,0,0) | 3.916559 / .240000 / 2.976196 |

Numerical tolerances: datum/depth/import comparison **0.001 m**; source-to-binary coordinates
**0.00001 m**; nominal envelope **0.012 m**, admitting the explicitly authored half-seams and
roundovers. These tolerances do not permit a 12 mm step or a collision gap.

### Family mating and placement

- Place an incoming unchanged `.01` at **(0,0,3)** with identity rotation: its north end
  meets this entry. Place an outgoing `.01` at **exit + 3 × exit tangent**, with Godot yaw
  **−θ**. Keep unit scale. The saved fixture demonstrates all three combinations.
- The same model supplies left turns by traversing from exit to entry and applying a rigid
  yaw/translation. No negative-scale mirror or duplicate left mesh is needed. Both traversal
  directions are tested. The pivot remains the original entry; do not assume a centred pivot.
- `.03` owns fascia/low trim. Curved attachment boundaries are radii **4.2 / 7.8 m** around
  (6,0,0), over the chosen angle; this delivery provides no fascia or duplicated terminal cap.
- `.04` support assemblies meet **Y=-0.24**. No claim of engineering capacity or final support
  spacing is made. `.05` landward transitions meet **Y=0** without a step.
- Shared `city_quay_furniture.02` owns rail geometry and rail collision. This bare deck does not
  depend on an unproduced rail model. Fit shared rails outboard where possible and keep lamps
  and seating outside the walking line; no unapproved rail sockets/post pitch are invented.
- Six recorded coastal districts remain prospective consumers. Old Quay remains a candidate;
  **East Docks remains excluded**. This is not a closed whole-island ring, harbour bridge,
  inner-basin dock, reclamation or authorization to change district boundaries.

## Source, exports and materials

Source: `art/source/models/environment/city_boardwalk_02/city_boardwalk_02.blend`.
The three collections overlap intentionally at their common entry anchor in the source; they
are alternatives, not an assembly. Export collections and roots are:

| Collection | Identity root / child | Output in `art/models/environment/city_boardwalk_02/` |
| --- | --- | --- |
| `export_city_boardwalk_02` | `CityBoardwalk02` / `CityBoardwalk02_Mesh` | `city_boardwalk_02.glb` |
| `export_city_boardwalk_02_45` | `CityBoardwalk02_45` / `CityBoardwalk02_45_Mesh` | `city_boardwalk_02_45.glb` |
| `export_city_boardwalk_02_22p5` | `CityBoardwalk02_22p5` / `CityBoardwalk02_22p5_Mesh` | `city_boardwalk_02_22p5.glb` |

Each has one mesh / four surfaces, applied identity transforms, metre units and weighted corner
normals. Blender +Y/+Z maps once to Godot -Z/+Y. No studio geometry, camera or light is exported
or saved in the source. `render.py` adds transient studio-only offsets and objects.

Materials match `.01` exactly, in the same exported slot order:

| Slot / Principled material | Linear base RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `boardwalk_underdeck_slate` | (.048,.069,.078) | .15 / .58 |
| 1 `boardwalk_timber_warm` | (.235,.145,.085) | 0 / .68 |
| 2 `boardwalk_timber_light` | (.260,.166,.101) | 0 / .68 |
| 3 `boardwalk_timber_muted` | (.215,.136,.085) | 0 / .68 |

All are opaque and backface-culled, without emission, images, procedural texture nodes or external
material dependencies. No textures/UV maps, material copies, rig, animation, destruction state,
sockets or custom LOD are needed for these flat-colour static members. Default Godot automatic
LOD/shadow-mesh import settings are retained; repeated-route LOD/performance acceptance is pending.
Shared `tools/assets/blender/export_settings.json` remains the exporter-settings owner. Local
recipes and the binary-audit convention follow `.01`; there is no shared general-purpose geometry
builder/validator in this checkout, and no new shared tooling or alternative exporter was introduced.

## Prefabs and collision

Three `scenes/prefabs/environment/city_boardwalk_02{,_45,_22p5}.tscn` wrappers retain their GLB
at **`Visuals/Model` with identity transform**. No embedded render meshes, editable imported
children, runtime hierarchy construction or gameplay scripts. Scene/dependency UIDs and node
identities are headlessly normalized and preserved through two save/load/resave cycles.

Each `Collision/Body` is a single StaticBody3D, **layer 1 / mask 0**, with one direct `Deck`
CollisionShape3D. A deliberately authored **closed ConcavePolygonShape3D slab** follows the
annular walking footprint, top Y=0 and bottom Y=-0.24. Unlike a convex hull, it does not fill the
inside of the elbow. There are only top, bottom and perimeter faces, no internal radial walls.
This simple static surface collision is separate from every visual board seam and bevel.

| Variant | Collision triangles / unique vertices | Measured top area (m²) |
| --- | --- | ---: |
| 90° | 260 / 132 | 33.915577 |
| 45° | 132 / 68 | 16.957788 |
| 22.5° | 68 / 36 | 8.478894 |

All saved collision edges have exactly two opposite uses after exact float32 coordinate matching:
**zero open/nonmanifold edges and zero degenerate triangles**. Tiny visual end/edge recesses are
bridged deliberately by the collider, consistent with `.01`. Collision is for static placement
only; do not attach this concave shape to a dynamic body.

There are **no invisible rails or edge barriers**. Safe elevated/waterfront placements require
shared rails, compatible support/shore arrangement and downstream falloff/clearance review.
Avoid duplicate coplanar terrain/deck collision. A rail-free coastal route is not accepted.

`tools/asset_production/city_boardwalk_02/walk_check.tscn` saves all three bends with unchanged
`.01` entry/exit instances, separated by 20 m for independent queries. Its collision-only actor
uses the production **ActorMotion** API with radius **0.35 m**, height **1.8 m**. This is a
technical fixture, not a world placement or new visible test asset.

## Validation and evidence

[validation.json](city_boardwalk_02-evidence/validation.json) contains measured source, binary
GLB, saved-collision, Godot resource/physics and canonical-check results.
[manifest.json](city_boardwalk_02-evidence/manifest.json) hashes every delivered payload except
itself. [final.log](city_boardwalk_02-evidence/final.log) retains concise successes and failures;
raw logs, prior framing and reexports remain in external scratch space.

- Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**.
- Per exported variant:

  | Variant | Triangles | Source vertices | GLB vertices | GLB bytes |
  | --- | ---: | ---: | ---: | ---: |
  | 90° | **3,716** | **1,924** | **1,924** | **71,956** |
  | 45° | **1,860** | **964** | **964** | **37,800** |
  | 22.5° | **932** | **484** | **484** | **20,712** |

- Every source/export has **zero degenerate faces and zero nonmanifold edges**, consistent
  winding, finite coordinates, unit-length normals, one mesh and four surfaces.
- All three **fresh-process exports are byte-identical** to the committed GLBs.
- Godot **4.8.dev7.official.c971f93e7** imports and resolves the full dependency chain, confirms
  GLB ancestry, identity transforms, bounds, opaque materials, collision and saved UIDs.
- Four scenes (three wrappers and fixture) pass two save/load/resave cycles without byte drift.
- **213 nominal support rays**, including both connector sides, and **9 outside/inner-void rays**
  are checked. **211 support rays hit directly; two exact shared-triangle-edge rays miss in
  Jolt.** Both misses are retained in JSON. Each requires **four surrounding rays at 0.0001 m**
  offsets, all hitting upward-facing Y=0 floor. Saved collision topology separately proves exact
  float32 shared edges with no cracks. This explicitly bounded numerical limitation is not
  hidden as a claim that every exact-edge ray hit. An initial strict run failed on those same
  two rays before adding these reported witnesses; no collision geometry was changed to mask it.
- **18 trajectories × 2 modes = 36 full traversals** exercise entry → bend → exit and reverse,
  at path radii **4.65 / 6 / 7.35 m**, using precomputed intent through production
  `ActorMotion.step`. Each segment endpoint must match within **0.002 m**, every tick retains
  floor support via `test_move`, and Y stays within 0.01 m. Cases use **74–210 fixed ticks per
  mode**, **4,488 ticks total**; AUTHORITY/REPLAY results agree. Reverse paths cover the reusable
  left-turn direction.
- Targeted pinned gdstyle checks pass without warnings. Both canonical runs pass engine/GUT
  pins, owned script compile/style, **14 Python tests**, GUT import and intentional-failure
  detection. The initial run passed **137/137 tests, 6,523 assertions**. The final run passed
  **136/137 tests, 6,520/6,523 assertions**: unchanged
  `tests/unit/audio/test_audio_voice_policy.gd::test_finished_one_shot_releases_voice_for_farther_event`
  fails at lines **113, 114 and 120** (one-shot completion/voice release counts). No audio code
  changed; no failing command was repeated unchanged. This is **not** an allowed ignored fixture
  failure: the final canonical suite is **not fully green**, and its timing-sensitive audio
  follow-up remains pending.

Four isolated Blender Cycles/CPU/AgX renders, **128 samples**, denoising:
[hero](city_boardwalk_02-evidence/hero.png), [side](city_boardwalk_02-evidence/side.png),
[detail](city_boardwalk_02-evidence/detail.png),
[47 m / 42° overhead](city_boardwalk_02-evidence/overhead_47m_42deg.png).
Native sizes are **1152×648 hero, 1024×576 detail, 1280×720 side and overhead**; no upscaling.
Hero and overhead show all three alternatives; side and detail show the 90° member. All were
visually inspected. Initial hero framing clipped the small variant and was corrected before
handoff. Final silhouettes are fully framed; muted radial seams and the slim slate backing stay
coherent with `.01`. At gameplay distance the warm curved walking strip reads before individual
boards. Overhead is vertical-down, **47 m height / 42° vertical FOV**, +Y Blender toward image
top, with studio-only offsets; not a native Godot gameplay capture or coastal-fit proof.
The 720 px cap supersedes historical 1280×800 evidence. PNGs use compression 95 while rendering,
then the same documented 7-bit/channel review-image encoding as `.01` to keep retention lean.
A trial 6-bit encoding showed background banding and was rejected. Smaller native hero/detail
renders meet the approximate 400 KB target without that banding; side/overhead are approximately
400 KB. Runtime source/export materials are unaffected.

### Exact reproduction (Git Bash, repository root)

Use a fresh scratch directory for each canonical run. The windowed editor is unavailable per
brief; scene text authoring followed by headless normalization is the authorized fallback.
No owner live Blender/Godot session is used or synchronized by these commands. Godot's project
addon starts its own short-lived endpoint during isolated CLI runs; no endpoint is contacted.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TOOLS=tools/asset_production/city_boardwalk_02
SCRATCH="C:/tmp/ft/assets/city_boardwalk_02/reproduce_$(date +%s)"
mkdir -p "$SCRATCH"
for script in author export render; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python "$TOOLS/$script.py"
done
# author_prefabs.py is INITIAL CREATION ONLY, before Godot normalization.
# It refuses existing files to preserve committed scene/node UIDs; do not rerun it here.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/export.py" -- "$SCRATCH/reexport"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/validate.py" -- "$SCRATCH/reexport"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script "res://$TOOLS/check.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "res://$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" check "$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" fmt --check "$TOOLS/check.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
python "$TOOLS/manifest.py" "$SCRATCH/checks"
```

Diagnostics are retained, not suppressed. Blender author/render emits the pinned API's
`Material.use_nodes` deprecation notice; source/export/validate/render jobs exit 0 without
allocation errors. Godot import emits the addon 4.8 compatibility warning. Editor normalization
exits 0 after successful saves but emits RID/ObjectDB shutdown leak diagnostics, matching the
sibling's editor-tool limitation. The final **non-editor resource/physics check exits 0 without
warnings/errors/leaks**. Canonical checks retain the unrelated final audio failure above.
No addon, production movement rule, audio rule or global setting was patched.

## Remaining acceptance

Independent art/technical review is required. Final dimension/radius selection, actual coast fit,
rail/fascia/support/transition mating, populated gameplay-camera readability, vehicle contact,
water-edge/falloff behavior, combat queries, navigation, real multiplayer transport/admission,
packaged-platform and sustained Deck/performance checks remain **pending**. Mode equivalence is
not a network test. Exact-edge Jolt ray precision and the final unrelated audio test failure are
explicit limitations for review. No register, TODO, district or whole-city gate is marked accepted.
