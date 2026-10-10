# city_boardwalk.04 — Coastal support assembly

10 October 2026. **Source, export and linked prefab delivered; bounded asset checks pass.
Independent review, world placement and gameplay/device acceptance remain pending.**
Produced by the commissioned implementation specialist on `lane/a-boardwalk`, under the
[production commission](commission.md) and current per-asset common brief. The latter supersedes
the historical lead-only Git/prefab restriction. No sibling, shared brief, register, project
setting, world scene or shoreline was changed.

Family: [shared island boardwalk](../city_boardwalk.md). Read and matched the delivered
[straight deck](city_boardwalk_01.md), [bends](city_boardwalk_02.md) and
[fascia/trim](city_boardwalk_03.md), Petrol & Coral [art direction](../../art-direction.md),
The Crescents v02 and world-v1 stage-03 district identities / stage-04 streets. These are style
and route references, not engineering or measured coast-fit evidence. Original Blender
construction only; no downloads, image-to-mesh, brands, external textures or runtime meshes.

## Design and dimensions

A simple dark-slate **two-post bent**: one continuous crosshead, two square posts, broad low
foot shoes and quiet upper collars. Soft manufactured arrises and the same two slate values
as `.03` make it a subordinate structural member, not a competing landmark. No noisy bolts,
diagonal snag points, duplicate timber slab, rail, lamp, seat, rock or seawall were introduced.
The shallow family underdeck bears on the crosshead; the support does not occupy the walk line.

All dimensions and support pitch are **provisional**, under the standing instruction to proceed
with sensible family-compatible values. Actual ground/shore fit and structural capacity remain
unapproved. Numerical source/export/import envelope tolerance: **0.001 m**; source-to-binary
coordinate comparison: **0.00001 m**.

| Interface | Godot local metres |
| --- | --- |
| Overall width X / height Y / depth Z | **3.360 / 2.000 / 0.560** |
| Whole visual AABB | **(-1.680,0,-0.280) → (1.680,2.000,0.280)** |
| Pivot | **(0,0,0)**, ground-centred between the two feet; not the deck surface |
| Axes | Crosshead spans **X**; route follows **-Z**; +Y up |
| Crosshead | **3.360 × 0.320 × 0.480**, centre (0,1.840,0), top **Y=2.000** |
| Post centres | **X=±1.380**, Z=0; centre spacing **2.760** |
| Each post | **0.340 × 1.620 × 0.380**, Y=0.080 to 1.700 |
| Each ground shoe | **0.500 × 0.120 × 0.560**, Y=0 to 0.120 |
| Each upper collar | **0.440 × 0.140 × 0.480**, Y=1.540 to 1.680 |
| Roundovers | Head/posts **12 mm**, shoes **14 mm**, collars **10 mm**, two segments |
| Ground to walking surface when fitted | **2.240 m**: 2 m support plus 0.24 m sibling deck |
| Provisional straight support pitch | **3.000 m**, independent of the 6 m deck repeat |

Seven closed solids share one mesh. The posts overlap their shoes/collars and enter the
crosshead by 20 mm, deliberately hiding internal butt seams; the assembly is not a boolean
union or a watertight single fabrication. Each component is manifold. The shoes are visible
support hardware, **not newly authored shore foundations**. No seabed or water level is implied.

### Family mating and placement

- For a `.01` whose walking surface is Y=0, place this support at **Y=-2.240**. Its bearing
  top then meets the existing **Y=-0.240** underside. Conversely, feet at world Y=0 require
  the deck/fascia roots at **Y=2.240**. Never apply a corrective model scale or rotation.
- On a centred 6 m straight, use supports at local **Z=±1.500**, aligned with the route.
  Repeating the deck every 6 m continues the provisional 3 m support rhythm. These offsets
  are demonstrated in the saved fixture, not a ratified engineering span or placed route.
- The **3.36 m** head fits inside `.01`'s **3.52 m** backing width, leaving **80 mm** per side.
  It is **120 mm** inboard of the timber edges and does not overlap `.03`'s outboard fascia.
  Fascia and shared rail mounting remain separate; this support adds no rail sockets.
- On a `.02` bend, put the bent centre on the 6 m centre-line arc at station θ:
  **(6(1−cos θ), deck Y−2.24, −6 sin θ)**, Godot yaw **−θ**. The crosshead is radial.
  The fixture checks the **22.5° station of the 45° bend**, translated X=24 for isolation.
  Six underside rays at that station pass. Other angle/station placements are dimensional
  guidance only; avoid connectors and independently fit bearing footprints before placement.
- The **1.680 m** crosshead soffit is **not an actor passage** for the 1.8 m capsule. Do not
  route pedestrians/cars under these supports. Their real central void is retained for
  visual and low query accuracy, not to promise an accessible underwalk or interior.
- Fit feet to existing stable shore/ground using rigid placement. Do not stretch the model,
  float the shoes above rocks, alter island polygons or fill water to accommodate it. Uneven
  or deeper sites need downstream fit review, not an undocumented extension of this asset.
- `.05` owns landward connections; `city_shore_edges` owns seawalls/rocks. Shared
  `city_quay_furniture.02` owns guard geometry/collision. None is duplicated or required to
  load this standalone component. Safe waterfront deployment still requires their integration.
- The six recorded coastal districts remain prospective consumers; Old Quay is only a candidate.
  **East Docks remains excluded**. No closed ring, inner-basin dock, reclamation or bridge
  across navigable water is authorized by this delivery.

## Source, export and materials

- Source: `art/source/models/environment/city_boardwalk_04/city_boardwalk_04.blend`.
- Named collection: **`export_city_boardwalk_04`**.
- Identity-transform root / mesh: **`CityBoardwalk04` / `CityBoardwalk04_Mesh`**.
- Explicit linked export: `art/models/environment/city_boardwalk_04/city_boardwalk_04.glb`,
  with committed `.glb.import` identity metadata.
- Parametric author, exporter, binary validator, isolated renderer, initial prefab author,
  saved mating fixture, headless checker and manifest helper:
  `tools/asset_production/city_boardwalk_04/`.

Metre units, applied transforms and weighted corner normals; Blender +Y/+Z converts exactly
once to Godot -Z/+Y. The export contains only the root and mesh. Studio objects are transient
in `render.py`, never saved to the source or export. Context decks/fascia in hero/overhead
renders are loaded from unchanged sibling Blender sources, not copied into this deliverable.

One mesh, two opaque, backface-culled Principled surfaces in exported slot order:

| Slot / name | Linear base RGB | Metallic / roughness |
| --- | --- | --- |
| 0 `boardwalk_support_slate` | (.048,.069,.078), matching sibling underdeck/fascia | .15 / .58 |
| 1 `boardwalk_support_shoes` | (.090,.126,.137), matching sibling edge trim | .20 / .50 |

No textures, embedded images, UV-dependent shaders, emission, transparency, redundant `.tres`
copies, rig, animation, destruction state or sockets. Materials remain GLB-owned. No custom
LOD; default Godot automatic LOD/shadow-mesh generation is retained, pending repeat-placement
review. Shared `tools/assets/blender/export_settings.json` remains the export-settings owner.
Local recipes follow the established family conventions; this checkout has no shared generic
Blender construction/binary-audit helper. No new shared tooling or competing contract was added.

## Prefab and collision

`scenes/prefabs/environment/city_boardwalk_04.tscn` retains the imported GLB at
**`Visuals/Model` with identity transform**. No embedded render meshes, editable imported
children, runtime hierarchy construction or gameplay script. Scene/dependency UIDs and node
identities were normalized headlessly and preserved through save/load/resave.

One StaticBody3D at **`Collision/Body`**, **layer 1 / mask 0**, has three direct enabled boxes:

| Child | Size X/Y/Z | Centre X/Y/Z |
| --- | --- | --- |
| `LeftPost` | .500 / 1.680 / .560 | -1.380 / .840 / 0 |
| `RightPost` | .500 / 1.680 / .560 | 1.380 / .840 / 0 |
| `Crosshead` | 3.360 / .320 / .480 | 0 / 1.840 / 0 |

The two post boxes deliberately envelope each post, collar and shoe, avoiding tiny collision
steps or decorative snag points. They are up to 80 mm wider and 90 mm deeper per side than the
posts. The third box matches the crosshead. Together they preserve the low central void;
there is no full-width invisible wall beneath it. The crosshead is below 2.5 m and must block
an approaching full-height actor. Visual bevels do not bevel collision. The sibling deck owns
its continuous walk collider; this prefab does not duplicate it.

`tools/asset_production/city_boardwalk_04/mating_check.tscn` saves a dressed straight on two
supports, a 45° bend on a radial support, and a separate contact specimen. Its floor and actor
are collision-only test shapes, not generated visible assets or world placements. The actor
uses the production **ActorMotion** API, capsule **radius 0.35 m / height 1.8 m**.

## Validation and evidence

[validation.json](city_boardwalk_04-evidence/validation.json) records measured source/binary,
Godot resource/physics results and canonical-check outcomes.
[manifest.json](city_boardwalk_04-evidence/manifest.json) hashes every delivered payload except
itself. [final.log](city_boardwalk_04-evidence/final.log) retains a concise command/diagnostic
receipt. Raw logs, intermediate images and fresh exports remain outside the checkout.

- Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**.
- **756 triangles, 392 source vertices, 504 GLB vertices; one mesh / two surfaces**.
- **Zero degenerate source/export faces and zero nonmanifold edges**, including actual binary
  edges after exact-position welding across normal/material seams. Consistent winding,
  unit-length source/export normals, finite coordinates, identity transforms and bounds pass.
- Ground Y=0 and bearing Y=2 match the independent dimensional contract. A fresh-process export
  is **byte-identical** to the committed **22,892-byte GLB**.
- Godot **4.8.dev7.official.c971f93e7** imports and loads all dependencies, verifies GLB ancestry,
  bounds, opaque materials and the three-box compound. **Two saved scenes** pass repeated
  save/load/resave with byte-stable results and registered scene/dependency UIDs.
- **18 underside bearing rays** pass: two straight supports plus one radial bend support,
  six points each. Every hit is the intended sibling deck at **Y=2.000**.
- **Five structure rays** pass: both posts and crosshead block; the low centre and exterior
  bypass remain clear. Hits identify the intended static body and exact collider depth.
- **Seven trajectories × two modes = 14 runs / 672 fixed ticks** use production
  `ActorMotion.step`, 48 ticks per mode. Both post contacts stop at **Z=0.630208 m**;
  the too-low central crosshead stops the full-height capsule at **Z=0.500000 m**. The clear
  bypass and all three above-deck lines finish at **Z=-2.000001 m**. Every tick retains floor
  support, with no lateral drift. AUTHORITY and REPLAY outcomes agree.
- Pinned gdstyle passes all **162 scripts** and formatting. Python recipe byte-compilation
  passes. Canonical checks pass engine/GUT pins, **14 Python tests**, **137/137 GUT tests /
  6,523 assertions**, GUT import and intentional-failure detection.
- **The aggregate canonical command exits 1**: its shared **120-second** compilation deadline
  expires after **99 of 162 scripts**, leaving **63 deadline results**, including this checker.
  All failed compilation logs say `CHECK DEADLINE EXCEEDED`; these are incomplete checks, not
  observed GDScript defects. Rendering ran concurrently and may have increased contention.
  A subsequent **targeted `--check-only`** of this asset's checker in the canonical clean
  compiler mirror exits **0 with clean diagnostics**. Full resource/physics execution also
  passes. The failed aggregate command was not repeated unchanged or suppressed; the full
  canonical suite remains **not fully green**. Aggregate compilation follow-up stays pending.

Four isolated Cycles/CPU/AgX renders, **96 samples**, denoising:
[hero](city_boardwalk_04-evidence/hero.png), [front elevation](city_boardwalk_04-evidence/side.png),
[head/collar detail](city_boardwalk_04-evidence/detail.png),
[47 m / 42° overhead](city_boardwalk_04-evidence/overhead_47m_42deg.png).
Native sizes are **1152×648 hero, 1024×576 detail, 1280×720 side and overhead**. All were visually
inspected: the broad open bent, closed feet and restrained joint shading read cleanly. The
assembled support is intentionally hidden under the warm deck in the vertical gameplay view;
it must not become decorative clutter in the walking line. Hero/overhead also show an isolated
bent for identification. The detail intentionally crops the beam/column to show the connection.
Overhead is vertical-down at **47 m / 42° vertical FOV**, Blender +Y at image top, with studio-only
placements. These are **not native Godot gameplay, populated coast-fit or engineering captures**.
The current 720 px cap supersedes historical 1280×800 evidence. PNG compression 95 at render,
then the sibling 7-bit/channel review-image encoding, keeps evidence lean; runtime materials
and geometry are unaffected.

### Exact reproduction (Git Bash, repository root)

Use fresh external scratch for each canonical run. The windowed editor is unavailable per brief;
text-authored scenes followed by headless normalization are the authorized fallback. No owner
live Blender/Godot session is used, modified or synchronized. The project addon starts its own
short-lived local endpoint during isolated CLI runs; no endpoint is contacted.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
TOOLS=tools/asset_production/city_boardwalk_04
SCRATCH="C:/tmp/ft/assets/city_boardwalk_04/reproduce_$(date +%s)"
mkdir -p "$SCRATCH"
for script in author export render; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python "$TOOLS/$script.py"
done
# author_prefabs.py is INITIAL CREATION ONLY; it refuses existing normalized scenes.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/export.py" -- "$SCRATCH/reexport.glb"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$TOOLS/validate.py" -- "$SCRATCH/reexport.glb"
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script "res://$TOOLS/check.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . --script "res://$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" check "$TOOLS/check.gd"
timeout 30 "$(mise which gdstyle)" fmt --check "$TOOLS/check.gd"
python -m compileall -q "$TOOLS"
timeout 1800 mise exec -- python tools/production_checks.py --output "$SCRATCH/checks"
# Retain the aggregate result even if it fails; this scoped compile does not replace it.
timeout 180 "$GODOT" --headless --path "$SCRATCH/checks/script-checks/compiler-project" \
  --check-only --script "res://$TOOLS/check.gd" > "$SCRATCH/targeted-compile.log" 2>&1
printf '%s\n' "$?" > "$SCRATCH/targeted-compile.exit"
python "$TOOLS/manifest.py" "$SCRATCH/checks"
```

Diagnostics are retained, not hidden. Blender's version-only probe emits a 23-byte shutdown
allocation notice; author/render emit the pinned `Material.use_nodes` deprecation notice.
Actual author/export/validate/render jobs exit 0 without allocation errors. Godot import emits
the addon 4.8 compatibility warning. Editor normalization saves successfully and exits 0 but
emits RID/ObjectDB shutdown leak diagnostics, matching sibling editor-tool limitations. The
final **non-editor resource/physics check and targeted compiler run exit 0 without warnings,
errors or leaks**. Initial targeted style warnings were corrected before canonical checks.
No vendor code, movement rule or global setting was patched.

## Remaining acceptance

Independent technical/art review is required. Final height/pitch/dimensions, actual shore/ground
and bend station fit, rail/access integration, populated native gameplay-camera readability,
vehicle contact, water-edge/falloff rules, combat queries, navigation, real multiplayer
transport/admission, packaged platforms and sustained Deck/performance remain **pending**.
AUTHORITY/REPLAY equality is not a network test; this is not structural engineering certification.
Incomplete aggregate compilation remains an explicit review limitation. No register, TODO,
district route or whole-city gate is marked accepted by this delivery.
