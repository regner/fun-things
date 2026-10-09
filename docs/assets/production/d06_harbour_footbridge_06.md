# d06_harbour_footbridge.06 — matching railing, edge-light and support family

**Source/export and seven linked component prefabs delivered; independent review and assembled-route
acceptance pending.** Original Blender construction, technical integration and render self-review by
the commissioned isolated production worker. Supervisor approved the provisional component values
below before construction; supervisor/user retain acceptance authority. This is not a completed safe
bridge or approval to place columns in streets.

References: [family brief](../d06_harbour_footbridge.md), [junction](d06_harbour_footbridge_01.md),
[main span](d06_harbour_footbridge_02.md), [south span](d06_harbour_footbridge_03.md),
[quay span](d06_harbour_footbridge_04.md), [access adaptations](d06_harbour_footbridge_05.md),
[commission](commission.md), [art direction](../../art-direction.md),
[Signal Row concept](../../concepts/districts-v1/signal-row.md),
[map context](../../concepts/districts-v1/map-context.md#signal-row-findings),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md) and
[streets](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes the brief's historical concept-only restriction, not pending fit.

## Design and provisional dimensions

Five fitted dark-teal railing/cyan-fascia components match the existing pale junction, shared 12 m span
and main/south/quay stairs. A restrained three-horizontal-member rhythm and square posts keep the
walking routes visually open; no roof, tower, sign or furniture obstructs the approaches. Two matching
pale tapered piers with petrol bearing heads are **separate, unplaced** support components. Geometry
is original Blender construction, not downloaded, purchased, image-to-mesh or runtime-generated.

The supervisor explicitly approved these **provisional component values**, not final map placement,
engineering, accessibility, vehicle clearance, navigation or traversal acceptance:

- Posts **0.10 × 0.10 m**, spaced at most 1.6 m in plan, with **0.12 × 0.12 m** top rails. Posts
  terminate inside the cap rather than duplicating its coplanar top surface. Mid rails are 0.07 m
  square; toe members are 0.10 m wide/high. Small manufactured joints are intentional.
- Nominal guard top **1.20 m above horizontal landings/decks**; **1.38 m above the smooth flight ramp**.
  The latter preserves at least **1.208125 m nominal centreline height above actual tread tops**,
  accounting for .05's 0.171875 m tread/ramp offset. At slope transitions the flight cap sits 0.18 m
  above the adjacent level cap, joined by the end-post rhythm. This is not building-code certification.
- Rail caps/strips have **6 mm, two-segment bevels**; posts/support boxes 8 mm; taper 18 mm. Bevelled
  flight end extrema are 2.342 mm inside the nominal 6.88 m top. Nominal-envelope tolerance **8 mm**;
  source-to-GLB coordinate tolerance **0.00001 m**; engine bounds tolerance **0.001 m**.
- Cyan fascia strip: **0.06 m tall × 0.07 m thick**, centred on the edge line, from 0.15 to 0.09 m below
  the deck/ramp datum. Its inner half intersects the slab; the outer half remains visible. Emission
  is appearance-only; **no light nodes**, illumination radius, navigation cue or gameplay state.
- Guard collision is one **0.12 m-thick continuous prism per exposed edge**, from 0.15 m below the
  local deck/ramp to the nominal guard top. Opposing straight guards leave **3.08 m clear** inside
  the original 3.2 m slab width. It deliberately blocks between visible bars, avoiding actor escapes
  and fine snag geometry. It also blocks physics rays; this is not see-through projectile collision.
- Supports are **5.15 m** tall for the provisional raised slab underside and **2.40 m** for a mid-landing
  underside. Each has a **1.20 × 1.20 × 0.20 m foot**, 0.85 m square/0.15 m collar, shaft tapering from
  **0.65 m to 0.50 m square**, and **2.40 × 0.30 × 0.70 m bearing head**. Shaft starts at Y=0.35 and
  ends 0.30 m below the top. No load capacity or permitted unsupported span distance is claimed.
- Metric units/scale 1; all exported roots/meshes at identity with applied transforms. Blender +Y
  maps to Godot -Z, Blender +Z to +Y. No corrective prefab model scale, offset or rotation.

| Variant | Measured Godot AABB min → max, metres | Dimensions X × Y × Z |
| --- | --- | --- |
| junction | (-3,-0.15,-3) → (3.292633,1.2,3.292632) | 6.292633 × 1.35 × 6.292632 |
| span | (-1.66,-0.15,-12) → (1.66,1.2,0) | 3.32 × 1.35 × 12 |
| main | (-1.66,-0.15,-19.84) → (1.66,6.877658,0) | 3.32 × 7.027658 × 19.84 |
| south | (-1.66,-0.15,-11.58) → (9.92,6.877658,0) | 11.58 × 7.027658 × 11.58 |
| quay | (-9.92,-0.15,-11.58) → (1.66,6.877658,0) | 11.58 × 7.027658 × 11.58 |
| support_tall | (-1.2,0,-0.6) → (1.2,5.15,0.6) | 2.40 × 5.15 × 1.20 |
| support_mid | (-1.2,0,-0.6) → (1.2,2.4,0.6) | 2.40 × 2.40 × 1.20 |

## Attachment and family handoff

Guard roots exactly share their target component's local datum. Junction uses .01's deck-surface
centre; span uses .02–.04's incoming-portal surface centre; access guards use .05's **ground below
incoming upper landing**. Apply the **same placement transform as the corresponding slab prefab**,
not a transform on `Visuals/Model`. No extra public sockets are needed: the existing slabs own the
route interfaces. Supports use ground-centred foot pivots with head long axis along local X.

- `junction`: only cyclic .01 footprint edges **1–2, 2–3, 4–5, 5–6, 7–8, 8–0** are guarded. North,
  SouthEast and West mating planes remain open.
- `span`: both X=±1.6 edges, Z=-12…0. Both end planes remain open. **Reuse this one guard component**
  for .02, .03 and .04; it does not duplicate or own their walking surfaces.
- `main`, `south`, `quay`: match .05's exact upper/flight/mid/apron perimeter. Shared section edges,
  incoming upper mouths, sideways turns and ground mouths are not barred across. Apron side guards
  stop at the ground mouth; no end gate or curb is added.
- For the provisional Y=5.5 junction assembly, guard placements mirror the existing family:
  junction (0,5.5,0); spans at North (0,5.5,-3)/yaw 0°, SouthEast
  (2.121320344,5.5,2.121320344)/yaw -135°, West (-3,5.5,0)/yaw +90°. Access guard roots are main
  (0,0,-15)/yaw 0°, south (10.606601718,0,10.606601718)/yaw -135°, quay (-15,0,0)/yaw +90°.
  These are **component-relative test coordinates**, not approved world placements.
- **No support is attached to that assembly.** World integration must reserve suitable land for the
  whole foot, collar, shaft and bearing envelope; verify roads/vehicle lanes, headroom, foot routes
  and actual slab contact before placing any support. Never assume junction-centre or span-centre
  columns are safe. The western landing stays on land, not across the harbour water; this remains
  distinct from the harbour-mouth road bridge.

## Source, exports and materials

- Source: `art/source/models/environment/d06_harbour_footbridge_06/d06_harbour_footbridge_06.blend`.
- Seven named collections `export_d06_harbour_footbridge_06_<variant>` from the table above. Each has
  root `D06HarbourFootbridge06_<variant>` and one `<root>_Mesh`; no socket, rig or animation.
- Seven GLBs under `art/models/environment/d06_harbour_footbridge_06/`, filenames
  `d06_harbour_footbridge_06_<variant>.glb`, each with its retained `.import` sidecar.
- Tools under `tools/asset_production/d06_harbour_footbridge_06/`: `author.py`, `layout.py`, `export.py`,
  `validate.py`, `write_prefabs.py`, `check_prefab.gd`/`.uid`, `record.py`. `layout.py` is the local
  guard-boundary owner used by the Blender author and prefab collision writer. Source/export tests
  use independently specified envelopes; engine tests use literal edge/mouth/seam expectations.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Export uses unchanged
  `tools/assets/blender/export_settings.json`, filtered by collection, with animations/skins disabled.
  Applied modifiers are saved; glTF triangulates editable source shells. No prototype dependencies.
- Guard surface order: `rail_dark_teal`, `edge_cyan`. Linear RGB (0.025,0.075,0.09) and
  (0.12,0.65,0.72), roughness 0.46 and 0.38; cyan emission strength 0.45. Actual glTF emissive factor
  (0.054,0.2925,0.324). Opaque back-culling Principled materials; no textures or embedded images.
- Support surface order matches .01–.05: `deck_warm_pale`, `deck_pale_fascia`,
  `deck_petrol_underside`; linear RGB (0.72,0.73,0.66), (0.49,0.59,0.59), (0.075,0.16,0.18),
  roughness 0.78/0.56/0.65. No emission, material remaps or real lights.
- Closed post/rail/light/pier shells intentionally meet/intersect at manufactured joints; these are
  not a welded single engineering solid. No open boundary or non-manifold edge is excused.
- Textures, rigs, animation, destruction and explicit LOD are not applicable. Default importer
  automatic LOD/shadow meshes remain; their in-engine visual quality and platform cost are pending.

## Prefabs and deliberate collision

All wrappers instance the matching GLB at **Visuals/Model**, identity transform and noneditable
imported children. No copied render mesh, replacement material or runtime-authored hierarchy.
`Collision/Body` is a layer-1/mask-0 StaticBody3D with direct CollisionShape3D children.

| Variant | Wrapper suffix after `scenes/prefabs/environment/d06_harbour_footbridge_06` | Prefab UID | Model UID |
| --- | --- | --- | --- |
| junction | `.tscn` | `uid://b4jwnu32khnh0` | `uid://caegd4o17k6oe` |
| span | `_span.tscn` | `uid://d23c40rychplo` | `uid://bjtw238f3j0b4` |
| main | `_main.tscn` | `uid://nnsaklc5b8qe` | `uid://qktd7uavsavg` |
| south | `_south.tscn` | `uid://dygm3ohve6wol` | `uid://cqge648xtl23k` |
| quay | `_quay.tscn` | `uid://doht1cmapxnw7` | `uid://bvrri80avp82p` |
| support_tall | `_support_tall.tscn` | `uid://dwoujphvjw3nr` | `uid://bskwy6dksancb` |
| support_mid | `_support_mid.tscn` | `uid://cgavv5uisfbwg` | `uid://c3x1qe3u1hjlu` |

Junction has **6** guard prisms; span **2**; each access **10**. Each is an eight-corner vertical-sided
convex prism with **0.005 m collision margin**, square mating ends and the nominal guard heights.
Pier variants each have **4 simple boxes**: foot, collar, conservative 0.65 m square shaft envelope,
and bearing head. They ignore cosmetic bevels/taper rather than introducing snag facets. No extra
floor, under-stair wall, navigation, ground or automatically generated mesh collider is included.

The common brief prohibits live MCP sessions and says the windowed editor is unavailable. Wrappers
were therefore authored as text, then loaded/packed/saved/reloaded/resaved by the pinned headless
engine. All seven second-save byte comparisons pass. `write_prefabs.py` preserves existing wrappers
and IDs on reauthoring. Headless results do not synchronize a separately open scene. No owner live
session, earlier asset, shared queue/progress/TODO, terrain, road, actor or world scene was modified.

## Evidence and validation

[Hero](d06_harbour_footbridge_06-evidence/hero.png),
[side](d06_harbour_footbridge_06-evidence/side.png),
[guard detail](d06_harbour_footbridge_06-evidence/guard_detail.png), and
[47 m overhead](d06_harbour_footbridge_06-evidence/overhead_47m_42deg.png) are isolated Blender
**Cycles CPU / 32 samples / AgX** renders, inspected by the producer. PNG compression 95, film dither
zero; hero/detail **1120×630**, side/overhead **1280×720**, about 286–419 KiB each. This follows the
common brief's later production-cleanliness maximum rather than its earlier 1280×800 wording.

Hero/overhead show an **exploded component catalogue**, not assembled bridge placement. Existing
.01, .02 and .05 Blender collections are linked for pale-slab render context **only after saving the
owned source and exporting**. No context geometry or library reference enters .06's source/GLBs.
Render-only offsets in Blender XYZ: junction (-19,-4,5.5), span (-12,-6,5.5), main (-5,-4,0),
south (2,-4,0), quay (25,-4,0), tall pier (-19,5,0), mid pier (-15,5,0). The overhead is vertical-down,
north-up, camera (0,5,47), **47 m above flat ground / 42° vertical FOV**. Side isolates the main access;
detail shows the south turn. Piers are visibly detached. They are not placed below roads or landings.

The overhead preserves the pale branching/turning route and open mouths, with quiet dark edges;
cyan reads chiefly along visible fascia, not as a bright competing roof outline. Initial catalogue
overlap/clipped hero framing were corrected, and post tops were lowered inside caps to avoid
coplanar post/cap surfaces. Renders prove neither engine appearance nor world fit.

[validation.json](d06_harbour_footbridge_06-evidence/validation.json) contains measured source/export,
engine, query and canonical-check receipts. [manifest.json](d06_harbour_footbridge_06-evidence/manifest.json)
hashes every produced payload except itself. [final.log](d06_harbour_footbridge_06-evidence/final.log)
is the one concise diagnostic receipt; retries/verbose logs remain in external scratch.

| Variant | Triangles | Blender vertices | GLB vertices including normal/material splits | Meshes / surfaces |
| --- | ---: | ---: | ---: | ---: |
| junction | 4,320 | 2,240 | 3,840 | 1 / 2 |
| span | 2,808 | 1,456 | 2,496 | 1 / 2 |
| main | 8,424 | 4,368 | 7,360 | 1 / 2 |
| south | 8,424 | 4,368 | 7,360 | 1 / 2 |
| quay | 8,424 | 4,368 | 7,360 | 1 / 2 |
| support_tall | 432 | 224 | 384 | 1 / 3 |
| support_mid | 432 | 224 | 384 | 1 / 3 |
| **Unique-export total** | **33,264** | **17,248** | **29,184** | **7 / 16** |

- **Zero degenerate source faces/export triangles, zero non-manifold edges**, positive closed volume,
  finite coordinates, unit source-corner/actual GLB normals. Two imported nodes per export. Actual
  buffer coordinates agree with the source; independent nominal envelopes pass bevel tolerance.
- All **seven saved-source fresh exports are byte-identical** to delivered GLBs.
- Pinned Godot resolves dependencies, linked ancestry, opaque materials/cyan emission, source bounds,
  model identity and registered resource UIDs. Seven wrapper two-save roundtrips are byte-stable.
- **116 physics rays + 25 explicit capsule overlaps = 141 bounded geometry queries** pass. Isolated
  cases cover every exposed edge, open route mouths/turns, flight-transition corners, vertical guard
  limits and support blocking/free space. Capsules use radius 0.35 m/height 1.8 m, not player movement.
- An ephemeral test assembles the actual .01–.05 slabs and fitted guards, without any support instance.
  At **all six junction/span/access seams**, rays on both sides hit guards while centre rays/capsules
  remain clear. This validates the component fit and boundary collision, **not actor traversal**.
- `production_checks.py` passes all layers: **85 GDScripts** formatted/linted/compiled, **11 Python
  tests**, **40 GUT tests / 458 assertions**, diagnostic negative control detected. No pre-existing
  failure exemptions were required. Targeted owned GDScript style/format checks also pass.
- Author, validator, import, normalization and fresh engine query exit 0. Import retains the existing
  MCP 4.8 compatibility warning. Editor-mode normalization has scan-abort/RID/ObjectDB shutdown
  diagnostics, preserved in final.log and **not described as clean**. The fresh non-editor check has
  **no ERROR/WARNING diagnostics**. Blender `use_nodes` deprecation warnings concern future versions.
- Initial owned allocation/line-length lint warnings were fixed. An initial corner test wrongly
  expected an open ray 1 cm from a turning guard: the outgoing side's 6 cm half-thickness correctly
  blocks that corner. The expectation was corrected; independent centre-turn/mouth probes pass.

## Exact reproduction

From this worktree in bash; the production-check output directory must be fresh for another run:

```sh
NID=d06_harbour_footbridge_06
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py already reexports all seven GLBs; independent exporter entrypoint:
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  "art/source/models/environment/$NID/$NID.blend" \
  --python "tools/asset_production/$NID/export.py" -- "$T/manual-reexport"
python "tools/asset_production/$NID/write_prefabs.py"
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

`record.py` refuses failed source, fresh-engine, normalization or canonical receipts before consolidating
and hashing. Reauthoring can change .blend bytes; saved-source GLB identity is the reproducibility gate.

## Remaining acceptance

Independent technical/art review is pending. World integration owns all support sites and contact,
final span lengths, three ground footprints, plaza/poster-drum separation, southern forecourt and Old
Quay fit, unchanged streets/district boundaries, and any displaced placeholders. Keep columns outside
vehicle lanes and reserve their full visual/collision envelope. The approval explicitly forbids
assuming support placement before that fit review.

**Not presently a supported player route.** .05 records production player `FLOATING` mode and
`ActorMotion` without gravity/descending floor-following; the player lane owns that work. Nothing in
this delivery changes it. Actual ascent/descent, foot contact, corner/seam movement, boundary impacts,
under-bridge vehicle headroom and camera/aim occlusion, elevated-route topology/navigation, authority/
prediction and real transports remain untested. In-engine visuals, package/device behavior and
sustained performance remain pending. Component completeness is not full game-ready bridge acceptance.
