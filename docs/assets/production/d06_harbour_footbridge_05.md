# d06_harbour_footbridge.05 — ground-access stair/landing adaptations

**Source/export and three linked component prefabs delivered; independent review and assembled-route
acceptance pending.** Original Blender construction, technical integration and render self-review by
the commissioned isolated production worker. Supervisor approved the provisional access design below
before construction; supervisor/user retain acceptance authority. This is not a completed safe bridge.

References: [family brief](../d06_harbour_footbridge.md), [junction/interface](d06_harbour_footbridge_01.md),
[main span](d06_harbour_footbridge_02.md), [southern span](d06_harbour_footbridge_03.md),
[Old Quay span](d06_harbour_footbridge_04.md), [commission](commission.md),
[art direction](../../art-direction.md), [Signal Row concept](../../concepts/districts-v1/signal-row.md),
[map context](../../concepts/districts-v1/map-context.md#signal-row-findings),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md), and
[streets](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes the historical concept-only restriction, not the pending map fit.

## Design and provisional dimensions

Three adaptations share one thin, pale two-flight stair language: **main straight**, **south quarter-turn
right**, **quay quarter-turn left**, viewed while descending away from the incoming span. Broad square
upper/middle landings make the changes in direction visible from above. No roof, tower, artwork or
obstacle obscures the route. Quiet warm-pale tops, cool-pale fascia and petrol undersides match .01–.04.
Tread/long edges receive an **8 mm, two-segment bevel**; mating planes remain square. The smaller stair
bevel preserves the tread rhythm rather than applying the larger span bevel to shallow rises.

The supervisor explicitly approved these **provisional component values**, not engineering, accessible
access, world footprint, vehicle clearance, navigation or traversal acceptance:

- Width **3.2 m** throughout; each flight descends **2.75 m over 5.12 m** in plan.
- Each flight has **16 rises of 0.171875 m** and **0.32 m treads**; two flights connect Y=5.5 to Y=0.
- Upper and mid landings and ground apron are **3.2 × 3.2 m**, with **0.35 m slab depth**.
- Ground apron walking face is **Y=0**; its approved thin foundation extends to **Y=-0.35**. The source
  pivot is **ground below the incoming upper-landing centre**, not the apron centre or visual AABB centre.
- Upper incoming socket is **(0,5.5,0)**. Local descent begins along **Godot -Z**; Blender +Y maps to -Z,
  Blender +Z to +Y. Root/mesh transforms are identity with metre units and applied scale/rotation.
- Continuous collision flight slope measures **28.24066°**, below the production player resource's
  **45° `floor_max_angle`**. This comparison does not establish movement support; see collision below.
- Source/GLB tolerance **0.00001 m**; engine bound/socket/top tolerance **0.001 m**. Seam samples 1 cm
  from slope transitions allow **0.007 m** vertical difference from the nominal landing height.

| Variant | Godot AABB min → max, metres | Dimensions X × Y × Z |
| --- | --- | --- |
| main | (-1.6,-0.35,-19.84) → (1.6,5.5,0) | 3.2 × 5.85 × 19.84 |
| south | (-1.6,-0.35,-11.52) → (9.92,5.5,0) | 11.52 × 5.85 × 11.52 |
| quay | (-9.92,-0.35,-11.52) → (1.6,5.5,0) | 11.52 × 5.85 × 11.52 |

## Snapping and .06 perimeter handoff

Public `Sockets/Incoming` and `Sockets/Ground` exactly relay the exported empties
`socket_incoming_<variant>` and `socket_ground_<variant>`. Socket local **-Z is outward**, +Y up;
no independently tuned offset or corrective imported-model rotation is used.

| Variant/socket | Local Godot position | Outward direction | Godot yaw |
| --- | --- | --- | --- |
| all / Incoming | (0,5.5,0) | (0,0,+1) | 180° |
| main / Ground | (0,0,-19.84) | (0,0,-1) | 0° |
| south / Ground | (9.92,0,-9.92) | (+1,0,0) | -90° |
| quay / Ground | (-9.92,0,-9.92) | (-1,0,0) | +90° |

With the junction surface at Y=5.5 and ground at Y=0, relative component placement is:
main origin **(0,0,-15), yaw 0°**; south origin **(10.606601718,0,10.606601718), yaw -135°**;
quay origin **(-15,0,0), yaw +90°**. These match the existing span outgoing interfaces and keep the
aprons on the same flat ground datum. They are assembly coordinates, **not approved world placements**.
For arbitrary placement, align the incoming marker with its span's outgoing marker with opposed
outward axes; account for the access marker's 5.5 m local elevation rather than raising the entire
access root by another 5.5 m. Do not scale or modify the imported `Visuals/Model`.

The following local plan rectangles and heights give .06 the exact exposed boundary owner. Rails,
edge-light geometry, **edge-blocking collision**, supports and column footprints remain exclusively
**.06-owned**. Shared rectangle boundaries and both route mouths must remain clear, not railed across.

| Section | X range | Z range | Walking elevation |
| --- | --- | --- | --- |
| Upper, all | -1.6…1.6 | -3.2…0 | 5.5 |
| Flight1, all | -1.6…1.6 | -8.32…-3.2 | 5.5 down to 2.75 toward -Z |
| Mid, all | -1.6…1.6 | -11.52…-8.32 | 2.75 |
| Flight2, main | -1.6…1.6 | -16.64…-11.52 | 2.75 down to 0 toward -Z |
| Apron, main | -1.6…1.6 | -19.84…-16.64 | 0 |
| Flight2, south | 1.6…6.72 | -11.52…-8.32 | 2.75 down to 0 toward +X |
| Apron, south | 6.72…9.92 | -11.52…-8.32 | 0 |
| Flight2, quay | -6.72…-1.6 | -11.52…-8.32 | 2.75 down to 0 toward -X |
| Apron, quay | -9.92…-6.72 | -11.52…-8.32 | 0 |

Each stair profile starts with a tread at the upper elevation; subsequent risers descend after every
0.32 m run, including the final rise down to the lower landing. The smooth collision plane is up to
**0.171875 m below** the visible treads. .06 must consider actual tread tops when choosing guard height;
this record does not invent its rail-height/support specification. The apron end is the ground-route
mouth, not a vertical curb. World integration must avoid duplicate coplanar ground collision beneath
that apron and reserve the whole descending footprint on land, outside vehicle lanes.

## Source, exports and materials

- Source: `art/source/models/environment/d06_harbour_footbridge_05/d06_harbour_footbridge_05.blend`.
  Three collections `export_d06_harbour_footbridge_05_<main|south|quay>` each contain root
  `D06HarbourFootbridge05_<variant>`, one `<root>_Mesh` and two named socket empties.
- Three explicit GLBs: `art/models/environment/d06_harbour_footbridge_05/` with filenames
  `d06_harbour_footbridge_05_main.glb`, `_south.glb`, `_quay.glb`, each with retained `.import` metadata.
  No prototype references, downloaded geometry, image-to-mesh, embedded textures or runtime meshes.
- Each mesh contains five closed source shells (three landings/two flights). Adjacent shells share
  exact mating planes; their internal caps are retained. There are no open boundaries/non-manifold
  edges. This is a deliberate small static assembly, not a welded single engineering solid.
- Tools: `tools/asset_production/d06_harbour_footbridge_05/{author,export,validate}.py`,
  `write_prefabs.py`, `check_prefab.gd` plus its UID, and `record.py`. Existing shared export settings
  and production checks are reused without modifications; no new shared framework was introduced.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Named-collection export uses
  `tools/assets/blender/export_settings.json`, with static animations/skins disabled. Applied static
  modifiers are saved; glTF triangulates the editable source.
- Material slot order: `deck_warm_pale`, `deck_pale_fascia`, `deck_petrol_underside`; linear RGB
  (0.72,0.73,0.66), (0.49,0.59,0.59), (0.075,0.16,0.18); roughness 0.78/0.56/0.65. Opaque, back-culling,
  texture-free Principled surfaces match .01–.04. No emission or Godot material remaps.
- Rig, animations, destruction states, textures and explicit LOD are not applicable. Default automatic
  importer LOD/shadow meshes are retained; their device/rendering quality and cost remain unaccepted.

## Prefabs and collision

All three wrappers use **Visuals/Model = identity-transform linked GLB instance**, with noneditable
imported children. No embedded render geometry or runtime-authored hierarchy exists.

| Variant | Prefab under `scenes/prefabs/environment/` | Prefab UID | Model UID |
| --- | --- | --- | --- |
| main | `d06_harbour_footbridge_05.tscn` | `uid://dcgvj3jp5tviw` | `uid://dr0gjsln27dgo` |
| south | `d06_harbour_footbridge_05_south.tscn` | `uid://li5fojsleqhl` | `uid://bidwr3287t2yu` |
| quay | `d06_harbour_footbridge_05_quay.tscn` | `uid://byk7ryicjls71` | `uid://bhbm8ilji2tdv` |

Each `Collision/Body` is static-world layer 1 / mask 0. Its five direct `CollisionShape3D` children are
`Upper`, `Flight1`, `Mid`, `Flight2`, `Apron`. Landings use **3.2 × 0.35 × 3.2 m boxes**; each flight
uses **one eight-corner convex ramp prism**, with underside 0.35 m vertically below its slope plane.
Cosmetic bevels and individual risers are deliberately excluded to avoid step snagging. No rail,
column, under-stair wall, background ground or navigation collider is silently added.

**Not presently a supported player route.** Inspection of the actual production `player.tscn` shows
`motion_mode = FLOATING`, while `ActorMotion.step` assigns Y velocity zero and does not supply gravity
or descending floor-following. The supervisor confirmed the player lane owns gravity/floor-snap work.
This asset does not change those rules. Passing slope/physics-ray checks cannot establish ascent,
descent, foot contact, corner turning, floor attachment, authority/replay or navigation. The tread/ramp
visual offset also requires movement/presentation review. Unguarded stairs must not be placed as safe
bridge gameplay until .06 and assembled traversal checks pass.

The commission prohibits live MCP sessions and says the windowed editor is unavailable. Wrappers were
therefore authored as text and loaded/packed/saved/reloaded/resaved using the pinned headless engine.
Second-save bytes are stable. `write_prefabs.py` creates missing wrappers only, preserving existing IDs
on reauthoring. Headless validation does not synchronize a separately open editor scene; no owner's
live session was accessed.

## Evidence and validation

[Hero](d06_harbour_footbridge_05-evidence/hero.png), [side](d06_harbour_footbridge_05-evidence/side.png),
[landing detail](d06_harbour_footbridge_05-evidence/landing_detail.png), and
[47 m overhead](d06_harbour_footbridge_05-evidence/overhead_47m_42deg.png) were inspected by the producer.
All are isolated **Blender Cycles CPU / 32 samples / AgX, 1280×720**, PNG compression 95, film dithering
disabled for lean lossless PNGs (248–364 KiB). The 720-pixel height follows the common brief's later
production-cleanliness limit rather than the earlier 800-pixel request. No lossy palette conversion is
used. Overhead is vertical-down/north-up, **47 m above ground and 42° vertical FOV**. Main/south/quay
are shown left-to-right with render-only X offsets -18/-9/+16 m; this comparison is not world placement.
Hero shows the same set from the opposite side; side isolates main, detail isolates south's turn.

The overhead clearly distinguishes the straight/two turning routes and tread rhythm, with broad
landings free of clutter. Initial hero framing hid the first flights behind their sides, so the final
camera faces the descending treads; the initial side-view studio horizon was removed. Cyan edges,
rails and supports remain .06's contribution. Renders prove neither map fit nor engine readability.

[validation.json](d06_harbour_footbridge_05-evidence/validation.json) holds source/export and engine
measurements; [manifest.json](d06_harbour_footbridge_05-evidence/manifest.json) hashes every produced
payload except itself. [final.log](d06_harbour_footbridge_05-evidence/final.log) is the one concise
receipt; raw logs/retries remain in external scratch.

- **Per variant: 1,908 triangles, 964 source vertices, 1,728 exported vertices including normal/material
  splits, one mesh, three surfaces, four imported nodes.** All three together: 5,724 triangles.
- **Zero degenerate source faces/export triangles, zero non-manifold edges**, positive closed volume,
  finite coordinates, unit source-corner and actual GLB normals. All **33 broad horizontal elevations**
  from 0 to 5.5 m are measured, proving the 32 rises. Actual source mating widths/depths and exported
  bounds match independent expectations.
- Fresh reexport of each saved collection is **byte-identical** to its delivered GLB.
- Pinned engine dependencies, imported ancestry, three materials, AABBs, model identity, full socket
  mappings and resource UIDs pass; all three wrappers pass byte-stable two-save roundtrips.
- **17 isolated top rays per variant** measure five walking regions (including both 28.24066° slopes),
  four independent footprint voids and eight landing-transition samples. **Six upper-seam rays per
  variant** straddle actual .02/.03/.04 span connections at lateral offsets -1.5/0/+1.5 m. Total **69
  bounded geometry queries** pass. This is not actor, vehicle, guardrail or complete assembly movement.
- `production_checks.py` passes all layers: **84 GDScripts** formatted/linted/compiled, **11 Python
  tests**, **40 GUT tests / 458 assertions**, and diagnostic negative control detected. No known-failure
  exemptions were required. These existing tests do not certify bridge traversal.
- Final author, validator, import, normalization and fresh engine query exit 0. Blender's `use_nodes`
  deprecation warnings concern future versions; the pinned tool succeeds. Import retains the existing
  MCP 4.8 compatibility warning. Editor-mode normalization has RID/ObjectDB shutdown leaks, recorded
  in final.log; the fresh non-editor query has **no ERROR/WARNING diagnostics**.
- Initial headless checks caught reversed quarter-turn public marker bases; corrected in the saved
  wrappers and reproduction recipe before the final full-transform checks. Initial owned lint warnings
  were resolved by separating small check helpers. An initial validator-writing shell command failed
  before writing a file; the final validator and all saved geometry checks pass.

## Exact reproduction

From the worktree in bash; choose a fresh production-check output directory for subsequent runs:

```sh
NID=d06_harbour_footbridge_05
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py reexports all three GLBs; this invokes the independent export entrypoint:
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

`record.py` refuses failed source, fresh-engine, normalization or canonical-check receipts before
consolidating and hashing. Reauthoring can change .blend bytes; saved-source GLB identity is the gate.
The collection roots remain unplaced at origin in the source; select one collection for isolated work.

## Remaining acceptance

Independent technical/art review is pending. .06 must provide guards, restrained cyan edge lights and
support family with safe footprints; no columns may be assumed safe in road lanes. World integration
owns the final three ground landing footprints, plaza/poster-drum separation, shopping forecourt fit,
unchanged roads and district boundaries, and identification of displaced Old Quay placeholders. Keep
the west end **on land**, distinct from the harbour-mouth road bridge. No terrain, world scene, road
tool, actor, shared queue/progress/TODO or earlier family asset was modified.

Production ascent/descent, foot contact, turns/seams, railing collision, vehicle headroom around all
supports/accesses, under-bridge camera/aim occlusion, elevated-route navigation/topology, authority/
prediction, real transports, in-engine visuals, package/device and sustained performance remain pending.
This component set does not claim complete three-destination route support or full game-ready acceptance.
