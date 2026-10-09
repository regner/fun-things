# d06_harbour_footbridge.01 — shared raised junction deck

**Source/export and linked component prefab delivered; independent review and assembled-route
acceptance pending.** Production commission supersedes the family brief's historical concept-only
restriction. Original model, integration and self-review: isolated commissioned production worker.
Supervisor approved the provisional dimensions/interface below before construction. No prior bridge
family outputs existed in this lane. The supervisor/user remain acceptance authorities.

References: [family brief](../d06_harbour_footbridge.md), [commission](commission.md),
[art direction](../../art-direction.md), [Signal Row concept](../../concepts/districts-v1/signal-row.md),
[map fit](../../concepts/districts-v1/map-context.md#signal-row-findings),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street context](../../concepts/world-v1/stage-04-streets/README.md).

## Design and provisional dimensions

One compact, thin, pale, three-portal Y junction. Its open top remains deliberately quiet; a cool pale
fascia and darker petrol underside distinguish slab depth in oblique views. Exposed edges have a
25 mm, three-segment bevel; portal faces remain planar for mating. No roof, tower, rail, light,
support, stair, sign or decorative obstacle is included. Those are separate family assets, not missing
pieces silently substituted into this record. The deck is original Blender construction, not a
procedural road-tool surface, downloaded mesh, generated image-to-mesh or runtime-created geometry.

The brief did not supply measurements. The live supervisor explicitly approved these **provisional
family interface values**, not final world placement, engineering or traversal acceptance:

- Three **3.2 m-wide** portals: north, south-east and west; centres **3.0 m** from the junction origin.
- Deck surface is **local Y = 0**, underside **Y = -0.35 m**. Pivot is **deck-surface centre**,
  deliberately not ground-contact centre. Blender Z maps to Godot Y; Blender +Y maps to Godot -Z.
- Intended placed surface height **5.5 m**, giving a slab-only underside **5.15 m** above flat ground.
  This reserves vehicle headroom; it is not a tested vehicle, road or future-support clearance claim.
- Godot AABB min **(-3, -0.35, -3)**, max **(3.252691269, 0, 3.252691269)** m.
  Width X × height Y × length Z: **6.252691269 × 0.35 × 6.252691269 m**.
- Numerical source/GLB tolerance **0.00001 m**; engine envelope/socket/query tolerance **0.001 m**.
  Metre units, root and mesh at identity, applied static rotation/scale; no hidden corrective scale.
- Spans .02–.04 must preserve width, slab depth and portal surface datum. .05 adapts three ground
  landings; its continuous collision ramp/stair-ramp must respect `ActorMotion.floor_max_angle`.
- .06 owns matching railings, restrained cyan edge lighting and supports, **including edge-blocking
  railing collision**. No columns may be assumed safe within road lanes. Nothing here changes roads,
  district polygons, terrain, navigation, actors or multiplayer rules.

## Snapping and perimeter contract for the remaining family

All coordinates are local Godot metres. Socket **local -Z points outward**, +Y points up. Public
markers at `Sockets/*` exactly relay the exported Blender empties; the engine checker compares their
full transforms. Do not introduce a second independently tuned socket offset. A mating span's incoming
socket must occupy the same plane with opposite outward direction, with both walking surfaces at Y=0.

| Public marker | Imported empty | Position | Outward direction | Godot yaw |
| --- | --- | --- | --- | --- |
| `Sockets/North` | `socket_north` | (0, 0, -3) | (0, 0, -1) | 0° |
| `Sockets/SouthEast` | `socket_south_east` | (2.121320344, 0, 2.121320344) | (0.707106781, 0, 0.707106781) | -135° |
| `Sockets/West` | `socket_west` | (-3, 0, 0) | (-1, 0, 0) | +90° |

The nominal footprint below is in cyclic order, as **(X,Z)** pairs. Each spans Y=-0.35 to 0.
Indices 0–1, 3–4 and 6–7 are the north, west and south-east open mating edges. Other edges belong to
.06's future exposed-edge treatment. The bevel is visual-only and does not inflate this footprint.

```text
0 ( 1.600000000, -3.000000000)    1 (-1.600000000, -3.000000000)
2 (-1.600000000, -1.600000000)    3 (-3.000000000, -1.600000000)
4 (-3.000000000,  1.600000000)    5 (-0.662741700,  1.600000000)
6 ( 0.989949494,  3.252691193)    7 ( 3.252691193,  0.989949494)
8 ( 1.600000000, -0.662741700)
```

## Source, export and materials

- Source: `art/source/models/environment/d06_harbour_footbridge_01/d06_harbour_footbridge_01.blend`.
- Export collection: `export_d06_harbour_footbridge_01`; root `D06HarbourFootbridge01`;
  one mesh `D06HarbourFootbridge01_Mesh` plus the three named socket empties.
- GLB: `art/models/environment/d06_harbour_footbridge_01/d06_harbour_footbridge_01.glb` and its
  preserved importer sidecar. Studio floor, camera and lights are outside the export collection.
- Reproducible scripts: `tools/asset_production/d06_harbour_footbridge_01/{author,export,validate}.py`.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Export uses
  `tools/assets/blender/export_settings.json`, restricted to the named collection with animations
  and skins disabled. Static modifiers are applied before saving; glTF triangulates the source.
- Material slot order: `deck_warm_pale`, `deck_pale_fascia`, `deck_petrol_underside`.
  Linear RGB respectively (0.72,0.73,0.66), (0.49,0.59,0.59), (0.075,0.16,0.18); roughness
  0.78/0.56/0.65. Opaque, back-culling Principled materials; no textures, embedded images, emission
  or additional Godot material remaps. These numeric colors are provisional family swatches.
- No rig, animations, destruction states or explicit LOD are applicable. Default importer automatic
  LOD/shadow mesh settings are retained; no platform cost budget or LOD visual acceptance is claimed.

## Prefab and collision

`scenes/prefabs/environment/d06_harbour_footbridge_01.tscn` links the GLB at **Visuals/Model**, identity
transform, noneditable imported children. No embedded render mesh or procedural runtime hierarchy.
Prefab UID `uid://b1f8xi50yoddt`; model UID `uid://clkvj0hhlhg1l`.

`Collision/Body` is a static-world layer-1/mask-0 StaticBody3D with four convex prism children:
Centre (footprint vertices 2,5,8), North (0,1,2,8), West (2,3,4,5), SouthEast (5,6,7,8). Together
these cover only the slab footprint/depth, not its empty recesses. The envelope intentionally ignores
the 25 mm cosmetic bevel to avoid tiny collision facets. No automatic triangle-mesh collision,
rail blocking, pillar, stair or ground collider is present. The unguarded component is **not a
standalone safe traversable route**; do not place it as completed bridge gameplay before .02–.06
assembly, guardrails and the downstream checks below.

Per the common brief, live MCP/editor sessions were prohibited and the windowed editor was unavailable.
The wrapper was authored as text and then loaded, packed, saved, reloaded and resaved using the pinned
headless editor. Second-save bytes were identical. This does not synchronize any separately open
editor scene. No live owner session was accessed.

## Evidence and validation

[Hero](d06_harbour_footbridge_01-evidence/hero.png),
[side](d06_harbour_footbridge_01-evidence/side.png),
[portal detail](d06_harbour_footbridge_01-evidence/portal_detail.png),
[gameplay-height overhead](d06_harbour_footbridge_01-evidence/overhead_47m_42deg.png).
All are isolated **Blender Cycles CPU / 32 samples / AgX, 1280×800** renders, inspected by the producer.
Hero/side/detail show the slab on a studio floor, not a placed structure. The overhead is vertical
perspective, north-up, **camera 47 m above ground, deck 5.5 m above ground**, vertical FOV 42°.
Only the render temporarily elevates the root; source/export/prefab keep Y=0 as the surface datum.
The pale Y outline and three square mouths read at this scale; the centre is intentionally undecorated.
Initial interpolated shading rounded the portal visually; explicit sharp normals corrected it before
final evidence. The separate railing/light family will supply the dark/cyan edge reading.
These images do not prove three complete ground routes or in-engine camera readability.

Numerical evidence: [validation.json](d06_harbour_footbridge_01-evidence/validation.json).
Producer SHA-256 inventory: [manifest.json](d06_harbour_footbridge_01-evidence/manifest.json).
Concise final receipt: [final.log](d06_harbour_footbridge_01-evidence/final.log).

- **236 triangles, 120 source vertices, 212 exported vertices including surface/normal splits**;
  **one mesh, three material surfaces**, five imported nodes (root, mesh, three empties).
- **Zero degenerate source faces/export triangles, zero non-manifold edges**, positive closed volume,
  finite coordinates, unit-length source corner and actual GLB normals. Portal dimensions measured
  from geometry, not inferred from empties. Source and actual GLB bounds match.
- Fresh export from the saved source is **byte-identical** to the delivered GLB.
- Pinned engine loads all dependencies and preserves imported ancestry, materials, AABB, identity
  transform, sockets and UIDs. Two-save normalization is byte-stable; fresh non-editor load/query
  exits 0 **without ERROR/WARNING diagnostics**.
- Eight independent top-ray solid/void cases pass at centre, three portals, three recesses and beyond
  the north portal. Upward ray measures underside **5.149999619 m** after test-only elevation to 5.5 m;
  horizontal ray at 5 m stays clear. These are bounded slab geometry queries, **not player/car motion**.
- Final `production_checks.py` **passes all layers**: 80 GDScripts formatted/linted/compiled,
  **11 Python tests**, **40 GUT tests / 458 assertions**, negative control detected. No pre-existing
  failures needed exemptions in this checkout. The first run found one owned async-loop lint warning;
  the final code follows the existing tool-only scan-wait pattern with a documented narrow waiver.
- Headless imports exit 0 with the existing MCP 4.8 compatibility warning. Editor-mode custom-tree
  normalization exits 0 with RID/ObjectDB shutdown leak diagnostics, retained in the concise log;
  it is not represented as a clean editor shutdown. An initial `filesystem_changed` wait timed out
  because no-change scans need not emit that signal; state polling fixed this. An initial Python
  validator used a nonexistent Vector distance method; corrected before final validation.

## Exact reproduction

From this worktree in bash; scratch output directories must be fresh for the production check runner:

```sh
NID=d06_harbour_footbridge_01
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# Independent exporter entrypoint (validate.py also performs a fresh export and byte comparison):
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

`record.py` consolidates existing successful source/engine/check receipts and hashes every produced
payload except its self-referential manifest. Raw retries and verbose tool logs stay in external scratch,
not the repository. Reauthoring may change Blender file bytes; deterministic GLB reexport is the gate.

## Remaining acceptance and handoff

Independent technical/art review is pending. Subsequent family workers must read the socket/perimeter
contract above without editing .01. .06 must keep the three portal mouths clear and supply edge guards;
.05 must check the production movement slope contract before authoring access collision. World integration
owns exact span lengths, support sites, three landings, unchanged roads/boundaries and any displaced
Old Quay placeholders. The raised route must remain on land, distinct from the harbour-mouth road bridge.

Assembled player/car movement, seam/turn/guardrail queries, overhead and under-bridge camera/aim occlusion,
navigation/topology, authority/prediction and real transport behavior remain untested for this bridge.
No full gameplay support for elevated routes is claimed. In-engine visual captures, packaged/device
checks and sustained performance are also pending. No world scene, TODO, queue or progress record was
changed, and this component delivery does not mark the entire bridge or register record accepted.
