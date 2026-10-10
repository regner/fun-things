# city_barriers.06 — Chain-link post/bracing set

10 October 2026. **Source/export and linked prefabs delivered; independent review and
world/gameplay acceptance pending.** Produced by the commissioned implementation
specialist on `lane/a-barriers`, starting from `31cc666d`. The current task/common
brief supersedes historical concept-only and lead-only integration restrictions in
[commission](commission.md). Family: [city_barriers](../city_barriers.md).
No sibling, shared register/progress record or world placement was changed.

## Design and dimensions

Original Blender construction: a common narrow galvanised capped post with three
levels of annular panel clamps, a slightly flared ground shoe and restrained oxide
at its base. **Line, terminal and corner** variants provide opposing, single and
right-angle clamp directions. Terminal/corner variants have slender diagonal
braces and small chamfered anchor plates. Corner brace attachments are staggered
vertically to avoid intersecting rods. No barbed wire, logos, gates, hinges,
interaction, destruction state or material-variation system was added.

Direction follows Petrol & Coral, approved district identities/Stage 4 route
constraints and the [Ironreach revision 02](../../concepts/districts-v1/ironreach.md).
The `.01` bollard, `.03` separator and `.05` panel records/tools/evidence were read.
The chain-link finishes and mounting pitch match `.05`, rather than duplicating the
painted bollard or quay-rail language. `.02`/`.04` have no delivered files here and
are not dependencies of this distinct chain-link system.

All dimensions below are **provisional authored choices** under the standing
production rules, not image-derived measurements or approved yard placements.
Godot axes are width X / height Y / depth Z, in metres:

| Variant | Visual dimensions X/Y/Z | AABB minimum | AABB maximum |
| --- | --- | --- | --- |
| Line | 0.210 / 2.160 / 0.096 | (-0.105, 0, -0.048) | (0.105, 2.160, 0.048) |
| Terminal | 0.998 / 2.160 / 0.158 | (-0.048, 0, -0.110) | (0.950, 2.160, 0.048) |
| Corner | 0.998 / 2.160 / 0.998 | (-0.048, 0, -0.950) | (0.950, 2.160, 0.048) |

- Common shaft diameter **0.080 m**, shoe diameter **0.096 m**, cap diameter 0.088 m.
  Cap top is **2.160 m**, 0.060 m above the panel's inherited 2.100 m top datum.
- Root and mesh origins `(0,0,0)` are the **main post's ground-contact centre**,
  not the asymmetric bracing footprint centre. Foot plates also contact Y=0.
- Metre units, unit scale and identity transforms. Blender +Z → Godot +Y;
  Blender +Y → Godot -Z. No corrective prefab scale or rotation.
- Clamps at Y=**0.400, 1.100, 1.800 m**. Panel-side annular bands: outer diameter
  0.060 m, bore diameter 0.051 m, height 0.040 m. This leaves 0.0005 m radial
  clearance around the delivered 0.050 m frame tube. Short stamped tabs join bands
  to post collars; the panel does not float in an unsupported mounting gap.
- Braces: diameter **0.026 m**, horizontal reach **0.900 m**, main attachment at
  Y=1.720 m; corner return attachment at Y=1.560 m. They sit 0.065 m to the inside
  of the respective fence plane, clear of its wire/tie envelope. Each toe has a
  0.100 × 0.090 m plan plate, 0.030 m high, and a small closed mounting socket.
- Envelope/datum tolerance ±0.001 m; source/GLB agreement tolerance 0.00001 m.

### Panel interface and `.07` handoff

Use one post at each **3.100 m** panel-centre interval. At a post origin:

| Variant | `.05` panel-centre placement in Godot | Panel rotation about +Y |
| --- | --- | --- |
| Line | (-1.550, 0, 0) and (1.550, 0, 0) | 0° each |
| Terminal | (1.550, 0, 0) | 0° |
| Corner | (1.550, 0, 0) and (0, 0, -1.550) | 0° and +90° |

Panel outer edges are 0.050 m from the post centre; its side-tube centrelines align
with the clamp bores at X=±0.075 m or Z=-0.075 m. The inherited 0.100 m panel underside
clearance is unchanged. Rotate the whole terminal/corner prefab to turn a run; never
mirror with negative scale, stretch panels or double up shared posts. Braces point
**into panel bays**, not into the vehicle opening or foot bypass. Leave their small
inside setback clear of actors; this is not a permission to narrow an approved route.

`.07` can reuse the 2.100 m panel top, 0.050 m frame tubing and the same finishes.
This component provides fence support clamps, **not gate hinge/latch hardware**.
A gate's own fittings, sweep/width and opening clearance remain its owner's work.
The required full straight/corner/terminal/open-paired-gate review remains pending
until `.07` exists. Preserve two main-yard vehicle openings, a pedestrian bypass
and the public boardwalk; no district-wide enclosure or final placement is implied.

## Source, exports and materials

- Source: `art/source/models/environment/city_barriers_06/city_barriers_06.blend`.
- Collections: `export_city_barriers_06_line`, `export_city_barriers_06_terminal`,
  `export_city_barriers_06_corner`.
- Roots: `CityBarriers06_Line`, `CityBarriers06_Terminal`, `CityBarriers06_Corner`;
  corresponding children end in `_Mesh`, editable mesh datablocks in `_Geometry`.
- Explicit exports: `art/models/environment/city_barriers_06/city_barriers_06_{line,terminal,corner}.glb`
  with the engine-generated `.import` sidecar for each.
- Tools: `tools/asset_production/city_barriers_06/{author,export,validate,finalize}.py`.
  Export consumes the shared `tools/assets/blender/export_settings.json` unchanged.
- One mesh per variant, constructed from closed lathed/swept shells and chamfered
  stamped tabs/plates. Intentional collar/post, tab/band and stud/brace/socket
  intersections represent fastened joints; this is not a Boolean-fused solid.
  Annular clamp bores are genuine voids. Topology checks apply to each closed shell.
- Saved export roots all stay at the origin: isolate the desired collection when
  inspecting the source. Evidence-only translations separate the three variants;
  those translations are applied after saving/exporting and never enter GLBs.
  Studio ground, lights and camera are outside the export collections.

Three opaque, backface-culled Principled material slots, matching `.05` **exactly**
(the validator compares actual GLB material dictionaries, not just their names):

| Slot | Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `fence_galvanised_frame` | (0.320, 0.380, 0.390) | 0.70 | 0.48 |
| 1 | `fence_galvanised_wire` | (0.190, 0.250, 0.260) | 0.60 | 0.55 |
| 2 | `fence_joint_oxide` | (0.160, 0.065, 0.026) | 0.05 | 0.84 |

The existing darker wire finish is reused on clamps/sockets. Oxide is confined to
small base/socket face bands; no noisy procedural grime or separate rusted model.
No textures, embedded images, UV maps, transparency, emission, rigs, animations,
exported sockets or damage states. Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF
exporter **5.2.40**. No explicit LOD; per-asset default Godot generated LOD/shadow-mesh/
compression settings remain unchanged. Actual repeated-kit/LOD cost remains unmeasured.

## Prefabs and collision

| Variant | Prefab under `scenes/prefabs/environment/` | Scene UID | GLB UID |
| --- | --- | --- | --- |
| Line | `city_barriers_06.tscn` | `uid://d0pw6qm0w13pi` | `uid://b3lxqm7b8ku0v` |
| Terminal | `city_barriers_06_terminal.tscn` | `uid://dav2qiky7duwa` | `uid://g0faayq13w8q` |
| Corner | `city_barriers_06_corner.tscn` | `uid://bd7hewksepxje` | `uid://dlwltujqdjt84` |

Each wrapper instances its imported GLB at **`Visuals/Model`, identity transform**.
No embedded replacement meshes or runtime-authored hierarchy. Text-authored scenes
were loaded/packed/resaved with isolated pinned headless Godot. No live Blender/Godot
MCP session was contacted; no separate open-editor synchronization is claimed.
Scene UIDs live in headers, and the check script's generated `.uid` is retained.

Standing collision rule: each support has **one** separate
`Collision/PostBody` StaticBody3D, layer **1**, mask **0**, with a minimal compound:

| Shape | Used by | Size X/Y/Z | Centre X/Y/Z |
| --- | --- | --- | --- |
| `Post` | all | (0.210, 2.160, 0.210) | (0, 1.080, 0) |
| `BraceX` | terminal/corner | (0.950, 1.760, 0.090) | (0.475, 0.880, -0.065) |
| `BraceZ` | corner | (0.090, 1.600, 0.950) | (0.065, 0.800, -0.475) |

These deliberately conservative boxes enclose fittings and close the triangle under
each brace, as thin blocking fence planes, instead of snag-prone diagonal cylinders.
The common post box overestimates the bare shaft by up to 0.065 m per side; braces
must stay in fence bays. The **inside corner is not filled by a broad box**. This
static-world query filtering is consistent with `.05`; visual openness does not
establish bullet/aim pass-through, removability, opening or replicated destruction.

Saved fixture `tools/asset_production/city_barriers_06/check_scene.tscn` instances
all three supports, a complete two-panel straight run, and a two-panel right-angle
fit using the unchanged `.05` prefab. It includes production `ActorMotion` with
r=0.35 m / h=1.8 m capsule and a collision-only floor. No visible floor asset or
world placement was added. `check.gd` asserts saved resource/import identities,
actual imported bounds/materials/colliders, panel alignment and physical outcomes.

## Validation and evidence

[Hero](city_barriers_06-evidence/hero.png) · [side](city_barriers_06-evidence/side.png) ·
[clamp/brace detail](city_barriers_06-evidence/detail.png) ·
[47 m / 42° overhead](city_barriers_06-evidence/overhead_47m_42deg.png).
Four isolated Blender CPU Cycles views at **1280×720**, six significant bits/channel,
PNG compression 9. The current common brief's 720-pixel maximum supersedes the older
1280×800 example. Overhead is vertical-down perspective, north-up, **47 m height /
42° vertical FOV**, without cropping or enlarging the geometry.

Producer inspected all four final views. Hero/side read as quiet galvanised supports;
corner, terminal and line appear left-to-right. The detail shows genuine clamp bores,
flat annular rims and staggered brace studs. At calibrated overhead distance the
post caps are tiny dots, the clamps are unresolved and braces are faint short lines.
These supports are intentionally subordinate to the panel/run, not independent
wayfinding. Actual populated-street lighting/actor visibility, wire shimmer, engine
LOD behavior and moving-camera readability remain unproved.

Measured [validation.json](city_barriers_06-evidence/validation.json):

| Variant | Source vertices | Source faces | Triangles | Export vertices | Closed shells | GLB bytes |
| --- | --- | --- | --- | --- | --- | --- |
| Line | 976 | 922 | 1,924 | 1,968 | 16 | 61,568 |
| Terminal | 832 | 752 | 1,632 | 1,648 | 14 | 52,148 |
| Corner | 1,264 | 1,122 | 2,468 | 2,576 | 24 | 79,432 |

- Each variant: **one mesh / three surfaces; zero degenerate faces/triangles and
  zero non-manifold edges**, finite coordinates and unit-length source/GLB normals.
  All source and actual binary GLB bounds agree within tolerance; positive closed volume.
- Actual Blender BVH rays confirm an open clamp bore and a solid post. The two
  corner brace surfaces have **zero intersections** after attachment staggering.
- Every exported material dictionary matches the actual sibling panel GLB.
- **All three fresh re-exports from the saved `.blend` are byte-identical**.
  Each GLB contains exactly root plus mesh; no camera/light/texture/animation payload.
- Godot **4.8.dev7.official.c971f93e7** imports and loads dependencies. Linked identity,
  imported bounds/surface properties, registered UIDs and four-scene roundtrip pass.
  Two fresh standalone normalization processes preserve all scene bytes and IDs.
- Low rays hit all posts, above-cap rays clear, both brace directions block and an
  interior-corner ray passes. Straight and right-angle panel/post seams have no
  layer-1 ray gap at the tested locations. Panel tube/clamp-centre alignment passes.
- Production `ActorMotion.step`, 48 ticks per contact/bypass case per authority/replay
  mode, all three variants: post contact stops at **Z=0.455729 m**, clear bypass ends
  at **Z=-2.000001 m**. Both modes match. This is local simulation parity, **not
  network transport/prediction or vehicle clearance acceptance**.
- Initial canonical production checks pass in full. The final run after the UID-saver
  fix passes owned GDScript formatting/lint/compilation, **14/14 Python tests and
  119/119 GUT tests, 6,362 assertions**; the diagnostic negative test correctly returns 1.
  **Final aggregate exit is 1**: the shared compiler's cumulative 120-second deadline
  expires before 12 unrelated `tools/assets/` scripts can run. Their logs contain only
  `CHECK DEADLINE EXCEEDED`; no asset script failed. Exact skipped paths remain in
  validation.json. This environment/check-budget limitation is not suppressed, and
  the unchanged failed aggregate was not rerun.

[final.log](city_barriers_06-evidence/final.log) is the concise command/diagnostic
receipt. Initial visual self-review found intersecting corner braces and smooth
annular end shading: both were corrected before final source validation. Initial
same-process normalization passed but a later process exposed UID-cache drift;
the saver now preserves the saved scene header's identity, followed by reimport and
two fresh-process byte-stability checks. No sibling IDs/files were changed. Blender
emits only future-6.0 `use_nodes` deprecation notices; headless import emits the
existing MCP addon 4.8-versus-tested-4.7 warning. Final standalone checks have no
source/resource/physics errors. Raw logs and scratch exports remain outside Git.
The [manifest](city_barriers_06-evidence/manifest.json) hashes all delivered payloads,
including source, tools, metadata, four renders and this record; it excludes itself.

## Exact reproduction

From the repository root in Git Bash with pinned tools installed:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
mkdir -p C:/tmp/ft/assets/city_barriers_06

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_06/author.py
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_06/validate.py
# Optional explicit export, independently of validation:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  art/source/models/environment/city_barriers_06/city_barriers_06.blend \
  --python tools/asset_production/city_barriers_06/export.py \
  -- C:/tmp/ft/assets/city_barriers_06/reexport

timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/city_barriers_06/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . \
  --check-only --script res://tools/asset_production/city_barriers_06/check.gd
timeout 30 "$GDSTYLE" fmt --check tools/asset_production/city_barriers_06/check.gd
timeout 30 "$GDSTYLE" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/city_barriers_06/check.gd
# Requires a fresh output directory; retain prior runs outside the checkout.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/city_barriers_06/checks
python tools/asset_production/city_barriers_06/finalize.py
```

`author.py` recreates source/export/renders. `validate.py` replaces validation.json;
run the Godot check afterward, then finalize to retain all sections. Do not rewrite
source or identities merely to inspect existing results. Finalization requires
passing owned checks; it preserves and narrowly classifies the external compiler
deadline failure above rather than reporting overall success. It compacts renders
before hashing the delivery.

## Remaining acceptance

Independent technical/art review is pending. Dimensions/spacing remain provisional.
Full-kit open-gate review awaits `.07`. World integration owns final fence runs,
entrance setbacks, two vehicle openings, foot bypass, boardwalk, actor/target
visibility and actual engine camera captures. Vehicle contact/turning/clearance,
real separate-process multiplayer transport/admission/prediction, packaged target
devices, Deck readability and sustained rendering/LOD/load performance remain
**unperformed**. The final global compiler deadline needs a complete downstream
canonical recheck in a sufficient execution window. No gameplay rule, road geometry,
world scene or shared tracker changed.
