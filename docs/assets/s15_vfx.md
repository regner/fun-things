# s15_vfx — technical weapon/effect mesh handoff

Status: **technical spike blockout only**, 9 October 2026. These meshes replace
engine-generated visible primitives in the S15 cost fixture. They preserve the
measured effect roles and approximate bounds; they are not accepted production VFX.
The S15 lane worker owns the original geometry, Blender source, exports, fixture
integration and measurements. No third-party mesh, material, texture or library is
incorporated.

## Source and output mapping

The shared source uses metres, Blender +Z up, and one explicit export collection per
output. Particle meshes are centered on their emission pivot. The rocket points along
local +X, matching `rocket.gd` movement. There is no collision, rig, animation, image,
UV dependency, socket, or gameplay state in these presentation-only assets.

| Source / collection | Explicit output and import sidecar | Saved consumers |
| --- | --- | --- |
| `prototypes/s15/art/source/models/effects/s15_vfx.blend`; `export_s15_fireball` | `prototypes/s15/art/models/effects/s15_fireball.glb` and `.import` | `prototypes/s15/tests/fixtures/s15/explosion.tscn` `Fireball` draw pass |
| same source; `export_s15_smoke` | `prototypes/s15/art/models/effects/s15_smoke.glb` and `.import` | `explosion.tscn` `Smoke` draw pass |
| same source; `export_s15_spark` | `prototypes/s15/art/models/effects/s15_spark.glb` and `.import` | `explosion.tscn` `Sparks` draw pass |
| same source; `export_s15_debris` | `prototypes/s15/art/models/effects/s15_debris.glb` and `.import` | `explosion.tscn` `Debris` draw pass |
| same source; `export_s15_muzzle_flash` | `prototypes/s15/art/models/effects/s15_muzzle_flash.glb` and `.import` | `prototypes/s15/tests/fixtures/s15/muzzle_flash.tscn` |
| same source; `export_s15_tracer` | `prototypes/s15/art/models/effects/s15_tracer.glb` and `.import` | `prototypes/s15/tests/fixtures/s15/tracer.tscn` |
| same source; `export_s15_impact` | `prototypes/s15/art/models/effects/s15_impact.glb` and `.import` | `prototypes/s15/tests/fixtures/s15/impact_puff.tscn` |
| same source; `export_s15_rocket_trail` | `prototypes/s15/art/models/effects/s15_rocket_trail.glb` and `.import` | `prototypes/s15/tests/fixtures/s15/rocket_trail.tscn` |
| same source; `export_s15_rocket` | `prototypes/s15/art/models/effects/s15_rocket.glb` and `.import` | `prototypes/s15/tests/fixtures/s15/rocket.tscn` `Model` |

`prototypes/s15/tools/s15/author_vfx_assets.py` rebuilds the source and all nine explicit exports
with Blender **5.2.2 LTS**. It starts from an empty file and applies
`prototypes/s01/tools/s01/export_settings.json`, overriding the selected collection, output path,
and animation flag for each output. Godot import uses pinned
**4.8.dev7.official.c971f93e7**, default scene import, scale 1.0, generated LODs,
tangents, and shadow meshes. Re-export all outputs together after changing the shared
source, then rerun isolated import, diagnostics, visual review, and S15 measurements.

## Geometry, materials and integration

| Output | Authored size/radius in metres | Vertices / triangles | Material behavior |
| --- | ---: | ---: | --- |
| fireball | radius 0.90 | 60 / 20 | neutral source material; fixture fire override |
| smoke | radius 1.10 | 60 / 20 | neutral source material; fixture smoke override |
| spark | 0.07 × 0.07 × 0.38 | 24 / 12 | neutral source material; fixture spark override |
| debris | 0.18 × 0.12 × 0.22 | 24 / 12 | neutral source material; fixture debris override |
| muzzle flash | 0.90 × 0.90 card | 4 / 2 | neutral source material; fixture flash override |
| tracer | 0.12 × 1.80 card | 4 / 2 | neutral source material; fixture tracer override |
| impact | 0.65 × 0.65 card | 4 / 2 | neutral source material; fixture impact override |
| rocket trail | radius 0.28 | 60 / 20 | neutral source material; fixture trail override |
| rocket | 0.95 long, radius 0.18 | 80 / 42 | opaque orange emitted `rocket_body` source material |

Each particle scene saves a linked GLB instance as hidden `MeshSource`. Its fixture
script assigns that imported `ArrayMesh` resource to `draw_pass_1`; it does not copy
or serialize vertex data. The wrapper retains its transparent/billboard or opaque
material override and its existing process material, counts, lifetimes, bounds, and
public API. The linked rocket model is rendered directly. Imported roots and shape
names are source-owned; runtime gameplay code must not address them.

## Handoff status

| Stage | Status and scope | Evidence / remaining work |
| --- | --- | --- |
| Brief | accepted, spike-only | Existing S15 effect roles, no-drop rule, camera and stress populations remain authoritative |
| Concept | accepted, technical-only | Low-poly mesh/card substitutions preserve technical color and silhouette roles; production concept remains open |
| Blender blockout | accepted, technical-only | Committed shared source and deterministic authoring script; dimensions and triangle counts above |
| Production asset | pending | Final topology, materials/textures, art review, LOD policy and platform quality tiers remain open |
| Export/import | accepted, spike-only | Nine committed GLBs and sidecars; isolated pinned-Godot import and fixture check pass |
| Prefab | accepted, fixture-only | Saved consumers link imported resources and an isolated graphical smoke run has no diagnostics |
| Placement | not applicable | These are emitter draw meshes and one rocket carrier, not world-sector assets |

Runtime cost and visual evidence remain owned by the
[S15 spike record](../spikes/s15.md). Production promotion must preserve the no-drop
explosion contract, replace technical quality tiers with measured lower-cost assets,
and complete art, integrated gameplay, renderer, OS and target-hardware review.
