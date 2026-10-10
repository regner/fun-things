# d06_harbour_footbridge.03 — southern-area connecting span

**Source/export and linked component prefab delivered; independent review and assembled-route
acceptance pending.** Original Blender construction, integration and visual self-review by the
commissioned isolated production worker. The supervisor/user remain acceptance authorities.
This is one component of the three-destination pedestrian connection, not a completed bridge.

References: [family brief](../d06_harbour_footbridge.md), [junction/interface](d06_harbour_footbridge_01.md),
[main-area span and approved length handoff](d06_harbour_footbridge_02.md), [commission](commission.md),
[art direction](../../art-direction.md), [Signal Row concept](../../concepts/districts-v1/signal-row.md),
[map context](../../concepts/districts-v1/map-context.md#signal-row-findings),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md), and
[street context](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes the family brief's historical concept-only restriction.

## Design and provisional dimensions

One straight, thin pale span continues the junction's **SouthEast** portal toward the northern
forecourt of Signal Row's southern shopping parade. It intentionally repeats .02's approved 12 m
slab design rather than inventing different southern decoration, width or depth. The .02 handoff
records the supervisor's direction that .03/.04 retain its interface and provisional length unless
the brief requires otherwise. This is that inherited direction, **not a new final world-fit approval**.

A broad quiet walking surface, cool pale fascia and petrol underside match .01/.02. Only the exposed
long edges receive a **25 mm, three-segment bevel**. Mating planes remain square and flush, with sharp
normals at the end edges. No roof, tower, sign, surface marking, ornament or obstacle is added.
Rails, cyan edge lights, edge-blocking collision and supports remain **.06-owned**; ground access
stairs/landings remain **.05-owned**. Geometry comes from original project-owned parametric Blender
construction, not downloads, purchased meshes, image-to-mesh or runtime-generated geometry.

- **3.2 m width × 0.35 m depth × 12 m length**, Godot X × Y × Z.
- Godot local AABB min **(-1.6,-0.35,-12)**, max **(1.6,0,0)** m.
- Pivot: **incoming portal surface centre (0,0,0)**, deliberately not ground-contact or slab centre.
  Local span runs along **-Z**, Z=0 to Z=-12. Blender +Y maps to Godot -Z; Blender +Z to Godot +Y.
- Walking surface **Y=0**; underside **Y=-0.35**. Intended placed surface height **5.5 m** reserves
  **5.15 m slab-only underside height** above flat ground. This is not certified vehicle headroom.
- Metric units/scale 1, root and mesh at identity, static transforms applied, no corrective root scale.
- Source/GLB dimension tolerance **0.00001 m**; engine bounds/socket/query tolerance **0.001 m**.
- Actual span length, landing footprint and support positions await the assembled fit study. Chaining
  modules does not establish safe support spacing or justify placing columns in road lanes.

## Snapping and family handoff

Public markers exactly relay the named Blender empties. Socket local **-Z points outward**, +Y up.
The incoming socket faces back toward the junction; outgoing faces along the span. The reusable
prefab remains unrotated; only its eventual placement rotates toward the southern forecourt.

| Public marker | Source empty | Local Godot position | Outward direction | Godot yaw |
| --- | --- | --- | --- | --- |
| `Sockets/Incoming` | `socket_incoming` | (0,0,0) | (0,0,+1) | 180° |
| `Sockets/Outgoing` | `socket_outgoing` | (0,0,-12) | (0,0,-1) | 0° |

To mate with .01, place the component at **(2.121320344,0,2.121320344)** relative to the junction,
with **yaw -135°**. Its incoming and `.01/Sockets/SouthEast` are coincident with opposed outward
axes. Outgoing becomes **(10.606601718,0,10.606601718)** in junction coordinates. Translate the
whole assembly to Y=5.5 only when using the provisional raised datum. Do not rotate the imported
`Visuals/Model` child, change socket offsets or compensate with a hidden scale.

For .06, local exposed long edges are **X=-1.6 and X=+1.6**, Z from -12 to 0, surface Y=0.
Short faces are **open mating connections**, not rail edges. Nominal collision corners are
(-1.6,0,0), (1.6,0,0), (1.6,0,-12), (-1.6,0,-12), with underside 0.35 m lower.
Use the same placement transform for associated rails/lights; preserve clear mouths and avoid
seam snag points. No support footprint is approved here. For .05, the outgoing socket is the
upper landing interface, not a claim that the shopping forecourt has been reached on the actual map.

## Source, export and materials

- Source: `art/source/models/environment/d06_harbour_footbridge_03/d06_harbour_footbridge_03.blend`.
- Export collection `export_d06_harbour_footbridge_03`; root `D06HarbourFootbridge03`, mesh
  `D06HarbourFootbridge03_Mesh`, and two socket empties. Studio ground, camera and lights are excluded.
- Explicit GLB: `art/models/environment/d06_harbour_footbridge_03/d06_harbour_footbridge_03.glb`, with
  its retained `.import`. No prototype dependency, external asset, texture or embedded image.
- Scripts: `tools/asset_production/d06_harbour_footbridge_03/{author,export,validate}.py`.
  The construction and validation recipe follows .02, with this record's own names/paths and
  a southern-orientation overhead view. No earlier family file or shared tool is modified.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Export loads the existing
  shared `tools/assets/blender/export_settings.json`, filtered to the named collection, with static
  animations/skins disabled. Modifiers are applied before saving; glTF triangulates source faces.
- Material order: `deck_warm_pale`, `deck_pale_fascia`, `deck_petrol_underside`; linear RGB
  (0.72,0.73,0.66), (0.49,0.59,0.59), (0.075,0.16,0.18), roughness 0.78/0.56/0.65. These match .01/.02.
  All are opaque, back-culling Principled materials. No emission or Godot material remaps.
- Rig, animations, destruction, textures and explicit LOD are not applicable. Default automatic
  importer LOD/shadow-mesh settings are retained; no platform cost budget is claimed.

## Prefab and collision

`scenes/prefabs/environment/d06_harbour_footbridge_03.tscn` links the GLB at **Visuals/Model** with
identity transform and noneditable imported children. No embedded render mesh or runtime hierarchy.
Prefab UID **uid://ibkajx12w4hu**; model UID **uid://cyd02lmjxtdfg**.

`Collision/Body` is a static-world layer-1/mask-0 StaticBody3D. Its only child `Slab` has
**BoxShape3D (3.2,0.35,12)** centred at **(0,-0.175,-6)**. The simple envelope deliberately ignores
the cosmetic 25 mm bevel rather than introducing tiny collision facets. There are no rail, support,
stair or ground colliders. **This unguarded component is not a standalone safe traversable route.**
Do not publish it as completed bridge gameplay before .04–.06, assembled guards and downstream checks.

The common brief prohibits live Blender/Godot MCP sessions and says the windowed editor is unavailable.
The wrapper was therefore authored as text and loaded, packed, saved, reloaded and resaved using the
pinned headless engine. The second save was byte-identical. This proves saved-resource stability, not
synchronization of a separately open editor scene. No live owner session was accessed.

## Evidence and validation

[Hero](d06_harbour_footbridge_03-evidence/hero.png),
[side](d06_harbour_footbridge_03-evidence/side.png),
[incoming portal detail](d06_harbour_footbridge_03-evidence/portal_detail.png), and
[47 m overhead](d06_harbour_footbridge_03-evidence/overhead_47m_42deg.png) are **1280×720 isolated
Blender Cycles CPU / 32 samples / AgX** renders inspected by the producer against the earlier family.
The pale thin slab, square ends and quiet surface are consistent. The overhead is vertical-down,
north-up, **47 m above ground / 42° vertical FOV**, with the span rendered at **5.5 m height and
-135° yaw** to illustrate the southern direction. Only the render receives that placement; the saved
source/export/prefab retain the local incoming surface datum and -Z orientation.

The first overhead had a hard illumination break from the unelevated studio lighting. Moving the
studio emitters with the render-only elevated/rotated slab corrected it; final overhead shows one
continuous pale route. Hero/side/detail use a floor immediately below the slab, not a placed bridge.
These images are not engine captures and do not prove complete routes to the three ground destinations.

[validation.json](d06_harbour_footbridge_03-evidence/validation.json) contains source, actual GLB and
engine measurements. [manifest.json](d06_harbour_footbridge_03-evidence/manifest.json) hashes every
produced payload except itself. [final.log](d06_harbour_footbridge_03-evidence/final.log) retains a concise
receipt and classified diagnostics; verbose logs/retries stay in external scratch.

- **60 triangles, 32 source vertices, 72 exported vertices including normal/material splits;
  one mesh, three surfaces, four imported nodes** (root, mesh and two empties).
- **Zero degenerate source faces/export triangles, zero non-manifold edges**, positive closed volume,
  finite coordinates and unit-length source corner/actual GLB normals.
- Source/GLB AABBs agree; both mating planes measure 3.2 m wide and 0.35 m deep from source vertices.
  Fresh export from the saved source is **byte-identical** to the delivered GLB.
- Pinned Godot resolves dependencies, imported ancestry/materials, AABB, identity model transform,
  full socket transforms and registered UIDs; two-save normalization is byte-stable.
- **Nine** isolated solid/void top rays pass at centre, both portals, inside/outside both sides and
  beyond both ends. Upward ray measures underside **5.149999619 m** after test-only elevation;
  a horizontal ray at Y=5 m remains clear of the slab, with no accidental pillar collider.
- Actual .01/.03 prefab mating passes at **SouthEast**. Outgoing lies at (10.606602,5.5,10.606602).
  **Six independent literal world-space top rays** straddle the diagonal junction seam by 1 cm on
  both sides at lateral offsets -1.5/0/+1.5 m; each hits its expected component at Y=5.5. These are
  geometry/API queries, **not production actor seam traversal or vehicle movement**.
- `production_checks.py` passes all layers: **85 GDScripts** formatted/linted/compiled,
  **11 Python tests**, **40 GUT tests / 458 assertions**, diagnostic negative control detected.
  No pre-existing failures required exemptions; owned GDScript also passes targeted gdstyle checks.
- Author, validator, import, normalization and fresh query process exit 0. Import retains the existing
  MCP pin compatibility warning. Editor-mode custom-tree normalization reports RID/ObjectDB shutdown
  leaks, preserved in final.log and not described as clean. The fresh non-editor query process has
  **no ERROR/WARNING diagnostics**.

## Exact reproduction

From this worktree in bash; choose a fresh production-check output directory for subsequent runs:

```sh
NID=d06_harbour_footbridge_03
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py performs a fresh export; the exporter can also be invoked independently:
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  "art/source/models/environment/$NID/$NID.blend" \
  --python "tools/asset_production/$NID/export.py" -- "$T/manual-reexport"
timeout 300 "$G" --headless --editor --path . --import --quit > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/normalize-final.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh-final.json" > "$T/prefab-fresh-final.log" 2>&1
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks-final"
python "tools/asset_production/$NID/record.py"
```

`record.py` refuses failed source/engine/check receipts before consolidating and hashing payloads.
Reauthoring may change .blend bytes; deterministic saved-source GLB reexport is the gate.

## Review round 1 — P3 evidence cleanliness

Addressed the sole finding for this component: regenerated all four evidence renders at
**1280×720**, PNG compression **95**, with film dithering disabled (the existing .05/.06 convention).
No palette quantization or post-render resizing was used. Saved-source studio settings and authoring
scripts agree; source geometry, materials, sockets, GLB bytes, importer settings and prefab bytes
remain unchanged from the reviewed candidate. No gameplay or placement changes were made.

| Render | Bytes |
| --- | ---: |
| `hero.png` | 253,299 |
| `overhead_47m_42deg.png` | 198,366 |
| `portal_detail.png` | 187,607 |
| `side.png` | 198,548 |

Combined PNG size fell from **3,951,134** to **837,820 bytes** (78.8% reduction).
All four views were visually inspected: full hero/side silhouettes and square portal detail remain
legible, and the 47 m / 42° overhead retains the intended route direction. The studio background
remains evidence-only, not a placed or engine-rendered environment. `validate.py` now checks saved
render settings; `record.py` rejects wrong-size PNGs and images above 400,000 bytes and records sizes.
Scratch-only negative controls for invalid PNG signature, 1280×800 dimensions and excess file size
were each rejected. All delivered PNGs also passed full Pillow decode and dimension/size checks.

Pinned author/render, source validation with byte-identical reexport, headless import, two-save
prefab normalization and fresh non-editor dependency/physics checks all passed again. The single
current lane-wide canonical run shared by .01–.04 passed **85 script checks, 11 Python tests,
40 GUT tests / 458 assertions**, including its diagnostic negative control. Fresh prefab logs remain
free of ERROR/WARNING; import retains the known MCP pin warning, normalization retains the existing
RID/ObjectDB shutdown diagnostics, and Blender retains `use_nodes` deprecation warnings.
These checks do not close downstream traversal, placement, rendering or device gates.

Review replay used the commands above for author/validate/import/normalize/fresh checks. Author and
validator logs are `$T/review-r1-author.log` and `$T/review-r1-validate.log`; current import/normalize/
fresh logs use the filenames above. Original engine receipts remain in `$T/pre-review-r1/`.
The canonical suite was run once for the identical final lane candidate, then reused explicitly:

```sh
C="C:/tmp/ft/assets/d06_harbour_footbridge_01/checks-review-r1"
# Run once for the lane; choose a fresh C directory for a subsequent replay:
timeout 1800 mise exec -- python tools/production_checks.py --output "$C"
# For this asset, with NID and T as defined above:
python "tools/asset_production/$NID/record.py" --checks "$C"
```

## Remaining acceptance

Independent technical/art review is pending. World integration owns exact span lengths, supports on
suitable ground, all three landings, southern forecourt fit, poster-drum separation, unchanged roads
and district boundaries, and any displaced Old Quay placeholders. The western link stays on land,
distinct from the harbour-mouth road bridge. No world, queue, progress or TODO file was changed.

Assembled player/car movement, seam crossing, guardrail collision, elevated-route navigation/topology,
under-bridge camera/aim occlusion, authority/prediction and real transport behavior remain untested.
In-engine visuals, packaged/device behavior and sustained performance are also pending. This delivery
does not claim full gameplay support for elevated routes or complete three-destination traceability.
