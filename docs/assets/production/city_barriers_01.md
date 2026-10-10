# city_barriers.01 — Short bollard

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay acceptance pending.** Produced by the commissioned implementation
specialist on `lane/a-barriers`. The current production task/common brief supersedes
historical concept-only and lead-only integration restrictions in the
[commission](commission.md). Family: [city_barriers](../city_barriers.md).
No other family member, shared register, progress record or world placement was changed.

## Design and dimensions

Original Blender construction: a compact dark petrol-metal bollard with a lightly
flared ground shoe, tapered shaft, rolled amber shoulder and shallow dark crown.
The single amber safety band rolls onto the shoulder so it remains a small top-view
cue. Broad smooth highlights and no fasteners, grime, logos or fine texture noise
keep it quieter than actors. It is pedestrian separation hardware, **not** a mooring
bollard, fence post, rail terminal or removable/destructible mechanism.

Direction follows Petrol & Coral, the approved district identities, and Stage 4's
furniture/route constraints. Dimensions below are **provisional authored choices**
under the standing production rules, not measurements inferred from concept images.

- Godot width X / height Y / depth Z: **0.360 × 0.900 × 0.360 m**.
- Godot AABB minimum `(-0.180, 0, -0.180)`, maximum `(0.180, 0.900, 0.180)` m.
- Ground shoe maximum diameter 0.360 m; shaft diameter 0.300 → 0.290 m.
- Shoulder diameter 0.320 m; amber band occupies Y=0.740–0.880 m.
- Root and mesh pivots `(0,0,0)` at the ground-centred footprint; Y=0 ground datum.
- Rotationally symmetric; Blender +Z → Godot +Y and Blender +Y → Godot -Z.
- Metre units, unit scale, identity rotation/location; no corrective prefab transform.
- Envelope/datum tolerance ±0.001 m; source/GLB coordinate agreement tolerance 0.00001 m.

Family handoff: `barrier_dark_metal` uses the accepted ordinary street-pole petrol
values; `barrier_safety_amber` is the restrained amber accent. Later service barriers
can reuse this palette without copying the bollard geometry. The rail/chain-link
members still follow their distinct family ownership. No sibling outputs existed
in this lane when this member began.

## Source, exports and materials

- Source: `art/source/models/environment/city_barriers_01/city_barriers_01.blend`.
- Export collection: `export_city_barriers_01`; root `CityBarriers01`; child
  `CityBarriers01_Mesh`; editable mesh `CityBarriers01_Geometry`.
- Explicit export: `art/models/environment/city_barriers_01/city_barriers_01.glb`
  with its committed `.import` sidecar. No prototype dependency.
- Tools: `tools/asset_production/city_barriers_01/{author,export,validate,finalize}.py`.
- Source geometry is one closed lathed shell, not overlapping capped components.
  Cameras, lights and the inspection floor are outside the named export collection.

Two opaque, backface-culled Principled material surfaces; no textures or embedded
images, no emission, transparency or unsupported procedural shading:

| Slot | Name | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `barrier_dark_metal` | (0.025, 0.075, 0.090) | 0.45 | 0.46 |
| 1 | `barrier_safety_amber` | (1.000, 0.527, 0.102) | 0.00 | 0.42 |

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. The export
script loads `tools/assets/blender/export_settings.json`, scopes the collection,
and disables skins/animations. No rig, sockets, UV map, texture, animation, damage
state or explicit LOD is needed for this static uniform-color fixture. Godot's
per-asset default generated LOD/shadow-mesh/compression settings are retained;
no performance budget is claimed and no project-wide import setting changed.

## Prefab and collision

`scenes/prefabs/environment/city_barriers_01.tscn` instances the imported GLB at
**`Visuals/Model` with identity transform**. No embedded mesh or runtime-authored
visual hierarchy. The saved wrapper and collision-only check scene were loaded,
packed and resaved headlessly. Two consecutive saves retain exact bytes and node
IDs. Scene UID `uid://ctqpd7a13v35p`; GLB UID `uid://c6avlcbkejtq`. Engine-generated
scene UIDs live in scene headers; the GDScript's generated `.uid` is retained.
The headless saver retains path-based external references; the checker separately
asserts all four resource UIDs are registered to their exact paths.

Standing collision rule: one separate `Collision/BollardBody` StaticBody3D with one
CylinderShape3D, radius **0.180 m**, height **0.900 m**, centre `(0,0.450,0)`.
Static-world layer 1 / mask 0 matches accepted environment prefabs. It conservatively
includes the broad shoe: at the narrow shaft the radial overestimate is 0.035 m.
This avoids a complex snag-prone collider and does not imply destruction or physics
interaction. Placement must preserve deliberate foot and car routes; do not infer
approved bollard spacing or an approved vehicle exclusion layout from this prefab.

Saved test fixture: `tools/asset_production/city_barriers_01/check_scene.tscn`.
It instances the actual prefab and production `ActorMotion` script, with a
radius 0.35 m / height 1.8 m capsule and a collision-only floor. It is not a new
visible floor asset or city layout. `check.gd` asserts the actual imported bounds,
materials, ancestry, dependency UIDs, simple collider and public physics outcomes.

## Validation and evidence

[Hero](city_barriers_01-evidence/hero.png) · [side](city_barriers_01-evidence/side.png) ·
[shoulder detail](city_barriers_01-evidence/detail.png) ·
[47 m / 42° overhead](city_barriers_01-evidence/overhead_47m_42deg.png).
All four are isolated Blender CPU Cycles renders at **1280×720**, PNG compression 9,
seven significant bits/channel to reduce denoised-background entropy. The current
common brief's 720-pixel maximum supersedes the example's historical 1280×800 size.
Overhead is vertical-down perspective, 47 m above datum, **42° vertical FOV**,
Blender +Y / Godot -Z at image top; it is not a close-view crop or enlarged asset.

Self-inspection: the hero/side silhouette reads as a short manufactured post with a
single amber band; the detail shows the continuous shoulder/cap transition. At the
calibrated overhead distance the asset reads as a roughly seven-pixel amber-rimmed
dot with a small shadow, intentionally subordinate to actors. It cannot communicate
an entire restricted route by itself. Actual street lighting, repeated placement,
moving-camera visibility and actor/target overlap remain downstream checks.

Measured source/export results in [validation.json](city_barriers_01-evidence/validation.json):

- **448 source vertices, 418 polygon faces, 892 triangles; 576 exported vertices**
  after material/normal splits; **one mesh / two surfaces**.
- **Zero degenerate faces/triangles and zero non-manifold edges**; positive closed
  volume 0.0649482 m³; finite coordinates and unit-length source/GLB normals.
- Maximum normal-length error <0.0000001; measured bounds match the stated envelope.
- Export contains exactly the root plus mesh, no cameras, lights, textures or animation.
- **Fresh export from the saved `.blend` is byte-identical** to the 21,124-byte GLB.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports and loads dependencies;
  linked-model identity, bounds, two opaque back-culled surfaces, registered UIDs and
  stable scene save/reload pass.
- Low ray at Y=0.5 hits the bollard; ray at Y=1.0 passes above it.
- Production `ActorMotion.step` runs 48 ticks for each contact/bypass case in both
  authority and replay modes. Contact stops at Z=-0.531250 m; bypass at X=0.8 m
  ends at Z=2.000001 m. Both modes match; capsule remains on the Y≈0.001 test floor.
  This is local simulation parity, **not network transport/prediction acceptance**.
- Canonical production checks: all owned GDScript formatting/lint/compilation pass;
  **119/119 GUT tests, 6,362 assertions pass**, including the required negative check.
  **13/14 Python tests pass**. The unchanged `test_host_budget_tracking` Popen mock
  lacks context-manager methods when Windows `platform.system()` starts a subprocess.
  Overall command exits 1; it is reported, not suppressed or attributed to this asset.
  Final owned script changes also pass a fresh targeted format/lint/compile/physics run.

[final.log](city_barriers_01-evidence/final.log) records the concise command receipt
and diagnostic classification. Initial validator misuse of a bmesh void return was
fixed without a geometry change. Initial editor-script resaving emitted shutdown RID
leaks; recovery mode disabled the check. The final **standalone headless** roundtrip
and check exit 0 without diagnostics. Headless import emits the existing MCP addon
version warning (4.8 vs latest tested 4.7); no source/resource error occurred. No live
Blender/Godot MCP session was contacted. Raw scratch logs remain outside the checkout.
The [producer manifest](city_barriers_01-evidence/manifest.json) hashes every delivered
payload, including source, scripts, scene, import metadata, renders and this record;
it excludes itself.

## Exact reproduction

From the repository root in Git Bash, with pinned tools already installed:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
mkdir -p C:/tmp/ft/assets/city_barriers_01

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_01/author.py
# Opens the saved source and exports again into C:/tmp/ft/assets/city_barriers_01/reexport.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_01/validate.py
# Standalone explicit export, if needed independently:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  art/source/models/environment/city_barriers_01/city_barriers_01.blend \
  --python tools/asset_production/city_barriers_01/export.py \
  -- C:/tmp/ft/assets/city_barriers_01/reexport

timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/city_barriers_01/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . \
  --check-only --script res://tools/asset_production/city_barriers_01/check.gd
timeout 30 "$GDSTYLE" fmt --check tools/asset_production/city_barriers_01/check.gd
timeout 30 "$GDSTYLE" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/city_barriers_01/check.gd
# Requires a fresh empty output directory; retain an earlier run outside the checkout.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/city_barriers_01/checks
python tools/asset_production/city_barriers_01/finalize.py
```

`author.py` recreates source/export/renders. `validate.py` replaces validation.json;
run the Godot check afterward, then finalize to retain all receipt sections. Do not
rewrite accepted source/UIDs just to rerun a check. Production-check failure above is
an open shared-tooling issue, not permission to edit another lane's files.

## Remaining acceptance

Independent technical/art review is pending. Dimensions/spacing remain provisional.
World integration owns clear route placement, corner/entrance setbacks, repeated-row
readability and actual actor/target visibility. Vehicle impacts/turning/clearance,
real separate-process network admission/prediction, target-device packaged behavior,
Deck readability and sustained rendering/performance remain **unperformed**. No world
scene, gameplay rule, runtime destruction state or shared tracking entry changed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
