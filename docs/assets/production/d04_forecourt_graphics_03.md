# d04_forecourt_graphics.03 — Quiet inset emblem

**Original artwork, flush Blender carrier, external material and linked prefab delivered;
bounded producer checks pass. Independent review and world/gameplay/device acceptance remain
pending.** Producer: commissioned implementation worker on `lane/a-d04g`; supervisor retains
acceptance authority. The [commission](commission.md) supersedes the concept-only stage.
References: [family brief](../d04_forecourt_graphics.md), [Glassward concept](../../concepts/districts-v1/glassward.md),
[selected district](../../concepts/districts-v1/map-context.md#district-04),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#glassward--the-skyline-presses-in),
and [downtown grid](../../concepts/world-v1/stage-04-streets/README.md#owner-refinement--a-gridded-high-rise-centre).

## Design and provenance

Two **offset slate appointment corners and one small cyan marker on a pale square field**.
The emblem translates the fictional corporate family's scheduling identity into quieter,
squared paving inlays. It is compact identity, not another long axis or transverse band:
[forecourt band](d04_forecourt_graphics_01.md), [entry axis](d04_forecourt_graphics_02.md),
[facade panel](d04_corporate_graphics_01.md), [directory](d04_corporate_graphics_02.md),
[entry wordmark](d04_corporate_graphics_03.md). Generous blank margins and an open centre keep
empty ground dominant. There is no text, arrow, ring, border, magenta, glowing edge, dense
joint pattern, grit or raised furniture. The emblem is **decorative, not a destination,
interaction target, objective marker, restriction, road marking or authoritative wayfinding**.
No real brand or final district/company naming decision is implied.

Pale `#C5CBCA`, slate `#85929D` and cyan `#57D9E5` reuse the earlier band's read-only palette
module. Cyan also matches all three corporate siblings. Exact-color pixels are **90.90271%
pale** and **0.134277% cyan**, excluding antialiasing. `artwork.py` is the original deterministic
Python/Pillow drawing recipe; `author.py` constructs the original Blender quad. No downloaded
image/mesh, external font, purchased asset, generated concept raster or image-to-mesh is used.

The standing ground-art rule and [sports-ground precedent](d01_sports_surface_03.md) authorize
this minimal flush carrier, **not an override or enlarged duplicate of a ground-finish swatch**.
Shared ground supplies the physical surface. No road-tool ownership or world layout changes.
All five earlier sibling handoffs were read; none lists this delivery as a stale pending item.
Their current manifests pass unchanged. No sibling document, manifest or historical receipt
needed editing. No queue, progress tracker, shared brief, TODO or gameplay code changed.

## Provisional dimensions and placement interface

These are **provisional authored values**, not measurements inferred from generated imagery
or an approved site allocation. Glassward's 98,953.4 m² gross area and 420.7 × 347.8 m bounds
are context only. Preserve the open three-tower forecourt and existing walking/driving choices.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Carrier X / Y / Z | **8 / 0 / 8**, one single-sided plane |
| AABB min / max | **(-4,.015,-4) / (4,.015,4)** |
| Pivot / supporting ground | `(0,0,0)`, footprint centre projected onto external ground |
| Artwork datum | **Y=.015**, intentional 15 mm anti-z-fighting lift |
| Combined slate emblem extent | **4.625 × 4.625**, X/Z=-2.1875…2.4375 |
| Each corner's outer envelope | **3.375 × 3.375**, **.375** stroke width |
| First / second corner minimum X/Z | **-2.1875 / -.9375**; offset **1.25** on both axes |
| Minimum blank outer margin | **1.5625**, east/south; north/west **1.8125** |
| Cyan marker | **.75 × .1875**, centre `(.75,.015,.78125)` |
| Source/binary position and UV tolerance | **.000001** |
| Godot AABB tolerance | **.001**, including .00001 m planar import padding |

Blender +Y/+Z maps to Godot -Z/+Y; +X is east. Root, mesh and `Visuals/Model` have identity
transforms, metre units and unit scale, without corrective rotation or scale. The two open
corners face north in the authored orientation; their asymmetry is intentional, not mirrored
UVs. Rotate the whole prefab about Y for an approved composition, never stretch it to fill a
courtyard. There is no socket, fixed site position or player-followed axis.

This is one complete **8 × 8 m atlas**, not a repeatable ground tile or the shared 4 m tiling
interface. Do not apply it to arbitrary road-segment UVs, repeat it as a traffic marking,
overlap it with the sibling motifs, or bridge curbs, steps, slopes and holes. A pale square
edge is intentional; resolve adjacency with the supporting ground in placement review.

## Source, export, material and prefab

| Deliverable | Path |
| --- | --- |
| Blender source | `art/source/models/environment/d04_forecourt_graphics_03/d04_forecourt_graphics_03.blend` |
| GLB + import | `art/models/environment/d04_forecourt_graphics_03/d04_forecourt_graphics_03.glb` |
| Texture + import | `art/textures/environment/d04_forecourt_graphics_03/quiet_inset_emblem_albedo.png` |
| Material | `art/materials/environment/d04_forecourt_graphics_03/quiet_inset_emblem.tres` |
| Linked prefab | `scenes/prefabs/environment/d04_forecourt_graphics_03.tscn` |
| Recipes/checks | `tools/asset_production/d04_forecourt_graphics_03/` |

Collection `export_d04_forecourt_graphics_03`; root `D04ForecourtGraphics03`; mesh
`D04ForecourtGraphics03_Mesh`; data `D04ForecourtGraphics03_Geometry`. No studio objects are saved
in source. One Principled slot **`quiet_inset_emblem`**: opaque, backface culled, roughness **.94**,
metallic 0, no emission/normal/ORM. The source PNG is relatively linked and unpacked. Export
briefly disconnects the image then restores it: **zero embedded GLB images**. The named collection
uses `tools/assets/blender/export_settings.json`, static animations and skins disabled.

PNG: **512 × 512 RGB8 sRGB**, **64 texels/metre**, **1,960 bytes**. UV0 covers the whole atlas:
Blender **U=(X+4)/8, V=(Y+4)/8**; exported top-origin image V maps south/+Z. Linear mipmapped
filtering, clamp/no repeat, identity UV scale/offset, lossless compression, full generated mip
chain and automatic 3D compression switching disabled. CPU image including mipmaps is
**1,048,575 bytes**, not measured GPU memory or an accepted budget. Edges use original 4×
supersampling, not texture grit. No alpha sorting or transparency dependency.

The saved `.glb.import` remaps only `quiet_inset_emblem` to the external material by UID with
fallback path. `Visuals/Model` is an ordinary identity imported GLB instance: no editable
children, copied mesh, material override or runtime hierarchy. Default generated LOD/shadow-mesh
options remain; two triangles need no manual LOD. No rig, clip, light, socket, navigation,
interaction or destruction state. Prefab UID `uid://r44nbds34kan`, GLB `uid://bv0db0f4wfots`,
material `uid://ds8ysxhase238`, texture `uid://nuj2oq6kwrll`. Scene/material UIDs are inline;
Godot creates no separate `.tscn.uid`/`.tres.uid` files. Checker `.gd.uid` is committed.

### Collision and supporting ground

**Visual-only flush artwork**, covered by the standing flush-face exception. No collider,
physics body, slab, deck or sidewall is supplied. Place only over existing flat
**collision-bearing ground at Y=0**, retaining the .015 m lift. Ground owns foot/car contact
and route continuity; this artwork is not a floor by itself. The shared
[plaza finish](city_ground_finishes_01.md) is suitable supporting appearance, but its review
swatch is not a world tile to duplicate. No collision/gameplay/network behavior changed.

## Evidence and measured checks

[Hero](d04_forecourt_graphics_03-evidence/hero.png) ·
[side](d04_forecourt_graphics_03-evidence/side.png) ·
[inset detail](d04_forecourt_graphics_03-evidence/detail.png) ·
[47 m / 42° overhead](d04_forecourt_graphics_03-evidence/overhead_47m_42deg.png).
All four final renders and the runtime PNG were personally inspected. Two separated slate
corners survive gameplay scale; the tiny cyan dash is subordinate and not required information.
The true-scale Courier on the blank south portion and Latch outside the square separate in
this static view. Close views show clean squared inlays, quiet margins and no raised slab.
Studio swatch edges are evidence boundaries, not exported geometry. Actual tower-shadow,
moving-camera and populated-world actor visibility remain unproved.

Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; Cycles CPU,
24 samples/denoising, AgX, RGB PNG compression 95, no dithering, **1280 × 720**. Render payloads
are 91,228–207,661 bytes. Overhead is north-up vertical perspective at Blender **(0,0,47)**,
**42° vertical FOV**, approximately 64.1 × 36.1 m coverage. `preview.py` temporarily instances
48 accepted Blender paving swatches and imports unchanged Courier/Latch GLBs for scale.
None is saved/exported or becomes world placement. These are **not Godot screenshots**,
gameplay-lighting approval, occlusion tests or motion evidence.

[validation.json](d04_forecourt_graphics_03-evidence/validation.json) records:

- **4 source/export vertices, 2 triangles, one mesh and one material surface**.
- **Zero degenerate source faces or binary triangles**, unit upward normals and finite positions.
- **Four intentional boundary/nonmanifold edges**, one closed four-edge perimeter on a
  single-sided flush plane; **zero non-boundary nonmanifold edges**, no loose geometry.
- Saved-source transforms, collection, UVs, material and relative image dependency pass; actual
  GLB positions/normals/indices/UVs/bounds are decoded and checked, not inferred from metadata.
- Fresh saved-source re-export is **byte-identical**, **1,400 bytes**, SHA-256
  `7249ba51c982190388e163ea1de8fc98532286d0bf84f52814822455e36799f9`.
- PNG SHA-256 `9bde3b5dbba35afb02c0de3156ee04ae09b52d9368cd572f1aeb1b79fd1d9d6a`;
  **five artwork tests pass**: opaque aspect, independent offset-corner/margin probes, sparse
  palette/inset accent, gameplay minification contrast, exact committed PNG byte reproduction.
- Godot **4.8.dev7.official.c971f93e7** final import and fresh non-editor load exit 0 with
  **no ERROR/SCRIPT ERROR lines**. Linked mesh, external material, bounds, actual mipmaps/filtering,
  absence of collision and registered resource UIDs pass.
- **Two byte-stable scene/material load/pack/save roundtrips**, after initial normalization,
  preserve exact bytes, saved IDs and UIDs. Final runtime hashes match both roundtrips.
- Python compilation, pinned **gdstyle 0.3.0** format check and zero-warning 100-character lint
  pass. No `tools/production_checks.py` invocation, per owner decision 52.

[manifest.json](d04_forecourt_graphics_03-evidence/manifest.json) hashes every produced payload
except itself and records unchanged dependencies. [final.log](d04_forecourt_graphics_03-evidence/final.log)
is the sole concise retained command summary. Scratch exports/raw logs remain under
`C:/tmp/ft/assets/d04_forecourt_graphics_03/`. Existing palette, binary-accessor/perimeter audit,
camera-aim and payload-inventory helpers are reused. No shared tooling was changed.

## Exact reproduction

Run from repository root in Bash with Python/Pillow **12.3.0**. Live MCP/windowed editors were
prohibited; resources were authored directly, then normalized with the isolated pinned headless
engine. This does not synchronize an owner's separate open scene. Preserve saved resource IDs.

```sh
N=d04_forecourt_graphics_03
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
`--factory-startup`, then `--python tools/asset_production/d04_forecourt_graphics_03/export.py
-- C:/tmp/ft/assets/d04_forecourt_graphics_03/export-only` in one command. Rebuilding `.blend`
preserves the recipe, not binary-identical Blender serialization. Revalidation replaces the
combined receipt. After all checks/final handoff edits, use `record.py --write` last to combine
receipts/regenerate the manifest; without `--write`, it verifies retained payloads.

## Diagnostics and remaining acceptance

No geometry, artwork, engine assertion or formatting failure needed repair. Initial texture
import defaults were changed to mipmapped lossless artwork; the external material remap was
saved by UID with fallback path before the final pinned import. All ordinary imports and
non-editor loads pass without errors.

Headless editor normalization exits 0 and passes assertions but reports scan-abort and
RID/ObjectDB shutdown leaks (**168 objects**), matching the earlier sibling tool pattern.
This is **not a clean editor-shutdown claim** or a freshly reproduced empty baseline. Final
ordinary import and runtime load are separately error-free. The addon retains its known
4.8-versus-tested-4.7 warning; Blender emits future `use_nodes` deprecation notices. No live
owner session was accessed, unrelated process stopped or diagnostic suppressed.

Pending: independent art/technical review; final footprint/emblem and district composition
selection; saved placement above continuous ground without stacked motifs or gameplay-marker
ambiguity; populated renderer/gameplay-camera, moving-mip/depth, tower-shadow and actor/target
visibility; foot/tyre contact, packaged filtering/LOD, repeated-placement profiling and Deck
performance. No world placement, movement, multiplayer transport or target-device test is
claimed, and no whole-register or final gameplay acceptance was closed.
