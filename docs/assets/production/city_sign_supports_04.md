# city_sign_supports.04 — Wayfinding post

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay/device acceptance pending.** Produced by the commissioned implementation
worker on `lane/a-signs`; the production lead owns acceptance and downstream integration.
[Commission](commission.md) and the current per-asset production brief supersede the
historical concept-only restrictions in [city_sign_supports](../city_sign_supports.md).
No sibling, register, shared brief, road tool, world placement or gameplay code changed.

## Design and dimensions

Original Blender construction: a slender cylindrical petrol mast with a cast shoe, shallow
metal foot and cap, three alternating arrow-shaped fingers, continuous bevelled frames,
recessed neutral faces, dark gaskets and simple mounting collars. The lower/upper arrows
point along local +X; the middle arrow points -X. This is one static model, not adjustable
or animated signage. The silhouette distinguishes it from the broad low panel and noticeboard
while retaining [the .02](city_sign_supports_02.md) and [.03](city_sign_supports_03.md)
material palette, inset face treatment and separate artwork ownership.

Northpoint's campus route markers supply the primary reference use; civic squares,
forecourts and pedestrian destinations elsewhere can reuse it. The [district identities](../../concepts/world-v1/stage-03-district-identities/README.md)
and [street hierarchy](../../concepts/world-v1/stage-04-streets/README.md) are context,
not accepted placement. Keep the foot out of movement corridors and the fingers away from
vehicle lanes and camera-critical routes. No brands, copy, downloaded geometry, image-to-mesh,
textures, interaction, interiors or destruction states are included.

These are **provisional authored dimensions**, permitted by the standing production rules,
not measurements inferred from concept images or approved world clearances:

| Quantity | Metres / contract |
| --- | --- |
| Overall Godot X/Y/Z | **2.88 × 3.92 × 0.40** |
| Godot AABB | min `(-1.44,0,-0.20)`, max `(1.44,3.92,0.20)` |
| Ground pivot | `(0,0,0)`, centre of the mounting foot |
| Foot | Diameter 0.40, bottom 0, top 0.055 |
| Cast shoe / mast | Shoe radius 0.13, top 0.22; mast radius 0.075, top 3.89 |
| Mast cap | Radius 0.093; top 3.92 |
| Fingers | Each 1.40 wide × 0.32 high; centres Y=2.75 / 3.20 / 3.65 |
| Finger X extents | Lower/upper 0.04…1.44; middle -1.44…-0.04 |
| Lowest finger edge | **2.59**, clear of the 2.5 m overhead-only threshold |
| Finger depth | Godot Z=-0.19…-0.07; frame lip Z=-0.19 |
| Mounting collars | Radius 0.103, height 0.15, centred at each finger height |
| Artwork field | Each **1.29 × 0.23**, arrow-shaped clipped outline |
| Artwork plane | Godot Z=-0.184; recessed 0.006 behind frame lip |
| Safe copy rectangle | Each 1.02 × 0.19, centred at X=±0.63 and its finger height |
| Numeric tolerance | Envelope/ground ±0.001; coordinate/UV comparison ±0.00001 |

Metre units, applied transforms, identity root and all mesh origins at ground datum.
Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z (front). No corrective prefab
scale/rotation. Road-tool mounting uses the ground-centred root, with saved placement yaw;
no socket or road-tool implementation is required. This does not authorize placement.

## Source, export, materials and artwork interface

- [Blender source](../../../art/source/models/environment/city_sign_supports_04/city_sign_supports_04.blend)
- [Explicit GLB](../../../art/models/environment/city_sign_supports_04/city_sign_supports_04.glb)
  with adjacent `.import` settings/identity.
- [Linked prefab](../../../scenes/prefabs/environment/city_sign_supports_04.tscn)
- [Author](../../../tools/asset_production/city_sign_supports_04/author.py),
  [export](../../../tools/asset_production/city_sign_supports_04/export.py),
  [source/binary validator](../../../tools/asset_production/city_sign_supports_04/validate.py),
  [headless prefab/motion check](../../../tools/asset_production/city_sign_supports_04/check_prefab.gd).

Collection `export_city_sign_supports_04` contains root `CitySignSupports04` and four mesh
objects: `CitySignSupports04_Hardware`, `CitySignSupports04_ArtworkLower`,
`CitySignSupports04_ArtworkMiddle`, `CitySignSupports04_ArtworkUpper`. Hardware subparts are
joined but remain editable closed connected components; intentionally overlapping joints
are not boolean-unioned. The studio stays outside the export collection. Blender
**5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**, shared
`tools/assets/blender/export_settings.json`, with static animation/skin export disabled.
No prototype dependencies, embedded images, external textures, rig, clips or emission.

Four opaque backface-culled Principled materials match .02/.03: `support_petrol`,
`recess_gasket`, `mount_metal`, `sign_face`; exact linear PBR values are in validation.json.
Hardware has three surfaces; each artwork carrier has two. Default Godot automatic LOD,
tangent and shadow-mesh generation remain on. No measured limit warrants bespoke LODs;
this is not a ratified triangle or performance budget.

**Override only slot 0 `sign_face` on the selected `ArtworkLower/Middle/Upper` mesh.**
Slot 1 `mount_metal` owns its sides/back; the hardware mesh is separate. Three faces share
the neutral default material but remain independently overridable. Use one opaque sRGB
albedo per destination field, white multiplier, clamp rather than repeat, and **129:23**
image aspect (e.g. 1290×230). Arrow outlines clip the texture; put copy inside the safe
rectangle rather than the pointed end. Do not mirror lettering for the middle arrow.
Artwork/materials belong to district owners and never require duplicate support meshes.
No runtime material-swapping API is added.

UV0 `UVMap` spans 0–1 per front face. Viewed from the common front, screen right is -X,
matching .01/.02/.03. Blender U=(R-X)/1.29 and V=(Z-bottom)/0.23, with these literals:

| Carrier | R (Blender X) | Bottom / top (Blender Z = Godot Y) | Safe-copy X range |
| --- | --- | --- | --- |
| Lower | 1.375 | 2.635 / 2.865 | 0.12…1.14 |
| Middle | -0.085 | 3.085 / 3.315 | -1.14…-0.12 |
| Upper | 1.375 | 3.535 / 3.765 | 0.12…1.14 |

Exported glTF V=0 at image top and V=1 at bottom. These triples are also retained under
`artwork_interface.meshes` in validation.json. Source and actual decoded GLB normals/UVs
are checked for each carrier, including upright, nonmirrored middle-arrow mapping.
Backs are deliberately blank hardware, not a second artwork interface. Artwork resolution,
filtering, mip behavior, copy and final readability remain downstream.

## Prefab and bounded collision validation

`Visuals/Model` is an identity-transform linked imported instance, with no embedded render
mesh, editable imported children or runtime-authored hierarchy. `Collision/Body/Shape`
is one CylinderShape3D, **radius 0.20 / height 2.50**, centre **(0,1.25,0)**, static-world
layer **1**, mask **0**. Its full foot-width radius deliberately simplifies the narrower
mast and shoe into one conservative obstruction. Above 2.5 m, the mast/cap/fingers are
visual-only per the standing overhead rule; no false solid box spans the arrow width.
No breakability, authoritative state or new physics behavior is introduced.

Pinned Godot **4.8.dev7.official.c971f93e7** imports and loads four linked meshes/nine
surfaces with expected bounds and the three artwork meshes' face/body slot order intact.
Headless pack/save/reopen/resave preserved normalized scene
bytes and UIDs. Prefab UID `uid://6edr6fd4ydkr`; GLB UID `uid://og5v15ucfr7`.
Scene UID/node identities are embedded; no `.tscn.uid` sidecar is generated. The generated
check script `.gd.uid` is retained. The editor was unavailable: text authoring followed by
headless save/reload was the mandated fallback, not a live-editor synchronization claim.

Physics rays prove a blocked centre at Y=0.7, clear side at X=0.3 and clear overhead at
Y=2.6. Runtime validation instantiates the **production player** (capsule radius 0.35 / height
1.8), calls `ActorMotion.step` for 60 fixed ticks per case and asserts independent endpoint
bounds. Starting at Z=2, authority and replay both stop at **Z=0.550780952 m**; the X=0.65
bypass reaches **Z=-2.999999762 m**. These are bounded production-API collision/movement
checks, not car handling, separate-process network admission/prediction or city-route proof.

## Evidence and measured validation

[Hero](city_sign_supports_04-evidence/hero.png) ·
[Side/rear](city_sign_supports_04-evidence/side.png) ·
[Frame/collar detail](city_sign_supports_04-evidence/detail.png) ·
[47 m / 42° overhead](city_sign_supports_04-evidence/overhead_47m_42deg.png).
All four were personally inspected. Alternating arrow silhouettes, inset faces and restrained
collars read cleanly in close views; the cylindrical foot/mast stays quiet and grounded.

Isolated Blender Cycles CPU, 32 samples/denoising, AgX, **1280×720**, PNG compression 95,
no dithering; all renders are below 216 KB. Hero/side are orthographic scale 8.0, detail
scale 2.5. Overhead is vertically down, north-up perspective, **47 m / 42° vertical FOV**;
720 pixels follows the current lean-evidence cap instead of the historical 800-pixel height.
Exact studio settings are retained in author.py. From overhead, aligned fingers overlap
into a thin quiet crossbar: **the vertical copy and arrow direction are not gameplay-readable
at screen centre**. This must not be the only essential navigation cue. No gratuitous roof
sign or emission was added to disguise that camera limitation. These are not engine captures,
actor-occlusion measurements or district/device lighting acceptance.

[validation.json](city_sign_supports_04-evidence/validation.json): **2,668 triangles;
1,360 source vertices; 1,773 split GLB vertices; four meshes; nine surfaces; zero degenerate
source faces/export triangles; zero nonmanifold source edges; unit source/export normals;
outward exported winding; correct bounds, ground pivot and three independent artwork UVs**.
Fresh export after opening the saved source is **byte-identical**, GLB **80,312 bytes**,
SHA-256 `6635fffeda54231e81db6e69214e82c26d072b5ad157e1930dd1d45ecdd308eb`.
The [manifest](city_sign_supports_04-evidence/manifest.json) hashes every produced payload
except itself. The [concise final log](city_sign_supports_04-evidence/final.log) retains
command outcomes and diagnostics; scratch exports, retry logs and test mirrors stay outside Git.

Canonical production checks pass with explicitly resolved mise tools: GDScript formatting,
style and all-script compilation; **14 Python tests; 86 GUT tests / 2,178 assertions**;
GUT import and intentional-negative failure detection. No pre-existing fixture failures
were waived. Direct pinned gdstyle also passes the owned script.

### Diagnostics and limitations

- The requested default production-check invocation failed before tests: its PATH-shim
  version subprocess hit cp1252 decoding and returned no engine version. Explicit mise
  `--godot`/`--gdstyle` plus `PYTHONUTF8=1` resolved that environment failure.
- The first pinned suite found one owned GDScript wrapping difference (style and compilation
  passed). Pinned `gdstyle fmt` corrected it, then the full suite passed in a fresh output
  directory. No shared tooling/configuration or sibling file was edited.
- Editor save/check assertions pass with exit 0, but shutdown emits GUI RID/ObjectDB leak
  diagnostics (168 objects), matching .02/.03's documented editor baseline. This run does
  **not** claim a clean editor shutdown or a newly reproduced no-asset baseline. Ordinary
  import, runtime checks and canonical isolated checks succeed; runtime has no warning/error
  diagnostics. The development plugin warns that 4.8 is newer than its tested 4.7 version.
- Blender version-only inspection reports one 24-byte shutdown allocation; author/export
  and validation exit 0 without topology/dependency or shutdown errors. Blender also emits
  the existing future `use_nodes` deprecation warning.
- The owner's live Blender/Godot sessions were never accessed. Headless import/save checks
  cannot prove that a separate open editor scene is synchronized.

## Exact reproduction

Run in Bash from the worktree root, using a fresh empty canonical-check output directory:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
NID=city_sign_supports_04
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/author.py
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/validate.py
timeout 300 "$GODOT" --headless --editor --path . --import --quit
timeout 180 "$GODOT" --headless --editor --path . --script res://tools/asset_production/$NID/check_prefab.gd
timeout 180 "$GODOT" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd
timeout 30 "$GDSTYLE" --max-warnings 0 tools/asset_production/$NID/check_prefab.gd
timeout 1800 env PYTHONUTF8=1 python tools/production_checks.py --godot "$GODOT" --gdstyle "$GDSTYLE" --output C:/tmp/ft/assets/$NID/checks-reproduce
```

Validation exports freshly to `C:/tmp/ft/assets/city_sign_supports_04/reexport` and compares
bytes. Export-only: same pinned Blender flags, load the saved `.blend` after
`--factory-startup`, then `--python tools/asset_production/$NID/export.py -- C:/tmp/ft/assets/$NID/export-only`.
Source validation rewrites validation.json: rerun editor/runtime checks afterwards to restore
engine results, then refresh manifest hashes after any artifact changes. Parametric source
rebuild is retained, not a promise of byte-identical `.blend` serialization.

## Remaining acceptance

Independent technical/art review; district artwork; actual engine gameplay-camera/lighting
captures; approved placement and populated actor/target visibility; vehicle movement/query
checks; actual separate-process multiplayer behavior; repeated-placement profiling, packaged
builds and Deck performance remain **pending**. The source/prefab is ready for those downstream
checks, not a blanket production-ready or whole-register acceptance claim. No TODO was closed.
