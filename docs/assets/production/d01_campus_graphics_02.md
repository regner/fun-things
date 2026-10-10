# d01_campus_graphics.02 — Entry panel face

**Artwork, material and linked prefab delivered for independent review.** Placement,
copy approval and full gameplay/device acceptance remain pending. Produced by the
commissioned implementation worker on `lane/a-campus`; the production lead and independent
reviewer own acceptance. The [commission](commission.md) and current production instructions
supersede the historical concept-only status of [the family brief](../d01_campus_graphics.md).
No world, registry, shared carrier, gameplay code or sibling payload was changed.

## Design and dimensions

Original Northpoint entry artwork gives the provisional **Institute of Almost Knowing** name
two broad rows, with the larger mint **ALMOST KNOWING** line as the primary cue. A mint open
book and warm point crest, quiet slate field, ivory supporting title, amber **ENTRY** and
**QUESTIONS WELCOME** labels preserve the [campus-map sibling's](d01_campus_graphics_01.md)
family language. **NORTHPOINT** is secondary district copy. Names, crest and wording remain
provisional, not owner-approved institutional branding. No real brands, downloaded images,
external fonts, map/navigation data or route arrows were introduced.

The [approved Northpoint identity](../../concepts/world-v1/stage-03-district-identities/README.md#northpoint--the-citys-breathing-space)
calls for earnest, quietly eccentric entrances with mint and restrained warm accents. The
[current street context](../../concepts/world-v1/stage-04-streets/README.md) has large campus
plots and quieter courts. The selected district's 6.40 ha / 287.3 × 347.2 m bounds are context,
not a placement allocation. This delivery chooses no parcel, road connection or entrance site.

Reuse [city_sign_supports.02](city_sign_supports_02.md), the existing broad low freestanding
panel. Its geometry, UVs and collider remain unchanged. This is an entry marker, not a
replacement wall plaque or an essential overhead navigation cue. Inherited dimensions are
**provisional authored values**, not measurements inferred from concept imagery:

| Quantity | Contract |
| --- | --- |
| Overall Godot X/Y/Z | **1.60 × 1.35 × 0.40 m** |
| Godot AABB | min `(-0.80,0,-0.20)`, max `(0.80,1.35,0.20)` m |
| Pivot / ground | `(0,0,0)`, ground-centred between feet |
| Artwork face | **1.44 × 0.39 m**, aspect **48:13** |
| Safe copy rectangle | **1.38 × 0.33 m**; 30-pixel inset at this resolution |
| Artwork plane | Godot Z=-0.071 m; bottom Y=0.88, top Y=1.27 m |
| Tolerance | Bounds/ground ±0.001 m; decoded UV/coordinates ±0.00001 |

Metre units and identity root/mesh transforms; Blender +Y → Godot -Z front, +Z → +Y up.
Front-view screen right is -X. UV0 maps U left-to-right, exported V=0 at image top;
actual UVs/normals are checked to avoid mirrored or inverted lettering. Rounded face corners
clip only the unprinted field. There is no corrective scale/rotation or overhanging artwork.

## Source, exports and materials

- [author.py](../../../tools/asset_production/d01_campus_graphics_02/author.py) is the original,
  reproducible 2D source, using Python **3.14.2** / Pillow **12.3.0**, RGB at 3× resolution,
  one Lanczos downsample and PNG compression level 9.
- [entry_panel_albedo.png](../../../art/textures/environment/d01_campus_graphics_02/entry_panel_albedo.png):
  **1440×390**, opaque sRGB albedo, 1000 pixels/metre, with committed `.import` metadata.
- [entry_panel.tres](../../../art/materials/environment/d01_campus_graphics_02/entry_panel.tres):
  white albedo multiplier, roughness **0.65**, linear mipmap filtering, clamp/no repeat,
  backface culling, opaque, no emission or UV transform. No normal/ORM/other texture maps.
  Texture import is lossless with mipmaps; automatic 3D compression switching is disabled.
- [Linked prefab](../../../scenes/prefabs/environment/d01_campus_graphics_02.tscn) inherits
  `city_sign_supports_02.tscn`, with only the face-slot material override.
- Existing Blender source:
  `art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend`;
  collection `export_city_sign_supports_02`, root `CitySignSupports02`, meshes
  `CitySignSupports02_Hardware` and `CitySignSupports02_ArtworkCarrier`.
- Existing explicit export:
  `art/models/environment/city_sign_supports_02/city_sign_supports_02.glb` and unchanged
  `.import`. [export.py](../../../tools/asset_production/d01_campus_graphics_02/export.py)
  reopens that source and delegates to its owner's exporter and the shared
  `tools/assets/blender/export_settings.json`, writing only scratch output.

**No duplicate `.blend` or GLB is delivered.** The standing artwork-reuse rule requires the
existing Blender-authored carrier. The original campus crest, palette and continuous letter
paths are imported from the [campus-map author](../../../tools/asset_production/d01_campus_graphics_01/author.py),
which traces letter construction to the two committed Signal Row artwork sources. Their
hashes are recorded in validation.json. No system fonts or third-party attribution are needed.
This face adds its own composition, not a fork of the family identity. Core colors remain
slate `#233F4A`, mint `#A3DCC5`, ivory `#F6F1DC`, amber `#FFC05A`.

## Prefab and collision

`Visuals/Model` remains the identity-transform linked import. The only appearance override
is `Visuals/Model/CitySignSupports02/CitySignSupports02_ArtworkCarrier`, surface **0**
`sign_face`. Surface 1 `mount_metal` keeps the sides/back unprinted; hardware is unchanged.
No embedded render mesh, runtime material-swapping script or hierarchy builder is added.

This uses the authorized **static artwork-on-reused-carrier editable-child exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement). After initial normalization,
two actual load/save cycles preserve both scene and material bytes; validation.json retains
three identical SHA-256 values for each. The checker reloads the material from disk too.
Unchanged bytes prove unchanged serialized identities/UIDs. It also checks registered
resource UIDs without path-fallback acceptance, exact inherited hierarchy/transforms,
imported mesh resource identity, one face-only override and the texture/material settings.

Prefab UID `uid://0hwlev2x3pae`; material UID `uid://d3n3s0r8oujs0`; texture UID
`uid://cmx5x6kcxhc6`. Scene/material UIDs are embedded in their resources, not `.tscn.uid`
sidecars. The checker has its engine-generated `.gd.uid` sidecar.

The inherited **one BoxShape3D (1.60,1.35,0.40)** at `(0,0.675,0)` on
`Collision/Body/Shape` is preserved, static-world layer **1**, mask **0**. The full box
intentionally blocks the visual gap below the face. The checker compares shape resource
identity, size, position, enabled state and masks with the original support. Artwork adds
no physics or gameplay state. The carrier's existing bounded actor/ray checks were **not
rerun or claimed as new evidence**. Keep placement out of passage mouths and junction views.

## Evidence and validation

[Hero](d01_campus_graphics_02-evidence/hero.png) ·
[Side/rear](d01_campus_graphics_02-evidence/side.png) ·
[Face detail](d01_campus_graphics_02-evidence/detail.png) ·
[47 m / 42° overhead](d01_campus_graphics_02-evidence/overhead_47m_42deg.png).

All four renders and the runtime PNG were personally inspected. Broad title and crest read
before small footer copy; generous margins remain clear of the frame and lettering is upright,
unmirrored. The side/rear view confirms unprinted backing and unchanged supports. The detail
shows the face only, intentionally cropping the lower posts. No carrier source was saved or
modified during rendering.

Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; Cycles CPU
32 samples, denoising, AgX, RGB **1280×720**, compression 95, no dithering. Existing carrier
studio lights/ground are reused. [preview.py](../../../tools/asset_production/d01_campus_graphics_02/preview.py)
records exact cameras; hero/side/detail orthographic scales are 3.0/3.2/1.7 m. The overhead
is vertical-down, north-up perspective at **47 m height / 42° vertical FOV**, using the
current 720-pixel evidence cap. **The centred vertical face is edge-on and its copy is not
readable in this gameplay view.** This cannot be the only mandatory wayfinding cue. No
artificially tilted face, emissive treatment or duplicate roof sign hides that limitation.
These are Blender previews, not accepted engine lighting, placement or device captures.

[validation.json](d01_campus_graphics_02-evidence/validation.json) records fresh checks:
**1,244 source vertices; 1,596 split GLB vertices; 2,448 triangles; two meshes; five surfaces;
zero degenerate source faces/export triangles; zero nonmanifold edges; unit source/export
normals; outward winding; correct bounds, ground pivot and face UV mapping**. Source, GLB
and base prefab hashes are unchanged before/after validation. Fresh shared-contract reexport
is byte-identical: **70,712 bytes**, SHA-256
`022dd559334d79c482182083be775c692ab4adf2a5277d3fb7ca7ec266ec76b7`.
The PNG also reproduces byte-for-byte.

Six Python tests pass: dimensions/opacity; PNG reproduction; safe margins; independent crest
pixels/title hierarchy; linked family language; absence of duplicate carrier geometry. Pinned
gdstyle formatting and lint pass with zero issues. Godot **4.8.dev7.official.c971f93e7** final
headless import has no `ERROR`/`SCRIPT ERROR`; runtime load/inspection has no warnings/errors.
Both scene/material roundtrips are byte-stable. [manifest.json](d01_campus_graphics_02-evidence/manifest.json)
hashes all delivered payloads except itself; [final.log](d01_campus_graphics_02-evidence/final.log)
retains concise final outcomes. Scratch logs and reexports remain outside the repository at
`C:/tmp/ft/assets/d01_campus_graphics_02/`.

### Diagnostics and limitations

- Direct text scene authoring followed by isolated headless normalization is the required
  fallback: the windowed editor is unavailable. No owner's live Blender/Godot session was
  accessed. Headless import does not synchronize a separately open scene.
- Headless editor save assertions pass with exit 0, but shutdown emits scan-abort and
  RID/ObjectDB leaks (168 objects), the same pattern documented by the carrier and campus-map
  sibling. This is **not a clean editor-shutdown claim** or a newly run empty-project baseline.
  Final ordinary import and runtime validation are clean at their stated scopes.
- Editor/import startup has the existing MCP plugin warning about 4.8 being newer than its
  tested 4.7 version. Blender preview emits the existing `use_nodes` deprecation warning.
  No diagnostic is suppressed and no plugin/project configuration was edited.
- Initial artwork test demanded too many exact-color pixels in antialiased thin lettering.
  It was corrected to require over 10% near-color ink in independently fixed title regions;
  visual artwork was not changed to satisfy it. One checker function-length lint finding
  after adding actual material reloads was resolved with a named reload/save helper.
- The earlier campus-map handoff contains no stale pending entry-panel item, so no sibling
  document or historical receipt required modification.

## Exact reproduction

Run from the worktree root in Bash. Source validation resets the receipt; collect engine
results afterwards. Run `audit.py --write` last, after all payload/documentation changes.

```sh
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
NID=d01_campus_graphics_02
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

Independent art/technical review; provisional institution/district/copy approval; approved
saved entrance placement; actual engine camera/lighting and populated actor/target visibility;
placement movement/query/vehicle checks and separate-process multiplayer implications;
repeated-placement profiling, packaged builds and Deck readability/performance remain
**pending**. This delivery adds no interactions, animation, navigation or destruction.
No world placement, whole-register completion, gameplay readiness or TODO closure is claimed.
