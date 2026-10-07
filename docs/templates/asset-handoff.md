# <asset_id> — asset handoff

Copy to `docs/assets/<asset_id>.md` when brief work starts; link it from the
[catalogue](../asset-catalogue.md). After copying, change these introductory links
to `../asset-catalogue.md` and `../assets.md`. Follow the canonical
[workflow](../assets.md); this template records an asset's facts and evidence,
not a second technical policy. Replace placeholders; mark unknowns pending with
an owner/checkpoint, and unused fields not applicable with a reason.

## Identity, brief and owners

- Asset ID/family, purpose, variants and spike-only/production scope:
- Gameplay/design brief and scene/API contract references:
- Chosen art/layout direction, concept selection/date and reviewer:
- Named owners: brief, concept, Blender source, technical integration, prefab,
  gameplay review, art review, world integration; list owned files:
- Original creator or source URL, license/notice, transformations and attribution:
- Required visual/gameplay states and consumers:
- Camera/renderer/resolution and acceptance tolerances; provisional or settled:
- Dimensions X/Y/Z in metres, local origin/datum, front/up and footprint/overhang:
- Visual/collider/clearance envelopes, ground contact and route/connector constraints:
- Rest/animated/effect bounds, culling margin and owning measurement reference:

## Source, exports and consumers

List every output from shared sources; link shared rig/material records. Verify
consumer lists with repository/editor inspection before reexport. Paths are relative
to repository root; preserve existing runtime paths and saved identities.

| Source and dependencies | Export collection/root and members | Output(s) and import sidecars | Direct/inherited prefabs and placed sectors |
| --- | --- | --- | --- |
| <art/source/...blend; linked libraries/images> | <export_asset_id; explicit members> | <GLBs/textures; .import files> | <scenes/..., including inherited variants> |

- Source/output revision reviewed and export date:
- Blender exact version/build/exporter, Godot exact pin and renderer:
- Export settings/preset location: GLB, units/Y-up, collection filtering, modifiers,
  triangulation, normals/tangents, texture handling, skin/clip sampling:
- Import settings and intentional overrides: root/scale, textures, materials,
  animation/loop settings, LOD/shadow mesh, any import hints/scripts:
- Scene/resource UIDs, node/inheritance identities and stable gameplay/world IDs
  to preserve; link saved files or identity comparison evidence:
- Expected imported hierarchy and required prefab-facing paths/components:
- Shared sources/material consumers and dependent topology/navigation/minimap/
  occluder data; revision owner and refresh procedure:

## Sockets, rig and clips

| Socket | Source parent/bone | Rest position/rotation, forward/up | Stable prefab path and consumer/owner |
| --- | --- | --- | --- |
| <name or not applicable> | <parent/bone> | <metres; rotation units declared> | <path; rule/component> |

- Rig source/owner, bone hierarchy/names, rest pose, skin/influences, attachment bones:
- Compatible variants and pose checks; link shared rig specification if applicable:

| Exported clip | Source action/slot/NLA and frame range | Frame rate/duration | Loop/final-pose behavior and consumer |
| --- | --- | --- | --- |
| <idle/walk/run/death or not applicable> | <export association/settings> | <fps; seconds> | <loop/one-shot; presentation owner> |

## Materials, textures and collision

| Slot name/order | Source assignment → Godot material | Textures and source/channel/color-space mapping | Variant overrides |
| --- | --- | --- | --- |
| <slot/index> | <Blender material; .tres path> | <paths or flat color; size/UV/tile metres> | <none or documented override> |

- Texture filtering/repeat, mipmaps/compression, normals, alpha/emission settings:
- Geometry/UV density, triangles/material surfaces, LOD method/transitions/rationale:
- Collision owner, shapes/envelopes, layers/masks contract and intentional visual gaps:
- Gameplay outcomes to test: movement/turns/seams/spawn/exit/boundaries/destruction:
- Performance/load reference and limits; mark unmeasured values provisional:

## Handoff acceptance

Every stage records evidence for the reviewed revision. Missing checks stay pending;
do not pre-fill acceptance. Include logs, measurements, comparable captures and
save/reopen diffs as required by the workflow. A spike-only review is not production
acceptance. Specify rejection/fix owner in findings; reopen dependent gates.

| Stage | Producer → reviewer (names) | Status/scope | Reviewed revision/date | Evidence and findings/fix owner |
| --- | --- | --- | --- | --- |
| Brief | <names> | pending | <revision/date> | <constraints, evidence> |
| Concept | <names> | pending | <revision/date> | <silhouettes, selected camera view/provenance> |
| Blender blockout | <names> | pending | <revision/date> | <scale/pivots; actual movement/camera> |
| Production asset | <names> | pending | <revision/date> | <style/rig/material/bounds review> |
| Export/import | <names> | pending | <revision/date> | <all outputs; clean import and existing editor> |
| Prefab | <names> | pending | <revision/date> | <ancestry/collision/IDs; inherited save/reopen> |
| Placement | <names> | pending | <revision/date> | <sectors/transforms; derived data/playtest/profile> |

## Change and rejection log

- Change/date/owner, reviewed source/output revision and prior accepted revision:
- Compatible appearance-only change or coordinated migration; affected consumers:
- Findings: file/node, observed failure, impact, expected outcome and fix owner:
- Reopened gates/derived data and retest evidence; preserved IDs/overrides/transforms:
- Checks not run and why, limitations, pending decisions/owners/checkpoints:
- Outcome and cohesive resolving commit/source revision:
