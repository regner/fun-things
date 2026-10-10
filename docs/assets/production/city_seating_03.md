# city_seating.03 — Corner seat

10 October 2026. **Source/export and bounded headless prefab checks delivered;
independent review and world/gameplay acceptance pending.** Commissioned specialist:
`worker` on `lane/a-seating`. The active asset-production common brief supersedes
historical concept-only and lead-only integration/Git restrictions in the
[commission](commission.md) and [family brief](../city_seating.md). No shared register,
progress, sibling, project or world files changed.

## Design and dimensions

An original backless L-shaped civic seat: one continuous ivory slab turns around
an open corner, with a recessed petrol rim and a continuous slate L plinth. Each
layer is a single closed extruded outline, not overlapping rectangular benches:
there is no diagonal seam across the elbow. Three-segment roundovers and weighted
normals match the [straight bench](city_seating_01.md) and
[short plaza seat](city_seating_02.md), using their exact named palette, .46 m seat
top and .09 m slab thickness. The open L silhouette differentiates this member
without extra colours, slats, fasteners, logos or texture noise. All visible asset
geometry is original pinned-Blender construction; no downloads, brands, external
art, image-to-mesh or runtime-generated geometry.

The low, quiet silhouette follows the [approved district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md), especially
communal courts and restrained forecourt furniture. District uses remain candidates;
this is not a newly selected Signal Row starting prop. Keep passage mouths,
intersection corners and car exits clear. No district placements or quantities chosen.

Dimensions are **provisional authored values**, not measurements from concept imagery:

| Measurement | Metres |
| --- | --- |
| Godot width X / height Y / depth Z | 2.10 / .46 / 2.10 |
| Whole visual AABB minimum | (-1.05, 0, -1.05) |
| Whole visual AABB maximum | (1.05, .46, 1.05) |
| Equal outer arm lengths / seat width | 2.10 / .65 |
| Seat top / slab thickness | .46 / .09 |
| Nominal clear notch width / depth | 1.45 / 1.45 |
| Petrol rim perimeter inset / bottom / top | .04 / .33 / .375 |
| Slate plinth perimeter inset / bottom / top | .10 / 0 / .34 |
| Seat / rim / plinth edge roundover | .035 / .018 / .045 |
| Nominal occupied plan area | 2.3075 square metres |

Acceptance tolerance: .001 m for bounds, datum and pivot. Root and mesh origins
(0,0,0) are at the ground plane beneath the **bounding-footprint centre**. Because
this footprint is concave, that centre lies in the open notch, not in the plinth;
the entire plinth bottom lies at Y=0. The rear arm runs across X at Godot Z=.40 to
1.05; the left arm runs along Z at X=-1.05 to -.40. The notch opens toward +X/-Z.
Blender +Y maps to Godot -Z, +Z to +Y, with metric units and applied transforms.
The inner roundover extends slightly into the nominal sharp notch (within .035 m).
Small hidden vertical overlaps connect the three layers without coplanar surfaces.

Static intact dressing only: no sitting interaction, rigs, animation, sockets,
destruction or interiors. No automatic placement/route or seating system introduced.

## Source, export and materials

- Source: `art/source/models/environment/city_seating_03/city_seating_03.blend`.
- Named export collection `export_city_seating_03`; root `CitySeating03`, mesh
  `CitySeating03_Mesh`. Three closed components joined into one mesh; no saved
  studio geometry, cameras or lights in source/export.
- Export: `art/models/environment/city_seating_03/city_seating_03.glb` plus its
  retained `.glb.import` identity. One output, no additional variants.
- Tools: `tools/asset_production/city_seating_03/`: parametric `author.py`, explicit
  `export.py`, source/binary `validate.py`, isolated `render.py`, `check.gd`, saved
  `physics_check.tscn` and `manifest.py`. Asset-specific checks follow the sibling
  conventions; export settings and canonical production checks reuse shared tools.

Three opaque, backface-culled Principled surfaces, actual exported slot order:

| Slot | Name | Linear base RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `seating_ivory` | (.82, .80, .67) | 0 | .48 |
| 1 | `seating_petrol_trim` | (.045, .10, .115) | .35 | .40 |
| 2 | `seating_slate` | (.23, .30, .34) | .15 | .48 |

No textures, embedded images, material remaps or overrides needed. No UV-dependent
finish. Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; export
loads `tools/assets/blender/export_settings.json`, filters the named collection and
disables skins/animations. Modifiers baked before saving; glTF triangulates.
Godot **4.8.dev7.official.c971f93e7** imports at scale 1 with default generated LODs
and shadow meshes. No manual LOD or repeat-placement performance claim.

## Prefab and collision

`scenes/prefabs/environment/city_seating_03.tscn` retains the linked imported model
at identity-transform `Visuals/Model`; no embedded mesh or runtime node composition.
Prefab UID `uid://dq82gdbg6jfwn`; import UID `uid://cn6g88dqtdf6t`. Pinned headless
normalization generated saved node identities and resource dependency UIDs. Scene
UIDs live in headers; the generated `check.gd.uid` sidecar is retained.

One static-world body at `Collision/Body`, layer 1 / mask 0, owns a minimal two-box
compound, separate from the visuals:

| Shape | Size X/Y/Z | Centre X/Y/Z |
| --- | --- | --- |
| `RearArm` | (2.10, .46, .65) | (0, .23, .725) |
| `LeftArm` | (.65, .46, 1.45) | (-.725, .23, -.325) |

Boxes meet at Z=.40 and continuously cover the L top without filling its open notch.
They deliberately fill the shallow plinth recess under the slab, avoiding snaggy
bevel/rim collision. The tiny inner roundover is not reproduced by collision.
Air above .46 m stays clear. Test fixture floor is collision-only; no new visible
floor mesh or world placement. A radius .35 m / height 1.8 m capsule exercises the
production `ActorMotion.step` API, not copied movement rules.

## Evidence and validation

[Hero](city_seating_03-evidence/hero.png), [side](city_seating_03-evidence/side.png),
[elbow/rim/plinth detail](city_seating_03-evidence/detail.png),
[47 m / 42° overhead](city_seating_03-evidence/overhead_47m_42deg.png).
All are isolated Blender Cycles CPU renders, 32 samples, denoising, AgX, 1280×720
maximum; RGB 7-bit-per-channel quantization and PNG compression 9 keep each below
400 KiB. Overhead is actual vertical-down perspective at 47 m height / 42° vertical
FOV, fixed north-up. The active cleanliness rule supersedes historical 1280×800
evidence sizing. Studio lighting is not a city-lighting or engine result.

Self-inspection of all four views: broad continuous top and inset base fit the
siblings. The elbow remains continuous, with a small manufactured inner bevel
junction visible only in the detail crop. At gameplay scale the roughly 43×43-pixel
L remains distinct from either straight member and visibly leaves the notch open;
trim detail appropriately recedes. No render changes were needed after inspection.
Actual populated engine readability, especially on pale paving, remains pending.

[validation.json](city_seating_03-evidence/validation.json) records:

- **852 triangles, 432 source vertices, 432 exported vertices, one mesh, three
  surfaces; GLB 14,524 bytes.**
- Zero degenerate faces/triangles and zero non-manifold edges; consistent winding,
  positive source volume, finite source coordinates, unit source/export normals.
- Source, actual binary GLB and imported engine bounds agree within .001 m; datum
  zero and identity local object/model transforms.
- Fresh-process re-export is **byte-identical**; GLB SHA-256
  `781fde877b3b673960f23c8e53ce0547f3f59fc1f8ea90888685b9dbfc2460a9`.
- Headless import/load, dependency UID resolution, opaque back-culled materials and
  byte-stable prefab/fixture save/reload pass.
- Five physics rays: solid rear arm, left arm and elbow seam at Y=.46; empty notch
  and clear air above the seat.
- Ten 60-tick actor cases: authority and replay each contact the rear arm from the
  inside (Z=.049935 m), left arm from inside (X=-.049935 m), rear from outside
  (Z=1.400065 m), bypass at X=1.55 m to Z=3 m, and leave the open notch to Z=-5.4 m.
  Corresponding authority/replay outcomes match. These are local simulation checks,
  **not multiplayer transport or vehicle contact acceptance**.
- Canonical production checks all pass: owned-script formatting/style/compilation,
  14 Python tests, GUT 86/86 tests (2,178 assertions), and expected negative-test
  failure detection. No pre-existing failure exemptions used.

Initial source validation incorrectly required all inner-corner vertices to stay
outside the sharp notch, overlooking the explicit .035 m concave roundover. The
check now allows only that roundover while rejecting a bridge across the notch;
no geometry or dimension was changed to bypass the check. The initial script-length
lint warning was resolved by separating ray queries from movement checks.

Diagnostics: pinned Blender reports Material/World `use_nodes` deprecation notices.
Headless import/normalization reports the MCP plugin's 4.8-version warning, and
normalization shutdown emits RID/ObjectDB leaks as in both siblings. Assertions
pass, but this is not a clean-editor-log claim. Standalone asset checks and canonical
production checks have no new error/warning diagnostics. No owner live session was
accessed; no windowed synchronization or inherited-scene roundtrip is claimed.
Raw logs remain outside the repository under `C:/tmp/ft/assets/city_seating_03/`.

## Exact reproduction

From repository root in Bash; scratch output stays outside the checkout. No live
MCP connection or windowed editor; all engine calls are timeout-bounded.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
ASSET=city_seating_03
TOOLS=tools/asset_production/$ASSET
TMP=C:/tmp/ft/assets/$ASSET
mkdir -p "$TMP"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/author.py"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/export.py"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/export.py" -- "$TMP/reexport"
timeout 180 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/validate.py" -- "$TMP/reexport/$ASSET.glb"
timeout 900 "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python "$TOOLS/render.py"
timeout 300 "$(mise which godot)" --headless --editor --path . --import --quit
timeout 180 "$(mise which godot)" --headless --editor --path . --script "res://$TOOLS/check.gd" -- --normalize
timeout 180 "$(mise which godot)" --headless --path . --script "res://$TOOLS/check.gd"
"$(mise which gdstyle)" fmt --check "$TOOLS/check.gd"
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$TOOLS/check.gd"
# Canonical checks require a fresh empty output directory on subsequent reviews.
timeout 1800 mise exec -- python tools/production_checks.py --output "$TMP/checks"
python "$TOOLS/manifest.py" "$TMP/checks"
```

The last command compacts renders, attaches render/check receipts to validation.json
and hashes every produced payload except the manifest itself.
[manifest.json](city_seating_03-evidence/manifest.json) is producer evidence, not an
independent acceptance verdict.

## Remaining acceptance

Independent art/technical review remains pending. World integration owns final
district need, placements, street-furniture zones, passage/car-exit clearance and
physics/aim behavior in context. Vehicle contact/turning, real-process multiplayer
collision/transport/prediction, populated engine-camera readability, package/device
checks and repeated-placement GPU/frame cost remain unperformed. No whole-register
READY, world-placement, Deck/performance or sitting-interaction claim.
