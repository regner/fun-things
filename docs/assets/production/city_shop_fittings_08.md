# city_shop_fittings.08 — projecting blade sign and bracket

Source/export candidate, 9 October 2026, delivered by the assigned production worker
for ROOT `fbd92534-e159-432f-aae7-28072c2bf3b2`, workspace `wks_59891ad7a05813e5`.
Original editable source and explicit GLB pass the recorded technical checks.
Independent acceptance and engine import, prefab, save/reopen, actual shell mounting,
collision, runtime/network, device/performance and world placement remain **pending**.
This is not source-only READY. The commission at
`2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661` and this assignment authorize production
and reversible dimensions beyond the older concept-only brief.

- Source: [city_shop_fittings_08.blend](../../../art/source/models/environment/city_shop_fittings_08/city_shop_fittings_08.blend).
- Export collection: `export_city_shop_fittings_08`; attachment root: `city_shop_fittings_08`.
- Output: [city_shop_fittings_08.glb](../../../art/models/environment/city_shop_fittings_08/city_shop_fittings_08.glb).
- Reproduction/check tools: [owned tools](../../../tools/asset_production/city_shop_fittings_08/).
- Authoritative evidence: [evidence directory](city_shop_fittings_08-evidence/), with
  [exact expected byte/SHA256 manifest](city_shop_fittings_08-evidence/manifest.json).

## Original design and provenance

An original rounded vertical housing, rolled shoulder, two continuous ivory trim
rings, seated blank face carriers and dark reveals attach to a narrow backplate
through two cantilever arms with tapered underside gussets. Four restrained captive
faceted fixing heads complete the mounting language. Sixteen separately editable
closed meshes plus one datum root, 3,624 triangles and eighteen material primitives.
No copied wall-panel mesh, external mesh, generated image asset, tenant copy or
production texture is used. There is no rig, animation, light, emission, collision,
opening mechanism or mandatory navigation function.

Read references: AGENTS.md, docs/assets.md, art-direction.md, city_shop_fittings.md,
Signal Row v03 and its F02 breakdown, commercial-graphics and southern-parade briefs,
the common district contract, Crescents v02 and Old Quay v03 frontage references,
and the accepted high-rise architecture/elevation sheet. The compact side-facing
vertical field follows Signal Row's frontage rhythm; broad rounded edges and quiet
trim follow the architectural study and read-only canopy .01 / fascia .02 previews.
Dimensions are authored choices, not measurements inferred from generated images.
No other asset is a source/export dependency. The district graphics owner supplies
future artwork and material remaps, reusing these two faces.

The [dimensioned elevation refinement](city_shop_fittings_08-evidence/elevation_design.svg)
was supplied before source construction; its [PNG](city_shop_fittings_08-evidence/elevation_design.png)
and the actual [source elevation](city_shop_fittings_08-evidence/source_elevation.png)
record the selected compact projection. The diagram is an editable measurement
illustration, not a second mesh. Read-only export/check/runner patterns were adapted
from .07 and the .01/.02 profile helpers; all blade geometry is newly authored in
private Blender. No shared Blender/Godot session, project, prefab, world, shared
asset or Git/index mutation was used. Frozen Batch02 was untouched.

## Metre attachment and clearance contract

The pivot is the **centre of the wall mounting plane**, not a ground pivot.
Blender +Y is forward away from the wall and +Z is up. One glTF Y-up conversion maps
these to Godot -Z and +Y. The two artwork faces intentionally point sideways ±X.
All exported object locations/rotations are zero, scales are one; modifiers are
applied. Mesh vertices carry the measured offsets from the common root datum.

| Measurement | Value in metres |
| --- | --- |
| Overall Godot width X / height Y / projection Z | 0.200 / 1.160 / 0.880 |
| Blender AABB | (-0.100, 0.000, -0.580) to (0.100, 0.880, 0.580) |
| Godot AABB | (-0.100, -0.580, -0.880) to (0.100, 0.580, 0.000) |
| Sign body extent along forward / vertical | 0.680 × 1.160; rear Y=0.200, nose Y=0.880 |
| Body thickness including trim | 0.148; trim planes X=±0.074 |
| Backplate footprint / depth | 0.200 × 0.960 / 0.030; rear exactly Y=0 |
| Captive fixing centres | Blender X=±0.065, Z=±0.420; depth Y=0.028–0.040 |
| Arms | 0.080 wide × 0.225 long × 0.064 high; Y=0.025–0.250, Z centres ±0.360 |
| Gussets | 0.052 wide; Y=0.026–0.235; Z relative to arm centre -0.130…-0.022 |
| Hardware total envelope | X ±0.100, Y=0…0.250, Z=-0.490…0.480 |
| Body / wall gap | 0.200, crossed only by the intended mounting hardware |
| Reserved fitting envelope, Blender | X ±0.200, Y=-0.020…0.980, Z ±0.680 |
| Reserved fitting envelope, Godot | X ±0.200, Y ±0.680, Z=-0.980…0.020 |
| Suggested pivot above finished ground | 3.200; lowest visible point 2.620 |
| Tolerances | AABB ±0.001; wall placement ±0.002; no corrective scale |

Use a flat facade patch at least 0.400 wide × 1.360 high and retain at least 0.100
physical gap from other fittings. Place beside canopy/fascia ends or check their
actual volumes; this sign is not assumed to fit above an arbitrary canopy. At the
suggested height the reserved lower boundary is 2.520 above ground. These are
reversible placement proposals, not pedestrian/headroom, fastening or engineering
acceptance. No wall holes, bolts through a real shell or load rating are supplied.
The backplate/arm overlap is 0.005 along Y and arm/shell overlap is 0.050; the face
carriers seat into the shell. Closed solids intentionally overlap at these joints;
the model is a visual assembly, not a watertight union or an engineered hollow box.

## Independent artwork interfaces

| Mesh | Stable slot 0 material | Outward normal / face plane |
| --- | --- | --- |
| `face_positive_x` | `blade_artwork_positive_x` | +X / X=+0.067 |
| `face_negative_x` | `blade_artwork_negative_x` | -X / X=-0.067 |

Each carrier's slot 1 is `blade_mount_metal` for sides/back. Replace only slot 0;
find GLB materials by name rather than assuming a global material index. Each face
is 0.580 wide × 1.060 high, aspect **29:53**, at Blender Y=0.250…0.830 and
Z=-0.530…0.530, with 0.045 corner radius. Keep important content inside the centred
0.500 × 0.980 rectangle; bleed background to the boundary and clamp texture edges.
Neither face needs duplicated coplanar geometry or a double-sided material.

UV0 on the +X face has U increasing with Blender +Y; on the -X face U increases
with Blender -Y. Both have V increasing with +Z in Blender. Thus the same image
reads left-to-right, upright, from either outward side. glTF flips V to image-down;
the independent decoder verifies all 36 boundary vertices and all 34 artwork
triangles on **each** face, including oriented UV determinants and outward normals.
The [positive](city_shop_fittings_08-evidence/uv_positive_x.png) and
[negative](city_shop_fittings_08-evidence/uv_negative_x.png) diagnostic renders
visually confirm TL/TR/BL/BR, readable text and right/up arrows on both sides.
The original 580×1060 chart is evidence only and is not packed into the source or
export. Future image resolution, emission and engine remapping belong to graphics
and integration owners. There is no district-content duplication.

## Materials and density

Six embedded opaque, single-sided Principled/glTF PBR materials; no texture,
external `.tres`, transparency, transmission or tangent-map requirement.
sRGB values below are converted to linear base colour in Blender.

| Material | sRGB | Metallic / roughness |
| --- | --- | --- |
| `blade_slate_petrol` | #405B68 | .25 / .46 |
| `blade_warm_trim` | #C8C2AD | .22 / .48 |
| `blade_recess` | #23333B | 0 / .72 |
| `blade_mount_metal` | #384850 | .45 / .50 |
| `blade_artwork_positive_x` | #C3C7BC | 0 / .56 |
| `blade_artwork_negative_x` | #C3C7BC | 0 / .56 |

Triangles: shell 284; each trim 432; each reveal 140; each carrier 140;
backplate 188; each arm 188; each gusset 204; each faceted fixing 236.
Density supports the close-view rounded profiles; no device budget or LOD
acceptance is inferred. Unused startup material/internal viewer handles may remain
in Blender, but no external image dependency or studio object enters the GLB.

## Checks, views and limits

[source_export_checks.json](city_shop_fittings_08-evidence/source_export_checks.json),
[glb_checks.json](city_shop_fittings_08-evidence/glb_checks.json), and
[attachment_and_reexport_checks.json](city_shop_fittings_08-evidence/attachment_and_reexport_checks.json)
pass: exact collection/node membership, applied transforms, finite vertices/unit
normals, positive volume per connected solid, manifold consistent winding,
nondegenerate polygons/triangles, triangle-versus-normal orientation, exact material
scope, both outward face mappings, source/export bounds and axis conversion,
seated attachment contacts, studio exclusion and **byte-identical saved-source
re-export**. GLB size is 98,848 bytes. Its SHA256 is
`d826c257c21de7754f0261e6376f942abbc6ddc249fdc5f5d5c7e3a54049a2b6`.
The exact source and all supporting file fingerprints are in the manifest.

The source retains an excluded exact 1×1×1 m reference. The final
[metre comparison](city_shop_fittings_08-evidence/measured_1m_comparison.png)
uses orthographic elevation to show the 1.160 body-height / 1 m ratio without
perspective distortion. The [hero](city_shop_fittings_08-evidence/hero.png),
[bracket](city_shop_fittings_08-evidence/bracket_detail.png), elevation, both UV
views and [wall mounting preview](city_shop_fittings_08-evidence/mounting_preview.png)
were visually inspected: broad continuous trim, seated faces, coherent cantilevers,
no obvious flipped faces or exposed coplanar flicker. This is producer self-check,
not independent art acceptance.

[project_camera.png](city_shop_fittings_08-evidence/project_camera.png) is an
unscaled 1280×800, vertical-down perspective, fixed-yaw Blender view at 47 m / 42°
vertical FOV. The sign is only a tiny vertical edge at that distance. It establishes
no text/wayfinding readability, populated-street visibility or roof-occlusion claim.
The wall/ground jig is an original temporary preview only. All camera transforms,
projection settings, fixture dimensions and render settings are recorded in
[preview_checks.json](city_shop_fittings_08-evidence/preview_checks.json).
No Blender preview is presented as Godot runtime evidence.

## Reproduction and complete diagnostics

[execution.json](city_shop_fittings_08-evidence/execution.json) retains exact argv,
process-local environment, durations, PIDs and exits. Full combined logs are kept.
Private `/usr/bin/blender` verifies Blender **5.2.2 LTS / d13f752e3b9c**, glTF
**5.2.40**; the requested `/usr/bin/blender5.2.2LTS` pathname does not exist
(recorded launch exit 127, FileNotFoundError). This is the authorized build at its
installed path. No version substitution or global configuration edit occurred.
Every Blender invocation uses `-noaudio -t 4`, `ALSOFT_DRIVERS=null`,
`SDL_AUDIODRIVER=dummy`, an owned cache and `--python-exit-code 1`.

All source/export/UV/attachment checks and renders exited 0. The exporter logs its
missing optional MeshOptimizer library as `ERROR`; compression is unused, and the
raw uncompressed GLB passed decoding and exact re-export. Blender 6.0 future
`use_nodes` deprecations and BlenderMCP addon registration/shutdown messages remain
unsuppressed. No shared connector/live editor was called. A premature image-view
attempt before rendering completed returned file-not-found; the completed file
was then inspected successfully. It was not a render failure.

One evidence-only fix pass corrected an overlapping elevation heading, widened
the bracket camera to remove top cropping, and changed the metre comparison from
perspective to orthographic. Original affected PNGs, SVG, preview script and
camera receipt remain in `initial_preview/`; final evidence is at the top level.
Source and export bytes were not changed by previews or the fix pass.

From repository root, the exact source can be reopened and audited/re-exported:

```sh
python tools/asset_production/city_shop_fittings_08/run.py verify_again /usr/bin/blender -b -noaudio -t 4 art/source/models/environment/city_shop_fittings_08/city_shop_fittings_08.blend --python-exit-code 1 --python tools/asset_production/city_shop_fittings_08/export.py -- docs/assets/production/city_shop_fittings_08-evidence/reexport_city_shop_fittings_08.glb
python tools/asset_production/city_shop_fittings_08/check_glb.py
python tools/asset_production/city_shop_fittings_08/manifest.py --verify
```

Use fresh runner labels: logs cannot be overwritten. `author.py` regenerates the
original source; `export.py` exports only exact declared members, enables UV/normals,
applies glTF Y-up once and excludes animations/cameras/lights/extras. `preview.py`
recreates all eight views without saving the source; optional names after `--`
rerender only those views. Rasterize the retained diagnostic/elevation SVGs with
the recorded ImageMagick argv. `manifest.py` inventories every owned file, including
historical evidence, except its self-referential manifest; regenerate only after
intentional changes. No workers or private writer processes remain active at handoff.
Concrete review fixes can return to this owner; downstream acceptance stays with
ROOT/integrator.
