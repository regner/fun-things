# d05_quay_paving.02 — Simple civic-square inset

10 October 2026. **Artwork, Blender carrier, material and linked prefab delivered; bounded
producer checks pass. Independent review and world/device acceptance remain pending.** Produced
by the isolated implementation worker on `lane/a-d05`; parent/reviewer owns acceptance. The
current common production brief and [commission](commission.md) supersede the historical
concept-only scope of [quay paving](../d05_quay_paving.md).

## Design and provenance

One quiet square field with **four rounded teal corner inlays**, broad breaks at the four
side centres and an undecorated centre. No medallion, lettering, concentric rings, arrows,
warning stripes, luminous edge, small tile noise or simulated damage. This is a discrete
civic-square accent, not a traffic marking, target, court, interaction zone or physical barrier.
It organises one small part of the square without carpeting the surrounding walking space.

The [quay border](d05_quay_paving_01.md) owns the paving palette: warm grey **#A6A79E** and
restrained teal **#657E7B**. `artwork.py` imports that palette unchanged. **93.7713%** of the PNG
is exactly the quiet field colour; the remainder includes teal and antialiased edges. The
[hall](d05_civic_graphics_01.md), [noticeboard](d05_civic_graphics_02.md),
[direction panel](d05_civic_graphics_03.md) and [shop fascias](d05_civic_graphics_04.md) establish
broad continuous graphics and quiet fields. Their brighter ivory/amber lettering is deliberately
not repeated on the ground. Gentle rounded elbows relate the inset to the border's flowing lines.

Original Blender construction and Python **3.14.2** / Pillow **12.3.0** artwork, drawn in metres
at 4x supersampling and downsampled once with Lanczos. No downloads, external fonts, real brands,
purchased/generated images, image-to-mesh or prototype dependencies. References read: Petrol &
Coral; approved Stage 3 Old Quay identity; Stage 4 smaller western/quay streets; selected Old Quay
map, district concept and shared concept contract; all five earlier lane handoffs; city_lights.01
source/export/evidence and batch 01–03 linked-prefab conventions. Concepts inform style, not
raster-derived dimensions. Sources, assets and historical receipts of all earlier siblings are
unchanged; **none of their current handoffs lists this inset as a stale pending deliverable**.

## Dimensions and ground interface

All dimensions are **provisional authored values**, consistent with the standing sports-surface
ground-artwork direction, not an approved district allocation. Godot local metres; +X east,
-Z north, +Z south. Blender +Y/+Z maps once to Godot -Z/+Y; all object transforms are identity.

| Interface | Contract |
| --- | --- |
| Carrier X / Y / Z | **6.000 / 0 / 6.000 m**, one upward-facing quad |
| Visual AABB min / max | **(-3, .015, -3) / (3, .015, 3)** |
| Ground-centred pivot | **(0,0,0)** |
| Supporting ground / artwork datum | **Y=0 / Y=.015**, 15 mm visual anti-z-fighting lift |
| Corner outline outer extent | **5 x 5 m**, inset **.5 m** from the field edges |
| Stroke width / outer elbow radius | **.18 / .45 m**, broad and continuous |
| Four central edge breaks | **2 m** each, centred on the cardinal axes |
| Guaranteed quiet centre | **4 x 4 m**, independently pixel-tested |
| Numeric bounds / UV tolerance | **.001 m / .000001** source/GLB; **.00005** engine UV |

The four gaps are **graphic breaks, not measured walk-route clearances**. Place the complete
prefab only over existing flat, continuous collision-bearing ground, with its root at that
ground's Y=0 datum. Do not overlap other motifs or crossing markings, carpet whole squares,
stretch the inset, put it over unsupported water/edges, or obscure passage mouths. Final
placement must preserve visible walking approaches. This asset does not build a ground slab,
seawall, curb, bridge, road surface, collider or navigation route. Shared ground-finish swatches
are not overridden. Decision 42 leaves generated road infrastructure with its existing owner.

## Source, exports, material and UVs

| Deliverable | Path |
| --- | --- |
| Editable Blender source | `art/source/models/environment/d05_quay_paving_02/d05_quay_paving_02.blend` |
| Explicit linked export | `art/models/environment/d05_quay_paving_02/d05_quay_paving_02.glb` + `.import` |
| Original albedo | `art/textures/environment/d05_quay_paving_02/civic_inset_albedo.png` + `.import` |
| External material | `art/materials/environment/d05_quay_paving_02/civic_inset.tres` |
| Flush-artwork prefab | `scenes/prefabs/environment/d05_quay_paving_02.tscn` |
| Recipes and checks | `tools/asset_production/d05_quay_paving_02/` |

Collection **export_d05_quay_paving_02** contains root **D05QuayPaving02** and mesh
**D05QuayPaving02_Mesh**, mesh data **D05QuayPaving02_Geometry**. No studio geometry is saved or
exported. One opaque Principled slot **civic_inset**, roughness **.94**, metallic 0, backface
culled, no emission/normal map. The saved Blender source references the committed PNG through a
relative, unpacked path. Export temporarily disconnects image colour and restores that link;
**zero embedded GLB images**. Saved Godot import remaps the named material to the external `.tres`;
no imported-child override, copied mesh or runtime appearance writer is needed.

Texture: **960 x 960 RGB8 sRGB**, **160 texels/metre**, one 6 x 6 m atlas. Blender UV0 is
U=(X+3)/6, V=(Y+3)/6; glTF flips stored V, so image U grows east/+X and V south/+Z. White albedo
multiplier, clamp/no repeat, linear mipmapped filtering, lossless PNG import with mipmaps and
automatic 3D compression conversion disabled. This is a **discrete inset, not a tileable ground
finish**. A surface owner may use the material on an explicitly UV-mapped 6 m square, but arbitrary
road-segment UV stretching does not satisfy the contract. Generated-surface UV adaptation is not
implemented or tested here. CPU RGB8 image payload including mipmaps is **3,686,352 bytes**;
that is not measured GPU allocation or an approved budget.

Final bytes/SHA-256, checked against the final validation receipt and manifest:

- GLB: **1,368 bytes**, `0f20c8105c5533221ed14540f0d49ec830831900172bf8928de1048fb98e14c8`.
- PNG: **11,905 bytes**, `3dc04296923c8ff67281cc9ff3e41f78719114a34f822fd619e310f3678e87f9`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**; shared
`tools/assets/blender/export_settings.json`, named collection, no animations/skins. Godot
**4.8.dev7.official.c971f93e7**, default generated LOD/shadow mesh settings. No manual LOD, rig,
socket, animation, gameplay state or interaction is required for this static artwork.

## Saved prefab and collision

`Visuals/Model` is an **identity-transform imported GLB instance**. The wrapper has **zero
collision objects**, no navigation or floor nodes. It follows the standing flush-face exception:
no sidewalls, steps or visible barriers require blocking. Ground owns all walking/driving
collision; do not add a duplicate collider or use this visual plane as a floor. Inspect feet,
tyres, shadows and depth separation on final placement. Godot pads planar AABB thickness to
.00001 m; source/GLB vertices stay at Y=.015 within tolerance.

Direct text authoring followed by pinned headless normalization is the required fallback:
windowed editor unavailable; no owner's live Blender/Godot/MCP session was touched or claimed
synchronized. After initial normalization, **two complete scene/material save/reload cycles
preserve exact bytes, node identities and UIDs**. Final import preserves engine-normalized
sidecars; two fresh runtime processes then resolve all prefab/model/material/texture dependencies
and agree exactly. Existing plugin services start automatically in isolated processes; no MCP calls.

## Evidence and validation

[Hero](d05_quay_paving_02-evidence/hero.png) ·
[Side](d05_quay_paving_02-evidence/side.png) ·
[Detail](d05_quay_paving_02-evidence/detail.png) ·
[47 m / 42-degree overhead](d05_quay_paving_02-evidence/overhead_47m_42deg.png).

All four renders and the source PNG were personally inspected. Isolated Blender Cycles CPU,
24 samples/denoising, AgX, **1280 x 720 RGB8 PNG**, compression 95, no dither; each below 219 KB.
Hero/side show the whole square and all four openings. Detail shows one continuous rounded elbow.
The near-view edge shadow comes from the 15 mm visual lift, not slab thickness. Read-only shared
plaza paving supplies studio context. The overhead uses unchanged Coral Courier and Latch GLBs
for scale, with one real-scale inset, not repeated installations or a saved placement.

Overhead is truly vertical-down, north-up perspective at **(0,0,47)** with **42-degree vertical
FOV**. The inset is about 120 pixels square: all four brackets and central breaks remain legible,
while the actor in its quiet centre and nearby car remain distinct. No camera tilt, enlarged
geometry, emission or artificial outline was used. These are **Blender observations, not Godot
screenshots**, moving-camera filtering, populated-world visibility or device acceptance.

Final [validation.json](d05_quay_paving_02-evidence/validation.json) records:

- **4 source vertices / 4 GLB vertices / 2 triangles; one mesh / one material surface**.
- Zero degenerate faces/triangles; unit-length upward source/export normals and upward winding.
- **Four intentional boundary/non-manifold edges**, one closed perimeter on a single-sided
  flush carrier; **zero non-boundary non-manifold edges**. No loose branches or studio objects.
- Independently measured source and decoded GLB bounds/UV0/transforms, relative external texture
  link and ground datum pass. Fresh saved-source re-export is **byte-identical** to the GLB.
- **Four Python tests pass**: exact PNG reproduction/format, quiet centre/margins/openings,
  independent four-corner/elbow/stroke landmarks, and minified contrast with quiet approaches.
- Godot checks actual imported arrays/UVs/upward normals, source-backed hierarchy, AABB, external
  material, filtering/mipmaps, zero overrides/collision and dependency UIDs.
- Two byte-stable save cycles and two identical fresh runtime receipts pass. Final import and
  runtime logs contain **no ERROR/SCRIPT ERROR**; runtime logs also have no warnings. Pinned
  GDScript format check and zero-warning lint pass; all owned Python scripts compile.

Shared binary accessor decoder, isolated studio helpers and civic manifest inventory helper are
reused without edits. [manifest.json](d05_quay_paving_02-evidence/manifest.json) hashes every
produced file except itself/cache, and separately hashes read-only dependencies including the
sibling palette. [final.log](d05_quay_paving_02-evidence/final.log) retains concise final outcomes
and actual diagnostics. Scratch/reexports/retry logs remain outside Git at
`C:/tmp/ft/assets/d05_quay_paving_02/`.

## Exact reproduction

From the repository root in Git Bash. Preserve existing saved identities and import settings.
`export.py` also accepts an output directory after `--` when run against the saved `.blend`.

```sh
N=d05_quay_paving_02
T="tools/asset_production/$N"
S="C:/tmp/ft/assets/$N"
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
mkdir -p "$S"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
python "$T/artwork.py"
timeout 120 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 --python "$T/author.py" > "$S/author.log" 2>&1
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 --python "$T/preview.py" > "$S/preview.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
  --factory-startup --threads 4 --python-exit-code 1 --python "$T/validate.py" > "$S/validate.log" 2>&1
python -m unittest discover -s "$T" -p 'test_*.py' -v > "$S/tests.log" 2>&1
python -m py_compile "$T"/*.py
timeout 60 "$(mise which gdstyle)" fmt --check "$T/check_prefab.gd" > "$S/format.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "$T/check_prefab.gd" > "$S/style.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-remap.log" 2>&1
timeout 180 "$G" --headless --editor --path . --script "$T/check_prefab.gd" -- \
  --normalize > "$S/roundtrip.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" > "$S/prefab-check.log" 2>&1
cp "$S/prefab-check.json" "$S/prefab-first-process.json"
timeout 180 "$G" --headless --path . --script "$T/check_prefab.gd" \
  > "$S/prefab-second-process.log" 2>&1
cmp "$S/prefab-first-process.json" "$S/prefab-check.json"
python "$T/record.py"
python "$T/record.py" --manifest write
python "$T/record.py" --manifest verify
```

## Diagnostics and remaining acceptance

The initial quiet-centre test sampled a rounded elbow; corrected its independent clear-centre
rectangle to the documented 4 x 4 m, without changing artwork or loosening colour tolerance.
Initial texture import used default mipmaps off; owned sidecars were set to the stated lossless/
mipmapped contract before normalization. No failed command is counted as a pass.

Normalization exits 0 and proves byte/UID stability, but retains the known editor scan-abort,
RID and 168 ObjectDB-instance shutdown leaks: **not a clean editor-shutdown log claim**. Final
import retains only the existing plugin's 4.8-versus-tested-4.7 warning. Blender emits its future
node-API deprecation warning. No global/addon changes or broad error suppression were introduced.
`tools/production_checks.py` was not run (owner decision 52).

Pending: independent art/technical review; provisional size/palette and actual square selection;
saved placement on continuous flat ground with open passage mouths; Godot lighting, contact,
shadow/depth and moving-camera filtering review; any generated-surface UV adapter; relevant
world/multiplayer integration, packaged builds, repeated-placement profiling and sustained
Deck/target-device performance. No collision or simulation rule changed, and no asset-specific
movement test is claimed. No shared queue, progress, brief, project setting, world scene or TODO
changed. This unplaced decorative artwork claims no whole-city or full gameplay acceptance.
