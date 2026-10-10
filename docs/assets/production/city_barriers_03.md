# city_barriers.03 — Low service barrier

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay acceptance pending.** Produced by the commissioned implementation
specialist on `lane/a-barriers`. The current task/common production brief supersedes
the historical concept-only and lead-only integration restrictions in the
[commission](commission.md). Family: [city_barriers](../city_barriers.md).
No shared register, progress record, sibling asset or world placement was changed.

## Design and dimensions

Original Blender construction: a short, solid pale-concrete service separator with
a broad battered lower flank, softened end arrises, narrow dark-metal protective
shoe and two sparse amber bands wrapping over the top onto both upper faces. The
continuous closed shell uses face-assigned materials, not overlapping decal meshes.
Smooth broad highlights and clean uniform surfaces follow Petrol & Coral; no grime,
logos, fasteners, lifting mechanism or fine texture noise. It is a **low solid
service-edge separator**, not a rail, bollard, chain-link fence or gate.

Direction follows the approved Ironreach/East Docks identities and Stage 4's quiet
furniture/clear-route constraints. The `.01` bollard's metal and amber material
values are preserved. No `.02` output exists in this checkout at the starting
revision `a71282e`; that assembly record is not a dependency of this solid separator.
The rail members retain their separate quay-furniture ownership.

These dimensions are **provisional authored choices** under the standing production
rules, not measurements inferred from concept images or approved placement spacing:

- Godot width X / height Y / depth Z: **2.400 × 0.600 × 0.550 m**.
- Godot AABB minimum `(-1.200, 0, -0.275)`, maximum `(1.200, 0.600, 0.275)` m.
- Long axis X; both long faces are equivalent. Blender +Z → Godot +Y;
  Blender +Y → Godot -Z. No corrective prefab rotation/scale.
- Broad lower foot is 0.550 m deep; main upper flank narrows to 0.350 m;
  flat top between the chamfers is 0.290 m deep.
- Two 0.180 m wide amber bands at X=-0.980…-0.800 and +0.800…+0.980 m,
  wrapping from Y=0.230 m to the top. Central 1.600 m span stays unmarked.
- Dark shoe occupies the lower 0.080 m of the long faces/underside; the concrete
  end cheeks remain exposed. End rounding is confined to the last 0.040 m per end.
- Root and mesh origins `(0,0,0)` at the ground-centred footprint, Y=0 datum.
  Metre units, identity location/rotation and unit scale; all modifiers applied.
- Envelope/ground tolerance ±0.001 m; source/GLB agreement tolerance 0.00001 m.

At 0.600 m this is lower than the family's 0.900 m bollard. Placement must still
check feet/target occlusion and preserve the two yard vehicle exits and foot bypass;
a low silhouette alone does not prove those constraints.

## Source, exports and materials

- Source: `art/source/models/environment/city_barriers_03/city_barriers_03.blend`.
- Collection `export_city_barriers_03`; root `CityBarriers03`; child
  `CityBarriers03_Mesh`; editable mesh `CityBarriers03_Geometry`.
- Export: `art/models/environment/city_barriers_03/city_barriers_03.glb` and its
  engine-generated `.import` sidecar. No prototype or external asset dependency.
- Tools: `tools/asset_production/city_barriers_03/{author,export,validate,finalize}.py`.
  Per-record scripts follow the accepted bollard/light conventions; the exporter
  uses the shared `tools/assets/blender/export_settings.json` contract unchanged.
- Construction uses explicit length sections and a chamfered cross-section in Blender,
  one closed shell with weighted corner normals. Studio floor/cameras/lights stay
  outside the export collection. No imported or downloaded geometry was used.

Three opaque, backface-culled Principled surfaces, stable slot order:

| Slot | Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `barrier_pale_concrete` | (0.480, 0.500, 0.460) | 0.00 | 0.78 |
| 1 | `barrier_dark_metal` | (0.025, 0.075, 0.090) | 0.45 | 0.46 |
| 2 | `barrier_safety_amber` | (1.000, 0.527, 0.102) | 0.00 | 0.42 |

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. No textures,
embedded images, UV maps, emission, transparency, rig, sockets, animations, damage
states or explicit LOD are needed for this static uniform-color prop. Default
per-asset Godot generated LOD/shadow-mesh/compression settings remain unchanged;
no performance budget is claimed and no global import setting changed.

## Prefab and collision

`scenes/prefabs/environment/city_barriers_03.tscn` instances the imported GLB at
**`Visuals/Model` with identity transform**. No embedded mesh or runtime-authored
visual hierarchy. The wrapper and collision-only fixture were authored as text,
then loaded/packed/resaved by isolated pinned headless Godot, per the common brief.
No live editor/MCP session was touched. Two successive saves retain exact bytes
and node identities; no claim is made about synchronizing a separate open editor.

- Prefab UID: `uid://vmg7hp3beq7w`.
- GLB UID: `uid://c4soogv8m6sln`.
- Engine-generated scene UIDs live in scene headers; the check script's generated
  `.uid` is retained. All four fixture/dependency resource UIDs resolve to their paths.
- One separate `Collision/BarrierBody` StaticBody3D, static-world layer **1**, mask **0**.
- One **BoxShape3D size (2.400, 0.600, 0.550) m**, centre `(0,0.300,0)`.
  This conservative envelope includes the lower foot and avoids snag-prone detailed
  collision. It overestimates the tapered sides by approximately 0.130 m per side
  at the flat top, slightly more at the rounded ends. Ground contact and total
  height remain exact. It does not imply removability, destruction or movable physics.

Saved test fixture: `tools/asset_production/city_barriers_03/check_scene.tscn`.
It instances the actual prefab and production `ActorMotion` script with a radius
0.35 m / height 1.8 m capsule and a collision-only test floor. The fixture adds
no visible floor model or world placement. `check.gd` tests actual imported bounds,
linked ancestry, dependency UIDs, simple collision and public physics outcomes.

## Validation and evidence

[Hero](city_barriers_03-evidence/hero.png) · [side](city_barriers_03-evidence/side.png) ·
[end/band detail](city_barriers_03-evidence/detail.png) ·
[47 m / 42° overhead](city_barriers_03-evidence/overhead_47m_42deg.png).
All four are isolated CPU Cycles Blender renders at **1280×720**, PNG compression 9,
seven significant bits/channel to reduce background entropy. The current common
brief's 720-pixel maximum supersedes the example's historical 1280×800 evidence.
Overhead is vertical-down perspective, **47 m height / 42° vertical FOV**, north-up
(Blender +Y / Godot -Z at image top), not an enlarged model or cropped camera view.

Producer self-inspection of all four views: the broad pale body reads as a low solid
edge, the dark shoe grounds it, and the two amber wraps remain quiet top-view cues.
The detail shows clean continuous arrises and no floating decal surfaces. The true
overhead footprint is roughly **48 × 11 pixels** with a short shadow; bands are
small but distinct. This isolated lighting/readability observation is not an engine
street capture or actor/target-occlusion acceptance. Independent art review is pending.

Measured results in [validation.json](city_barriers_03-evidence/validation.json):

- **192 source vertices, 178 polygon faces, 380 triangles; 260 exported vertices**
  after normal/material splits; **one mesh / three surfaces**.
- **Zero degenerate faces/triangles; zero non-manifold edges**; closed positive
  volume 0.5932144 m³. Finite coordinates, unit-length source/GLB normals.
- Maximum source normal-length error 0.000000139; export error 0.000000091.
- Actual source/GLB/engine AABBs match the provisional envelope within tolerance.
- Export contains exactly root plus mesh, no cameras/lights/textures/animation.
- **Fresh export from saved `.blend` is byte-identical** to the 11,216-byte GLB.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports and loads all dependencies;
  model identity, three opaque back-culled surfaces, registered UIDs and two-scene
  byte-stable save/reload pass.
- Low ray at Y=0.5 hits `BarrierBody`; ray at Y=0.7 passes above the barrier.
- Production `ActorMotion.step`, 48 ticks per contact/bypass case in both authority
  and replay modes: contact stops at Z=-0.626302 m; bypass at X=1.8 m reaches
  Z=2.000001 m. Capsule remains on the Y≈0.001 m floor and both modes match.
  This is local simulation parity, **not network transport/prediction acceptance**.
- Canonical production checks **pass without ignored failures**: owned-script
  formatting/lint/compilation; **14/14 Python tests; 119/119 GUT tests with 6,362
  assertions**; required diagnostic negative test correctly returns 1.

[final.log](city_barriers_03-evidence/final.log) is the concise command/diagnostic
receipt. Source authoring and validation passed on their first runs. Blender emits
only future-6.0 `use_nodes` deprecation notices; headless import emits the existing
MCP addon 4.8-versus-tested-4.7 warning. No new source/resource/script errors or
standalone-check diagnostics occurred. No failure was suppressed. Raw logs/scratch
reexports remain outside the checkout. The [producer manifest](city_barriers_03-evidence/manifest.json)
hashes every delivered payload, including source, tools, prefab, import metadata,
renders and this record; it excludes itself.

## Exact reproduction

From the repository root in Git Bash, with the pinned tools installed:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
mkdir -p C:/tmp/ft/assets/city_barriers_03

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_03/author.py
# Opens the saved source, measures actual binary accessors, and reexports to scratch.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_03/validate.py
# Optional standalone export, using the same shared settings:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  art/source/models/environment/city_barriers_03/city_barriers_03.blend \
  --python tools/asset_production/city_barriers_03/export.py \
  -- C:/tmp/ft/assets/city_barriers_03/reexport

timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/city_barriers_03/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . \
  --check-only --script res://tools/asset_production/city_barriers_03/check.gd
timeout 30 "$GDSTYLE" fmt --check tools/asset_production/city_barriers_03/check.gd
timeout 30 "$GDSTYLE" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/city_barriers_03/check.gd
# Requires an empty output directory: retain previous runs outside the checkout.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/city_barriers_03/checks
python tools/asset_production/city_barriers_03/finalize.py
```

`author.py` recreates source/export/renders. `validate.py` replaces validation.json;
run the Godot check after it, then finalize to retain every receipt section. Do not
rewrite source or UIDs merely to inspect the existing asset. `finalize.py` requires
a successful canonical-check summary and compacts renders before hashing delivery.

## Remaining acceptance

Independent technical/art review remains pending. Dimensions and placement spacing
remain provisional. World integration owns entrance setbacks, route gaps, repeated
placement, target/feet visibility and actual gameplay-camera captures. Vehicle
contact/turning/clearance, real separate-process network admission/prediction,
packaged target-device behavior, Deck readability and sustained rendering/load
performance remain **unperformed**. No world scene, road geometry, interaction,
gameplay rule or shared tracker was changed; no blanket production-ready verdict.
