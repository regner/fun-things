# d08_repair_graphics.02 — Depot direction panel

10 October 2026. **Artwork/material/linked-prefab candidate delivered; independent review and
world/gameplay/device acceptance pending.** Producer: assigned lane worker, `lane/a-d08g`.
Authority: current per-record task and [production commission](commission.md), superseding the
historical concept-only restriction. Family: [repair graphics](../d08_repair_graphics.md).

## Design and provenance

**DEPOT / PARTS THIS WAY**, with a broad right arrow in an ivory field, large dark depot copy,
sun-faded amber background and two restrained cyan service strokes. The `depot_right_patched`
finish adds an uneven ivory/old-paint repaint behind the lower copy. Both retain sparse chipped
edges and exactly the same depot identity and rightward cue. No random grime, dense scratches,
external fonts, downloaded art, real brands, light nodes, emission or animation.

Palette, smooth original path lettering, two-line cyan signature and patch treatment match the
already-delivered [repair fascia .01](d08_repair_graphics_01.md), inspected alongside these
outputs. Original Python/Pillow artwork uses that sibling's canvas/palette read-only; its
project-owned path canvas and letter skeletons trace to `d06_commercial_graphics_02/author.py`
and `.01/author.py`. This delivery adds its own W glyph, directional layout, arrow and authored
paint-wear shapes. No Signal Row image or mesh is copied. Python **3.14.2**, Pillow **12.3.0**;
3x supersampling followed by one Lanczos downsample.

| Palette role | sRGB |
| --- | --- |
| Dark paint / lettering | `#263F43` |
| Sun-faded amber field | `#DCAE66` |
| Ivory arrow field / original copy | `#E9DFC1` |
| Restrained cyan service strokes | `#78ACA9` |
| Exposed old paint | `#B6A77E` |
| Repaint patch | `#DCCDA5` |

This practical, warm Ironreach treatment is deliberately less electric than Signal Row.
Copy, colour tuning and rightward layout are **provisional producer choices**; no final sign
copy selection or real depot route is claimed. Placement must make the arrow truthful; the
artwork neither controls navigation nor implies a repair shop interaction, inventory or economy.
The selected Ironreach district is the irregular 5.81 ha area, not an older M1 adjacency plan.
Its courts, road widths, boundary and open escape routes remain unchanged.

## Source, exports and material interface

**Hardware reuse exception:** family revision 02 selects `city_sign_supports.02` low panels.
The standing reuse rule prohibits a duplicate Blender/GLB carrier. This artwork delivery has
no redundant per-ID `.blend`, GLB or export script. Its unchanged original source chain is:

- `art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend`
- Collection `export_city_sign_supports_02`, root `CitySignSupports02`.
- Meshes `CitySignSupports02_Hardware` and `CitySignSupports02_ArtworkCarrier`.
- `art/models/environment/city_sign_supports_02/city_sign_supports_02.glb` and `.import`.
- `scenes/prefabs/environment/city_sign_supports_02.tscn`.
- [Hardware/source interface](city_sign_supports_02.md),
  [linked-prefab conventions](batch_01-integration.md).

`tools/asset_production/d08_repair_graphics_02/validate.py` executes the hardware owner's
source/binary validator and exporter with **only output directory assignments redirected to
scratch**. Every original assertion remains: source topology, independent actual GLB accessor
geometry/UVs/normals, named export membership and fresh byte comparison. The shared explicit
`tools/assets/blender/export_settings.json` contract remains unchanged; studio nodes stay out.
Before/after hashes protect all reused source/export/prefab and helper dependencies.

Owned recipe: `tools/asset_production/d08_repair_graphics_02/author.py`.
Each of `depot_right` and `depot_right_patched` maps to:

- `art/textures/environment/d08_repair_graphics_02/<variant>_albedo.png` plus `.import`.
- `art/materials/environment/d08_repair_graphics_02/<variant>.tres`.

Both textures are **1440 x 390 RGB**, opaque sRGB albedo, **48:13** aspect, UV0, no other maps
or embedded images. Materials: white multiplier, roughness **0.82**, metallic **0**, no emission,
backface culling, linear mipmapped filtering (engine default enum 3), clamp/no repeat,
identity UV scale/offset. Lossless imports, actual imported mipmaps enabled, automatic detect-3D
compression changes disabled. Only carrier slot 0 `sign_face` changes; slot 1 `mount_metal`
keeps the carrier sides/rear, and all frame/gasket/post/foot materials remain original.

| Inherited measurement | Contract |
| --- | --- |
| Whole Godot X/Y/Z size | **1.600 x 1.350 x 0.400 m** |
| Godot AABB | min **(-0.800,0,-0.200)**; max **(0.800,1.350,0.200)** m |
| Pivot / ground datum | **(0,0,0)**, centred between the feet |
| Panel body | Width **1.60 m**, height **0.55 m**, bottom **0.80 m** |
| Artwork face | **1.440 x 0.390 m**, bottom **0.880 m**, top **1.270 m** |
| Face plane / corners | Godot **Z=-0.071 m**, corner radius **0.022 m** |
| Safe copy rectangle | Centred **1.380 x 0.330 m**, primary text/arrow inside |
| UV orientation | U toward Blender -X, V toward +Z; ordinary PNG upright/unmirrored |
| Tolerances | Engine envelope **+/-0.001 m**, source/GLB coordinates **+/-0.00001 m** |

Dimensions are the inherited hardware's **provisional authored values**, not new layout
approval. Blender +Z maps to Godot +Y, Blender +Y to Godot -Z. Face-view right is local -X;
the right arrow follows that direction. No model scaling, corrective rotation, face tilt or
billboarding is introduced. Rig, clips, sockets, damage states and new LODs are not applicable.
Keep existing hardware automatic LOD settings; no performance budget is claimed.

## Saved prefabs, collision and identity retention

- `scenes/prefabs/environment/d08_repair_graphics_02.tscn` — sun-faded original.
- `scenes/prefabs/environment/d08_repair_graphics_02_patched.tscn` — uneven lower repaint.

Both inherit the unchanged low-panel prefab. `Visuals/Model` remains its identity-transform
linked GLB instance. Exactly one saved face-slot override per variant:

`Visuals/Model/CitySignSupports02/CitySignSupports02_ArtworkCarrier:surface_material_override/0`

This uses the **narrow editable-child face-slot exception** in
[assets.md, Prefabs](../../assets.md#prefabs-and-authored-placement): a static,
non-identity-sensitive artwork carrier, no copied mesh data or hardware changes. The owned
checker reuses existing hierarchy and pack/save helpers and proves initial normalization plus
**two byte-stable load/pack/save cycles per variant**, including material resources. Full-byte
equality preserves serialized node identities, inheritance paths and resource UIDs; final file
hashes are retained in validation.json and verified against the producer manifest.

Collision remains exactly the hardware-owned **one BoxShape3D**, **(1.60,1.35,0.40) m** at
**(0,0.675,0)**, `Collision/Body/Shape`, static world layer **1**, mask **0**. It deliberately
blocks the visual gap beneath the panel. Tests compare the same shape resource, transforms,
body count and layers, not a replacement approximation. Each actual variant passes centre
ray blocked at Y=0.7, side ray clear at X=0.9, and overhead ray clear at Y=1.6. No collider,
collision behavior, navigation, destructibility or network state is added or modified.
Hardware-owner production actor-motion evidence is historical context, **not a rerun here**.

Mount the complete prefab once on flat ground near a depot approach, not over another panel.
Do not put its 0.40 m-deep feet/box across passage mouths, yard turning paths or junction views.
The low sign must not be the only essential navigation cue; preserve alternate readable cues
and make actual placement/route direction match the arrow.

The task prohibits live editor sessions and the windowed editor is unavailable. Resources
were authored as text, then loaded/packed/resaved only with isolated pinned headless Godot.
No separate open editor scene is claimed synchronized. The pin stores scene/material UIDs
inline, texture UIDs in `.import`, and the script UID in `.gd.uid`; it emits no `.tscn.uid`
or `.tres.uid` sidecars here. No runtime-authored visible hierarchy or geometry.

## Evidence and validation

[Hero](d08_repair_graphics_02-evidence/hero.png),
[patched side](d08_repair_graphics_02-evidence/side.png),
[patched face detail](d08_repair_graphics_02-evidence/detail.png),
[47 m / 42-degree overhead](d08_repair_graphics_02-evidence/overhead_47m_42deg.png).
All are isolated Blender renders, **1280 x 720**, Cycles CPU, 32 samples, AgX, PNG compression
95, no dithering. Each is below 190 KB. Exact cameras/lighting are in `preview.py`; source
files are never saved with preview materials. No studio geometry is exported or duplicated.

Self-inspected both runtime textures and all four final renders. Hero/side show the upright,
unmirrored right arrow, stable shared hardware and readable close-view text. Detail shows
sparse broad edge wear and uneven lower repaint without obscuring the depot or arrow.
Overhead camera is vertical/north-up at Blender **(0,10,47)**, **42-degree vertical FOV**, sign
at its unmodified ground pivot. Hardware occupies only approximately **32 x 10 pixels**, its
face much thinner: **DEPOT, lower copy and arrow are not reliably identifiable at gameplay
height**. It is optional close-view wayfinding/decor, not a claimed gameplay-readable route
system. No larger texture would fix geometric foreshortening. These are not Godot gameplay
captures, roof-occlusion tests or district lighting acceptance.

[validation.json](d08_repair_graphics_02-evidence/validation.json) records:

- Reused geometry: **1,244 source vertices, 1,596 GLB vertices, 2,448 triangles,
  two meshes, five surfaces**. No new geometry.
- **Zero non-manifold edges, degenerate source faces and degenerate GLB triangles**;
  unit-length source/export normals, outward winding, positive source volume, finite positions,
  metre scale, applied transforms, ground pivot, bounds and front UV orientation pass.
- Blender **5.2.2 LTS**, build **d13f752e3b9c**, exporter **5.2.40**.
  Fresh saved-source export is **byte-identical**, **70,712 bytes**, SHA-256
  `022dd559334d79c482182083be775c692ab4adf2a5277d3fb7ca7ec266ec76b7`.
- Godot **4.8.dev7.official.c971f93e7**: dependencies load, two meshes/five surfaces and one
  front-only override per variant, unchanged hierarchy/mesh/collision resources, six total ray
  expectations, real mipmaps, and four total stable scene/material roundtrip cycles pass.
- **Six artwork tests pass**: exact PNG reproduction, independent palette/border samples,
  rightward arrow samples, primary cues unchanged by repaint, 96 x 26 front-facing contrast
  proxy, invalid-variant rejection. The proxy is not an overhead-readability test.
- Pinned **gdstyle 0.3.0** formatting and zero-warning lint pass for the added checker.
- Final full pinned import exits 0 with **no ERROR/SCRIPT ERROR**; independent runtime load
  exits 0 with no warning/error lines. Shared resources remain byte-identical.

[manifest.json](d08_repair_graphics_02-evidence/manifest.json) hashes every produced payload
except itself and ignored Python caches. [final_checks.log](d08_repair_graphics_02-evidence/final_checks.log)
retains concise results and diagnostics. Scratch exports, raw logs and intermediate receipts
stay outside Git under `C:/tmp/ft/assets/d08_repair_graphics_02/`.

## Exact reproduction

From the worktree root; Blender/engine invocations are bounded and audio-disabled:

```sh
N=d08_repair_graphics_02
S=C:/tmp/ft/assets/$N
mkdir -p "$S"
export PYTHONIOENCODING=utf-8
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
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --editor --path . \
  --script res://tools/asset_production/$N/check_prefab.gd -- --normalize
cp "$S/prefab.json" "$S/normalized.json"
timeout 300 "$(mise which godot)" --headless --path . --import
timeout 180 "$(mise which godot)" --headless --path . \
  --script res://tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" fmt --check tools/asset_production/$N/check_prefab.gd
"$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  tools/asset_production/$N/check_prefab.gd
```

After intentional reproduction, source validation refreshes its receipt. Merge scratch
`normalized.json` as `godot_normalization` and `prefab.json` as `godot_load` into validation.json;
refresh recorded test/check/render observations, then run
`python tools/asset_production/d08_repair_graphics_02/manifest.py --write` last. The default
manifest invocation verifies without writing. No `production_checks.py` invocation is claimed
or required for this unplaced asset (decision 52).

## Diagnostics and remaining acceptance

Initial artwork authoring exposed the missing shared W skeleton; a new original W was added
locally, leaving shared tools unchanged. One initial test sampled the anti-aliased chip boundary
rather than its interior; the sample moved four pixels inward without changing the artwork or
expected palette. All six final tests pass. Blender exits 0; existing node API future-deprecation
warnings are not hidden.

Headless editor normalization passes its assertions and byte comparisons, exits 0, then emits
the existing scan-aborted warning and RID/ObjectDB shutdown leaks also recorded by the hardware
and sibling owners. This is **not a clean editor exit claim**. Final full import has only the
existing MCP 4.8-versus-4.7 compatibility warning, no ERROR/SCRIPT ERROR. Runtime load is clean.
The project's existing addon automatically opens its local listener; no live-session/MCP requests
were sent. This delivery does not change or suppress addon behavior.

Remaining: independent technical/art review, owner selection of provisional copy/palette,
saved world placement with truthful arrow direction and route/vehicle/foot clearance,
actual gameplay-camera/population views and roof occlusion, target renderer/mip behavior,
repeated-placement performance, packaged build and Deck checks. No new motion, multiplayer or
device acceptance is claimed. The earlier fascia handoff has no stale pending depot item;
it and its evidence manifest remain unchanged. The registry owns other family deliveries.
