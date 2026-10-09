# d06_commercial_graphics.02 — Three contrasting shop-fascia artworks

9 October 2026. **Artwork/material/linked-prefab candidate delivered; independent review,
world/gameplay-camera and target-device acceptance pending.** Production authority:
[commission](commission.md), current per-record task and supervisor direction. Producer:
assigned lane worker on `lane/a-d06gfx`. Family: [Signal Row graphics](../d06_commercial_graphics.md).
Earlier family delivery: [hall title](d06_commercial_graphics_01.md).

## Design, provenance and approved scope

Three original fictional businesses share smooth rounded lettering and the hall's palette,
but deliberately do **not** reuse its split clock-ring or layout:

| Variant | Provisional tenant | Dominant non-text graphic |
| --- | --- | --- |
| `loose_change` | LOOSE CHANGE, bargain shop | Large magenta angular price tag on the left, dark right half |
| `second_helping` | SECOND HELPING, late food | Cyan flood field with a broad dark bowl and three steam strokes |
| `side_b` | SIDE B, records/nightlife | Filled ivory disc at left, quiet middle, broad magenta block at right |

Supervisor approved these tenants, graphic direction and the same integration exception as
`.01`: **reuse the unchanged accepted shared fascia, with saved face-only material overrides;
do not construct/export another carrier or add a coplanar panel.** The existing Blender
source → GLB → linked prefab chain satisfies the artwork's applied geometry requirement.
There is intentionally no redundant per-ID `.blend`, GLB or `export.py`. The validator invokes
the existing hardware owner's source/export audit instead of copying its geometry rules.

All art is explicitly drawn by the committed Python/Pillow recipe. No external fonts, image
models, downloaded art, generated concept pixels, real brands or third-party attribution
requirements. The existing `.01/author.py` owns the shared original letter skeletons and palette;
this recipe imports them unchanged and adds only original G/B glyphs. Smooth filled shapes and
rounded strokes are supersampled 3× then filtered once. The record's names remain provisional
fictional copy, not a final owner copy-selection decision.

| Palette role | sRGB |
| --- | --- |
| Petrol field/copy | `#102C3C` |
| Magenta | `#F54BBA` |
| Cyan | `#45DFE5` |
| Warm ivory | `#F6F1DC` |

Follows approved district identities, Signal Row v03 and stage-04 street constraints: accents
at shop fronts, not roof centres/roads; no world placement, new sign hardware, lighting,
interaction, navigation, building dimensions or tenant-count assumption. The cyan face is
intentionally a brighter contrast within this three-tenant set; populated-world placement
must control repetition rather than blanketing all facades with the brightest variant.

## Source, outputs and inherited dimensions

Editable source: `tools/asset_production/d06_commercial_graphics_02/author.py`.
Python **3.14.2**, Pillow **12.3.0**. For each of the three variant names above:

- Texture: `art/textures/environment/d06_commercial_graphics_02/<variant>_albedo.png`
  plus its `.import`; **2000 × 400 RGB**, opaque sRGB albedo, 5:1 aspect.
- Material: `art/materials/environment/d06_commercial_graphics_02/<variant>.tres`.
  White albedo multiplier, roughness **0.56**, metallic **0**, opaque/backface-culling,
  no emission. Linear mipmapped filtering, clamp/no repeat. Lossless texture import,
  mipmaps enabled, automatic 3D compression changes disabled; no normal/ORM/emission maps.
- Prefab: `scenes/prefabs/environment/d06_commercial_graphics_02_<variant>.tscn`.
  Imported shared GLB remains linked at identity `Visuals/Model`.

Reused, unchanged geometry:

- Source: `art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend`.
- Collection/root: `export_city_shop_fittings_02` / `city_shop_fittings_02`.
- Export: `art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb` and
  existing import metadata. See [shared fascia handoff](city_shop_fittings_02.md).

| Interface | Inherited measurement |
| --- | --- |
| Whole fascia X/Y/Z, Godot | **3.200 × 0.800 × 0.140 m** |
| Godot AABB | min **(-1.600, -0.400, -0.140)**; max **(1.600, 0.400, 0)** m |
| Mounting pivot | Wall-contact centre **(0,0,0)**, not ground-centred |
| Artwork face | **3.000 × 0.600 m**, Godot Z=**-0.128** |
| Safe content | Centred **2.940 × 0.540 m**; outer 20 texture pixels remain petrol |
| UV0 orientation | U toward Blender -X; V toward +Z; glTF flips V storage |
| Mounting proposal | Centre **3.8 m** above ground, vertical flat bay, unchanged shared contract |
| Bound tolerance | ±0.001 m; hardware source validator enforces tighter 1e-6 |

No new rig, clips, sockets, LOD, collider, navigation or state. Decorative hardware adds no
blocking volume; the facade owns collision. Do not stack this complete fascia variant with
another fascia at the same transform.

## Saved override and identity contract

Each wrapper changes exactly `surface_material_override/0` on:

`Visuals/Model/city_shop_fittings_02/fascia_artwork_carrier`

The checked original slot is `fascia_artwork_face`. Back/sides retain `fascia_mount_metal`;
all other surfaces, geometry and transforms remain unchanged. No embedded render mesh,
global `material_override` or runtime material-application script is added.

The saved editable-child override is the supervisor-approved narrow exception already used
for `.01`, not a project-wide replacement for the normal wrapper-appearance convention.
Every variant retains the imported carrier's `unique_id=247601221`, parent-ID ancestry,
registered resource UIDs and its own wrapper/node identities. Two load/pack/save cycles,
then another normalization invocation, preserve all three scene files byte-for-byte.
A future shared-hardware hierarchy change must revalidate these paths and IDs; this pass
proves the current unchanged source/GLB, not arbitrary future reexports.

The engine stores scene/material UIDs inline, texture UIDs in `.import`, and the checker
script UID in `.gd.uid`; it does not produce separate `.tscn.uid` or `.tres.uid` sidecars.
The checker extends the existing family checker to reuse material/geometry/bounds expectations,
while overriding variant-specific paths and saves. It never normalizes the hall resources.
The producer manifest similarly reuses the family's inventory/hash helper without invoking
its hall-writing entrypoint.

Live editor/MCP tools were prohibited by the production brief. These wrappers were authored
as text, then loaded/packed/resaved by isolated pinned **headless** Godot. No owner's live
session was accessed, refreshed, saved or claimed synchronized.

## Evidence, visual findings and measured validation

[Hero](d06_commercial_graphics_02-evidence/hero.png),
[side](d06_commercial_graphics_02-evidence/side.png),
[disc/trim detail](d06_commercial_graphics_02-evidence/detail.png),
[47 m / 42° overhead](d06_commercial_graphics_02-evidence/overhead_47m_42deg.png).
Four isolated Blender renders, each **1280×800**, Cycles CPU **32 samples**, AgX. Camera,
lighting and temporary comparison transforms are explicitly recorded in `preview.py`.
The source opens read-only: transient material-slot copies and comparison translations
are never saved over the shared source or exported as new geometry.

Hero/side order is top-to-bottom tag, bowl, disc. The detail isolates the SIDE B disc and
inset frame. Inspected all four images plus the three runtime PNGs: upright/unmirrored copy,
clean margins, smooth artwork edges, distinct graphic layouts and unchanged hardware trim.
The initial side framing clipped a frame corner; the final camera scale was increased to
show all three complete panels and the revised side render was inspected.

The overhead is vertical/north-up at Blender **(0,10,47)**, vertical FOV **42°**, with roots
at **(4,0,3.8)**, **(0,0,3.8)**, **(-4,0,3.8)**. Left-to-right: tag, bowl, disc. They remain
vertical and full-scale, not tilted/enlarged for visibility. The whole panels occupy only
approximately **75–80 × 7 px** each; the face is thinner still. **The broad left-magenta,
cyan-field and right-magenta/ivory distributions are visibly different without reading text.**
The tag/bowl/disc's semantic details and lettering are not reliably readable at this scale.
This is bounded isolated colour-mass differentiation, **not** actual world navigation,
all-camera-position or populated-scene readability acceptance. A face directly below the
camera or hidden by roofs cannot be made readable by increasing texture resolution.

[validation.json](d06_commercial_graphics_02-evidence/validation.json) records:

- Per reused fascia: **836 source vertices, 1,072 GLB vertices, 1,656 triangles,
  seven meshes, eight surfaces**, five unchanged source hardware materials.
- **Zero degenerate faces/triangles and zero non-manifold edges**, consistent closed-solid
  winding, unit-length corner normals, applied transforms and metre units. Counts are
  inherited geometry audited again, not three newly created models.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**. Fresh saved-source
  reexport is **byte-identical**, 45,616 bytes, SHA-256
  `4fd2106f09ef4a35edafbcf3a3a68ea94983e721fd84d852a406e2d26de6552f`.
- Pinned Godot **4.8.dev7.official.c971f93e7**: all three dependency chains load, each with
  seven unchanged imported mesh resources, one front-only override, inherited exact bounds,
  identity `Visuals/Model`, opaque/clamped/mipmapped artwork and no collision. Stable repeated
  scene normalization/UID checks; final non-editor load has no WARNING/ERROR/SCRIPT ERROR.
- **Four artwork tests pass**, covering exact opaque dimensions/PNG byte reproduction,
  all safe borders, independent motif pixels, and distinct broad colour masses after
  severe **75×4 px** downsampling. This proxy supplements, not replaces, the actual render.
- Owned pinned gdstyle **0.3.0** lint/format pass. Full production checks pass: owned
  formatting/style/explicit compilation, **nine Python tool tests**, **23 GUT tests /
  196 assertions**, import and the intentionally failing negative diagnostic test.

[manifest.json](d06_commercial_graphics_02-evidence/manifest.json) hashes every produced
payload except itself and uncommitted Python caches. Shared source/model and reused tooling
are hashed separately in validation. [final_checks.log](d06_commercial_graphics_02-evidence/final_checks.log)
retains concise outcomes/diagnostics; scratch exports, raw logs and engine receipts remain
outside Git at `C:/tmp/ft/assets/d06_commercial_graphics_02/`.

## Exact reproduction

From the worktree root, with the pinned Python/Pillow and Blender/Godot available:

```sh
python tools/asset_production/d06_commercial_graphics_02/author.py
python -m unittest discover -s tools/asset_production/d06_commercial_graphics_02 -p 'test_*.py' -v

timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/d06_commercial_graphics_02/validate.py

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/d06_commercial_graphics_02/preview.py

timeout 300 "$(mise which godot)" --headless --editor --path . --import
# Normalize only when intentionally saving owned resources.
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/d06_commercial_graphics_02/check_prefab.gd -- --normalize
# Complete the filesystem scan after first normalization to register newly saved UIDs.
timeout 300 "$(mise which godot)" --headless --editor --path . --import
# Non-mutating dependency/resource/override validation:
timeout 180 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/d06_commercial_graphics_02/check_prefab.gd
"$(mise which gdstyle)" check tools/asset_production/d06_commercial_graphics_02/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/d06_commercial_graphics_02/check_prefab.gd
# Use a fresh output directory for each full run.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/d06_commercial_graphics_02/checks_reproduce
python tools/asset_production/d06_commercial_graphics_02/manifest.py
```

`validate.py` refreshes the source/export section of validation.json; this retained candidate
also combines the separate scratch `prefab.json`, normalization receipt and production summary.
Reassemble those actual receipts before a new evidence write. `manifest.py --write` explicitly
refreshes producer hashes after intentional changes; normal invocation verifies them only.

## Diagnostics, corrections and remaining gates

- Initial in-memory PNG test omitted Pillow's explicit PNG format; fixed the test harness,
  closed its image handle, removed the deprecated pixel iterator, and reran all four tests.
  Initial one-line GDScript length warning was fixed; final owned lint/format is clean.
- The first load immediately after creating material UIDs warned about UID fallback because
  normalization quit before the editor scan completed. A complete headless import registered
  the saved UIDs; the final independent load has no fallback or missing-dependency diagnostics.
- Headless normalization exits 0 with passing resource/byte checks, but emits the existing
  addon 4.8-versus-4.7 warning, scan-aborted warning and editor shutdown RID/ObjectDB leaks.
  These are not suppressed or called a clean editor exit. Full import/non-editor load and
  full production checks are separately successful. No source or gameplay failure was ignored.
- Pinned Blender's `--version` probe emitted its tiny shutdown allocation diagnostic;
  production rendering emitted node-API deprecation warnings. Actual source validation and
  rendering exit 0; no topology/export failures or audio shutdown failures occurred.

Pending: independent technical/art review; final fictional copy selection; saved world/flat-bay
placement; actual target-renderer, populated gameplay-camera and occlusion review; future
shared-fascia hierarchy/reexport identity retention; packaged filtering and sustained Deck
performance. No collision, simulation, multiplayer or authoritative world data changed, so
this handoff neither claims new movement/network tests nor authorizes placement.
