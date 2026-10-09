# s04_kit — bounded technical source handoff

New spike-only car and track, created by the S04 direct Sol6.1 HIGH lead on8 October
2026. Review stage: exact `2370ad1c182b46e51f5dc4c6b6ab6157819e84b0`
independently ACCEPTED for bounded technical use; original P2/P3 CLOSED. See
[exact-final acceptance and durable note](../spikes/s04.md#accepted-exact-final-disposition)
and [full original REQUEST CHANGES](../reviews/s04-10874476.md). Production art, feel,
body/controls/dimensions/turning/prediction, camera/readability, physical keys/focus,
Steam/Deck and full S04/P0/M1/production acceptance remain OPEN. Brief and criteria:
[S04](../spikes/s04.md), [body/seat contract](../spikes/s04-contracts.md), accepted
[Petrol & Coral direction](../art-direction.md) and [six-block scope](../world-layout.md).
Original geometry/materials created in Blender; no external model/image/library or
new license dependency. Source/integration owner is S04; Regner owns product feel.

## Source, explicit outputs and consumers

| Source / explicit collection | Linked export and preserved sidecar | Saved consumers |
| --- | --- | --- |
| `prototypes/s04/art/source/models/spikes/s04_kit.blend` / `export_s04_car` | `prototypes/s04/art/models/spikes/s04_car.glb` + `.glb.import` | `prototypes/s04/tests/fixtures/s04/kinematic.tscn`, `dynamic.tscn`; their instances in `body_comparison.tscn`, inherited `boot.tscn`; S05 `car.tscn` inherited by S05 boot/burst instances |
| Same source / `export_s04_track` | `prototypes/s04/art/models/spikes/s04_track.glb` + `.glb.import` | `prototypes/s04/tests/fixtures/s04/track.tscn`; comparison/boot instances; S05 boot CityRoot/Track, inherited by S05 burst |

All source members are explicit in `prototypes/s04/tools/s04/export_members.json`; `export.py`
validates those exact members and unit transforms. The committed .blend is the
editable source; bootstrap `create_sources.py` refuses overwrite. Source and both
outputs must change together. Reverse consumers verified in saved scenes/editor.
`editor_harness.tscn` is editor-only inspection; runtime runners exclude editor
harnesses from their addon-free mirrors. S03 boot inheritance and S02 input class
reuse preserve originals. No S02 art is drawn by S04, although class dependency
mirrors contain its accepted assets. No world-sector/nav/minimap/occluder integration.

Blender5.2.2 LTS `d13f752e3b9c`, glTF exporter5.2.40; metre units, +Y Godot up/-Z
forward, applied source transforms, bevels/triangulation, GLB/Y-up/modifiers/normals,
embedded flat materials, no textures/rig/skin/clips/animations or external resources.
Godot pin4.8.dev7.official.c971f93e7; original renderer/Jolt/project settings unchanged.
New default imports retain unit scale/materials and linked GLB mesh resources;
no detached/embedded project-owned draw meshes or imported-child appearance overrides.
Byte-identical reexport of both outputs passed; the optional missing MeshOptimizer
library diagnostic is retained explicitly. Source `.gdignore` prevents Blender import.

## Measured technical geometry

Editor-imported bounds: car X1.88/Y1.54/Z3.4 m, bottomY0, source/model root at ground
centre, no prefab corrective scale/rotation. Body collision is an upright1.8×1.5×3.4 m
box centredY0.75; decorative tires extend0.04 m each side and roof0.04 m above it.
The flat fixture's deliberate overhang is not district/exit clearance acceptance.
Pad80×80 m, topY0; visible walls and separately saved solid boxes match placement.
No floor collider/gravity is used: both candidates are constrained to the plane;
rigid translationY/rotationX,Z locked. Track layer1, car layer4/mask5; replicas zero.
These are measured fixture facts, not settled M1 dimensions or handling.

| Source marker → prefab socket | Local position metres (zero rotation) | Purpose |
| --- | --- | --- |
| `socket_driver` → `Sockets/DriverSeat` | (0,0.8,0.1) | Future occupant attachment candidate |
| `socket_entry_left/right` → `Sockets/EntryLeft/Right` | (±1.3,0,0.1) | Future entry candidate |
| `socket_exit_left/right` → `Sockets/ExitLeft/Right` | (±1.5,0,0.1) | Future clearance candidates; no exit tests claimed |

Sockets copied through the editor from source markers onto stable wrapper markers;
imported children remain linked. Physics queries will use root-relative sockets.
Materials are smooth bevelled coral car, petrol cabin, ivory stripe, charcoal tires;
track uses petrol/emerald/slate/ivory. Embedded source-owned flat colors/roughness0.8;
no UV/texture-channel/filter/alpha/emission pipeline. No LOD or budget chosen; visual
cost and sustained LCD/OLED60FPS unmeasured. Front/rear recognition derives from
geometry/stripe, but actual overhead readability could not be reviewed without draw.

## Evidence and remaining acceptance

[Retained evidence](../spikes/s04-evidence/README.md) owns reexport fingerprints,
imported bounds/mesh ancestry, authoring/save-reopen receipts and UID/node identity
checks. Both body candidates pass actual movement/contact APIs and passive physics
checks; separate-process ENet covers collision, stale fences and seated reauthorization.
The inherited boot save/reopen removed redundant instance property serialization
while preserving UIDs, unique node IDs, inherited parent IDs and placement. Accepted
119 original source/fixture/pin paths were byte-identical to8b6dc30.

Camera is provisional47 m/42° vertical fixed yaw at native1280×800, unchanged from
S02 assumptions. One native-window diagnosis had `can_draw=false`, no drawn frames;
no concept/image/headless substitute certifies visual quality, focus or physical
keys. No production style/gameplay/world/target approval is supplied. Required next
handoff: drawable matched camera/lighting states, Regner handling/control review,
actual seat/exit and district queries, Steam and hardware proof under their owners.

## Accepted partial S05 inherited consumers

[Exact754a0b5 S05](../spikes/s05.md#accepted-exact-final-disposition) adds saved
[car](../../prototypes/s05/tests/fixtures/s05/car.tscn) -> S04 kinematic -> unchanged s04_car GLB/
import -> this same s04_kit source. Saved [boot](../../prototypes/s05/tests/fixtures/s05/boot.tscn)
instances that car and S04 track -> unchanged s04_track GLB/import -> the same source;
[burst](../../prototypes/s05/tests/fixtures/s05/burst.tscn) inherits boot with twelve saved cars.
The source map above now includes these reverse consumers, without new asset identity,
source/export changes, copied meshes or imported-child overrides. S05's new scene/
script identities do not change S04 source/import identities or export membership.

[Single S05 contract](../spikes/s05-contracts.md#source-reuse-and-evidence-boundary)
and retained saved-roundtrip/resource receipts bound this technical reuse. Current
wreck appearance is the unchanged neutral car; stationary retained box/query behavior
is not wreck art, moving-contact/final-clearance or production acceptance. Eight
cosmetic tokens are not authored/drawn explosions. Source-linked actual effects,
Regner policies, final-S02/S04-dimension spacing/contact reruns and all visual/input/
feel/Steam/Deck/S07/P0/M1/production gates remain open. No new reexport ran here.

## Accepted partial S06 reverse consumers

The original S04 and S05 source maps above remain intact; original statements about
no world-sector/minimap integration describe the S04 handoff, before this consumer.
[Partial S06 exact7fb302b](../spikes/s06.md#accepted-exact-final-disposition) adds:

| Source collection → export/import | Preserved linked prefab | Saved S06 consumers |
| --- | --- | --- |
| `s04_kit.blend` / `export_s04_car` → `s04_car.glb` + `.glb.import` | [S04 kinematic](../../prototypes/s04/tests/fixtures/s04/kinematic.tscn), `PresentationAnchor/Visuals/Model`, original Collision/Sockets | [intersection](../../prototypes/s06/tests/fixtures/s06/intersection.tscn)/`CarWest` and `CarEast`, inherited by [intersection_wide](../../prototypes/s06/tests/fixtures/s06/intersection_wide.tscn) |

No S06 dynamic-body or track consumer is added. Separate source-linked road geometry
belongs to the [S06 handoff](../spikes/s06-source-handoff.md), with ONE
[contract](../spikes/s06-contracts.md). Cars use unchanged `configure`/`step`/
`motion_state`/`neutralize` and shared handling; no second pose/physics writer.
Actual collider1.8×1.5×3.4 m bodies complete sequential opposing legal LEFT turns
in721 ticks/12.0167 s each with one seam/no sampled outside/contact. Discrete planar
samples do not accept continuous sweep, concurrent junction safety, final dimensions/
turning/exits/wreck contacts, drawn camera/feel or production car art. Larger envelope
analysis uses retained poses, not changed-body physics. Shared-source changes still
reexport both car/track outputs and inspect original/S05/**S06 base/inherited**
consumers; final choices require affected actual route/contact/seam/map reruns.
No source/output/import/UID/socket/placement edit or reexport ran here. All full S04/
S06/S07, Steam/Deck/input/feel/P0/six-block M1/production gates remain open.
