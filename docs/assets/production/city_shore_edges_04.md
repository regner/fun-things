# city_shore_edges.04 — Edge corner

10 October 2026. **Six source/export components, linked prefabs and bounded engine checks
delivered; independent review and world/gameplay acceptance pending.** Original Blender
construction by the commissioned implementation specialist. References: [commission](commission.md),
[shore family brief](../city_shore_edges.md), [low seawall](city_shore_edges_01.md),
[quay edge](city_shore_edges_02.md), [rock shore](city_shore_edges_03.md),
[approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street context](../../concepts/world-v1/stage-04-streets/README.md).
The explicit production commission supersedes the historical concept-only restriction.
No downloads, purchased meshes, image-to-mesh, external artwork or real brands were used.

## Design and approved delivery scope

A **six-piece same-profile connector set**: a 90° mitre corner and a finished terminal
for each of the low wall, deep quay and rock shore. The supervisor explicitly confirmed
this scope during production; mixed-profile transitions are a separate placement-driven
follow-up, not a silently omitted part of this delivery.

Wall and quay carry forward broad battered slate faces, dark toes, narrow bed recesses
and pale chamfered coping. The corners have continuous mitred coping rather than added
ornament; the short terminals finish with a softened nose. Rock connectors have a quiet
dark toe, two broad shoulders around the bend and a tapered terminal outcrop. Weighted
mineral normals avoid crunchy bands without adding rubble or fine textures. These small
connectors use the sibling's dark body tone, not its central weathered accent outcrop.
Old Quay and East Docks share the same interfaces; placement and separately owned
furniture provide district differences.

All dimensions below are **provisional authored values**, permitted by the production
standing rules and matching the already delivered siblings, not inferred concept-image
measurements or approval of coast fit. No coast/harbour polygon, land height, water
level, road, boardwalk deck, furniture or water-entry mechanic was changed.

## Dimensions, datums and mating interfaces

Godot +Y is up; Blender +Z maps to +Y and Blender +Y to Godot -Z. Roots and mesh nodes
are identity transforms with metre units. Bounds/datum tolerance is ±.001 m; section
matching tolerance is .000001 m. Corner roots are **centreline bend anchors at the land
datum**, not the centres of their asymmetric L-shaped bounds. Terminal roots are centred
on their 1 m plan length at the same family land datum.

| Variant suffix | Godot AABB minimum → maximum (m) | X/Y/Z size (m) |
| --- | --- | --- |
| `wall_corner` | (-2, 0, -2) → (.36, 1, .36) | 2.36 × 1 × 2.36 |
| `wall_end` | (-.5, 0, -.36) → (.5, 1, .36) | 1 × 1 × .72 |
| `quay_corner` | (-2, -2.4, -2) → (.6, 0, .6) | 2.6 × 2.4 × 2.6 |
| `quay_end` | (-.5, -2.4, -.6) → (.5, 0, .6) | 1 × 2.4 × 1.2 |
| `rock_corner` | (-2, -.6, -2) → (.8, .65, .8) | 2.8 × 1.25 × 2.8 |
| `rock_end` | (-.5, -.6, -.8) → (.5, .65, .8) | 1 × 1.25 × 1.6 |

- Low wall: land contact Y=0, barrier top Y=1; no below-datum retaining face.
- Quay: coping top/land datum Y=0, retaining toe Y=-2.4. **Do not raise terrain**
  to the toe. This flush walkable cap is not an above-ground guardrail.
- Rock: land datum passes through the body at Y=0, toe Y=-.6, shoulder crest Y=.65.
  This is an obstacle, not a walking deck or rock-climbing route.
- Corner joins: incoming centre (-2, 0, 0), tangent +X; outgoing centre (0, 0, -2),
  tangent -Z. Both are planar, unbevelled mating sections. In Blender the mitre ring
  is (-u, u, height), connecting X=-2 to Y=+2 without intersecting loft stations.
- Terminal join: centre (-.5, 0, 0), tangent +X; finished nose at X=+.5. Wall/quay
  nose finishing occupies the last .15 m, reducing half-width to 84% and trimming
  upper/lower heights by .025 m. Rock nose reduces half-width to 40% and top to .15 m;
  the preceding shoulder reaches .65 m. The dark toe remains closed.

`author.py` reads the actual closed cut-face boundary loops from the three committed
sibling Blender sources. It does **not** interpret `.03`'s unordered vertex receipt as
a polygon. It constructs new lofted corner/end solids, removes the appended complete
sibling mesh datablocks and saves only the six new export collections. No original
straight carrier is duplicated in this asset. Exact mating sets contain **24 vertices
for wall/quay and 31 for rock**, with measured maximum coordinate error **0 m** against
the original sibling source at all nine mating faces. Source hashes and ordered per-asset
point measurements are retained in validation.json.

### Placement example and limits

For a corner at identity, place the corresponding straight at (-4, 0, 0), another at
(0, 0, -4) with Godot yaw +90°, and the terminal at (0, 0, -6.5) with yaw +90°. The
saved check fixture uses these exact wrappers/transforms for all three families. The
visual joins meet at X=-2, Z=-2 and Z=-6; there is no scaling or corrective model offset.

Rotate an entire compatible run to orient it, preserving its handed section. Wall/quay
sections are symmetric; the rock section is **not** symmetric across its width. Do not
independently yaw a rock terminal 180° and assume it fits the opposite end of an unchanged
straight. The supplied rock connector is handed; opposite-handed rock ends/bends, other
angles, curves and polygon-specific closures need placement-driven variants rather than
negative scales or forced approximate seams. This set does not claim to fit every coast
bend. No world placement or shoreline redesign is included.

## Sources, exports and materials

- Source: `art/source/models/environment/city_shore_edges_04/city_shore_edges_04.blend`.
- Six collections: `export_city_shore_edges_04_<suffix>` using the table suffixes.
- Roots: `CityShoreEdges04_<suffix>`; single child `CityShoreEdges04_<suffix>_Mesh`.
- GLBs: `art/models/environment/city_shore_edges_04/city_shore_edges_04_<suffix>.glb`,
  each with its retained `.glb.import` metadata/UID.
- Linked wrappers: `scenes/prefabs/environment/city_shore_edges_04_<suffix>.tscn`.
- Reproducible author/export/validate/render/check/manifest recipes and saved assembly:
  `tools/asset_production/city_shore_edges_04/`.

Wall/quay have four opaque Principled slots, identical to siblings .01/.02:
`shore_body_slate` (.20, .265, .29; roughness .72), `shore_foot_dark_slate`
(.095, .145, .16; .78), `shore_joint_recess` (.045, .075, .085; .82), and
`shore_coping_pale_slate` (.46, .52, .53; .62). Values are linear RGB. Rock has two
slots in order: `shore_foot_dark_slate`, `shore_body_slate`. All metallic 0, back-face
culled, no emission. Four closed solid islands per masonry mesh; two per rock mesh.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Exports use the
shared `tools/assets/blender/export_settings.json`, named collection filters, Y-up and
no skins/animations. No textures, embedded images, external material overrides, rig,
clips, sockets, destruction, water simulation, lights or interiors. Studio geometry
and display transforms are never saved in the production source. Default Godot LOD
and shadow mesh generation remain enabled; repeated-placement cost is not measured.

## Prefab, collision and bounded engine checks

Each wrapper keeps an identity-transform imported instance at `Visuals/Model`. Collision
is separate at `Collision/Body`: one static body on world layer 1/mask 0, **two simple
boxes for a corner, one for a terminal**. Their union follows the L rather than filling
its concave open area. Family widths/heights match sibling conservative envelopes;
small coping/body recesses and rock shoulder hollows do not become snagging shapes.

The outgoing corner box has **1 mm padding at each longitudinal end**. An initial exact
butt collider produced floating-point ray cracks at the wall/quay outgoing joint's
precise Z=-2 plane, despite capsule traversal succeeding. The tiny overlap removes those
query cracks at both the internal compound seam and the sibling join; no visual profile
or sibling is modified. Collision otherwise has the table's bounds. Terminal boxes
conservatively fill the softened/tapered noses, particularly the rock terminal's upper
space. Keep rock connectors outside walking routes; its uniform .65 m collider top is
not approval of a deck. Final contact fidelity/vehicle placement review remains pending.

Pinned Godot **4.8.dev7.official.c971f93e7** imported all six GLBs, loaded/packed/saved/
reloaded all six wrappers and the assembly twice, preserving byte-stable scene UIDs and
node identities. Linked dependencies and serialized UIDs resolve; imported bounds,
materials and collision match explicit assertions. Text scene authoring plus isolated
headless normalization is the prescribed fallback. No live editor was accessed and
separate open-editor synchronization is not claimed.

The saved `physics_check.tscn` has three L assemblies using the real sibling wrappers,
test-only collision floors and production `ActorMotion` (capsule r=.35 m, h=1.8 m).
It does not generate visible test meshes. `check.gd` exercises:

- **37 rays**: either side and exactly on nine straight/corner/end seam planes,
  three above-top clear rays, and seven downward rays proving continuous Y=0 quay
  walking over the incoming joint, mitre, outgoing joint and terminal.
- **16 movement cases** in AUTHORITY/REPLAY: wall/rock input-seam contact, terminal-nose
  contact, clear end bypass, plus quay input-to-mitre and mitre-to-terminal walking.
- Wall seam stop Z=.709635; rock seam stop Z=1.166666; nose stop Z=-7.350259;
  bypass reaches Z=-3. Quay walks reach X=11.9998 and Z=-6.499601 with feet within
  .001 m of Y=0. Contact/end-position tolerance is .025 m.
- Maximum authority/replay positional difference **.000847106 m**, below .001 m.
  A second standalone process reproduces the bounded results. This is not actual
  multiplayer transport/admission/prediction or vehicle-driving acceptance.

## Evidence and validation

[Hero](city_shore_edges_04-evidence/hero.png) · [Side](city_shore_edges_04-evidence/side.png) ·
[Terminal details](city_shore_edges_04-evidence/detail.png) ·
[47 m / 42° overhead](city_shore_edges_04-evidence/overhead_47m_42deg.png).
Four isolated Blender Cycles/AgX renders, **1280×720**, not engine captures. Columns
are wall/quay/rock; corners are behind the terminals. Hero/side/detail temporarily align
component bottoms to a studio floor (quay roots lifted 2.4 m, rock .6 m) to expose every
retaining face; these are exhibit transforms, **not land placement**. The overhead
restores every root to the common land datum, uses a vertical-down perspective camera
47 m above it, 42° vertical FOV, Blender +Y at image top and studio floor below the
quay toe. The later 720-high production limit supersedes the old 800-high reference.

All four final images were inspected. Wall/quay remain clear pale L-shaped strips and
rock reads as a broader quiet rounded connector overhead. Initial unweighted and flat
rock normals were compared; applied weighted normals retain the smooth family treatment.
Fine seam shading and blue-hour readability still need actual engine placement review.
Blender output dither is disabled; PNG compression 95 followed by lossless 8-bit RGB
recompression at level 9 keeps every rendered color value and each image below 400 KiB.

[validation.json](city_shore_edges_04-evidence/validation.json):

| Variant | Triangles | Source vertices | Export split vertices | Surfaces | GLB bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| wall_corner | 128 | 72 | 224 | 4 | 9,504 |
| wall_end | 176 | 96 | 313 | 4 | 11,936 |
| quay_corner | 128 | 72 | 230 | 4 | 9,664 |
| quay_end | 176 | 96 | 316 | 4 | 12,032 |
| rock_corner | 426 | 217 | 329 | 2 | 12,376 |
| rock_end | 240 | 124 | 242 | 2 | 9,164 |

Total **1,274 triangles / 677 source vertices / six meshes / 20 surfaces**. Every
variant has zero degenerate source faces/export triangles, zero non-manifold edges,
consistent winding, unit-length normals and applied transforms. Actual binary GLB
positions, indices and normals are checked, not only accessor metadata. All six fresh
exports are byte-identical to their committed GLBs.

Owned GDScript formatting/lint and individual compilation pass. The final canonical
production command **exited 1**: its global 120 s compilation deadline left **75 of
166 scripts** deadline-limited, including this asset's check. Every failed compile log
contains only the deadline marker, not script diagnostics. All 75 then compiled
individually with separate 180 s bounds, exit 0/no diagnostics; source hashes and
outcomes remain separate from the failed canonical result. Repository formatting/style,
**14 Python tests**, **137/137 GUT tests / 6,523 assertions**, engine/GUT pins, isolated
import and expected-failure negative control passed. No failure is waived or relabelled.
An earlier canonical run compiled all 166 scripts but correctly failed owned formatting;
that formatting is fixed. Shared tooling was not edited.

[manifest.json](city_shore_edges_04-evidence/manifest.json) hashes every produced payload
except itself. [final.log](city_shore_edges_04-evidence/final.log) is the concise retained
receipt. Raw retries, check mirrors and intermediate renders stay under
`C:/tmp/ft/assets/city_shore_edges_04/`. Blender emits pinned `Material.use_nodes`
deprecation notices. Headless editor normalization emits the known addon version warning
and shutdown RID/ObjectDB diagnostics after successful saves; final standalone checks
have no script/error/warning diagnostics. Initial fixture bypasses fell off an undersized
test floor; the floor was widened without changing production geometry.

## Reproduction

From repository root in Bash, with Pillow available for render compression. Only use
isolated pinned tools; never live sessions. Use a fresh canonical output directory.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_shore_edges_04
S=C:/tmp/ft/assets/city_shore_edges_04
mkdir -p "$S"
for step in author export render; do
  timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
    --python-exit-code 1 --python "$T/$step.py" || exit $?
done
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/reexport"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" -- "$S/reexport"
timeout 300 "$G" --headless --editor --path . --import
timeout 180 "$G" --headless --editor --path . --script "$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "$T/check.gd"
timeout 60 "$(mise which gdstyle)" --max-warnings 0 "$T/check.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
```

For deadline-limited canonical results, reproduce the individual compiler follow-up
using the exact Python/GNU-timeout command in [the quay sibling](city_shore_edges_02.md#reproduction),
substituting `city_shore_edges_04` and the new check directory. Keep its canonical status
failed. Then run `python "$T/manifest.py" "$S/checks-reproduction"`; its validation
requires successful owned compilation and hashes the final payload. An unchanged
canonical deadline failure should not be repeatedly rerun.

## Remaining acceptance and follow-ups

Independent technical/art review, actual engine blue-hour/gameplay-camera views,
whole-coast fitting, visual seam shading, water/land exposure, boardwalk/furniture
alignment, route and vehicle contact fidelity, actual network transports, packaged
builds, LOD transitions and sustained GPU/Deck/repetition profiling remain pending.
This delivery is not an approved world placement or water-entry system.

**Mixed-profile transitions explicitly deferred by supervisor decision:** low wall ↔
quay (above-ground barrier versus below-datum retaining face), low wall ↔ rock (coping
versus outcrop), and quay ↔ rock (deep flush quay versus shallow rock toe). World
integration should identify actual pairs, turn angles, handedness, exposure and required
lengths before commissioning them. Never directly butt these incompatible profiles,
raise land, or modify the saved shoreline to hide a mismatch. Opposite-handed rock
terminals/bends are likewise a placement-demand follow-up. No shared brief, queue,
progress, sibling, world scene, road data, gameplay rule or project setting was changed.
