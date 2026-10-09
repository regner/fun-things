# d06_commercial_graphics.03 — Two poster wraps

9 October 2026. **Artwork/material/linked-prefab candidate delivered; independent review,
world/gameplay-camera and target-device acceptance pending.** Production authority:
[commission](commission.md), current per-record task and supervisor approval. Producer:
assigned lane worker on `lane/a-d06gfx`. Family: [Signal Row graphics](../d06_commercial_graphics.md).
Earlier family deliveries: [hall title](d06_commercial_graphics_01.md) and
[three shop fascias](d06_commercial_graphics_02.md).

## Design, provenance and approved scope

| Variant | Provisional fictional copy | Dominant non-text shape |
| --- | --- | --- |
| `last_call` | LAST CALL / FIRST REGRET | Broad magenta zigzag burst on petrol |
| `small_prices` | SMALL PRICES / BIG STORIES | Two cyan offset, notched ticket blocks on petrol |

Supervisor approved both proposed designs/copy and the same geometry-reuse exception as the
previous graphics: **reuse unchanged `d06_poster_drum.01`; no redundant .blend, GLB, decal shell
or carrier**. Its existing Blender source → explicit GLB → linked prefab chain satisfies the
artwork's applied-geometry requirement. New wrappers inherit the complete drum prefab and
preserve its exact cylinder collision, changing only the existing `poster_wrap` surface.
There is intentionally no per-ID geometry source or `export.py`; `validate.py` invokes the
hardware owner's existing source/export audit read-only and redirects its outputs to scratch.

The art is original Python/Pillow construction, not downloaded imagery, generated concept
pixels, external fonts or real brands. The earlier `.01` recipe owns the shared original
letter skeletons and palette; `.02` owns the reusable smooth-path canvas plus G/B glyphs.
This recipe reuses them unchanged on disk and adds only an original M skeleton. Shapes and
letter paths are supersampled 3× and filtered once. No attribution dependencies are introduced.
Copy remains provisional, not a final Regner naming selection.

| Shared palette | sRGB |
| --- | --- |
| Quiet petrol | `#102C3C` |
| Magenta | `#F54BBA` |
| Cyan | `#45DFE5` |
| Warm ivory | `#F6F1DC` |

Front and back repeat the same artwork. This does not duplicate the hall clock-ring or the
shop tag/bowl/disc motifs. Follows approved district identities, Signal Row v03 and stage-04
street constraints: commercial-corner decoration; quiet roofs/roads; no new world placement,
lights, advertising system, interaction, navigation or building-dimension assumption.

## Source, runtime outputs and inherited interface

- Recipe: `tools/asset_production/d06_commercial_graphics_03/author.py`;
  Python **3.14.2**, Pillow **12.3.0**.
- Textures: `art/textures/environment/d06_commercial_graphics_03/<variant>_albedo.png`
  and `.import`, for both variant names above; **2400 × 1000 RGB**, opaque sRGB albedo.
- Materials: `art/materials/environment/d06_commercial_graphics_03/<variant>.tres`;
  white albedo multiplier, roughness **0.7**, metallic **0**, opaque/backface-culled,
  no emission, linear mipmapped filtering, clamp/no repeat. Lossless texture imports,
  **mipmaps enabled**, automatic 3D compression changes disabled. No extra maps.
- Prefabs: `scenes/prefabs/environment/d06_commercial_graphics_03_<variant>.tscn`.
  Each inherits `scenes/prefabs/environment/d06_poster_drum_01.tscn`.
- Existing source: `art/source/models/environment/d06_poster_drum_01/d06_poster_drum_01.blend`;
  collection `export_d06_poster_drum_01`, root `D06PosterDrum01`, body and cap meshes.
- Existing linked export: `art/models/environment/d06_poster_drum_01/d06_poster_drum_01.glb`.
  Full hardware contract: [poster drum handoff](d06_poster_drum_01.md).

| Inherited measurement | Metres / convention |
| --- | --- |
| Whole Godot X/Y/Z | **0.90 / 1.45 / 0.90** |
| Godot AABB | min **(-0.45, 0, -0.45)**; max **(0.45, 1.45, 0.45)** |
| Pivot | Ground-centred **(0,0,0)**; applied identity transforms |
| Poster radius / bottom / top | **0.397 / 0.24 / 1.28** |
| Poster usable height / circumference | **1.04 / approximately 2.4945** |
| Artwork aspect | **2.40:1**, matching the approximately 2.399:1 physical wrap |
| UV0 seam / front | U=**0/1**, Godot **+Z** rear / U=**0.5**, Godot **-Z** front |
| UV0 vertical | Blender V=0 lower, V=1 upper; glTF stores V=0 top, V=1 bottom |
| Tolerances | Bounds ±0.001 m; source/export coordinates 0.00001 m |

The 1200-pixel design repeats twice and is cyclically offset by 600 pixels, placing panel
centres at U=0/1 and U=0.5. The rear seam crosses the **continuous centre of the design**;
it is not hidden under a blank strip. Both sides of that seam have exactly the same pixel
neighbourhood as the interior front centre. Quiet 65-pixel top and 60-pixel bottom margins
keep artwork away from trim. No UV transforms, tiling scale or additional surface is needed.

## Saved prefab, material and collision contract

Exactly one override per wrapper:

`Visuals/Model/D06PosterDrum01/D06PosterDrum01_Body:surface_material_override/1`

The original slot name is checked as `poster_wrap`. Body slot 0 and cap slot 0 remain
`drum_frame_petrol`. `Visuals/Model` stays the identity-transform linked GLB instance. No
embedded mesh, global `material_override`, runtime appearance script or copied collision.
The inherited `Collision/Body/Shape` remains the same CylinderShape3D resource: radius
**0.45 m**, height **1.45 m**, centre **Y=0.725 m**, enabled; static world layer **1**, mask **0**.
No new collision behavior is implied by these visual variants. Place one complete variant,
not a second drum at the same transform. The alternate `.02` cap is not duplicated here.

Supervisor approved this narrow **saved editable-child surface override** exception, as
for the previous lane graphics. Both wrappers retain their base-prefab inheritance, imported
body `unique_id=1927634215`, parent-ID ancestry and existing base child identities. Two
load/pack/save cycles and a separate repeat invocation preserve scene bytes and IDs exactly.
Future hardware hierarchy/reexport changes must recheck these overrides; this proves the
current unchanged hardware, not arbitrary future migrations. Scene/material UIDs are inline,
texture UIDs are in `.import`, and the checker UID is in `.gd.uid`; Godot does not generate
separate `.tscn.uid` or `.tres.uid` sidecars here.

Live editor/MCP mutations were prohibited by the task. Text-authored wrappers were normalized
by isolated pinned headless Godot. No owner's live session was accessed, refreshed or saved,
and no separately open scene is claimed synchronized. The existing project plugin starts
and stops its own local server during headless checks; no MCP requests were made.

## Evidence and measured validation

[Hero](d06_commercial_graphics_03-evidence/hero.png),
[side](d06_commercial_graphics_03-evidence/side.png),
[rear-seam detail](d06_commercial_graphics_03-evidence/detail.png),
[47 m / 42° overhead](d06_commercial_graphics_03-evidence/overhead_47m_42deg.png).
Four isolated Blender renders, each **1280×800**, Cycles CPU **32 samples**, AgX. Camera,
lights and comparison translations are explicit in `preview.py`. Source is opened read-only;
transient duplicate instances and material-slot data copies are never saved or exported.

Inspected all four final images: upright/unmirrored copy, distinct burst/ticket silhouettes,
clean trim, no split or colour discontinuity at either rear seam. Hero/side show last-call
left and small-prices right; the rear detail reverses that order. Initial rear lighting was
too dim for seam inspection; a broad rear fill was added and all views re-rendered/inspected.
The broad bright cap highlight in the hero is studio reflection, not a material override.

Overhead is vertical/north-up from Blender **(0,10,47)**, **42° vertical FOV**. Drums are
unscaled/grounded at **(1,0,0)** and **(-1,0,0)**, no camera-facing tilt. Each occupies about
**20×26 pixels**, with only a few pixels of wrap above the quiet cap. The cyan/magenta
accent slivers differ, but **the motifs and text are not reliably identifiable at this
camera scale**. This small subordinate support is not a text-dependent navigation cue.
No texture-resolution increase can expose a wrap hidden below its cap. Actual populated
world, renderer, occlusion and gameplay-camera acceptance remain pending.

[validation.json](d06_commercial_graphics_03-evidence/validation.json) records:

- Per unchanged drum: **1,152 source vertices, 1,556 GLB vertices, 2,296 triangles,
  two meshes, three surfaces**, two source hardware materials.
- **Zero degenerate source faces/GLB triangles, zero non-manifold edges**, unit source
  corner and exported normals; metre units, ground pivot and inherited bounds pass.
- Existing owner's complete source/GLB audit reused. Additional independent checks verify
  actual front/rear UV position and lower/upper orientation: 4 seam, 4 front, 128 bottom
  and 128 top loop samples. Source/export/material/import/base-prefab dependencies unchanged.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**; fresh saved-source
  reexport is byte-identical to the committed **66,628-byte** shared GLB.
- Pinned Godot **4.8.dev7.official.c971f93e7**: both dependency chains load, hierarchy and
  transforms equal the unchanged base, same imported mesh/cylinder resources, one wrap-only
  override, exact bounds, real imported mipmaps and stable repeated normalization.
  Final non-editor dependency check has no WARNING/ERROR/SCRIPT ERROR diagnostics.
- **Four artwork tests pass**: exact opaque size/PNG byte identity, front/back repetition and
  seam neighbourhood equality, independent motif/quiet-border pixels, and distinct colour
  masses after 48×20-pixel texture downsampling. This proxy is not a gameplay-camera test.
- Owned gdstyle **0.3.0** lint/format pass. Full production suite passes: owned script
  formatting/style/explicit compilation, **nine Python tool tests**, **23 GUT tests /
  196 assertions**, import and the intentional-negative diagnostic test.

[manifest.json](d06_commercial_graphics_03-evidence/manifest.json) hashes every produced file
except itself and uncommitted Python caches. Shared dependencies are hashed separately in
validation. [final_checks.log](d06_commercial_graphics_03-evidence/final_checks.log) retains
concise outcomes/diagnostics. Full logs, temporary export and intermediate receipts remain
outside Git in `C:/tmp/ft/assets/d06_commercial_graphics_03/`.

## Exact reproduction

From this worktree root with the pinned tools available:

```sh
N=d06_commercial_graphics_03
python tools/asset_production/$N/author.py
python -m unittest discover -s tools/asset_production/$N -p 'test_*.py' -v

timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/validate.py

timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy \
  'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python tools/asset_production/$N/preview.py

timeout 300 "$(mise which godot)" --headless --editor --path . --import
# Only normalize when intentionally saving owned resources.
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd -- --normalize
# Register newly saved UIDs before independent runtime validation.
timeout 300 "$(mise which godot)" --headless --editor --path . --import
timeout 180 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" check tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/$N/check_prefab.gd
# Use a fresh output directory for each full suite run.
timeout 1800 mise exec -- python tools/production_checks.py \
  --output C:/tmp/ft/assets/$N/checks_reproduce
python tools/asset_production/$N/manifest.py
```

`validate.py` refreshes the source/export portion of validation.json. The retained candidate
also combines actual scratch engine/normalization and production receipts; reassemble those
before a new evidence write. The existing hardware validator is top-level, not a callable API;
its two output assignments are redirected in memory with exact-match guards, retaining all
owner assertions and its `__file__` exporter resolution. No private geometry validator copy.
`manifest.py --write` explicitly refreshes hashes after intentional changes; default verifies.

## Diagnostics and remaining gates

Headless editor normalization exits 0 and passes all resource/identity assertions but emits
the existing addon 4.8-versus-4.7 warning, scan-aborted warning and editor shutdown RID/ObjectDB
leaks. These are retained, not suppressed or called a clean editor exit. Full import and
non-editor dependency checks are separately successful. The production suite is green;
no compile/style failures were ignored. Blender renders emit pinned node-API deprecation
warnings but exit 0; source audit/export exits 0 without topology or audio-shutdown faults.
Initial texture imports had no mipmaps; corrected both owned import settings before final
validation and added a real imported-mipmap assertion.

Pending: independent technical/art review, final fictional copy selection, saved world
placement away from intersection sightlines/passage mouths/bridge landings, actual populated
renderer/gameplay visibility, future hardware-reexport identity retention, packaged filtering,
repeat-placement cost and sustained Deck performance. Hardware movement/query/network gates
remain with the existing drum and placement owners. No collision, simulation, authoritative
world data or multiplayer behavior changed, so no new gameplay/network acceptance is claimed.
