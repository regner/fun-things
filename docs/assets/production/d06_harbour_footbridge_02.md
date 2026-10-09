# d06_harbour_footbridge.02 — main-area connecting span

**Source/export and linked component prefab delivered; independent review and assembled-route
acceptance pending.** Original Blender construction, integration and visual self-review by the
commissioned isolated production worker. The supervisor approved the provisional 12 m design before
construction; the supervisor/user remain acceptance authorities. This is one component of the
three-destination pedestrian connection, not a completed bridge or a new road/water crossing.

References: [family brief](../d06_harbour_footbridge.md), [junction and family interface](d06_harbour_footbridge_01.md),
[commission](commission.md), [art direction](../../art-direction.md),
[Signal Row concept](../../concepts/districts-v1/signal-row.md),
[map context](../../concepts/districts-v1/map-context.md#signal-row-findings),
[district identities](../../concepts/world-v1/stage-03-district-identities/README.md),
[street context](../../concepts/world-v1/stage-04-streets/README.md).
The production commission supersedes the family brief's historical concept-only restriction.

## Design and provisional dimensions

One straight, thin pale span continues the northern junction portal toward Signal Row's main area.
Broad quiet walking surface, cool pale fascia and petrol underside exactly retain .01's three
materials. Only the exposed long edges receive a **25 mm, three-segment bevel**. Both mating end
planes stay square and flush; sharp edge normals prevent a rounded-over portal appearance.
No roof, tower, ornament, surface marking or obstacle is added. Railings, cyan edge lights and supports
remain **.06-owned**, and access stairs/ground landings remain **.05-owned**.

The live supervisor explicitly approved these **provisional component values**, not final world fit,
engineering, navigation or traversal acceptance:

- **3.2 m wide × 0.35 m deep × 12 m long**, Godot X × Y × Z dimensions.
- Godot AABB min **(-1.6, -0.35, -12)**, max **(1.6, 0, 0)** m.
- Pivot **incoming portal surface centre (0,0,0)**, deliberately not ground-contact centre or slab
  centre. The span runs along Godot **-Z**, from Z=0 to Z=-12. Blender +Y maps to Godot -Z; +Z to +Y.
- Walking surface **Y=0**, underside **Y=-0.35**. Intended placed surface height **5.5 m** reserves
  **5.15 m slab-only underside height** above flat ground, not a certified road/vehicle clearance.
- Root and mesh transforms are identity; metric units/scale 1 and applied static transforms.
- Source/GLB dimensional tolerance **0.00001 m**; engine envelope/socket/query tolerance **0.001 m**.
- The supervisor requested .03/.04 retain the same incoming/outgoing interface and provisional 12 m
  length unless their brief clearly requires otherwise. Final lengths and landing footprints remain
  a world-fit decision. Chaining this component does not establish safe support spacing.

## Snapping and family handoff

Public markers exactly relay exported Blender empties. Socket local **-Z points outward**, +Y up.
The incoming socket faces back toward the junction; outgoing faces along the span. Do not rotate the
span to make both sockets face the same way, or introduce a hidden root scale/offset.

| Public marker | Source empty | Godot position | Outward direction | Godot yaw |
| --- | --- | --- | --- | --- |
| `Sockets/Incoming` | `socket_incoming` | (0,0,0) | (0,0,+1) | 180° |
| `Sockets/Outgoing` | `socket_outgoing` | (0,0,-12) | (0,0,-1) | 0° |

Place this prefab at **(0,0,-3)** relative to the .01 junction with identity rotation. Its incoming
plane then coincides with `.01/Sockets/North`, outward axes opposed; outgoing is **(0,0,-15)** in
junction coordinates. Both surfaces share the junction datum. Repeated spans translate another 12 m
along local -Z; neither imported hierarchy nor material assignment needs overrides.

For .06: the exposed long edge lines are **X=-1.6 and X=+1.6**, Z from -12 to 0, walking datum Y=0.
The short end faces are open connections, not railing edges. Nominal slab/collision corners are
(-1.6,0,0), (1.6,0,0), (1.6,0,-12), (-1.6,0,-12), with underside 0.35 m lower. Preserve the portal
mouths and avoid collision snag points at seams. .06 owns edge-blocking collision and support
placement; no column location is approved here, particularly not within vehicle lanes.

## Source, export and materials

- Source: `art/source/models/environment/d06_harbour_footbridge_02/d06_harbour_footbridge_02.blend`.
- Named collection `export_d06_harbour_footbridge_02`; root `D06HarbourFootbridge02`, mesh
  `D06HarbourFootbridge02_Mesh`, and the two socket empties. Studio ground, lights and camera are
  excluded. Geometry is original Blender construction, not downloaded, image-to-mesh or runtime-built.
- Export: `art/models/environment/d06_harbour_footbridge_02/d06_harbour_footbridge_02.glb` plus its
  preserved `.import` sidecar. No prototype dependencies, textures or embedded images.
- Reproducible scripts: `tools/asset_production/d06_harbour_footbridge_02/{author,export,validate}.py`.
  They follow .01's construction/check conventions and the existing shared export settings, without
  modifying .01 or introducing a new shared tool owner.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Export uses
  `tools/assets/blender/export_settings.json`, filtered to the named collection, with animations and
  skins disabled. Static modifiers are applied before save; glTF triangulates source faces.
- Material slot order: `deck_warm_pale`, `deck_pale_fascia`, `deck_petrol_underside`. Linear RGB
  (0.72,0.73,0.66), (0.49,0.59,0.59), (0.075,0.16,0.18); roughness 0.78, 0.56, 0.65 respectively.
  Texture-free opaque back-culling Principled materials match .01; no emission or Godot remaps.
- Rig, animations, destruction, textures and explicit LOD are not applicable. Default automatic
  importer LOD/shadow-mesh settings remain; no platform cost budget is claimed.

## Prefab and collision

`scenes/prefabs/environment/d06_harbour_footbridge_02.tscn` instances the GLB at **Visuals/Model**,
identity transform with noneditable imported children. No copied render mesh or runtime hierarchy.
Prefab UID **uid://c70pnp44flogm**; model UID **uid://br6gwt3gijy1y**.

`Collision/Body` is a static-world layer-1/mask-0 StaticBody3D. Its sole child `Slab` is a
**BoxShape3D (3.2,0.35,12)** centred at **(0,-0.175,-6)**. This deliberate slab envelope ignores the
25 mm cosmetic bevel, avoiding tiny collision facets; it does not add rail, support, stair or ground
collision. **The unguarded component is not a standalone safe traversable route.** Do not publish it
as completed bridge gameplay before the remaining family, guardrails and downstream checks pass.

The common brief forbids live MCP/editor sessions and states the windowed editor is unavailable.
The wrapper was therefore authored as text, then loaded/packed/saved/reloaded/resaved by the pinned
headless engine. Its second save was byte-identical. This is saved-resource validation, not proof
that a separately open editor is synchronized. No live owner session was accessed.

## Evidence and validation

[Hero](d06_harbour_footbridge_02-evidence/hero.png),
[side](d06_harbour_footbridge_02-evidence/side.png),
[incoming portal detail](d06_harbour_footbridge_02-evidence/portal_detail.png),
[47 m overhead](d06_harbour_footbridge_02-evidence/overhead_47m_42deg.png).
All four **1280×800 Blender Cycles CPU / 32 samples / AgX** renders were inspected by the producer
and compared with .01. Thin pale slab, square end faces and restrained long-edge bevel are consistent.
The vertical-down north-up overhead uses **47 m above ground / 42° vertical FOV**, with the span
rendered at the provisional 5.5 m elevation. Its quiet straight route reads clearly without rooftop
obstruction. Rails/cyan accents will be supplied by .06 rather than duplicated here.
Hero/side/detail use a studio floor immediately below the slab, not a placed bridge. Render-only
elevation is not saved to source/export. These are not engine screenshots or route acceptance.

[validation.json](d06_harbour_footbridge_02-evidence/validation.json) records measurements, actual GLB
metadata and engine results; [manifest.json](d06_harbour_footbridge_02-evidence/manifest.json) hashes all
produced payloads except the manifest itself. [final.log](d06_harbour_footbridge_02-evidence/final.log)
retains concise results and classified diagnostics; raw logs remain outside the repository.

- **60 triangles, 32 source vertices, 72 exported vertices including surface/normal splits;
  one mesh, three surfaces, four imported nodes** (root, mesh, two empties).
- **Zero degenerate source faces/export triangles, zero non-manifold edges**, positive closed
  volume, finite exported coordinates, unit-length source corner and actual GLB normals.
- Source and actual GLB AABBs agree; both mating planes measure 3.2 m wide and 0.35 m deep from
  source vertices. Fresh export from saved source is **byte-identical** to the delivered GLB.
- Pinned Godot dependencies, linked ancestry, identity model transform, surfaces, AABB, socket full
  transforms and registered UIDs pass. Save/reload/resave is byte-stable.
- **Nine** independent isolated top-ray solid/void cases pass at centre, both portals, inside/outside
  both sides and beyond each end. Upward ray measures underside **5.149999619 m** after test-only
  elevation; horizontal ray at 5 m passes beneath it without an accidental support collider.
- Actual .01/.02 prefab mating passes: incoming coincident/opposed to North, outgoing at (0,5.5,-15).
  **Six** top rays at X=-1.5/0/+1.5 and Z=-3.01/-2.99 hit the appropriate component at Y=5.5 on
  either side of the junction seam. These are bounded geometry queries, **not actor movement**.
- Final `production_checks.py` passes all layers: **81 GDScripts** formatted/linted/compiled,
  **11 Python tests**, **40 GUT tests / 458 assertions**, and diagnostic negative control detected.
  No pre-existing failure exemptions were needed. Initial owned max-local-variable lint warning
  was corrected before the canonical run.
- Author, source validator, import, normalization and fresh engine checks exit 0. Import retains the
  existing MCP pin compatibility warning. Editor-mode custom-tree normalization has RID/ObjectDB
  shutdown leak diagnostics, recorded in final.log, not described as clean. The subsequent fresh
  non-editor load/query has **no ERROR/WARNING diagnostics**.

## Exact reproduction

From this worktree in bash; use a fresh output directory for another production-check run:

```sh
NID=d06_harbour_footbridge_02
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py already reexports; this independently invokes the same exporter entrypoint:
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
Reauthoring may change .blend bytes; deterministic saved-source GLB reexport is the acceptance gate.

## Remaining acceptance

Independent technical/art review is pending. World integration owns final span lengths, supports on
suitable ground, three landings, plaza/poster-drum separation, unchanged roads/district boundaries and
any displaced Old Quay placeholders. The western connection stays on land and remains distinct from
the harbour-mouth road bridge. No world scene or shared queue/progress/TODO record was changed.

Assembled actor/car movement, seam crossing, guardrail collision, under-bridge camera/aim occlusion,
elevated-route navigation/topology, authority/prediction, real transport behavior and in-engine visuals
remain untested for this bridge. Packaged/device behavior and sustained performance also remain
pending. This component does not claim full gameplay support for elevated routes or complete visual
traceability to all three ground-level destinations; .03–.06 and assembled placement are still needed.
