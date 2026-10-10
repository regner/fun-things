# d07_retail_buildings.02 — Secondary low retail box

**Source/export and linked prefab delivered; independent review and world/gameplay acceptance pending.**
Produced by the commissioned asset-production worker on `lane/a-retail`. Inputs:
[family brief](../d07_retail_buildings.md), [Broadlot concept](../../concepts/districts-v1/broadlot.md),
[selected map](../../concepts/districts-v1/07-broadlot-map.png),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces)
and [giant retail sibling](d07_retail_buildings_01.md). The resumed production commission
supersedes the brief's historical concept-only restriction, not its design constraints.
The worker owns source/export/bounded integration; the supervisor and independent reviewer
own acceptance, and the world integrator owns eventual placement.

Original Blender construction only: no downloads, real brands, image-to-mesh, external
textures, prototype references or runtime-generated render geometry. No live Blender/Godot
session was used. Editor-managed files used the explicitly authorized direct-text plus
pinned headless import/pack/save fallback; this does not synchronize an open editor.

## Design and provisional dimensions

One broad, low, rectangular sales hall contrasts with the giant sibling's three stepped
roof planes and recessed corner. A single quiet blue roof, slate sides, muted plum public
frontage and offset coral entrance band preserve Broadlot's family identity. Four grouped
opaque display bays and a closed double entrance provide restrained human-scale detail.
Sparse side piers and one closed rear service panel finish the non-public elevations;
there is no rooftop equipment clutter, sawtooth workshop roof or residential pitch.

These are **provisional authored dimensions**, not measurements inferred from the raster
or accepted parcel sizes. The concept proposes combining middle footprints 14/20 and
freeing 06/04 for parking; this delivery neither replaces those placeholders nor changes
roads, forecourts, district boundaries or the shoreline. The district's 474.5 × 234.8 m
bounding rectangle is not this asset's allocation.

All dimensions are Godot-local metres: front **-Z**, up **+Y**.

| Element | Dimensions / bounds |
| --- | --- |
| Solid rectangular hall | 42 m wide × 28 m deep × 6.6 m coping height |
| Ground footprint | 1,176 m²; X=-21…21, Z=-14…14 |
| Complete visual AABB | min (-21,0,-14), max (21,6.68,14); size (42,6.68,28) |
| Roof deck top | Y=6.34, recessed 0.26 m below blue coping |
| Plum frontage | X=-20.85…20.85, Y=0.3…5.3, face Z=-13.89 |
| Closed entrance surround | 4.6 m wide × 3 m high, centred X=8, Y=1.7 |
| Coral band | X=1…15, Y=5.3…6.5, face Z=-14 |
| Coral top return | X=1…15, Z=-14…-12.76, Y=6.36…6.68 |

Tolerance is ±0.001 m for measured envelope/ground. Root and mesh pivot are the
bounding-footprint ground centre (0,0,0). Blender +Y front / +Z up maps once to Godot
-Z / +Y; root, mesh and linked prefab model have identity transforms and unit scale.
The hall occupies about 53% of .01's 2,208 m² footprint and has a 6.6 m rather than
9.6 m main roof: it remains a large retail store, not a rescaled small-shop shell.

### Family continuity and boundaries

The `volume()` section follows .01's documented construction proportions: 0.32 m petrol
shoe, walls inset 0.12 m from its perimeter, 0.50 m blue coping, roof deck recessed
0.26 m, and a 0.23 m petrol reveal centred 0.65 m below the coping. Identical material
names and values are retained. The source is independently authored from these section
parameters; it does not depend on executing the sibling's author script or duplicate
its three-tier silhouette. Repeated placements reuse this single prefab.

This store has its own **closed** entrance; no interior, working door, roof traversal,
loading dock, destruction, animation, lights or interaction system is implied.
The separate **.03 entrance annex remains assigned to .01's reserved bay**, whose
attachment contract is unchanged; .02 does not introduce a competing annex interface.
No sockets were requested. Coral is blank architectural hardware, not delivered tenant
copy or accepted wayfinding; retail graphics/sign island remain separate records.

## Source, export, materials and prefab

- Source: `art/source/models/environment/d07_retail_buildings_02/d07_retail_buildings_02.blend`.
- Collection: `export_d07_retail_buildings_02`.
- Root / mesh: `D07RetailBuildings02` / `D07RetailBuildings02_Mesh`.
- GLB: `art/models/environment/d07_retail_buildings_02/d07_retail_buildings_02.glb`.
- Prefab: `scenes/prefabs/environment/d07_retail_buildings_02.tscn`.
- Reproduction/check tools: `tools/asset_production/d07_retail_buildings_02/`.

One static mesh combines closed architectural components. Wall/shoe/roof/trim/glazing
contacts and intersections are intentional; this is not a boolean union or navigable
hollow shell. All individual component edges are manifold. Applied bevels and weighted
normals are baked into editable source geometry; glTF triangulates faces. Studio ground,
camera and lights stay outside the export collection. No textures, embedded images,
rig, animation, morphs or explicit LODs. Default import LOD/shadow generation is retained;
populated-scene cost and LOD appearance remain unaccepted.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. `export.py` loads
`tools/assets/blender/export_settings.json`, restricts export to the named collection
and disables animations/skins. No private replacement for the shared export contract.

Seven opaque, back-culled Principled surfaces, in actual GLB/Godot order:

| Slot | Material | Linear base RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `retail_trim_petrol` | .028, .067, .092 | .25 / .47 |
| 1 | `retail_wall_slate` | .13, .19, .235 | .10 / .50 |
| 2 | `retail_roof_blue` | .035, .12, .30 | .18 / .46 |
| 3 | `retail_wall_plum` | .14, .08, .14 | .10 / .50 |
| 4 | `retail_frame_slate` | .24, .32, .36 | .30 / .42 |
| 5 | `retail_glazing_opaque` | .022, .065, .09 | .32 / .25 |
| 6 | `retail_band_coral` | .88, .20, .12 | .05 / .48 |

`Visuals/Model` is an identity-transform linked GLB instance; no copied mesh, editable
imported children, material overrides or runtime-authored hierarchy. Prefab UID
`uid://p052akskcswu`, GLB UID `uid://ck0gbao60mbw2`. Engine-normalized node identities,
GLB `.import` and check-script `.uid` are retained; the prefab UID is inline in `.tscn`.

### Deliberate collision

One `Collision/Body` StaticBody3D, layer 1 / mask 0, with one `ShellSolid` BoxShape3D:
**size (42,6.6,28), centre (0,3.3,0)**. The solid spans the whole closed store, including
the entrance. It follows the shoe/coping perimeter, conservatively 0.12 m outside most
wall faces. Tiny bevels, glazing, transoms and piers do not create snag colliders.
The coral return's top 0.08 m is overhead visual-only. There are no corner gaps or
extra blockers beyond the documented rectangular envelope. Roof collision does not
establish a walkable route or authorize rooftop gameplay.

## Evidence and measured validation

[Hero](d07_retail_buildings_02-evidence/hero.png) ·
[Rear/side](d07_retail_buildings_02-evidence/side.png) ·
[Frontage detail](d07_retail_buildings_02-evidence/frontage_detail.png) ·
[47 m / 42° overhead](d07_retail_buildings_02-evidence/overhead_47m_42deg.png).

All four final renders were inspected. Isolated Blender Cycles CPU, 24 samples,
denoised, AgX, **1280×720**, PNG compression 95, no output dithering. Approximately
313/304/339/191 KB respectively; no image quantization or painted postprocessing.
The overhead is genuinely vertical-down perspective, camera Blender (0,0,47),
Godot (0,47,0), **42° vertical FOV**, north at image top. The full rectangular roof
fits at actual scale with a small margin, and the coral return remains visible.
Glazing is not essential overhead information. These are not Godot lighting,
player-visibility or populated-city acceptance captures.

[validation.json](d07_retail_buildings_02-evidence/validation.json) records:

- **4,536 triangles**, **2,352 source vertices**, **3,024 GLB vertices** after splits;
  **one mesh / seven surfaces**.
- **Zero degenerate source faces**, **zero nonmanifold source edges**, **zero
  degenerate exported triangles**; finite coordinates and normals asserted.
- Maximum normal-length errors: source **1.59e-7**, GLB **1.07e-7** (rounded up).
- Source, actual GLB accessors and Godot bounds match literal expected AABB within
  0.001 m. Ground is -8.94e-8 m from float rounding.
- Fresh reexport from the reopened saved source is **byte-identical**, **127,392 bytes**,
  SHA-256 `20b470ccb685fe717fa110a17b389b69de3b329bb41ee6b00def38ef985edb1b`.
- Pinned headless import and fresh prefab load resolve all dependencies, UIDs,
  seven actual material surfaces and identity transforms. Pack/save/reload/resave
  is byte-stable after initial normalization.
- **12 independent direct physics shape queries** pass: closed entrance/interior,
  all four corners, clear front/sides/rear, roof solid and above-roof clearance.
  A front ray hits **(8,1,-14)**. A 0.35 m radius / 1.8 m high CharacterBody capsule
  swept 12 m stops at **Z=-14.35009765625**; a side bypass at X=21.5 reaches **Z=-8**
  without contact. These are real physics APIs, not production ActorMotion, car
  handling, combat or multiplayer acceptance.
- Full `production_checks.py` passes: **219 GDScripts** lint/format/compile clean,
  **17 Python tests**, **165 GUT tests / 6,918 assertions**, and the intentional
  negative control correctly rejected. No known-failure exclusions were needed.
  The owned check also passes explicit lint, format and compile commands.

### Corrections and diagnostics

The first hero exposed the plum skin buried behind the slate wall. Its face and the
adjacent glazing stack were moved forward within the unchanged footprint; the final
hero/detail confirm plum visibility. All final renders, source, GLB and checks were
regenerated. No palette, dimension or collision workaround was used.

Blender reports API deprecation notices only. Headless editor normalization exits 0,
saves stable bytes and passes resource/physics assertions, but reports existing
MCP 4.8 compatibility and editor shutdown RID/ObjectDB leak diagnostics. These are
retained, not suppressed or called clean. Fresh **non-editor** load/physics and
check-only compilation exit 0 without ERROR/WARNING diagnostics. Final import exits 0
with the compatibility warning. No engine, plugin or project-setting patch was made.

[final.log](d07_retail_buildings_02-evidence/final.log) is the concise receipt;
[manifest.json](d07_retail_buildings_02-evidence/manifest.json) hashes every produced
payload except itself. Scratch exports/retries/raw logs stay outside the checkout at
`C:/tmp/ft/assets/d07_retail_buildings_02/`.

## Exact reproduction

From repository root in Bash, using isolated bounded processes. Production-check
output must be fresh; use a new directory on reruns and pass it to `record.py`.

```sh
NID=d07_retail_buildings_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py" > "$T/author-final.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py" > "$T/validate.log" 2>&1
# Independent export entrypoint, if needed (validate.py already byte-compares a reexport):
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background "art/source/models/environment/$NID/$NID.blend" \
  --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/export.py" \
  -- "$T/manual-reexport"
timeout 300 "$G" --headless --path . --import > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/prefab-normalize.log" 2>&1
timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh.json" > "$T/prefab-fresh.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python "tools/asset_production/$NID/record.py" --checks "$T/checks"
```

`author.py` constructs source/GLB and renders; `export.py` applies shared settings;
`validate.py` measures source/actual GLB and fresh export bytes; `check_prefab.gd`
checks engine resources and bounded physics, with `--normalize` reserved for headless
editor pack/save; `record.py` consolidates final external receipts and hashes payloads.

## Remaining acceptance / handoff

1. Independent art/technical review of this exact candidate; no self-acceptance.
2. **d07_retail_buildings.03** entrance annex remains pending, using **.01's** reserved
   bay and rear-closure allowance. Neither sibling geometry nor that interface changed.
3. Retail graphics and detached sign island remain separate deliveries.
4. Saved world placement, parking/road/forecourt preservation, actual player/car
   movement/turning, weapon queries and authoritative/predicted/multiplayer checks.
5. Actual Godot gameplay-camera lighting/visibility, LOD review, packaged dependencies,
   repeated-instance cost and sustained target-device performance.
6. Headless editor shutdown diagnostics remain a tooling/integration limitation.

Only this asset's owned paths and the specifically requested .01 handoff-link/current
manifest update changed. .01 historical receipts and all source/export/prefab bytes
remain unchanged. No queue, progress, shared brief, catalogue, world scene or global
project file changed; no TODO, register row or whole-game gate is marked accepted.
