# s01_static — technical asset handoff

Spike-only asymmetric static fixture. [S01](../spikes/s01.md) owns exact settings,
logs, versions, source/export hashes and observed failure history; the canonical
[workflow](../assets.md) and [scene contract](../scene-structure.md) remain owners
of policy. Accepted Petrol & Coral and city +X east/-Z north inform the brief.
This is no production building/prop or camera/movement acceptance.

## Brief, owners and provenance

Codex produces and technically reviews brief, neutral concept, Blender source,
export/import, prefab, materials and fixture placement. Regner owns the accepted
art direction; no separate production art acceptance is claimed. Original authored
boxes, bevels and 8×8 palette; project-owned, no third-party dependencies/attribution.
Purpose: prove explicit GLB, static sockets, metre datum, repeated imports and a
coral inherited material variant. Envelope/tolerance chosen for the test:
Body 2×1×1 m (Godot X/Y/Z), ground centre Y=0; comparisons within 0.0001 m.
Front is asymmetric toward -Z; one-metre ruler at X=1.3. Overview/vertical reference
views and renderer are recorded in S01, not claimed as approved gameplay views.

## Source and consumers

| Source/dependencies | Collection/root/members | Output/settings | Consumers |
| --- | --- | --- | --- |
| `prototypes/s01/art/source/models/spikes/s01_static.blend`; packed palette also retained as `prototypes/s01/art/source/textures/spikes/s01_palette.png` | `export_s01_static`; synthetic glTF scene root; Body, Front, Meter, socket_muzzle, right_axis, up_axis | `prototypes/s01/art/models/spikes/s01_static.glb` and `.glb.import`; palette exported separately to `prototypes/s01/art/textures/spikes/s01_palette.png` and `.png.import` | `prototypes/s01/tests/fixtures/s01/static_prefab.tscn`, inherited `static_variant.tscn`; StaticA/StaticB/Variant in `roundtrip.tscn` |

Material slots: Body uses `body_paint` → external `s01_petrol.tres` → explicit
runtime palette; Front uses `front_accent` (flat coral), Meter `meter_reference`
(flat ivory). Stable surface names, one material per object. Variant root overrides
`body_material=s01_coral.tres`; application changes presentation only. Imported
children are not editable or serialized in the accepted variant. Both imports share
petrol material/texture. No embedded image, linked source library, normal map,
transparency, emission, bake, LOD or derived navigation/minimap data is needed.
Blender modifiers/triangulation are applied; source mesh density is intentionally
tiny, with no production polygon/performance budget inferred.

## Measurements and sockets

| Item | Imported local measurement |
| --- | --- |
| Body | AABB min (-1,-0.5,-0.5), size (2,1,1); object translation (0,0.5,0) |
| Front, final | AABB min (-0.35,-0.125,-0.125), size (0.7,0.25,0.25); translation (0,0.75,-0.625) |
| Meter | Size (0.1,1,0.1); translation (1.3,0.5,0) |
| Combined render bounds | Min (-1,0,-0.75), max (1.35,1,0.5); asymmetric ruler is outside the body footprint |
| socket_muzzle | Blender empty (0,+0.75,+0.75); Godot (0,+0.75,-0.75), identity basis, local -Z forward/+Y up |
| right_axis / up_axis | Godot (1,0,0) / (0,1,0), unit root scales |

Socket path is `Visuals/Model/socket_muzzle` for this technical fixture. It has no
weapon consumer; production must expose the scene contract's socket API through a
source-derived adapter. Rig/clips are not applicable to static content. Ruler and
front are decoration, not authoritative collision. Saved Collision/Body/Shape is
a 2×1×1 m BoxShape3D at (0,0.5,0), default fixture layer/mask; tests establish the
resource envelope/inheritance only. Movement/turn/clearance/network checks belong
to S02/S04/S06, so no production collision gate is accepted.

## Handoffs, 7 October 2026

Reviewed revision is the final source/export fingerprint in S01 evidence, with
all files delivered in the same change. Producer → reviewer is Codex → Codex for
this technical self-review; no silence or independent art review is implied.

| Stage | Status/scope | Evidence/findings |
| --- | --- | --- |
| Brief | accepted, technical-only | Bounded dimensions, tolerance, axes and import/repetition requirements above |
| Concept | accepted, neutral fixture-only | Simple asymmetric boxes/ruler; no production style acceptance |
| Blender blockout | accepted, resource-only | Linked source/export, measured datum/bounds/normals/sockets; actual movement not applicable to this technical scope |
| Production asset | not applicable | No finished art or calibrated palette |
| Export/import | accepted, asset profile | Exact tools/preset/sidecars, re-export, no images embedded, clean cache and existing editor inspection |
| Prefab | accepted, wrapper workflow | Linked model, deliberate box resource, wrapper material variant and identities; direct imported-child override rejected |
| Placement | accepted, fixture-only | Five saved IDs/transforms; repeated mesh sharing, save/close/reopen and hashes; no sector/navigation/performance acceptance |

Compatible technical appearance revision: front width 0.5→0.6→0.7 m stays inside
the existing body's X footprint and changes neither collision nor sockets. Both
exports were refreshed; inherited color, root identities and placement preserved
with the accepted root override. Direct child-override identity churn and editor/
full-project diagnostics are recorded in S01. Codex owns future fixes if that
rejected alternative becomes needed; engine changes and production cases deferred.
