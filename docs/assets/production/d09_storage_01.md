# d09_storage.01 — Long container

**Production source/export, linked prefab and bounded checks delivered; independent
review, world placement and gameplay/device acceptance pending.** Commissioned by
Regner under [the production commission](commission.md) and the current per-asset
lane brief, superseding the older concept-only restriction.

Producer: commissioned implementation specialist, branch `lane/a-storage`.
Accepting owners: independent art/technical reviewers, then world/gameplay/device
owners. Original Blender construction only; no downloads, real brands, generated
image-to-mesh content, external textures or runtime-authored geometry. References:
[storage family](../d09_storage.md), [East Docks](../../concepts/districts-v1/east-docks.md),
and [district identities](../../concepts/world-v1/stage-03-district-identities/README.md).
No earlier storage sibling existed in this lane when this member was authored.

## Design and dimensions

One long, low blue/slate freight container, with continuous trapezoidal side and
roof corrugation, eight softly bevelled corner castings, a perimeter steel frame,
closed paired end doors, four restrained locking bars and two small blank amber
identification faces. The broad quiet roof remains subordinate to the existing
warehouse/crane silhouettes. All doors are static; no interior, cargo inventory,
opening state, movable stack, rig, socket, animation or destruction mechanic.

Dimensions are **provisional authored choices**, not measurements from generated
concept art or approval of a district arrangement. No container stack or maze is
included. The 30 m² footprint is not an allocation of the 5.03 ha district.

| Contract | Metres, Godot local coordinates |
| --- | --- |
| Visual size X / Y / Z | **2.500 / 2.600 / 12.000** |
| Visual AABB minimum | **(-1.250, 0, -6.000)** |
| Visual AABB maximum | **(1.250, 2.600, 6.000)** |
| Root / mesh pivot | (0,0,0), ground-centred footprint |
| Closed door front | -Z; Blender +Y converts once to Godot -Z |
| Long-axis direction | Z; Blender Y |
| Side corrugated face height | Y=0.200–2.400 |
| Long side / roof corrugation | 24 folds across 11.640 m, pitch 0.485, depth 0.045 |
| Closed door leaves | Each 1.055 wide × 2.200 high |
| Corner castings | 0.240 × 0.240 × 0.240 |
| Bound / ground-datum tolerance | ±0.001 |

Metre units, applied static rotation/scale, identity roots and no corrective
wrapper rotation or scale. Corners contact ground at Y=0. The raised belly is
closed geometry, not a crawl space. Individual manufactured shells intersect
at intended joints; they are not a Boolean-unioned watertight assembly.

### Family and artwork interface

The `build_container(length=12.0)` recipe owns this cross-section, corner-post,
closed-door and corrugated-panel language. Subsequent container work can reuse
this authored recipe with an explicitly chosen length rather than copying a
private primitive library or uniformly scaling the long mesh. Reuse the four
material names below; this document does not allocate other family outputs.

Identification backing is already included on each long side. Only the outward
**1.400 × 0.460 m** quad on each backing uses `storage_id_face` (surface **3**, zero
based). The two quad centres are **(±1.230, 1.960, -4.650)**, outward normals ±X;
Y range **1.730–2.190**, Z range **-5.350–-3.950**. UV0 fills 0–1 per quad, upright
and left-to-right from outside either side. Backing and edge faces remain in the
steel slot; validation asserts exactly four exported artwork triangles and unit
UV corners. This is the carrier seam for [freight graphics](../d09_freight_graphics.md),
not new artwork, selected copy, essential overhead wayfinding or a gameplay ID.
The current prefab has no imported-child overrides. Later artwork can use the
recorded face-slot-only reuse exception in [assets](../../assets.md#prefabs-and-authored-placement)
with its own stable save/reload evidence, without duplicating this carrier.

## Source, exports and materials

- Source: `art/source/models/environment/d09_storage_01/d09_storage_01.blend`.
- Export collection: `export_d09_storage_01`.
- Root / mesh: `D09Storage01` / `D09Storage01_Mesh`.
- Export: `art/models/environment/d09_storage_01/d09_storage_01.glb` plus `.import`.
- Linked wrapper: `scenes/prefabs/environment/d09_storage_01.tscn`.
- Author/export/validator, saved check scene, GDScript check and finalizer:
  `tools/asset_production/d09_storage_01/`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
`export.py` loads `tools/assets/blender/export_settings.json`, filters the named
collection, and disables skins/animations. Studio cameras, lights and ground are
outside the export. The saved source retains editable meshes; `author.py` retains
the parametric construction. Bevels and weighted normals are applied before save.

One mesh, four opaque, back-culled Principled material surfaces, ordered:

1. `storage_body_blue` — large folded blue steel fields; linear RGB (.055,.135,.235).
2. `storage_frame_slate` — perimeter frame, posts and door recess; (.055,.085,.120).
3. `storage_hardware_steel` — castings, hinges and locking bars; (.240,.300,.340).
4. `storage_id_face` — sparse blank amber face only; (.950,.520,.150).

Exact metallic/roughness values are in validation.json. No textures, embedded
images, emission, transparency or material remapping. Default Godot automatic LOD
and shadow meshes remain enabled. Fold bevels and closed cap strips account for
most mesh density; no numerical triangle budget was supplied. Repeated-placement
cost and LOD transitions remain unmeasured, not accepted by a small file size.

## Prefab and collision

`Visuals/Model` is an identity-transform imported GLB instance with one mesh and
four surfaces. There are no copied mesh arrays, imported-child edits or runtime
node construction. `Collision/Body/Shell` is a direct CollisionShape3D child of one
StaticBody3D: BoxShape3D **(2.5,2.6,12)** at **(0,1.3,0)**, static-world layer **1**,
mask **0**. The deliberate whole-container envelope closes small corrugation and
frame recesses without snagging on individual bars. It matches the full bounds,
with no corner gaps or external protruding collider. Main side sheets sit at most
0.10 m inside the envelope; rear steel at most 0.13 m inside it. No interior or
rooftop traversal is introduced; the top is merely part of the closed solid box.

Godot scene UID `uid://bqm0xefctop4r`; model import UID `uid://bv4lwewpy085p`.
Two byte-stable load/pack/save/reload roundtrips preserved scene bytes and node
identities. A subsequent pinned import and separate fresh-process check resolved
all dependencies and UIDs. Per the brief, scene text was authored directly and
normalized headlessly; the unavailable windowed editor and owner's live sessions
were not used or synchronized by these checks.

## Evidence and validation

[Hero](d09_storage_01-evidence/hero.png) ·
[side](d09_storage_01-evidence/side.png) ·
[door detail](d09_storage_01-evidence/detail.png) ·
[47 m / 42° overhead](d09_storage_01-evidence/overhead_47m_42deg.png).

All are isolated **Blender Cycles CPU, 32 samples, AgX, 1280×720** renders, not
Godot captures. The overhead is vertically down, north-up, at (0,0,47) in Blender,
42° vertical perspective FOV. The current 720-pixel evidence cap supersedes the
older 800-pixel render request. Evidence PNGs use six significant bits/channel
and maximum compression; runtime materials are not color-reduced.

The producer inspected all four final images. The long blue rectangle and broad
roof folds remain identifiable overhead; small side labels intentionally do not
read from above. The low mass does not become a landmark, though in-context
subordination, repeated-pattern density and actor occlusion require placement
review. Studio background quantization is evidence compression, not asset texture.

Final numbers are copied from [validation.json](d09_storage_01-evidence/validation.json):

- **10,168 source vertices; 20,100 triangles; 11,074 exported vertices** including
  normal/material splits. **1 mesh, 4 surfaces**.
- **0 degenerate source faces/triangles, 0 degenerate GLB triangles,
  0 non-manifold source edges**; unit-length source and export normals pass.
- Maximum normal-length error: source **1.639127598e-7**, export **1.1552321454e-7**.
- Source bounds, actual GLB binary positions and engine AABB agree within 0.001 m.
- Fresh source re-export is byte-identical: **479,048 bytes**, SHA-256
  `f3140a621c96f5ab2ecc17ec91dafa53b589d5e9ad5a9a151eba242c5d091876`.
- Three front rays (centre and near both corners) hit the actual saved container
  body at Z=-6; the ray above the roof clears.
- Production `ActorMotion.step` capsule **r=0.35 m, h=1.8 m**, 192 ticks per case:
  authoritative and replay contact both stop at **Z=-6.350257396698**; clear side
  bypass at X=2 ends at **Z=8.00001239776611**. No networking claim follows.
- A provisional **1.8×1.5×4.4 m** car-box physics cast hits the front (safe fraction
  **0.0899658203125**); bypass at X=2.3 clears (safe fraction **1.0**). This is not
  actual driving, turning or vehicle-controller acceptance.
- Pinned imports and fresh-process check exit 0 with no ERROR/SCRIPT ERROR lines.
  `gdstyle fmt --check` and lint at max line length 100 / zero warnings pass.

Initial self-review corrected coplanar frame/casting overlap. A first topology
check then rejected seven zero-area triangles from concave corrugation-cap
triangulation; quad-strip caps corrected them without weakening checks. Initial
GDScript lint findings were resolved by extracting the car-envelope check. The
Windows shell did not expose `gdstyle` directly, so validation uses `mise which`.
Blender emits forward-looking `use_nodes` deprecation notices; import emits the
existing MCP toolkit 4.8-versus-tested-4.7 warning. No addon changes or broad error
suppression. Scratch/retry logs are outside the repository. A concise final
[check log](d09_storage_01-evidence/final-checks.log) and final
[producer manifest](d09_storage_01-evidence/manifest.json) retain current evidence.

## Exact reproduction

Run from this worktree root in Bash. Every Blender call is isolated with the
pinned CLI; all engine invocations are headless. Authoring regenerates source and
renders, so do not run it over unrelated unsaved source work.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy

timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_01/author.py
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python tools/asset_production/d09_storage_01/validate.py
# Validator opens the saved source and reexports to C:/tmp/ft/assets/d09_storage_01/reexport.
python tools/asset_production/d09_storage_01/finalize.py --compress-renders

timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_01/check.gd -- --normalize
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --path . \
  --script tools/asset_production/d09_storage_01/check.gd
"$GDSTYLE" fmt --check tools/asset_production/d09_storage_01/check.gd
"$GDSTYLE" --max-line-length 100 --max-warnings 0 tools/asset_production/d09_storage_01/check.gd
python tools/asset_production/d09_storage_01/finalize.py
```

No `tools/production_checks.py` run: owner decision 52 keeps unplaced-asset
validation bounded to its source, imports, prefab and owned checks. The manifest
hashes every produced payload except itself; shared export settings are listed as
a read-only dependency. Reproduction must update this handoff's receipt values
and concise log if a later source revision changes them, then regenerate the
manifest last.

## Remaining acceptance

- Independent art/technical acceptance of this exact candidate.
- Saved district placement with sparse low groups at loading edges; keep the open
  crane apron, service spur and ordinary street footways clear. No stack-height
  acceptance or arrangement is implied by this single ground-level prop.
- Actual engine-camera appearance, actor/target occlusion and LOD transitions in
  context; this source-view check does not accept whole-district readability.
- Actual vehicle driving/turning, network transport/admission/prediction and
  collision lifecycle implications in the integrated world.
- Packaged-platform/Deck and repeated-placement GPU/frame-time performance.

No register/progress/shared brief/world scene was changed, no TODO was closed,
and no whole-city or full game-ready acceptance is claimed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
