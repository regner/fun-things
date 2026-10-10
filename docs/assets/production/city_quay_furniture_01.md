# city_quay_furniture.01 — Mooring bollard

10 October 2026. **Source/export and linked-prefab candidate delivered; independent
review and world/gameplay/device acceptance pending.** Production commissioned by
Regner under [commission](commission.md) and the current per-asset common brief,
which supersede the earlier concept-only restrictions in the
[waterfront furniture brief](../city_quay_furniture.md).

Producer: commissioned implementation specialist, branch `lane/a-quay`. Supervisor
owns independent acceptance and integration. This is the first delivered member of
this family lane; no sibling output was present to modify. Queue, shared briefs,
progress, existing assets, world scenes and project settings are unchanged.

## Design and dimensions

Original Blender construction: a squat cast-metal mooring bollard with an oval
mushroom head, undercut rope waist, gently flared foot, rounded rectangular anchor
plate and four restrained hex anchors. The broad head distinguishes it from the
slim road bollard. Dark teal casting, slate anchors and a narrow painted amber crown
rim follow Petrol & Coral and the Old Quay / East Docks district identities. No
ropes, boats, labels, real brands, downloaded meshes, textures or new interactions.

All dimensions below are **provisional authored values**, not measurements inferred
from concept images. They follow the standing authorization to proceed with sensible
prop envelopes. Acceptance tolerance is **±0.001 m** for dimensions and datum;
source-to-export bounds must agree within **0.00001 m**.

| Property | Metres, Godot local axes |
| --- | --- |
| Visual size X / Y / Z | **0.900 / 0.780 / 0.600** |
| Visual AABB minimum | **(-0.450, 0.000, -0.300)** |
| Visual AABB maximum | **(0.450, 0.780, 0.300)** |
| Oval head plan | 0.900 × 0.580; long axis X |
| Waist at height 0.500 | 0.360 × 0.340 |
| Anchor plate | 0.680 × 0.080 × 0.600 |
| Amber painted rim | Height 0.715–0.755, integrated material assignment |
| Bolt head | Radius 0.038, height 0.030; four positions X ±0.260 / Z ±0.220 |
| Root and mesh pivot | (0, 0, 0), ground-centred under the plate |
| Static collision box | 0.900 × 0.780 × 0.600, centre (0, 0.390, 0) |

Metric units, unit scale, applied static rotation/scale, no negative scale. Blender
+Z maps to Godot +Y and Blender +Y maps to Godot -Z, with the head length along X.
The two long sides are symmetric; there is no asymmetric functional front. Place
with the long head approximately parallel to a quay edge as a visual convention,
not an authored city placement or a mooring connection API.

The entire footprint is an obstacle. Keep it outside pedestrian through-routes,
loading positions, rail openings and ladder approaches. The brief's **continuous,
unobstructed quay** criterion remains a placement gate, not something an isolated
asset can certify. No boundary, climbing, swimming, rope or boat simulation is added.

## Source, export and materials

- Source: `art/source/models/environment/city_quay_furniture_01/city_quay_furniture_01.blend`.
- Collection: `export_city_quay_furniture_01`.
- Root: `CityQuayFurniture01`; mesh: `CityQuayFurniture01_Mesh`.
- Explicit export: `art/models/environment/city_quay_furniture_01/city_quay_furniture_01.glb`
  and its pinned-engine `.glb.import` sidecar.
- Linked prefab: `scenes/prefabs/environment/city_quay_furniture_01.tscn`.
- Reproduction tools: `tools/asset_production/city_quay_furniture_01/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**; glTF exporter **5.2.40**.
`export.py` reads the shared `tools/assets/blender/export_settings.json`, selects
only the named collection and disables animation/skin export. Studio plane, camera
and lights remain in the source for reproducibility but outside the export scope.
No prototype dependencies, embedded images or runtime-generated render geometry.

One joined static mesh has three opaque, back-culled Principled surfaces:

| Slot | Material | Linear base RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `quay_dark_metal` | (0.025, 0.075, 0.090) | 0.45 | 0.46 |
| 1 | `quay_working_amber` | (1.000, 0.527, 0.102) | 0.00 | 0.42 |
| 2 | `quay_hardware_slate` | (0.115, 0.165, 0.185) | 0.55 | 0.40 |

These stable names and values are a material-language reference for later .02/.03
members, not an additional shared material API. No textures, UV maps, shader code,
external material resources, rigs, clips, sockets or damage states are needed. The
uniform paint requires no UV allocation. Godot's default automatic import LODs,
shadow meshes and compression remain enabled; device performance is unmeasured.

The casting, plate and four bolts are individually closed shells in one mesh.
Casting seats 0.010 m into the plate; bolts seat 0.004 m into it. These concealed
manufactured overlaps are intentional, not non-manifold seams or coincident exposed
surfaces. The cast crown uses continuous smooth normals; a first-render flat-cap
normal break was removed before the final export and all final renders.

## Prefab and bounded engine checks

The prefab preserves the imported model at **`Visuals/Model`, identity transform**,
with no copied mesh, corrective scale/rotation or imported-child override.
`Collision/BollardBody/Shape` is the only collision shape: one static-world box,
layer **1**, mask **0**. It conservatively fills the head/waist/plate envelope instead
of adding snagging bolt or undercut collision. It is an ordinary solid prop, not
visual-only decoration or a continuous waterfront boundary.

The pinned Godot **4.8.dev7.official.c971f93e7** headless check:

- Loads the wrapper and recursively resolves all dependencies and resource UIDs.
- Confirms imported ancestry, identity transform, one mesh, three opaque back-culled
  surfaces and measured bounds matching the literal dimensions above.
- Packs/resaves the wrapper and saved collision-only test fixture, then reloads and
  verifies byte-stable saves. A later fresh process loads the same registered IDs.
- Confirms one separate static body/box and a low ray hit on the actual body; a ray
  above the head is clear.
- Calls production `ActorMotion.step` with the production **radius 0.35 m / height
  1.8 m capsule**, for 48 ticks per case in both AUTHORITY and REPLAY modes. Both
  modes stop at **(0, 0.001, -0.666666329)** and bypass at X=0.95 to
  **(0.949999988, 0.001, 2.000000715)**. Outcomes match exactly between modes.

The nominal contact plane is Z=-0.650 m. Initial testing used a 15 mm symmetric
contact tolerance and failed on the 16.666 mm conservative pre-contact gap. The
final independent expectation rejects **any penetration** and pre-contact gaps
larger than **30 mm**. The collider and production motion were not altered to pass.
This is a bounded public-API actor/query check, not vehicle handling or real
multiplayer transport/admission/prediction acceptance.

The test fixture at `tools/asset_production/city_quay_furniture_01/check_scene.tscn`
contains the linked prefab, production motion script and collision-only floor and
capsule. It adds no visible procedural geometry or world placement. Scene UIDs are
stored inline; the check script's `.gd.uid` is committed.

## Evidence and reproduction

[Hero](city_quay_furniture_01-evidence/hero.png),
[side](city_quay_furniture_01-evidence/side.png),
[crown detail](city_quay_furniture_01-evidence/detail.png),
[47 m / 42° overhead](city_quay_furniture_01-evidence/overhead_47m_42deg.png).
All four are isolated **Blender** renders at **1280×720**, CPU Cycles, 32 samples,
AgX, broad studio fill. The overhead is vertical-down perspective, 47 m above the
zero datum, 42° vertical FOV, Blender +Y image-up. The current common brief's
720-pixel maximum supersedes the historical 1280×800 evidence size. PNGs use seven
significant bits/channel and maximum compression, approximately 344–410 KB each.

All four final views were inspected. The head, narrow amber edge and rounded casting
read cleanly close up; the crown remains a small, restrained oval at gameplay scale.
Anchors are close-view detail rather than required gameplay cues. No giant colour
patch was added to compensate for the camera distance. These views do not substitute
for a Godot lighting/populated-quay review.

Final source/export measures:

- **1,272 source vertices / 1,244 source faces / 2,520 triangles**.
- **1,619 exported vertices / one mesh / three surfaces**.
- **Zero degenerate faces, zero degenerate triangles, zero non-manifold edges**.
- Maximum unit-normal length error: source **1.63e-7**, export **9.50e-8**.
- GLB **70,128 bytes**, fresh re-export **byte-identical**.
- Source and exported bounds, materials, hashes, engine checks and production-check
  results: [validation.json](city_quay_furniture_01-evidence/validation.json).
- SHA-256 of every delivered payload, excluding the self-referential manifest:
  [manifest.json](city_quay_furniture_01-evidence/manifest.json).
- Concise final command receipts: [checks.log](city_quay_furniture_01-evidence/checks.log).

Run from the repository root using Git Bash and the installed mise pins. No owner's
live Blender/Godot session is used. The windowed editor is unavailable under the
production brief, so the wrapper was text-authored and normalized in the headless
engine. No open scene synchronization is claimed or required for these isolated
processes. Scratch logs and fresh exports stay outside the repository.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
NID=city_quay_furniture_01
SCRATCH="C:/tmp/ft/assets/$NID"
mkdir -p "$SCRATCH"

ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 900 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# Optional explicit fresh export; validate.py already performs the byte comparison.
ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy timeout 180 "$BLENDER" \
  -noaudio --background "art/source/models/environment/$NID/$NID.blend" \
  --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/export.py" -- "$SCRATCH/reexport"
python "tools/asset_production/$NID/finalize.py" --compress-renders

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd" -- --normalize
timeout 180 "$GODOT" --headless --path . \
  --script "res://tools/asset_production/$NID/check.gd"
timeout 60 "$(mise which gdstyle)" check "tools/asset_production/$NID/check.gd"
# The output directory must be fresh; use another suffix for a later rerun.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output "$SCRATCH/checks-final"
python "tools/asset_production/$NID/finalize.py" --checks "$SCRATCH/checks-final"
```

Final repository production checks **passed**: owned-script style/format/compilation,
**16 Python tests**, **149 GUT tests / 6,768 assertions**, and the intentional-failure
negative control. The asset-specific GDScript also passes pinned gdstyle 0.3.0.
No known failure exclusion was necessary on this worktree. Logs were inspected:
Blender only reports future-6.0 `use_nodes` deprecation notices; project import emits
the existing MCP toolkit 4.8-versus-tested-4.7 warning. Final asset load/physics logs
contain no errors or warnings. No diagnostic was suppressed or vendor code changed.

## Remaining acceptance

- Supervisor: independent art/technical review at the committed candidate.
- World/layout owner: approve provisional dimensions and actual sparse Old Quay /
  East Docks placement, keeping paths, loading positions and access openings clear.
- Gameplay owner: actual vehicle contact/turning and real multiplayer movement/query
  checks against chosen placements; the simplified undercut envelope remains explicit.
- Art/integration owner: actual engine lighting and gameplay-camera/readability review
  in populated quay scenes. Do not claim Blender studio views as engine captures.
- Device/performance owner: repeated-placement, packaged-build and sustained Deck
  profiling. Triangle counts and headless checks are not a performance budget.

No shared asset-generation helper was introduced: the existing shared export settings,
production-check runner and production motion API are reused; the required per-ID
construction, measurement and scene checks stay local. No source/export/prefab work is
blocked; these downstream acceptance items remain deliberately pending.
