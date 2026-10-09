# car_latch_a — first car production checkpoint

9 October 2026. Producer: vehicle lead Codex. Concept owner: Regner, who approved
all three car directions. Original geometry/materials; no external vehicle assets.
The initial source pass preceded the routing change; hinged-door/spatial refinement
used verified Astra/high. See the [routing receipt](../concepts/assets-v1/vehicle/handoff.md).
Status: **reviewable source/import/preview checkpoint; final production art pending**.

## Brief and sources

Latch compact, based on the [approved concept](../concepts/assets-v1/vehicle/01_latch_compact.png).
Smooth chunky original city vehicle, unbranded. Actual closed visual size is
1.8930 m wide × 1.5400 m high × 3.4320 m long.
Provisional visual sizing includes tire/hub/light overhang and is not a collider.
Origin is ground-centred; Godot +Y up/-Z forward, Blender +Z up/+Y forward.
Root transforms are unit scale, identity rotation. Imported/source AABB agreement
is checked within 0.002 m; approved concept proportions were illustrative, not measured.

| Source / collection | Export and import | Saved consumers |
| --- | --- | --- |
| `art/source/models/city_cars/car_latch_a.blend` / `export_car_latch_a` | `art/models/city_cars/car_latch_a.glb` + `.glb.import` | `scenes/prefabs/city_cars/car_latch_a.tscn`; `scenes/previews/city_cars/car_latch_a_preview.tscn` |

The wrapper has `Visuals/Model` as a linked GLB instance, with the imported named
asset root below it; no editable imported-child overrides or embedded draw meshes.
No physics/controller/Health/seat gameplay is supplied. An integrator mounts the
visual wrapper beneath its own `PresentationAnchor`; the proposed production
vehicle entity contract is not replaced by this visual wrapper.

Blender 5.2.2 LTS `d13f752e3b9c`, glTF settings inherited explicitly from
`tools/s01/export_settings.json`, with skins/animations disabled for these rigid
source parts. Export includes only the named collection: applied bevels, normals,
triangulation and glTF Y-up conversion. The non-export metre reference stays in
Blender. `tools/vehicle_assets/reexport.py` reads the saved sources without rebuilding
geometry. Four-source byte-identical scratch reexport passes, including preview floor.

Godot 4.8-dev7 `c971f93e7`, default per-asset import with generated LODs; no global
project settings changed. Resource UIDs and editor node identities are saved in the
wrapper/preview/import sidecars. Six scenes pass a stable save/reopen roundtrip.
No inherited variant is introduced, so inherited-override validation is not applicable.

## Rigid parts, sockets and clips

Four source-authored axle centres under `Visuals/Model/car_latch_a/Wheels`:
`SteerFrontLeft`, `SteerFrontRight`, `SteerRearLeft`, `SteerRearRight`, each with its
corresponding `Spin…` child. Wheel spin uses local X; steering uses Godot Y.
There are 2 rigid door hinges under `Visuals/Model/car_latch_a/Doors`:
`HingeFrontLeft`, `HingeFrontRight`.
Each hinge owns its panel/window/handle and front-door mirror. No skin or armature
is required. Simple interior floor/seats/dashboard support the opening-door view;
no detailed interior, working handles, rear hatch/trunk or passenger animation is claimed.

The saved preview's `AnimationPlayer` has `RESET` and a looping six-second
`mechanical_demo`: rigid wheel spin/front steering and side doors opening to50°
then closing. It changes visual descendants only. This is cosmetic preview playback,
not a production per-door controller/clip API or entry/exit/network acceptance.
Animation keys are saved in the Godot preview, not hidden in runtime mesh generation.
Final per-door interaction playback requirements belong to the integrator handoff.

| Source marker → wrapper socket | Godot position metres |
| --- | --- |
| `socket_driver` → `Sockets/DriverSeat` | [-0.34, 0.86, -0.12] |
| `socket_entry_left` → `Sockets/EntryLeft` | [-1.3399999999999999, 0, -0.1] |
| `socket_entry_right` → `Sockets/EntryRight` | [1.3399999999999999, 0, -0.1] |
| `socket_exit_left` → `Sockets/ExitLeft` | [-1.56, 0, -0.1] |
| `socket_exit_right` → `Sockets/ExitRight` | [1.56, 0, -0.1] |

Source markers live under the imported `Markers` node. Saved wrapper markers are
copied from source transforms and checked for equality, not independently hand-tuned.
Driver/entry/exit poses are provisional candidates. Open doors widen visual bounds;
these candidates are not proof of actor fit or safe clearance. Gameplay queries must
use authoritative physics pose, not smoothed presentation. Final driver fit awaits
the player's versioned production dimensions/seat contract.

## Materials, bounds and validation

Eight source-owned opaque flat materials: body_paint, hood_inset, glass, tire, trim,
wheel_hub, headlamp, tail_lamp. Each mesh uses its source-assigned slot; the GLB owns
these materials and lamps use restrained emission. No textures, external material
remaps or texture-channel/UV-bake workflow is needed at this checkpoint. Glass is
opaque stylized glazing. No shared material writer or external texture dependency.

Source has 10104 triangles after applied authoring operations; no triangle
or sustained-device budget is ratified. Generated import LOD appearance and crowd
performance remain unmeasured.

[Inspection](vehicle_car_evidence/car_latch_a_inspection.png) ·
[Actual game camera](vehicle_car_evidence/car_latch_a_game.png) ·
[Doors open](vehicle_car_evidence/car_latch_a_doors.png).
Captures use Linux NVIDIA GTX1070 OpenGL Compatibility,1280×800,60FPS cap/VSync;
GameCamera at(0,47,0), vertical down/north-up,FOV42°, near0.1/far160. A separate saved
inspection camera supplies the close view. Captures prove drawn appearance and
sampled rigid poses, not performance or gameplay. JSON alongside each PNG records
camera, renderer, actual dimensions,50° hinge checks, fixed root and open/rest bounds.

[Source record](vehicle_car_evidence/car_latch_a_source.json),
[import checks](vehicle_car_evidence/import_checks.json),
[reexport fingerprints](vehicle_car_evidence/reexport.json),
[save/reopen receipt](vehicle_car_evidence/roundtrip.json).

## Acceptance and unfinished checks

- Concept: accepted by Regner. Source/export/import/preview: checks above passed;
  independent Sol 6.1/high [review](vehicle_car_evidence/independent_review_69219f0.md)
  accepted candidate `69219f0` within the first-checkpoint scope, with no scoped defects.
- Full-loop rendered playback and intermediate moving-part clearance: pending;
  current captures sample rest and 2.5-second open poses.
- Production art: pending. Current forms are simplified first-pass models; roundness,
  glazing/body joins, door-edge shading, wheels and closer silhouette fidelity need
  further art review/polish against the approved sheets. See the scoped
  [next art pass](vehicle_car_evidence/next_art_pass.md). No final owner model approval.
- Collision, driver fit, grounded exits, turns, spawn queries, gameplay/networking,
  damage/wreck states and world placement: external integrator, not performed here.
- Forward+/target-device appearance and sustained Deck performance: pending. These
  captures use a bounded Compatibility preview; they do not certify the main renderer.
- No physics body, collision layer, main launch, shared TODO/catalogue or world file
  was changed. Bus/truck concept approval remains independently pending.
