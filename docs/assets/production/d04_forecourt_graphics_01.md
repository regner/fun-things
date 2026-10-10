# d04_forecourt_graphics.01 — Broad paving band

**Original artwork, flush Blender carrier, linked prefab and bounded producer checks delivered;
independent review and world/gameplay/device acceptance remain pending.** Producer: commissioned
implementation worker on `lane/a-d04g`; supervisor retains acceptance authority. The
[commission](commission.md) supersedes the historical concept-only stage. References:
[family brief](../d04_forecourt_graphics.md), [Glassward concept](../../concepts/districts-v1/glassward.md),
[selected map](../../concepts/districts-v1/map-context.md#district-04),
[approved identity](../../concepts/world-v1/stage-03-district-identities/README.md#glassward--the-skyline-presses-in),
and [downtown grid](../../concepts/world-v1/stage-04-streets/README.md#owner-refinement--a-gridded-high-rise-centre).

## Design and provenance

A long, quiet **pale-neutral paving strip with a broad slate inset and one short cyan accent**.
It unifies open ground without filling the forecourt with objects. Pale `#C5CBCA` shoulders
contrast against the cool shared plaza finish; slate `#85929D` ties back to the shared paving
palette; cyan `#57D9E5` exactly matches the three delivered
[corporate](d04_corporate_graphics_01.md) [graphics](d04_corporate_graphics_02.md)
[siblings](d04_corporate_graphics_03.md). No lettering, arrows, emblem, magenta, continuous neon
edge, seams, cracks, micro-noise, raised borders or new landmark. The cyan inset is decorative,
not a destination, lane marking, crossing, interactable marker or gameplay route authority.
The broad geometry and negative space carry identity, not small details.

`artwork.py` is the original deterministic Python/Pillow drawing recipe. `author.py` constructs
the original minimal quad in Blender. No external font/image, downloaded geometry, purchased
asset, generated concept raster, image-to-mesh or real brand is used.

The supervisor explicitly directed this asset to follow the accepted
[d01 ground-artwork precedent](d01_sports_surface_03.md): **new minimal flush geometry**, not an
override or enlarged copy of the shared ground swatch. This supplies a placeable artwork prefab
without duplicating a ground slab or collider. Shared ground owns the physical surface. This
approval is specific to forecourt ground artwork; it does not change the generated-road owner
or authorize hand-authored road/sidewalk infrastructure.

The earlier corporate handoffs contain no stale pending item resolved here. Their three current
manifests were verified unchanged; no sibling document, manifest or historical receipt was edited.
No queue, shared brief, progress tracker, TODO, world scene, road or gameplay code changed.

## Provisional dimensions and placement interface

All dimensions are **provisional authored choices**, not inferred from generated imagery or an
approved district arrangement. The 24 m length is a restrained forecourt-scale graphic, not a
new plot allocation. Glassward's exact district area is 98,953.4 m² gross, bounds 420.7 × 347.8 m;
that is context, not space reserved for this strip. Placement must preserve open space, existing
streets and walking/driving choices around the three towers.

| Contract | Metres, Godot local axes unless noted |
| --- | --- |
| Carrier X / Y / Z | **24 / 0 / 4**, one single-sided plane |
| AABB min / max | **(-12,.015,-2) / (12,.015,2)** |
| Pivot / supporting ground | `(0,0,0)`, strip centre projected onto external ground |
| Artwork elevation | **Y=.015**, intentional 15 mm anti-z-fighting lift |
| Central slate band | **24 × 1.50**, Godot Z=-.75…+.75 |
| Pale shoulders | **1.25** each, full length |
| Cyan inset | **1.50 × .1875**, X=9…10.5, Z=-.09375…+.09375 |
| Inset to east end | **1.50** clear margin |
| Source/binary bounds and UV tolerance | **.000001** |
| Godot AABB tolerance | **.001**, including .00001 m planar import padding |

Long axis X; +X east, -Z north, +Z south. Blender +Y maps to Godot -Z; Blender +Z to Godot +Y.
Root, mesh and prefab transforms are identity, unit scale, metres; no corrective rotation or
scale. Do not stretch the prefab to fit a whole courtyard. It is a **single complete 24 × 4 m
artwork**, not a tiling kit or continuous cyan wayfinding line. Repeating it end-to-end repeats
the cyan accent and requires composition review. Do not overlap coplanar motifs or span slopes,
steps, curbs, holes or road carriageways. There is no mounting socket or accepted site position.

## Source, export, material and prefab

| Deliverable | Path |
| --- | --- |
| Blender source | `art/source/models/environment/d04_forecourt_graphics_01/d04_forecourt_graphics_01.blend` |
| Explicit GLB + import | `art/models/environment/d04_forecourt_graphics_01/d04_forecourt_graphics_01.glb` |
| Texture + import | `art/textures/environment/d04_forecourt_graphics_01/broad_paving_band_albedo.png` |
| Material | `art/materials/environment/d04_forecourt_graphics_01/broad_paving_band.tres` |
| Linked prefab | `scenes/prefabs/environment/d04_forecourt_graphics_01.tscn` |
| Recipes and checks | `tools/asset_production/d04_forecourt_graphics_01/` |

Collection `export_d04_forecourt_graphics_01`; root `D04ForecourtGraphics01`; mesh
`D04ForecourtGraphics01_Mesh`; data `D04ForecourtGraphics01_Geometry`. The saved source contains
no studio mesh/camera/light. Its sole Principled material slot is **`broad_paving_band`**, opaque,
backface culled, roughness **.94**, metallic 0, no emission/normal/ORM. The committed PNG is
linked by a **relative unpacked path**. Export temporarily disconnects the image and restores it;
**zero embedded GLB images**. The shared `tools/assets/blender/export_settings.json` contract is
loaded explicitly, with named-collection filtering and static animations/skins disabled.

PNG: **1536 × 256 RGB8 sRGB**, **64 texels/metre**, **1,849 bytes**. Pale exact-color pixels
occupy **60.9375%**, cyan exact-color pixels **0.187174%**, excluding antialiasing. The antialiased
edges are original 4× supersampled drawing, not grit. UV0 covers one entire 24 × 4 m atlas:
Blender **U=(X+12)/24**, **V=(Y+2)/4**; exported image axes are east/+X and south/+Z. Linear
mipmap filtering, clamp, full generated mip chain, lossless compression, automatic 3D compression
switch disabled. No alpha or sorting dependency. Runtime CPU image including mips is
**1,572,870 bytes**, not measured GPU memory or an accepted platform budget.

Use the supplied prefab or a surface-owner mesh with this same footprint and UV mapping. This
is **not the shared 4 m tiling interface**: do not plug the atlas into arbitrary road segment UVs.
No live road-tool integration is claimed or required to load the delivered artwork prefab.
Saved `.glb.import` maps only `broad_paving_band` to the external `.tres` by UID/fallback path.
`Visuals/Model` remains an identity imported GLB instance, with no editable children, copied
mesh or material overrides. Default generated LOD/shadow-mesh settings remain; a two-triangle
plane needs no manual LOD asset.

Prefab UID `uid://0n3kx8bqmq8a`, GLB UID `uid://cc6xbg2wbc347`, material UID
`uid://beydyxlqrkgg1`, texture UID `uid://c6smmc1orf8ca`. Scene/material UIDs are inline;
Godot does not create separate `.tscn.uid`/`.tres.uid` files. The checker `.gd.uid` is committed.
No rig, animation, destruction state, light, navigation, interaction or runtime script.

### Collision and supporting ground

**Visual-only flush artwork**, following the standing flush-face exception. No physics body,
collider, walkable deck, sidewalls or ground surface is supplied. Place it only over existing
flat **collision-bearing ground at Y=0**, preserving the .015 m visual lift. The shared
[plain plaza material](city_ground_finishes_01.md) remains suitable supporting appearance;
its review swatch is not a world tile to duplicate beneath this prefab. Supporting ground owns
actor/car collision, foot contact and route continuity. Do not use this artwork alone as a floor.
No collision behavior or network state changed, and no movement/network acceptance is claimed.

## Evidence and measured validation

[Hero](d04_forecourt_graphics_01-evidence/hero.png) ·
[side](d04_forecourt_graphics_01-evidence/side.png) ·
[inset detail](d04_forecourt_graphics_01-evidence/detail.png) ·
[47 m / 42° overhead](d04_forecourt_graphics_01-evidence/overhead_47m_42deg.png).
All four final images and the runtime PNG were visually inspected. The broad shoulders and
slate strip remain clear at gameplay scale; the cyan remains a small subordinate dash, not a
required cue. The true-scale Courier on the central band and Latch beside it separate in this
static view. Hero/side/detail show clean margins and no raised slab. Supporting studio swatch
edges are evidence boundaries, not part of this export. Ground/actor contrast in tower shadow,
camera motion and alternate palettes remains an engine review item.

Isolated Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; Cycles CPU,
24 samples/denoising, AgX, RGB PNG compression 95, no dithering; **1280 × 720**, each under
210 KB. Overhead is north-up vertical perspective, camera Blender **(0,0,47)**, **42° vertical
FOV**, approximately 64.1 × 36.1 m coverage. It shows the whole strip. `preview.py` temporarily
links 48 copies of the accepted Blender paving swatch and imports the unchanged Courier/Latch
GLBs for context; none is saved/exported or becomes world placement. These are **not Godot
screenshots**, tower-occlusion proofs, gameplay lighting approval or moving-camera evidence.

[validation.json](d04_forecourt_graphics_01-evidence/validation.json) records:

- **4 source/export vertices, 2 triangles, one mesh, one material surface**.
- **Zero source degenerate faces or binary triangles**, finite positions and unit upward normals.
- **Four intentional boundary/nonmanifold edges**, one closed four-edge perimeter of a
  single-sided flush plane; **zero non-boundary nonmanifold edges**. No loose geometry.
- Source and actual decoded GLB positions/normals/UVs/indices, transforms, named collection,
  material, datum, dependency path and bounds pass. Decoder/perimeter helpers reuse the accepted
  sports-ground audit; no shared tool was changed.
- Final GLB **1,400 bytes**, SHA-256
  `220fb5ec95d07e02c9eedc4d832c066d160402ed83606a6b42afce41b6d8c1c9`;
  fresh saved-source re-export is **byte-identical**.
- Final PNG SHA-256 `23b188924db672ac7d7d8a73ff9d135fcb3d167d71b9da2f8790b373c374fb49`;
  **five artwork tests pass**: opaque aspect, independent band/shoulder probes, single sparse
  cyan/no magenta, gameplay minification contrast, and exact PNG byte reproduction.
- Godot **4.8.dev7.official.c971f93e7** final import and fresh non-editor dependency load exit 0
  with **no ERROR/SCRIPT ERROR lines**. Linked geometry/material, imported mipmaps, filtering,
  UV transform, no collision and registered resource UIDs pass.
- **Two byte-stable prefab/material load/pack/save roundtrips** after initial normalization,
  retaining exact bytes, UIDs and node identities. Final runtime hashes match those receipts.
- Owned Python compilation, **gdstyle 0.3.0** format check and zero-warning 100-character lint
  pass. No global `production_checks.py` invocation, per owner decision 52.

[manifest.json](d04_forecourt_graphics_01-evidence/manifest.json) hashes every produced payload
except itself and records read-only dependencies. [final.log](d04_forecourt_graphics_01-evidence/final.log)
is the only retained concise command log. Scratch exports, retries and raw logs remain under
`C:/tmp/ft/assets/d04_forecourt_graphics_01/`. Existing payload-inventory, binary-accessor and
camera-aim helpers are reused. Asset-specific plane/engine checks follow the accepted ground-art
conventions; no shared generic plane/check framework was introduced.

## Exact reproduction

Run from repository root in Bash with Python/Pillow **12.3.0**. Live MCP/windowed editors are
prohibited; resources were authored as text then normalized with the isolated headless engine.
This does not synchronize any owner's separate open scene. Preserve saved import/resource IDs.

```sh
N=d04_forecourt_graphics_01
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
python -m py_compile "$T/author.py" "$T/artwork.py" "$T/export.py" "$T/validate.py" \
  "$T/preview.py" "$T/test_artwork.py" "$T/record.py"
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
`--factory-startup`, use `--python tools/asset_production/d04_forecourt_graphics_01/export.py
-- C:/tmp/ft/assets/d04_forecourt_graphics_01/export-only` in one command. Rebuilding `.blend`
preserves the recipe, not binary-identical Blender serialization. Revalidation replaces the
measurement receipt. After all checks and final handoff edits, run `record.py --write` last to
combine receipts and regenerate the manifest; without `--write` it verifies retained hashes.

## Diagnostics and remaining acceptance

Initial audit adaptation accidentally replaced the `court` substring inside the new record name;
first the source path check and then the expected node-name assertion failed. Both owned names
were corrected; the wrong scratch/owned export filename was removed and source/export rebuilt.
Final validation passes all assertions. One long GDScript material-path constant failed lint;
it was wrapped and final formatting/lint pass. No failure was suppressed or left as a placeholder.

Headless editor normalization exits 0 and passes its assertions but emits scan-abort and
RID/ObjectDB shutdown leaks (**168 objects**), matching the documented sibling tool pattern.
This is **not a clean editor-shutdown claim** or a newly reproduced no-asset baseline. Final
ordinary import and runtime load are independently error-free. Import retains the known
4.8-versus-tested-4.7 addon warning; Blender emits future `use_nodes` deprecation notices. No
live owner session was accessed, no unrelated processes were stopped, and no diagnostics hidden.

Pending: independent technical/art review; final footprint and district composition selection;
saved placement over continuous ground, no overlapping motifs and open forecourt preservation;
populated renderer/gameplay-camera, moving-mip/depth, tower-shadow and actor/target visibility;
foot/tyre contact, packaged filtering/LOD, repeated-placement profiling and Deck performance.
No world placement, movement, multiplayer transport or target-device test is claimed, and no
whole-register or final gameplay acceptance was closed.
