# d04_forecourt_graphics.02 — Entry-axis motif

**Original artwork, flush Blender carrier, external material and linked prefab delivered;
bounded producer checks pass. Independent review and world/gameplay/device acceptance remain
pending.** Producer: commissioned implementation worker on `lane/a-d04g`; supervisor retains
acceptance authority. The [commission](commission.md) supersedes the concept-only stage.
References: [family brief](../d04_forecourt_graphics.md), [Glassward concept](../../concepts/districts-v1/glassward.md),
[selected district](../../concepts/districts-v1/map-context.md#district-04),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#glassward--the-skyline-presses-in),
and [downtown grid](../../concepts/world-v1/stage-04-streets/README.md#owner-refinement--a-gridded-high-rise-centre).

## Design and provenance

Two long **slate open-ended brackets on a pale rectangular field**, with inward shoulders at
the entry end and one small cyan dash on the axis. The generous empty centre suggests alignment
with a lobby without adding furniture, raised borders or an interactive landmark. It differs
from the [broad transverse band](d04_forecourt_graphics_01.md) by its longitudinal paired strokes
and open terminal. This is decorative entry alignment, **not authoritative wayfinding, a road
lane, parking bay, crossing, access restriction or required destination marker**. Place it in a
pedestrian forecourt composition, not a carriageway or car park. There are no arrows, text,
magenta accents, glowing edges, dense joints, surface noise or corporate emblem.

Pale `#C5CBCA`, slate `#85929D` and cyan `#57D9E5` are reused directly from the earlier band's
read-only palette module. The cyan also matches all three delivered
[corporate](d04_corporate_graphics_01.md) [graphics](d04_corporate_graphics_02.md)
[siblings](d04_corporate_graphics_03.md). Exact-color pixels are **88.0051% pale** and
**0.140381% cyan**, excluding antialiasing; empty ground remains dominant.

`artwork.py` is the original reproducible Python/Pillow recipe; `author.py` constructs the
original minimal Blender quad. No downloaded image/mesh, external font, real brand, purchased
asset, generated concept raster or image-to-mesh is used. This follows the standing ground-art
rule and [sports-ground precedent](d01_sports_surface_03.md): a new flush carrier, **not an
override or enlarged copy of a ground-finish swatch**. Road-tool ownership is unchanged.

All four earlier sibling handoffs were read; none lists this delivery as a stale pending item.
Their current manifests pass unchanged, so no sibling document, manifest or historical receipt
was edited. No queue, progress tracker, shared brief, TODO, world scene or gameplay code changed.

## Provisional dimensions and placement interface

These are **provisional authored dimensions**, not inferred concept-image measurements or an
approved site allocation. Glassward's 98,953.4 m² gross area and 420.7 × 347.8 m bounds provide
context only. Preserve the three-tower forecourt's open space and existing routes.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Carrier X / Y / Z | **8 / 0 / 16**, one single-sided plane |
| AABB min / max | **(-4,.015,-8) / (4,.015,8)** |
| Pivot / supporting ground | `(0,0,0)`, footprint centre projected onto external ground |
| Artwork datum | **Y=.015**, intentional 15 mm anti-z-fighting lift |
| Long axis / proposed entry end | Z axis / **-Z north** |
| Parallel slate strokes | **.50 × 12**, X=-2.50…-2.00 and 2.00…2.50; Z=-6…6 |
| North inward shoulders | Z=-6…-5.50; combined with strokes, X=-2.50…-.75 and .75…2.50 |
| Clear central field / north gap | **4.00** wide between long strokes / **1.50** gap at shoulders |
| Outer blank margins | **1.50** left/right; **2.00** north/south |
| Cyan dash | **1.50 × .1875**, centre `(0,.015,-4.50)` |
| Source/binary position and UV tolerance | **.000001** |
| Godot AABB tolerance | **.001**, including .00001 m planar import padding |

Blender +Y/+Z maps to Godot -Z/+Y; +X is east. Root, mesh and `Visuals/Model` are identity
transforms, metre units and unit scale. No corrective rotation/scale. Rotate the entire prefab
around Y to align its north end toward an actual entry; do not stretch it. There is no socket,
fixed district placement or rule that a player must follow its axis.

This is one complete **8 × 16 m atlas**, not a tiling strip or the shared 4 m ground-material
interface. Do not apply it to arbitrary road segment UVs, repeat it as a traffic marking,
overlap coplanar motifs, or bridge curbs, steps, slopes and holes. Adjacent band/motif placement
must resolve edges without stacked faces. Actual entry-grid fit remains placement review.

## Source, export, material and prefab

| Deliverable | Path |
| --- | --- |
| Blender source | `art/source/models/environment/d04_forecourt_graphics_02/d04_forecourt_graphics_02.blend` |
| GLB + import | `art/models/environment/d04_forecourt_graphics_02/d04_forecourt_graphics_02.glb` |
| Texture + import | `art/textures/environment/d04_forecourt_graphics_02/entry_axis_motif_albedo.png` |
| Material | `art/materials/environment/d04_forecourt_graphics_02/entry_axis_motif.tres` |
| Linked prefab | `scenes/prefabs/environment/d04_forecourt_graphics_02.tscn` |
| Recipes/checks | `tools/asset_production/d04_forecourt_graphics_02/` |

Collection `export_d04_forecourt_graphics_02`; root `D04ForecourtGraphics02`; mesh
`D04ForecourtGraphics02_Mesh`; data `D04ForecourtGraphics02_Geometry`. No studio objects are
saved in source. One Principled slot **`entry_axis_motif`**: opaque, backface culled, roughness
**.94**, metallic 0, no emission, normal or ORM. The source PNG is relatively linked and unpacked.
Export temporarily disconnects its image, then restores it: **no embedded GLB image**. The named
collection is exported through `tools/assets/blender/export_settings.json`, static animations
and skins disabled. The neutral exported slot is intentionally remapped in Godot.

PNG is **512 × 1024 RGB8 sRGB**, **64 texels/metre**, **3,274 bytes**. UV0 covers the whole atlas:
Blender **U=(X+4)/8, V=(Y+8)/16**; glTF's top-origin image V maps south/+Z. Linear mipmapped
filtering, clamp/no repeat, identity UV scale/offset, lossless compression, full generated mip
chain and automatic 3D compression switching disabled. CPU image including mipmaps is
**2,097,153 bytes**, not measured GPU memory or a platform budget. Antialiasing is original
4× supersampling, not texture grit; no alpha sorting or transparency dependency.

Saved `.glb.import` remaps only `entry_axis_motif` to the external material by UID and fallback
path. The prefab keeps one imported identity `Visuals/Model` instance: no editable children,
copied mesh, runtime hierarchy or material override. Default generated LOD/shadow-mesh options
remain; two triangles do not warrant a manual LOD. No rig, clip, light, socket, navigation,
interaction or destruction state. Prefab UID `uid://dydb3ac3wt5wm`, GLB UID `uid://2t554rcqv1f5`,
material UID `uid://cw0jfy88nhf3d`; scene/material UIDs are inline and Godot creates no separate
`.tscn.uid`/`.tres.uid` files. The checker's `.gd.uid` and texture/model `.import` files are kept.

### Collision and supporting ground

**Visual-only flush artwork**, covered by the standing flush-face exception. No collider,
physics body, slab, deck or sidewall is supplied. Place only above existing flat
**collision-bearing ground at Y=0**, retaining the .015 m lift. Ground owns foot/car contact and
route continuity; this artwork is not a floor by itself. The shared
[plaza finish](city_ground_finishes_01.md) is suitable supporting appearance, but its review
swatch is not a world tile to duplicate. No gameplay/collision/network behavior changed.

## Evidence and measured checks

[Hero](d04_forecourt_graphics_02-evidence/hero.png) ·
[side](d04_forecourt_graphics_02-evidence/side.png) ·
[terminal detail](d04_forecourt_graphics_02-evidence/detail.png) ·
[47 m / 42° overhead](d04_forecourt_graphics_02-evidence/overhead_47m_42deg.png).
All four final renders and the runtime PNG were personally inspected. The two neutral strokes
and open north terminal read clearly at gameplay scale; cyan stays subordinate. The true-scale
Courier in the empty centre and Latch outside the field separate in this static view. Close
views show clean rectangular margins and no raised slab. Studio swatch borders are evidence
boundaries, not exported geometry. This does not prove moving-camera or tower-shadow visibility.

Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; Cycles CPU,
24 samples/denoising, AgX, RGB PNG compression 95, no dithering, **1280 × 720**. Four files are
89–231 KB. Overhead is north-up vertical perspective at Blender **(0,0,47)**, **42° vertical FOV**,
approximately 64.1 × 36.1 m coverage. `preview.py` temporarily instances 48 accepted Blender
paving swatches and imports unchanged Courier/Latch GLBs. None is saved/exported or a world
placement. These are **not Godot screenshots**, gameplay-lighting approval or occlusion tests.

[validation.json](d04_forecourt_graphics_02-evidence/validation.json) records:

- **4 source/export vertices, 2 triangles, one mesh and one material surface**.
- **Zero degenerate source faces or binary triangles**, unit upward normals and finite positions.
- **Four intentional boundary/nonmanifold edges**, one closed perimeter of a single-sided flush
  plane; **zero non-boundary nonmanifold edges**, no loose geometry. Ground supplies collision.
- Saved-source transforms, collection, UVs, material and relative image dependency pass; actual
  GLB positions/normals/indices/UVs/bounds are decoded and checked rather than trusting metadata.
- Fresh saved-source export is **byte-identical**, **1,396 bytes**, SHA-256
  `cf87e23cb8c0d5c13395c99e30fa0437851c74a57fe33ff93b64a6645ba48d6e`.
- PNG SHA-256 `922dad9ae7ac84174b841918db8a19a4d5568a941df29922e22e02d366948129`;
  **five artwork tests pass**: opaque aspect, independent open-axis/margin probes, sparse palette
  and north accent, gameplay minification contrast, exact PNG byte reproduction.
- Godot **4.8.dev7.official.c971f93e7** final import and fresh non-editor load exit 0 with
  **no ERROR/SCRIPT ERROR lines**. Linked mesh, external material, bounds, mipmaps/filtering,
  no collision and resource UID registration pass.
- **Two byte-stable scene/material load/pack/save roundtrips**, after initial normalization,
  preserve exact bytes, saved IDs and UIDs. Final runtime hashes match both roundtrips.
- Python compilation, pinned **gdstyle 0.3.0** formatting and zero-warning 100-character lint
  pass. No `tools/production_checks.py` run, per owner decision 52.

[manifest.json](d04_forecourt_graphics_02-evidence/manifest.json) hashes every produced payload
except itself, and records read-only dependencies. [final.log](d04_forecourt_graphics_02-evidence/final.log)
is the only retained concise command summary. Scratch exports/raw logs remain in
`C:/tmp/ft/assets/d04_forecourt_graphics_02/`. Tools reuse the existing palette, binary-accessor/
perimeter audit, camera-aim and payload-inventory helpers; no shared tooling was modified.

## Exact reproduction

Run from repository root in Bash with Python/Pillow **12.3.0**. Live MCP/windowed editors were
prohibited; resources were authored directly, then normalized with the isolated pinned headless
engine. This is not synchronization of an owner's separate open scene. Preserve saved IDs.

```sh
N=d04_forecourt_graphics_02
T=tools/asset_production/$N
S=C:/tmp/ft/assets/$N
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
export PYTHONIOENCODING=utf-8
mkdir -p "$S"
python "$T/artwork.py"
python -m unittest discover -s "$T" -p 'test_*.py' -v > "$S/artwork-tests.log" 2>&1
for script in author validate preview; do
  timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background \
    --factory-startup --threads 4 --python-exit-code 1 --python "$T/$script.py"
done
python -m py_compile "$T"/*.py
"$(mise which gdstyle)" fmt --check "$T/check_prefab.gd" > "$S/format.log" 2>&1
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 "$T/check_prefab.gd" \
  > "$S/lint.log" 2>&1
timeout 300 "$G" --headless --path . --import
timeout 180 "$G" --headless --editor --path . --script "res://$T/check_prefab.gd" \
  -- --normalize > "$S/normalize.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$S/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script "res://$T/check_prefab.gd" > "$S/prefab.log" 2>&1
python "$T/record.py"
```

Export-only: same pinned Blender/audio/timeout flags, load the saved `.blend` after
`--factory-startup`, then `--python tools/asset_production/d04_forecourt_graphics_02/export.py
-- C:/tmp/ft/assets/d04_forecourt_graphics_02/export-only` in one command. Rebuilding `.blend`
preserves the recipe, not binary-identical Blender serialization. Revalidation replaces the
combined receipt. After all checks and final handoff edits, use `record.py --write` last to
combine receipts/regenerate the manifest; without `--write`, it verifies retained payloads.

## Diagnostics and remaining acceptance

No geometry, artwork, engine assertion or formatting failure needed repair. Initial texture
import defaults were explicitly changed to mipmapped lossless/clamped artwork, and the source
material remap was saved by UID with fallback path before the final pinned import.

Headless editor normalization exits 0 and passes assertions but reports scan-abort and
RID/ObjectDB shutdown leaks (**168 objects**), matching the earlier sibling tool pattern.
This is **not a clean editor-shutdown claim** or a freshly reproduced empty baseline. Final
ordinary import and runtime load are separately error-free. The addon retains its known
4.8-versus-tested-4.7 warning; Blender emits future `use_nodes` deprecation notices. No live
owner session was used, no unrelated process stopped and no diagnostic suppressed.

Pending: independent art/technical review; final footprint, lobby-axis and district composition
selection; saved placement above continuous ground without motif overlaps or traffic-marking
ambiguity; populated renderer/gameplay-camera, moving-mip/depth, tower-shadow and actor/target
visibility; foot/tyre contact, packaged filtering/LOD, repeated-placement profiling and Deck
performance. No world placement, movement, multiplayer transport or target-device test is
claimed, and no whole-register or final gameplay acceptance was closed.
