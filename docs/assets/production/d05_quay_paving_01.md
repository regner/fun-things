# d05_quay_paving.01 — Broad quay border motif

10 October 2026. **Artwork, Blender carrier, material and linked prefab delivered; bounded
producer checks pass. Independent review and world/device acceptance remain pending.** Produced
by the isolated implementation worker on `lane/a-d05`; parent/reviewer owns acceptance. The current
production brief and [commission](commission.md) supersede the historical concept-only scope of
[quay paving](../d05_quay_paving.md).

## Design and provenance

Two broad, parallel harbour lines flow gently along a **quiet warm-grey #A6A79E** field, with
**restrained teal #657E7B** accents. Each 8 m strip contains two slow 4 m ripples. The lines are
0.10 m wide, separated by a generous unpainted interval, and vary only 0.08 m either side of their
centre tracks. **78.4123%** of the PNG is exactly the quiet field colour; the remaining pixels
include both teal and antialiased edges. No grit, simulated damage, checker grid, letters,
wayfinding arrows, warning stripes, emission or luminous outline. This is decoration, not a
traffic marking, physical boundary or navigation promise.

The earlier civic [hall](d05_civic_graphics_01.md), [noticeboard](d05_civic_graphics_02.md),
[direction panel](d05_civic_graphics_03.md) and [shop fascias](d05_civic_graphics_04.md) establish
quiet fields, broad continuous graphics and restrained waterfront colour. Their slate/ivory/amber
signage remains unchanged; paving uses the family brief's warmer midtone and muted teal rather
than copying bright sign lettering onto the ground. The paired lines echo the hall's harbour
seal without repeating civic text across walking space.

Original parametric Blender construction and Python **3.14.2** / Pillow **12.3.0** artwork.
`artwork.py` draws metre-space continuous paths at 4x supersampling, then one Lanczos downsample.
No downloads, external fonts, real brands, purchased/generated images or image-to-mesh. References
read: Petrol & Coral; approved Stage 3 Old Quay identity; Stage 4 smaller western/quay streets;
[Old Quay concept](../../concepts/districts-v1/old-quay.md), selected district/map context and shared
concept contract; all four earlier civic handoffs; city_lights.01 source/export/evidence and batch
01–03 prefab conventions. Concepts inform style, not raster-derived measurements.

### Approved carrier direction

The supervisor explicitly selected the accepted [sports surface](d01_sports_surface_01.md) /
[field](d01_sports_surface_02.md) / [court](d01_sports_surface_03.md) ground-artwork precedent:
**an original minimal flush carrier, not a reused material-study swatch or a new ground slab**.
This is a placeable decorative prefab over existing ground. The shared plaza swatch is not
copied, scaled or overridden. No new seawall, curb, bridge, road or walk collider is supplied.
Generated road infrastructure remains its owner's responsibility under decision 42.

## Dimensions and placement interface

All dimensions are **provisional authored values**, not an approved district allocation.
Godot local metres; long axis X; +X east, -Z north, +Z south. Blender +Y/+Z maps once to
Godot -Z/+Y. Identity root/mesh transforms, metre units, origin projected to supporting ground.

| Interface | Contract |
| --- | --- |
| Carrier X / Y / Z | **8.000 / 0 / 1.200 m**, one upward-facing quad |
| Visual AABB min / max | **(-4, .015, -.6) / (4, .015, .6)** |
| Ground-centred pivot | **(0,0,0)** |
| Supporting ground datum | **Y=0**, continuous collision owned by the ground |
| Artwork elevation | **Y=.015**, 15 mm anti-z-fighting lift, not a step |
| End-to-end pitch | **8 m** along local X, aligned orientation and no overlap |
| Longitudinal motif period | **4 m**; two cycles in the texture |
| Transverse line centres | Image V metres **.38 / .82**, with +/- **.08 m** smooth variation |
| Stroke width / minimum quiet edge | **.10 / .25 m** geometrically, plus antialias filter support |
| Numeric bounds / UV tolerance | **.001 m / .000001** source and GLB; **.00005** engine UV |

Use in short, intentional straight border runs along the civic square or quay walking edge,
not carpeted over the whole square. Stop runs before passage mouths, stairs, dock access or
crossings so openings remain visually legible. Do not overlap strips at bends or place them
across water/unsupported edges. Arbitrary curved-quay fitting and corner/termination composition
are placement work, not claims made by this straight motif. No road alignment or world sector
has changed. The 24 m repeated evidence display is not an approved installation plan.

The four earlier civic handoffs contain **no stale pending item for this asset**. Their docs,
source/export payloads, evidence manifests and historical receipts are unchanged.

## Source, export, material and UVs

| Deliverable | Path |
| --- | --- |
| Editable Blender source | `art/source/models/environment/d05_quay_paving_01/d05_quay_paving_01.blend` |
| Explicit linked export | `art/models/environment/d05_quay_paving_01/d05_quay_paving_01.glb` + `.import` |
| Original albedo | `art/textures/environment/d05_quay_paving_01/quay_border_albedo.png` + `.import` |
| External material | `art/materials/environment/d05_quay_paving_01/quay_border.tres` |
| Placeable flush-artwork prefab | `scenes/prefabs/environment/d05_quay_paving_01.tscn` |
| Recipes and checks | `tools/asset_production/d05_quay_paving_01/` |

Collection **export_d05_quay_paving_01** contains root **D05QuayPaving01** and mesh
**D05QuayPaving01_Mesh**, mesh data **D05QuayPaving01_Geometry**. Source contains only the carrier;
preview studio objects are never saved or exported. One opaque Principled slot **quay_border**,
roughness **.94**, metallic 0, backface culled, no emission or normal map. The Blender source links
the committed PNG by a **relative unpacked path**. Export temporarily disconnects image colour
and restores it afterward; **zero embedded GLB images**. Saved Godot import remaps the named slot
to the external material by UID with its fallback path; no copied mesh or child override.

Texture is **1280 x 192 RGB8 sRGB**, **160 texels/metre**, one 8 x 1.2 m atlas. Blender UV0
U=(X+4)/8 and V=(Y+.6)/1.2; glTF flips stored V, so image U grows east/+X and V south/+Z. White
albedo multiplier, clamp/no repeat, linear mipmapped filtering, lossless texture import with
mipmaps and automatic 3D compression conversion disabled. Both X endpoint columns match exactly.
Repeating the saved prefab at 8 m pitch preserves the graphic without stretching it. Texture
and material can also be applied to a surface owner's authored strip with the same physical UV
mapping and explicit per-strip 0–1 UVs; the material is **not** a world-space/triplanar shader.
Normalized UVs stretched over arbitrary full-length road segments do not satisfy this contract.
Live generated-surface UV adaptation has not been tested and is not implemented here.

Final bytes/SHA-256, copied from the final source/artwork validation values:

- GLB: **1,400 bytes**, `ccdcae5f9dc5db712a322b1e894d02501ef2cef48a4cf10b2a772d81891db854`.
- PNG: **12,056 bytes**, `21c3fed0ff7b5944bca3cb065524aef798e678d03155e8ef814857173619f8d7`.

Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**. Shared
`tools/assets/blender/export_settings.json`; named collection, no animation/skin export.
Pinned Godot **4.8.dev7.official.c971f93e7**, default generated LOD/shadow meshes. No manual LOD,
rig, socket, animation, gameplay state, runtime artwork script or interaction. Imported RGB8 CPU
image payload including mipmaps is **983,034 bytes**; that is not measured GPU memory or a budget.

## Prefab and collision

`Visuals/Model` is an **identity-transform imported GLB instance**. The saved wrapper has no
CollisionObject3D, collider, navigation or floor nodes. This follows the standing flush-face
exception: there are no sidewalls, rails, raised kerbs or barriers. **Place only over existing
flat, collision-bearing ground at the prefab's local Y=0 datum.** Do not use the artwork as a
walkable floor or add a duplicate ground collider. Retain the 15 mm lift and inspect feet, tyres,
shadows and depth separation after placement. Godot pads planar AABB thickness to .00001 m;
all source/GLB vertex heights remain .015 within tolerance.

The required direct-file/headless fallback was used because live editor sessions are prohibited
and the windowed editor is unavailable. No owner's live Blender/Godot/MCP session was accessed
or claimed synchronized. Pinned headless load/pack/save normalized the material and prefab;
**two further full save/reload passes preserve exact bytes, node identities and UIDs**. A final
import preserves engine-normalized sidecars; two fresh runtime processes then resolve the
scene/model/material/texture UIDs with identical passing receipts and no missing dependencies.

## Evidence and validation

[Hero](d05_quay_paving_01-evidence/hero.png) ·
[Side](d05_quay_paving_01-evidence/side.png) ·
[Detail](d05_quay_paving_01-evidence/detail.png) ·
[47 m / 42-degree overhead](d05_quay_paving_01-evidence/overhead_47m_42deg.png).

All four final images and the source PNG were personally inspected. Isolated Blender Cycles CPU,
24 samples/denoising, AgX, **1280 x 720 RGB8 PNG**, compression 95, no dither. All renders are below
223 KB. Hero and overhead show **three linked repetitions / 24 m**, with unbroken end-to-end
lines. Side and detail show a single carrier and broad clean strokes. The slight near-view edge
shadow comes from the documented visual lift, not slab geometry. Read-only shared plaza paving
supplies studio context; the unchanged Coral Courier and Latch GLBs provide overhead scale.
Nothing from the studio is exported or saved as a district placement.

The overhead is truly vertical-down, north-up perspective at **(0,0,47)**, **42-degree vertical
FOV**. The border is a quiet narrow strip, its two lines remain discernible, and adjacent actor/car
colours stand out. No camera tilt, enlarged asset or emission fakes gameplay visibility. These
are Blender observations, **not Godot screenshots**, moving-camera shimmer or populated-world
actor-visibility acceptance.

Final [validation.json](d05_quay_paving_01-evidence/validation.json) records:

- **4 source vertices / 4 GLB vertices / 2 triangles; one mesh / one surface**.
- Zero degenerate faces/triangles, unit-length upward normals and upward winding.
- **Four intentional boundary/non-manifold edges**, one closed perimeter on the single-sided
  decal; **zero non-boundary non-manifold edges**. No loose branches or exported studio objects.
- Source and independently decoded GLB bounds, UV0, transforms, external image link and datum
  pass. Fresh saved-source re-export is **byte-identical** to the committed GLB.
- Four Python tests pass: exact PNG reproduction/format; quiet field and margins; independent
  two-line stroke/gap/crest/trough checks; seamless endpoints and minified stroke contrast.
- Godot verifies imported **four vertices / two triangles**, unit upward normals, UV orientation,
  material/mipmap/texture format, AABB, linked ancestry, no overrides and zero collision objects.
- Two byte-stable scene/material save cycles and two identical fresh runtime receipts pass.
  Final import and runtime checks have **no ERROR/SCRIPT ERROR** lines. Both runtimes also have
  no warning lines. Pinned GDScript format and zero-warning lint pass; Python syntax check passes.

`validate.py` reuses the sports field's binary accessor decoder without running its validator;
`preview.py` reuses the sports oval's isolated studio helpers. Shared export settings and the
civic inventory helper are reused unchanged. [manifest.json](d05_quay_paving_01-evidence/manifest.json)
hashes every produced payload except itself/cache, and separately hashes read-only dependencies.
[final.log](d05_quay_paving_01-evidence/final.log) retains concise outcomes and actual diagnostics.
Scratch/reexports/logs remain outside Git at `C:/tmp/ft/assets/d05_quay_paving_01/`.

## Exact reproduction

From the repository root in Git Bash. Never use the owner's live editor. Preserve saved import
and scene identities; all Blender/engine calls are bounded and use the mandated pins.
`export.py` also accepts an output directory after `--` when run against the saved source.

```sh
N=d05_quay_paving_01
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
python -m py_compile "$T/author.py" "$T/artwork.py" "$T/export.py" \
  "$T/preview.py" "$T/validate.py" "$T/record.py" "$T/test_artwork.py"
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

No failing command is counted as a pass. Initial imports produced default non-mipmapped texture
settings; owned sidecars were changed to the stated lossless/mipmapped settings before checks.
Normalization exits 0 and proves stable bytes/UIDs but retains the known plugin version warning,
scan-abort, RID and 168 ObjectDB-instance shutdown leaks: **not a clean editor-log claim**.
Final import retains only the plugin's 4.8-versus-tested-4.7 warning. Blender reports its future
node-API deprecation warning. No addon/global settings changes or broad error suppression.
`tools/production_checks.py` was not run (owner decision 52).

Pending: independent art/technical review; provisional size/palette and actual district run
selection; saved placement over continuous flat ground with visually open passage mouths;
actual Godot lighting, actor/car contact, shadow/depth and moving-camera filtering review;
any generated-surface UV adapter; relevant world/multiplayer integration, packaged builds,
repeated-placement profiling and sustained target-device/Deck performance. No new collision or
simulation rule requires an asset-specific movement test here, and none is claimed. No shared
queue, progress, brief, project setting, world scene or TODO changed. This unplaced decorative
artwork claims no whole-city or full gameplay acceptance.
