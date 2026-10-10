# city_barriers.05 — Chain-link panel

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay acceptance pending.** Produced by the commissioned implementation
specialist on `lane/a-barriers`. The current task/common production brief supersedes
historical concept-only and lead-only integration restrictions in the
[commission](commission.md). Family: [city_barriers](../city_barriers.md).
No shared register, progress record, sibling asset or world placement was changed.

## Design and dimensions

Original Blender construction: a repeatable straight galvanised tubular frame with
rounded corners, open diamond wire weave, three small wire ties at each side and
restrained oxide on two lower frame joints. Twenty-four continuous zigzag strands
alternate front/back depth at their knuckles; this is actual see-through geometry,
not an opaque sheet, alpha-cutout texture or welded square-grid substitute. Broad
highlights, quiet cool metal and sparse local wear follow Petrol & Coral and the
[Ironreach revision 02](../../concepts/districts-v1/ironreach.md) repair-yard direction.
No barbed wire, logos, gates, posts, feet, destruction or interaction was added.

The `.01` bollard and `.03` separator were inspected for family consistency. This
member deliberately uses the brief's lighter galvanised finish instead of their
painted petrol body or pale concrete; no competing amber accent was needed. No `.02`
or `.04` production files exist in this checkout at starting revision `6e62e48`;
those quay-rail assembly records are not dependencies of the chain-link panel.
The post/bracing and gate designs remain separately owned by `.06` and `.07`.

All dimensions are **provisional authored choices** under the standing production
rules, not measurements inferred from the district image or approved yard spacing:

- Godot visual width X / height Y / depth Z: **3.000 × 2.000 × 0.063 m**.
- Godot visual AABB minimum `(-1.500, 0.100, -0.0315)`, maximum
  `(1.500, 2.100, 0.0315)` m. The frame itself is 0.050 m deep; ties set total depth.
- Root/mesh origins `(0,0,0)` at the ground projection of the panel centre.
  Ground datum Y=0; **visual bottom is Y=0.100 m**, a mounting clearance, not feet.
  This panel must be supported by the later post kit in world placement. Isolated
  evidence shows the component alone, not a self-supporting fence installation.
- Long/repeat axis X. Both faces are equivalent. Blender +Z → Godot +Y and
  Blender +Y → Godot -Z; metre units, identity transforms, unit scale.
- Frame tube diameter **0.050 m**; centreline X=±1.475 m, bottom Y=0.125 m,
  top Y=2.075 m; corner centreline radius 0.065 m.
- Wire diameter **0.007 m**, six-sided smooth-shaded cross-section; 24 strands,
  0.120 m anchor spacing, 16 height intervals. Diamond centreline diagonals are
  approximately **0.240 × 0.24375 m**, deliberately coarser than literal fine fencing.
  Alternating knuckles lie ±0.006 m off the panel plane. End caps terminate inside
  the horizontal frame tubes. Side ties are closed 0.005 m diameter wire loops.
- No numeric scale correction or hidden placement transform in the prefab.
  Envelope/datum tolerance ±0.001 m; source/GLB agreement tolerance 0.00001 m.

### Provisional interface for `.06` and `.07`

Reuse the 2.100 m top datum, 0.100 m underside clearance, 0.050 m frame tubing,
wire geometry rhythm and named finishes below. This component owns no posts,
hinges or latch. Its outside mounting edges are X=±1.500 m and its vertical tube
centreline is X=±1.475 m; continuous straight tube regions accept post clamps.
For later assembly fitting, a **3.100 m panel-centre pitch** provisionally reserves
0.100 m between neighbouring panel edges for one shared post. An 0.080 m post at
the middle of that interval leaves 0.010 m bracket clearance per side. This is a
handoff proposal, not a claim that a matching post/gate has been built or tested.
Do not scale the panel to arbitrary lengths or double up shared posts; repeat whole
panels and author a different length only if an approved layout actually needs it.

The required straight-run/corner/terminal/open-paired-gate review remains pending
until `.06`/`.07` exist. Preserve the two main-yard vehicle openings, separate foot
gap/bypass and public boardwalk. No district-wide enclosure or placement is implied.

## Source, exports and materials

- Source: `art/source/models/environment/city_barriers_05/city_barriers_05.blend`.
- Collection `export_city_barriers_05`; root `CityBarriers05`; child
  `CityBarriers05_Mesh`; editable mesh `CityBarriers05_Geometry`.
- Export: `art/models/environment/city_barriers_05/city_barriers_05.glb` and its
  engine-generated `.import` sidecar. No prototype or downloaded geometry dependency.
- Tools: `tools/asset_production/city_barriers_05/{author,export,validate,finalize}.py`.
  Per-record scripts follow the accepted light/barrier conventions; export consumes
  the existing shared `tools/assets/blender/export_settings.json` unchanged.
- One joined mesh contains **31 closed shells**: frame, 24 strands and six ties.
  Deliberate wire-end/frame and tie/frame intersections represent attachment, not
  a fused solid. Manifold checks apply to each shell, not to a Boolean union.
  Cameras, lights and inspection floor remain outside the export collection.

Three opaque, backface-culled Principled surfaces, stable slot order:

| Slot | Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `fence_galvanised_frame` | (0.320, 0.380, 0.390) | 0.70 | 0.48 |
| 1 | `fence_galvanised_wire` | (0.190, 0.250, 0.260) | 0.60 | 0.55 |
| 2 | `fence_joint_oxide` | (0.160, 0.065, 0.026) | 0.05 | 0.84 |

These names/values are the chain-link finish handoff for later posts/gates. Oxide
is a face-assigned shared finish at lower joints, not a second damaged fence mesh;
any future scuffed variant should reuse this geometry with material variation.
No separate scuffed variant or shared-material system was invented in this task.

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. No textures,
embedded images, UV maps, emission, transparency, rig, sockets, animation or damage
states. No explicit LOD was authored. Godot's default per-asset generated LOD,
shadow-mesh and compression settings remain unchanged; thin-wire simplification
and repeated-fence cost still require actual renderer/profile review. No global
import setting or performance budget changed.

## Prefab and collision

`scenes/prefabs/environment/city_barriers_05.tscn` instances the GLB at
**`Visuals/Model` with identity transform**, without embedded replacement meshes.
The wrapper and collision-only fixture were text-authored then loaded, packed and
resaved by isolated pinned headless Godot, as required by the common brief. No
live Blender/Godot MCP session was touched and no separate editor synchronization
is claimed. Two consecutive saves retain exact scene bytes and node identities.

- Prefab UID `uid://do0kyi5smmipf`; GLB UID `uid://byloy6losneuk`.
- Scene UIDs live in scene headers; the check script's generated `.uid` is retained.
  All four fixture/dependency resource UIDs resolve to their exact paths.
- One separate `Collision/BarrierBody` StaticBody3D, static-world layer **1**, mask **0**.
- One thin **BoxShape3D size (3.000, 2.100, 0.063) m**, centre `(0,1.050,0)`.
  It intentionally closes the visible 0.100 m underside gap and all wire holes,
  following the standing solid-barrier collision rule. No detailed snag-prone wire
  collision. It blocks ordinary layer-1 queries; visual transparency does **not**
  establish bullet/aim pass-through or a new gameplay filtering rule.
- This static wrapper does not imply movable temporary fencing, damage, opening,
  locking or replicated lifecycle state. World integration supplies support posts.

Saved fixture: `tools/asset_production/city_barriers_05/check_scene.tscn`. It instances
this actual prefab and production `ActorMotion`, radius 0.35 m / height 1.8 m capsule,
with a collision-only test floor. No visible floor asset or world placement was added.
`check.gd` tests linked ancestry, imported bounds/materials, UIDs, separate simple
collision and outcomes through public physics and production movement APIs.

## Validation and evidence

[Hero](city_barriers_05-evidence/hero.png) · [side](city_barriers_05-evidence/side.png) ·
[wire/tie detail](city_barriers_05-evidence/detail.png) ·
[47 m / 42° overhead](city_barriers_05-evidence/overhead_47m_42deg.png).
All four are isolated CPU Cycles Blender renders at **1280×720**, PNG compression 9,
six significant bits/channel. The current brief's 720-pixel maximum supersedes
the example's historical 1280×800 evidence. Overhead is vertical-down perspective,
**47 m height / 42° vertical FOV**, north-up, without cropping or enlarging the asset.

Producer inspected all four views: hero and side show a clean light frame and open,
regular diamond pattern; the detail shows depth-separated knuckles and small ties.
Wear is confined to two lower joints. From the calibrated overhead view it reads as
an approximately **63-pixel-long thin pale line**, with a quiet shadow; the individual
diamonds are **not resolvable** at that distance. The thin edge is intentional rather
than an opaque wall; it is not proof that a populated street's targets remain visible.
Moving-camera wire shimmer, engine LODs, street lighting and actor overlap are pending.

Measured [validation.json](city_barriers_05-evidence/validation.json) results:

- **3,168 source vertices, 3,072 polygon faces, 6,240 triangles; 3,504 exported vertices**
  after material/normal splits; **one mesh / three surfaces**.
- **Zero degenerate faces/triangles; zero non-manifold edges**; 31 closed components,
  positive total signed volume 0.0197002 m³. Finite coordinates and unit normals.
- Maximum source normal-length error 0.000000105; export error 0.000000071.
- Independent Blender BVH rays confirm a central diamond opening is clear while
  the top frame blocks. No opaque visual sheet hides behind the wire pattern.
- Source/GLB/engine AABBs match the provisional envelope within tolerance.
  Export contains exactly root plus mesh, without cameras/lights/textures/animation.
- **Fresh re-export from saved `.blend` is byte-identical** to the 124,276-byte GLB.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports and loads dependencies;
  identity ancestry, three opaque back-culled surfaces, UIDs and stable roundtrip pass.
- Layer-1 ray at Y=0.5 hits the barrier; ray at Y=2.2 clears the top.
- Production `ActorMotion.step`, 48 ticks per contact/bypass case in authority and
  replay modes: contact stops at Z=-0.381510 m; bypass at X=2.1 m reaches
  Z=2.000001 m. Capsule remains at the ground datum; both modes match. This is
  local simulation parity, **not network transport/prediction acceptance**.
- Canonical production checks **pass without ignored failures**: owned GDScript
  format/lint/compile; **14/14 Python tests; 119/119 GUT tests, 6,362 assertions**;
  required diagnostic negative test correctly returns 1.

[final.log](city_barriers_05-evidence/final.log) is the concise command/diagnostic
receipt. Source creation, validation, normalization and checks passed. Blender emits
only future-6.0 `use_nodes` deprecation notices; headless import emits the existing
MCP addon 4.8-versus-tested-4.7 warning. No new resource/script/physics diagnostic was
suppressed. Full scratch logs and re-exports remain outside the checkout. The
[manifest](city_barriers_05-evidence/manifest.json) hashes every delivered payload,
including source, scripts, prefab, metadata, four renders and this record; excludes itself.

## Exact reproduction

From the repository root in Git Bash, with pinned tools installed:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
mkdir -p C:/tmp/ft/assets/city_barriers_05

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_05/author.py
# Opens saved source, checks actual binary accessors and freshly exports to scratch.
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_05/validate.py
# Optional explicit export with the shared contract:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  art/source/models/environment/city_barriers_05/city_barriers_05.blend \
  --python tools/asset_production/city_barriers_05/export.py \
  -- C:/tmp/ft/assets/city_barriers_05/reexport

timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/city_barriers_05/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . \
  --check-only --script res://tools/asset_production/city_barriers_05/check.gd
timeout 30 "$GDSTYLE" fmt --check tools/asset_production/city_barriers_05/check.gd
timeout 30 "$GDSTYLE" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/city_barriers_05/check.gd
# Requires an empty output directory; retain earlier runs outside the checkout.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/city_barriers_05/checks
python tools/asset_production/city_barriers_05/finalize.py
```

`author.py` recreates source/export/renders. `validate.py` replaces validation.json;
run the Godot check after it, then finalize to retain every receipt section. Do not
rewrite source or UIDs merely to inspect existing results. `finalize.py` requires
a passing canonical summary and compacts renders before hashing all delivery files.

## Remaining acceptance

Independent technical/art review pending. Dimensions, post spacing and assembly
interfaces remain provisional. Required full-kit straight/corner/terminal/open-gate
review awaits `.06`/`.07`; that is not a dependency of this standalone panel design.
World integration owns supporting posts, two yard openings, foot bypass, boardwalk,
entrance setbacks, repeated-run fit, target/feet visibility and actual engine camera
captures. Vehicle contact/turning/clearance, real separate-process network behavior,
packaged target-device behavior, Deck readability and sustained rendering/load/LOD
performance remain **unperformed**. No placement, gameplay rule, world scene,
road geometry, interaction or shared tracking entry was changed.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
