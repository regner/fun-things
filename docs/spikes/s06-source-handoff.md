# S06 neutral intersection source handoff

Producer/source/editor/world owner: sole S06 Sol6.1 HIGH lead. Technical spike
handoff; independent review and production art remain distinct. Original Blender
geometry/materials, no external model/image/library/license dependency. Neutral
Petrol & Coral flat intersection, not detailed accepted street art.

| Committed source / collection | Explicit output / saved linked consumer |
| --- | --- |
| `prototypes/s06/art/source/models/spikes/s06_intersection.blend`, `export_s06_west` | `prototypes/s06/art/models/spikes/s06_west.glb` + engine `.import` → `prototypes/s06/tests/fixtures/s06/west.tscn/Visuals/Model` |
| Same source, `export_s06_east` | `prototypes/s06/art/models/spikes/s06_east.glb` + engine `.import` → `prototypes/s06/tests/fixtures/s06/east.tscn/Visuals/Model` |

Exact34 named members are in `prototypes/s06/tools/s06/export_members.json`; committed source owns
subsequent authoring, bootstrap refuses overwrite. Metres, Blender +Z up/+Y front
converted once to Godot +Y up/-Z forward. Applied positive unit scale/rotation,
triangulation, embedded original flat shader colors/roughness0.8, no textures,
animation/rig/skins/extensions, corrective prefab scale or generated Godot mesh.
Blender5.2.2 LTS `d13f752e3b9c`/glTF5.2.40; unchanged Godot4.8-dev7/gdstyle0.3.0.
Export uses unchanged S01 settings with animations disabled, explicit collections.
New sidecars use engine defaults and retain imported scene UIDs.

Imported source spans X/Z[-24,24], road horizontal/vertical carriageways9 m wide,
sidewalks4 m wide/visual top0.015 m, road topY0. West/East split exactly atX0.
Two15.5×0.6×15.5 m islands per side occupy the far quadrants, matched by deliberately
saved World collision boxes. Source crossing markings have3 m length atZ6.5.
No floor collider/gravity: planar bodies hold their datum. Decoration and topology
do not create implicit physics/navigation. Raised curbs/slopes are unproved.

`intersection.tscn` instances both sectors and unchanged S02 actor/pistol and two
reviewed S04 kinematic cars. Its inherited `intersection_wide.tscn` changes camera
42°→50° only. S02 actor/model/pistol and S04 car/collider/sockets retain accepted
source/import ancestry; all originals are immutable. This new consumer supplement
avoids editing the concurrent canonical catalogue/handoff/world/API guides.

Source→exports→sectors→intersection/inherited variant must be reviewed together
after a change, with explicit editor refresh/reopen and stale-data bake checks.
Source reexport equality, exact imported geometry, placement/UID/node identities,
raw logs and retained fingerprints accompany the result. Actual sampled bodies
prove only these planar routes. Source/static captures do not certify runtime
drawn readability, camera follow, physical input/focus or feel. Final S02/S04 choices
require affected route/contact/map reruns, with source/envelope changes coordinated.
