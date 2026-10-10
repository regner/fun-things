# city_shore_edges.03 — Simple rock shore

10 October 2026. **Source/export, linked prefab and bounded physics checks delivered;
independent review and world/gameplay acceptance pending.** Original Blender construction
by the commissioned implementation specialist. References: [commission](commission.md),
[shore-edge brief](../city_shore_edges.md), [low seawall](city_shore_edges_01.md),
[quay edge](city_shore_edges_02.md), [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street context](../../concepts/world-v1/stage-04-streets/README.md). The explicit
production task supersedes the historical concept-only restriction. No downloads,
image-to-mesh, purchased models, external artwork, real brands or textures were used.

## Design and provisional dimensions

Three broad slate outcrops over a continuous dark mineral toe. Unequal shoulders,
a slightly lighter central rock and restrained softened edges distinguish the natural
shore treatment from the siblings' straight pale coping strips. No pebbles, noisy
surface textures, seaweed, furniture or implied water interaction. Two mirrored end
outcrops provide compatible cut sections; the middle outcrop has its own asymmetric
hull. The continuous toe undulates in plan rather than supplying a masonry plinth.
Old Quay and East Docks reuse this component; their differences remain placement-owned.

Dimensions are **provisional authored values**, allowed by the production standing
rules, not measurements taken from concept images or approval of coast fit.
**Y=0 is the existing land-contact datum through the rock body**, not the toe bottom
or the crest. Embed the lower .6 m beside the coast rather than raising terrain.
The studio floor beneath the toe is not a proposed land or water level.

| Contract | Godot local metres |
| --- | --- |
| Root/pivot | (0, 0, 0), centred in plan at the land-contact datum |
| Whole AABB | min (-2, -.6, -.8), max (2, .65, .8) |
| Whole X/Y/Z size | 4.000 × 1.250 × 1.600 |
| Toe | Y=-.600 to -.300; closed underside, gently varying width |
| Highest rock crest | Y=+.650; no walkable deck is authored |
| End joins | X=-2 and X=+2, identical planar cut sections |
| Repeat placement | Translate 4.000 along X; no scale or corrective rotation |
| Intended water-facing side | -Z (Blender +Y) |
| Single static collider | 4 × 1.25 × 1.6 box centred (0, .025, 0) |

Envelope/datum tolerance is ±.001 m. Blender +Z maps to Godot +Y; Blender +Y
maps to Godot -Z. Root and joined mesh have identity transforms and metre units.
The model has no socket markers, collision import suffixes or attachment API.

### Family interface and handoff to `.04`

This delivery supplies **only the straight rock shore**. `.04` owns compatible
corners, finished terminals and mixed-edge transitions. Quay furniture retains rails,
mooring bollards and ladders; boardwalk/marina owners retain decks and supports.
Nothing here changes saved coast/harbour polygons, land elevation, tide height or
water-entry rules. A rotated straight is not proof of curved-polygon fit.

The common 4 m repeat and X end planes match the family convention, **not the
siblings' cross-sections**: `.01` is a 1 m high/.72 m wide barrier; `.02` is a flush,
2.4 m deep/1.2 m wide retaining face. Do not directly butt these different profiles
as though they matched. The rock treatment does not replace the deeper quay face.
World integration and `.04` must resolve exposed ends, bends and material/height
transitions without expanding the coast or lifting land.

Validation records identical sets of **31 vertices at each end plane**, comprising
six toe vertices and 25 vertices on the clipped rock section. Exact measured Blender
(Y,Z) pairs are retained in `validation.json:end_profile_blender_yz`; negate Blender Y
for Godot Z. That array is a sorted coordinate set, **not a connected polygon loop**.
For connector construction, use the closed cut-face boundaries in the saved source
mesh at X=±2. `author.py` preserves the input hull recipe, bevel and cut operations;
its `END_PROFILE` is an input shape, not the final beveled end section. No longitudinal
end bevel opens a daylight gap. Collinear placements share end planes; neither
smooth-normal continuity nor arbitrary coast fits are claimed tested visually in-engine.

## Source, export and materials

- Source: `art/source/models/environment/city_shore_edges_03/city_shore_edges_03.blend`.
- Collection: `export_city_shore_edges_03`; root `CityShoreEdges03`, child
  `CityShoreEdges03_Mesh`. Four closed component islands joined into one mesh.
- Export: `art/models/environment/city_shore_edges_03/city_shore_edges_03.glb`
  with retained `.glb.import` settings/identity.
- Wrapper: `scenes/prefabs/environment/city_shore_edges_03.tscn`.
- Author/export/validate/render/check/manifest recipes:
  `tools/asset_production/city_shore_edges_03/`.

Opaque, back-face-culled Principled surfaces, metallic 0 and no emission:

| Export slot | Material | Linear RGB | Roughness |
| --- | --- | --- | --- |
| 0 | `shore_foot_dark_slate` | .095, .145, .16 | .78 |
| 1 | `shore_body_slate` | .20, .265, .29 | .72 |
| 2 | `shore_rock_weathered_slate` | .32, .39, .41 | .76 |

Body/toe colors match `.01`/`.02`; the new weathered mineral tone is darker than
their pale coping. Broad original convex hulls have .04 m, three-segment edge softening
on sufficiently sharp edges, overlap clamping and applied weighted normals. The outer
hulls overlap beneath their shoulders to avoid deep holes; they are intentionally
separate closed solids, not a boolean-unioned terrain mesh. The lower toe is closed.
There are no degenerate or non-manifold source elements; hidden inter-island overlaps
are intentional. No texture/normal-map dependency, embedded image, rig, clips, lights,
interior, destruction or water simulation is included.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**. Export reuses
`tools/assets/blender/export_settings.json`, the named collection only, Y-up, no
skins/animations. Studio objects are not saved in the source or exported. Default
Godot LOD/shadow-mesh generation is retained; transition quality and repeat cost
remain unmeasured. Local recipes follow the sibling conventions; no shared generic
mineral-mesh authoring helper exists. Shared export settings and production checks
are reused rather than changing the common tools.

## Prefab, collision and bounded engine checks

`Visuals/Model` remains an identity-transform linked imported GLB, not copied geometry.
Separate `Collision/Body/RockShore` supplies one simple world-layer-1/mask-0 static box.
The envelope blocks the visible shore obstacle, spans its below-land toe and bridges
the narrow rock creases. It deliberately fills the curved shoulders and lower spaces
between outcrops: it is conservative, not a precise mesh collider or a walkable rock
course. The top is uniformly Y=.65 even where visible shoulders are lower. Keep this
obstacle out of authored walking/driving routes; do not use its box top as a deck or
an invisible extended coast guard. Final route/vehicle and contact fidelity review
remain placement gates, not claims established by this simplified collider.

Pinned Godot **4.8.dev7.official.c971f93e7** imported the GLB and loaded/packed/saved/
reloaded the wrapper and owned fixture twice. Subsequent saves were byte-stable,
including scene UIDs/node identities. Dependency checks resolve all linked paths and
serialized UIDs; imported bounds, three opaque materials, identity model transform
and the separate single-box collision envelope pass explicit assertions. Text scene
authoring plus isolated headless normalization is the prescribed editor fallback.
No live Blender/Godot session was accessed; separate open-editor synchronization is
not claimed. No runtime-authored visible hierarchy is added.

The saved `physics_check.tscn` uses two real wrappers at X=0 and X=4, a test-only
collision floor at Y=0 and production `ActorMotion` (capsule radius .35 m, height 1.8 m).
No visible test geometry is generated. The bounded `check.gd` checks:

- **12 rays** at X=0, 1.999, 2 and 2.001: Y=.2/.6 block at Z=-.8; Y=.75 stays clear.
- **Eight 60-tick movement cases**: front, rear, joined-end contact and a clear end
  bypass, in both AUTHORITY and REPLAY modes through production `ActorMotion.step`.
- Front/seam stop Z=-1.166666269; rear stop Z=+1.166666269; bypass at X=-2.5 reaches
  Z=2.999999762. Contact assertions allow .02 m solver tolerance around the capsule
  and collider envelope; the bypass has an independent .01 m endpoint tolerance.
- Authority/replay position error is **.000129433 m**, below the .001 m limit.
- A second standalone process repeats the same results. These are physics/query
  equivalence observations, **not multiplayer transport/admission/prediction proof**.

## Evidence and validation

[Hero](city_shore_edges_03-evidence/hero.png) · [Side](city_shore_edges_03-evidence/side.png) ·
[Rock shoulder detail](city_shore_edges_03-evidence/detail.png) ·
[47 m / 42° overhead](city_shore_edges_03-evidence/overhead_47m_42deg.png).
All four are isolated Blender Cycles/AgX **1280×720** renders, not engine captures.
Overhead is vertical-down perspective, 47 m above the land datum, vertical FOV 42°,
Blender +Y at image top. The later 720-high cleanliness limit supersedes the older
800-high reference. All views were inspected. An initial uniform segmented profile
was replaced with broader unequal outcrops; a subsequent unrestricted bevel produced
spikes and was corrected with overlap clamping, welding and angle-limited bevels.
The final form has clean large shoulders, a quiet toe and a legible three-mass overhead
silhouette without rubble noise. PNG compression 95 followed by seven-significant-bit
RGB encoding/compression 9 keeps each image below 400 KiB.

[validation.json](city_shore_edges_03-evidence/validation.json) records:

- **966 triangles, 491 source vertices, 699 exported split vertices**.
- **One mesh, three surfaces**, zero degenerate source faces/export triangles,
  zero non-manifold source edges, consistent winding and unit-length normals.
- Actual binary GLB positions, indices and normals validated, not just accessor metadata.
- 4 × 1.25 × 1.6 m bounds, identity land-contact pivot and identical planar end sections.
- Separate fresh export byte-identical to the **25,256-byte GLB**.
- Owned GDScript style/format and final whole-project compilation passed.
- Final canonical production checks **passed, exit 0**: engine/GUT pins, repository
  formatting/lint/compilation, **14 Python tests**, **137/137 GUT tests / 6,523 assertions**,
  isolated import and the expected-failure negative control. No failures were waived.
- An intermediate cleanup added enough blank lines to exceed the owned helper's
  50-line limit; that canonical run failed. Extracting the ray checks and correcting
  spacing resolved it; the final complete run passed independently.

[manifest.json](city_shore_edges_03-evidence/manifest.json) hashes every produced payload
except itself. [final.log](city_shore_edges_03-evidence/final.log) retains the concise
command/results receipt. Scratch renders, intermediate recipes, raw logs, reexports
and check mirrors stay under `C:/tmp/ft/assets/city_shore_edges_03/`, not in the payload.

Diagnostics: Blender's pinned `Material.use_nodes` deprecation notices are retained
in scratch logs; final operations exit normally. Headless editor normalization emits
the known addon version warning and shutdown RID/ObjectDB leak diagnostics after
successful scene checks. Final standalone physics checks have no script/error/warning
diagnostics. The intermediate owned style failures are corrected, not ignored.

## Reproduction

From repository root in Bash; use only the isolated pins, never live sessions.
Pillow is required for PNG recompression. Use a fresh production-check output folder.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_shore_edges_03
S=C:/tmp/ft/assets/city_shore_edges_03
mkdir -p "$S"
for step in author export render; do
  timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
    --python-exit-code 1 --python "$T/$step.py" || exit $?
done
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/reexport.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" -- "$S/reexport.glb"
timeout 300 "$G" --headless --editor --path . --import
timeout 180 "$G" --headless --editor --path . --script "$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 180 "$G" --headless --path . --script "$T/check.gd"
timeout 60 "$(mise which gdstyle)" --max-warnings 0 "$T/check.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
python "$T/manifest.py" "$S/checks-reproduction"
```

## Remaining acceptance

Independent art/technical review, actual engine blue-hour/gameplay-camera views,
whole-coast fitting and `.04` corner/end/transition tests, land/water levels,
boardwalk alignment, actor route/vehicle contact fidelity, real network transports,
packaged builds, LOD transitions and sustained GPU/Deck/repetition profiling remain
pending. This component does not approve world placement or define water access.
No shared brief, queue, progress, road data, world scene, sibling asset, gameplay rule
or project setting was changed.
