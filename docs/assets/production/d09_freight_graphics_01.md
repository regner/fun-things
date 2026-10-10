# d09_freight_graphics.01 — Warehouse fascia art

10 October 2026. **Artwork, material and linked-prefab candidate delivered; independent
review and world/gameplay/device acceptance pending.** Commissioned by Regner under the
[production commission](commission.md) and current asset-common standing rules. Producer:
assigned isolated worker on `lane/a-freight`. Accepting owners: independent art/technical
reviewers, then the world/gameplay/device owners. This is not a registry-ready verdict.

References: [freight graphics family](../d09_freight_graphics.md),
[approved East Docks identity](../../concepts/world-v1/stage-03-district-identities/README.md#east-docks--the-city-ends-at-work),
[street hierarchy](../../concepts/world-v1/stage-04-streets/README.md),
[shared fascia](city_shop_fittings_02.md), and
[warehouse vocabulary](d09_warehouses_01.md). No earlier freight-graphics sibling existed
in this lane. No shared sources, warehouse, family brief, queue, progress or world scene
was changed. The concept-only restriction is superseded by this explicit commission.

## Design, provenance and family seam

**URGENT EVENTUALLY / FREIGHT** in broad ivory/amber industrial capitals, a rounded
amber parcel-clock emblem, three separated steel cargo bars and a restrained arrow.
The clock embedded in the parcel supplies the logistics joke without extra small copy.
All lettering, shapes and layout are original Python/Pillow paths; no downloaded font,
real brand, external image, image generation or purchased geometry. Fictional copy remains
provisional. The arrow is part of decorative business graphics, not an authored route,
loading-bay road marking, saved location identity or navigation instruction.

| Family role | sRGB | Treatment |
| --- | --- | --- |
| Quiet field | `#143344` | Cool petrol-steel, over 70% of the texture |
| Cargo emblem / freight | `#FFC05A` | Warm amber loading accent |
| Business title | `#F6F1DC` | Warm ivory |
| Cargo bars / arrow shaft | `#85929D` | Cool steel |

This establishes the freight family's palette and parcel-clock/cargo-bar grammar.
Subsequent graphics can reuse that business voice while respecting their own carrier UVs
and copy hierarchy. Do not stretch this 5:1 face across a container or build a second
carrier. On the long warehouses, use sparse branded working corners; do not tile bright
artwork across each bay or compete with the broad blue roofs and quiet aprons. The
5.03 ha district is context, not an allocation or a new placement plan.

## Source, runtime outputs and dimensions

The standing **reuse rule** applies: accepted shared fascia hardware already supplies
the face. No redundant per-ID `.blend`, GLB, coplanar panel or export script is produced.
The Blender-sourced face requirement is met by the unchanged chain:

- Source: `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
- Collection / root: `export_city_shop_fittings_02` / `city_shop_fittings_02`.
- Export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb`.
- Hardware validation/export owner: `tools/asset_production/city_shop_fittings_02/export.py`.
  The owned validator calls `perform` with scratch paths, retaining the accepted export
  contract and proving byte identity rather than rewriting shared export settings.

New outputs:

- Reproducible artwork: `tools/asset_production/d09_freight_graphics_01/author.py`.
  Python **3.14.2**, Pillow **12.3.0**, 3x supersampled vector paths, one Lanczos downsample.
- Texture: `art/textures/environment/d09_freight_graphics_01/warehouse_fascia_albedo.png`
  and engine-generated `.import`; **2000 x 400 RGB**, opaque sRGB albedo, no alpha/maps.
- Material: `art/materials/environment/d09_freight_graphics_01/warehouse_fascia.tres`.
  White multiplier, roughness **0.62**, metallic **0**, opaque/back-culled, no emission.
  Linear mipmapped filtering, clamp/no repeat, lossless import, mipmaps enabled,
  automatic 3D compression conversion disabled. No embedded textures in the shared GLB.
- Prefab: `scenes/prefabs/environment/d09_freight_graphics_01.tscn`.
  `Visuals/Model` instances the shared GLB at identity; no copied geometry.

| Interface | Inherited metres, Godot local coordinates |
| --- | --- |
| Whole visual X / Y / Z | **3.200 / 0.800 / 0.140** |
| AABB min | **(-1.600, -0.400, -0.140)** |
| AABB max | **(1.600, 0.400, 0)** |
| Pivot | Wall-contact centre `(0,0,0)`, not ground contact |
| Face | **3.000 x 0.600**, Z=-0.128 |
| Safe artwork | Centred **2.940 x 0.540**; all outer 20 texture pixels stay field |
| UV0 | U toward Blender -X, V toward Blender +Z; glTF flips V storage |
| Axes | Blender +Y/+Z maps to Godot -Z/+Y once |
| Bounds tolerance | +/-0.001; source/GLB validator checks within 0.000001 |

The inherited **3.8 m wall-centre mounting height** is a provisional demonstration,
not saved world placement. Keep the carrier flush to a flat unobstructed facade bay,
above the 2.5 m overhead threshold; the 3.4 m lower edge clears the 1.8 m actor. Facade
collision owns blocking. This decorative flush fascia has **no additional collider**,
rig, animation, socket, dynamic state, collision change or gameplay script. Do not stack
it over another fascia or use it as a freestanding prop. No enlarged warehouse sign or
new building attachment envelope was inferred from the district concept.

## Saved face override and identity retention

The only override is `surface_material_override/0` on:

`Visuals/Model/city_shop_fittings_02/fascia_artwork_carrier`

The source slot is `fascia_artwork_face`. The carrier's rear/side slot and other six
meshes/materials remain unchanged. The prefab uses the authorized static-artwork
[editable-child face-slot exception](../../assets.md#prefabs-and-authored-placement):
linked GLB unchanged, no whole-object material override, no geometry copied, two
byte-stable save/reload cycles. The check compares every mesh with an independent
unmodified GLB instance, then verifies material, UV-carrier slot, inherited bounds and
all loaded dependency UIDs. Final `validation.json` retains both normalization and
fresh-process receipts; saved scene/material hashes and dependency UIDs agree.

- Prefab UID: `uid://dfxuc0tbk5dfi`.
- Material UID: `uid://bek2p6tjyns1f`.
- Texture UID: `uid://djegqdhwv1kqp` in `.import`.
- Existing GLB UID: `uid://cdtnvrp3u64wi`.

Godot stores scene/material UIDs inline and the check script UID in its `.uid`; it does
not produce separate `.tscn.uid`/`.tres.uid` files here. Current imported hierarchy and
saved child identities survive two roundtrips. Future shared-hardware hierarchy changes
must recheck the slot path/identity; this is not proof for arbitrary reexports.

Live MCP/editor sessions were forbidden by the production brief. Direct text resources
were loaded, packed and resaved with isolated pinned headless Godot runtime resource
APIs, then reimported and checked from a fresh process. No owner's open scene was touched
or claimed synchronized. No editor/windowed camera or gameplay test is implied.

## Evidence and measured validation

[Hero](d09_freight_graphics_01-evidence/hero.png) ·
[side](d09_freight_graphics_01-evidence/side.png) ·
[parcel-clock detail](d09_freight_graphics_01-evidence/detail.png) ·
[47 m / 42-degree overhead](d09_freight_graphics_01-evidence/overhead_47m_42deg.png).

All four are isolated **Blender** Cycles CPU, 32 samples, AgX, **1280 x 720**, PNG
compression 100. Evidence-only seven-bit RGB channel reduction keeps each below 400 KB;
the runtime artwork is not color-reduced. `preview.py` records lighting and cameras and
opens the shared source read-only without saving it. Overhead is perspective, vertical
down, Blender +Y at image top, camera `(0,10,47)` with **42-degree vertical FOV**;
only the fascia root is temporarily translated to `(0,0,3.8)` for mounting height.
No artificial tilt, scale boost or duplicated building geometry improves that view.

Producer inspected the texture and all four final compressed renders. Upright/unmirrored
copy, the whole cargo-clock emblem, edge margins, inset seating and original carrier
materials read cleanly in the close views. At the real gameplay distance the fascia
is only an approximately **70 x 7 pixel strip**: neither business name nor clock detail
is reliably readable. It is a restrained warm cluster, **not an overhead landmark or
essential wayfinding cue**. Repetition/warehouse placement must rely on architectural
identity and actual camera review, not texture-resolution inflation. No overhead text
readability acceptance is claimed.

[validation.json](d09_freight_graphics_01-evidence/validation.json) records:

- **836 source vertices, 1,072 GLB vertices, 1,656 triangles, 7 meshes, 8 surfaces**.
- **Zero degenerate source faces, zero degenerate GLB triangles, zero non-manifold
  edges**; closed consistently wound solids and applied metre transforms.
- Unit-length source corner normals; maximum GLB normal-length error
  **1.0940659689318011e-7**.
- Literal source/GLB bounds and loaded prefab bounds agree with the inherited table.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, glTF exporter **5.2.40**: fresh saved-source
  reexport **byte-identical**, shared GLB **45,616 bytes**, SHA-256
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- **Four artwork tests** pass: exact RGB/size, safe margins/quiet field, independent
  cargo-clock/cluster pixel expectations, fresh PNG byte identity.
- Pinned **Godot 4.8.dev7.official.c971f93e7** import exits 0 with no ERROR/SCRIPT ERROR;
  fresh prefab load exits 0 with no warning/error and all dependencies resolved.
- **Two byte-stable scene/material save/reload cycles**, one face-only override,
  seven unchanged imported mesh resources, no collision.
- Pinned **gdstyle 0.3.0** format check and zero-warning lint pass. The headless prefab
  invocation compiles and executes the only added GDScript.

[manifest.json](d09_freight_graphics_01-evidence/manifest.json) hashes every produced
payload except itself and uncommitted Python cache. Shared dependencies are hashed
separately in validation and the manifest and remain unchanged. [final.log](d09_freight_graphics_01-evidence/final.log)
retains concise final outcomes; raw logs/scratch export stay in
`C:/tmp/ft/assets/d09_freight_graphics_01/`, not Git.

## Exact reproduction

From the worktree root in Git Bash; keep timeouts/audio flags/thread count. Run with
Python/Pillow and the pinned tools above. Rebuilding receipts is explicit; plain
`record.py` verifies the delivered manifest without rewriting it.

```sh
NID=d09_freight_graphics_01
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
OUT="C:/tmp/ft/assets/$NID"
mkdir -p "$OUT"
export PYTHONIOENCODING=utf-8
python tools/asset_production/$NID/author.py
python -m unittest discover -s tools/asset_production/$NID -p 'test_*.py' -v > "$OUT/tests.log" 2>&1
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/validate.py > "$OUT/source.log" 2>&1
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" -noaudio --background --factory-startup --threads 4 --python-exit-code 1 --python tools/asset_production/$NID/preview.py > "$OUT/render.log" 2>&1
python tools/asset_production/$NID/record.py --compress-renders
timeout 300 "$G" --headless --path . --import > "$OUT/import-initial.log" 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd -- --normalize > "$OUT/normalize.log" 2>&1
timeout 300 "$G" --headless --path . --import > "$OUT/import-final.log" 2>&1
timeout 180 "$G" --headless --path . --script res://tools/asset_production/$NID/check_prefab.gd > "$OUT/prefab.log" 2>&1
"$S" fmt --check tools/asset_production/$NID/check_prefab.gd > "$OUT/format.log" 2>&1
"$S" --max-line-length 100 --max-warnings 0 tools/asset_production/$NID/check_prefab.gd > "$OUT/style.log" 2>&1
python tools/asset_production/$NID/record.py --write
python tools/asset_production/$NID/record.py
```

## Diagnostics and remaining acceptance

One initial owned lint warning (101-character texture constant) was corrected by
wrapping the constant; final formatting/lint pass. Initial Windows receipt packaging
used CRLF; writers now explicitly emit LF and the final manifest is checked against
staged Git bytes as well as working files. Headless import retains the installed
MCP toolkit's Godot-4.8-versus-tested-4.7 warning, not an asset error. Blender `--version`
alone emitted a 23-byte shutdown allocation diagnostic; actual source/export/render
runs exited 0 without that diagnostic. Preview emits Blender's `use_nodes` API
DeprecationWarnings for Blender 6.0. No diagnostics were suppressed or vendor tools edited.

Pending: independent art/technical review and final fictional copy selection; sparse
warehouse/facade placement and building attachment/occlusion checks; actual renderer
filtering and gameplay-camera review in the populated world; packaged device and
sustained performance/Deck tests. No multiplayer, movement, road-tool, gameplay authority
or collision behavior was changed, so no new network/physics acceptance is claimed.
No `production_checks.py` run, under owner decision 52. No world placement is authorized
by this source/material candidate alone.
