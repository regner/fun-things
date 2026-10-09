# s13_humanoid — technical character/crowd handoff

Status: **technical blockout only**, 9 October 2026. This asset tests the shared-rig,
clip, palette and crowd-cost direction. It is not production character art or an
accepted player/pedestrian silhouette. The S13 lane worker authored the source,
export, integration and measurements; independent review remains pending.

## Brief and source mapping

Purpose: one shared low-poly humanoid for player/pedestrian presentation experiments,
with exact `idle`, `walk`, `run` and `death` clips, three flat-color variants and a
68-live/16-dead crowd fixture. The accepted [art direction](../art-direction.md)
informs chunky proportions and ivory/coral/cobalt colors. The asset remains a neutral
technical blockout; it does not replace the accepted concepts or select production
clothing, hair, local-player identification or animation quality.

| Source / output | Declared content | Consumers |
| --- | --- | --- |
| `art/source/models/characters/s13_humanoid.blend` | Blender 5.2.2 LTS; collection `export_s13_humanoid`; objects `Rig`, `Skin` | Explicit export below |
| `art/models/characters/s13_humanoid.glb` and `.import` | One skinned mesh, one seven-bone skin, four actions, no images/extensions/compression | `tests/fixtures/s13/character.tscn` |
| `tools/s13/author_humanoid.py` | Rebuild authoring script for this original blockout | Creates source and initial export; not runtime code |
| `tools/s13/export_humanoid.py` | Validated collection export from the committed `.blend` | `tools/s13/reexport.py` |
| `art/materials/s13_{ivory,coral,cobalt}.tres` | Opaque external palette materials | Wrapper-owned overrides and saved crowd instances |
| `tests/fixtures/s13/character.tscn` | Linked model under `PresentationAnchor/Visuals/Model`, notifier and presentation API | 84 saved instances in `crowd.tscn` |

The S13 lane worker created every model, rig, animation and material for this project.
No third-party mesh, rig, animation, texture, image or library is incorporated.

## Geometry, rig and clips

Blender uses metres, +Z up and +Y front; import maps this to Godot +Y up and -Z
forward. The origin is ground between the feet. Bind-pose AABB from the GLB position
accessor is minimum `(-0.5, 0, -0.29000002)` and maximum
`(0.5, 1.80000007, 0.205)` metres. The single material surface has **297 vertices
and 396 triangles**, below the spike's 1,500-triangle ceiling. Broad bevels and
smooth shading are deliberate technical readability choices, not final topology.

Stable technical bones are `root`, `spine`, `head`, `arm_l`, `arm_r`, `leg_l` and
`leg_r`. Every vertex has one influence. This is enough to measure a skinned crowd,
but is not an anatomical production hierarchy. There are no hand/weapon sockets,
fingers, facial bones, retargeting contract, corrective shapes or authored LOD meshes.
The committed Godot import configuration enables automatic mesh LOD generation;
production must add required attachment bones/sockets and validate its LOD strategy
through a coordinated rig migration.

| Clip | Blender frames at 30 fps | Imported duration | Technical behavior |
| --- | ---: | ---: | --- |
| `idle` | 1–61 | 2.033333 s | In-place sway; wrapper repeats it |
| `walk` | 1–31 | 1.033333 s | In-place opposing limbs; wrapper repeats it |
| `run` | 1–21 | 0.7 s | In-place faster opposing limbs; wrapper repeats it |
| `death` | 1–31 | 1.033333 s | One shot; wrapper seeks to and freezes its final pose for corpses |

The imported actions do not currently carry loop metadata. The technical wrapper
restarts locomotion clips on completion. Production imports should own reviewed loop
settings/seams rather than relying on this spike callback. No clip translates the
entity/model root or applies gameplay events.

## Variants, wrapper and saved placement

The linked mesh retains its `body_paint` material. `character.gd` applies one saved
external material at the wrapper boundary; it does not copy geometry or serialize an
editable imported child. The three variants establish palette swapping only. Mesh or
outfit variants remain valid when their skin, rest pose, bone names and attachment
contract match this shared rig.

`character.tscn` exposes presentation-only state changes and visibility throttling.
`crowd.tscn` saves all transforms: 30 live actors inside the 47 m/42° camera view,
38 live actors outside it, and 16 visible final-pose corpses. Runtime chooses clips
and update detail but does not create the hierarchy or placement. There is no
collision, movement, health, AI, network state or gameplay authority in this fixture.

## Handoff status

| Stage | Status and scope | Evidence / remaining work |
| --- | --- | --- |
| Brief | accepted, spike-only | Dimensions, triangle ceiling, rig/clips, populations, camera and variants are explicit |
| Concept | accepted, technical-only | Chunky neutral blockout follows Petrol & Coral; production concept selection is unchanged |
| Blender blockout | accepted, technical-only | Committed source/authoring script; 396 triangles; measured bounds and stable names |
| Production asset | pending | Final anatomy, clothing/hair silhouettes, weapon socket, production motion, authored/validated LOD strategy and art review are absent |
| Export/import | accepted, spike-only | Pinned Blender export is byte-identical; isolated Godot import and public API checks pass |
| Prefab | accepted, fixture-only | Linked GLB, saved material API, notifier and imported animation paths; no copied mesh |
| Placement | accepted, fixture-only | Saved 68-live/16-dead population and 42°/47 m camera; production world placement is not implied |

Re-export evidence is in
[`s13-evidence/reexport.json`](../spikes/s13-evidence/reexport.json). Crowd and cost
results are owned by the [S13 spike record](../spikes/s13.md). Source/export changes
must update both together, preserve the rig compatibility inputs, rerun the isolated
import/public API check, and visually review all three palettes and the death pose.
