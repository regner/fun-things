# city_sign_supports.03 — Noticeboard

10 October 2026. **Source/export and linked prefab delivered; independent review and
world/gameplay/device acceptance pending.** Produced by the commissioned implementation
worker on `lane/a-signs`; the production lead owns acceptance and world integration.
[Commission](commission.md) and the current per-asset production brief supersede the
historical concept-only restrictions in [city_sign_supports](../city_sign_supports.md).
No sibling, register, shared brief, world placement, road tool or gameplay code changed.

## Design and dimensions

Original Blender construction: a broad civic multi-notice board with a continuous rounded
petrol frame, recessed neutral artwork field, gasket, closed rear shell, twin posts and
cast shoes/feet. A shallow rain cap and taller notice field distinguish it from the
[low panel .02](city_sign_supports_02.md), while retaining its profile construction,
material names/colors and face-only artwork interface. The panel remains blank: district
artwork owns the multi-notice arrangement and copy, not extra modelled papers or lettering.
No real brands, downloaded geometry, image-to-mesh, texture noise or transparent glazing.

Terrace Ward's communal courts and Old Quay's civic squares are the primary reference uses
from the [district identities](../../concepts/world-v1/stage-03-district-identities/README.md).
No district placement is implied. Use the smaller wall panel where one notice suffices.
Keep this taller board out of passage mouths, narrow walking links and junction views;
its generous face must not hide routes. The rain cap is a static shape, not a weather system.

These are **provisional authored dimensions**, permitted by the current standing production
rules, not concept-image measurements or approved placement envelopes:

| Quantity | Metres / contract |
| --- | --- |
| Overall Godot X/Y/Z size | **1.90 × 2.10 × 0.44** |
| Godot AABB | min `(-0.95,0,-0.22)`, max `(0.95,2.10,0.22)` |
| Pivot | Ground `(0,0,0)`, centred between feet; no buried geometry |
| Panel body | Width 1.80, height 1.20, bottom 0.82, top 2.02 |
| Profile depth | Blender Y=-0.060…0.080; rear shell reaches -0.062 |
| Outer frame corner | Radius 0.060, six segments per quarter |
| Rain cap | 1.90 wide × 0.30 deep × 0.10 high, centre Blender `(0,0.03,2.05)` |
| Posts | Centres X=±0.67; 0.11 square; Blender Y=-0.018; top 1.88 |
| Feet | Each 0.30 wide × 0.44 deep × 0.055 high |
| Artwork face | **1.64 × 1.04**, bottom 0.90, top 1.94; radius 0.022 |
| Artwork plane | Godot Z=-0.071; recessed 0.009 behind frame lip |
| Safe copy rectangle | 1.58 × 0.98, centred in the face |
| Tolerance | Envelope/ground ±0.001; coordinate/UV comparison ±0.00001 |

Metre units, applied rotation/scale, identity root and mesh origins. Blender +Z becomes
Godot +Y; Blender +Y becomes Godot -Z (front). No corrective prefab rotation/scale.

## Source, export, materials and artwork interface

- [Blender source](../../../art/source/models/environment/city_sign_supports_03/city_sign_supports_03.blend)
- [Explicit GLB](../../../art/models/environment/city_sign_supports_03/city_sign_supports_03.glb)
  and its adjacent `.import` metadata.
- [Linked prefab](../../../scenes/prefabs/environment/city_sign_supports_03.tscn)
- [Author](../../../tools/asset_production/city_sign_supports_03/author.py),
  [export](../../../tools/asset_production/city_sign_supports_03/export.py),
  [source/binary validation](../../../tools/asset_production/city_sign_supports_03/validate.py),
  [headless prefab/motion checks](../../../tools/asset_production/city_sign_supports_03/check_prefab.gd).

Collection `export_city_sign_supports_03` contains exactly `CitySignSupports03`,
`CitySignSupports03_Hardware` and `CitySignSupports03_ArtworkCarrier`. Hardware parts are
joined into one mesh with closed, editable connected components. Interlocking components
are not boolean-unioned; each is manifold. The retained studio is outside the export.
Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. The exporter loads
shared `tools/assets/blender/export_settings.json`, selecting only the declared collection
and disabling static animation/skin export. No prototype dependencies.

Four opaque, backface-culled Principled materials: `support_petrol`, `recess_gasket`,
`mount_metal`, `sign_face`, matching .02. Exact linear PBR factors are in validation.json.
Hardware has three surfaces; the artwork carrier has two. No textures, embedded images,
emission, rigs, animations, damage states or sockets are required. Default Godot automatic
LOD, tangent and shadow-mesh generation remain on; this is not a ratified performance budget.

**Override only `CitySignSupports03_ArtworkCarrier` slot 0 `sign_face`.** Slot 1
`mount_metal` owns sides/back; hardware is a separate mesh. UV0 `UVMap` spans the front 0–1
with rounded corners clipping artwork. Use opaque sRGB albedo, white multiplier, clamp
(not repeat), and **41:26** image aspect (e.g. 1640×1040). Filtering/mip/readability review
belongs to the district artwork handoff. Blender UV is U=(0.82-X)/1.64, V=(Z-0.90)/1.04.
Exported glTF V=0 at image top, V=1 at bottom; front-view screen right is -X, matching .01/.02.
Source and actual GLB UVs/normals are validated upright and unmirrored. Multiple notices
belong in one artwork image/material; no new support model is needed for each district.
No runtime material-swapping API or interaction is introduced.

## Prefab and bounded collision validation

`Visuals/Model` is the identity-transform imported instance, with no embedded render mesh,
editable imported children or runtime-authored hierarchy. The standing collision rule
requires a freestanding solid: `Collision/Body/Shape` is one BoxShape3D **(1.90,2.10,0.44)**,
centred at **(0,1.05,0)**, static-world layer **1**, mask **0**. This deliberately conservative
full envelope blocks the under-panel gap and minor empty margins around posts/cap; it is
not a crouch/underpass surface. No breakability, gameplay state or authority changes.

Pinned Godot **4.8.dev7.official.c971f93e7** imported and loaded the model with both meshes,
five surfaces and expected bounds. Headless pack/save/reopen/resave preserved normalized
scene bytes/UIDs. Prefab UID `uid://p0xsrjdmsw2s`; GLB UID `uid://bubc8cpo6gkqt`.
The text scene contains its UID/node identities; no `.tscn.uid` sidecar is generated.
The check script's Godot-generated `.gd.uid` is retained.

Actual physics rays prove a solid centre at Y=0.7, clear side at X=1.05 and clear overhead
at Y=2.3. Runtime validation instantiates the **production player** with capsule radius
0.35/height 1.8 and calls `ActorMotion.step` for 60 fixed ticks per case. Starting at Z=2,
authority and replay both stop at **Z=0.570312202 m**; the X=1.4 bypass reaches
**Z=-2.999999762 m**. Independent endpoint bounds are asserted. These are bounded production
API checks, not vehicle handling, real transport/admission/prediction or city-route proof.

## Evidence and measured validation

[Hero](city_sign_supports_03-evidence/hero.png) ·
[Side/rear](city_sign_supports_03-evidence/side.png) ·
[Cap/frame detail](city_sign_supports_03-evidence/detail.png) ·
[47 m / 42° overhead](city_sign_supports_03-evidence/overhead_47m_42deg.png).
All four were personally inspected: rounded frame highlights, recessed face, simple rear
clamps and grounded feet read cleanly; cap/taller proportions distinguish the noticeboard.

Isolated Blender Cycles CPU, 32 samples/denoising, AgX, 1280×720, PNG compression 95,
no dithering; each PNG is below 240 KB. Hero and side are orthographic scale 4.8; detail
scale 1.4. Overhead is vertical-down, north-up perspective, **47 m height / 42° vertical
FOV**, cropped to the current 720-pixel evidence cap instead of the historical 800-pixel
height. Exact studio settings are in author.py. At gameplay scale the cap forms a quiet
short strip; the vertical face is effectively edge-on at image centre. **Copy is not
readable from this camera and must not be an essential navigation cue.** These are not
engine screenshots or actor/target occlusion, district lighting or device acceptance.

[validation.json](city_sign_supports_03-evidence/validation.json): **2,636 triangles;
1,340 source vertices; 1,711 split GLB vertices; two meshes; five surfaces; zero degenerate
source faces/export triangles; zero nonmanifold source edges; unit-length source/export
normals; outward exported winding; correct pivot, dimensions and artwork mapping**.
Fresh export after opening the saved source is **byte-identical**, GLB **75,520 bytes**,
SHA-256 `f6ed9b4bd732c2e46104cf52453641e6c6e212483dd27d26d33a683dfefbdd8c`.
The [manifest](city_sign_supports_03-evidence/manifest.json) hashes every produced payload
except itself. [Final log](city_sign_supports_03-evidence/final.log) retains concise command
outcomes and diagnostics; scratch exports, check mirrors and raw logs stay outside Git.

Canonical production checks pass with explicitly resolved mise tools: owned GDScript
formatting/lint/all-script compilation; **14 Python tests**; **86 GUT tests / 2,178
assertions**; GUT import and intentional-negative failure detection. Direct pinned gdstyle
reports zero issues. No pre-existing fixture failures needed to be waived.

### Diagnostics and limitations

- The default production-check command failed before tests because its PATH-shim version
  subprocess returned no engine version. Explicit `--godot` and `--gdstyle` from mise,
  with `PYTHONUTF8=1`, resolved it. No shared tool/configuration was edited.
- Editor save/check assertions pass and exit 0, but shutdown emits GUI RID/ObjectDB leak
  diagnostics (168 objects), matching the sibling .02's documented no-asset/editor baseline.
  This run does **not** claim a clean editor shutdown or a newly reproduced baseline.
  Ordinary `--import --quit`, runtime checks and canonical isolated checks succeed; runtime
  has no warning/error diagnostics. The development plugin warns 4.8 is newer than its
  tested 4.7 version during editor startup.
- Blender version-only inspection reports one 24-byte shutdown allocation; author/export
  and validation exit 0 without topology, dependency or shutdown errors.
- Direct scene text authoring followed by headless save/reload is the mandated fallback:
  the windowed editor is unavailable and the owner's live sessions were never accessed.
  Headless import does not synchronize a separate open editor scene.

## Exact reproduction

From the worktree root in Bash; use a new empty output directory for canonical checks:

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
NID=city_sign_supports_03
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

Validation freshly exports to `C:/tmp/ft/assets/city_sign_supports_03/reexport` and compares
the bytes. Export-only: use the same Blender flags, add the saved `.blend` after
`--factory-startup`, then `--python tools/asset_production/$NID/export.py -- C:/tmp/ft/assets/$NID/export-only`.
Source validation rewrites its JSON; run both engine checks afterwards to restore engine
results, and refresh manifest hashes after any artifact changes. Source rebuilds retain
the parametric recipe, not a promise of byte-identical `.blend` file serialization.

## Remaining acceptance

Old Quay noticeboard artwork is delivered in [d05_civic_graphics.02](d05_civic_graphics_02.md);
final copy and placement acceptance remain separate.

Independent technical/art review; actual engine gameplay-camera/lighting captures;
approved placements and populated actor/target visibility; car movement/query
checks; separate-process multiplayer behavior; repeated-placement profiling, packaged
builds and Deck performance remain **pending**. This source/prefab is ready for those
checks, not a whole-register or full production acceptance claim. No TODO was closed.
