# d01_campus_graphics.03 — Route-arrow set

**Three artwork/material/linked-prefab variants delivered for independent review.**
Copy approval, placement and full gameplay/device acceptance remain pending. Produced by
this lane's commissioned implementation worker; production lead and independent reviewer
own acceptance. The [commission](commission.md) and current asset-production instructions
supersede the historical concept-only status of [the family brief](../d01_campus_graphics.md).
No world, registry, shared carrier, gameplay code or sibling payload was changed.

## Design and dimensions

Original **left, ahead and right** arrow faces: broad solid mint silhouettes, slate field,
ivory **CAMPUS ROUTE** title, mint **NORTHPOINT**, restrained amber institution line and the
existing open-book/point campus crest. Only the arrow changes between variants; all lettering
and the crest remain identical and unmirrored. The visual hierarchy keeps direction primary
before the small copy is readable. Names, crest, wording and supporting route-marker use
remain **provisional**, not approved branding or a surveyed route specification.

This follows the [Northpoint identity](../../concepts/world-v1/stage-03-district-identities/README.md#northpoint--the-citys-breathing-space):
earnest, quietly eccentric mint entrances and route markers against calmer campus courts.
The [current street context](../../concepts/world-v1/stage-04-streets/README.md) preserves large
campus plots and quiet walking paths. District bounds of 6.40 ha / 287.3 × 347.2 m are context,
not an allocation or chosen sign placement. No destination/direction pair, route topology,
distance, road symbol or gameplay navigation data is invented by this set.

The [campus map](d01_campus_graphics_01.md) and [entry face](d01_campus_graphics_02.md) supply
the existing family palette, original continuous letter paths and crest. Reuse the entry
face's [city_sign_supports.02](city_sign_supports_02.md) low freestanding hardware, unchanged:

| Quantity | Inherited provisional contract |
| --- | --- |
| Overall Godot X/Y/Z | **1.60 × 1.35 × 0.40 m** |
| Godot AABB | min `(-0.80,0,-0.20)`, max `(0.80,1.35,0.20)` m |
| Pivot / ground | `(0,0,0)`, ground-centred between feet |
| Artwork face | **1.44 × 0.39 m**, aspect **48:13** |
| Safe copy rectangle | **1.38 × 0.33 m**, 30-pixel inset at this resolution |
| Artwork plane | Godot Z=-0.071 m; bottom Y=0.88, top Y=1.27 m |
| Tolerances | Bounds/ground ±0.001 m; decoded coordinates/UV ±0.00001 |

Metre units; identity root/mesh transforms; Blender +Y → Godot -Z front and +Z → +Y up.
Front-view screen right is -X. UV0 maps U left-to-right; exported V=0 is the image top.
The arrows are relative to the viewer facing the sign: left/right on the printed face;
up means **continue ahead**, not north, stairs or an upper floor. Placement must orient the
whole prefab to its approach and verify the intended route; do not rotate/mirror only its
texture or infer a world-space route vector from the image. There is no runtime navigation API.

## Source, exports and materials

- Original reproducible 2D source:
  [author.py](../../../tools/asset_production/d01_campus_graphics_03/author.py), Python
  **3.14.2**, Pillow **12.3.0**, RGB drawn at 3× resolution and downsampled once with Lanczos.
- Three runtime **1440×390** opaque sRGB PNGs (1000 pixels/metre, PNG compression level 9):
  `art/textures/environment/d01_campus_graphics_03/route_{left,ahead,right}_albedo.png`,
  each with its pinned-engine `.import` metadata.
- Three materials:
  `art/materials/environment/d01_campus_graphics_03/route_{left,ahead,right}.tres`.
  White albedo multiplier, roughness **0.65**, linear mipmap filtering, clamp/no repeat,
  backface culling, opaque, no emission, no UV transform or other maps. Texture import is
  lossless with mipmaps; automatic 3D compression switching is disabled.
- Shared Blender source:
  `art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend`,
  collection `export_city_sign_supports_02`, root `CitySignSupports02`, children
  `CitySignSupports02_Hardware` and `CitySignSupports02_ArtworkCarrier`.
- Shared explicit export:
  `art/models/environment/city_sign_supports_02/city_sign_supports_02.glb` and unchanged
  `.import`. [export.py](../../../tools/asset_production/d01_campus_graphics_03/export.py)
  delegates to the existing carrier exporter and shared
  `tools/assets/blender/export_settings.json`, writing only scratch output.

**No duplicate `.blend` or GLB is delivered:** the standing artwork-reuse rule requires the
existing Blender-authored carrier. Original arrows and composition are authored here; the
palette, continuous letters and crest are imported through the entry/map sibling sources,
which trace lettering to the two committed Signal Row artwork sources. Input hashes are in
validation.json. No system fonts, external images, real brands or attribution dependency.
Core swatches remain slate `#233F4A`, mint `#A3DCC5`, ivory `#F6F1DC`, amber `#FFC05A`.

## Prefabs and collision

| Variant | Saved prefab under `scenes/prefabs/environment/` | Prefab UID |
| --- | --- | --- |
| Ahead (default) | `d01_campus_graphics_03.tscn` | `uid://bxd0fk6sf45tt` |
| Left | `d01_campus_graphics_03_left.tscn` | `uid://dmogd4vaghn0c` |
| Right | `d01_campus_graphics_03_right.tscn` | `uid://cffgq2llp5l0` |

Each inherits `city_sign_supports_02.tscn`. `Visuals/Model` stays the identity-transform
imported instance. The only saved appearance override is
`Visuals/Model/CitySignSupports02/CitySignSupports02_ArtworkCarrier`, surface **0** `sign_face`.
Surface 1 `mount_metal` retains the unprinted rear/sides; the hardware is unchanged.
There is no embedded mesh, runtime material switcher or runtime-built hierarchy.

This uses the authorized **static artwork-on-reused-carrier editable-child exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement). After normalization,
two actual reload/save cycles preserve bytes for **all three scenes and all three materials**;
validation.json retains three equal hashes per resource. Thus serialized identities/UIDs
remain unchanged. Scene/material UIDs are embedded rather than separate `.tscn.uid` files;
the checker has its Godot-generated `.gd.uid`. Runtime checks require registered dependency
UIDs (not text-path fallback), unchanged hierarchy/transforms/imported mesh resources, exactly
one correct face override, correct material/texture settings and the inherited collider.

Every variant retains the carrier-owned **one BoxShape3D (1.60,1.35,0.40)** at
`(0,0.675,0)` on `Collision/Body/Shape`, static-world layer **1**, mask **0**. This deliberate
full box blocks the visual gap beneath the sign; it must not be placed across a walking path.
The checker compares shape identity, size, transform, enabled state and layers/masks with the
original support. Artwork adds no physics. Existing carrier movement/ray checks are **not
rerun or claimed as new evidence**. Placement-specific actor/car/query checks remain required.

## Evidence and validation

[Hero: all three variants](d01_campus_graphics_03-evidence/hero.png) ·
[Side/rear](d01_campus_graphics_03-evidence/side.png) ·
[Ahead detail](d01_campus_graphics_03-evidence/detail.png) ·
[47 m / 42° overhead](d01_campus_graphics_03-evidence/overhead_47m_42deg.png).

All four renders and the runtime artwork were personally inspected. Arrows distinguish
clearly, copy stays upright and margins remain clear of the frame; the family crest and calm
palette match the earlier faces. Side/rear confirms the backing remains unprinted. Hero uses
three temporary unchanged-source instances for comparison, not a saved world arrangement.

Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**, Cycles CPU 32 samples,
denoising, AgX, RGB **1280×720**, compression 95, no dithering. Existing carrier studio
lights/ground are reused. [preview.py](../../../tools/asset_production/d01_campus_graphics_03/preview.py)
records exact cameras and temporary comparison positions; hero/side/detail orthographic
scales are 6.6/3.2/1.7 m. The overhead is vertical-down north-up perspective, **47 m height /
42° vertical FOV**, under the current 720-pixel evidence cap. **The vertical faces are edge-on;
arrows and copy are unreadable from this centred gameplay view.** These decorative approach
markers cannot be an essential or sole gameplay navigation cue. No tilted face, emission or
oversized roof sign hides that inherited limitation. Renders are isolated Blender evidence,
not approved engine lighting, gameplay placement or device captures. Each PNG is below 400 KB.

[validation.json](d01_campus_graphics_03-evidence/validation.json) freshly measures the reused
carrier: **1,244 source vertices; 1,596 split GLB vertices; 2,448 triangles; two meshes;
five surfaces; zero degenerate source faces/export triangles; zero nonmanifold edges; unit
source/export normals; outward winding; correct bounds, pivot and face UVs**. Counts are per
carrier; variants reuse the same geometry. Source, GLB and base prefab remain unchanged.
Fresh shared-contract export is byte-identical: **70,712 bytes**, SHA-256
`022dd559334d79c482182083be775c692ab4adf2a5277d3fb7ca7ec266ec76b7`.
All three PNGs reproduce byte-for-byte. The validator delegates to the sibling's existing
same-carrier assertions, redirecting only its output receipt and scratch exporter; it never
writes sibling evidence. Shared validation-tool hashes are retained for reproducibility.

**Seven Python tests pass**: dimensions/opacity; exact PNG reproduction; independent safe
margins; literal arrow-direction pixels and reduced silhouettes; identical unmirrored common
identity; three linked prefabs/no duplicate carrier; rejection of unknown variants. Pinned
gdstyle format/lint pass with zero issues. Godot **4.8.dev7.official.c971f93e7** final headless
import has no `ERROR`/`SCRIPT ERROR`; runtime load/inspection has no warnings/errors. Six
resource roundtrip checks are byte-stable. [manifest.json](d01_campus_graphics_03-evidence/manifest.json)
hashes all delivered payloads except itself; [final.log](d01_campus_graphics_03-evidence/final.log)
retains concise outcomes. Scratch logs/reexports stay in `C:/tmp/ft/assets/d01_campus_graphics_03/`.

### Diagnostics and limitations

- Required editor fallback: direct text resource authoring, isolated headless normalization
  and actual save/reload. The windowed editor is unavailable; no owner's live Blender/Godot
  session was accessed. Headless import does not synchronize a separately open scene.
- Editor save assertions pass and exit 0, but shutdown reports the known scan-abort and
  RID/ObjectDB leak pattern (168 objects), also documented by the carrier and siblings.
  This is **not a clean editor-shutdown claim** or a newly run empty-project baseline.
  Ordinary final import and runtime checks are clean at their stated scopes.
- Startup includes the existing MCP compatibility warning for Godot 4.8 versus its tested
  4.7. Blender emits its existing `use_nodes` deprecation warning. Nothing is suppressed.
- Initial owned lint found dictionary spacing and one long line; both were corrected.
  An initial arrow test sampled outside a triangular shoulder; samples were moved into the
  independently chosen shoulder interiors. Artwork was not changed to satisfy the test.
- Neither earlier sibling's current handoff lists a pending route-arrow delivery. No sibling
  document/manifest update is required, and historical receipts remain unchanged.

## Exact reproduction

From the worktree root in Bash. Source validation resets the receipt; collect engine results
afterwards. Run `audit.py --write` last after all payload/documentation edits.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
NID=d01_campus_graphics_03
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

For scratch-only export use the same bounded Blender flags with
`--python tools/asset_production/$NID/export.py -- C:/tmp/ft/assets/$NID/reexport`.
No broad production-check suite ran (decision 52); validation is bounded to this asset.

## Remaining acceptance

Independent art/technical review; supporting-use and provisional institution/district/copy
approval; approved saved placements with verified approach-relative directions; actual engine
camera/lighting and populated actor/target visibility; placement movement/query/vehicle checks
and separate-process multiplayer implications; repeated-placement profiling, packaged builds
and Deck readability/performance remain **pending**. No navigation, interaction, destruction,
animation or lighting simulation is added. No whole-register completion, world placement,
gameplay readiness or TODO closure is claimed.
