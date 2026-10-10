# d01_campus_graphics.01 — Campus-map face

**Artwork, material and linked prefab delivered for independent review.** World placement,
copy approval, gameplay/device and full production acceptance remain pending. Produced by
this lane's commissioned implementation worker; the production lead and independent reviewer
own acceptance. [Commission](commission.md) and the current asset-production instructions
supersede the historical concept-only status of [the family brief](../d01_campus_graphics.md).
No registry, world, shared carrier, gameplay code or family sibling was changed.

## Design and dimensions

Original Northpoint map artwork: a quiet slate field, mint title and open-book/point crest,
warm ivory copy and amber destination badges. Four distinct silhouette keys show the open
main-hall court, oval sports field/pavilion, teaching wings and striped lighthouse. The
institution name **Institute of Almost Knowing**, place names and humorous subtitles are
**provisional copy**, not owner-approved text. The crest is an original provisional family
mark, not a real institution's identity. No downloaded images, external fonts or brands.

The diagram retains the exact selected district outline from record `1` in
[the owner-exported boundary JSON](../../concepts/world-v1/stage-04-streets/district-editor/brackett-districts.json).
Its internal symbols are illustrative, not surveyed buildings or gameplay navigation data.
It follows the [current Northpoint concept](../../concepts/districts-v1/northpoint.md): field
northeast, hall southwest of the field, lighthouse northwest, smaller academic wings south.
The footer explicitly reads **ILLUSTRATIVE / NOT TO SCALE**. There is no player marker,
"you are here", scale bar or invented road network. This is a decorative campus diagram,
not a minimap or another owner of saved road/placement data. The selected district's gross
6.40 ha / 287.3 × 347.2 m bounds are context, not an allocation to this sign.

Reuse the existing [city_sign_supports.03 noticeboard](city_sign_supports_03.md), whose tall,
generous face accommodates the map and legend without inventing another carrier. Its
provisional hardware dimensions are inherited unchanged:

| Quantity | Contract |
| --- | --- |
| Overall Godot X/Y/Z | **1.90 × 2.10 × 0.44 m** |
| AABB | min `(-0.95,0,-0.22)`, max `(0.95,2.10,0.22)` m |
| Pivot / ground | `(0,0,0)`, ground-centred between the feet |
| Artwork field | **1.64 × 1.04 m**, aspect **41:26** |
| Safe copy rectangle | **1.58 × 0.98 m**; 30 unprinted pixels per edge at this resolution |
| Artwork plane | Godot Z=-0.071 m; bottom Y=0.90, top Y=1.94 m |
| Tolerance | Bounds/ground ±0.001 m; decoded UV/coordinates ±0.00001 |

Metre units, identity root/mesh transforms, Blender +Y → Godot -Z front and +Z → +Y up.
UV0 has U left-to-right when viewed from the front (toward local -X); exported V is zero
at image top. No scale correction, mirrored lettering, added mesh or changed collider.

## Source, exports and materials

- [Reproducible artwork source](../../../tools/asset_production/d01_campus_graphics_01/author.py).
  Python **3.14.2**, Pillow **12.3.0**, RGB image drawn at 3× size and downsampled once with
  Lanczos. The final receipt records actual versions; PNG compression level 9.
- [Runtime PNG](../../../art/textures/environment/d01_campus_graphics_01/campus_map_albedo.png),
  **1640×1040**, opaque sRGB albedo, with its Godot-generated `.import` metadata.
- [Material](../../../art/materials/environment/d01_campus_graphics_01/campus_map.tres):
  `campus_map`, white albedo multiplier, roughness **0.65**, linear mipmap filtering,
  clamp/no repeat, backface culling, opaque, no emission, no UV transform, no other maps.
  Import is lossless with mipmaps generated; 3D auto-compression switching is disabled.
- [Saved prefab](../../../scenes/prefabs/environment/d01_campus_graphics_01.tscn), inheriting
  the existing noticeboard prefab rather than duplicating its node hierarchy or geometry.
- Reused source:
  `art/source/models/environment/city_sign_supports_03/city_sign_supports_03.blend`;
  collection `export_city_sign_supports_03`, root `CitySignSupports03`.
- Reused explicit export:
  `art/models/environment/city_sign_supports_03/city_sign_supports_03.glb` and its unchanged
  `.import` identity/settings. [export.py](../../../tools/asset_production/d01_campus_graphics_01/export.py)
  delegates to the carrier owner's exporter and the shared
  `tools/assets/blender/export_settings.json`, writing only scratch output.

**No new `.blend`/GLB is delivered:** the standing artwork-reuse rule requires the existing
Blender-sourced carrier. Original continuous letter skeletons are reused from the committed
Signal Row [letter source](../../../tools/asset_production/d06_commercial_graphics_01/author.py)
and [its extension](../../../tools/asset_production/d06_commercial_graphics_02/author.py),
with only missing campus letters added locally. The imagery, crest, composition and copy
arrangement are original. Input hashes are retained in validation.json. No external font
license or runtime attribution dependency is introduced.

Family reuse contract: `author.py` exposes `PALETTE`, `GLYPHS`, `Canvas` and `crest` for
subsequent campus artwork. Core swatches are slate `#233F4A`, mint `#A3DCC5`, ivory
`#F6F1DC`, amber `#FFC05A`; coral `#FF725D` is limited to the lighthouse stripe. Keep the
crest, institution spelling and restrained accent hierarchy consistent; no shared file
needs modification to create another face.

## Prefab and collision

The prefab inherits `city_sign_supports_03.tscn`. Its `Visuals/Model` remains the unchanged
identity-transform imported instance. The **only** saved appearance override is
`Visuals/Model/CitySignSupports03/CitySignSupports03_ArtworkCarrier`, surface **0**
`sign_face`. Surface 1 `mount_metal` retains the sides/back; the separate hardware mesh is
unchanged. No runtime swapping script or hierarchy builder is added.

This explicitly uses the authorized **static artwork-on-reused-carrier editable-child
exception** in [assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement).
Two save/reload cycles after normalization preserved the **prefab bytes**; the material was
saved repeatedly from memory with byte-identical results but was not reloaded between saves.
Three matching SHA-256 entries for each are retained in validation.json. Scene identities,
ancestry and UIDs remain unchanged across the prefab cycles. The runtime checker also
requires registered UIDs (not text-path fallback), identical hierarchy/transforms/imported
mesh resources, exactly one face override, and all material/texture settings.

Prefab UID `uid://deuwcyvy7lkbv`; material UID `uid://d154r2tsfhp48`; texture UID
`uid://bt063qhei15cg`. Godot stores scene/material UIDs inside these resources, not separate
`.tscn.uid` files. The checker has its generated `.gd.uid` sidecar.

The inherited **one BoxShape3D (1.90,2.10,0.44)** at `(0,1.05,0)` remains on
`Collision/Body/Shape`, static-world layer **1**, mask **0**. The carrier's deliberate full
box includes the gap under the panel and prevents walking through the freestanding prop.
The checker asserts shape resource identity, dimensions, transform, enabled state and masks
against the original prefab; artwork adds no physics. Existing bounded actor/ray checks
belong to the carrier handoff and were **not rerun or claimed as new gameplay evidence**.
Placement must keep this tall panel out of passage mouths and camera-critical routes.

## Evidence and validation

[Hero](d01_campus_graphics_01-evidence/hero.png) ·
[Side/rear](d01_campus_graphics_01-evidence/side.png) ·
[Artwork detail](d01_campus_graphics_01-evidence/detail.png) ·
[47 m / 42° overhead](d01_campus_graphics_01-evidence/overhead_47m_42deg.png).

All four were personally inspected. Title/crest, diagram and four-row legend separate
cleanly before the small humorous subtitles are readable. Symbols and warm keys stay
inside the district outline, copy stays within the safe frame margins, and lettering is
upright/unmirrored. The side image confirms the existing blank rear/hardware. No source
geometry was edited for rendering.

Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`, Cycles CPU 32 samples, denoising,
AgX, **1280×720**, RGB PNG compression 95, no dithering. The unchanged carrier's studio
supplies lighting/ground; [preview.py](../../../tools/asset_production/d01_campus_graphics_01/preview.py)
records exact cameras. Hero/side/detail are orthographic scales 4.3/4.8/2.05 m. Overhead
is vertical-down north-up perspective, **47 m height / 42° vertical FOV**, at the current
720-pixel evidence cap. **The centred vertical face is edge-on and copy is unreadable at
this gameplay view. It cannot be an essential navigation cue.** No oversized roof sign,
emission or tilted hardware was added to disguise that limitation. These are Blender
renders, not engine lighting/device or actual gameplay-camera acceptance.

[validation.json](d01_campus_graphics_01-evidence/validation.json) records fresh measurements:
**1,340 source vertices; 1,711 split GLB vertices; 2,636 triangles; two meshes; five
surfaces; zero degenerate source faces/exported triangles; zero nonmanifold edges;
unit source/export normals; outward winding; correct bounds, pivot and face UV mapping**.
The source, existing GLB and base prefab remain byte-identical before/after the checks.
Fresh shared-contract export reproduces the committed GLB exactly: **75,520 bytes**,
SHA-256 `f6ed9b4bd732c2e46104cf52453641e6c6e212483dd27d26d33a683dfefbdd8c`.
The PNG also reproduces byte-for-byte from the committed drawing script.

Five Python tests pass: opaque size/aspect; fresh PNG byte equality; independent safe
margin bounds; independent interior color samples for large landmarks/crest; no duplicate
carrier source/export. Pinned gdstyle formatting and lint pass with zero issues. Pinned
Godot **4.8.dev7.official.c971f93e7** import completes without `ERROR`/`SCRIPT ERROR`;
runtime prefab load/inspection completes without warning/error diagnostics. Two saved
roundtrips for both resources are byte-stable. The [manifest](d01_campus_graphics_01-evidence/manifest.json)
hashes every delivered payload except itself; [final.log](d01_campus_graphics_01-evidence/final.log)
retains concise outcomes. Scratch exports/retry logs remain in `C:/tmp/ft/assets/d01_campus_graphics_01/`.

### Diagnostics and limitations

- The required editor fallback is direct text authoring followed by isolated headless
  save/reload. The windowed editor is unavailable; no owner's live Blender/Godot session
  was accessed. Headless import cannot synchronize a separate open scene.
- Headless editor save/check assertions pass and exit 0, but shutdown reports the same
  scan-abort/RID/ObjectDB leak pattern documented by the carrier (168 objects). This is
  **not a clean editor-shutdown claim** or a newly reproduced empty-project baseline.
  Final ordinary import has no errors; runtime inspection has no warnings/errors.
- Import/editor startup emits the existing MCP plugin warning that 4.8 is newer than
  its tested 4.7. No plugin or project settings were changed and nothing was suppressed.
- Initial runtime saw a newly saved material UID before a filesystem scan had registered
  it. A pinned import resolved registration; final checks explicitly require registered
  dependency UIDs. An initial missing `Q` glyph and two owned lint limits were corrected
  before final validation. Blender emits the existing `use_nodes` deprecation notice.

## Exact reproduction

From the worktree root in Bash. Never launch a windowed editor or use a live MCP session.
`validate.py` resets the source receipt; collect the engine evidence afterwards. Final
`audit.py --write` must run after the last documentation or payload edit.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
NID=d01_campus_graphics_01
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
mkdir -p C:/tmp/ft/assets/$NID
python tools/asset_production/$NID/author.py
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/validate.py
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/preview.py
timeout 300 "$GODOT" --headless --path . --import
timeout 180 "$GODOT" --headless --editor --path . --script res://tools/asset_production/$NID/check_prefab.gd -- --normalize
cp C:/tmp/ft/assets/$NID/prefab.json C:/tmp/ft/assets/$NID/normalize.json
timeout 300 "$GODOT" --headless --path . --import > C:/tmp/ft/assets/$NID/import-final.log 2>&1
timeout 180 "$GODOT" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd > C:/tmp/ft/assets/$NID/runtime.log 2>&1
python tools/asset_production/$NID/test_artwork.py
timeout 30 "$GDSTYLE" fmt --check tools/asset_production/$NID/check_prefab.gd
timeout 30 "$GDSTYLE" --max-line-length 100 --max-warnings 0 tools/asset_production/$NID/check_prefab.gd
python tools/asset_production/$NID/audit.py --collect
python tools/asset_production/$NID/audit.py --write
python tools/asset_production/$NID/audit.py
```

For scratch-only reexport, use the same bounded Blender flags with
`--python tools/asset_production/$NID/export.py -- C:/tmp/ft/assets/$NID/reexport`.
No production-check suite was run (decision 52); validation is bounded to this asset.

## Remaining acceptance

Independent art/technical review; provisional institution/place/copy approval and supporting
map use; approved saved placement and authoritative final map content; actual engine
camera/lighting and populated actor/target visibility; vehicle/movement/query checks for
placements; separate-process multiplayer implications; repeated-placement profiling,
packaged builds and Deck readability/performance remain **pending**. This asset adds no
interactions, navigation, destruction, animation or light simulation. No world placement,
whole-register completion, gameplay readiness or TODO closure is claimed.
