# city_barriers.07 — Paired chain-link vehicle gate

10 October 2026. **Source/export and linked static prefabs delivered; independent
review and world/gameplay acceptance pending.** Produced by the commissioned
implementation specialist on `lane/a-barriers`, starting from `01b9ae7a`.
The current task/common production brief supersedes the historical concept-only
and lead-only integration restrictions in [commission](commission.md).
Family: [city_barriers](../city_barriers.md). No sibling, shared register/progress
record, road geometry, world placement or gameplay system was changed.

## Design and dimensions

Original Blender construction: **two separate hinge-pivoted chain-link gate
leaves**, with the delivered panel's rounded galvanised frame, see-through woven
diamond rhythm, a rear tension brace, two annular hinge knuckles per leaf and a
small sliding-bolt/keeper silhouette. A third component supplies the stationary
post collars, hinge cheeks and retained pins. It mounts on the **existing `.06`
terminal posts**, not a newly duplicated carrier. Rust remains confined to small
joint/collar bands. No barbed wire, logos, textures, padlock, animation, interaction,
locking, damage state or runtime hierarchy construction was added.

Direction follows Petrol & Coral, approved district identities/Stage 4 and
[Ironreach revision 02](../../concepts/districts-v1/ironreach.md). The `.01`, `.03`,
`.05` and `.06` deliveries were read; `.02`/`.04` have no delivered files in this
checkout and are not dependencies of the distinct chain-link kit. The source
recipe reuses `.05`'s frame/weave construction and `.06`'s hardware geometry
helpers without modifying them. The gate is not merely a scaled panel: its hinge
axis, brace, support fittings and asymmetric mating latch are separately authored.

All dimensions are **provisional authored choices** under the standing production
rules, not concept-image measurements or approved yard/vehicle clearances.
Godot dimensions are width X / height Y / depth Z, in metres:

| Component | Dimensions X/Y/Z | AABB minimum | AABB maximum |
| --- | --- | --- | --- |
| Left leaf, including bolt | 3.262 / 2.000 / 0.177 | (-0.027, 0.100, -0.110) | (3.235, 2.100, 0.067) |
| Right leaf, including keeper | 3.1595 / 2.000 / 0.157 | (-3.1325, 0.100, -0.090) | (0.027, 2.100, 0.067) |
| Stationary hinge mount | 0.182 / 1.030 / 0.094 | (-0.162, 0.585, -0.047) | (0.020, 1.615, 0.047) |

- Both frame bodies are **3.000 × 2.000 m**, matching `.05`; tube diameter 0.050 m,
  underside Y=0.100 m, top Y=2.100 m. The left frame spans local X=0.075…3.075 m;
  the right spans X=-3.075…-0.075 m. Both keep the 24-strand, 0.007 m diameter wire
  and approximately 0.240 × 0.24375 m diamond rhythm. No opaque panel behind the wire.
- Root/mesh origin `(0,0,0)` is the **vertical hinge axis projected to the ground**,
  not the leaf centre. Metre units, unit scale, applied rotation/scale. Blender
  +Z → Godot +Y and Blender +Y → Godot -Z; no corrective imported-model transform.
- Hinge centres Y=**0.650 and 1.550 m**, avoiding `.06`'s panel-clamp levels.
  Knuckle outer diameter 0.054 m, bore diameter 0.025 m, pin diameter 0.024 m;
  0.0005 m radial clearance and 0.005 m cheek-to-knuckle vertical clearance.
- Mount post-collar bore diameter 0.081 m fits `.06`'s 0.080 m shaft; stationary
  post centre is X=-0.115 m relative to the left hinge. Rotate the mount 180°
  about +Y for the right side. Two cheeks per pin support the leaf knuckle.
- Rear tension brace diameter 0.024 m, 0.055 m behind the wire plane; short
  standoffs join it to the frame. It remains visual decoration, not extra collision.
- Bolt axis at Y=1.100 m, Z=-0.060 m; diameter 0.016 m. The keeper has a genuine
  aperture and receives the bolt without intersecting its surfaces. This is a
  static closed-fitting depiction, not an operable latch or gameplay state.
- Envelope/datum tolerance ±0.001 m; source/GLB agreement tolerance 0.00001 m.

### Kit interface and saved configurations

Default `city_barriers_07.tscn` is **statically open inward by 90°**, matching the
Ironreach concept. `city_barriers_07_closed.tscn` is a separate **static closed
configuration/reference**, not a state machine. Both reuse the same three exports
and the existing terminal-post prefab; no alternate geometry or animation clips.

| Part | Position in assembly X/Y/Z | Rotation about Godot +Y |
| --- | --- | --- |
| Left leaf | (-3.150, 0, 0) | +90° open, 0° closed |
| Right leaf | (3.150, 0, 0) | -90° open, 0° closed |
| Left mount | (-3.150, 0, 0) | 0° |
| Right mount | (3.150, 0, 0) | 180° |
| Existing left terminal post | (-3.265, 0, 0) | 180° |
| Existing right terminal post | (3.265, 0, 0) | 0° |

Hinge-axis spacing **6.300 m**, post-axis spacing **6.530 m**; closed frame-end
separation **0.150 m**, bridged visually by the latch and physically by the simple
leaf envelopes. Open leaves extend toward **Godot -Z** into the yard. Measured
open collider-to-collider width is **6.1660001 m**; this is an asset measurement,
not accepted turning room. Reserve approximately 3.24 m behind each hinge for the
longer leaf's extent; tested static 0°/45°/90° hardware fit is not continuous
animation or vehicle-swept-clearance certification.

Terminal braces face **away from the gate opening and into the fence bays**.
Adjacent `.05` panel centres are X=±4.815 m, Y=Z=0; following support centres are
X=±6.365 m. Continue the inherited **3.100 m** pitch and do not double up posts,
scale panels or mirror prefab roots negatively. Full straight/line/corner/terminal/
open-gate context is supplied in the saved check fixture and the hero/overhead
renders. This is a kit-fit study, not district placement. Preserve both main-yard
vehicle openings, separate pedestrian bypass and public boardwalk downstream.

## Source, exports and materials

- Source: `art/source/models/environment/city_barriers_07/city_barriers_07.blend`.
- Named collections: `export_city_barriers_07_{left,right,mount}`.
- Roots: `CityBarriers07_Left`, `CityBarriers07_Right`, `CityBarriers07_Mount`;
  corresponding mesh children end in `_Mesh`, editable mesh datablocks in `_Geometry`.
- Explicit exports: `art/models/environment/city_barriers_07/city_barriers_07_{left,right,mount}.glb`,
  with one engine-generated `.import` sidecar each.
- Tools: `tools/asset_production/city_barriers_07/{author,export,validate,finalize}.py`,
  plus `check.gd`, its `.uid` and the saved `check_scene.tscn` fixture.
- Export uses the unchanged shared `tools/assets/blender/export_settings.json`.
  Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**.
- Saved source roots remain at the origin in their neutral component orientations;
  isolate collections to inspect. Sibling mesh context is loaded **only after**
  saving/exporting for the isolated evidence renders. No sibling mesh is duplicated
  into a gate export or saved gate source. Studio ground/lights/cameras are excluded.
- Each mesh contains closed manufactured shells; intentional wire/frame, brace/
  standoff and strap/knuckle intersections represent attachments, not a Boolean
  union. Topology checks apply per shell. Mating leaves and stationary/moving hinge
  surfaces are separately checked for unwanted intersections.

Three opaque, backface-culled Principled slots match the `.05`/`.06` finishes exactly;
validation compares actual exported material dictionaries to `.05`:

| Slot | Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- | --- |
| 0 | `fence_galvanised_frame` | (0.320, 0.380, 0.390) | 0.70 | 0.48 |
| 1 | `fence_galvanised_wire` | (0.190, 0.250, 0.260) | 0.60 | 0.55 |
| 2 | `fence_joint_oxide` | (0.160, 0.065, 0.026) | 0.05 | 0.84 |

No textures, embedded images, UV maps, emission, transparency, rigs, sockets,
animations, damage variants or explicit LOD. Existing per-asset Godot automatic
LOD/shadow-mesh/compression defaults remain unchanged. Thin-wire LOD/shimmer and
repeated-fence cost need actual renderer/performance review; no budget is claimed.

## Prefabs and collision

| Prefab under `scenes/prefabs/environment/` | Scene UID | GLB UID |
| --- | --- | --- |
| `city_barriers_07_left.tscn` | `uid://ctk4cliroskru` | `uid://8v5b7pjoxm10` |
| `city_barriers_07_right.tscn` | `uid://bshq2emluo3ff` | `uid://bm7i211emvjw4` |
| `city_barriers_07_mount.tscn` | `uid://b7dpkpsqps1b2` | `uid://b3k38kq64jb02` |
| `city_barriers_07.tscn` (open assembly) | `uid://pirflhamo2yp` | Existing component instances |
| `city_barriers_07_closed.tscn` | `uid://bu0kklhi8in2u` | Existing component instances |

Component wrappers instance their GLB at **`Visuals/Model`, identity transform**.
The assembly parents place those wrappers at the saved hinge/post offsets above.
No embedded replacement meshes. Scenes were authored as text and loaded/packed/
resaved with isolated pinned headless Godot per the common brief. No live Blender/
Godot MCP session was touched; no separate open-editor synchronization is claimed.
All six owned scenes preserve bytes/UIDs across two fresh normalization processes.
Scene UIDs live in headers; the script's generated `.uid` is retained.

Standing collision rule: each new component has **one separate static body and
one simple box**, `Collision/Body/Shape`, layer **1**, mask **0**:

| Component | Box size X/Y/Z | Centre X/Y/Z |
| --- | --- | --- |
| Left leaf | (3.262, 2.100, 0.177) | (1.604, 1.050, -0.0215) |
| Right leaf | (3.1595, 2.100, 0.157) | (-1.55275, 1.050, -0.0115) |
| Stationary mount | (0.182, 1.030, 0.094) | (-0.071, 1.100, 0) |

Leaf boxes intentionally close the 0.100 m underside gap and all wire openings,
include fittings, and overlap slightly at the closed latch. This conservatively
extends the blocking face beyond the thin wire, avoiding snag-prone mesh collision.
The mount's box spans its two collars; the existing post and brace colliders are
reused unchanged. The open assembly leaves the opening empty while its rotated
leaves still block at the sides. Visual openness does not imply bullet/aim
pass-through or a new filtering rule. No collision toggling or runtime gate motion.

## Validation and evidence

[Hero/full kit](city_barriers_07-evidence/hero.png) ·
[closed side](city_barriers_07-evidence/side.png) ·
[latch detail](city_barriers_07-evidence/detail.png) ·
[47 m / 42° overhead](city_barriers_07-evidence/overhead_47m_42deg.png).
Four isolated Blender CPU Cycles renders, **1280×720**, PNG compression 9 and six
significant bits/channel. The current common brief's 720-pixel maximum supersedes
the older 1280×800 example. Overhead is true vertical-down perspective at **47 m /
42° vertical FOV**, north-up, without enlarging/cropping the asset.

Producer inspected all four final views: open leaves flank an obvious wide gap in
matching straight/corner/terminal fencing; the side shows symmetric tension braces
and coherent diamond mesh. Detail shows a solid retained bolt through a hollow
keeper, not intersecting fittings. At calibrated overhead distance the frames read
as thin pale lines around a roughly **123-pixel clear opening**. Individual diamonds,
knuckles and latch are unresolved. These are kit-context Blender observations,
not engine street captures or actor/target-visibility acceptance.

Measured [validation.json](city_barriers_07-evidence/validation.json):

| Component | Source vertices | Source faces | Triangles | Export vertices | Closed shells | GLB bytes |
| --- | --- | --- | --- | --- | --- | --- |
| Left | 3,512 | 3,342 | 6,892 | 4,256 | 42 | 146,308 |
| Right | 3,512 | 3,344 | 6,888 | 4,304 | 43 | 147,444 |
| Mount | 464 | 404 | 904 | 992 | 8 | 32,040 |

- Each: **one mesh / three surfaces; zero degenerate faces/triangles, zero
  non-manifold edges**, positive closed volume, finite vertices and unit normals.
  Maximum source normal-length error <0.000000122; exported error <0.000000094.
- Actual binary GLB bounds match source and independent literal expected envelopes.
  Only the declared root/mesh are exported; no camera/light/texture/animation data.
- **All three fresh re-exports from saved `.blend` are byte-identical**.
- Blender BVH tests prove hollow knuckle bores, solid pins, an open keeper passage,
  zero closed leaf/latch surface intersections and zero leaf/mount surface
  intersections at 0°, 45°, 90° for both leaves.
- Pinned Godot **4.8.dev7.official.c971f93e7** imports/loads all dependencies;
  identity ancestry, imported bounds/materials/colliders and registered UIDs pass.
  Six saved scenes are byte-stable across two fresh normalization processes.
- Layer-1 queries confirm panel/post and closed-latch seams block, above-gate rays
  clear, open gateway rays pass and both opened leaves still block laterally.
- Production `ActorMotion.step`, capsule r=0.35 m / h=1.8 m, 48 ticks per case in
  authority/replay modes, at X=-1.5/0/+1.5 m: closed fixture stops at
  **Z=8.417486 m** (gate placed at Z=8 m); open passage reaches **Z=-2.000001 m**.
  Floor contact and both modes agree. This is local simulation parity, **not
  multiplayer transport/admission/prediction acceptance**.
- An independent **2.0 × 1.5 × 4.5 m** collision-only vehicle-sized box swept through
  the opening clears the open gate and stops at the closed gate. This is a bounded
  physics query, **not actual car controller, turning, braking or impact acceptance**.
- Canonical checks: owned GDScript formatting/lint/compilation pass; **14/14 Python
  tests and 119/119 GUT tests (6,362 assertions)** pass; diagnostic negative test
  correctly returns 1. **Aggregate exit is 1**: the shared cumulative 120-second
  compilation deadline prevents **11 unrelated `tools/assets/` scripts** from
  running. Exact paths and `CHECK DEADLINE EXCEEDED` classification are retained.
  No owned script failed. The final additional width assertion passes a fresh
  targeted formatting/lint/compile/physics run; unchanged global failure was not rerun.

[final.log](city_barriers_07-evidence/final.log) records concise command outcomes and
corrections: initial hinge strap intruded into the pin bore; its attachment was
shortened and source/export/renders rebuilt. An initial saved Godot open-angle sign
mismatch was caught by independent directional/physics assertions and corrected
without changing source axes. Initial lint local-variable warning was resolved by
separating collision validation. Final checks have no new source/resource/physics
diagnostics. Blender emits future-6.0 `use_nodes` deprecation notices; import emits
the existing MCP addon 4.8-versus-tested-4.7 warning. Neither is hidden. Raw logs and
scratch exports remain outside Git. The [manifest](city_barriers_07-evidence/manifest.json)
hashes every delivered payload except itself and records read-only authoring dependencies.

## Exact reproduction

From repository root in Git Bash with pinned tools installed:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
mkdir -p C:/tmp/ft/assets/city_barriers_07

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_07/author.py
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/city_barriers_07/validate.py
# Optional explicit re-export independent of validation:
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  art/source/models/environment/city_barriers_07/city_barriers_07.blend \
  --python tools/asset_production/city_barriers_07/export.py \
  -- C:/tmp/ft/assets/city_barriers_07/reexport

timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --path . \
  --script res://tools/asset_production/city_barriers_07/check.gd -- --normalize
timeout 180 "$GODOT" --headless --path . \
  --check-only --script res://tools/asset_production/city_barriers_07/check.gd
timeout 30 "$GDSTYLE" fmt --check tools/asset_production/city_barriers_07/check.gd
timeout 30 "$GDSTYLE" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/city_barriers_07/check.gd
# Requires an empty output directory; preserve earlier runs outside the checkout.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/city_barriers_07/checks
python tools/asset_production/city_barriers_07/finalize.py
```

`author.py` rebuilds source/exports/renders; `validate.py` replaces validation.json,
so run the Godot check afterward, then finalize. Finalization requires passing
owned checks, retains the narrowly classified external compiler-deadline failure
instead of claiming aggregate success, compacts renders and hashes the delivery.
Do not regenerate source or UIDs merely to inspect existing artifacts.

## Remaining acceptance

Independent technical/art review remains pending. Dimensions, spacing, placement
and visibility are provisional. World integration owns both yard exits, foot
bypass, boardwalk, support/leaf setbacks, actual street camera captures and target/
feet occlusion. Actual car contact/turning/braking, real separate-process network
transport/admission/prediction, packaged target devices, Deck readability and
sustained GPU/LOD/load performance remain **unperformed**. The global compiler
needs a complete downstream check within a sufficient execution window. No gate
interaction or replication behavior is implied by these static configurations.

## Saved identity normalization

Identity normalized by the saved-identity pass; geometry/material values unchanged.
