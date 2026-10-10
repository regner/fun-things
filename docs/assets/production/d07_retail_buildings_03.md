# d07_retail_buildings.03 — Small entrance annex

**Source/export and linked prefabs delivered; independent review and world/gameplay acceptance pending.**
Produced by the commissioned asset-production worker on `lane/a-retail`. Inputs:
[family brief](../d07_retail_buildings.md), [Broadlot concept](../../concepts/districts-v1/broadlot.md),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces),
[giant store and attachment contract](d07_retail_buildings_01.md) and
[secondary store](d07_retail_buildings_02.md). The resumed production commission supersedes
historical concept-only restrictions; it does not confer independent acceptance.
The worker owns source/export/bounded technical integration; the reviewer owns acceptance
and the world integrator owns eventual placement.

Original Blender construction: no downloads, real brands, image-to-mesh, external textures,
prototype dependencies or runtime-generated render geometry. No live Blender/Godot session
was touched. The authorized direct-file/headless import and pack/save workflow was used;
it does not synchronize an unrelated open editor.

## Design and provisional dimensions

A low, broad **attached closed entrance volume**, not a third standalone store. Its quiet
blue recessed roof, plum walls, slate piers, opaque entrance/sidelight groups and restrained
coral band continue both retail siblings. The parent remains much larger: this component
occupies only 51.84 m², compared with .01's 2,208 m² footprint. A saved attachment assembly
proves the intended relationship instead of substituting a detached shop pad.

Dimensions are **provisional authored values** within .01's 12 m wide × 6 m projection ×
4.15 m high allowance, not measurements inferred from concept images or approved parcels.
No world placeholders, forecourt, road, parking, district boundary or coastline changed.
All following coordinates are Godot-local metres, **-Z front**, **+Y up**.

| Element | Dimensions / bounds |
| --- | --- |
| Solid annex | X=-5.4…5.4, Z=-4.8…0, Y=0…4 |
| Complete visual AABB | min (-5.4,0,-4.8), max (5.4,4.08,0.12) |
| Whole visual width / height / depth | 10.8 / 4.08 / 4.92 m |
| Ground-contact pivot | (0,0,0), centre of **rear attachment edge**, not footprint centre |
| Roof deck top / blue coping crown | 3.74 / 4.0 m |
| Rear wall/coping closure | extends locally to Z=+0.12, meeting the recessed parent wall |
| Closed centre glazing | 3.6 m wide × 2.45 m high, centre X=0, Y=1.62 |
| Front sidelights | two 2.5 m wide × 2.45 m high opaque panes |
| Coral face | X=-4.2…4.2, Y=3.16…3.9, front Z=-4.8 |
| Coral top return | X=-4.2…4.2, Z=-4.78…-3.78, Y=3.8…4.08 |

Envelope/ground tolerance: ±0.001 m. Root and mesh have identity transforms, applied
rotation/scale and metre units. Blender +Y/+Z maps once to Godot -Z/+Y. The unusual rear
pivot follows the sibling's explicit attachment contract; no corrective prefab transform.

### Family continuity and attachment

Retained section proportions: 0.32 m petrol shoe, walls inset 0.12 m, 0.50 m blue coping,
roof deck recessed 0.26 m below crown and 0.23 m petrol reveal centred 0.65 m below crown.
The front coping/reveal are recessed a further 0.06 m behind the coral face to prevent
coplanar surface interference. The return ends 0.02 m behind that face. Rear closure
bridges the permitted 0.12 m to the parent wall; it is not a rear gameplay projection.

Attach the component root at **(0,0,-19)** in .01, identity yaw and scale. The rear solid
plane Z=0 meets .01's shoe/collider plane, while closure Z=+0.12 reaches its plum wall
at parent Z=-18.88. The 10.8 m width stays inside the reserved ±6 m bay and clear of the
adjacent display frames. Maximum height 4.08 m leaves 0.07 m below the parent's band
bottom at 4.15 m. The parent remains closed behind the annex; no shell opening is implied.

`d07_retail_buildings_03_attached.tscn` composes the unchanged .01 prefab at identity and
this annex at the stated datum. It is a reusable reference assembly, **not a saved world
placement**. Use the assembly once, or the annex with an existing parent; do not place the
assembly over an already placed .01 and duplicate its geometry/collision. .02 retains its
own closed entrance and does not receive a competing attachment interface.

No interiors, working doors, thresholds/steps, roof traversal, lights, animations,
destruction or interaction behavior. Blank coral is architectural identity hardware;
tenant copy, retail graphics, sign island and parking/forecourt dressing remain separate.
No gameplay sockets were requested; the datum is documented and saved as source properties.

## Source, export, materials and prefabs

- Source: `art/source/models/environment/d07_retail_buildings_03/d07_retail_buildings_03.blend`.
- Collection: `export_d07_retail_buildings_03`.
- Root / mesh: `D07RetailBuildings03` / `D07RetailBuildings03_Mesh`.
- Export: `art/models/environment/d07_retail_buildings_03/d07_retail_buildings_03.glb`.
- Prefab: `scenes/prefabs/environment/d07_retail_buildings_03.tscn`.
- Linked assembly: `scenes/prefabs/environment/d07_retail_buildings_03_attached.tscn`.
- Tools: `tools/asset_production/d07_retail_buildings_03/`.

One static mesh combines closed architectural pieces. Contact/intersection between walls,
roof, shoe, panes and trim is intentional, not a boolean union or navigable hollow shell.
All component edges are manifold; bevels and weighted normals are applied in the editable
source. glTF triangulates faces. No textures/embedded images, rig, clips, morphs or explicit
LODs. Godot import LOD/shadow generation remains at defaults, not performance acceptance.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**. `export.py` loads the
shared `tools/assets/blender/export_settings.json`, exports only the named collection and
disables animation/skins. Studio ground, lights and camera are excluded. For side/overhead
renders only, `author.py` reads .01's existing source mesh after saving/exporting this asset;
that context is neither saved into the annex blend nor exported into its GLB.

Seven opaque, back-culled Principled surfaces in actual GLB/Godot order. Names and values
match the siblings; slot order is asset-specific, not a shared index contract.

| Slot | Material | Linear base RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `retail_trim_petrol` | .028, .067, .092 | .25 / .47 |
| 1 | `retail_wall_plum` | .14, .08, .14 | .10 / .50 |
| 2 | `retail_roof_blue` | .035, .12, .30 | .18 / .46 |
| 3 | `retail_frame_slate` | .24, .32, .36 | .30 / .42 |
| 4 | `retail_glazing_opaque` | .022, .065, .09 | .32 / .25 |
| 5 | `retail_wall_slate` | .13, .19, .235 | .10 / .50 |
| 6 | `retail_band_coral` | .88, .20, .12 | .05 / .48 |

`Visuals/Model` is an identity-transform linked GLB instance. No copied render mesh,
editable imported children or material override. Prefab UID `uid://du2ujtjwiw5vb`, GLB
UID `uid://crtc3v5dremfs`, assembly UID `uid://bqgwo7xmiiseb`. Engine-generated scene/node
identities, GLB `.import` and check-script `.uid` are retained; scene UIDs are inline.

### Deliberate collision

One `Collision/Body` StaticBody3D, layer 1 / mask 0, containing one `AnnexSolid` box:
**size (10.8,4,4.8), centre (0,2,-2.4)**. It follows the entire closed annex footprint,
including closed entrance. The square shoe/collision corners conservatively enclose small
visual bevels; most wall faces are 0.12 m inset. No pane, pier or mullion snag colliders.
Rear closure is covered by the parent solid after attachment. The top 0.08 m coral return
is overhead visual-only. Collision on the roof does not authorize rooftop gameplay.

## Evidence and measured validation

[Hero](d07_retail_buildings_03-evidence/hero.png) ·
[Attached side](d07_retail_buildings_03-evidence/side.png) ·
[Entrance detail](d07_retail_buildings_03-evidence/frontage_detail.png) ·
[47 m / 42° overhead](d07_retail_buildings_03-evidence/overhead_47m_42deg.png).

All four final images were inspected. Blender Cycles CPU, 24 samples, denoised, AgX,
**1280×720**, PNG compression 95, no output dithering or painted/quantized postprocessing.
Hero/detail isolate the annex; side/overhead reuse the unchanged .01 source for attachment
context. The side exceeds the approximate 400 KB target slightly to retain both facades.
The calibrated overhead is vertical-down perspective at **47 m / 42° vertical FOV**,
Godot camera (0,47,0), annex at origin and parent shifted to (0,0,19), north at image top.
The giant rear roof is intentionally cropped at actual scale, not shrunk to fit the view.
The annex projection, blue roof and front coral return read clearly. These are isolated
Blender renders, not Godot lighting, populated-world or actor-visibility acceptance.

[validation.json](d07_retail_buildings_03-evidence/validation.json) records:

- **3,672 triangles**, **1,904 source vertices**, **2,448 GLB vertices** after splits;
  **one mesh / seven surfaces**.
- **Zero degenerate source faces**, **zero nonmanifold source edges**, **zero degenerate
  exported triangles**; finite positions/normals and unit-length normals asserted.
- Maximum normal-length errors: source **1.56e-7**, GLB **1.30e-7** (rounded up).
- Source, actual GLB accessors and Godot AABB match literal expected bounds within
  0.001 m; measured ground datum is exactly zero.
- Fresh reopened-source export is **byte-identical**, **105,816 bytes**, SHA-256
  `b538d3a0c33ac10310ad4f3190955155345df6a7455848f1c0fd12bc4b8b4da2`.
- Pinned import and fresh load resolve linked dependencies, UIDs, seven material surfaces
  and identity model transforms. Both prefab and attachment assembly pass byte-stable
  pack/save/reload/resave after initial engine normalization.
- **12 independent physics shape queries** cover closed entrance, interior, all four
  corners, exterior and above-roof clearance. Front ray hits (0,1,-4.8), within tolerance.
  A radius 0.35 m / height 1.8 m CharacterBody capsule swept 12 m stops at
  **Z=-5.1513671875**; a bypass at X=5.9 reaches **Z=2** without contact.
- **Six attachment seam queries** cover both sides and ends of the mating plane and clear
  outside corners. The saved assembly uses the exact parent datum, yaw and unit scale.
  These engine APIs prove bounded collision/dependency behavior, not production ActorMotion,
  car handling, combat, route or multiplayer acceptance.
- Targeted source/export validation, pinned import (no ERROR/SCRIPT ERROR), prefab
  roundtrip/fresh physics check, owned check-only compilation, and gdstyle lint/format
  all pass. Command exits and raw-log hashes are retained in `targeted_checks`.
  Earlier full-project test results are historical only, not a handoff prerequisite.

### Corrections and diagnostic limits

Initial renders exposed coplanar fascia/roof, rear coping and mullion intersections.
The front coping/reveal were recessed behind the coral face, the return separated from
its face plane, rear closure changed to abut rather than overlap the coping crown, and
mullion/plate faces offset slightly. Final source, exports, renders and receipts were
regenerated; dimensions and collider were unchanged. Parent geometry was not altered.

Blender reports API deprecation notices only. Headless editor normalization exits 0 and
saves stable bytes but reports the existing MCP 4.8 compatibility warning and shutdown
RID/ObjectDB leaks. Final import exits 0 with the compatibility warning. Fresh non-editor
load/physics and check-only compilation exit 0 without ERROR/WARNING. These diagnostics
are retained, not suppressed or described as clean; no engine/plugin patch was made.
The initial worker session was interrupted by a provider timeout; the resumed worker
inspected partial outputs and refreshed final engine/check receipts before committing.

[final.log](d07_retail_buildings_03-evidence/final.log) is the concise receipt;
[manifest.json](d07_retail_buildings_03-evidence/manifest.json) hashes every owned payload
except itself. Raw logs/retries/scratch exports stay at `C:/tmp/ft/assets/d07_retail_buildings_03/`.

## Exact reproduction

Run from repository root in Bash. All engines are isolated, pinned and timeout-bounded.
`run_check` records each actual exit and log; `set -e` stops before recording a manifest
if any command fails. Old exit receipts are removed before the run. No full-project
validation is required. For receipt-only refreshes, skip `author.py`: it is the source,
export and render creation step, not needed when those payloads are unchanged.

```sh
set -e
NID=d07_retail_buildings_03
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
rm -f "$T"/{validate,import-final,prefab-normalize,compile,prefab-fresh,gdstyle-lint,gdstyle-format}.exit
# Capture each actual exit; a failed command stops the set -e workflow.
run_check() {
  local name="$1" code=0
  shift
  "$@" > "$T/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$T/$name.exit"
  return "$code"
}
# Creation only; skip for a receipt-only refresh of unchanged source/exports/renders.
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py" > "$T/author-final.log" 2>&1
run_check validate timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py reopens source, measures actual GLB data and byte-compares a scratch reexport.
run_check import-final timeout 300 "$G" --headless --path . --import
run_check prefab-normalize timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize
run_check compile timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
run_check prefab-fresh timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh.json"
run_check gdstyle-lint timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
run_check gdstyle-format timeout 60 "$(mise which gdstyle)" fmt --check \
  "tools/asset_production/$NID/check_prefab.gd"
python "tools/asset_production/$NID/record.py"
```

`author.py` creates source/GLB and four renders; `export.py` applies the shared export
contract; `validate.py` measures source/GLB/reexport; `check_prefab.gd` checks saved resources,
collision and attachment, with `--normalize` for headless editor pack/save; `record.py`
consolidates final receipts and regenerates the manifest after the handoff is final.

## Review round 1 corrections

Replaced the prohibited full-project reproduction dependency with required targeted
command receipts in `record.py`, this reproduction block, validation JSON and final log.
The recorder checks actual GLB bytes/hash against the validator and regenerates the
manifest last.
Source, GLB, prefab and four render payloads are unchanged; source/reexport, import,
roundtrip, fresh dependency/physics, check-only compilation and gdstyle were rerun.
No new art or gameplay acceptance is claimed. Original broader test history remains
in Git, not a required input to current receipts.

## Remaining acceptance / handoff

1. Independent art/technical review of the exact committed candidate; no self-acceptance.
2. Retail graphics and detached sign island remain separate deliveries.
3. Saved world placement and preservation of roads/parking/forecourt, actual player/car
   motion/turning, weapon queries, authoritative/predicted and real multiplayer checks.
4. Actual Godot gameplay-camera lighting/visibility, LOD review, packaged dependency checks,
   repeated-instance cost and sustained target-device performance.
5. Headless editor shutdown diagnostics remain a tooling/integration limitation.

Only this asset's owned paths and the authorized .01/.02 stale-pending handoff links/current
manifest entries changed. Sibling source/export/prefab bytes and historical receipts remain
unchanged. No queue, progress, shared brief, catalogue, world scene or project settings
changed; no TODO, register row or whole-game gate is marked accepted.
