# d07_retail_buildings.01 — Giant stepped retail box

**Source/export and linked prefab delivered; independent review and world/gameplay acceptance pending.**
Produced by the commissioned asset-production worker on `lane/a-retail`, under the
resumed per-record commission. [Family brief](../d07_retail_buildings.md),
[Broadlot concept](../../concepts/districts-v1/broadlot.md),
[selected map](../../concepts/districts-v1/07-broadlot-map.png) and
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#broadlot--big-roofs-bigger-empty-spaces)
are the design inputs. The production commission supersedes the brief's historical
concept-only restriction; it does not accept this model or city placement by inference.
No preceding retail-family deliveries existed in this lane.

Original Blender construction only: no downloads, real brands, generated-image meshes,
external textures or prototype dependencies. The worker owns source, export and bounded
technical integration; the supervisor/reviewer owns acceptance, and the world integrator
owns eventual placement. No live Blender or Godot editor session was used or touched.

## Design and provisional dimensions

A giant low sales hall with a lower plum side wing and still-lower front sales wing.
Three unequal roof planes and the recessed front-right corner give a stepped plan as
well as a stepped elevation. Broad blue roofs, quiet slate/plum walls, opaque grouped
storefront/clerestory glazing, petrol reveals and a single coral entrance band follow
Broadlot rather than residential pitches or workshop sawteeth. There is deliberately
no roof-equipment clutter. Flat colours and small applied bevels provide smooth highlights.

These are **provisional authored dimensions**, consistent with the concept's approximate
65 × 38 m scale reference, not dimensions measured from its raster or ratified parcels.
The selected district's 474.5 × 234.8 m bounds are not this asset's allocation. The northern
17/19 consolidation and nearby forecourt remain a layout proposal; no existing footprint,
road, parking surface, shoreline, boundary or world scene is replaced here.

All dimensions below are Godot-local metres; front is **-Z**, up is **+Y**.

| Part | X bounds | Z bounds | Ground / maximum height |
| --- | --- | --- | --- |
| Main hall | -32…16 | -11…19 | 0 / 9.6 |
| Side wing | 16…32 | -5…19 | 0 / 7.2 |
| Front wing | -32…16 | -19…-11 | 0 / 5.4 |
| Coral band face | -10…10 | -19…-18.82 | 4.15 / 5.2 |
| Coral top return | -10…10 | -19…-17.76 | 5.16 / 5.48 |

- Complete visual AABB: **min (-32, 0, -19), max (32, 9.6, 19)**;
  width / height / depth **64 / 9.6 / 38 m**, ±0.001 m tolerance.
- Ground footprint is 2,208 m²: 48×38 plus the 16×24 side wing. The remaining
  front-right 16×14 m rectangle is open, not part of the solid building.
- Ground-centred root and mesh pivot at (0,0,0), centred on the bounding rectangle,
  not the irregular footprint's area centroid. Flat ground datum Y=0.
- Blender +Y front / +Z up maps once to Godot -Z / +Y. Export nodes and linked
  prefab model have identity transforms and unit scale; no compensating rotations.
- No interior, opening doors, roof traversal, animated/destruction states, light
  nodes or interaction behavior. Closed glazing is opaque, not an interior promise.

### Family sections and attachment handoff

The parametric `volume()` section in `author.py` is the reference for .02's wall/roof
language: 0.32 m petrol ground shoe, wall faces inset 0.12 m from its perimeter,
0.50 m wide blue coping, roof deck recessed 0.26 m below the coping crown, and a
0.23 m dark reveal centred 0.65 m below it. Reuse these section proportions and
material names/values in the secondary low retail box; do not duplicate this whole
stepped silhouette or make a scaled small-shop shell. These construction dimensions
are not shared runtime code or extra exported modules.

The **small entrance annex .03 is a separate attached component**, not another store:

- Attachment root datum **(0,0,-19)** on the shell, identity yaw; local -Z is outward.
  The annex's rear solid/collision plane should be local Z=0, extending forward.
- Reserved width **12 m** (X=-6…6), projection **up to 6 m**, overall height
  **up to 4.15 m**, below the coral face. This is a fit allowance, not a demand to
  fill every maximum. Annex ground must remain Y=0.
- The shell's closed plum wall is at Z=-18.88, while its shoe/collision edge is -19.
  Annex rear closure/trim may extend **0.12 m locally +Z** to meet that recessed wall;
  its gameplay solid need not extend behind the attachment datum. This avoids a
  visible seam without adding a shell opening or revising its collider.
- The central bay is blank intentionally. Adjacent display frames end at X=-6.49
  and start at X=7.29; do not cover them with a wider annex. The shell remains solid
  behind the annex; annex closed entrance presentation does not create an interior.
- No runtime sockets are requested. The ground datum and maximum allowance are
  recorded on the Blender root as authoring properties (not exported extras).

The coral face is blank architectural identity hardware. Tenant copy, promotional
artwork, detached sign island, parking markings, fixtures and world forecourt are
separate records; none is substituted here.

## Source, export, materials and prefab

- Source: `art/source/models/environment/d07_retail_buildings_01/d07_retail_buildings_01.blend`.
- Collection: `export_d07_retail_buildings_01`.
- Root / mesh: `D07RetailBuildings01` / `D07RetailBuildings01_Mesh`.
- GLB: `art/models/environment/d07_retail_buildings_01/d07_retail_buildings_01.glb`.
- Prefab: `scenes/prefabs/environment/d07_retail_buildings_01.tscn`.
- Tools: `tools/asset_production/d07_retail_buildings_01/`.

One static mesh combines closed architectural pieces. Contact/intersection between
wall, shoe, roof, trim and glazing components is intentional; this is not a boolean
union or hollow navigable shell. All component edges are manifold. Applied bevels
and weighted normals remain in the saved editable source; glTF triangulates faces.
Studio ground/camera/lights are outside the export collection. No textures, embedded
images, rig, animation, morphs or explicit LODs are needed. Import-generated LODs and
shadow meshes retain engine defaults; their populated-scene cost/appearance is unaccepted.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**. `export.py` uses
`tools/assets/blender/export_settings.json`, limits export to the named collection,
and disables animations/skins. No private substitute for the shared export contract.
Per-asset measurement and prefab checks follow the existing production tool pattern.

Seven opaque, back-culled Principled surfaces in actual GLB/Godot order:

| Slot | Material | Linear base RGB | Metallic / roughness |
| --- | --- | --- | --- |
| 0 | `retail_trim_petrol` | .028, .067, .092 | .25 / .47 |
| 1 | `retail_wall_slate` | .13, .19, .235 | .10 / .50 |
| 2 | `retail_roof_blue` | .035, .12, .30 | .18 / .46 |
| 3 | `retail_wall_plum` | .14, .08, .14 | .10 / .50 |
| 4 | `retail_frame_slate` | .24, .32, .36 | .30 / .42 |
| 5 | `retail_glazing_opaque` | .022, .065, .09 | .32 / .25 |
| 6 | `retail_band_coral` | .88, .20, .12 | .05 / .48 |

The prefab has identity-transform **Visuals/Model**, directly linked to the GLB.
No copied render mesh, editable imported children, material overrides or procedural
scene composition. Prefab UID `uid://d2cm3erl8jfjg`, GLB UID `uid://dastl8r660i3u`.
Godot-generated node identities, GLB `.import` and GDScript `.uid` are retained;
the `.tscn` stores its own UID inline.

### Deliberate collision

`Collision/Body` is one StaticBody3D, layer 1 / mask 0, with the minimum three
BoxShape3D children matching the three solid parts above. Sizes/centres:

- Main: size (48,9.6,30), centre (-8,4.8,4).
- Side: size (16,7.2,24), centre (24,3.6,7).
- Front: size (48,5.4,8), centre (-8,2.7,-15).

These boxes meet at their section boundaries without an interior passage. They
conservatively follow the ground-shoe envelopes, 0.12 m outside most wall faces;
their square corners do not reproduce small visual bevels. They preserve the
16×14 m front-right notch. No individual glazing/pier snag colliders. The coral
return above the front box is visual-only; no overhead trim or tiny decoration
adds collision. Roof collision does not authorize rooftop routes or gameplay.

## Evidence and measured validation

[Hero](d07_retail_buildings_01-evidence/hero.png) ·
[Side](d07_retail_buildings_01-evidence/side.png) ·
[Frontage detail](d07_retail_buildings_01-evidence/frontage_detail.png) ·
[47 m / 42° overhead](d07_retail_buildings_01-evidence/overhead_47m_42deg.png).

All four were inspected after fixes. Isolated Blender Cycles CPU, 24 samples,
denoised, AgX, **1280×720**, PNG compression 95, output dithering disabled. No image
quantization or post-render paint. Renders are approximately 396/359/484/209 KB;
the detail is slightly above the ~400 KB target to preserve surface highlights.

The overhead is genuinely vertical-down perspective at **47 m**, **42° vertical FOV**,
Blender camera (0,19,47), corresponding to Godot (0,47,-19); north is image top.
It is intentionally centred on the entrance/forecourt: a 64×38 m building cannot fit
in the view at that camera height, and its rear/left are cropped rather than shrinking
the asset or changing FOV. Roof steps and the top-facing coral band remain readable;
facade glazing is not essential overhead-readable information. Hero and side establish
the complete silhouette. These are not in-engine lighting or player-visibility proofs.

[validation.json](d07_retail_buildings_01-evidence/validation.json) records:

- **6,804 triangles**, **3,528 source vertices**, **4,536 GLB vertices** after splits;
  **one mesh / seven surfaces**.
- **Zero degenerate source faces**, **zero nonmanifold source edges**, **zero
  degenerate exported triangles**; finite coordinates/normals asserted.
- Maximum normal-length error: source **1.78e-7**, GLB **1.36e-7**.
- Source, actual GLB accessors and Godot AABB match literal expected bounds within
  0.001 m. Ground is approximately -8.94e-8 m from floating-point rounding.
- Fresh reexport from the reopened saved source is **byte-identical**, **189,408 bytes**,
  SHA-256 `07bfe7e69f708d7e411d84449fe6654d97acca43ab16c700468ba6c78d935ecb`.
- Pinned headless Godot import, linked dependencies, UIDs, actual seven material
  surfaces, transforms and three collision sizes/centres pass. Pack/save/reload/resave
  is byte-stable after initial engine normalization.
- **12 independent direct physics shape queries** pass for solid interior, closed
  front/rear, sides, clear notch, exterior and stepped-height clearance. Front ray
  hits (0,1,-19). A 0.35 m radius / 1.8 m high CharacterBody capsule moving 12 m stops
  at Z=-19.35009765625 on the front, and crosses the clear notch to Z=-6 exactly.
  These use real engine APIs, not duplicated collision formulae, but they are not
  production ActorMotion, vehicle, combat, multiplayer or route acceptance.
- Full `production_checks.py` passes: **218 scripts** lint/format/compile clean,
  **17 Python tests**, **165 GUT tests / 6,918 assertions**, and the intentional
  negative control is correctly rejected. No known-failure exclusions were needed
  on this checkout. The owned script also passes explicit lint/format/compile checks.

### Corrections and diagnostic limits

Visual inspection found a coplanar coral-return/blue-coping stripe in the first
camera render. Raising the return's top to 5.48 m removed the interference; all four
final renders and source/export checks were refreshed. Disabling output dithering
reduced evidence size without geometry changes or palette quantization.

The initial editor-mode normalization waited on a filesystem signal that did not
complete, and its bounded command timed out (124), without a saved prefab change.
It was replaced with bounded filesystem polling and a fail-closed 60-second check
deadline. The corrected editor run saves and verifies stable bytes, exits 0, but
reports the known editor/plugin shutdown RID/ObjectDB leaks and MCP 4.8 compatibility
warning. Those diagnostics are retained in the concise final log, not suppressed
or called clean. Fresh non-editor dependency/physics checks and explicit compilation
exit 0 without ERROR/WARNING diagnostics. An added collider-size assertion initially
exceeded the lint local-variable limit; extracting a focused collision-check helper
resolved it, followed by the clean full `checks-final2` run. Blender reports 6.0 API
deprecation notices only. No vendor, plugin or project-setting changes were made.

[final.log](d07_retail_buildings_01-evidence/final.log) is the concise check receipt;
[manifest.json](d07_retail_buildings_01-evidence/manifest.json) hashes every delivered
payload except itself. Raw logs, intermediate renders and scratch exports remain
outside the checkout at `C:/tmp/ft/assets/d07_retail_buildings_01/`.

## Exact reproduction

Run from repository root in Bash. Only isolated timeout-bounded processes are used.
The production-check output directory must be fresh; use another suffix on reruns.

```sh
NID=d07_retail_buildings_01
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py reopens source, measures actual GLB data and byte-compares a scratch reexport.
# Independent export entrypoint, when needed:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background "art/source/models/environment/$NID/$NID.blend" \
  --threads 4 --python-exit-code 1 --python "tools/asset_production/$NID/export.py" \
  -- "$T/manual-reexport"
timeout 300 "$G" --headless --path . --import > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/prefab-normalize-final.log" 2>&1
timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh.json" > "$T/prefab-fresh.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks-final2"
python "tools/asset_production/$NID/record.py"
```

`author.py` builds the editable source, exports, and renders the four views.
`export.py` loads the shared settings and accepts an output directory after `--`.
`validate.py` validates source/GLB and fresh-export bytes. `check_prefab.gd` validates
saved engine resources and bounded physics; `--normalize` is only for headless editor
pack/save. `record.py` incorporates the final external receipts and hashes payloads.

## Remaining acceptance / handoff

1. Independent art/technical review of this exact candidate; no self-acceptance.
2. **d07_retail_buildings.02** secondary low box remains pending; use the family
   section and material contract above. **d07_retail_buildings.03** entrance annex
   remains pending; attach using the reserved bay and rear-closure allowance above.
3. Separate retail graphics and sign-island owners provide their own deliveries.
4. Saved world placement, road/parking/forecourt preservation, actual player/car
   movement/turning, weapon queries and authoritative/predicted/multiplayer checks.
5. Actual Godot gameplay-camera lighting/visibility, import LOD review, packaged
   dependency checks, repeated-instance cost and sustained target-device performance.
6. Editor CLI shutdown diagnostics remain an integration/tooling limitation; this
   asset does not patch the pinned engine or plugins.

No queue, progress, shared brief, catalogue, sibling, world scene or global project
file was modified. No whole-game gate, TODO or register row is marked accepted.
