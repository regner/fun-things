# d05_civic_graphics.04 — Warm shop-front fascia artwork set

10 October 2026. **Three artwork/material/prefab variants delivered; bounded producer checks
pass. Independent review, final copy selection and world/device acceptance remain pending.**
Produced by the isolated implementation worker on `lane/a-d05`; parent/reviewer owns acceptance.
The current common production brief and [commission](commission.md) supersede the historical
concept-only scope of [Harbour civic graphics](../d05_civic_graphics.md).

## Design and provenance

Three **provisional** fictional waterfront tenants, each with a distinct original trade emblem:

| Variant | Main copy | Secondary copy | Emblem / field |
| --- | --- | --- | --- |
| `tide_tea` | TIDE TEA | TEA AT YOUR OWN PACE | Steaming cup and saucer / slate |
| `quay_pantry` | QUAY PANTRY | DAILY GOODS | Broad pantry jar / muted plum |
| `hem_repairs` | HEM REPAIRS | A STITCH IN QUAY TIME | Thread spool / slate |

Three is the bounded production proposal for the brief's open artwork count, not a required
placed quantity. The ordinary tea shop, grocer and clothing repair shop suit the quay's small
shop-homes. No interaction, opening hours, inventory, quest or new business simulation is implied.

The earlier [hall](d05_civic_graphics_01.md), [noticeboard](d05_civic_graphics_02.md) and
[direction panel](d05_civic_graphics_03.md) establish slate **#344953**, ivory **#F6F1DC** and
muted amber **#E9B96E**. This set adds quiet plum **#514452**, as requested by the family brief.
Broad ivory capitals and one small amber aside leave more than 75% of each face as quiet field.
There is no emission, neon tubing, luminous outline, grunge, microprint or texture noise.

`author.py` imports the existing family capital paths/palette and draws original continuous
trade-symbol paths. Python **3.14.2** / Pillow **12.3.0**, 3x supersampling and one Lanczos
downsample. No external fonts, real brands, downloads, purchased/generated images, or separate
font licensing payload. The reusable lettering dependencies remain unchanged and are hashed.

References read: Petrol & Coral direction; approved Stage 3 Old Quay identity; Stage 4 smaller
quay streets; Old Quay asset breakdown and shared concept contract; shared shop fitting and
fascia handoffs; all three earlier civic deliveries; city_lights.01 source/export/evidence and
batch 01–03 prefab conventions. Concepts informed style, not raster-derived dimensions.

## Source, exports and materials

The standing reuse rule applies: **no duplicate per-ID .blend, GLB, face mesh or exporter**.
The reproducible editable artwork source is `tools/asset_production/d05_civic_graphics_04/author.py`.
All three variants reuse the complete existing [fascia hardware](city_shop_fittings_02.md):

- Blender source: `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
- Collection/root: `export_city_shop_fittings_02` / `city_shop_fittings_02`.
- Export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`.
- Base prefab: `scenes/prefabs/environment/city_shop_fittings_02.tscn`.
- `validate.py` calls the hall's existing reusable fascia audit with its scratch/evidence paths
  redirected. That audit invokes the hardware exporter and independent binary decoder with the
  shared export settings unchanged. No dependency is saved; reexports stay in external scratch.

Runtime paths for each variant in the table:

- Texture: `art/textures/environment/d05_civic_graphics_04/<variant>_albedo.png` plus `.import`.
- Material: `art/materials/environment/d05_civic_graphics_04/<variant>.tres`.
- Prefab: `scenes/prefabs/environment/d05_civic_graphics_04_<variant>.tscn`.

Each image is **2000 x 400 RGB**, 5:1, opaque sRGB albedo. No normal/ORM/emission maps or
embedded images. Materials use white albedo multiplier, metallic 0, roughness **0.56**, backface
culling, opaque/no emission, linear mipmapped filtering and clamp/no repeat. Texture import is
lossless, mipmaps enabled, automatic 3D compression changes disabled. Saved engine-generated
material, scene and texture UIDs remain linked. No runtime material writer or UV correction.

Final texture sizes and SHA-256, copied from the final validation receipt:

| Texture | Bytes | SHA-256 |
| --- | ---: | --- |
| `tide_tea_albedo.png` | 39129 | `b4d075ceb31d439a42d0a9a6035a79de1d32246e758f2ba163e8c04cc2cbf4c1` |
| `quay_pantry_albedo.png` | 46393 | `a9abe2ce9e298680afcbcf7cd0719eadff6dface4b191fce40b3b20b7395c4a0` |
| `hem_repairs_albedo.png` | 49687 | `c427fb527d2452a7d05164d6e3c595bd13f951e6129ec2f93620b62025d8122f` |

## Dimensions, placement interface and collision

Inherited hardware measurements in Godot metres; tolerance +/-0.001 m:

| Interface | Contract |
| --- | --- |
| Overall X/Y/Z | **3.200 x 0.800 x 0.140** |
| AABB | min **(-1.600,-0.400,-0.140)**; max **(1.600,0.400,0)** |
| Pivot | Wall-contact centre `(0,0,0)`, not ground-mounted |
| Artwork plane | **3.000 x 0.600**, Godot Z=**-0.128** |
| Safe content | Centred **2.940 x 0.540**; outer **20 px** stays quiet |
| UV0 | U grows toward Blender -X; V toward Blender +Z |
| glTF UV | V storage flipped; image top V=0, bottom V=1; upright and unmirrored |
| Axes | Blender +Y/+Z converts once to Godot -Z/+Y |
| Suggested mount | Inherited provisional **3.8 m** pivot, lowest geometry **3.4 m** |
| Flat mounting bay | At least **3.4 m** wide, adjacent fittings at least **0.1 m** apart |

Preserve the hardware's reserved fitting volume and wall datum; reject curved/corner mounts.
Place a delivered tenant prefab **instead of**, never on top of, a blank fascia. Review actual
shell/canopy placement and clearances downstream. There is no saved district or building assembly.
The evidence's stacked catalogue display is not an installation plan.

All three saved scenes inherit the unchanged base fascia. `Visuals/Model` remains an identity-
transform imported GLB. The only saved appearance override is:

`Visuals/Model/city_shop_fittings_02/fascia_artwork_carrier: surface_material_override/0`

Slot 0 is checked against **fascia_artwork_face**; slot 1 **fascia_mount_metal** and all other
hardware surfaces, meshes, transforms and imported identities stay unchanged. No copied vertex
data, duplicate coplanar plane, global override or runtime-authored hierarchy. This uses the
explicit **static artwork face-slot editable-child exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement). After initial normalization,
**two complete save/reload cycles per variant preserve exact bytes, node identities and UIDs**.
The receipt retains three equal SHA-256 snapshots per scene; final import and two fresh runtime
processes preserve the same hashes and resolve each scene/base/model/material/texture UID.

These flush, above-head wall fittings are **visual-only**, matching the standing collision rule.
The mounting building owns blocking; no collider, navigation, gameplay state, authority rule,
rig, animation, socket or LOD policy changes. No freestanding mounting is authorized.

The earlier civic `.01`, `.02` and `.03` current handoffs contain no stale pending `.04` item;
none needed a sibling-status edit. Their sources, evidence manifests and historical receipts
are untouched. No shared brief, queue, progress, TODO, project settings or world file changed.

## Evidence and validation

[Hero](d05_civic_graphics_04-evidence/hero.png) ·
[Side](d05_civic_graphics_04-evidence/side.png) ·
[Face detail](d05_civic_graphics_04-evidence/detail.png) ·
[47 m / 42-degree overhead](d05_civic_graphics_04-evidence/overhead_47m_42deg.png).

All four renders and three source PNGs were personally inspected. Isolated Blender Cycles CPU,
32 samples/denoising, AgX, **1280 x 720**, RGB8 PNG compression 95, no dither. All renders are below
244 KB. Hero/side show all three tenant designs, warm restrained colour and unchanged recessed
hardware; detail shows the tea sign's upright lettering, emblem and face margin. The initial
side framing was too tight at the top; widened and rerendered before final evidence.

The straight-down north-up perspective is **47 m high / 42-degree vertical FOV**, with fascia
pivots at the inherited provisional **3.8 m** mount height and hypothetical bays X=-4/0/4 m.
There is deliberately no substitute facade geometry. The signs are tiny thin edges and their
vertical faces are **not gameplay-readable overhead**, even without roof occlusion. Text and
symbols are decorative close-view identity, not essential navigation. No enlargement, camera
tilt, emission or added roof signage was used to fake readability. These are Blender renders,
not Godot screenshots or populated-world camera/actor acceptance.

Final [validation.json](d05_civic_graphics_04-evidence/validation.json) records:

- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**.
- Reused hardware per instance: **836 source vertices / 1,072 GLB vertices / 1,656 triangles**;
  **7 meshes / 8 surfaces**, five unchanged hardware materials. No new geometry.
- **Zero degenerate source faces/export triangles and zero non-manifold edges**; unit source/
  export normals, outward winding, applied transforms, metre units and wall-centred pivot.
- Source, independently decoded GLB and imported Godot bounds match the inherited contract.
  **28 imported front vertices**, maximum UV error **0.000021656**, below **0.00005** compressed-
  attribute tolerance; upright/unmirrored face mapping is independently checked.
- Fresh saved-source reexport **byte-identical**, **45,616 bytes**, SHA-256
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- **Four Python tests pass** across all variants: exact reproducible PNGs/format, quiet safe
  margins, independent trade-emblem landmarks and asymmetric upright title strokes/counters.
- Pinned Godot **4.8.dev7.official.c971f93e7** final import: no ERROR/SCRIPT ERROR.
  Two identical fresh runtime receipts verify unchanged meshes, exactly one face override per
  variant, UVs/bounds, material/filtering/mipmaps, no collision and all dependency UIDs.
- Two byte-stable save/reload cycles per prefab; GDScript format check and zero-warning lint pass.

[manifest.json](d05_civic_graphics_04-evidence/manifest.json) hashes every produced payload
except itself/cache, including tools, tests, sidecars, this doc, receipt and four renders.
`record.py` reuses the earlier civic inventory helper. Shared dependencies are hashed separately,
not copied into this asset's payload. [final.log](d05_civic_graphics_04-evidence/final.log) retains
concise final outcomes and actual diagnostics. Scratch exports/retry logs stay outside Git at
`C:/tmp/ft/assets/d05_civic_graphics_04/`.

## Exact reproduction

From the worktree root in Git Bash; never use a live editor:

```sh
NID=d05_civic_graphics_04
P="$(pwd -W)"
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
export PYTHONIOENCODING=utf-8
python "tools/asset_production/$NID/author.py"
python -m unittest discover -s "tools/asset_production/$NID" -p 'test_*.py' -v \
  > "$T/tests-final.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/validate.py" > "$T/validate.log" 2>&1
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "$P/tools/asset_production/$NID/preview.py" > "$T/preview-final.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$T/import-first.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/normalize-final.log" 2>&1
cp "$T/prefab.json" "$T/roundtrips.json"
timeout 300 "$G" --headless --path . --import > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" > "$T/load-final.log" 2>&1
cp "$T/prefab.json" "$T/load-first.json"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" > "$T/load-second.log" 2>&1
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd" \
  > "$T/fmt-final.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd" > "$T/lint-final.log" 2>&1
python "tools/asset_production/$NID/record.py"
python "tools/asset_production/$NID/record.py" --manifest write
python "tools/asset_production/$NID/record.py" --manifest verify
```

`record.py` rejects script errors, missing markers, differing runtime receipts, stale saved
scene hashes or changed dependencies. No `tools/production_checks.py` run (owner decision 52).
Text material/prefab authoring followed by headless normalization is the mandated fallback:
windowed editor unavailable; no owner's live Blender/Godot/MCP session was accessed or claimed
synchronized. Existing plugin services start automatically in isolated processes; no MCP calls.

## Diagnostics and remaining acceptance

No failing validation/test/style command is counted as a pass. Initial texture imports used
default mipmaps off; owned sidecars were changed to the family lossless/mipmapped settings and
reimported before normalization. The tighter first side framing was replaced by the inspected
final view; detail was refined to a single close-up rather than duplicating the catalogue view.

Normalization exits 0 and proves stable scenes, but retains the known pinned-editor scan-abort,
RID and 168 ObjectDB-instance shutdown leaks and plugin compatibility warning. It is **not a
clean editor shutdown log**. Final import has only the existing plugin's 4.8-versus-tested-4.7
warning. Both runtime logs have no ERROR/WARNING/SCRIPT ERROR. Blender emits its future node-API
deprecation warning. No global configuration, addon changes or broad error suppression.

Pending: independent art/technical review; final business names/copy/count selection; district
placement and actual fascia/canopy/shell clearance; Godot lighting/filtering and populated
camera/roof/actor visibility review; world movement/aim/vehicle and relevant multiplayer checks;
packaged builds, repeated-placement profiling and target-device/Deck performance. This unplaced
decorative artwork claims no whole-world or full production acceptance and closes no TODO.
